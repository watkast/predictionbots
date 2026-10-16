"""Strategy helpers shared by all models.

A strategy only talks to the `SimAPI`-shaped object (identical in backtest and
live paper trading). Keep strategies stateless w.r.t. venue details; the
runner injects markets, fee schedules and reference signals.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

from pb.core.types import Action, Book, Order, TIF, Trade
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
    the desired quote moved by >= `requote_tick` to limit churn."""

    def __init__(self, api: SimAPI, strategy_name: str, tick: float = 0.01,
                 requote_tick: float = 0.01):
        self.api = api
        self.name = strategy_name
        self.tick = tick
        self.requote = requote_tick
        self.live: dict[str, dict[str, Order]] = {}

    def set(self, market_id: str, q: Quote) -> None:
        cur = self.live.setdefault(market_id, {})
        for side, px, sz, act in (("bid", q.bid, q.bid_size, Action.BUY),
                                  ("ask", q.ask, q.ask_size, Action.SELL)):
            o = cur.get(side)
            if o is not None and (o.order_id not in {x.order_id for x in self.api.open_orders(market_id)}):
                cur.pop(side, None)
                o = None
            if px is None or sz <= 0:
                if o is not None:
                    self.api.cancel(o.order_id)
                    cur.pop(side, None)
                continue
            px = round_tick(px, self.tick)
            if o is not None:
                if abs(o.price - px) < self.requote - 1e-9 and o.remaining >= sz * 0.5:
                    continue
                self.api.cancel(o.order_id)
            new = Order(market_id, act, px, sz, tif=TIF.GTC, post_only=True, strategy=self.name)
            self.api.place(new)
            cur[side] = new

    def pull(self, market_id: str) -> None:
        for o in self.live.pop(market_id, {}).values():
            self.api.cancel(o.order_id)

    def pull_all(self) -> None:
        for m in list(self.live):
            self.pull(m)
