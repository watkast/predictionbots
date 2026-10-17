"""Baseline T2 — Momentum TAKER: buy after a 20c move.

Deliberately a taker strategy that the research expects to LOSE after fees
(taker fee + spread + the ~29% of moves that round-trip). It is included so
the backtest report can show the number rather than assert it.

Mechanism: if the mid rose by >= `move` (default 0.20) over `window`
seconds, buy YES at the ask with an IOC sized to `depth_frac` of the
depth within `max_walk`; if it fell by >= `move`, sell YES (buy NO).
Hold for `hold` seconds or until the move continues by `tp` (take profit at
the touch, IOC) or reverses by `stop` (stop at the touch, IOC); otherwise
hold to settlement if `hold_to_settlement`. One entry per market per
`cooldown`. Gated off inside `no_trade_before_close`.

Failure modes: everything a taker faces - paying spread + 7c*p(1-p) fee on
entry and again on exit, chasing moves that were already fully priced,
adverse selection by makers who see the same move. Disabled on crypto 15-min
series by default (a 20c move there is settlement information, not momentum).
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

from pb.core.types import Action, Book, Market, Order, TIF
from pb.sim.engine import Fill, Settlement, SimAPI, Strategy
from pb.strategies.base import clamp_size, register, secs_to_close


@dataclass
class TakerMomentumParams:
    move: float = 0.20
    window: float = 900.0
    size: float = 10.0
    depth_frac: float = 0.5
    max_walk: float = 0.02
    hold: float = 3600.0
    tp: float = 0.10
    stop: float = 0.10
    hold_to_settlement: bool = False
    cooldown: float = 3600.0
    no_trade_before_close: float = 300.0
    price_band: tuple[float, float] = (0.05, 0.95)
    disable_series_prefixes: tuple[str, ...] = ("KXBTC", "KXETH", "crypto")


@register
class TakerMomentum(Strategy):
    name = "taker_momentum"

    def __init__(self, params: TakerMomentumParams | None = None, markets: list[str] | None = None):
        self.p = params or TakerMomentumParams()
        self.markets = set(markets or [])
        self.mids: dict[str, deque[tuple[float, float]]] = {}
        self.entries: dict[str, tuple[float, float, int]] = {}   # mid -> (ts, entry_mid, direction)
        self.last: dict[str, float] = {}
        self.takes: list[dict] = []

    def on_settlement(self, api: SimAPI, s: Settlement) -> None:
        self.entries.pop(s.market_id, None)

    def on_market_added(self, api: SimAPI, market: Market) -> None:
        if self.markets:
            self.markets.add(market.market_id)

    def on_market_removed(self, api: SimAPI, market_id: str) -> None:
        self.markets.discard(market_id)
        for d in (self.mids, self.entries, self.last):
            d.pop(market_id, None)

    def enabled(self, api: SimAPI, mid: str) -> bool:
        m = api.market(mid)
        if m is None:
            return True
        s = (m.series or m.market_id or "").upper()
        return not s.startswith(tuple(x.upper() for x in self.p.disable_series_prefixes))

    def on_book(self, api: SimAPI, b: Book) -> None:
        if self.markets and b.market_id not in self.markets:
            return
        if b.mid is None:
            return
        p = self.p
        mid = b.market_id
        h = self.mids.setdefault(mid, deque(maxlen=5000))
        h.append((b.ts, b.mid))
        while h and b.ts - h[0][0] > p.window:
            h.popleft()
        pos = api.position(mid).contracts
        ent = self.entries.get(mid)
        if ent is not None and pos != 0:
            t0, m0, d = ent
            pnl_move = (b.mid - m0) * d
            exit_ = (pnl_move >= p.tp) or (pnl_move <= -p.stop) or \
                    (not p.hold_to_settlement and api.now - t0 >= p.hold) or \
                    secs_to_close(api, mid) < p.no_trade_before_close
            if exit_:
                act = Action.SELL if pos > 0 else Action.BUY
                px = (b.best_bid - p.max_walk) if act is Action.SELL else (b.best_ask + p.max_walk)
                if px is not None:
                    api.place(Order(mid, act, px, abs(pos), tif=TIF.IOC, strategy=self.name))
                    self.entries.pop(mid, None)
            return
        if ent is not None and pos == 0:
            self.entries.pop(mid, None)
        if not self.enabled(api, mid) or secs_to_close(api, mid) < p.no_trade_before_close:
            return
        if api.now - self.last.get(mid, -math.inf) < p.cooldown:
            return
        if not (p.price_band[0] <= b.mid <= p.price_band[1]):
            return
        ref = h[0][1]
        move = b.mid - ref
        if abs(move) < p.move or b.best_ask is None or b.best_bid is None:
            return
        if move > 0:
            depth = b.depth_within(Action.BUY, p.max_walk)
            sz = clamp_size(p.size, p.depth_frac * depth)
            if sz > 0:
                api.place(Order(mid, Action.BUY, b.best_ask + p.max_walk, sz, tif=TIF.IOC, strategy=self.name))
                self.entries[mid] = (api.now, b.mid, +1)
        else:
            depth = b.depth_within(Action.SELL, p.max_walk)
            sz = clamp_size(p.size, p.depth_frac * depth)
            if sz > 0:
                api.place(Order(mid, Action.SELL, b.best_bid - p.max_walk, sz, tif=TIF.IOC, strategy=self.name))
                self.entries[mid] = (api.now, b.mid, -1)
        self.last[mid] = api.now
        self.takes.append({"ts": api.now, "market": mid, "move": move})
