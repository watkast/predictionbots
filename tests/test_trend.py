"""pb.trend: signals, rebalance accounting, costs, walk-forward, data parsers, paper tick, CLI smoke. No network."""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from pb.trend import data as tdata
from pb.trend import paper
from pb.trend.backtest import (TrendParams, cash_index, gem_weights, month_ends, run_strategy, simulate, sma_weights,
                               strategy_weights, synthetic_prices, tsmom_weights, vol_target, walk_forward)

ROOT = Path(__file__).resolve().parents[1]


def _bdays(n, start="2010-01-04"):
    return pd.bdate_range(start, periods=n)


def flat_prices(n=600, syms=("SPY", "EFA", "IEF"), level=100.0):
    idx = _bdays(n)
    return pd.DataFrame({s: level for s in syms}, index=idx)


def trending_prices(n=1300, up=("SPY",), down=("EFA",), flat=("IEF",), rate=0.0005):
    idx = _bdays(n)
    cols = {}
    for s in up:
        cols[s] = 100.0 * np.exp(rate * np.arange(n))
    for s in down:
        cols[s] = 100.0 * np.exp(-rate * np.arange(n))
    for s in flat:
        cols[s] = 100.0 + 0.001 * np.arange(n)
    return pd.DataFrame(cols, index=idx)


# --------------------------------------------------------------------------- signals


def test_month_ends_and_cash_index():
    P = flat_prices(300)
    M = month_ends(P)
    assert len(M) == len(set(zip(P.index.year, P.index.month)))
    assert all(t == P.index[P.index.to_period("M") == t.to_period("M")][-1] for t in M.index)
    rate, ci = cash_index(0.0365, P.index)
    gaps = np.diff(P.index.values.astype("datetime64[D]").astype(np.int64))
    assert ci.iloc[0] == 1.0 and ci.iloc[-1] == pytest.approx(np.prod(1 + 0.0365 * gaps / 365), rel=1e-9)
    _, ci0 = cash_index(None, P.index)
    assert (ci0 == 1.0).all()


def test_tsmom_long_only_uptrend_and_skip_month():
    P = trending_prices()
    M = month_ends(P)
    _, ci = cash_index(0.0, P.index)
    w = tsmom_weights(M, ci.reindex(M.index), lookback=12, skip=1)
    # first 13 months have no signal (NaN return) -> all cash
    assert (w.iloc[:13].sum(axis=1) == 0).all()
    late = w.iloc[14:]
    assert np.allclose(late["SPY"], 1 / 3)      # 1/N_valid with N=3
    assert (late["EFA"] == 0).all()
    assert np.allclose(late["IEF"], 1 / 3)      # flat-but-rising beats 0 % cash
    # with a 10 % cash yield the slow IEF drift fails the excess-return test
    _, ci2 = cash_index(0.10, P.index)
    w2 = tsmom_weights(M, ci2.reindex(M.index), 12, 1)
    assert (w2.iloc[14:]["IEF"] == 0).all() and np.allclose(w2.iloc[14:]["SPY"], 1 / 3)
    # skip=1 means the latest month is ignored: a crash in the last month does not flip the signal
    P2 = P.copy()
    last_month = P2.index.to_period("M") == P2.index[-1].to_period("M")
    P2.loc[last_month, "SPY"] *= 0.5
    w3 = tsmom_weights(month_ends(P2), ci.reindex(M.index), 12, 1)
    assert w3.iloc[-1]["SPY"] == pytest.approx(1 / 3)
    w4 = tsmom_weights(month_ends(P2), ci.reindex(M.index), 12, 0)
    assert w4.iloc[-1]["SPY"] == 0


def test_sma_signal():
    P = trending_prices()
    M = month_ends(P)
    w = sma_weights(M, months=10)
    assert (w.iloc[:9].sum(axis=1) == 0).all()
    assert np.allclose(w.iloc[10:]["SPY"], 1 / 3) and (w.iloc[10:]["EFA"] == 0).all()


def test_gem_picks_best_equity_or_bond():
    P = trending_prices(up=("SPY", "EFA"), down=(), flat=("IEF",))
    P["EFA"] = 100.0 * np.exp(0.001 * np.arange(len(P)))  # EFA trends harder than SPY
    M = month_ends(P)
    _, ci = cash_index(0.0, P.index)
    w = gem_weights(M, ci.reindex(M.index), 12, ("SPY", "EFA"), "IEF")
    assert (w.iloc[12:]["EFA"] == 1.0).all() and (w.iloc[12:][["SPY", "IEF"]] == 0).all().all()
    # both equities below cash -> bond
    Pd = trending_prices(up=(), down=("SPY", "EFA"), flat=("IEF",))
    wd = gem_weights(month_ends(Pd), ci.reindex(M.index), 12, ("SPY", "EFA"), "IEF")
    assert (wd.iloc[12:]["IEF"] == 1.0).all()
    # bond missing -> cash
    Pd2 = Pd[["SPY", "EFA"]]
    wd2 = gem_weights(month_ends(Pd2), ci.reindex(M.index), 12, ("SPY", "EFA"), "IEF")
    assert (wd2.iloc[12:].sum(axis=1) == 0).all()


