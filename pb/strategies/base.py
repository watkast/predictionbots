"""Strategy helpers shared by all models.

A strategy only talks to the `SimAPI`-shaped object (identical in backtest and
live paper trading). Keep strategies stateless w.r.t. venue details; the
runner injects markets, fee schedules and reference signals.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

from pb.core.types import Action, Book, Level, Order, TIF, Trade
from pb.sim.engine import SimAPI, Strategy

REGISTRY: dict[str, type[Strategy]] = {}


def register(cls):
    REGISTRY[cls.name] = cls
    return cls


def round_tick(p: float, tick: float = 0.01) -> float:
    return max(tick, min(1 - tick, round(round(p / tick) * tick, 6)))


class Toxicity:
    """Order-flow toxicity proxy (bucketed VPIN-lite + print-rate spike).

    Bartlett & O'Hara show trailing VPIN predicts maker losses on Kalshi
    single-name markets; we use it as a quote-pull gate."""

    def __init__(self, bucket: float = 50.0, n_buckets: int = 20):
        self.bucket = bucket
        self.buckets: deque[tuple[float, float]] = deque(maxlen=n_buckets)
        self._buy = 0.0
        self._sell = 0.0
        self.prints: deque[float] = deque(maxlen=200)

    def on_trade(self, t: Trade) -> None:
        self.prints.append(t.ts)
        if t.taker_action is Action.BUY:
            self._buy += t.size
        else:
            self._sell += t.size
        if self._buy + self._sell >= self.bucket:
            self.buckets.append((self._buy, self._sell))
            self._buy = self._sell = 0.0

    @property
    def vpin(self) -> float:
        if not self.buckets:
            return 0.0
        imb = sum(abs(b - s) for b, s in self.buckets)
        vol = sum(b + s for b, s in self.buckets)
        return imb / vol if vol else 0.0

    def print_rate(self, now: float, window: float = 60.0) -> float:
        return sum(1 for t in self.prints if now - t <= window) / window


@dataclass
class Quote:
    bid: float | None
    ask: float | None
    bid_size: float
    ask_size: float


class QuoteManager:
    """Keeps at most one bid and one ask resting per market; replaces only when
    the desired quote moved by >= `requote_tick` to limit churn.

    An order just placed is *in flight* for the engine's order latency and is
    not yet in `open_orders`; it is still ours. Treating it as gone (the old
    behaviour) placed a duplicate on every requote inside the latency window,
    and the duplicates were never cancelled (orphans). We therefore keep an
    order until it has been SEEN resting and then disappears (filled/cancelled),
    or until `inflight_grace` seconds pass without it ever appearing (rejected,
    e.g. by the risk gate, whose ids start with "rejected-"). Any resting order
    on the market carrying our strategy name that we do not track is an orphan
    and gets cancelled."""

    def __init__(self, api: SimAPI, strategy_name: str, tick: float = 0.01,
                 requote_tick: float = 0.01, inflight_grace: float = 5.0):
        self.api = api
        self.name = strategy_name
        self.tick = tick
        self.requote = requote_tick
        self.grace = inflight_grace
        self.live: dict[str, dict[str, Order]] = {}
        self._placed_at: dict[str, float] = {}
        self._seen: set[str] = set()

    def _alive(self, o: Order, open_ids: set[str]) -> bool:
        oid = o.order_id or ""
        if oid in open_ids:
            self._seen.add(oid)
            return True
        if oid in self._seen or oid.startswith("rejected-"):
            return False            # was resting and is gone: filled or cancelled
        placed = self._placed_at.get(oid)
        if placed is None:
            return False
        return self.api.now - placed <= self.grace   # still in flight

    def _forget(self, o: Order) -> None:
        oid = o.order_id or ""
        self._placed_at.pop(oid, None)
        self._seen.discard(oid)

    def set(self, market_id: str, q: Quote) -> None:
        cur = self.live.setdefault(market_id, {})
        open_orders = self.api.open_orders(market_id)
        open_ids = {x.order_id for x in open_orders}
        tracked = {o.order_id for o in cur.values()}
        # orphans: resting orders of ours on this market that we no longer track
        for x in open_orders:
            if x.strategy == self.name and x.order_id not in tracked:
                self.api.cancel(x.order_id)
        for side, px, sz, act in (("bid", q.bid, q.bid_size, Action.BUY),
                                  ("ask", q.ask, q.ask_size, Action.SELL)):
            o = cur.get(side)
            if o is not None and not self._alive(o, open_ids):
                self._forget(o)
                cur.pop(side, None)
                o = None
            if px is None or sz <= 0:
                if o is not None:
                    self.api.cancel(o.order_id)
                    self._forget(o)
                    cur.pop(side, None)
                continue
            px = round_tick(px, self.tick)
            if o is not None:
                if abs(o.price - px) < self.requote - 1e-9 and o.remaining >= sz * 0.5:
                    continue
                self.api.cancel(o.order_id)
                self._forget(o)
            new = Order(market_id, act, px, sz, tif=TIF.GTC, post_only=True, strategy=self.name)
            oid = self.api.place(new)
            new.order_id = new.order_id or oid
            self._placed_at[new.order_id or ""] = self.api.now
            cur[side] = new

    def pull(self, market_id: str) -> None:
        for o in self.live.pop(market_id, {}).values():
            self.api.cancel(o.order_id)
            self._forget(o)
        # orphans too
        for x in self.api.open_orders(market_id):
            if x.strategy == self.name:
                self.api.cancel(x.order_id)

    def pull_all(self) -> None:
        for m in list(self.live):
            self.pull(m)


# ----------------------------------------------------------------------------
# Shared helpers for the strategy suite
# ----------------------------------------------------------------------------
def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


class SignalCache:
    """Latest (ts, value) per key with staleness checks."""

    def __init__(self) -> None:
        self.latest: dict[str, tuple[float, object]] = {}

    def put(self, key: str, ts: float, value) -> None:
        self.latest[key] = (ts, value)

    def get(self, key: str, now: float, max_age: float = math.inf):
        v = self.latest.get(key)
        if v is None or now - v[0] > max_age:
            return None
        return v[1]

    def age(self, key: str, now: float) -> float:
        v = self.latest.get(key)
        return math.inf if v is None else now - v[0]


def secs_to_close(api: SimAPI, market_id: str) -> float:
    m = api.market(market_id)
    if m is None or not m.close_ts:
        return math.inf
    return m.close_ts - api.now


def maker_fee_per_contract(api: SimAPI, market_id: str, p: float) -> float:
    """Maker fee in price units for one contract at price p (0 on fee-free series)."""
    sched = api.fee(market_id)
    return sched.maker_rate * p * (1 - p) - sched.maker_rebate_frac * sched.taker_rate * p * (1 - p)


def taker_fee_per_contract(api: SimAPI, market_id: str, p: float) -> float:
    return api.fee(market_id).taker_rate * p * (1 - p)


def walk_cost(levels: list[Level], qty: float) -> tuple[float, float]:
    """Average price and fillable quantity when taking `qty` through `levels`
    (best-first). Returns (avg_price, filled)."""
    filled = 0.0
    cost = 0.0
    for lvl in levels:
        if filled >= qty - 1e-12:
            break
        take = min(lvl.size, qty - filled)
        if take <= 0:
            continue
        cost += take * lvl.price
        filled += take
    return (cost / filled if filled > 0 else float("nan")), filled


def clamp_size(size: float, *caps: float, min_size: float = 1.0) -> float:
    s = min([size, *[c for c in caps if c is not None]])
    return s if s >= min_size else 0.0
