"""pb.carry: backtest math, fee drag, basis shock, thresholds, paper tick, data parsers. No network."""
import importlib.util
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from pb.carry import data as cdata
from pb.carry import paper
from pb.carry.backtest import CarryParams, align, run_backtest, synthetic_dataset, walk_forward, HOURS_PER_YEAR
from pb.carry.venues import KRAKEN_BTC, COINBASE_BTC, LegFees, VenueFees, annualize, venue_fees

ROOT = Path(__file__).resolve().parents[1]
ZERO = VenueFees(name="zero", spot=LegFees(0, 0), perp=LegFees(0, 0), funding_interval_hours=8, perp_max_leverage=10,
                 maintenance_margin_frac=0.05)


def flat_dataset(n=400, rate=0.0001, price=50_000.0):
    """Constant funding, constant prices: pnl must be exactly funding - costs."""
    ts = 1_577_836_800.0 + np.arange(n) * 8 * 3600
    df = pd.DataFrame({"ts": ts, "rate": rate, "interval_hours": 8.0, "spot_close": price, "perp_close": price,
                       "perp_high": price})
    df["ann"] = df["rate"] * (HOURS_PER_YEAR / 8)
    return df


# --------------------------------------------------------------------------- venues / fees


def test_leg_cost_bps_and_per_contract():
    # Kraken US perp: $0.0113 per 0.01 BTC contract -> 100 contracts per BTC
    c = KRAKEN_BTC.perp.cost(50_000.0, 50_000.0, maker=False)  # 1 BTC = 100 contracts
    assert c == pytest.approx(1.13)
    assert KRAKEN_BTC.spot.cost(10_000, 50_000, maker=False) == pytest.approx(38.0)
    assert KRAKEN_BTC.spot.cost(10_000, 50_000, maker=True) == pytest.approx(22.0)
    cb = COINBASE_BTC.perp.cost(1_000, 100_000, maker=False)  # 1 nano contract
    assert cb == pytest.approx(1_000 * 2 / 1e4 + 0.15)


def test_venue_fee_overrides():
    v = venue_fees("kraken", "btc", {"spot.taker_bps": 80, "maintenance_margin_frac": 0.1})
    assert v.spot.taker_bps == 80 and v.maintenance_margin_frac == 0.1 and v.perp.per_contract == 0.0113
    with pytest.raises(KeyError):
        venue_fees("kraken", "BTC", {"nope": 1})


def test_annualize():
    assert annualize(0.0001, 8) == pytest.approx(0.1095)
    assert annualize(0.00001, 1) == pytest.approx(0.0876)


# --------------------------------------------------------------------------- backtest math


def test_funding_only_pnl_exact_with_zero_fees():
    df = flat_dataset(n=100, rate=0.0001)
    p = CarryParams(capital=15_000, perp_collateral_frac=0.5, tbill_rate=0.0, slippage_bps=0.0, entry_ann=0.05, exit_ann=0.0)
    r = run_backtest(df, p, ZERO)
    N = p.notional()
    assert N == pytest.approx(10_000)
    # signal valid from i=2 (lookback 3), enter at i=2, earn intervals 3..99 = 97 intervals
    assert r.n_trades == 1
    assert r.funding_captured == pytest.approx(97 * 0.0001 * N)
    assert r.net_pnl == pytest.approx(r.funding_captured)
    assert r.basis_pnl == pytest.approx(0.0)
    assert r.costs == 0.0
    assert r.time_in_market == pytest.approx(97 / 100)
    assert r.trades[0]["reason"] == "end_of_data"


def test_fee_drag_round_trip_and_slippage():
    df = flat_dataset(n=50, rate=0.0001, price=50_000)
    p = CarryParams(capital=15_000, tbill_rate=0.0, slippage_bps=2.0)
    r = run_backtest(df, p, KRAKEN_BTC)
    N = p.notional()
    spot_fee = 2 * N * 38 / 1e4
    perp_fee = 2 * (N / (0.01 * 50_000)) * 0.0113
    assert r.fees == pytest.approx(spot_fee + perp_fee)
    assert r.slippage == pytest.approx(4 * N * 2 / 1e4)  # 2 legs x 2 sides
    assert r.net_pnl == pytest.approx(r.funding_captured - r.fees - r.slippage)
    # Maker spot leg: cheaper and no slippage on that leg
    rm = run_backtest(df, CarryParams(capital=15_000, tbill_rate=0.0, slippage_bps=2.0, spot_maker=True), KRAKEN_BTC)
    assert rm.fees < r.fees and rm.slippage == pytest.approx(2 * N * 2 / 1e4)
    # Coinbase spot tier is a much larger drag than Kraken
    rc = run_backtest(df, p, COINBASE_BTC)
    assert rc.fees > 1.8 * r.fees