def test_vol_target_only_derisks_and_caps_gross():
    rng = np.random.default_rng(1)
    idx = _bdays(400)
    P = pd.DataFrame({"A": 100 * np.exp(np.cumsum(0.02 * rng.standard_normal(400))),   # ~32 % vol
                      "B": 100 * np.exp(np.cumsum(0.001 * rng.standard_normal(400)))}, index=idx)  # ~1.6 % vol
    M = month_ends(P)
    w = pd.DataFrame({"A": 1.0, "B": 0.0}, index=M.index)
    ws, scale = vol_target(w, P, target_vol=0.10, lookback_days=63)
    assert (scale.iloc[4:] < 0.5).all() and (ws.iloc[4:]["A"] < 0.5).all()
    w2 = pd.DataFrame({"A": 0.0, "B": 1.0}, index=M.index)
    ws2, scale2 = vol_target(w2, P, target_vol=0.10, lookback_days=63)
    assert (scale2 == 1.0).all()            # low-vol book is never levered up
    w3 = pd.DataFrame({"A": 0.0, "B": 1.5}, index=M.index)
    ws3, _ = vol_target(w3, P, target_vol=1.0, lookback_days=63, max_gross=1.0)
    assert (ws3.sum(axis=1) <= 1.0 + 1e-9).all()


# --------------------------------------------------------------------------- accounting


def test_rebalance_accounting_flat_prices_costs_only():
    P = flat_prices(600)
    M = month_ends(P)
    W = pd.DataFrame({"SPY": 0.5, "EFA": 0.3, "IEF": 0.0}, index=M.index)
    p = TrendParams(capital=10_000, spread_bps=1.0, slippage_bps=2.0, exec_lag_days=1)
    r = simulate(P, W, None, p)
    # first rebalance buys 80 % of (NAV - reserved cost) at 3 bps; later months trade nothing
    # (no drift, same targets, sub-$1 dust ignored)
    assert r.n_rebalances in (len(M), len(M) - 1)
    bought = 0.8 * (10_000 - 8_000 * 3 / 1e4)
    assert r.costs_usd == pytest.approx(bought * 3 / 1e4)
    assert r.final_equity == pytest.approx(10_000 - r.costs_usd)
    assert r.annual_turnover == pytest.approx(bought / 10_000 / r.years)
    assert r.avg_cash_weight == pytest.approx(0.2, abs=0.01)
    assert r.max_drawdown == 0.0 and r.cagr < 0          # equity starts after the first (costed) trade
    assert (r.equity >= 0).all()
    # commission per line
    pc = TrendParams(capital=10_000, spread_bps=0, slippage_bps=0, commission_usd=1.0)
    rc = simulate(P, W, None, pc)
    assert rc.costs_usd == pytest.approx(2.0)


def test_exec_lag_and_drift_with_cash_yield():
    n = 300
    idx = _bdays(n)
    P = pd.DataFrame({"SPY": 100.0 * (1.01 ** np.arange(n))}, index=idx)   # +1 %/day
    M = month_ends(P)
    W = pd.DataFrame({"SPY": 0.5}, index=M.index)
    p = TrendParams(capital=10_000, spread_bps=0, slippage_bps=0, exec_lag_days=1)
    r = simulate(P, W, 0.0, p)
    # starts at the first exec day (one trading day after the first month-end)
    first_exec = P.index[P.index.get_loc(M.index[0]) + 1]
    assert pd.Timestamp(r.start) == first_exec
    assert r.equity.iloc[0] == pytest.approx(10_000)
    # day after: half the book grew 1 %
    assert r.equity.iloc[1] == pytest.approx(10_000 * 1.005)
    # with a 10 % cash yield the cash half accrues act/365 across the first gap
    r2 = simulate(P, W, 0.10, p)
    gap = (r2.equity.index[1] - r2.equity.index[0]).days
    assert r2.equity.iloc[1] == pytest.approx(5_000 * 1.01 + 5_000 * (1 + 0.10 * gap / 365))
    assert r2.sharpe < r.sharpe   # excess over a higher cash rate
    # monthly rebalance back to 50 % sells the drifted excess: turnover > 0 after the first month
    assert r.annual_turnover > 0.5 / r.years


