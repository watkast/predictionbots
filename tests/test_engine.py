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


# ---------------------------------------------------------------------------
# fill-attribution audit fixes (reports/AUDIT_mm_crypto_twap.md)
# ---------------------------------------------------------------------------
def test_cross_fill_needs_real_size_and_records_crossing_depth():
    s = Once([Order("M", Action.BUY, 0.50, 10)])
    e, r = run(s, [book(0, [(0.45, 100)], [(0.55, 30)]),
                   book(1, [(0.40, 100)], [(0.48, 0.0), (0.56, 30)]),   # empty level "through" us: no fill
                   book(2, [(0.40, 100)], [(0.47, 4), (0.56, 30)])])    # real size through us: fill
    assert len(e.fills) == 1 and e.fills[0].ts == 2 and e.fills[0].price == 0.50
    assert e.fill_context[0]["assumed_cross"] and e.fill_context[0]["touch_depth"] == 4


def test_no_fills_after_close_or_on_settled_market():
    m = Market(venue=Venue.KALSHI, market_id="M", close_ts=10.0)
    e = Engine([m], lambda _: KALSHI_DEFAULT, SimConfig(order_latency=0.0, cancel_latency=0.0))
    e.add_strategy(Once([Order("M", Action.SELL, 0.60, 10)]))
    e.run([book(0, [(0.50, 100)], [(0.62, 30)]),
           book(11, [(0.65, 100)], [(0.70, 30)]),                        # crossed after close_ts
           Trade(11.5, "M", 0.70, 50, Action.BUY)])                      # print after close
    assert e.fills == [] and e.orders                                     # still resting, not credited
    e2 = Engine([mk()], lambda _: KALSHI_DEFAULT, SimConfig(order_latency=0.0, cancel_latency=0.0))
    e2.add_strategy(Once([Order("M", Action.SELL, 0.60, 10)]))
    e2.run([book(0, [(0.50, 100)], [(0.62, 30)]), Settlement(1, "M", 1.0),
            book(2, [(0.99, 100)], [])])
    assert e2.fills == [] and not e2.orders


def test_taker_touch_depth_is_pre_trade():
    s = Once([Order("M", Action.BUY, 0.60, 3, tif=TIF.IOC)])
    e, r = run(s, [book(0, [(0.45, 100)], [(0.50, 3), (0.70, 30)])])
    assert e.fills[0].size == 3 and e.fill_context[0]["touch_depth"] == 3   # not 0 (post-trade)


def test_print_fill_records_print_size():
    s = Once([Order("M", Action.SELL, 0.60, 10)])
    e, r = run(s, [book(0, [(0.50, 100)], [(0.60, 0)]), Trade(1, "M", 0.61, 25, Action.BUY)])
    assert e.fills and e.fill_context[0] == {"assumed_cross": False, "touch_depth": 25.0}


def test_position_limit_counts_resting_same_side_orders():
    s = Once([Order("M", Action.BUY, 0.50, 60), Order("M", Action.BUY, 0.49, 60), Order("M", Action.BUY, 0.48, 60)])
    e, r = run(s, [book(0, [(0.45, 100)], [(0.55, 30)])], cfg=SimConfig(order_latency=0.0, cancel_latency=0.0,
                                                                          max_position_per_market=100))
    assert sum(o.remaining for o in e.orders.values()) == 60              # 2nd and 3rd blocked


def test_cancel_before_arrival_never_rests():
    class S(Strategy):
        def __init__(self):
            self.done = False

        def on_book(self, api, b):
            if not self.done:
                self.done = True
                oid = api.place(Order("M", Action.BUY, 0.40, 10))
                api.cancel(oid)                                           # cancel lands before arrival
    e = Engine([mk()], lambda _: KALSHI_DEFAULT, SimConfig(order_latency=1.0, cancel_latency=0.1))
    e.add_strategy(S())
    e.run([book(0, [(0.45, 100)], [(0.55, 30)]), book(5, [(0.45, 100)], [(0.55, 30)])])
    assert not e.orders and not e._cancelled


def test_mark_uses_one_sided_book_and_settlement():
    s = Once([Order("M", Action.SELL, 0.50, 10)])
    e, r = run(s, [book(0, [(0.45, 100)], [(0.52, 30)]), book(1, [(0.55, 100)], [(0.60, 30)]),  # crossed: short 10 @ .50
                   book(2, [], [(0.01, 100)])])                                                   # asks only
    assert e.mark("M") == 0.01 and e.equity() == pytest.approx(10 * (0.50 - 0.01))
    e._on_settlement(Settlement(3, "M", 0.0))
    assert e.mark("M") == 0.0 and e.equity() == pytest.approx(5.0)
