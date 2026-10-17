"""Model 1 — Inventory-aware, toxicity-gated passive market maker.

The only strategy family with large-sample evidence of positive expectancy on
both Kalshi (makers +1.9c/contract on single-name markets, Bartlett & O'Hara
2026) and Polymarket (~70% of active makers profitable, TUM 2025).

Mechanics
---------
* Fair value = microprice of the book, optionally blended with an external
  reference (`fair_signal`, e.g. a weather-model probability, a de-vigged
  sharp sportsbook line, or a TWAP-implied P(up) for 15-min crypto).
* Half-spread = max(min_half_spread, k * sigma) where sigma is a short-window
  realised volatility of the mid; widened by toxicity (VPIN) and shrunk
  toward the touch when competition is thin.
* Inventory skew (Avellaneda-Stoikov flavour): quote centre shifts against
  inventory by `gamma * inventory / max_inv`.
* Quote-pull gates: VPIN > vpin_max, print-rate spike, last `pull_before_close`
  seconds (settlement sniping), reference signal stale, book too thin to be
  real, spread too tight to earn fee+edge.
* Sizes capped by a fraction of the resting depth at the touch so we never
  pretend to be bigger than the market.

Every parameter is explicit so the optimiser/agent can sweep them.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

from pb.core.types import Book, Fill, Market, Trade
from pb.sim.engine import Settlement, Signal, SimAPI
from pb.sim.engine import Strategy
from pb.strategies.base import Quote, QuoteManager, Toxicity, register, round_tick


@dataclass
class MMParams:
    size: float = 10.0
    max_inventory: float = 50.0
    min_half_spread: float = 0.01
    vol_k: float = 1.5
    vol_window: float = 300.0
    gamma: float = 0.02           # inventory skew in price per full inventory
    vpin_max: float = 0.6
    print_rate_max: float = 1.0   # prints/sec over 60s that we consider a storm
    pull_before_close: float = 180.0
    fair_signal: str | None = None       # name of Signal to blend as fair value
    fair_weight: float = 0.5
    signal_max_age: float = 120.0
    min_touch_depth: float = 5.0         # don't quote into an empty/fake book
    depth_frac_cap: float = 0.5          # size <= this * touch depth
    join_only: bool = False              # never improve the touch
    edge_min: float = 0.0                # require (fair - bid) >= edge_min etc.
    price_band: tuple[float, float] = (0.05, 0.95)
    tick: float = 0.01


@register
class InventoryMM(Strategy):
    name = "mm_inventory"

    def __init__(self, params: MMParams | None = None, markets: list[str] | None = None):
        self.p = params or MMParams()
        self.markets = set(markets or [])
        self.tox: dict[str, Toxicity] = {}
        self.mids: dict[str, deque[tuple[float, float]]] = {}
        self.signals: dict[str, tuple[float, float]] = {}
        self.qm: QuoteManager | None = None

    # -- lifecycle ------------------------------------------------------------
    def on_start(self, api: SimAPI) -> None:
        self.qm = QuoteManager(api, self.name, tick=self.p.tick)

    def on_signal(self, api: SimAPI, sig: Signal) -> None:
        if self.p.fair_signal and sig.name == self.p.fair_signal and sig.market_id:
            self.signals[sig.market_id] = (sig.ts, float(sig.value))

    def on_trade(self, api: SimAPI, t: Trade) -> None:
        self.tox.setdefault(t.market_id, Toxicity()).on_trade(t)

    def on_settlement(self, api: SimAPI, s: Settlement) -> None:
        self.qm.pull(s.market_id)

    def on_market_added(self, api: SimAPI, market: Market) -> None:
        if self.markets:
            self.markets.add(market.market_id)

    def on_market_removed(self, api: SimAPI, market_id: str) -> None:
        if self.qm is not None:
            self.qm.pull(market_id)
        self.markets.discard(market_id)
        for d in (self.tox, self.mids, self.signals):
            d.pop(market_id, None)

    def on_fill(self, api: SimAPI, f: Fill) -> None:
        b = api.book(f.market_id)
        if b is not None:
            self._quote(api, b)

    # -- core -------------------------------------------------------------------
    def on_book(self, api: SimAPI, b: Book) -> None:
        if self.markets and b.market_id not in self.markets:
            return
        self._quote(api, b)

    def _sigma(self, mid_hist: deque[tuple[float, float]]) -> float:
        if len(mid_hist) < 3:
            return 0.0
        vals = [m for _, m in mid_hist]
        d = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
        mu = sum(d) / len(d)
        return math.sqrt(sum((x - mu) ** 2 for x in d) / len(d))

    def _quote(self, api: SimAPI, b: Book) -> None:
        p = self.p
        m = api.market(b.market_id)
        hist = self.mids.setdefault(b.market_id, deque(maxlen=600))
        if b.mid is not None:
            hist.append((b.ts, b.mid))
            while hist and b.ts - hist[0][0] > p.vol_window:
                hist.popleft()

        # ---- gates -------------------------------------------------------------
        pull = False
        if b.mid is None or b.spread is None:
            pull = True
        elif m is not None and m.close_ts and (m.close_ts - api.now) < p.pull_before_close:
            pull = True
        elif b.bids[0].size < p.min_touch_depth or b.asks[0].size < p.min_touch_depth:
            pull = True
        tox = self.tox.get(b.market_id)
        if tox is not None and (tox.vpin > p.vpin_max or tox.print_rate(api.now) > p.print_rate_max):
            pull = True
        fair = b.microprice()
        if p.fair_signal:
            s = self.signals.get(b.market_id)
            if s is None or api.now - s[0] > p.signal_max_age:
                pull = True
            else:
                fair = (1 - p.fair_weight) * fair + p.fair_weight * s[1]
        if fair is None or not (p.price_band[0] <= fair <= p.price_band[1]):
            pull = True
        if pull:
            self.qm.pull(b.market_id)
            return

        # ---- quote construction -------------------------------------------
        inv = api.position(b.market_id).contracts
        sigma = self._sigma(hist)
        half = max(p.min_half_spread, p.vol_k * sigma)
        if tox is not None:
            half *= (1 + tox.vpin)
        centre = fair - p.gamma * (inv / p.max_inventory)
        bid = centre - half - p.edge_min
        ask = centre + half + p.edge_min
        # never cross; optionally never improve the touch
        bid = min(bid, b.best_ask - p.tick)
        ask = max(ask, b.best_bid + p.tick)
        if p.join_only:
            bid = min(bid, b.best_bid)
            ask = max(ask, b.best_ask)
        bid = round_tick(bid, p.tick)
        ask = round_tick(ask, p.tick)
        if ask - bid < p.tick:
            self.qm.pull(b.market_id)
            return

        bid_sz = min(p.size, p.depth_frac_cap * b.bids[0].size, max(0.0, p.max_inventory - inv))
        ask_sz = min(p.size, p.depth_frac_cap * b.asks[0].size, max(0.0, p.max_inventory + inv))
        self.qm.set(b.market_id, Quote(bid if bid_sz >= 1 else None, ask if ask_sz >= 1 else None,
                                        bid_sz, ask_sz))