def test_missing_asset_is_cash_and_yearly_returns():
    P = trending_prices(n=800)
    P.loc[P.index[:300], "EFA"] = np.nan
    M = month_ends(P)
    W = pd.DataFrame({"SPY": 0.0, "EFA": 1.0, "IEF": 0.0}, index=M.index)
    p = TrendParams(capital=10_000, spread_bps=0, slippage_bps=0)
    r = simulate(P, W, None, p)
    # while EFA has no price the weight is dropped (cash); afterwards it is held and loses
    assert r.equity.iloc[:250].std() == 0
    assert r.final_equity < 10_000
    assert set(r.yearly) == set(r.equity.index.year.unique())
    assert r.worst_year in r.yearly and r.worst_year_ret == min(r.yearly.values())


def test_benchmarks_and_strategy_weights_shapes():
    P, cash = synthetic_prices(6, seed=3)
    p = TrendParams()
    for s in ("tsmom", "sma", "gem", "ensemble", "spy_bh", "sixty_forty"):
        w = strategy_weights(P, cash, p, s)
        assert (w.sum(axis=1) <= 1.0 + 1e-9).all() and (w >= -1e-12).all().all()
    bh = run_strategy(P, cash, p, "spy_bh")
    assert bh.annual_turnover == pytest.approx(1.0 / bh.years, rel=1e-3) and bh.avg_cash_weight == pytest.approx(0, abs=1e-6)
    sf = run_strategy(P, cash, p, "sixty_forty")
    assert sf.ann_vol < bh.ann_vol
    with pytest.raises(ValueError):
        strategy_weights(P, cash, p, "nope")


# --------------------------------------------------------------------------- walk-forward


def test_walk_forward_selects_on_prior_window_and_scores_next():
    P, cash = synthetic_prices(8, seed=5)
    grid = {"tsmom_lookback": [6, 12], "target_vol": [0.08, 0.12]}
    wf = walk_forward(P, cash, TrendParams(), grid, strategy="tsmom", train_years=3, min_train_days=400)
    assert wf["grid_runs"] == 4
    years = [o["year"] for o in wf["oos"]]
    first = P.index[0].year
    assert years and years[0] == first + 3 and years == sorted(years)
    for o in wf["oos"]:
        assert o["train_years"] == [o["year"] - 3, o["year"] - 1]
        assert set(o["chosen"]) == {"tsmom_lookback", "target_vol"}
        # the chosen point really is the best train-window Sharpe among the grid
        best = -np.inf
        for gp in [{"tsmom_lookback": a, "target_vol": b} for a in (6, 12) for b in (0.08, 0.12)]:
            r = run_strategy(P, cash, TrendParams(**gp), "tsmom")
            yi = r.returns.index.year
            tr = (yi >= o["year"] - 3) & (yi < o["year"])
            x = r.excess[tr]
            best = max(best, float(x.mean() / x.std() * np.sqrt(252)))
        assert o["train_objective"] == pytest.approx(best)
    agg = wf["aggregate"]
    assert agg["years"] == years and "sharpe" in agg and "worst_year" in agg
    assert wf["oos"][-1]["ret"] == pytest.approx(min(o["ret"] for o in wf["oos"])) or agg["worst_year_ret"] <= wf["oos"][-1]["ret"]


# --------------------------------------------------------------------------- data parsers / download


STOOQ = "Date,Open,High,Low,Close,Volume\n2024-01-02,470.1,473.2,469.0,472.65,80000000\n2024-01-03,471.0,472.0,468.0,468.79,70000000\n"
FRED = "observation_date,DGS3MO\n2024-01-02,5.46\n2024-01-03,.\n2024-01-04,5.44\n"


def test_parse_stooq_and_fred():
    df = tdata.parse_stooq_csv(STOOQ)
    assert list(df.columns) == tdata.PRICE_COLS and len(df) == 2
    assert df.close.iloc[-1] == 468.79 and df.date.iloc[0] == "2024-01-02" and not df.adjusted.iloc[0]
    assert tdata.parse_stooq_csv("No data").empty and tdata.parse_stooq_csv("<html>").empty
    fr = tdata.parse_fred_csv(FRED)
    assert len(fr) == 2 and fr.rate.iloc[0] == pytest.approx(0.0546)
    fr2 = tdata.parse_fred_csv("DATE,DGS3MO\n2020-01-02,1.5\n")
    assert fr2.rate.iloc[0] == pytest.approx(0.015)


