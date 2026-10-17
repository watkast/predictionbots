"""Model 7 — Complete-set arbitrage (same venue), taker IOC, sized to depth.

Two shapes, both held to settlement (no merge/redeem modelled, so capital is
locked until resolution and the profit is the settlement payoff minus cost):

1. **Binary complete set**: YES ask + NO ask < 1 - fees. In our YES-leg
   convention the NO ask is 1 - YES bid, so this is a *crossed* book
   (best_bid > best_ask), which happens transiently on Kalshi where the YES
   and NO books are separate. We lift the ask and hit the bid with IOC orders
   for min(depth) contracts; the position nets to zero and the realised pnl is
   bid - ask - both taker fees.
2. **Multi-outcome**: markets sharing `Market.event_id` whose outcomes are
   mutually exclusive and exhaustive (`meta["mutually_exclusive"]` truthy,
   or `assume_exclusive=True`). If sum of YES asks < 1 - fees - `min_edge` we
   buy YES on every leg (one leg pays 1); if sum of YES bids > 1 + fees +
   `min_edge` we sell YES on every leg (collect sum(bids), pay out 1).
   Size = min over legs of fillable depth at our limit (walked through the
   recorded levels, so a 1-contract leg caps the whole set) times
   `depth_frac`. All legs are sent as IOC; a partially filled set leaves a
   residual directional position that we flatten with `flatten_residual`
   (IOC at the touch) rather than hold - that is the main failure mode.

Fees: taker fee per leg from the engine's schedule (Kalshi 0.07*p(1-p)
rounded up per order; Polymarket per-category rate). Because Kalshi rounds
each order's fee UP to the cent, tiny sizes are fee-dominated: `min_size`.

Evidence: complete-set mispricings exist mostly in thin multi-outcome
events and are small/fleeting; taker fees of 7c*p(1-p) per leg kill most
of them (needs >~3.5c of gross edge on a 2-leg set at p=0.5). Included
because it is risk-free when fully filled and the simulator's depth-walking
makes the fill assumption honest.
Failure modes: legging risk (IOC partial fills), non-exhaustive event sets
(an "other" outcome not listed -> ΣYES may legitimately be < 1), capital
lock until resolution, stale sibling books.

Targets: Kalshi multi-market events (candidate/outcome ladders), Polymarket
neg-risk events (where the venue's own CTF merge would be the real exit).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from pb.core.types import Action, Book, Market, Order, TIF
from pb.sim.engine import Fill, Settlement, SimAPI, Strategy
from pb.strategies.base import register, taker_fee_per_contract, walk_cost


@dataclass
class CompleteSetParams:
    min_edge: float = 0.005            # net of fees, per set
    max_size: float = 100.0
    min_size: float = 5.0              # below this Kalshi's cent rounding dominates
    depth_frac: float = 0.8            # take at most this fraction of the binding depth
    max_sets_per_event: float = 500.0  # total contracts per event
    assume_exclusive: bool = False
    cooldown: float = 2.0              # seconds between attempts on the same event
    flatten_residual: bool = True
    slippage_pad: float = 0.0          # extra price allowance per leg beyond walked avg


@register
class CompleteSetArb(Strategy):
    name = "complete_set_arb"

    def __init__(self, params: CompleteSetParams | None = None, markets: list[str] | None = None):
        self.p = params or CompleteSetParams()
        self.markets = set(markets or [])
        self.events: dict[str, set[str]] = {}
        self.expected: dict[str, set[str]] = {}   # event -> all sibling ids known at start
        self.last_try: dict[str, float] = {}
        self.sets_done: dict[str, float] = {}
        self.pending: dict[str, dict[str, float]] = {}   # event -> {market: expected size}
        self.opportunities: list[dict] = []

    def on_settlement(self, api: SimAPI, s: Settlement) -> None:
        pass

    def on_market_added(self, api: SimAPI, market: Market) -> None:
        if self.markets:
            self.markets.add(market.market_id)
        if market.event_id:
            self.events.setdefault(market.event_id, set()).add(market.market_id)
            self.expected.setdefault(market.event_id, set()).add(market.market_id)

    def on_market_removed(self, api: SimAPI, market_id: str) -> None:
        self.markets.discard(market_id)
        self.last_try.pop("bin:" + market_id, None)
        for ev, mids in list(self.events.items()):
            mids.discard(market_id)
            self.expected.get(ev, set()).discard(market_id)
            if not mids:
                self.events.pop(ev, None)
                self.expected.pop(ev, None)
                self.pending.pop(ev, None)

    def on_book(self, api: SimAPI, b: Book) -> None:
        if self.markets and b.market_id not in self.markets:
            return
        m = api.market(b.market_id)
        if m is None:
            return
        self._binary(api, b, m)
        if m.event_id:
            self.events.setdefault(m.event_id, set()).add(b.market_id)
            self._multi(api, m.event_id)

    def on_start(self, api: SimAPI) -> None:
        # Know the full outcome set up front: a set is only complete if EVERY
        # sibling the runner knows about has a book; quoting on a subset buys
        # a non-exhaustive set (the classic "sum < 1 because an outcome is missing").
        for mid in self.markets:
            m = api.market(mid)
            if m is not None and m.event_id:
                self.events.setdefault(m.event_id, set()).add(mid)
                self.expected.setdefault(m.event_id, set()).add(mid)

    def on_fill(self, api: SimAPI, f: Fill) -> None:
        pass

    # -- binary crossed book ---------------------------------------------------------
    def _binary(self, api: SimAPI, b: Book, m: Market) -> None:
        if b.best_bid is None or b.best_ask is None or b.best_bid <= b.best_ask:
            return
        key = "bin:" + b.market_id
        if api.now - self.last_try.get(key, -math.inf) < self.p.cooldown:
            return
        size = min(self.p.max_size, self.p.depth_frac * min(b.bids[0].size, b.asks[0].size))
        if size < self.p.min_size:
            return
        avg_a, fa = walk_cost(b.asks, size)
        avg_b, fb = walk_cost(b.bids, size)
        size = min(fa, fb, size)
        if size < self.p.min_size:
            return
        fee = taker_fee_per_contract(api, b.market_id, avg_a) + taker_fee_per_contract(api, b.market_id, avg_b)
        edge = avg_b - avg_a - fee
        if edge < self.p.min_edge:
            return
        self.last_try[key] = api.now
        self.opportunities.append({"ts": api.now, "kind": "binary", "market": b.market_id, "edge": edge, "size": size})
        api.place(Order(b.market_id, Action.BUY, self._limit_for(b.asks, size), size, tif=TIF.IOC, strategy=self.name))
        api.place(Order(b.market_id, Action.SELL, self._limit_for(b.bids, size), size, tif=TIF.IOC, strategy=self.name))

    # -- multi-outcome ---------------------------------------------------------------
    def _exclusive(self, api: SimAPI, mids: set[str]) -> bool:
        if self.p.assume_exclusive:
            return True
        for mid in mids:
            m = api.market(mid)
            if m is not None and (m.meta or {}).get("mutually_exclusive"):
                return True
        return False

    def _multi(self, api: SimAPI, event_id: str) -> None:
        mids = self.events.get(event_id, set())
        if len(mids) < 2 or not self._exclusive(api, mids):
            return
        if event_id in self.expected and not self.expected[event_id] <= mids:
            return
        if api.now - self.last_try.get(event_id, -math.inf) < self.p.cooldown:
            return
        if self.sets_done.get(event_id, 0.0) >= self.p.max_sets_per_event:
            return
        books = {mid: api.book(mid) for mid in mids}
        if any(b is None or not b.bids or not b.asks for b in books.values()):
            return
        room = self.p.max_sets_per_event - self.sets_done.get(event_id, 0.0)
        # --- buy all YES ---
        size = min([self.p.max_size, room] + [self.p.depth_frac * b.asks[0].size for b in books.values()])
        if size >= self.p.min_size:
            legs = {}
            ok = True
            total = 0.0
            fees = 0.0
            for mid, b in books.items():
                avg, filled = walk_cost(b.asks, size)
                if filled < size - 1e-9:
                    ok = False
                    break
                legs[mid] = (avg, self._limit_for(b.asks, size))
                total += avg
                fees += taker_fee_per_contract(api, mid, avg)
            if ok and 1.0 - total - fees >= self.p.min_edge:
                self._fire(api, event_id, Action.BUY, legs, size, 1.0 - total - fees)
                return
        # --- sell all YES ---
        size = min([self.p.max_size, room] + [self.p.depth_frac * b.bids[0].size for b in books.values()])
        if size >= self.p.min_size:
            legs = {}
            ok = True
            total = 0.0
            fees = 0.0
            for mid, b in books.items():
                avg, filled = walk_cost(b.bids, size)
                if filled < size - 1e-9:
                    ok = False
                    break
                legs[mid] = (avg, self._limit_for(b.bids, size))
                total += avg
                fees += taker_fee_per_contract(api, mid, avg)
            if ok and total - 1.0 - fees >= self.p.min_edge:
                self._fire(api, event_id, Action.SELL, legs, size, total - 1.0 - fees)

    @staticmethod
    def _limit_for(levels, size: float) -> float:
        acc = 0.0
        for lvl in levels:
            acc += lvl.size
            if acc >= size - 1e-9:
                return lvl.price
        return levels[-1].price

    def _fire(self, api: SimAPI, event_id: str, action: Action, legs: dict[str, tuple[float, float]],
              size: float, edge: float) -> None:
        self.last_try[event_id] = api.now
        self.sets_done[event_id] = self.sets_done.get(event_id, 0.0) + size
        self.opportunities.append({"ts": api.now, "kind": "multi", "event": event_id, "action": action.value,
                                   "legs": len(legs), "edge": edge, "size": size})
        before = {mid: api.position(mid).contracts for mid in legs}
        for mid, (avg, limit) in legs.items():
            px = limit + (self.p.slippage_pad if action is Action.BUY else -self.p.slippage_pad)
            api.place(Order(mid, action, px, size, tif=TIF.IOC, strategy=self.name))
        if self.p.flatten_residual:
            api.schedule(1.0, lambda: self._flatten(api, legs, before, action, size))

    def _flatten(self, api: SimAPI, legs: dict, before: dict, action: Action, size: float) -> None:
        """If legs filled unevenly, cut every leg back to the smallest filled size."""
        got = {mid: abs(api.position(mid).contracts - before[mid]) for mid in legs}
        if not got:
            return
        lo = min(got.values())
        for mid, g in got.items():
            excess = g - lo
            if excess < 1e-9:
                continue
            b = api.book(mid)
            if b is None:
                continue
            if action is Action.BUY and b.best_bid is not None:
                api.place(Order(mid, Action.SELL, b.best_bid, excess, tif=TIF.IOC, strategy=self.name))
            elif action is Action.SELL and b.best_ask is not None:
                api.place(Order(mid, Action.BUY, b.best_ask, excess, tif=TIF.IOC, strategy=self.name))
