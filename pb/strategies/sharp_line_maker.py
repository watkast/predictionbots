"""Model 6 — Sharp-line maker for sports markets.

Mechanism
---------
Prediction-market sports mids track the de-vigged Pinnacle line within
0.1-0.75 points, so there is no edge in TAKING at the market; the edge is
being the resting liquidity around the sharp line while retail crosses the
spread. We consume `sharp_prob` (de-vigged Pinnacle, falling back to a
DK/FD consensus - see pb.data.feeds.sharp_signals_from_odds) and quote

    bid = fair - half_spread,   ask = fair + half_spread

post-only, one tick inside the touch if that still leaves our required
margin (`join_only` keeps us at the touch). Kalshi sports series charge a
MAKER fee of 0.0175 * p(1-p) per contract, so the half-spread must satisfy
half_spread >= maker_fee(p) + `edge_min`; we compute the fee from the
engine's schedule (zero on Polymarket, where makers are free).

Gates: signal older than `max_age` (sharp lines move on injury news - a
stale line is poison) -> pull; `game_state` signal == "in" (live) -> pull
unless `allow_live`; the last `pull_before_close` seconds; book mid more
than `max_divergence` from the sharp line (someone knows something, or the
link is wrong) -> pull; toxicity (VPIN) widens and eventually pulls.

Inventory skew as in the inventory MM.

Evidence: sports mids = de-vigged Pinnacle within 0.1-0.75pt; makers the
only profitable cohort; favourite-longshot bias REVERSES in sports so no
directional lean is applied. Kalshi sports maker fee makes the minimum
viable half-spread ~0.5c at p=0.5 plus edge.
Failure modes: wrong market<->game link (divergence gate), stale sharp line
during lineup news, live-game sniping (gate), parlay-leg markets (overpriced
~3%/leg - not handled here).

Targets: Kalshi KXNFL/KXNBA/KXMLB/... game lines (maker fee), Polymarket
sports (maker free). Needs an odds feed with `OddsLink`s.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from pb.core.types import Book, Fill, Trade
from pb.sim.engine import Settlement, Signal, SimAPI, Strategy
from pb.strategies.base import (Quote, QuoteManager, SignalCache, Toxicity, clamp_size,
                                maker_fee_per_contract, register, round_tick, secs_to_close)


@dataclass
class SharpLineParams:
    size: float = 10.0
    max_inventory: float = 50.0
    half_spread: float = 0.02
    edge_min: float = 0.005            # on top of maker fee
    gamma: float = 0.03
    max_age: float = 180.0
    allow_live: bool = False
    pull_before_close: float = 300.0
    max_divergence: float = 0.06       # |book mid - sharp| beyond which we pull
    vpin_max: float = 0.7
    join_only: bool = False
    min_touch_depth: float = 2.0
    depth_frac_cap: float = 0.5
    price_band: tuple[float, float] = (0.05, 0.95)
    tick: float = 0.01


@register
class SharpLineMaker(Strategy):
    name = "sharp_line_maker"

    def __init__(self, params: SharpLineParams | None = None, markets: list[str] | None = None):
        self.p = params or SharpLineParams()
        self.markets = set(markets or [])
        self.sharp = SignalCache()
        self.state: dict[str, str] = {}
        self.tox: dict[str, Toxicity] = {}
        self.qm: QuoteManager | None = None

    def on_start(self, api: SimAPI) -> None:
        self.qm = QuoteManager(api, self.name, tick=self.p.tick)

    def on_settlement(self, api: SimAPI, s: Settlement) -> None:
        self.qm.pull(s.market_id)

    def on_trade(self, api: SimAPI, t: Trade) -> None:
        self.tox.setdefault(t.market_id, Toxicity()).on_trade(t)

    def on_fill(self, api: SimAPI, f: Fill) -> None:
        b = api.book(f.market_id)
        if b is not None:
            self._quote(api, b)

    def on_signal(self, api: SimAPI, sig: Signal) -> None:
        if not sig.market_id:
            return
        if sig.name == "sharp_prob":
            v = sig.value.get("p") if isinstance(sig.value, dict) else sig.value
            try:
                self.sharp.put(sig.market_id, sig.ts, float(v))
            except (TypeError, ValueError):
                return
        elif sig.name == "game_state":
            self.state[sig.market_id] = str(sig.value)
        else:
            return
        b = api.book(sig.market_id)
        if b is not None:
            self._quote(api, b)

    def on_book(self, api: SimAPI, b: Book) -> None:
        if self.markets and b.market_id not in self.markets:
            return
        self._quote(api, b)

    def min_half_spread(self, api: SimAPI, mid: str, fair: float) -> float:
        return max(self.p.half_spread, maker_fee_per_contract(api, mid, fair) + self.p.edge_min)

    def _quote(self, api: SimAPI, b: Book) -> None:
        p = self.p
        mid = b.market_id
        fair = self.sharp.get(mid, api.now, p.max_age)
        pull = fair is None or b.mid is None
        if not pull:
            if self.state.get(mid) == "in" and not p.allow_live:
                pull = True
            elif self.state.get(mid) == "post":
                pull = True
            elif secs_to_close(api, mid) < p.pull_before_close:
                pull = True
            elif abs(b.mid - fair) > p.max_divergence:
                pull = True
            elif not (p.price_band[0] <= fair <= p.price_band[1]):
                pull = True
            elif b.bids[0].size < p.min_touch_depth or b.asks[0].size < p.min_touch_depth:
                pull = True
        tox = self.tox.get(mid)
        if tox is not None and tox.vpin > p.vpin_max:
            pull = True
        if pull:
            self.qm.pull(mid)
            return
        inv = api.position(mid).contracts
        half = self.min_half_spread(api, mid, fair)
        if tox is not None:
            half *= 1 + tox.vpin
        centre = fair - p.gamma * (inv / p.max_inventory)
        bid = centre - half
        ask = centre + half
        bid = min(bid, b.best_ask - p.tick)
        ask = max(ask, b.best_bid + p.tick)
        if p.join_only:
            bid = min(bid, b.best_bid)
            ask = max(ask, b.best_ask)
        bid = round_tick(bid, p.tick)
        ask = round_tick(ask, p.tick)
        # re-check the margin after clamping to the touch: never post inside fee+edge
        if fair - bid < half - 1e-9:
            bid = None
        if ask - fair < half - 1e-9:
            ask = None
        if bid is None and ask is None:
            self.qm.pull(mid)
            return
        bid_sz = clamp_size(p.size, p.depth_frac_cap * b.bids[0].size, max(0.0, p.max_inventory - inv))
        ask_sz = clamp_size(p.size, p.depth_frac_cap * b.asks[0].size, max(0.0, p.max_inventory + inv))
        self.qm.set(mid, Quote(bid if bid_sz > 0 else None, ask if ask_sz > 0 else None, bid_sz, ask_sz))
