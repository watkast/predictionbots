import math

import pytest

from oddsmath import core
from oddsmath.core import OddsError


def test_conversions_round_trip():
    for p in (0.05, 0.3, 0.5, 0.7, 0.95):
        assert core.american_to_prob(core.prob_to_american(p)) == pytest.approx(p, abs=1e-4)
        assert core.decimal_to_prob(core.prob_to_decimal(p)) == pytest.approx(p)
        assert core.fractional_to_prob(core.prob_to_fractional(p)) == pytest.approx(p, abs=2e-3)
    assert core.american_to_prob(-110) == pytest.approx(110 / 210)
    assert core.american_to_prob(150) == pytest.approx(0.4)
    assert core.fractional_to_prob("5/2") == pytest.approx(1 / 3.5)
    assert core.cents_to_prob(63) == 0.63
    assert core.prob_to_american(0.5) == -100.0


def test_conversion_errors():
    with pytest.raises(OddsError):
        core.american_to_prob(50)
    with pytest.raises(OddsError):
        core.decimal_to_prob(1.0)
    with pytest.raises(OddsError):
        core.fractional_to_prob("abc")
    with pytest.raises(OddsError):
        core.to_prob(0.5, "martian")
    with pytest.raises(OddsError):
        core.cents_to_prob(100)


@pytest.mark.parametrize("method", core.DEVIG_METHODS)
def test_devig_sums_to_one_and_removes_vig(method):
    implied = [core.american_to_prob(-110), core.american_to_prob(-110)]
    fair = core.devig(implied, method)
    assert sum(fair) == pytest.approx(1.0)
    assert fair[0] == pytest.approx(0.5, abs=1e-6)
    three = [0.5, 0.35, 0.25]  # 10% overround, 3 outcomes
    fair3 = core.devig(three, method)
    assert sum(fair3) == pytest.approx(1.0)
    assert fair3[0] > fair3[1] > fair3[2]


def test_devig_power_and_shin_favor_longshots_less_than_multiplicative():
    # favourite-longshot bias: power/shin shade more off the longshot than proportional scaling
    q = [0.80, 0.30]
    mult = core.devig(q, "multiplicative")
    power = core.devig(q, "power")
    shin = core.devig(q, "shin")
    assert power[1] < mult[1]
    assert shin[1] < mult[1]


def test_devig_report_all_methods_and_hold():
    rep = core.devig_report([-110, -110], "american", "all", ["A", "B"])
    assert rep["hold"] == pytest.approx(2 * 110 / 210 - 1, abs=1e-6)
    assert set(rep["outcomes"][0]) >= {"fair_multiplicative", "fair_additive", "fair_power", "fair_shin"}
    with pytest.raises(OddsError):
        core.devig_report([-110], "american")
    with pytest.raises(OddsError):
        core.devig_report([-110, -110], "american", "power", ["only-one"])


def test_kalshi_fee_matches_repo_formula():
    # 0.07 * 100 * 0.5 * 0.5 = 1.75 -> rounds up to the cent (already exact)
    f = core.venue_fee("kalshi", 0.5, 100)
    assert f["fee_usd"] == 1.75
    # 0.07 * 1 * 0.5 * 0.5 = 0.0175 -> ceil to 0.02
    assert core.venue_fee("kalshi", 0.5, 1)["fee_usd"] == 0.02
    assert core.venue_fee("kalshi", 0.5, 100, "maker")["fee_usd"] == 0.0
    assert core.venue_fee("kalshi", 0.5, 100, "maker", maker_fees=True)["fee_usd"] == pytest.approx(0.4375, abs=0.01)