def test_idle_tbill_yield_when_flat_and_benchmark():
    df = flat_dataset(n=365 * 3 + 1, rate=-0.0001)  # never enters (negative funding)
    p = CarryParams(capital=10_000, tbill_rate=0.04)
    r = run_backtest(df, p, KRAKEN_BTC)
    assert r.n_trades == 0 and r.time_in_market == 0
    # simple (non-compounded) accrual over one year ~ 4%
    assert r.idle_yield == pytest.approx(408, rel=0.01)  # 4% compounded per interval over ~1 year
    assert r.benchmark_tbill_pnl == pytest.approx(400, rel=0.02)
    assert abs(r.excess_over_tbill_ann) < 0.002


def test_basis_shock_is_a_loss_until_exit_and_recorded():
    n = 60
    df = flat_dataset(n=n, rate=0.0002)
    # perp premium jumps +100 bps at i=20 against the short perp, stays
    df.loc[20:, "perp_close"] = df.loc[20:, "perp_close"] * 1.01
    df.loc[20:, "perp_high"] = df.loc[20:, "perp_close"]
    p = CarryParams(capital=15_000, tbill_rate=0.0, slippage_bps=0.0, entry_ann=0.05, exit_ann=0.0)
    r = run_backtest(df, p, ZERO)
    N = p.notional()
    assert r.worst_basis_shock_bps == pytest.approx(-100, rel=1e-3)
    assert r.worst_basis_shock_usd == pytest.approx(-0.01 * N, rel=1e-3)
    # equity dips by the shock while held; drawdown reflects it
    eq = r.equity.equity.to_numpy()
    assert eq[20] < eq[19]
    assert r.max_drawdown >= 0.01 * N - 0.0002 * N * 2
    # held to end: premium still there -> realized basis loss of N * 1%
    assert r.basis_pnl == pytest.approx(-0.01 * N, rel=1e-3)
    # the worst-any stat sees the same shock
    assert r.worst_basis_shock_bps_any == pytest.approx(-100, rel=1e-3)


def test_threshold_entry_and_exit_logic():
    n = 40
    rates = np.zeros(n)
    rates[5:15] = 0.0002  # ann 0.219 -> enter once trailing-3 mean > 0.08 (i=6: 2 of 3 prints)
    rates[15:] = 0.0      # trailing mean decays below exit 0.02 at i=17
    rates[30:] = -0.0001  # negative print
    df = flat_dataset(n=n)
    df["rate"] = rates
    df["ann"] = df["rate"] * (HOURS_PER_YEAR / 8)
    p = CarryParams(capital=15_000, tbill_rate=0.0, slippage_bps=0.0, entry_ann=0.08, exit_ann=0.02, lookback=3)
    r = run_backtest(df, p, ZERO)
    assert r.n_trades == 1
    t = r.trades[0]
    i_entry = int((df.ts == t["entry_ts"]).idxmax())
    i_exit = int((df.ts == t["exit_ts"]).idxmax())
    assert i_entry == 6 and i_exit == 17 and t["reason"] == "signal_below_exit"
    assert t["funding"] == pytest.approx(sum(rates[7:18]) * p.notional())
    # negative-print exit: enter again when rates high then a single negative print
    rates2 = np.full(n, 0.0002)
    rates2[20] = -0.00005
    df2 = flat_dataset(n=n)
    df2["rate"] = rates2
    df2["ann"] = df2["rate"] * (HOURS_PER_YEAR / 8)
    r2 = run_backtest(df2, p, ZERO)
    assert r2.trades[0]["reason"] == "negative_print" and r2.n_trades == 2
    r3 = run_backtest(df2, CarryParams(**{**asdict(p), "exit_on_negative_print": False}), ZERO)
    assert r3.n_trades == 1


