"""Behavioural tests: favorite_maker, endgame_bond, complete_set_arb,
cross_venue_arb, mean_revert_overreaction, taker_lag, taker_momentum."""
import math

import pytest

from pb.core.fees import KALSHI_DEFAULT, KALSHI_WITH_MAKER_FEES, polymarket_schedule
from pb.core.types import Action, TIF, Venue
from pb.sim.engine import SimConfig
from pb.strategies.complete_set_arb import CompleteSetArb, CompleteSetParams
from pb.strategies.cross_venue_arb import CrossVenueArb, CrossVenueParams
from pb.strategies.endgame_bond import EndgameBond, EndgameParams
from pb.strategies.favorite_maker import FavoriteMaker, FavoriteMakerParams
from pb.strategies.mean_revert_overreaction import OverreactionFade, OverreactionParams
from pb.strategies.taker_lag import TakerLag, TakerLagParams
from pb.strategies.taker_momentum import TakerMomentum, TakerMomentumParams
from tests.helpers import book, mk, resting, run, settle, sig, trade

DAY = 86400.0


# ----------------------------------------------------------------------------
# favorite_maker
# ----------------------------------------------------------------------------
def test_favorite_bids_yes_favourite_as_maker_below_ask():
    m = mk("KXPRES-26-D", series="KXPRES", close_ts=60 * DAY)
    s = FavoriteMaker(FavoriteMakerParams(size=10, min_touch_depth=1))
    e, r, rec = run(s, [m], [book(0, [(0.80, 20)], [(0.82, 20)], m.market_id)])
    o = resting(e)
    assert len(o) == 1 and o[0].action is Action.BUY and o[0].post_only
    assert o[0].price <= 0.81 and o[0].price >= 0.80
    assert o[0].size <= 10


def test_favorite_sells_yes_when_no_is_the_favourite():
    m = mk("KXPRES-26-R", series="KXPRES", close_ts=60 * DAY)
    s = FavoriteMaker(FavoriteMakerParams(size=10, min_touch_depth=1))
    e, r, rec = run(s, [m], [book(0, [(0.18, 20)], [(0.20, 20)], m.market_id)])
    o = resting(e)
    assert len(o) == 1 and o[0].action is Action.SELL
    assert o[0].price >= 0.19


def test_favorite_excludes_sports_and_short_horizons_and_mid_prices():
    sport = mk("KXNFLGAME-X", series="KXNFLGAME", close_ts=60 * DAY)
    s = FavoriteMaker(FavoriteMakerParams(min_touch_depth=1))
    e, _, _ = run(s, [sport], [book(0, [(0.80, 20)], [(0.82, 20)], sport.market_id)])
    assert resting(e) == []
    short = mk("KXCPI-X", series="KXCPI", close_ts=0.5 * DAY)
    s = FavoriteMaker(FavoriteMakerParams(min_touch_depth=1))
    e, _, _ = run(s, [short], [book(0, [(0.80, 20)], [(0.82, 20)], short.market_id)])
    assert resting(e) == []
    midp = mk("KXPRES-M", series="KXPRES", close_ts=60 * DAY)
    s = FavoriteMaker(FavoriteMakerParams(min_touch_depth=1))
    e, _, _ = run(s, [midp], [book(0, [(0.50, 20)], [(0.52, 20)], midp.market_id)])
    assert resting(e) == []


def test_favorite_hurdle_blocks_low_annualised_edge():
    # 0.95 price, 300 days: edge tiny relative to lock -> no quote
    m = mk("KXPRES-L", series="KXPRES", close_ts=300 * DAY)
    s = FavoriteMaker(FavoriteMakerParams(min_touch_depth=1, hurdle_annual=0.5, edge=0.0))
    e, _, _ = run(s, [m], [book(0, [(0.95, 20)], [(0.96, 20)], m.market_id)])
    assert resting(e) == []
    s2 = FavoriteMaker(FavoriteMakerParams(min_touch_depth=1, hurdle_annual=0.0, edge=0.0))
    e2, _, _ = run(s2, [m], [book(0, [(0.95, 20)], [(0.96, 20)], m.market_id)])
    assert len(resting(e2)) == 1


def test_favorite_calibration_slope():
    s = FavoriteMaker(FavoriteMakerParams())
    assert s.true_prob(0.8, 0.5) == pytest.approx(0.8)
    assert s.true_prob(0.8, 60) == pytest.approx(0.5 + 1.32 * 0.3)


