import pytest

from pb.core.fees import FeeSchedule, KALSHI_DEFAULT
from pb.core.types import Action, Book, Level, Market, Order, TIF, Trade, Venue
from pb.sim.engine import Engine, Settlement, SimConfig, Strategy


def mk(mid="M"):
    return Market(venue=Venue.KALSHI, market_id=mid)


def book(ts, bids, asks, mid="M"):
    return Book(ts=ts, market_id=mid,
                bids=[Level(p, s) for p, s in bids],
                asks=[Level(p, s) for p, s in asks])


class Once(Strategy):
    def __init__(self, orders):
        self.orders = orders
        self.done = False
    def on_book(self, api, b):
        if not self.done:
            self.done = True
            for o in self.orders:
                api.place(o)


def run(strategy, events, cfg=None, fee=KALSHI_DEFAULT):
    e = Engine([mk()], lambda m: fee, cfg or SimConfig(order_latency=0.0, cancel_latency=0.0))
    e.add_strategy(strategy)
    return e, e.run(events)


def test_taker_limited_by_depth():
    s = Once([Order("M", Action.BUY, 0.60, 500, tif=TIF.IOC)])
    e, r = run(s, [book(0, [(0.50, 100)], [(0.52, 30), (0.55, 20)]), book(10, [(0.50, 100)], [(0.52, 30)])])
    # only 50 contracts existed within our limit; we cannot buy 500
    assert sum(f.size for f in e.fills) == 50
    assert all(not f.is_maker for f in e.fills)
    assert e.fills[0].price == 0.52 and e.fills[1].price == 0.55


def test_taker_fee_kalshi_rounds_up():
    s = Once([Order("M", Action.BUY, 0.60, 10, tif=TIF.IOC)])
    e, r = run(s, [book(0, [], [(0.50, 100)])])
    # 0.07*10*0.25 = 0.175 -> 0.18
    assert e.fills[0].fee == pytest.approx(0.18)


def test_maker_waits_for_queue():
    s = Once([Order("M", Action.BUY, 0.50, 10)])  # join bid at 0.50 behind 100
    ev = [book(0, [(0.50, 100)], [(0.55, 100)]),
          Trade(1, "M", 0.50, 60, Action.SELL),    # consumes queue only
          Trade(2, "M", 0.50, 60, Action.SELL)]    # 40 more queue, then 10 of ours... but only 20 left
    e, r = run(s, ev)
    assert sum(f.size for f in e.fills) == 10
    assert e.fills[0].is_maker


def test_maker_not_filled_by_wrong_side():
    s = Once([Order("M", Action.BUY, 0.50, 10)])
    ev = [book(0, [(0.49, 100)], [(0.55, 100)]),
          Trade(1, "M", 0.55, 500, Action.BUY)]   # buyers lifting asks don't fill our bid
    e, r = run(s, ev)
    assert not e.fills


def test_post_only_rejected_when_crossing():
    s = Once([Order("M", Action.BUY, 0.60, 10, post_only=True)])
    e, r = run(s, [book(0, [(0.50, 100)], [(0.52, 30)]), Trade(1, "M", 0.52, 100, Action.SELL)])
    assert not e.fills and not e.orders


def test_cross_through_assumes_adverse_fill():
    s = Once([Order("M", Action.SELL, 0.60, 10)])
    e, r = run(s, [book(0, [(0.50, 100)], [(0.62, 30)]),
                   book(1, [(0.65, 100)], [(0.70, 30)])])  # market gapped up through our ask
    assert e.fills and e.fills[0].price == 0.60 and e.fills[0].is_maker


def test_settlement_pnl():
    s = Once([Order("M", Action.BUY, 0.60, 10, tif=TIF.IOC)])
    e, r = run(s, [book(0, [], [(0.40, 100)]), Settlement(5, "M", 1.0)], fee=FeeSchedule(0.0))
    assert r.pnl == pytest.approx(10 * (1.0 - 0.40))


def test_position_flip_accounting():
    from pb.sim.engine import Position
    p = Position()
    p.apply(Action.BUY, 0.40, 10, 0)
    p.apply(Action.SELL, 0.50, 15, 0)   # close 10 for +1.0, open short 5 @0.50
    assert p.realized == pytest.approx(1.0)
    assert p.contracts == -5 and p.avg_price == pytest.approx(0.50)
    p.apply(Action.BUY, 0.30, 5, 0)
    assert p.realized == pytest.approx(2.0)
    assert p.contracts == 0


def test_position_limit_blocks_resting():
    cfg = SimConfig(order_latency=0.0, cancel_latency=0.0, max_position_per_market=5)
    s = Once([Order("M", Action.BUY, 0.50, 10)])
    e, r = run(s, [book(0, [(0.50, 1)], [(0.55, 1)])], cfg=cfg)
    assert not e.orders
