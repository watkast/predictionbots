"""Synthetic market generator for smoke tests and CI.

NOT for judging profitability — it exists so the framework can be exercised
without network access. Real evaluation uses recorded/historical data only.
"""
from __future__ import annotations

import random

from pb.core.types import Action, Book, Level, Market, Trade, Venue
from pb.sim.engine import Settlement


def synthetic_events(market_id: str = "SYN", seconds: int = 3600, seed: int = 1,
                     start_p: float = 0.5, step_sigma: float = 0.004,
                     depth: float = 40.0, trade_rate: float = 0.2,
                     informed_frac: float = 0.3):
    rng = random.Random(seed)
    p = start_p
    events = []
    truth = rng.random() < start_p
    for t in range(seconds):
        drift = (0.0005 if truth else -0.0005) * informed_frac
        p = min(0.98, max(0.02, p + rng.gauss(drift, step_sigma)))
        spread = 0.02 if rng.random() < 0.8 else 0.04
        bid = round(p - spread / 2, 2)
        ask = round(p + spread / 2, 2)
        bids = [Level(round(bid - i * 0.01, 2), depth * rng.uniform(0.3, 1.5)) for i in range(5)]
        asks = [Level(round(ask + i * 0.01, 2), depth * rng.uniform(0.3, 1.5)) for i in range(5)]
        events.append(Book(ts=float(t), market_id=market_id, bids=bids, asks=asks))
        if rng.random() < trade_rate:
            informed = rng.random() < informed_frac
            buy = truth if informed else rng.random() < 0.5
            px = ask if buy else bid
            events.append(Trade(ts=t + 0.5, market_id=market_id, price=px,
                                size=rng.uniform(1, 30), taker_action=Action.BUY if buy else Action.SELL))
    events.append(Settlement(ts=float(seconds + 1), market_id=market_id, result=1.0 if truth else 0.0))
    return [Market(venue=Venue.KALSHI, market_id=market_id, close_ts=float(seconds))], events
