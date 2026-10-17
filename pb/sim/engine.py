"""Event-driven, liquidity-realistic simulator.

Design goals (the user's hard requirement: *no fantasy fills*):

* Taker orders are filled ONLY against resting size actually present in the
  recorded order book, level by level, after a configurable latency. The
  consumed size is removed so a second taker in the same snapshot cannot eat
  the same liquidity twice.
* Maker (resting) orders are filled ONLY when a public trade prints at or
  through our price on the taker side that would hit us, and only after the
  resting size that was ahead of us in the queue at placement has been consumed
  by prints. If a later book snapshot shows the market traded through our price
  (touch moved past us) while we had no print data, we assume we were filled
  (that is the adverse case, so it is the conservative assumption).
* Cancels take effect after latency; prints in between can still hit us.
* Fees are charged by the venue's schedule, maker vs taker.
* Positions settle at the market result; unresolved positions are marked at mid.

Events are replayed in timestamp order. A `Feed` is any iterable of events.
"""
from __future__ import annotations

import heapq
import itertools
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Optional

from pb.core.fees import FeeSchedule
from pb.core.types import Action, Book, Fill, Level, Market, Order, TIF, Trade


# ----------------------------------------------------------------------------
# Events
# ----------------------------------------------------------------------------
@dataclass(slots=True)
class Signal:
    """External reference data (crypto index price, forecast, sharp odds...)."""
    ts: float
    name: str
    market_id: str | None
    value: Any


@dataclass(slots=True)
class Settlement:
    ts: float
    market_id: str
    result: float  # 1.0 or 0.0 (YES payoff)


Event = Book | Trade | Signal | Settlement


# ----------------------------------------------------------------------------
# Portfolio
# ----------------------------------------------------------------------------
@dataclass
class Position:
    contracts: float = 0.0    # signed YES contracts (negative = short YES = long NO)
    cost: float = 0.0         # net cash paid to acquire the position (signed)
    realized: float = 0.0
    fees: float = 0.0

    def apply(self, action: Action, price: float, size: float, fee: float) -> None:
        signed = size if action is Action.BUY else -size
        self.fees += fee
        if self.contracts == 0 or (self.contracts > 0) == (signed > 0):
            self.contracts += signed
            self.cost += signed * price
            return
        # reducing / flipping
        avg = self.cost / self.contracts
        closing = min(abs(self.contracts), abs(signed))
        if self.contracts > 0:
            self.realized += closing * (price - avg)
        else:
            self.realized += closing * (avg - price)
        new = self.contracts + signed
        if abs(new) < 1e-12:
            self.contracts, self.cost = 0.0, 0.0
        elif (new > 0) == (self.contracts > 0):
            self.contracts, self.cost = new, new * avg        # partial reduce
        else:
            self.contracts, self.cost = new, new * price      # flipped: new leg at fill price

    @property
    def avg_price(self) -> float:
        return self.cost / self.contracts if self.contracts else 0.0

    def capital_at_risk(self) -> float:
        """Collateral locked: long YES locks cost; short YES (long NO) locks (1-p)*n."""
        if self.contracts > 0:
            return self.cost
        if self.contracts < 0:
            return abs(self.contracts) - abs(self.cost)
        return 0.0


# ----------------------------------------------------------------------------
# Strategy API
# ----------------------------------------------------------------------------
class SimAPI:
    """What a strategy sees. Mirrors the live runner API exactly."""

    def __init__(self, engine: "Engine"):
        self._e = engine

    @property
    def now(self) -> float:
        return self._e.now

    def book(self, market_id: str) -> Optional[Book]:
        return self._e.books.get(market_id)

    def market(self, market_id: str) -> Optional[Market]:
        return self._e.markets.get(market_id)

    def position(self, market_id: str) -> Position:
        return self._e.positions[market_id]

    def open_orders(self, market_id: str | None = None) -> list[Order]:
        return [o for o in self._e.orders.values()
                if market_id is None or o.market_id == market_id]

    def place(self, order: Order) -> str:
        return self._e.submit(order)

    def cancel(self, order_id: str) -> None:
        self._e.cancel(order_id)

    def cancel_all(self, market_id: str | None = None) -> None:
        for o in list(self.open_orders(market_id)):
            self.cancel(o.order_id)

    def schedule(self, delay: float, callback: Callable[[], None]) -> None:
        self._e.schedule(self._e.now + delay, callback)

    def fee(self, market_id: str) -> FeeSchedule:
        """Fee schedule the engine will charge for this market (so strategies can
        require spread >= maker fee + edge, or price taker arbs net of fees)."""
        return self._e.fee_for(market_id)

    def log(self, msg: str) -> None:
        self._e.logs.append((self._e.now, msg))


