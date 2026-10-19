"""Behavioural tests for the ORACLE-LAG v4 taker rule (pb/strategies/oracle_lag.py)."""
from pb.core.types import Action, TIF, Venue
from pb.strategies.oracle_lag import OracleLag, OracleLagParams
from tests.helpers import book, mk, run, sig

OPEN = 1_792_152_000.0  # a window open
MID = "KXBTC15M-26OCT160815-15"


def _market():
    return mk(MID, venue=Venue.KALSHI, series="KXBTC15M", close_ts=OPEN + 900,
              meta={"window_open_ts": OPEN, "window_close_ts": OPEN + 900, "asset": "BTC"})


def _tape(path):
    """One tick per minute from 15 minutes before the open: path(k) is the price at minute k
    (k < 0 is pre-window history)."""
    ev = []
    for k in range(-15, 14):
        ev.append(sig(OPEN + 60 * k + 1, "btc_index", {"price": path(k)}))
        ev.append(sig(OPEN + 60 * k + 59, "btc_index", {"price": path(k)}))
    return ev


def test_buys_up_at_minute_10_when_spot_and_twap_clear_the_buffer():
    # flat 80,000 before the open, then +60 from minute 1: twap at minute 10 ~ 80,044 > 80,020
    path = lambda k: 80_000.0 if k < 1 else 80_060.0
    ev = _tape(path)
    ev.append(book(OPEN + 605, [(0.78, 500)], [(0.80, 500)], MID))
    ev.sort(key=lambda e: e.ts)
    s = OracleLag(OracleLagParams(atr_guard=False))
    e, r, rec = run(s, [_market()], ev)
    o = [x for x in rec.submitted if x.tif is TIF.IOC]
    assert len(o) == 1 and o[0].action is Action.BUY and o[0].price == 0.85
    assert o[0].size == 375  # $300 / 0.80
    # the resting take-profit follows the fill
    tp = [x for x in rec.submitted if x.tif is TIF.GTC]
    assert len(tp) == 1 and tp[0].action is Action.SELL and tp[0].price == 0.88 and tp[0].size == 375


def test_buys_down_as_sell_yes_and_respects_cap_and_ceasefire():
    path = lambda k: 80_000.0 if k < 1 else 79_940.0
    ev = _tape(path)
    # NO ask = 1 - bid: bid 0.04 -> NO at 0.96 -> ceasefire; nothing placed and the round is done
    ev.append(book(OPEN + 605, [(0.04, 500)], [(0.06, 500)], MID))
    ev.sort(key=lambda e: e.ts)
    s = OracleLag(OracleLagParams(atr_guard=False))
    e, r, rec = run(s, [_market()], ev)
    assert not rec.submitted and s.decisions[-1]["action"] == "ceasefire"
    # bid 0.14 -> NO at 0.86 > cap: keep watching, no order; later bid 0.20 -> NO at 0.80: take
    ev = _tape(path)
    ev.append(book(OPEN + 605, [(0.14, 500)], [(0.16, 500)], MID))
    ev.append(book(OPEN + 700, [(0.20, 500)], [(0.22, 500)], MID))
    ev.sort(key=lambda e: e.ts)
    s = OracleLag(OracleLagParams(atr_guard=False))
    e, r, rec = run(s, [_market()], ev)
    o = [x for x in rec.submitted if x.tif is TIF.IOC]
    assert len(o) == 1 and o[0].action is Action.SELL and abs(o[0].price - 0.15) < 1e-9 and o[0].ts >= OPEN + 700


def test_no_trade_before_minute_10_inside_chop_band_or_in_the_kill_window():
    path = lambda k: 80_000.0 if k < 1 else 80_060.0
    ev = _tape(path)
    ev.append(book(OPEN + 500, [(0.78, 500)], [(0.80, 500)], MID))   # too early at 500; live book carries on
    ev.sort(key=lambda e: e.ts)
    s = OracleLag(OracleLagParams(atr_guard=False))
    e, r, rec = run(s, [_market()], ev)
    assert rec.submitted and all(o.ts >= OPEN + 600 for o in rec.submitted)
    # kill window: book + fresh tick with <= 45 s left -> nothing
    ev = _tape(path)
    ev.append(sig(OPEN + 869, "btc_index", {"price": 80_060.0}))
    ev.append(book(OPEN + 870, [(0.78, 500)], [(0.80, 500)], MID))
    ev.sort(key=lambda e: e.ts)
    s = OracleLag(OracleLagParams(atr_guard=False))
    e, r, rec = run(s, [_market()], ev)
    assert not rec.submitted
    # chop: +8 only
    path = lambda k: 80_000.0 if k < 1 else 80_008.0
    ev = _tape(path)
    ev.append(book(OPEN + 605, [(0.78, 500)], [(0.80, 500)], MID))
    ev.sort(key=lambda e: e.ts)
    s = OracleLag(OracleLagParams(atr_guard=False))
    e, r, rec = run(s, [_market()], ev)
    assert not rec.submitted


def test_v4_veto_blocks_entry_when_price_dips_below_a_rising_twap():
    # rising twap (+60 from minute 1) but spot has dipped under the twap at minute 10
    def path(k):
        if k < 1:
            return 80_000.0
        if k < 10:
            return 80_080.0
        return 80_030.0  # > anchor + chop, twap still > anchor + 20, but spot < twap with slope > 0
    ev = _tape(path)
    ev.append(book(OPEN + 605, [(0.78, 500)], [(0.80, 500)], MID))
    ev.sort(key=lambda e: e.ts)
    s = OracleLag(OracleLagParams(atr_guard=False, v4_veto=True))
    e, r, rec = run(s, [_market()], ev)
    assert not rec.submitted
    s = OracleLag(OracleLagParams(atr_guard=False, v4_veto=False))
    e, r, rec = run(s, [_market()], ev)
    assert len(rec.submitted) >= 1


def test_size_is_capped_by_resting_depth_not_by_cash():
    path = lambda k: 80_000.0 if k < 1 else 80_060.0
    ev = _tape(path)
    ev.append(book(OPEN + 605, [(0.78, 500)], [(0.80, 12), (0.84, 5), (0.90, 1000)], MID))
    ev.sort(key=lambda e: e.ts)
    s = OracleLag(OracleLagParams(atr_guard=False))
    e, r, rec = run(s, [_market()], ev)
    o = [x for x in rec.submitted if x.tif is TIF.IOC]
    assert len(o) == 1 and o[0].size == 17
