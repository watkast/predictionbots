#!/usr/bin/env python
"""Daily trend paper tick (GitHub Actions, after the US close): mark the paper
book at the latest close, rebalance to the strategy's month-end targets when a
new month-end has arrived, append to data/trend/paper-*.jsonl. No orders.

    python scripts/trend_paper.py --download      # refresh prices, then one tick (needs internet)
    python scripts/trend_paper.py                 # one tick from the cached parquet
    python scripts/trend_paper.py --summary       # roll ledgers up -> reports/trend_paper.md|json
    python scripts/trend_paper.py --force         # rebalance now even inside the month

Strategy and params come from configs/trend.yaml (``paper:`` / ``backtest.params``).
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
from pb.trend import paper  # noqa: E402


def summary_markdown(s: dict) -> str:
    L = ["# Trend paper book (signals only, no orders)", "",
         f"generated {datetime.now(timezone.utc).isoformat()}", "",
         "| strategy | ticks | rebalances | NAV $ | pnl $ | costs $ | max DD | drift | price date | stale days | since |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, r in s.items():
        nav = f"{r['nav']:.2f}" if isinstance(r.get("nav"), (int, float)) else "-"
        pnl = f"{r['pnl']:.2f}" if isinstance(r.get("pnl"), (int, float)) else "-"
        drift = f"{r['last_drift']:.3f}" if isinstance(r.get("last_drift"), (int, float)) else "-"
        L.append(f"| {name} | {r['ticks']} | {r['rebalances']} | {nav} | {pnl} | {r['costs']:.2f} | {r['max_drawdown']:.4f} | "
                 f"{drift} | {r['last']} | {r['stale_days']} | {r['first']} |")
    for name, r in s.items():
        if r.get("last_weights") or r.get("last_target"):
            L += ["", f"## {name}: current vs target weights", "", "| symbol | held | target |", "|---|---|---|"]
            syms = sorted(set(r.get("last_weights", {})) | set(r.get("last_target", {})))
            for sym in syms:
                L.append(f"| {sym} | {r['last_weights'].get(sym, 0.0):.3f} | {r['last_target'].get(sym, 0.0):.3f} |")
            srcs = r.get("sources") or {}
            if srcs:
                L.append(f"\nprice sources: {', '.join(f'{k}={v}' for k, v in sorted(srcs.items()))}")
    L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=str(ROOT / "configs/trend.yaml"))
    ap.add_argument("--data-dir", default=str(ROOT / "data/trend"))
    ap.add_argument("--reports-dir", default=str(ROOT / "reports"))
    ap.add_argument("--download", action="store_true", help="refresh prices first (needs internet)")
    ap.add_argument("--summary", action="store_true", help="only write reports/trend_paper.md|json")
    ap.add_argument("--force", action="store_true", help="rebalance on this tick regardless of month")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    cfg = yaml.safe_load(open(args.config))
    data_dir = Path(args.data_dir)
    if args.download:
        tdata.download_all(cfg, data_dir)
    if not args.summary:
        res = paper.tick(cfg, data_dir, force_rebalance=args.force)
        print(json.dumps(res, indent=1, default=float))
    s = paper.summarize(data_dir)
    rd = Path(args.reports_dir)
    rd.mkdir(parents=True, exist_ok=True)
    (rd / "trend_paper.json").write_text(json.dumps({"entries": s}, indent=1, default=float))
    (rd / "trend_paper.md").write_text(summary_markdown(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