class Strategy:
    name = "base"

    def on_start(self, api: SimAPI) -> None: ...
    def on_book(self, api: SimAPI, book: Book) -> None: ...
    def on_trade(self, api: SimAPI, trade: Trade) -> None: ...
    def on_signal(self, api: SimAPI, sig: Signal) -> None: ...
    def on_fill(self, api: SimAPI, fill: Fill) -> None: ...
    def on_settlement(self, api: SimAPI, s: Settlement) -> None: ...
    def on_end(self, api: SimAPI) -> None: ...


# ----------------------------------------------------------------------------
# Engine
# ----------------------------------------------------------------------------
@dataclass
class SimConfig:
    order_latency: float = 0.3        # seconds from submit to book interaction
    cancel_latency: float = 0.3
    maker_queue_model: str = "behind"   # "behind": we join the back of the queue
    # Low-fidelity data mode (trade tape + candles, no L2): a maker fill is
    # credited ONLY when a print goes strictly THROUGH our price, never at it.
    maker_requires_through: bool = False
    fill_through_on_cross: bool = True  # treat book crossing our price as a fill
    participation_cap: float = 1.0      # max fraction of a print we may absorb
    max_position_per_market: float = math.inf
    max_capital: float = math.inf       # total collateral cap
    mark_unresolved_at_mid: bool = True
    # Reality guard: a taker order can never take more than this fraction of
    # the total resting size within 5c of the touch (protects against believing
    # a 1-contract book could absorb 500).
    taker_depth_cap_frac: float = 1.0