# ----------------------------------------------------------------------------
# endgame_bond
# ----------------------------------------------------------------------------
def test_endgame_bids_in_window_with_depth_and_caps():
    m = mk("KXHIGHNY-X", series="KXHIGHNY", close_ts=6 * 3600.0)
    s = EndgameBond(EndgameParams(size=500, min_depth=20, max_per_market=100))
    e, r, rec = run(s, [m], [book(0, [(0.96, 200)], [(0.98, 200)], m.market_id)])
    o = resting(e)
    assert len(o) == 1 and o[0].action is Action.BUY and o[0].price == pytest.approx(0.96)
    assert o[0].size <= 100 / 0.96 + 1e-9 and o[0].size <= 100  # depth frac 0.5 * 200
    assert all(x.post_only and x.tif is TIF.GTC for x in rec.submitted)


def test_endgame_gates_time_depth_category():
    base = EndgameParams(min_depth=20)
    far = mk("KXHIGHNY-F", series="KXHIGHNY", close_ts=48 * 3600.0)
    e, _, _ = run(EndgameBond(base), [far], [book(0, [(0.96, 200)], [(0.98, 200)], far.market_id)])
    assert resting(e) == []
    thin = mk("KXHIGHNY-T", series="KXHIGHNY", close_ts=6 * 3600.0)
    e, _, _ = run(EndgameBond(base), [thin], [book(0, [(0.96, 5)], [(0.98, 200)], thin.market_id)])
    assert resting(e) == []
    pol = mk("KXSCOTUS-P", series="KXSCOTUS", close_ts=6 * 3600.0)
    e, _, _ = run(EndgameBond(base), [pol], [book(0, [(0.96, 200)], [(0.98, 200)], pol.market_id)])
    assert resting(e) == []
    late = mk("KXHIGHNY-L", series="KXHIGHNY", close_ts=5 * 60.0)
    e, _, _ = run(EndgameBond(base), [late], [book(0, [(0.96, 200)], [(0.98, 200)], late.market_id)])
    assert resting(e) == []


def test_endgame_total_cap_across_markets():
    ms = [mk(f"KXHIGHNY-{i}", series="KXHIGHNY", close_ts=6 * 3600.0) for i in range(3)]
    s = EndgameBond(EndgameParams(size=100, min_depth=20, max_per_market=1000, max_total=150))
    ev = []
    for i, m in enumerate(ms):
        ev.append(book(i, [(0.96, 500)], [(0.98, 500)], m.market_id))
        ev.append(trade(i + 0.5, 0.95, 100, False, m.market_id))   # sell print through our bid -> fills
    e, r, rec = run(s, ms, ev)
    locked = sum(e.positions[m.market_id].capital_at_risk() for m in ms)
    assert locked <= 150 + 100 * 0.96 + 1e-6   # at most one over-fill of a resting order
    assert all(f.is_maker for f in e.fills)


# ----------------------------------------------------------------------------
# complete_set_arb
# ----------------------------------------------------------------------------
def test_binary_crossed_book_arb_sizes_to_depth_and_nets_flat():
    m = mk("KXX-1", series="KXX")
    s = CompleteSetArb(CompleteSetParams(min_edge=0.0, min_size=1, depth_frac=1.0))
    # YES bid 0.60 > YES ask 0.52: buy at 0.52, sell at 0.60, 8c gross, fees ~ 2*0.07*0.25 = 3.5c
    e, r, rec = run(s, [m], [book(0, [(0.60, 7)], [(0.52, 12)], m.market_id)])
    assert sum(f.size for f in e.fills if f.action is Action.BUY) == 7
    assert sum(f.size for f in e.fills if f.action is Action.SELL) == 7
    assert e.positions[m.market_id].contracts == 0
    assert all(not f.is_maker and o.tif is TIF.IOC for f, o in zip(e.fills, rec.submitted))
    assert r.pnl > 0


def test_binary_arb_rejected_when_fees_eat_edge():
    m = mk("KXX-2", series="KXX")
    s = CompleteSetArb(CompleteSetParams(min_edge=0.0, min_size=1))
    e, r, rec = run(s, [m], [book(0, [(0.53, 50)], [(0.52, 50)], m.market_id)])   # 1c gross < 3.5c fees
    assert rec.submitted == []