def test_polymarket_and_novig_fees():
    assert core.venue_fee("polymarket", 0.5, 100, category="crypto")["fee_usd"] == pytest.approx(1.75)
    assert core.venue_fee("polymarket", 0.5, 100, category="politics")["fee_usd"] == pytest.approx(1.0)
    assert core.venue_fee("polymarket", 0.5, 100, category="geopolitics")["fee_usd"] == 0.0
    assert core.venue_fee("polymarket", 0.5, 100, side="maker", category="crypto")["fee_usd"] == 0.0
    assert core.venue_fee("novig", 0.5, 100)["fee_usd"] == 0.0            # pregame free
    assert core.venue_fee("novig", 0.5, 100, live=True)["fee_usd"] == pytest.approx(1.5)
    assert core.venue_fee("novig", 0.5, 100, side="maker", live=True)["fee_usd"] == 0.0
    with pytest.raises(OddsError):
        core.venue_fee("bovada", 0.5, 1)
    with pytest.raises(OddsError):
        core.venue_fee("kalshi", 0.5, 0)


def test_ev_and_kelly():
    r = core.ev_report(0.55, 2.0, "decimal", stake=100, kelly_mult=1.0, bankroll=1000)
    assert r["ev_usd"] == pytest.approx(10.0)
    assert r["edge"] == pytest.approx(0.05)
    assert r["kelly_full"] == pytest.approx(0.10)
    assert r["kelly_stake_usd"] == pytest.approx(100.0)
    # no edge -> zero kelly, negative EV
    r2 = core.ev_report(0.45, 2.0)
    assert r2["kelly_full"] == 0.0 and r2["ev_usd"] < 0
    # prediction market: fair 0.60, buy at 55c on Kalshi as taker with $55 (100 contracts)
    r3 = core.ev_report(0.60, 55, "cents", stake=55, venue="kalshi")
    assert r3["fee_usd"] == pytest.approx(0.07 * 100 * 0.55 * 0.45, abs=0.01)
    assert r3["ev_usd"] == pytest.approx(100 * (0.60 - 0.55) - r3["fee_usd"], abs=1e-6)
    with pytest.raises(OddsError):
        core.ev_report(0.5, 2.0, stake=0)


def test_arb_detection_and_stakes():
    outcomes = [
        {"label": "home", "quotes": [{"book": "a", "odds": 2.10}, {"book": "b", "odds": 1.95}]},
        {"label": "away", "quotes": [{"book": "a", "odds": 1.90}, {"book": "b", "odds": 2.05}]},
    ]
    r = core.arb_report(outcomes, bankroll=100)
    assert r["is_arb"]
    assert r["legs"][0]["book"] == "a" and r["legs"][1]["book"] == "b"
    assert r["sum_implied"] == pytest.approx(1 / 2.10 + 1 / 2.05)
    assert sum(l["stake"] for l in r["legs"]) == pytest.approx(100, abs=0.02)
    payouts = [l["payout_if_wins"] for l in r["legs"]]
    assert max(payouts) - min(payouts) < 0.05
    assert r["guaranteed_profit_usd"] > 0
    no_arb = core.arb_report([{"quotes": [{"odds": -110, "fmt": "american"}]},
                              {"quotes": [{"odds": -110, "fmt": "american"}]}])
    assert not no_arb["is_arb"] and no_arb["margin_pct"] < 0
    with pytest.raises(OddsError):
        core.arb_report([{"quotes": []}, {"quotes": [{"odds": 2}]}])


def test_complete_set_needs_more_than_fees():
    # 48c + 48c = 4c gross edge; Kalshi taker fees ~1.75c/contract each leg -> ~0.5c net
    r = core.complete_set_report(0.48, 0.48, "kalshi", 100)
    assert r["gross_edge_cents"] == pytest.approx(4.0)
    assert r["is_arb"] and 0 < r["net_profit_usd"] < 1.0
    r2 = core.complete_set_report(0.49, 0.49, "kalshi", 100)
    assert not r2["is_arb"]
    r3 = core.complete_set_report(0.49, 0.49, "novig", 100)  # pregame free
    assert r3["is_arb"] and r3["net_profit_usd"] == pytest.approx(2.0)


def test_parlay():
    r = core.parlay([0.5, 0.5], offered_decimal=3.5)
    assert r["fair_prob"] == 0.25 and r["fair_decimal"] == 4.0
    assert r["ev_per_unit"] == pytest.approx(0.25 * 2.5 - 0.75)
    with pytest.raises(OddsError):
        core.parlay([])
    assert math.isclose(core.parlay([0.9])["fair_prob"], 0.9)