class Engine:
    def __init__(self, markets: Iterable[Market], fee_for: Callable[[str], FeeSchedule],
                 config: SimConfig | None = None):
        self.cfg = config or SimConfig()
        self.markets: dict[str, Market] = {m.market_id: m for m in markets}
        self.fee_for = fee_for
        self.books: dict[str, Book] = {}
        self.positions: dict[str, Position] = defaultdict(Position)
        self.orders: dict[str, Order] = {}
        self.fills: list[Fill] = []
        self.logs: list[tuple[float, str]] = []
        self.now = 0.0
        self._ids = itertools.count(1)
        self._timers: list[tuple[float, int, Callable[[], None]]] = []
        self._pending: list[tuple[float, int, Callable[[], None]]] = []
        self.strategies: list[Strategy] = []
        self.api = SimAPI(self)
        self.equity_curve: list[tuple[float, float]] = []
        self._last_mark = -math.inf
        self.mark_interval = 60.0
        self.settled: dict[str, float] = {}
        # Reality bookkeeping (parallel to self.fills): was the maker fill an
        # *assumed* fill from the book crossing our price without a print, and
        # how deep was the touch on the side we interacted with at that moment.
        self.fill_context: list[dict] = []
        self._cancelled: set[str] = set()

    # -- public --------------------------------------------------------------
    def add_strategy(self, s: Strategy) -> None:
        self.strategies.append(s)

    def schedule(self, ts: float, cb: Callable[[], None]) -> None:
        heapq.heappush(self._timers, (ts, next(self._ids), cb))

    def submit(self, order: Order) -> str:
        oid = order.order_id or f"o{next(self._ids)}"
        order.order_id = oid
        order.ts = self.now
        if order.size <= 0:
            return oid
        self.schedule(self.now + self.cfg.order_latency, lambda: self._arrive(order))
        return oid

    def cancel(self, order_id: str) -> None:
        # remembered so an order still in flight does not rest after its cancel landed
        self._cancelled.add(order_id)

        def _land() -> None:
            if self.orders.pop(order_id, None) is not None:
                self._cancelled.discard(order_id)   # it had rested; else arrival will drop it

        self.schedule(self.now + self.cfg.cancel_latency, _land)

    def run(self, events: Iterable[Event]) -> "Result":
        for s in self.strategies:
            s.on_start(self.api)
        for ev in events:
            self._advance(ev.ts)
            self._dispatch(ev)
        self._advance(self.now + 1e-9)
        for s in self.strategies:
            s.on_end(self.api)
        return Result(self)

    # -- internals -----------------------------------------------------------
    def _advance(self, ts: float) -> None:
        """Fire timers (order arrivals, cancels, strategy timers) up to ts."""
        while self._timers and self._timers[0][0] <= ts:
            t, _, cb = heapq.heappop(self._timers)
            self.now = max(self.now, t)
            cb()
        self.now = max(self.now, ts)
        if self.now - self._last_mark >= self.mark_interval:
            self.equity_curve.append((self.now, self.equity()))
            self.max_cap = max(getattr(self, "max_cap", 0.0), self.capital_at_risk())
            self._last_mark = self.now

    def _dispatch(self, ev: Event) -> None:
        if isinstance(ev, Book):
            self._on_book(ev)
        elif isinstance(ev, Trade):
            self._on_trade(ev)
        elif isinstance(ev, Settlement):
            self._on_settlement(ev)
        elif isinstance(ev, Signal):
            for s in self.strategies:
                s.on_signal(self.api, ev)

    def _on_book(self, book: Book) -> None:
        self.books[book.market_id] = book
        if self.cfg.fill_through_on_cross and self._tradable(book.market_id, book.ts):
            self._check_cross_fills(book)
        for s in self.strategies:
            s.on_book(self.api, book)

    def _on_trade(self, tr: Trade) -> None:
        if self._tradable(tr.market_id, tr.ts):
            self._maker_fills_from_print(tr)
        for s in self.strategies:
            s.on_trade(self.api, tr)

    def _tradable(self, market_id: str, ts: float | None = None) -> bool:
        """False once a market is settled or past its trading close: nothing can
        fill us there (a book/print after close is a venue artefact, not liquidity)."""
        if market_id in self.settled:
            return False
        m = self.markets.get(market_id)
        if m is not None and m.close_ts:
            t = self.now if ts is None else max(ts, self.now)
            if t > m.close_ts + 1e-9:
                return False
        return True

    def _on_settlement(self, st: Settlement) -> None:
        pos = self.positions[st.market_id]
        m = self.markets.get(st.market_id)
        if m is not None:
            m.result = st.result
            m.settle_ts = st.ts
        self.settled[st.market_id] = st.result
        if pos.contracts != 0:
            # settle at result price with no fee
            pos.apply(Action.SELL if pos.contracts > 0 else Action.BUY,
                      st.result, abs(pos.contracts), 0.0)
        for oid in [o for o, od in self.orders.items() if od.market_id == st.market_id]:
            self.orders.pop(oid, None)
        for s in self.strategies:
            s.on_settlement(self.api, st)

    # -- order arrival ---------------------------------------------------------
    def _arrive(self, order: Order) -> None:
        if order.order_id in self._cancelled:
            self._cancelled.discard(order.order_id)
            return
        if not self._tradable(order.market_id):
            return
        book = self.books.get(order.market_id)
        if book is None:
            if order.tif is TIF.GTC:
                self.orders[order.order_id] = order  # rest blind
            return
        crosses = self._crosses(order, book)
        if order.post_only and crosses:
            return  # rejected
        if crosses:
            self._take(order, book)
        if order.remaining > 1e-9:
            if order.tif is TIF.GTC:
                self._rest(order, book)
            elif order.tif is TIF.FOK and order.filled > 0:
                # FOK partially filled is impossible; undo not modelled -> treat as IOC
                pass

    @staticmethod
    def _crosses(order: Order, book: Book) -> bool:
        if order.action is Action.BUY:
            return book.best_ask is not None and order.price >= book.best_ask - 1e-12
        return book.best_bid is not None and order.price <= book.best_bid + 1e-12

    def _take(self, order: Order, book: Book) -> None:
        levels = book.asks if order.action is Action.BUY else book.bids
        cap = self.cfg.taker_depth_cap_frac * book.depth_within(order.action, 0.05)
        takeable = min(order.remaining, cap) if cap > 0 else 0.0
        if order.tif is TIF.FOK and takeable + 1e-9 < order.size:
            return
        # reality bookkeeping: depth at the touch BEFORE we consume it
        touch_before = levels[0].size if levels else 0.0
        for lvl in levels:
            if takeable <= 1e-9:
                break
            ok = (lvl.price <= order.price + 1e-12) if order.action is Action.BUY \
                else (lvl.price >= order.price - 1e-12)
            if not ok or lvl.size <= 0:
                break
            qty = min(lvl.size, takeable)
            lvl.size -= qty
            takeable -= qty
            self._fill(order, lvl.price, qty, is_maker=False, touch_depth=touch_before)
        # drop empty levels
        if order.action is Action.BUY:
            book.asks = [l for l in book.asks if l.size > 1e-9]
        else:
            book.bids = [l for l in book.bids if l.size > 1e-9]

    def _rest(self, order: Order, book: Book) -> None:
        if not self._allowed(order):
            return
        same = book.bids if order.action is Action.BUY else book.asks
        ahead = 0.0
        for lvl in same:
            if abs(lvl.price - order.price) < 1e-9:
                ahead = lvl.size if self.cfg.maker_queue_model == "behind" else 0.0
                break
        order.queue_ahead = ahead
        self.orders[order.order_id] = order

    def _allowed(self, order: Order) -> bool:
        """Position cap counts the position PLUS every resting order on the same
        side (otherwise N resting orders of size <= cap can fill into N x cap)."""
        pos = self.positions[order.market_id]
        signed = order.remaining if order.action is Action.BUY else -order.remaining
        resting = sum(o.remaining for o in self.orders.values()
                      if o.market_id == order.market_id and o.action is order.action
                      and o.order_id != order.order_id)
        resting_signed = resting if order.action is Action.BUY else -resting
        if abs(pos.contracts + resting_signed + signed) > self.cfg.max_position_per_market + 1e-9:
            return False
        return True

    # -- maker fills -----------------------------------------------------------
    def _maker_fills_from_print(self, tr: Trade) -> None:
        """A print at price p with taker BUY means someone lifted asks up to p:
        every resting ask of ours priced <= p is in line. Size at *our* level is
        consumed queue-first."""
        printed = tr.size * self.cfg.participation_cap
        for oid, o in list(self.orders.items()):
            if o.market_id != tr.market_id or printed <= 1e-9:
                continue
            if tr.taker_action is Action.BUY and o.action is Action.SELL and o.price <= tr.price + 1e-12:
                hit = o.price < tr.price - 1e-12  # swept through us entirely
            elif tr.taker_action is Action.SELL and o.action is Action.BUY and o.price >= tr.price - 1e-12:
                hit = o.price > tr.price + 1e-12
            else:
                continue
            if hit:
                qty = min(o.remaining, printed)
            elif self.cfg.maker_requires_through:
                continue
            else:
                # same level: queue first
                take_queue = min(o.queue_ahead, printed)
                o.queue_ahead -= take_queue
                avail = printed - take_queue
                qty = min(o.remaining, avail)
            if qty <= 1e-9:
                continue
            printed -= qty
            self._fill(o, o.price, qty, is_maker=True, touch_depth=tr.size)
            if o.remaining <= 1e-9:
                self.orders.pop(oid, None)

    @staticmethod
    def _crossing_depth(book: Book, o: Order) -> float:
        """Resting size on the OPPOSITE side at or through our price, counting
        only levels with real size. 0 => nothing could have traded with us."""
        if o.action is Action.BUY:
            return sum(l.size for l in book.asks if l.size > 1e-9 and l.price <= o.price + 1e-12)
        return sum(l.size for l in book.bids if l.size > 1e-9 and l.price >= o.price - 1e-12)

    def _check_cross_fills(self, book: Book) -> None:
        """Book moved through our resting price without a print we saw -> assume
        filled (adverse). Only a level with non-zero size can cross us; the
        caller has already excluded settled / closed markets. Also refresh
        queue_ahead downward if our level shrank."""
        for oid, o in list(self.orders.items()):
            if o.market_id != book.market_id:
                continue
            depth = self._crossing_depth(book, o)
            if depth > 1e-9:
                self._fill(o, o.price, o.remaining, is_maker=True, assumed_cross=True, touch_depth=depth)
                self.orders.pop(oid, None)
            else:
                same = book.bids if o.action is Action.BUY else book.asks
                lvl_size = next((l.size for l in same if abs(l.price - o.price) < 1e-9), 0.0)
                o.queue_ahead = min(o.queue_ahead, lvl_size)

    # -- fills ---------------------------------------------------------------
    def _fill(self, order: Order, price: float, qty: float, is_maker: bool,
              assumed_cross: bool = False, touch_depth: float | None = None) -> None:
        sched = self.fee_for(order.market_id)
        fee = sched.fee(price, qty, is_maker)
        order.filled += qty
        f = Fill(ts=self.now, market_id=order.market_id, order_id=order.order_id,
                 action=order.action, price=price, size=qty, fee=fee,
                 is_maker=is_maker, strategy=order.strategy)
        self.positions[order.market_id].apply(order.action, price, qty, fee)
        self.fills.append(f)
        # touch_depth = the liquidity this fill was measured against, BEFORE the
        # fill: taker -> resting size at the touch we hit; maker from a print ->
        # the print size; assumed cross -> opposite-side size at/through our
        # price. Callers pass it; the fallback below is only for direct calls.
        if touch_depth is None:
            b = self.books.get(order.market_id)
            touch_depth = 0.0
            if b is not None:
                if is_maker:
                    touch_depth = self._crossing_depth(b, order)
                else:
                    same = b.asks if order.action is Action.BUY else b.bids
                    touch_depth = same[0].size if same else 0.0
        self.fill_context.append({"assumed_cross": assumed_cross, "touch_depth": float(touch_depth)})
        for s in self.strategies:
            s.on_fill(self.api, f)

    # -- accounting ------------------------------------------------------------
    def equity(self) -> float:
        total = 0.0
        for mid, pos in self.positions.items():
            total += pos.realized - pos.fees
            if pos.contracts != 0:
                total += pos.contracts * (self.mark(mid) - pos.avg_price)
        return total

    def mark(self, market_id: str) -> float:
        """Mark price: settlement result if settled, else mid, else the one
        side that exists (a one-sided book near expiry is still information),
        else our average price."""
        if market_id in self.settled:
            return self.settled[market_id]
        b = self.books.get(market_id)
        if b is not None:
            if b.mid is not None:
                return b.mid
            if b.best_bid is not None:
                return b.best_bid
            if b.best_ask is not None:
                return b.best_ask
        return self.positions[market_id].avg_price

    def capital_at_risk(self) -> float:
        return sum(p.capital_at_risk() for p in self.positions.values())


