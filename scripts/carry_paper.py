#!/usr/bin/env python
"""Hourly carry paper tick (GitHub Actions): poll live funding rates, apply the
backtest's entry/exit rules, append to data/carry/paper-*.jsonl. No orders.

    python scripts/carry_paper.py                 # one tick (needs internet)
    python scripts/carry_paper.py --summary       # roll ledgers up -> reports/carry_paper.md|json

Sources and entries come from configs/carry.yaml (``paper:``).
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

from pb.carry import paper  # noqa: E402


def summary_markdown(s: dict, live_rows: list[dict]) -> str:
    L = ["# Carry paper ledger (signals only, no orders)", "",
         f"generated {datetime.now(timezone.utc).isoformat()}", "",
         "| entry | ticks | enters | exits | in-pos share | funding $ | costs $ | net $ | last signal (ann) | since |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for name, r in s.items():
        since = datetime.fromtimestamp(r["first_ts"], tz=timezone.utc).strftime("%Y-%m-%d") if r["first_ts"] else "-"
        sig = f"{r['last_signal']:.3f}" if isinstance(r.get("last_signal"), (int, float)) else "-"
        L.append(f"| {name} | {r['ticks']} | {r['enters']} | {r['exits']} | {r['in_pos_frac']:.2f} | {r['funding']:.2f} | "
                 f"{r['costs']:.2f} | {r['net']:.2f} | {sig} | {since} |")
    latest: dict[str, dict] = {}
    for r in live_rows:
        latest[f"{r['source']}/{r['asset']}"] = r
    if latest:
        L += ["", "## Latest live funding (annualized)", "", "| source/asset | rate/interval | ann | interval end | product |", "|---|---|---|---|---|"]
        for k, r in sorted(latest.items()):
            ie = datetime.fromtimestamp(r["interval_ts"], tz=timezone.utc).strftime("%Y-%m-%d %H:%M") if r.get("interval_ts") else "-"
            L.append(f"| {k} | {r['rate']:.6f} | {r['ann']:.3f} | {ie} | {r.get('product_id')} |")
    # US-venue vs Binance proxy error, when both exist
    by = {}
    for r in live_rows:
        by.setdefault((r["source"], r["asset"]), []).append(r["ann"])
    for a in ("BTC", "ETH"):
        for us in ("coinbase", "bitnomial"):
            if (us, a) in by and ("binance", a) in by:
                m_us = sum(by[(us, a)]) / len(by[(us, a)])
                m_bn = sum(by[("binance", a)]) / len(by[("binance", a)])
                L.append(f"\nmean annualized funding {us}/{a}: {m_us:.3f} vs binance/{a}: {m_bn:.3f} "
                         f"(n={len(by[(us, a)])}/{len(by[('binance', a)])}) — proxy gap {m_us - m_bn:+.3f}")
    L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=str(ROOT / "configs/carry.yaml"))
    ap.add_argument("--data-dir", default=str(ROOT / "data/carry"))
    ap.add_argument("--reports-dir", default=str(ROOT / "reports"))
    ap.add_argument("--summary", action="store_true", help="only write reports/carry_paper.md|json")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    cfg = yaml.safe_load(open(args.config))
    data_dir = Path(args.data_dir)
    if not args.summary:
        res = paper.tick(cfg, data_dir)
        print(json.dumps(res, indent=1, default=float))
    s = paper.summarize(data_dir)
    live = paper._read_jsonl(data_dir / "funding-live.jsonl")
    rd = Path(args.reports_dir)
    rd.mkdir(parents=True, exist_ok=True)
    (rd / "carry_paper.json").write_text(json.dumps({"entries": s, "live_rows": len(live)}, indent=1, default=float))
    (rd / "carry_paper.md").write_text(summary_markdown(s, live))
    return 0


if __name__ == "__main__":
    sys.exit(main())
