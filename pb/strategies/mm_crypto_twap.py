"""Model 2 — 15-minute crypto up/down passive market maker (Kalshi KXBTC15M /
KXETH15M; Polymarket 5/15-min up-or-down).

Mechanism
---------
The contract pays if the settlement reference (Kalshi: 60 s average of the CF
Benchmarks BRTI at window close; Polymarket: Chainlink 60 s TWAP) exceeds the
window's opening reference. We model P(up) from a spot index signal
(`btc_index` / `eth_index`, optionally blended with `twap60`):

    z   = ln(S_t / S_open)
    tau = max(T_close - t - 30s, 0)             (the 60s average "sees" ~half)
    p   = Phi( z / (sigma * sqrt(tau)) )

sigma is the realised log-return volatility of the index estimated from the
signal history (per-second, EWMA-ish over `vol_window`), floored to
`vol_floor`. We quote post-only around that fair with an inventory skew and a
spread that widens with sigma*sqrt(tau)-uncertainty and with toxicity. We
never take.

Guards (all research-driven):
* `pull_before_close` (default 90 s): late flips happen in 13-32% of near-line
  windows; the last minutes are pure sniping by index-arb takers.
* jump guard: if the index moved more than `jump_k` * sigma_5s in 5 s, pull
  for `jump_cooldown` s (the book has not repriced yet; our quote is stale).
* `max_abs_delta`: flatten rule - when |inventory| > max_abs_delta we only
  quote the reducing side (and more aggressively, up to the touch).
* signal staleness: no index within `signal_max_age` -> pull.
* fair outside `price_band` (near-certain windows) -> pull; nothing to earn.

Evidence: makers +0.8c/contract on Kalshi crypto/macro (Bartlett & O'Hara
2026); crypto 15-min series carry ZERO maker fee on Kalshi and makers are
free on Polymarket. Taker index-lag strategies lose after the 7c fee
(see taker_lag.py baseline).

Failure modes: index feed outage (we pull), vol regime shift inside the
window (sigma underestimates -> adverse selection), reference mismatch
(Coinbase spot vs BRTI/Chainlink composite can diverge several bps around
exchange outages), settlement based on a 60 s *average* not the last print
(we approximate by shortening tau by 30 s).

Targets: Kalshi KXBTC15M / KXETH15M (fee-free maker); Polymarket crypto
up/down (maker free). Needs `Market.meta["window_open_ts"/"window_close_ts"]`
or a parseable ticker (pb.data.feeds.KalshiCryptoWindow); the window open
price is taken from the first index print at/after window open (or
`meta["open_price"]` if the venue supplies it).
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

from pb.core.types import Book, Fill, Market, Trade
from pb.data.feeds import KalshiCryptoWindow, signal_price
from pb.sim.engine import Settlement, Signal, SimAPI, Strategy
from pb.strategies.base import (Quote, QuoteManager, Toxicity, clamp_size, norm_cdf,
                                register, round_tick)


@dataclass
class CryptoMMParams:
    size: float = 10.0
    max_inventory: float = 60.0
    max_abs_delta: float = 40.0          # beyond this, quote only the reducing side
    min_half_spread: float = 0.02
    unc_k: float = 0.5                   # half-spread += unc_k * (sigma*sqrt(tau) in prob units)
    gamma: float = 0.04                  # inventory skew per full inventory
    vol_window: float = 900.0            # seconds of index history for realised vol
    vol_floor: float = 0.00015           # per-second log-return vol floor (~0.9%/hr)
    pull_before_close: float = 90.0
    jump_k: float = 4.0                  # pull if |5s move| > jump_k * sigma_5s
    jump_cooldown: float = 20.0
    signal_max_age: float = 10.0
    twap_weight: float = 0.3             # blend twap60 into spot reference when fresh
    index_signal: str | None = None      # override (default from asset: btc_index/eth_index)
    vpin_max: float = 0.7
    min_touch_depth: float = 3.0
    depth_frac_cap: float = 0.5
    price_band: tuple[float, float] = (0.06, 0.94)
    tick: float = 0.01
    avg_window: float = 60.0             # settlement averaging window length


@register
class CryptoTwapMM(Strategy):
    name = "mm_crypto_twap"

    def __init__(self, params: CryptoMMParams | None = None, markets: list[str] | None = None):
        self.p = params or CryptoMMParams()
        self.markets = set(markets or [])
        self.idx: dict[str, deque[tuple[float, float]]] = {}   # signal name -> (ts, price)
        self.twap: dict[str, tuple[float, float]] = {}         # asset -> (ts, twap)
        self.windows: dict[str, KalshiCryptoWindow] = {}
        self.open_px: dict[str, float] = {}
        self.jump_until: dict[str, float] = {}
        self.tox: dict[str, Toxicity] = {}
        self.qm: QuoteManager | None = None
        self.last_fair: dict[str, float] = {}

    # -- lifecycle --------------------------------------------------------------
    def on_start(self, api: SimAPI) -> None:
        self.qm = QuoteManager(api, self.name, tick=self.p.tick)

    def on_settlement(self, api: SimAPI, s: Settlement) -> None:
        self.qm.pull(s.market_id)
        self.windows.pop(s.market_id, None)
        self.open_px.pop(s.market_id, None)

    def on_market_added(self, api: SimAPI, market: Market) -> None:
        if self.markets:
            self.markets.add(market.market_id)
        self.windows.pop(market.market_id, None)   # (re)derive the window from fresh meta

    def on_market_removed(self, api: SimAPI, market_id: str) -> None:
        if self.qm is not None:
            self.qm.pull(market_id)
        self.markets.discard(market_id)
        for d in (self.windows, self.open_px, self.jump_until, self.tox, self.last_fair):
            d.pop(market_id, None)

    def on_trade(self, api: SimAPI, t: Trade) -> None:
        self.tox.setdefault(t.market_id, Toxicity()).on_trade(t)

    def on_fill(self, api: SimAPI, f: Fill) -> None:
        b = api.book(f.market_id)
        if b is not None:
            self._quote(api, b)

    # -- signals ----------------------------------------------------------------
    def on_signal(self, api: SimAPI, sig: Signal) -> None:
        px = signal_price(sig)
        if px is None or px <= 0:
            return
        if sig.name.endswith("_index"):
            h = self.idx.setdefault(sig.name, deque(maxlen=20000))
            h.append((sig.ts, px))
            while h and sig.ts - h[0][0] > self.p.vol_window:
                h.popleft()
            asset = sig.name.split("_")[0].upper()
            # capture window open prices
            for mid, w in self.windows.items():
                if w.asset == asset and mid not in self.open_px and sig.ts >= w.open_ts:
                    self.open_px[mid] = px
            # jump guard
            for mid, w in self.windows.items():
                if w.asset == asset and self._jumped(h, sig.ts):
                    self.jump_until[mid] = sig.ts + self.p.jump_cooldown
            for mid in list(self.windows):
                if self.windows[mid].asset == asset:
                    b = api.book(mid)
                    if b is not None:
                        self._quote(api, b)
        elif sig.name == "twap60":
            asset = ""
            if isinstance(sig.value, dict):
                asset = str(sig.value.get("asset", "")).upper()
            if asset:
                self.twap[asset] = (sig.ts, px)

    def _jumped(self, h: deque[tuple[float, float]], now: float) -> bool:
        if len(h) < 10:
            return False
        last = h[-1][1]
        ref = next((p for t, p in reversed(h) if now - t >= 5.0), None)
        if ref is None:
            return False
        move = abs(math.log(last / ref))
        sig5 = self._sigma(h) * math.sqrt(5.0)
        return move > self.p.jump_k * sig5

    def _sigma(self, h: deque[tuple[float, float]]) -> float:
        """Per-second log-return vol from irregularly spaced prints."""
        if len(h) < 5:
            return self.p.vol_floor
        var = 0.0
        tsum = 0.0
        prev_t, prev_p = h[0]
        for t, p in list(h)[1:]:
            dt = t - prev_t
            if dt <= 0 or p <= 0 or prev_p <= 0:
                continue
            var += math.log(p / prev_p) ** 2
            tsum += dt
            prev_t, prev_p = t, p
        if tsum <= 0:
            return self.p.vol_floor
        return max(self.p.vol_floor, math.sqrt(var / tsum))

    # -- fair value -------------------------------------------------------------
    def _window(self, api: SimAPI, mid: str) -> KalshiCryptoWindow | None:
        w = self.windows.get(mid)
        if w is None:
            m = api.market(mid)
            if m is None:
                return None
            w = KalshiCryptoWindow.from_market(m)
            if not w.ok or not w.asset:
                return None
            self.windows[mid] = w
            op = (m.meta or {}).get("open_price")
            if op:
                try:
                    self.open_px[mid] = float(op)
                except (TypeError, ValueError):
                    pass
        return w

    def fair(self, api: SimAPI, mid: str) -> tuple[float | None, float]:
        """(P(up), uncertainty in prob units) or (None, 0) if not computable."""
        w = self._window(api, mid)
        if w is None:
            return None, 0.0
        name = self.p.index_signal or w.strike_signal
        h = self.idx.get(name)
        if not h or api.now - h[-1][0] > self.p.signal_max_age:
            return None, 0.0
        spot = h[-1][1]
        tw = self.twap.get(w.asset)
        if tw and api.now - tw[0] <= self.p.signal_max_age and self.p.twap_weight > 0:
            spot = (1 - self.p.twap_weight) * spot + self.p.twap_weight * tw[1]
        if mid not in self.open_px:
            # first print after open not seen yet: use the earliest print we hold if it's after open
            cand = next((p for t, p in h if t >= w.open_ts), None)
            if cand is None:
                return None, 0.0
            self.open_px[mid] = cand
        op = self.open_px[mid]
        if op <= 0:
            return None, 0.0
        tau = max(w.close_ts - api.now - self.p.avg_window / 2, 0.0)
        sigma = self._sigma(h)
        z = math.log(spot / op)
        if tau <= 1e-9:
            return (1.0 if z > 0 else 0.0), 0.0
        s = sigma * math.sqrt(tau)
        p = norm_cdf(z / s)
        # uncertainty of p w.r.t. a one-sigma move of the index over the next 5s
        unc = abs(norm_cdf((z + sigma * math.sqrt(5)) / s) - p)
        return p, unc

    # -- quoting ------------------------------------------------------------------
    def on_book(self, api: SimAPI, b: Book) -> None:
        if self.markets and b.market_id not in self.markets:
            return
        self._quote(api, b)

    def _quote(self, api: SimAPI, b: Book) -> None:
        p = self.p
        mid = b.market_id
        w = self._window(api, mid)
        pull = w is None
        if not pull:
            if w.close_ts - api.now < p.pull_before_close:
                pull = True
            elif api.now < self.jump_until.get(mid, -math.inf):
                pull = True
        tox = self.tox.get(mid)
        if tox is not None and tox.vpin > p.vpin_max:
            pull = True
        if b.best_bid is None or b.best_ask is None:
            pull = True
        elif b.bids[0].size < p.min_touch_depth or b.asks[0].size < p.min_touch_depth:
            pull = True
        fair, unc = (None, 0.0) if pull else self.fair(api, mid)
        if fair is None or not (p.price_band[0] <= fair <= p.price_band[1]):
            pull = True
        if pull:
            self.qm.pull(mid)
            return
        self.last_fair[mid] = fair
        inv = api.position(mid).contracts
        half = max(p.min_half_spread, p.unc_k * unc)
        if tox is not None:
            half *= 1 + tox.vpin
        centre = fair - p.gamma * (inv / p.max_inventory)
        bid = centre - half
        ask = centre + half
        # flatten rule: only quote the reducing side, allowed up to one tick inside the touch
        if inv > p.max_abs_delta:
            bid = None
            ask = max(min(ask, b.best_ask - p.tick), b.best_bid + p.tick)
        elif inv < -p.max_abs_delta:
            ask = None
            bid = min(max(bid, b.best_bid + p.tick), b.best_ask - p.tick)
        # never cross
        if bid is not None:
            bid = round_tick(min(bid, b.best_ask - p.tick), p.tick)
        if ask is not None:
            ask = round_tick(max(ask, b.best_bid + p.tick), p.tick)
        if bid is not None and ask is not None and ask - bid < p.tick:
            self.qm.pull(mid)
            return
        bid_sz = clamp_size(p.size, p.depth_frac_cap * b.bids[0].size, max(0.0, p.max_inventory - inv))
        ask_sz = clamp_size(p.size, p.depth_frac_cap * b.asks[0].size, max(0.0, p.max_inventory + inv))
        if inv > p.max_abs_delta:
            ask_sz = clamp_size(min(abs(inv), 2 * p.size), p.depth_frac_cap * b.asks[0].size)
        elif inv < -p.max_abs_delta:
            bid_sz = clamp_size(min(abs(inv), 2 * p.size), p.depth_frac_cap * b.bids[0].size)
        self.qm.set(mid, Quote(bid if bid_sz > 0 else None, ask if ask_sz > 0 else None, bid_sz, ask_sz))
