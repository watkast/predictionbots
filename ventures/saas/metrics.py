#!/usr/bin/env python
"""Portfolio metrics for the SaaS ventures: reads ventures/saas/metrics.json and
exposes rows + totals + kill-rule verdicts for scripts/dashboard.py (and prints
a table from the CLI). Stdlib only.

    python ventures/saas/metrics.py                 # table
    python ventures/saas/metrics.py --json          # machine-readable summary

metrics.json schema (one entry per product; every number is for the trailing
30 days unless the key says otherwise; all money in USD):

{
  "as_of": "2026-10-17",                # ISO date the numbers were pulled
  "products": [
    {
      "id": "oddsmath",                  # == portfolio.yaml id
      "name": "oddsmath API",
      "status": "idea|building|live|sunset",
      "channel": "rapidapi|stripe|apify|gumroad|mcp|...",
      "launched": "2026-11-01" | null,   # first day it could take money
      "mrr_usd": 0.0,                    # recurring revenue (payment-link subs + marketplace)
      "revenue_30d_usd": 0.0,            # all cash incl. one-off / pay-per-call
      "subscribers": 0,                  # paying, active
      "churn_pct_30d": 0.0,              # cancelled / start-of-period subscribers * 100
      "cost_usd_30d": 0.0,               # hosting + fees + any paid data
      "uptime_pct_30d": 100.0,           # external monitor (UptimeRobot/Cloudflare)
      "requests_30d": 0,                 # billable calls
      "support_tickets_30d": 0,          # emails / marketplace questions / refunds
      "support_minutes_30d": 0,          # owner time actually spent
      "note": "free text"
    }
  ]
}

Kill rules (also documented in PLAN.md §f): a live product is `SUNSET` when it is
>= 60 days past launch and MRR < $20, or support_minutes_30d > 60, or
uptime_pct_30d < 99.0 two months running (tracked by the caller), or net margin
< 0 for 2 months. `WATCH` = any single rule close to tripping.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_PATH = HERE / "metrics.json"

KILL_MRR_USD = 20.0
KILL_AFTER_DAYS = 60
KILL_SUPPORT_MINUTES = 60
KILL_UPTIME_PCT = 99.0

NUMERIC_DEFAULTS = {
    "mrr_usd": 0.0, "revenue_30d_usd": 0.0, "subscribers": 0, "churn_pct_30d": 0.0,
    "cost_usd_30d": 0.0, "uptime_pct_30d": 100.0, "requests_30d": 0,
    "support_tickets_30d": 0, "support_minutes_30d": 0,
}


def _parse_date(s) -> date | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s)).date()
    except ValueError:
        return None


def load(path: Path | str = DEFAULT_PATH) -> dict:
    """Load and normalise metrics.json. Missing file -> empty portfolio (never raises)."""
    p = Path(path)
    if not p.exists():
        return {"as_of": None, "products": []}
    raw = json.loads(p.read_text() or "{}")
    products = []
    for prod in raw.get("products", []):
        row = dict(prod)
        row.setdefault("id", "?")
        row.setdefault("name", row["id"])
        row.setdefault("status", "idea")
        row.setdefault("channel", "")
        row.setdefault("launched", None)
        row.setdefault("note", "")
        for k, dflt in NUMERIC_DEFAULTS.items():
            v = row.get(k)
            row[k] = type(dflt)(v) if v is not None else dflt
        products.append(row)
    return {"as_of": raw.get("as_of"), "products": products}


def verdict(row: dict, today: date | None = None) -> tuple[str, list[str]]:
    """(SUNSET|WATCH|OK|n/a, reasons). Only live products get a verdict."""
    today = today or date.today()
    if row.get("status") != "live":
        return "n/a", [f"status={row.get('status')}"]
    reasons: list[str] = []
    launched = _parse_date(row.get("launched"))
    age = (today - launched).days if launched else None
    kill = False
    if age is not None and age >= KILL_AFTER_DAYS and row["mrr_usd"] < KILL_MRR_USD:
        kill = True
        reasons.append(f"MRR ${row['mrr_usd']:.0f} < ${KILL_MRR_USD:.0f} after {age} days")
    if row["support_minutes_30d"] > KILL_SUPPORT_MINUTES:
        kill = True
        reasons.append(f"support {row['support_minutes_30d']} min/30d > {KILL_SUPPORT_MINUTES}")
    if row["uptime_pct_30d"] < KILL_UPTIME_PCT:
        reasons.append(f"uptime {row['uptime_pct_30d']:.2f}% < {KILL_UPTIME_PCT}% (kill if 2 months)")
    net = row["revenue_30d_usd"] - row["cost_usd_30d"]
    if net < 0:
        reasons.append(f"net margin ${net:.2f} < 0 (kill if 2 months)")
    if kill:
        return "SUNSET", reasons
    if reasons or (age is not None and age >= KILL_AFTER_DAYS - 14 and row["mrr_usd"] < KILL_MRR_USD):
        if not reasons:
            reasons.append(f"MRR ${row['mrr_usd']:.0f} with {KILL_AFTER_DAYS - age} days to kill review")
        return "WATCH", reasons
    return "OK", []


def summarize(data: dict, today: date | None = None) -> dict:
    """Totals + per-product rows (with verdicts) for the dashboard."""
    rows = []
    for r in data.get("products", []):
        v, why = verdict(r, today)
        rows.append({**r, "verdict": v, "verdict_reasons": why,
                     "net_30d_usd": round(r["revenue_30d_usd"] - r["cost_usd_30d"], 2)})
    live = [r for r in rows if r["status"] == "live"]
    totals = {
        "products": len(rows),
        "live": len(live),
        "mrr_usd": round(sum(r["mrr_usd"] for r in rows), 2),
        "revenue_30d_usd": round(sum(r["revenue_30d_usd"] for r in rows), 2),
        "cost_30d_usd": round(sum(r["cost_usd_30d"] for r in rows), 2),
        "net_30d_usd": round(sum(r["net_30d_usd"] for r in rows), 2),
        "subscribers": sum(r["subscribers"] for r in rows),
        "support_tickets_30d": sum(r["support_tickets_30d"] for r in rows),
        "support_minutes_30d": sum(r["support_minutes_30d"] for r in rows),
        "min_uptime_pct_30d": min((r["uptime_pct_30d"] for r in live), default=None),
        "sunset_candidates": [r["id"] for r in rows if r["verdict"] == "SUNSET"],
    }
    return {"as_of": data.get("as_of"), "totals": totals, "rows": rows}


def dashboard_rows(path: Path | str = DEFAULT_PATH, today: date | None = None) -> dict:
    """The one call scripts/dashboard.py should make (see PLAN.md loader note)."""
    return summarize(load(path), today)


def _table(summary: dict) -> str:
    cols = ["id", "status", "channel", "mrr_usd", "subscribers", "churn_pct_30d", "cost_usd_30d",
            "uptime_pct_30d", "support_tickets_30d", "verdict"]
    lines = [" | ".join(cols)]
    for r in summary["rows"]:
        lines.append(" | ".join(str(r.get(c, "")) for c in cols))
    t = summary["totals"]
    lines.append(f"TOTAL mrr=${t['mrr_usd']} net30d=${t['net_30d_usd']} subs={t['subscribers']} "
                 f"live={t['live']}/{t['products']} sunset={t['sunset_candidates']} as_of={summary['as_of']}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--path", default=str(DEFAULT_PATH))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    s = dashboard_rows(a.path)
    print(json.dumps(s, indent=1, default=str) if a.json else _table(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