def test_multi_outcome_buy_all_yes_sized_to_thinnest_leg():
    ms = [mk(f"KXWIN-{c}", series="KXWIN", event_id="KXWIN", meta={"mutually_exclusive": True}) for c in "ABC"]
    s = CompleteSetArb(CompleteSetParams(min_edge=0.0, min_size=1, depth_frac=1.0), [m.market_id for m in ms])
    ev = [book(0, [(0.25, 50)], [(0.28, 50)], ms[0].market_id),
          book(1, [(0.25, 50)], [(0.28, 4)], ms[1].market_id),      # thin leg: 4 contracts
          book(2, [(0.30, 50)], [(0.32, 50)], ms[2].market_id)]     # sum asks 0.88 + fees ~ 0.045 < 1
    e, r, rec = run(s, ms, ev)
    assert len(rec.submitted) == 3
    assert all(o.size == 4 and o.tif is TIF.IOC for o in rec.submitted)
    assert all(e.positions[m.market_id].contracts == 4 for m in ms)


def test_multi_outcome_waits_for_every_known_sibling():
    ms = [mk(f"KXWIN4-{c}", series="KXWIN4", event_id="KXWIN4", meta={"mutually_exclusive": True}) for c in "ABC"]
    s = CompleteSetArb(CompleteSetParams(min_edge=0.0, min_size=1, depth_frac=1.0), [m.market_id for m in ms])
    ev = [book(0, [(0.25, 50)], [(0.28, 50)], ms[0].market_id), book(1, [(0.25, 50)], [(0.28, 50)], ms[1].market_id)]
    e, r, rec = run(s, ms, ev)   # C never shows a book: 0.56 "sum" is not a complete set
    assert rec.submitted == []


def test_multi_outcome_requires_exclusivity_flag():
    ms = [mk(f"KXWIN2-{c}", series="KXWIN2", event_id="KXWIN2") for c in "AB"]
    s = CompleteSetArb(CompleteSetParams(min_edge=0.0, min_size=1))
    ev = [book(0, [(0.25, 50)], [(0.28, 50)], ms[0].market_id), book(1, [(0.25, 50)], [(0.28, 50)], ms[1].market_id)]
    e, r, rec = run(s, ms, ev)
    assert rec.submitted == []


def test_multi_outcome_residual_flattened_on_partial_fill():
    ms = [mk(f"KXWIN3-{c}", series="KXWIN3", event_id="KXWIN3", meta={"mutually_exclusive": True}) for c in "AB"]
    s = CompleteSetArb(CompleteSetParams(min_edge=0.0, min_size=1, depth_frac=1.0))
    # leg B's book disappears before our order lands (latency), so only A fills
    cfg = SimConfig(order_latency=0.5, cancel_latency=0.0)
    ev = [book(0, [(0.30, 50)], [(0.35, 10)], ms[0].market_id), book(0.1, [(0.30, 50)], [(0.35, 10)], ms[1].market_id),
          book(0.2, [(0.30, 50)], [(0.90, 10)], ms[1].market_id),   # B ask vanished
          book(3, [(0.30, 50)], [(0.35, 10)], ms[0].market_id)]
    e, r, rec = run(s, ms, ev, cfg=cfg)
    assert e.positions[ms[1].market_id].contracts == 0
    assert e.positions[ms[0].market_id].contracts == 0   # flattened the 10 we bought on A


# ----------------------------------------------------------------------------
# cross_venue_arb
# ----------------------------------------------------------------------------
def pair_markets():
    k = mk("KXBTC15M-P", series="KXBTC15M", meta={"pair_id": "btc-1"})
    p = mk("0xpolytoken", venue=Venue.POLYMARKET, series="crypto", meta={"pair_id": "btc-1", "category": "crypto"})
    return k, p


def fee_table(k, p):
    return {k.market_id: KALSHI_DEFAULT, p.market_id: polymarket_schedule("crypto")}


