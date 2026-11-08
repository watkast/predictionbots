"""Score the weather snapshots: did the Kalshi price or the NWS-based probability call daily highs better?

Reads weather/snapshots.jsonl (market p and forecast p per contract, hourly), looks up each settled contract's result on
Kalshi's public API, and for each contract uses the LAST snapshot taken at least `--lead-hours` before the close.
Reports Brier scores (lower is better) for the market and the forecast, the share of contracts where the gap between
them exceeded the taker fee, and what buying whenever the forecast beat the market by more than the fee would have
returned. Writes weather/CALIBRATION.md and weather/resolved.json.

  python scripts/weather_resolve.py --snapshots weather/snapshots.jsonl --out weather
  python scripts/weather_resolve.py selftest
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

KALSHI = "https://external-api.kalshi.com/trade-api/v2"


def fee(p: float) -> float:
    return 0.07 * p * (1 - p)


def pick_snapshots(rows: list[dict], lead_hours: float) -> dict[str, dict]:
    """ticker -> the last snapshot at least lead_hours before the end of the market's date (23:59 local ~ 06:00 UTC next day; we use the date + 1 day 05:00 UTC)."""
    best: dict[str, dict] = {}
    for r in rows:
        if not r.get("ticker") or not r.get("date"):
            continue
        end = datetime.fromisoformat(r["date"] + "T00:00:00+00:00").timestamp() + 29 * 3600
        t = datetime.strptime(r["t"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc).timestamp()
        if end - t < lead_hours * 3600:
            continue
        if r["ticker"] not in best or r["t"] > best[r["ticker"]]["t"]:
            best[r["ticker"]] = r
    return best


def score(picked: dict[str, dict], results: dict[str, int]) -> dict:
    rows = [(r, results[k]) for k, r in picked.items() if k in results]
    if not rows:
        return {"n": 0}
    bm = statistics.mean((r["p_market"] - y) ** 2 for r, y in rows)
    bf = statistics.mean((r["p_nws"] - y) ** 2 for r, y in rows)
    gap = [(r, y) for r, y in rows if abs(r["p_nws"] - r["p_market"]) > fee(r["p_market"])]
    # strategy: buy YES when forecast > market + fee, buy NO when forecast < market - fee; one contract, hold to settlement
    pnl, staked = 0.0, 0.0
    for r, y in gap:
        p = r["p_market"]
        if r["p_nws"] > p:
            pnl += (1 - p if y else -p) - fee(p); staked += p
        else:
            q = 1 - p
            pnl += (1 - q if not y else -q) - fee(q); staked += q
    return {"n": len(rows), "brier_market": round(bm, 4), "brier_forecast": round(bf, 4), "gap_share": round(len(gap) / len(rows), 3),
            "gap_trades": len(gap), "gap_pnl_per_dollar": round(pnl / staked, 4) if staked else None}


def fetch_results(tickers: list[str]) -> dict[str, int]:
    import httpx
    out = {}
    with httpx.Client(timeout=30) as c:
        for i in range(0, len(tickers), 100):
            r = c.get(f"{KALSHI}/markets", params={"tickers": ",".join(tickers[i:i + 100]), "limit": 100})
            if r.status_code != 200:
                print("kalshi", r.status_code, r.text[:120], file=sys.stderr); continue
            for m in r.json().get("markets") or []:
                res = str(m.get("result") or "").lower()
                if res in ("yes", "no"):
                    out[m["ticker"]] = 1 if res == "yes" else 0
    return out


def report(s: dict, lead: float) -> str:
    if not s.get("n"):
        return f"# Weather calibration\n\nNo settled contracts yet with a snapshot at least {lead:g} h before the close.\n"
    better = "forecast" if s["brier_forecast"] < s["brier_market"] else "market"
    return (f"# Weather calibration — Kalshi daily highs vs. the NWS forecast\n\nUpdated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}. "
            f"{s['n']} settled contracts, each scored on its last snapshot at least {lead:g} hours before the day ended.\n\n"
            f"| Measure | Market price | NWS-based probability |\n| --- | --- | --- |\n| Brier score (lower is better) | {s['brier_market']} | {s['brier_forecast']} |\n\n"
            f"The {better} called it better. The two differed by more than the taker fee on {s['gap_share']*100:.0f}% of contracts "
            f"({s['gap_trades']}); buying the forecast's side on those returned {s['gap_pnl_per_dollar']*100:+.1f}% per dollar after fees "
            f"(paper, one contract each, at the snapshot price).\n" if s.get("gap_pnl_per_dollar") is not None else
            f"# Weather calibration\n\n{s['n']} contracts; Brier market {s['brier_market']}, forecast {s['brier_forecast']}; no gaps larger than the fee.\n")


def selftest() -> None:
    rows = [{"t": "2026-11-08T12:00Z", "ticker": "A", "date": "2026-11-09", "p_market": 0.3, "p_nws": 0.5},
            {"t": "2026-11-09T20:00Z", "ticker": "A", "date": "2026-11-09", "p_market": 0.9, "p_nws": 0.9},
            {"t": "2026-11-08T12:00Z", "ticker": "B", "date": "2026-11-09", "p_market": 0.6, "p_nws": 0.2}]
    picked = pick_snapshots(rows, 12)
    assert picked["A"]["p_market"] == 0.3 and "B" in picked
    s = score(picked, {"A": 1, "B": 0})
    assert s["n"] == 2 and s["brier_forecast"] < s["brier_market"] and s["gap_trades"] == 2 and s["gap_pnl_per_dollar"] > 0, s
    assert "Brier" in report(s, 12)
    print("selftest ok")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--snapshots", required=True); r.add_argument("--out", default="weather"); r.add_argument("--lead-hours", type=float, default=12)
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        selftest(); return
    rows = [json.loads(l) for l in open(a.snapshots) if l.strip()]
    picked = pick_snapshots(rows, a.lead_hours)
    past = [k for k, r in picked.items() if r["date"] < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    results = fetch_results(past) if past else {}
    s = score(picked, results)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "resolved.json").write_text(json.dumps({"summary": s, "results": results}))
    (out / "CALIBRATION.md").write_text(report(s, a.lead_hours))
    print(report(s, a.lead_hours))


if __name__ == "__main__":
    main()