def test_liquidation_on_rally_forced_exit():
    n = 30
    df = flat_dataset(n=n, rate=0.0002)
    # rally: perp high +60% at i=10 (collateral 50% + no idle - 5% maint = 45% distance)
    df.loc[10, "perp_high"] = 50_000 * 1.6
    p = CarryParams(capital=15_000, tbill_rate=0.0, slippage_bps=0.0, topup_from_idle=False, liq_penalty_bps=50)
    r = run_backtest(df, p, KRAKEN_BTC)
    assert r.liquidations == 1
    t = r.trades[0]
    assert t["reason"] == "liquidation"
    assert t["exit_perp"] == pytest.approx(50_000 * 1.45)
    assert t["liq_fee"] == pytest.approx(10.0 + p.notional() * 50 / 1e4)
    assert r.liq_distance_frac == pytest.approx(0.45)
    # with idle top-up the distance is wider and the same rally does not liquidate
    p2 = CarryParams(capital=30_000, notional_frac=1 / 3, tbill_rate=0.0, slippage_bps=0.0, topup_from_idle=True)
    r2 = run_backtest(df, p2, KRAKEN_BTC)
    assert r2.liquidations == 0 and r2.liq_distance_frac > 0.9


def test_align_merges_candles_and_perp_high():
    f = pd.DataFrame({"ts": [3600 * 8, 3600 * 16], "rate": [0.0001, 0.0002], "interval_hours": 8.0})
    hrs = np.arange(0, 17) * 3600.0
    spot = pd.DataFrame({"ts": hrs, "open": 1, "high": 1, "low": 1, "close": 100 + np.arange(17), "volume": 1})
    perp = spot.copy()
    perp["close"] = perp["close"] + 1
    perp["high"] = perp["close"] + 5
    perp.loc[12, "high"] = 999
    a = align(f, spot, perp)
    assert list(a.spot_close) == [108, 116]
    assert list(a.perp_close) == [109, 117]
    assert a.perp_high.iloc[0] == 109 + 5 and a.perp_high.iloc[1] == 999
    assert a.ann.iloc[0] == pytest.approx(annualize(0.0001, 8))


def test_walk_forward_picks_on_prior_year_and_scores_next():
    df = synthetic_dataset(n=3 * 365 * 3, seed=1, ann_mean=0.12)
    base = CarryParams(capital=10_000)
    wf = walk_forward(df, base, {"entry_ann": [0.05, 0.1], "exit_ann": [0.0, 0.02]}, ZERO)
    assert [o["year"] for o in wf["oos"]] == [2021, 2022]
    for o in wf["oos"]:
        assert o["train_year"] == o["year"] - 1 and set(o["chosen"]) == {"entry_ann", "exit_ann"}
    assert "annualized_net" in wf["aggregate"]


def test_synthetic_run_is_sane_and_summary_serialisable():
    df = synthetic_dataset(n=2000, seed=3)
    r = run_backtest(df, CarryParams(), KRAKEN_BTC)
    s = r.summary()
    json.dumps(s, default=float)
    assert 0 <= s["time_in_market"] <= 1
    assert s["intervals"] == 2000 and s["costs"] >= 0 and s["max_drawdown"] >= 0
    assert s["funding_captured"] + s["basis_pnl"] + s["idle_yield"] - s["costs"] == pytest.approx(s["net_pnl"], abs=1e-6)


# --------------------------------------------------------------------------- data parsers


def test_months_between_and_epoch_norm():
    assert cdata.months_between("2023-11", "2024-02") == ["2023-11", "2023-12", "2024-01", "2024-02"]
    assert cdata._norm_epoch_s(1_700_000_000_000) == 1_700_000_000.0
    assert cdata._norm_epoch_s(1_700_000_000_000_000) == 1_700_000_000.0
    assert cdata._norm_epoch_s(1_700_000_000) == 1_700_000_000.0


