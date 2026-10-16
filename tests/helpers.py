"""Hand-built event helpers for strategy tests (no network, no synthetic randomness)."""
from __future__ import annotations

from pb.core.fees import KALSHI_DEFAULT, FeeSchedule
from pb.core.types import Action, Book, Level, Market, Order, Trade, Venue
from pb.sim.engine import Engine, Settlement, Signal, SimConfig


def mk(mid="M", **kw) -> Market:
    kw.setdefault("venue", Venue.KALSHI)
    return Market(market_id=mid, **kw)


def book(ts, bids, asks, mid="M") -> Book:
    return Book(ts=float(ts), market_id=mid,
                bids=[Level(p, s) for p, s in bids], asks=[Level(p, s) for p, s in asks])


def trade(ts, price, size, buy=True, mid="M") -> Trade:
    return Trade(ts=float(ts), market_id=mid, price=price, size=size,
                 taker_action=Action.BUY if buy else Action.SELL)


def sig(ts, name, value, mid=None) -> Signal:
    return Signal(ts=float(ts), name=name, market_id=mid, value=value)


def settle(ts, result, mid="M") -> Settlement:
    return Settlement(ts=float(ts), market_id=mid, result=result)


class Recorder:
    """Wraps an Engine so tests can inspect every order submitted."""

    def __init__(self, engine: Engine):
        self.engine = engine
        self.submitted: list[Order] = []
        orig = engine.submit

        def submit(o: Order) -> str:
            self.submitted.append(o)
            return orig(o)

        engine.submit = submit  # type: ignore[method-assign]


def run(strategy, markets, events, fee: FeeSchedule | dict | None = None, cfg: SimConfig | None = None):
    """Run with zero latency so assertions are deterministic. Returns (engine, result, recorder)."""
    if fee is None:
        fee_for = lambda m: KALSHI_DEFAULT
    elif isinstance(fee, dict):
        fee_for = lambda m: fee.get(m, KALSHI_DEFAULT)
    else:
        fee_for = lambda m: fee
    e = Engine(markets, fee_for, cfg or SimConfig(order_latency=0.0, cancel_latency=0.0))
    rec = Recorder(e)
    e.add_strategy(strategy)
    r = e.run(events)
    return e, r, rec


def resting(engine: Engine, mid: str | None = None) -> list[Order]:
    return [o for o in engine.orders.values() if mid is None or o.market_id == mid]
