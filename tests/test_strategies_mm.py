"""Behavioural tests for the maker strategies: quotes exist when conditions are
met, are pulled when gated, never cross the touch, sizes <= depth."""
import math

import pytest

from pb.core.fees import KALSHI_DEFAULT, KALSHI_WITH_MAKER_FEES
from pb.core.types import Action, Order, TIF, Venue
from pb.sim.engine import Engine, SimConfig, Strategy
from pb.strategies.mm_crypto_twap import CryptoMMParams, CryptoTwapMM
from pb.strategies.mm_weather_ladder import WeatherLadderMM, WeatherLadderParams
from pb.strategies.sharp_line_maker import SharpLineMaker, SharpLineParams
from tests.helpers import book, mk, resting, run, settle, sig, trade


# ----------------------------------------------------------------------------
# mm_crypto_twap
# ----------------------------------------------------------------------------
BTC = "KXBTC15M-26OCT161315-T"


def crypto_market(open_ts=1000.0, close_ts=1900.0):
    return mk(BTC, series="KXBTC15M", close_ts=close_ts,
              meta={"window_open_ts": open_ts, "window_close_ts": close_ts})


def index_stream(t0, t1, start=100000.0, drift=0.0, wiggle=5.0):
    out = []
    px = start
    for i, t in enumerate(range(int(t0), int(t1))):
        px = start + drift * (t - t0) + (wiggle if i % 2 else -wiggle)
        out.append(sig(t, "btc_index", px))
    return out


def test_crypto_mm_quotes_both_sides_and_never_crosses():
    s = CryptoTwapMM(CryptoMMParams(size=5, min_touch_depth=1))
    ev = index_stream(950, 1300) + [book(1300.5, [(0.48, 20), (0.47, 30)], [(0.52, 20), (0.53, 30)], BTC)]
    ev.sort(key=lambda e: e.ts)
    e, r, rec = run(s, [crypto_market()], ev)
    orders = resting(e, BTC)
    assert {o.action for o in orders} == {Action.BUY, Action.SELL}
    bid = next(o for o in orders if o.action is Action.BUY)
    ask = next(o for o in orders if o.action is Action.SELL)
    assert bid.price < 0.52 and ask.price > 0.48
    assert all(o.post_only and o.tif is TIF.GTC for o in rec.submitted)
    assert all(o.size <= 0.5 * 20 for o in orders)
    assert r.fills == []  # nothing printed, nothing filled


def test_crypto_mm_fair_tracks_index():
    s = CryptoTwapMM(CryptoMMParams(size=5, min_touch_depth=1, min_half_spread=0.01))
    # index rallies 0.5% above open: fair should be well above 0.5
    ev = index_stream(950, 1000) + index_stream(1000, 1300, start=100000.0, drift=1.5)
    ev.append(book(1300.5, [(0.60, 20)], [(0.64, 20)], BTC))
    ev.sort(key=lambda e: e.ts)
    e, r, rec = run(s, [crypto_market()], ev)
    fair = s.last_fair[BTC]
    assert fair > 0.75


def test_crypto_mm_pulls_before_close_and_when_signal_stale():
    s = CryptoTwapMM(CryptoMMParams(size=5, min_touch_depth=1, pull_before_close=90, signal_max_age=10))
    ev = index_stream(950, 1300) + [book(1300.5, [(0.48, 20)], [(0.52, 20)], BTC)]
    # 1) stale signal: book at 1400 with last index at 1299
    ev.append(book(1400, [(0.48, 20)], [(0.52, 20)], BTC))
    ev.sort(key=lambda e: e.ts)
    e, r, rec = run(s, [crypto_market()], ev)
    assert resting(e, BTC) == []
    # 2) inside pull_before_close with fresh signal
    s2 = CryptoTwapMM(CryptoMMParams(size=5, min_touch_depth=1, pull_before_close=90))
    ev2 = index_stream(950, 1000) + index_stream(1800, 1850) + [book(1850.5, [(0.48, 20)], [(0.52, 20)], BTC)]
    ev2.sort(key=lambda e: e.ts)
    e2, _, _ = run(s2, [crypto_market()], ev2)
    assert resting(e2, BTC) == []


def test_crypto_mm_jump_guard_pulls():
    s = CryptoTwapMM(CryptoMMParams(size=5, min_touch_depth=1, jump_k=3.0, jump_cooldown=30))
    ev = index_stream(950, 1300, wiggle=1.0)
    ev.append(book(1300.2, [(0.48, 20)], [(0.52, 20)], BTC))
    # 2% jump in a second
    ev.append(sig(1301, "btc_index", 102000.0))
    ev.append(book(1301.5, [(0.60, 20)], [(0.64, 20)], BTC))
    ev.sort(key=lambda e: e.ts)
    e, r, rec = run(s, [crypto_market()], ev)
    assert s.jump_until[BTC] > 1301
    assert resting(e, BTC) == []