def test_parse_coinbase_perp_products():
    prods = [
        {"product_id": "BIP-20DEC30-CDE", "display_name": "nano Bitcoin Perp", "base_currency_id": "BTC",
         "future_product_details": {"contract_expiry_type": "EXPIRING", "funding_rate": "0.00001"}},
        {"product_id": "BIT-24APR26-CDE", "display_name": "nano Bitcoin Apr 26", "base_currency_id": "BTC",
         "future_product_details": {"contract_expiry_type": "EXPIRING", "funding_rate": ""}},
        {"product_id": "ETP-20DEC30-CDE", "display_name": "nano Ether Perp", "base_currency_id": "ETH",
         "future_product_details": {"contract_expiry_type": "PERPETUAL"}},
        {"product_id": "BTC-PERP-INTX", "display_name": "BTC PERP", "future_product_details": {"contract_expiry_type": "PERPETUAL"}},
    ]
    assert cdata.parse_coinbase_perp_products(prods) == {"BTC": "BIP-20DEC30-CDE", "ETH": "ETP-20DEC30-CDE"}


def test_live_parsers():
    cb = paper.parse_coinbase_product({"product_id": "BIP-20DEC30-CDE", "price": "100000",
                                       "future_product_details": {"funding_rate": "0.00001", "funding_interval": "3600s",
                                                                  "funding_time": "2026-10-17T15:00:00Z"}})
    assert cb["rate"] == 1e-5 and cb["interval_hours"] == 1.0 and cb["mark"] == 100000 and cb["interval_ts"] > 0
    assert paper.parse_coinbase_product({"future_product_details": {}}) is None
    bn = paper.parse_bitnomial({"funding_rates": [
        {"product_id": "BTCUCZ50", "funding_rate": "0.0001", "interval_end": "2026-10-17T08:00:00Z", "mark_price": "100100"},
        {"product_id": "BTCUCZ50", "funding_rate": "0.0002", "interval_end": "2026-10-17T16:00:00Z", "mark_price": "100200"}]})
    assert bn["rate"] == 0.0002 and bn["mark"] == 100200
    bi = paper.parse_binance([{"symbol": "BTCUSDT", "fundingRate": "0.0001", "fundingTime": 1760000000000, "markPrice": "1"},
                              {"symbol": "BTCUSDT", "fundingRate": "0.0003", "fundingTime": 1760028800000, "markPrice": "2"}])
    assert bi["rate"] == 0.0003 and bi["interval_ts"] == 1760028800.0
    by = paper.parse_bybit({"result": {"list": [{"symbol": "BTCUSDT", "fundingRate": "0.0001", "fundingRateTimestamp": "1760000000000"}]}})
    assert by["rate"] == 0.0001
    ok = paper.parse_okx({"data": [{"instId": "BTC-USDT-SWAP", "fundingRate": "0.0001", "realizedRate": "0.00012", "fundingTime": "1760000000000"}]})
    assert ok["rate"] == 0.00012
    assert paper.parse_okx({"data": []}) is None


# --------------------------------------------------------------------------- paper tick (no network)


def _cfg():
    return {"assets": ["BTC"], "paper": {"sources": {"bitnomial": {}, "binance": {}},
                                        "entries": [{"name": "kraken-BTC", "source": "bitnomial", "asset": "BTC", "fee_venue": "kraken",
                                                     "notional": 1000, "entry_ann": 0.08, "exit_ann": 0.02, "lookback": 3}]}}


