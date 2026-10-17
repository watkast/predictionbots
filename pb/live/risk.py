"""Risk manager for the paper runner: a gate in front of `Engine.submit`.

Everything here is paper-trading only (there is no live-money path in this
repo) but the limits are designed so the same object could sit in front of a
real venue adapter.

Checks, in order, on every submitted order:

1. **Kill switch**: if `kill_file` (default `data/KILL`) exists, halt: cancel
   everything and reject all orders until the file is removed (then auto-resume
   only if `auto_resume=True`; default False, a halt is sticky).
2. **Daily loss limit**: net pnl since the local-day start below
   `-daily_loss_limit` -> halt + cancel all. The pnl is marked at the
   *conservative* side of the book (`equity_conservative()`: bid for a long
   YES position, ask for a short one) whenever a two-sided book exists, so a
   position that could only be unwound at a loss trips the limit before the
   mid says so; one-sided / absent books fall back to `Engine.mark`.
3. **Stale data**: no `Book` update on any traded market for `stale_secs` ->
   cancel all open orders and reject new ones until a fresh book arrives
   (not sticky).
4. **Rate limit**: more than `max_orders_per_min` submissions in the trailing
   60 s -> reject (not sticky).
5. **Capital caps**: the collateral this order would lock (price * size for a
   BUY-YES, (1 - price) * size for a SELL-YES) plus current capital at risk and
   resting-order collateral must stay under `max_capital_per_market` for the
   market and `max_capital_total` overall. Orders that *reduce* a position
   are always allowed through the capital checks.

`status()` returns a JSON-able dict (halted, reason, counters, pnl today,
capital in use) that the paper runner writes into its summary.
"""
from __future__ import annotations

import logging
import math
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from pb.core.types import Action, Book, Order
from pb.sim.engine import Engine

log = logging.getLogger(__name__)


@dataclass
class RiskLimits:
    daily_loss_limit: float = 50.0            # dollars; net pnl today < -X -> halt
    max_capital_per_market: float = 500.0     # dollars of collateral locked per market
    max_capital_total: float = 2000.0         # dollars of collateral locked overall
    max_orders_per_min: int = 120
    stale_secs: float = 60.0                  # no book update for this long -> cancel all
    kill_file: str = "data/KILL"
    auto_resume: bool = False                 # resume after the kill file is removed / day rolls
    day_tz_offset_h: float = 0.0              # local-day boundary for the daily limit (hours from UTC)


@dataclass
class RiskState:
    halted: bool = False
    halt_reason: str = ""
    halted_at: float = 0.0
    rejected: int = 0
    accepted: int = 0
    cancel_all_count: int = 0
    stale: bool = False
    day_start: float = 0.0
    day_open_equity: float = 0.0
    reject_reasons: dict[str, int] = field(default_factory=dict)


