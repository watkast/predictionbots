#!/usr/bin/env python
"""Carry backtest CLI -> reports/carry_backtest.md|json.

    python scripts/carry_backtest.py --download          # on Actions: fetch data/carry/*.parquet first
    python scripts/carry_backtest.py                     # backtest from data/carry
    python scripts/carry_backtest.py --synthetic         # CI smoke, no network

Reads configs/carry.yaml (``backtest:`` section). Full-period rows for the base
params and each ``variants`` entry, then walk-forward out-of-sample rows per
year (``oos<year>``) chosen from ``grid`` on the previous year.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pb.carry import data as cdata  # noqa: E402
from pb.carry.backtest import CarryParams, align, run_backtest, synthetic_dataset, walk_forward  # noqa: E402
from pb.carry.venues import venue_fees  # noqa: E402


def _fmt_ts(t: float) -> str:
    return datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%d")


def load_aligned(data_dir: Path, asset: str, source: str) -> "pd.DataFrame | None":  # noqa: F821
    fp = data_dir / f"funding-{source}-{asset}.parquet"
    sp = data_dir / f"candles-binance-spot-{asset}.parquet"
    pp = data_dir / f"candles-binance-um-{asset}.parquet"
    if not (fp.exists() and sp.exists() and pp.exists()):
        return None
    return align(cdata.load_funding(fp), cdata.load_candles(sp), cdata.load_candles(pp))


def run(cfg: dict, data_dir: Path, synthetic: bool = False) -> dict:
    bt = cfg.get("backtest", {})
    base = CarryParams(**bt.get("params", {}))
    grid = bt.get("grid", {"entry_ann": [0.05, 0.08, 0.12], "exit_ann": [0.0, 0.02]})
    out: dict = {"generated_at": datetime.now(timezone.utc).isoformat(), "synthetic": synthetic, "assets": {}}
    for asset in [a.upper() for a in cfg.get("assets", ["BTC", "ETH"])]:
        if synthetic:
            df = synthetic_dataset(n=3 * 365 * 3, seed=hash(asset) % 1000)
        else:
            df = load_aligned(data_dir, asset, bt.get("funding_source", "binance"))
            if df is None or len(df) < 10:
                out["assets"][asset] = {"error": f"no data under {data_dir} for {asset}"}
                continue
        rows = []
        variants = [{"name": "base"}] + list(bt.get("variants", []))
        for v in variants:
            v = dict(v)
            name = v.pop("name")
            venue = v.pop("venue", bt.get("venue", "kraken"))
            fees = venue_fees(venue, asset, bt.get("fee_overrides"))
            p = CarryParams(**{**asdict(base), **v})
            r = run_backtest(df, p, fees)
            s = r.summary()
            s.pop("trades", None)
            rows.append({"name": name, **s})
        fees = venue_fees(bt.get("venue", "kraken"), asset, bt.get("fee_overrides"))
        wf = walk_forward(df, base, grid, fees)
        out["assets"][asset] = {"rows": rows, "walk_forward": wf, "n_intervals": int(len(df)),
                                "start": _fmt_ts(float(df.ts.iloc[0])), "end": _fmt_ts(float(df.ts.iloc[-1]))}
    return out


def to_markdown(res: dict) -> str:
    L = ["# Carry backtest (long spot + short perp)", "",
         f"generated {res['generated_at']}  synthetic={res['synthetic']}", "",
         "Funding/candles are **Binance proxies** for the US perps (Coinbase `BIP-20DEC30-CDE`, "
         "Kraken Derivatives US `PBTCUC`); fees from `pb/carry/venues.py`. "
         "`oos<year>` rows pick thresholds on the prior year and score the named year; they are the ones that count.", ""]
    if res["synthetic"]:
        L.append("**SYNTHETIC DATA — CI smoke only, numbers are meaningless.**\n")
    cols = ["name", "annualized_net", "excess_over_tbill_ann", "cagr", "max_drawdown_frac", "funding_captured", "costs",
            "basis_pnl", "idle_yield", "time_in_market", "n_trades", "liquidations", "worst_basis_shock_bps",
            "mean_ann_funding", "frac_intervals_positive"]
    hdr = "| " + " | ".join(cols) + " |"
    sep = "|" + "---|" * len(cols)

    def row(r: dict) -> str:
        cells = []
        for c in cols:
            v = r.get(c)
            if isinstance(v, float):
                cells.append(f"{v:.4f}" if abs(v) < 10 else f"{v:,.0f}")
            else:
                cells.append(str(v))
        return "| " + " | ".join(cells) + " |"

    for asset, a in res["assets"].items():
        L.append(f"## {asset}")
        if "error" in a:
            L += [a["error"], ""]
            continue
        L.append(f"{a['n_intervals']} funding intervals, {a['start']} .. {a['end']}\n")
        L += [hdr, sep] + [row(r) for r in a["rows"]]
        wf = a["walk_forward"]
        for o in wf.get("oos", []):
            L.append(row({**o, "name": f"oos{o['year']} {o['chosen']}"}))
        agg = wf.get("aggregate") or {}
        if agg:
            L.append("")
            L.append(f"walk-forward aggregate: annualized net {agg['annualized_net']:.4f}, "
                     f"max DD {agg['max_drawdown_frac']:.4f}, time in market {agg['time_in_market']:.2f}, "
                     f"liquidations {agg['liquidations']}, years {agg['years']}")
        L.append("")
    L += ["## Reading this", "",
          "* `annualized_net` is net of fees, slippage, basis drift and liquidation penalties and **includes** T-bill yield on idle cash; "
          "`excess_over_tbill_ann` subtracts an all-cash T-bill benchmark — that is the number the venture must beat.",
          "* `always_in` is the no-threshold control; `coinbase_fees` shows what Coinbase Advanced spot tiers do to a small account.",
          "* `worst_basis_shock_bps` is the worst single-interval perp-premium move against the position while held.",
          "* Liquidations > 0 means the 50 % perp collateral (plus idle top-up) was not enough for a rally; raise collateral or cut leverage.", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=str(ROOT / "configs/carry.yaml"))
    ap.add_argument("--data-dir", default=str(ROOT / "data/carry"))
    ap.add_argument("--download", action="store_true", help="download/refresh data first (needs internet)")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--report-name", default="carry_backtest")
    ap.add_argument("--reports-dir", default=str(ROOT / "reports"))
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    cfg = yaml.safe_load(open(args.config))
    data_dir = Path(args.data_dir)
    if args.download:
        cdata.download_all(cfg, data_dir)
    res = run(cfg, data_dir, synthetic=args.synthetic)
    rd = Path(args.reports_dir)
    rd.mkdir(parents=True, exist_ok=True)
    (rd / f"{args.report_name}.json").write_text(json.dumps(res, indent=1, default=float))
    (rd / f"{args.report_name}.md").write_text(to_markdown(res))
    print(to_markdown(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