def test_paper_tick_state_machine(tmp_path):
    seq = {"bitnomial": [], "binance": []}
    calls = {"n": 0}

    def fake_fetch(source, asset, client, cfg):
        if source == "binance":
            return {"rate": 0.0001, "interval_hours": 8.0, "interval_ts": 1.0, "mark": None, "product_id": "BTCUSDT"}
        k = calls["n"]
        rate = [0.0003, 0.0003, 0.0003, 0.0003, 0.0, 0.0, 0.0][min(k, 6)]
        return {"rate": rate, "interval_hours": 8.0, "interval_ts": 1000.0 + 8 * 3600 * k, "mark": 50_000.0, "product_id": "BTCUCZ50"}

    outs = []
    for k in range(7):
        calls["n"] = k
        outs.append(paper.tick(_cfg(), tmp_path, client=object(), now=2000.0 + k * 3600 * 8, fetch=fake_fetch))
    e = [o["entries"]["kraken-BTC"] for o in outs]
    assert e[0]["signal"] is None and e[1]["signal"] is None
    assert e[2]["signal"] == pytest.approx(annualize(0.0003, 8)) and e[2]["in_pos"]
    assert e[3]["funding_open"] == pytest.approx(0.0003 * 1000)  # one new interval accrued
    # exits when trailing-3 mean drops below 0.02 (k=6: all three zero)
    assert e[5]["in_pos"] and not e[6]["in_pos"]
    led = [json.loads(l) for l in (tmp_path / "paper-kraken-BTC.jsonl").read_text().splitlines()]
    kinds = [r["type"] for r in led]
    assert kinds.count("enter") == 1 and kinds.count("exit") == 1 and kinds.count("funding") == 4  # incl. the exit interval
    assert led[[i for i, r in enumerate(led) if r["type"] == "exit"][0]]["funding_in_trade"] == pytest.approx(0.0003 * 1000)  # k=3 only; k=4..6 print 0
    # live log deduplicates by interval: binance posted the same interval 7 times -> 1 row
    live = [json.loads(l) for l in (tmp_path / "funding-live.jsonl").read_text().splitlines()]
    assert sum(1 for r in live if r["source"] == "binance") == 1
    assert sum(1 for r in live if r["source"] == "bitnomial") == 7
    st = json.loads((tmp_path / "paper-state.json").read_text())
    assert st["kraken-BTC"]["trades"] == 1 and st["kraken-BTC"]["fees"] > 0
    s = paper.summarize(tmp_path)
    assert s["kraken-BTC"]["enters"] == 1 and s["kraken-BTC"]["net"] == pytest.approx(0.0003 * 1000 - s["kraken-BTC"]["costs"])


def test_paper_tick_survives_fetch_errors(tmp_path):
    def bad(source, asset, client, cfg):
        raise RuntimeError("boom")
    out = paper.tick(_cfg(), tmp_path, client=object(), now=1.0, fetch=bad)
    assert out["errors"] and out["entries"]["kraken-BTC"]["signal"] is None
    assert (tmp_path / "paper-state.json").exists()


# --------------------------------------------------------------------------- scripts / config / workflow


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_carry_backtest_cli_synthetic(tmp_path):
    m = _load("carry_backtest")
    rc = m.main(["--synthetic", "--reports-dir", str(tmp_path), "--data-dir", str(tmp_path / "nodata")])
    assert rc == 0
    j = json.loads((tmp_path / "carry_backtest.json").read_text())
    assert set(j["assets"]) == {"BTC", "ETH"}
    names = [r["name"] for r in j["assets"]["BTC"]["rows"]]
    assert names[:2] == ["base", "maker_spot"] and "coinbase_fees" in names and "always_in" in names
    assert j["assets"]["BTC"]["walk_forward"]["oos"]
    md = (tmp_path / "carry_backtest.md").read_text()
    assert "SYNTHETIC" in md and "oos2021" in md
    # no data -> graceful error rows
    rc = m.main(["--reports-dir", str(tmp_path), "--data-dir", str(tmp_path / "nodata"), "--report-name", "x"])
    assert rc == 0 and "error" in json.loads((tmp_path / "x.json").read_text())["assets"]["BTC"]


def test_carry_paper_cli_summary_only(tmp_path):
    m = _load("carry_paper")
    rc = m.main(["--summary", "--data-dir", str(tmp_path / "d"), "--reports-dir", str(tmp_path / "r")])
    assert rc == 0 and (tmp_path / "r" / "carry_paper.md").exists()


def test_config_and_workflow_shape():
    cfg = yaml.safe_load(open(ROOT / "configs/carry.yaml"))
    CarryParams(**cfg["backtest"]["params"])
    for e in cfg["paper"]["entries"]:
        venue_fees(e["fee_venue"], e["asset"])
        assert e["source"] in cfg["paper"]["sources"]
    wf = yaml.safe_load(open(ROOT / ".github/workflows/carry.yml"))
    steps = " ".join(s.get("run", "") for s in wf["jobs"]["carry"]["steps"])
    assert "carry_paper.py" in steps and "carry_backtest.py --download" in steps and "HEAD:data" in steps
    v = yaml.safe_load(open(ROOT / "configs/ventures.yaml"))["ventures"]
    assert any(x["id"] == "crypto_funding_carry" and x["verdict"] == "unproven" for x in v)