def test_cross_venue_taker_takes_only_when_gap_clears_both_fees():
    k, p = pair_markets()
    s = CrossVenueArb(CrossVenueParams(min_edge=0.0, min_size=1, depth_frac=1.0, slippage_pad=0.0))
    # Kalshi ask 0.40, Poly bid 0.52 -> 12c gap; fees 0.07*0.24 + 0.07*0.25 ~ 3.4c
    ev = [book(0, [(0.38, 30)], [(0.40, 30)], k.market_id), book(0.1, [(0.52, 10)], [(0.54, 30)], p.market_id),
          settle(10, 1.0, k.market_id), settle(10, 1.0, p.market_id)]
    e, r, rec = run(s, [k, p], ev, fee=fee_table(k, p))
    assert len(rec.submitted) == 2
    assert all(o.tif is TIF.IOC and o.size == 10 for o in rec.submitted)
    assert r.pnl == pytest.approx(10 * (0.52 - 0.40) - r.fees)
    assert r.pnl > 0
    # small gap -> nothing
    s2 = CrossVenueArb(CrossVenueParams(min_edge=0.0, min_size=1))
    ev2 = [book(0, [(0.38, 30)], [(0.40, 30)], k.market_id), book(0.1, [(0.42, 10)], [(0.44, 30)], p.market_id)]
    e2, r2, rec2 = run(s2, [k, p], ev2, fee=fee_table(k, p))
    assert rec2.submitted == []


def test_cross_venue_taker_walks_depth_not_touch():
    k, p = pair_markets()
    s = CrossVenueArb(CrossVenueParams(min_edge=0.0, min_size=1, depth_frac=1.0, slippage_pad=0.0, max_size=20))
    # touch gap 12c but only 2 contracts at the touch; next level gap is 1c -> average gap too small for 20
    ev = [book(0, [(0.38, 30)], [(0.40, 2), (0.51, 50)], k.market_id), book(0.1, [(0.52, 50)], [(0.54, 30)], p.market_id)]
    e, r, rec = run(s, [k, p], ev, fee=fee_table(k, p))
    # size was capped by touch depth (2) -> below min_size? min_size=1 so it trades 2
    assert all(o.size == 2 for o in rec.submitted)


def test_cross_venue_maker_mode_rests_on_kalshi_then_hedges():
    k, p = pair_markets()
    s = CrossVenueArb(CrossVenueParams(mode="maker_kalshi", min_edge=0.0, min_size=1, hedge_pad=0.0,
                                       slippage_pad=0.0, maker_size=10))
    ev = [book(0, [(0.40, 30)], [(0.50, 30)], k.market_id), book(0.1, [(0.52, 50)], [(0.54, 30)], p.market_id)]
    e, r, rec = run(s, [k, p], ev, fee=fee_table(k, p))
    o = resting(e, k.market_id)
    assert len(o) == 1 and o[0].post_only and o[0].action is Action.BUY
    assert o[0].price < 0.52 and o[0].price >= 0.40
    # a sell print through our bid fills us; the hedge fires on Polymarket
    e2, r2, rec2 = run(CrossVenueArb(CrossVenueParams(mode="maker_kalshi", min_edge=0.0, min_size=1, hedge_pad=0.0,
                                                      slippage_pad=0.0, maker_size=10)),
                       [k, p], ev + [trade(1, 0.30, 10, False, k.market_id)], fee=fee_table(k, p))
    assert e2.positions[k.market_id].contracts == 10
    assert e2.positions[p.market_id].contracts == -10
    assert any(not f.is_maker and f.market_id == p.market_id for f in e2.fills)


# ----------------------------------------------------------------------------
# mean_revert_overreaction
# ----------------------------------------------------------------------------
def jump_events(mid, up=True, prints=8):
    ev = [book(0, [(0.49, 20)], [(0.51, 20)], mid)]
    for t in range(1, 40):
        ev.append(book(t * 10, [(0.49, 20)], [(0.51, 20)], mid))
    # storm of prints then a jump
    base = 400
    for i in range(prints):
        ev.append(trade(base + i, 0.51 if up else 0.49, 5, up, mid))
    px = (0.59, 0.61) if up else (0.39, 0.41)
    ev.append(book(base + prints, [(px[0], 20)], [(px[1], 20)], mid))
    return ev


def test_overreaction_rests_far_side_post_only_and_never_crosses():
    m = mk("KXPOL-1", series="KXPOL", close_ts=1e6)
    s = OverreactionFade(OverreactionParams(jump=0.05, size=10))
    e, r, rec = run(s, [m], jump_events(m.market_id, up=True))
    o = resting(e)
    assert len(o) == 1 and o[0].action is Action.SELL and o[0].post_only
    assert o[0].price >= 0.61   # at or above the new ask
    assert o[0].size <= 10
    s2 = OverreactionFade(OverreactionParams(jump=0.05, size=10))
    e2, _, _ = run(s2, [m], jump_events(m.market_id, up=False))
    o2 = resting(e2)
    assert len(o2) == 1 and o2[0].action is Action.BUY and o2[0].price <= 0.39