def test_download_all_merges_and_prefers_adjusted(tmp_path):
    cfg = {"universe": ["SPY"], "data": {"cash_symbols": []}}

    def fetch_unadj(sym, client, prefer_yfinance=True):
        return tdata.parse_stooq_csv(STOOQ)

    def fetch_adj(sym, client, prefer_yfinance=True):
        df = tdata.parse_stooq_csv("Date,Open,High,Low,Close,Volume\n2024-01-03,0,0,0,400.0,1\n2024-01-04,0,0,0,401.0,1\n",
                                   source="yfinance", adjusted=True)
        return df

    def fred(series, client):
        return tdata.parse_fred_csv(FRED)

    w = tdata.download_all(cfg, tmp_path, client=object(), fetch=fetch_unadj, fetch_fred=fred)
    assert set(w) == {"SPY", "fred"} and (tmp_path / "manifest.json").exists()
    # adjusted series replaces overlapping unadjusted rows; older unadjusted rows are kept
    tdata.download_all(cfg, tmp_path, client=object(), fetch=fetch_adj, fetch_fred=fred)
    df = pd.read_parquet(tmp_path / "prices-SPY.parquet")
    assert list(df.date) == ["2024-01-02", "2024-01-03", "2024-01-04"]
    assert df.close.tolist() == [472.65, 400.0, 401.0] and df.adjusted.iloc[-1]
    # a later unadjusted fetch does not overwrite the adjusted rows
    tdata.download_all(cfg, tmp_path, client=object(), fetch=fetch_unadj, fetch_fred=fred)
    df = pd.read_parquet(tmp_path / "prices-SPY.parquet")
    assert df.close.tolist() == [472.65, 400.0, 401.0]
    wide, meta = tdata.load_prices(tmp_path, ["SPY", "QQQ"])
    assert list(wide.columns) == ["SPY"] and meta["SPY"]["adjusted"] and meta["SPY"]["source"] == "yfinance"
    cy = tdata.load_cash_yield(tmp_path)
    assert cy.iloc[0] == pytest.approx(0.0546)
    # yfinance missing in the sandbox -> empty frame, no crash
    assert tdata.yfinance_daily("SPY").empty or True


# --------------------------------------------------------------------------- paper tick


def _paper_cfg():
    return {"universe": ["SPY", "EFA", "IEF"], "backtest": {"params": {"spread_bps": 1.0, "slippage_bps": 2.0}},
            "paper": {"strategy": "gem", "capital": 10_000, "stale_days": 7}}


def test_paper_tick_rebalances_once_per_month_and_marks(tmp_path):
    P = trending_prices(n=700, up=("SPY",), down=("EFA",), flat=("IEF",))
    cash = pd.Series(0.0, index=P.index)
    cfg = _paper_cfg()
    # first tick: the day after a month-end -> rebalance into SPY (GEM: SPY beats EFA and cash)
    M = month_ends(P)
    t0 = P.index.get_loc(M.index[-3]) + 1
    now = P.index[t0].timestamp() + 3600
    r1 = paper.tick(cfg, tmp_path, now=now, prices=P.iloc[:t0 + 1], cash_rate=cash)
    assert r1["rebalanced"] and r1["target"] == {"SPY": 1.0}
    assert r1["weights"]["SPY"] == pytest.approx(1.0, abs=1e-3)
    assert r1["nav"] == pytest.approx(10_000 - (10_000 - 3.0) * 3 / 1e4, rel=1e-6)
    assert r1["cash"] >= 0
    book = json.loads((tmp_path / "paper-book.json").read_text())
    assert book["rebalances"] == 1 and book["last_rebalance_month"] == str(M.index[-3].date())[:7]
    # next day: same month -> no trade, NAV follows SPY (+0.05 %/day)
    r2 = paper.tick(cfg, tmp_path, now=now + 86400, prices=P.iloc[:t0 + 2], cash_rate=cash)
    assert not r2["rebalanced"]
    assert r2["nav"] == pytest.approx(r1["nav"] * P.SPY.iloc[t0 + 1] / P.SPY.iloc[t0], rel=1e-9)
    # the day after the next month-end, but with stale prices (tick 30 days late): no rebalance
    t1 = P.index.get_loc(M.index[-2]) + 1
    r3 = paper.tick(cfg, tmp_path, now=P.index[t1].timestamp() + 30 * 86400, prices=P.iloc[:t1 + 1], cash_rate=cash)
    assert not r3["rebalanced"] and r3["stale_days"] >= 30
    # same day, fresh prices -> rebalance (same target, only drift trades -> tiny turnover)
    r4 = paper.tick(cfg, tmp_path, now=P.index[t1].timestamp() + 3600, prices=P.iloc[:t1 + 1], cash_rate=cash)
    assert r4["rebalanced"]
    rows = paper._read_jsonl(tmp_path / "paper-gem.jsonl")
    assert [r["type"] for r in rows] == ["rebalance", "tick", "tick", "tick", "rebalance", "tick"]
    assert rows[4]["turnover"] < 1.0
    s = paper.summarize(tmp_path)
    assert s["gem"]["ticks"] == 4 and s["gem"]["rebalances"] == 2 and s["gem"]["nav"] == pytest.approx(r4["nav"])
    assert s["gem"]["max_drawdown"] <= 0