def test_crypto_mm_flatten_rule_only_quotes_reducing_side():
    s = CryptoTwapMM(CryptoMMParams(size=5, min_touch_depth=1, max_abs_delta=10, max_inventory=100))
    ev = index_stream(950, 1300) + [book(1300.5, [(0.48, 20)], [(0.52, 20)], BTC)]
    ev.sort(key=lambda e: e.ts)
    e, r, rec = run(s, [crypto_market()], ev)
    # force a long position and re-quote
    e.positions[BTC].apply(Action.BUY, 0.50, 30, 0.0)
    s._quote(e.api, e.books[BTC])
    e._advance(e.now + 1)
    orders = resting(e, BTC)
    assert orders and all(o.action is Action.SELL for o in orders)


def test_crypto_mm_never_takes_even_when_book_is_mispriced():
    s = CryptoTwapMM(CryptoMMParams(size=5, min_touch_depth=1))
    ev = index_stream(950, 1000) + index_stream(1000, 1300, drift=2.0)  # strongly up -> fair ~1
    ev.append(book(1300.5, [(0.30, 20)], [(0.34, 20)], BTC))              # book says 0.32
    ev.sort(key=lambda e: e.ts)
    e, r, rec = run(s, [crypto_market()], ev)
    # fair outside band -> pulled; and in any case all orders are post-only
    assert all(o.post_only for o in rec.submitted)
    assert not any(f for f in e.fills if not f.is_maker)


def test_crypto_mm_signal_dict_value_and_twap_blend():
    s = CryptoTwapMM(CryptoMMParams(size=5, min_touch_depth=1, twap_weight=0.5))
    ev = [sig(t, "btc_index", {"price": 100000.0 + (1 if t % 2 else -1), "src": "coinbase"}) for t in range(950, 1300)]
    ev.append(sig(1299.5, "twap60", {"asset": "BTC", "twap": 100000.0}))
    ev.append(book(1300.5, [(0.48, 20)], [(0.52, 20)], BTC))
    ev.sort(key=lambda e: e.ts)
    e, r, rec = run(s, [crypto_market()], ev)
    assert BTC in s.last_fair and abs(s.last_fair[BTC] - 0.5) < 0.1
    assert len(resting(e, BTC)) == 2


# ----------------------------------------------------------------------------
# mm_weather_ladder
# ----------------------------------------------------------------------------
def ladder(n=4, close_ts=100000.0):
    ms = []
    for i in range(n):
        lo = 70 + 2 * i
        ms.append(mk(f"KXHIGHNY-26OCT16-B{lo}", series="KXHIGHNY", event_id="KXHIGHNY-26OCT16", close_ts=close_ts,
                     title=f"{lo}° to {lo + 1}°",
                     meta={"ladder_group": "KXHIGHNY-26OCT16", "rung_lo": lo, "rung_hi": lo + 1}))
    return ms


def test_weather_sells_only_overpriced_rungs_and_never_crosses():
    ms = ladder()
    fair = [0.10, 0.45, 0.35, 0.10]
    s = WeatherLadderMM(WeatherLadderParams(size=5, edge=0.03, min_touch_depth=1, peak_window=0.0))
    ev = []
    for m, f in zip(ms, fair):
        ev.append(sig(10, "fcst_prob", f, m.market_id))
    # market asks sum to 1.10: rung0 at 0.15 (over by 0.05), rung1 at 0.46 (not over enough), rung2 0.40, rung3 0.09 (under)
    asks = [0.15, 0.46, 0.40, 0.09]
    bids = [0.12, 0.42, 0.36, 0.06]
    for m, a, b in zip(ms, asks, bids):
        ev.append(book(20, [(b, 10)], [(a, 10)], m.market_id))
    e, r, rec = run(s, ms, ev)
    res = {o.market_id: o for o in resting(e)}
    assert all(o.action is Action.SELL for o in res.values())
    assert ms[0].market_id in res and ms[2].market_id in res
    assert ms[3].market_id not in res          # under-priced rung: do not sell
    for o in res.values():
        bk = e.books[o.market_id]
        assert o.price > bk.best_bid           # never crosses
        assert o.size <= 5
    # our ask on rung0 is at least fair+edge
    assert res[ms[0].market_id].price >= 0.10 + 0.03 - 1e-9
    assert all(o.post_only for o in rec.submitted)


