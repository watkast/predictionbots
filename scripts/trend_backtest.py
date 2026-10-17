#!/usr/bin/env python
"""Trend backtest CLI -> reports/trend_backtest.md|json.

    python scripts/trend_backtest.py --download          # on Actions: fetch data/trend/*.parquet first
    python scripts/trend_backtest.py                     # backtest from data/trend
    python scripts/trend_backtest.py --synthetic         # CI smoke, no network

Reads configs/trend.yaml (``backtest:`` section). Full-period rows for every
strategy (tsmom, sma, gem, ensemble) and benchmark (spy_bh, sixty_forty), then
walk-forward out-of-sample rows per year (``oos<year>``) chosen from ``grid`` on
the prior ``train_years``.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pb.trend import data as tdata  # noqa: E402
from pb.trend.backtest import BENCHMARKS, STRATEGIES, TrendParams, run_strategy, synthetic_prices, walk_forward  # noqa: E402


def run(cfg: dict, data_dir: Path, synthetic: bool = False) -> dict:
    bt = cfg.get("backtest", {})
    base = TrendParams.from_dict(bt.get("params", {}))
    grid = bt.get("grid", {"tsmom_lookback": [6, 12], "sma_months": [10], "target_vol": [0.10]})
    wf_cfg = bt.get("walk_forward", {})
    universe = list(cfg.get("universe", tdata.UNIVERSE))
    out: dict = {"generated_at": datetime.now(timezone.utc).isoformat(), "synthetic": synthetic,
                 "universe": universe, "params": base.__dict__ | {"gem_equity": list(base.gem_equity)}}
    meta: dict = {}
    if synthetic:
        prices, cash = synthetic_prices(int(bt.get("synthetic_years", 30)), seed=0, symbols=[*universe, "SHY"])
        prices = prices[universe]
        meta = {s: {"source": "synthetic", "adjusted": True, "first": str(prices[s].first_valid_index().date())}
                for s in universe}
    else:
        prices, meta = tdata.load_prices(data_dir, universe)
        cash = tdata.load_cash_yield(data_dir, cfg.get("data", {}).get("fred_series", "DGS3MO"))
        if prices.empty or "SPY" not in prices.columns or len(prices) < 300:
            out["error"] = f"no price data under {data_dir}"
            return out
        prices = prices.dropna(how="all")
    out["data"] = {"start": str(prices.index[0].date()), "end": str(prices.index[-1].date()), "days": int(len(prices)),
                   "cash_yield": "fred" if cash is not None else "none (0 %)", "symbols": meta}
    rows = []
    for s in [*STRATEGIES, *BENCHMARKS]:
        try:
            r = run_strategy(prices, cash, base, s)
            rows.append(r.summary())
        except ValueError as e:
            rows.append({"name": s, "error": str(e)})
    out["rows"] = rows
    out["walk_forward"] = walk_forward(prices, cash, base, grid, strategy=wf_cfg.get("strategy", "ensemble"),
                                       train_years=int(wf_cfg.get("train_years", 10)),
                                       objective=wf_cfg.get("objective", "sharpe"))
    hc = float(bt.get("decay_haircut", 0.5))
    agg = out["walk_forward"].get("aggregate") or {}
    if agg:
        out["reality"] = {"decay_haircut": hc, "oos_sharpe": agg["sharpe"], "oos_sharpe_haircut": agg["sharpe"] * hc,
                          "oos_cagr": agg["cagr"], "oos_excess_cagr_haircut_approx": (agg["cagr"] - _cash_mean(cash)) * hc,
                          "cash_mean": _cash_mean(cash)}
    return out


def _cash_mean(cash) -> float:
    if cash is None:
        return 0.0
    try:
        return float(cash.mean())
    except Exception:  # noqa: BLE001
        return float(cash)


def to_markdown(res: dict) -> str:
    L = ["# Trend / momentum backtest (monthly ETF, overnight holds only)", "",
         f"generated {res['generated_at']}  synthetic={res['synthetic']}", ""]
    if res["synthetic"]:
        L.append("**SYNTHETIC DATA — CI smoke only, numbers are meaningless.**\n")
    if "error" in res:
        L += [res["error"], ""]
        return "\n".join(L)
    d = res["data"]
    L.append(f"Daily closes {d['start']} .. {d['end']} ({d['days']} days); cash sleeve earns {d['cash_yield']}. "
             "Costs: 1 bp spread + 2 bp slippage per trade, zero commission; signal at month-end close, executed next close.\n")
    L += ["| symbol | first date | source | dividend-adjusted |", "|---|---|---|---|"]
    for s, m in d["symbols"].items():
        L.append(f"| {s} | {m.get('first')} | {m.get('source')} | {m.get('adjusted')} |")
    L.append("")
    cols = ["name", "cagr", "ann_vol", "sharpe", "max_drawdown", "worst_year", "worst_year_ret", "annual_turnover",
            "cost_drag_ann", "avg_cash_weight", "start", "end"]
    L += ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]

    def row(r: dict) -> str:
        cells = []
        for c in cols:
            v = r.get(c)
            cells.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        return "| " + " | ".join(cells) + " |"

    for r in res["rows"]:
        L.append(row(r) if "error" not in r else f"| {r['name']} | error: {r['error']} |")
    wf = res.get("walk_forward", {})
    if wf.get("oos"):
        L += ["", f"## Walk-forward (ensemble; {wf['grid_runs']} grid points, chosen on the prior train window by Sharpe)", "",
              "| year | train | chosen | train Sharpe | OOS return | OOS Sharpe | OOS max DD |", "|---|---|---|---|---|---|---|"]
        for o in wf["oos"]:
            L.append(f"| {o['year']} | {o['train_years'][0]}-{o['train_years'][1]} | {o['chosen']} | {o['train_objective']:.2f} | "
                     f"{o['ret']:.4f} | {o['sharpe']:.2f} | {o['max_drawdown']:.4f} |")
        a = wf["aggregate"]
        L += ["", f"OOS chained: CAGR {a['cagr']:.4f}, vol {a['ann_vol']:.4f}, Sharpe {a['sharpe']:.2f}, max DD {a['max_drawdown']:.4f}, "
              f"worst year {a['worst_year']} ({a['worst_year_ret']:.4f}), {a['frac_years_positive']:.0%} of years positive, years {a['years'][0]}-{a['years'][-1]}"]
    else:
        L += ["", "Walk-forward: not enough history for a train window yet."]
    rl = res.get("reality")
    if rl:
        L += ["", "## Reality", "",
              f"* Post-publication decay: published trend/momentum Sharpe roughly halves out of sample "
              f"(McLean & Pontiff; arxiv 2105.01380). OOS Sharpe {rl['oos_sharpe']:.2f} -> expect ~{rl['oos_sharpe_haircut']:.2f}; "
              f"OOS CAGR {rl['oos_cagr']:.4f} vs mean cash yield {rl['cash_mean']:.4f} -> haircut excess ~{rl['oos_excess_cagr_haircut_approx']:.4f}/yr.",
              "* On a $10k account that excess is tens to a few hundred dollars a year; the drawdowns are not haircut."]
    L += ["", "## Reading this", "",
          "* `oos<year>` rows and the chained OOS line are the only numbers that count; full-period rows use fixed params.",
          "* Compare the ensemble against `spy_bh` and `sixty_forty` on Sharpe and max DD, not CAGR: trend is a drawdown-control trade.",
          "* Stooq closes are split- but not dividend-adjusted (`dividend-adjusted=False`): total returns and the momentum ranking of TLT/IEF/VNQ/SPY are biased down; yfinance rows are total-return.",
          "* The full ETF universe exists only from 2006 (DBC); earlier years run on whatever ETFs existed, so the 10-year-train walk-forward starts in 2016 on real data.",
          "* Turnover is one-way per year as a fraction of NAV; cost drag is what 3 bps per trade costs at that turnover.", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=str(ROOT / "configs/trend.yaml"))
    ap.add_argument("--data-dir", default=str(ROOT / "data/trend"))
    ap.add_argument("--download", action="store_true", help="download/refresh data first (needs internet)")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--report-name", default="trend_backtest")
    ap.add_argument("--reports-dir", default=str(ROOT / "reports"))
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    cfg = yaml.safe_load(open(args.config))
    data_dir = Path(args.data_dir)
    if args.download:
        tdata.download_all(cfg, data_dir)
    res = run(cfg, data_dir, synthetic=args.synthetic)
    rd = Path(args.reports_dir)
    rd.mkdir(parents=True, exist_ok=True)
    (rd / f"{args.report_name}.json").write_text(json.dumps(res, indent=1, default=str))
    (rd / f"{args.report_name}.md").write_text(to_markdown(res))
    print(to_markdown(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