class RiskManager:
    """Wraps `engine.submit`. Call `install()` once; `on_event()` from the
    runner for each Book; `check()` on a heartbeat for the stale/kill guards."""

    def __init__(self, engine: Engine, limits: Optional[RiskLimits] = None,
                 clock: Callable[[], float] = time.time, name: str = ""):
        self.engine = engine
        self.limits = limits or RiskLimits()
        self.clock = clock
        self.name = name
        self.state = RiskState()
        self._orig_submit: Optional[Callable[[Order], str]] = None
        self._submits: deque[float] = deque()
        self._inflight: deque[tuple[float, Order]] = deque()   # accepted, maybe not yet on the book
        self._last_book: dict[str, float] = {}
        self._reset_day(self.clock())

    # -- install / wrap -----------------------------------------------------------
    def install(self) -> "RiskManager":
        if self._orig_submit is None:
            self._orig_submit = self.engine.submit
            self.engine.submit = self.submit  # type: ignore[method-assign]
        return self

    def uninstall(self) -> None:
        if self._orig_submit is not None:
            self.engine.submit = self._orig_submit  # type: ignore[method-assign]
            self._orig_submit = None

    # -- day accounting -----------------------------------------------------------
    def _day_key(self, ts: float) -> float:
        off = self.limits.day_tz_offset_h * 3600.0
        d = datetime.fromtimestamp(ts + off, tz=timezone.utc)
        return d.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() - off

    def _reset_day(self, now: float) -> None:
        self.state.day_start = self._day_key(now)
        self.state.day_open_equity = self.equity_conservative()

    def mark_conservative(self, market_id: str) -> float:
        """Liquidation mark: bid for a long YES position, ask for a short one,
        when both sides exist; otherwise the engine's mark (settlement / mid /
        the one side / avg price)."""
        if market_id in self.engine.settled:
            return self.engine.settled[market_id]
        pos = self.engine.positions.get(market_id)
        b = self.engine.books.get(market_id)
        if pos is not None and pos.contracts != 0 and b is not None \
                and b.best_bid is not None and b.best_ask is not None:
            return b.best_bid if pos.contracts > 0 else b.best_ask
        return self.engine.mark(market_id)

    def equity_conservative(self) -> float:
        total = 0.0
        for mid, pos in self.engine.positions.items():
            total += pos.realized - pos.fees
            if pos.contracts != 0:
                total += pos.contracts * (self.mark_conservative(mid) - pos.avg_price)
        return total

    def pnl_today(self) -> float:
        return self.equity_conservative() - self.state.day_open_equity

    def forget_market(self, market_id: str) -> None:
        """The runner dropped a market (settled / closed): stop the stale guard
        from watching it."""
        self._last_book.pop(market_id, None)

    # -- guards ------------------------------------------------------------------
    def halt(self, reason: str) -> None:
        if not self.state.halted:
            log.error("RISK HALT (%s): %s", self.name, reason)
        self.state.halted = True
        self.state.halt_reason = reason
        self.state.halted_at = self.clock()
        self.cancel_all()

    def resume(self) -> None:
        if self.state.halted:
            log.warning("risk resume (%s) after: %s", self.name, self.state.halt_reason)
        self.state.halted = False
        self.state.halt_reason = ""

    def cancel_all(self) -> None:
        n = 0
        for oid in list(self.engine.orders):
            self.engine.cancel(oid)
            n += 1
        # orders still in flight (submitted, latency not elapsed): pop them once they land
        lat = max(self.engine.cfg.order_latency, self.engine.cfg.cancel_latency)
        for _, o in self._inflight_orders():
            if o.order_id and o.order_id not in self.engine.orders:
                self.engine.schedule(self.engine.now + lat, lambda oid=o.order_id: self.engine.orders.pop(oid, None))
                n += 1
        if n:
            self.state.cancel_all_count += 1
            log.warning("risk (%s): cancelled %d open orders", self.name, n)

    def kill_requested(self) -> bool:
        try:
            return Path(self.limits.kill_file).exists()
        except OSError:  # pragma: no cover
            return False

    def on_event(self, ev: object) -> None:
        if isinstance(ev, Book):
            self._last_book[ev.market_id] = self.clock()
            if self.state.stale and not self._any_stale():
                self.state.stale = False
                log.info("risk (%s): data fresh again", self.name)

    def _any_stale(self) -> Optional[str]:
        now = self.clock()
        for mid in self.engine.markets:
            if mid in self.engine.settled:
                continue
            last = self._last_book.get(mid)
            if last is None:
                continue  # never seen a book: nothing to be stale about (cannot quote anyway)
            if now - last > self.limits.stale_secs:
                return mid
        return None

    def check(self) -> None:
        """Heartbeat: kill switch, day roll, daily loss, stale data."""
        now = self.clock()
        if self._day_key(now) != self.state.day_start:
            self._reset_day(now)
            if self.state.halted and self.state.halt_reason.startswith("daily_loss") and self.limits.auto_resume:
                self.resume()
        if self.kill_requested():
            if not self.state.halted:
                self.halt(f"kill_file {self.limits.kill_file}")
        elif self.state.halted and self.state.halt_reason.startswith("kill_file") and self.limits.auto_resume:
            self.resume()
        pnl = self.pnl_today()
        if pnl < -abs(self.limits.daily_loss_limit) and not self.state.halted:
            self.halt(f"daily_loss {pnl:.2f} < -{self.limits.daily_loss_limit:.2f}")
        stale_mid = self._any_stale()
        if stale_mid and not self.state.stale:
            self.state.stale = True
            log.warning("risk (%s): no book for %s in %.0fs; cancelling all", self.name, stale_mid, self.limits.stale_secs)
            self.cancel_all()

    # -- capital --------------------------------------------------------------------
    @staticmethod
    def order_collateral(o: Order) -> float:
        p = min(max(o.price, 0.0), 1.0)
        return (p if o.action is Action.BUY else 1.0 - p) * o.remaining

    def _reduces_position(self, o: Order) -> bool:
        pos = self.engine.positions.get(o.market_id)
        if pos is None or pos.contracts == 0:
            return False
        signed = o.size if o.action is Action.BUY else -o.size
        return (pos.contracts > 0) != (signed > 0) and abs(signed) <= abs(pos.contracts) + 1e-9

    def _inflight_orders(self) -> list[tuple[float, Order]]:
        """Accepted orders whose arrival latency has not elapsed on the engine clock."""
        horizon = self.engine.now - self.engine.cfg.order_latency - 1e-9
        while self._inflight and self._inflight[0][0] < horizon:
            self._inflight.popleft()
        return list(self._inflight)

    def resting_collateral(self, market_id: Optional[str] = None) -> float:
        total = 0.0
        seen: set[str] = set()
        for o in self.engine.orders.values():
            if market_id is None or o.market_id == market_id:
                total += self.order_collateral(o)
                seen.add(o.order_id or "")
        for _, o in self._inflight_orders():
            if (o.order_id not in seen) and (market_id is None or o.market_id == market_id) and o.filled == 0:
                total += self.order_collateral(o)
        return total

    def capital_in_use(self, market_id: Optional[str] = None) -> float:
        if market_id is None:
            return self.engine.capital_at_risk() + self.resting_collateral()
        pos = self.engine.positions.get(market_id)
        return (pos.capital_at_risk() if pos else 0.0) + self.resting_collateral(market_id)

    # -- the gate ----------------------------------------------------------------------
    def _reject(self, o: Order, reason: str) -> str:
        self.state.rejected += 1
        self.state.reject_reasons[reason] = self.state.reject_reasons.get(reason, 0) + 1
        log.debug("risk reject %s %s %.2f x %.0f: %s", o.market_id, o.action.value, o.price, o.size, reason)
        # mimic Engine.submit's contract (an id comes back) but the order never reaches the
        # book, so it will not show up in `open_orders` and strategies re-quote normally
        o.order_id = o.order_id or f"rejected-{self.state.rejected}"
        return o.order_id

    def submit(self, o: Order) -> str:
        assert self._orig_submit is not None, "RiskManager.install() not called"
        self.check()
        if self.state.halted:
            return self._reject(o, "halted")
        if self.state.stale:
            return self._reject(o, "stale_data")
        now = self.clock()
        while self._submits and now - self._submits[0] > 60.0:
            self._submits.popleft()
        if len(self._submits) >= self.limits.max_orders_per_min:
            return self._reject(o, "rate_limit")
        if o.size > 0 and not self._reduces_position(o):
            need = self.order_collateral(o)
            if self.capital_in_use(o.market_id) + need > self.limits.max_capital_per_market + 1e-9:
                return self._reject(o, "market_capital_cap")
            if self.capital_in_use() + need > self.limits.max_capital_total + 1e-9:
                return self._reject(o, "total_capital_cap")
        self._submits.append(now)
        self.state.accepted += 1
        oid = self._orig_submit(o)
        if o.size > 0:
            self._inflight.append((self.engine.now, o))
        return oid

    # -- reporting ------------------------------------------------------------------------
    def status(self) -> dict:
        s = self.state
        return {
            "halted": s.halted,
            "halt_reason": s.halt_reason,
            "halted_at": s.halted_at,
            "stale": s.stale,
            "kill_file": self.limits.kill_file,
            "kill_file_present": self.kill_requested(),
            "pnl_today": round(self.pnl_today(), 4),
            "daily_loss_limit": self.limits.daily_loss_limit,
            "capital_in_use": round(self.capital_in_use(), 2),
            "capital_in_use_by_market": {m: round(self.capital_in_use(m), 2) for m in self.engine.markets
                                         if self.capital_in_use(m) > 0},
            "max_capital_total": self.limits.max_capital_total,
            "max_capital_per_market": self.limits.max_capital_per_market,
            "orders_last_min": len([t for t in self._submits if self.clock() - t <= 60.0]),
            "max_orders_per_min": self.limits.max_orders_per_min,
            "accepted": s.accepted,
            "rejected": s.rejected,
            "reject_reasons": dict(s.reject_reasons),
            "cancel_all_count": s.cancel_all_count,
            "last_book_age": {m: round(self.clock() - t, 1) for m, t in self._last_book.items()},
            "stale_secs": self.limits.stale_secs,
        }


__all__ = ["RiskLimits", "RiskManager", "RiskState"]