def test_weather_pulls_when_forecast_stale_or_missing():
    ms = ladder()
    s = WeatherLadderMM(WeatherLadderParams(size=5, signal_max_age=100, min_touch_depth=1, peak_window=0.0))
    ev = [sig(10, "fcst_prob", 0.10, ms[0].market_id), book(20, [(0.12, 10)], [(0.20, 10)], ms[0].market_id),
          book(200, [(0.12, 10)], [(0.20, 10)], ms[0].market_id)]
    e, r, rec = run(s, ms, ev)
    assert resting(e) == []
    assert any(o.action is Action.SELL for o in rec.submitted)  # it did quote at t=20


def test_weather_peak_window_pulls_favorites_only():
    ms = ladder(close_ts=10 * 3600.0)
    # peak at close - 6h = 4h; now = 2h -> inside the 6h peak window
    s = WeatherLadderMM(WeatherLadderParams(size=10, edge=0.02, min_touch_depth=1, peak_window=6, favorite_thresh=0.4))
    ev = [sig(7000, "fcst_prob", 0.50, ms[1].market_id), sig(7000, "fcst_prob", 0.08, ms[3].market_id),
          book(7200, [(0.55, 10)], [(0.60, 10)], ms[1].market_id),
          book(7200, [(0.12, 10)], [(0.16, 10)], ms[3].market_id)]
    e, r, rec = run(s, ms, ev)
    res = {o.market_id: o for o in resting(e)}
    assert ms[1].market_id not in res      # favourite pulled in the peak window
    assert ms[3].market_id in res          # longshot still sold, at half size
    assert res[ms[3].market_id].size == 5


def test_weather_group_short_cap_limits_total_size():
    ms = ladder()
    s = WeatherLadderMM(WeatherLadderParams(size=10, edge=0.01, min_touch_depth=1, max_group_short=12, peak_window=0.0))
    ev = []
    for m in ms:
        ev.append(sig(10, "fcst_prob", 0.10, m.market_id))
        ev.append(book(20, [(0.25, 50)], [(0.30, 50)], m.market_id))
    # fill the first two asks via prints through them
    ev.append(trade(30, 0.35, 10, True, ms[0].market_id))
    ev.append(trade(31, 0.35, 10, True, ms[1].market_id))
    e, r, rec = run(s, ms, ev)
    sold = -sum(e.positions[m.market_id].contracts for m in ms)
    assert sold <= 12 + 1e-9
    # after the cap is reached, no further resting asks of positive size
    for o in resting(e):
        assert o.size <= 12 - sold + 1e-9 or sold < 12


def test_weather_ladder_sum_guard_blocks_when_ladder_not_rich():
    ms = ladder(n=2)
    s = WeatherLadderMM(WeatherLadderParams(size=5, edge=0.02, sum_margin=0.10, min_touch_depth=1, peak_window=0.0))
    # fairs 0.5/0.5, our asks would be 0.52 each -> sum 1.04 < 1.10 margin -> no quotes
    ev = [sig(10, "fcst_prob", 0.5, ms[0].market_id), sig(10, "fcst_prob", 0.5, ms[1].market_id),
          book(20, [(0.49, 10)], [(0.53, 10)], ms[0].market_id), book(20, [(0.49, 10)], [(0.53, 10)], ms[1].market_id)]
    e, r, rec = run(s, ms, ev)
    assert resting(e) == []


# ----------------------------------------------------------------------------
# sharp_line_maker
# ----------------------------------------------------------------------------
NFL = "KXNFLGAME-26OCT19-KC"


def nfl_market():
    return mk(NFL, series="KXNFLGAME", close_ts=1e6)


def test_sharp_quotes_around_line_with_fee_aware_spread():
    s = SharpLineMaker(SharpLineParams(size=5, half_spread=0.0, edge_min=0.005, min_touch_depth=1))
    ev = [sig(10, "sharp_prob", {"p": 0.60}, NFL), book(11, [(0.55, 20)], [(0.65, 20)], NFL)]
    e, r, rec = run(s, [nfl_market()], ev, fee=KALSHI_WITH_MAKER_FEES)
    orders = resting(e, NFL)
    assert {o.action for o in orders} == {Action.BUY, Action.SELL}
    bid = next(o.price for o in orders if o.action is Action.BUY)
    ask = next(o.price for o in orders if o.action is Action.SELL)
    fee = 0.0175 * 0.6 * 0.4
    assert 0.60 - bid >= fee + 0.005 - 1e-9 and ask - 0.60 >= fee + 0.005 - 1e-9
    assert bid < 0.65 and ask > 0.55
    assert all(o.post_only for o in rec.submitted)