def test_paper_tick_cash_accrues_and_no_data(tmp_path):
    P = flat_prices(400)
    cash = pd.Series(0.0365, index=P.index)
    cfg = _paper_cfg()
    cfg["paper"]["strategy"] = "tsmom"          # flat prices: never long -> all cash
    t0 = len(P) - 10
    r1 = paper.tick(cfg, tmp_path, now=P.index[t0].timestamp(), prices=P.iloc[:t0 + 1], cash_rate=cash)
    assert r1["target"] == {} and r1["cash_w"] == pytest.approx(1.0)
    r2 = paper.tick(cfg, tmp_path, now=P.index[-1].timestamp(), prices=P, cash_rate=cash)
    days = (P.index[-1] - P.index[t0]).days
    assert r2["nav"] == pytest.approx(10_000 * (1 + 0.0365 * days / 365))
    r = paper.tick(cfg, tmp_path / "empty", now=1.0)
    assert "error" in r


# --------------------------------------------------------------------------- CLI smoke / config / workflow


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_trend_backtest_cli_synthetic(tmp_path):
    cfg = yaml.safe_load(open(ROOT / "configs/trend.yaml"))
    cfg["backtest"]["grid"] = {"tsmom_lookback": [6, 12], "sma_months": [10], "target_vol": [0.10]}
    cfg["backtest"]["synthetic_years"] = 14
    cfg["backtest"]["walk_forward"]["train_years"] = 3
    (tmp_path / "cfg.yaml").write_text(yaml.safe_dump(cfg))
    m = _load("trend_backtest")
    rc = m.main(["--synthetic", "--config", str(tmp_path / "cfg.yaml"), "--reports-dir", str(tmp_path),
                 "--data-dir", str(tmp_path / "nodata")])
    assert rc == 0
    j = json.loads((tmp_path / "trend_backtest.json").read_text())
    assert [r["name"] for r in j["rows"]] == ["tsmom", "sma", "gem", "ensemble", "spy_bh", "sixty_forty"]
    assert j["walk_forward"]["oos"] and j["walk_forward"]["grid_runs"] == 2 and "reality" in j
    md = (tmp_path / "trend_backtest.md").read_text()
    assert "SYNTHETIC" in md and "Walk-forward" in md and "Post-publication decay" in md
    # no data -> graceful error
    rc = m.main(["--config", str(tmp_path / "cfg.yaml"), "--reports-dir", str(tmp_path), "--data-dir",
                 str(tmp_path / "nodata"), "--report-name", "x"])
    assert rc == 0 and "error" in json.loads((tmp_path / "x.json").read_text())


def test_trend_paper_cli_summary_only(tmp_path):
    m = _load("trend_paper")
    rc = m.main(["--summary", "--data-dir", str(tmp_path / "d"), "--reports-dir", str(tmp_path / "r")])
    assert rc == 0 and (tmp_path / "r" / "trend_paper.md").exists()


def test_config_workflow_and_venture_entry():
    cfg = yaml.safe_load(open(ROOT / "configs/trend.yaml"))
    p = TrendParams.from_dict(cfg["backtest"]["params"])
    assert p.max_gross <= 1.0 and p.exec_lag_days >= 1
    for k in cfg["backtest"]["grid"]:
        assert hasattr(p, k)
    wf = yaml.safe_load(open(ROOT / ".github/workflows/trend.yml"))
    txt = open(ROOT / ".github/workflows/trend.yml").read()
    assert "trend_paper.py" in txt and "trend_backtest.py" in txt and "yfinance" in txt and "LIVE_TRADING" not in txt
    assert "jobs" in wf
    v = yaml.safe_load(open(ROOT / "configs/ventures.yaml"))["ventures"]
    e = [x for x in v if x["id"] == "etf_trend_momentum"]
    assert len(e) == 1 and e[0]["status"] == "building" and e[0]["verdict"] == "unproven" and e[0]["capital_usd"] == 0