def test_overreaction_needs_print_storm_and_is_off_on_crypto():
    m = mk("KXPOL-2", series="KXPOL", close_ts=1e6)
    s = OverreactionFade(OverreactionParams(jump=0.05, min_prints=5))
    e, _, rec = run(s, [m], jump_events(m.market_id, prints=2))
    assert rec.submitted == []
    c = mk("KXBTC15M-Z", series="KXBTC15M", close_ts=1e6)
    s = OverreactionFade(OverreactionParams(jump=0.05))
    e, _, rec = run(s, [c], jump_events(c.market_id))
    assert rec.submitted == []


def test_overreaction_takes_profit_on_reversion_and_time_stops():
    m = mk("KXPOL-3", series="KXPOL", close_ts=1e6)
    s = OverreactionFade(OverreactionParams(jump=0.05, size=10, tp_frac=0.5, tp_taker=True, tp_patience=0))
    ev = jump_events(m.market_id, up=True)
    t = ev[-1].ts
    ev.append(trade(t + 1, 0.70, 10, True, m.market_id))               # lifted through our ask -> short 10
    ev.append(book(t + 2, [(0.54, 20)], [(0.56, 20)], m.market_id))    # half reverted -> exit wanted
    ev.append(book(t + 3, [(0.54, 20)], [(0.56, 20)], m.market_id))    # patience 0 -> IOC at the ask
    e, r, rec = run(s, [m], ev)
    assert e.positions[m.market_id].contracts == 0
    assert r.pnl > 0


# ----------------------------------------------------------------------------
# taker baselines
# ----------------------------------------------------------------------------
BTC = "KXBTC15M-26OCT161315-T"


def test_taker_lag_takes_with_ioc_only_when_edge_beats_fee():
    m = mk(BTC, series="KXBTC15M", close_ts=1900.0, meta={"window_open_ts": 1000.0, "window_close_ts": 1900.0})
    s = TakerLag(TakerLagParams(edge=0.02, size=10, depth_frac=1.0))
    ev = [sig(t, "btc_index", 100000.0 + (1 if t % 2 else -1)) for t in range(950, 1001)]
    ev += [sig(t, "btc_index", 100000.0 + 1.5 * (t - 1000) + (1 if t % 2 else -1)) for t in range(1001, 1300)]
    ev.append(book(1300.5, [(0.50, 20)], [(0.55, 20)], BTC))   # fair >> 0.55
    e, r, rec = run(s, [m], ev)
    assert len(rec.submitted) == 1 and rec.submitted[0].tif is TIF.IOC and rec.submitted[0].action is Action.BUY
    assert e.fills and not e.fills[0].is_maker and e.fills[0].size <= 20
    # fairly priced book -> no take
    s2 = TakerLag(TakerLagParams(edge=0.02))
    ev2 = [sig(t, "btc_index", 100000.0 + (1 if t % 2 else -1)) for t in range(950, 1300)]
    ev2.append(book(1300.5, [(0.49, 20)], [(0.51, 20)], BTC))
    e2, _, rec2 = run(s2, [m], ev2)
    assert rec2.submitted == []


def test_taker_momentum_buys_after_move_and_exits():
    m = mk("KXPOL-M", series="KXPOL", close_ts=1e6)
    s = TakerMomentum(TakerMomentumParams(move=0.20, window=900, size=10, tp=0.05, stop=0.05, depth_frac=1.0))
    ev = [book(0, [(0.30, 20)], [(0.32, 20)], m.market_id), book(100, [(0.52, 20)], [(0.54, 20)], m.market_id),
          book(200, [(0.60, 20)], [(0.62, 20)], m.market_id)]
    e, r, rec = run(s, [m], ev)
    assert rec.submitted[0].action is Action.BUY and rec.submitted[0].tif is TIF.IOC
    assert e.fills[0].price == pytest.approx(0.54) and not e.fills[0].is_maker
    assert e.positions[m.market_id].contracts == 0  # exited on tp
    assert all(not f.is_maker for f in e.fills)
    assert r.fees > 0