def test_sharp_pulls_on_stale_signal_live_game_and_divergence():
    base = dict(size=5, max_age=100, min_touch_depth=1)
    # stale
    s = SharpLineMaker(SharpLineParams(**base))
    e, _, _ = run(s, [nfl_market()], [sig(10, "sharp_prob", 0.6, NFL), book(11, [(0.55, 20)], [(0.65, 20)], NFL),
                                      book(200, [(0.55, 20)], [(0.65, 20)], NFL)])
    assert resting(e, NFL) == []
    # live
    s = SharpLineMaker(SharpLineParams(**base))
    e, _, _ = run(s, [nfl_market()], [sig(10, "sharp_prob", 0.6, NFL), book(11, [(0.55, 20)], [(0.65, 20)], NFL),
                                      sig(12, "game_state", "in", NFL)])
    assert resting(e, NFL) == []
    # allow_live keeps quotes
    s = SharpLineMaker(SharpLineParams(allow_live=True, **base))
    e, _, _ = run(s, [nfl_market()], [sig(10, "sharp_prob", 0.6, NFL), book(11, [(0.55, 20)], [(0.65, 20)], NFL),
                                      sig(12, "game_state", "in", NFL)])
    assert len(resting(e, NFL)) == 2
    # divergence
    s = SharpLineMaker(SharpLineParams(**base))
    e, _, _ = run(s, [nfl_market()], [sig(10, "sharp_prob", 0.6, NFL), book(11, [(0.80, 20)], [(0.84, 20)], NFL)])
    assert resting(e, NFL) == []


def test_sharp_sizes_capped_by_depth():
    s = SharpLineMaker(SharpLineParams(size=50, min_touch_depth=1, depth_frac_cap=0.5))
    ev = [sig(10, "sharp_prob", 0.5, NFL), book(11, [(0.45, 8), (0.44, 100)], [(0.55, 6), (0.56, 100)], NFL)]
    e, _, _ = run(s, [nfl_market()], ev)
    for o in resting(e, NFL):
        assert o.size <= (4 if o.action is Action.BUY else 3)


def test_quote_manager_no_orphans_under_latency():
    """Requotes inside the order-latency window used to place duplicates that were
    never cancelled (the 2026-10-16 KXBTC15M run rested 23 bids for one quote)."""
    from pb.strategies.base import Quote, QuoteManager

    class S(Strategy):
        name = "qm"

        def on_start(self, api):
            self.qm = QuoteManager(api, self.name)

        def on_book(self, api, b):
            for _ in range(4):                      # several index prints per book tick
                self.qm.set("M", Quote(0.48, 0.52, 10, 10))

    e = Engine([mk()], lambda m: KALSHI_DEFAULT, SimConfig(order_latency=0.3, cancel_latency=0.3))
    e.add_strategy(S())
    e.run([book(t, [(0.47, 100)], [(0.53, 100)]) for t in range(1, 11)])
    assert len(e.orders) == 2 and sum(o.remaining for o in e.orders.values()) == 20


def test_quote_manager_sweeps_orphans_and_forgets_rejected():
    from pb.strategies.base import Quote, QuoteManager

    class S(Strategy):
        name = "qm"

        def on_start(self, api):
            self.qm = QuoteManager(api, self.name)
            self.n = 0

        def on_book(self, api, b):
            self.n += 1
            if self.n == 1:   # an untracked order of ours (e.g. from a resumed run)
                api.place(Order("M", Action.BUY, 0.30, 5, strategy=self.name))
            self.qm.set("M", Quote(0.48, None, 10, 0))

    e = Engine([mk()], lambda m: KALSHI_DEFAULT, SimConfig(order_latency=0.0, cancel_latency=0.0))
    e.add_strategy(S())
    e.run([book(t, [(0.47, 100)], [(0.53, 100)]) for t in range(1, 4)])
    assert [o.price for o in e.orders.values()] == [0.48]
    # a risk-rejected id is dropped immediately and re-placed on the next quote
    qm = e.strategies[0].qm
    rejected = Order("M", Action.BUY, 0.48, 10, order_id="rejected-1", strategy="qm")
    qm.live["M"]["bid"] = rejected
    qm.set("M", Quote(0.48, None, 10, 0))
    e._advance(e.now + 1.0)                     # let the replacement land and the orphan sweep run
    assert qm.live["M"]["bid"] is not rejected
    assert [o.order_id for o in e.orders.values()] == [qm.live["M"]["bid"].order_id]