# ----------------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------------
class Result:
    def __init__(self, e: Engine):
        self.engine = e
        self.fills = e.fills
        self.equity_curve = e.equity_curve
        self.logs = e.logs

    @property
    def pnl(self) -> float:
        return self.engine.equity()

    @property
    def fees(self) -> float:
        return sum(f.fee for f in self.fills)

    @property
    def gross(self) -> float:
        return self.pnl + self.fees

    def summary(self) -> dict:
        import numpy as np
        n = len(self.fills)
        maker = sum(1 for f in self.fills if f.is_maker)
        vol = sum(f.size for f in self.fills)
        eq = np.array([v for _, v in self.equity_curve]) if self.equity_curve else np.array([0.0])
        peak = np.maximum.accumulate(eq)
        dd = float((peak - eq).max()) if len(eq) else 0.0
        max_cap = max(getattr(self.engine, "max_cap", 0.0), self.engine.capital_at_risk())
        diffs = np.diff(eq) if len(eq) > 1 else np.array([0.0])
        sharpe = float(diffs.mean() / diffs.std() * np.sqrt(len(diffs))) if diffs.std() > 0 else 0.0
        per_market = {}
        for m, p in self.engine.positions.items():
            per_market[m] = round(p.realized - p.fees, 4)
        wins = sum(1 for v in per_market.values() if v > 0)
        return {
            "net_pnl": round(self.pnl, 4),
            "gross_pnl": round(self.gross, 4),
            "fees": round(self.fees, 4),
            "fills": n,
            "maker_fills": maker,
            "taker_fills": n - maker,
            "contracts_traded": round(vol, 2),
            "max_drawdown": round(dd, 4),
            "max_capital_at_risk": round(max_cap, 2),
            "markets_traded": len(per_market),
            "market_win_rate": round(wins / len(per_market), 3) if per_market else 0.0,
            "sharpe_like": round(sharpe, 2),
        }
