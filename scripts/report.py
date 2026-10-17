#!/usr/bin/env python
"""Aggregate paper-run ledgers and backtest reports into reports/README.md.

Inputs
------
* data/ledger/*.summary.json   (PaperRunner summaries; run_id = <entry>-<date> by convention)
* data/ledger/*.jsonl          (fill ledgers; used for the per-day equity CSV)
* reports/*.json               (scripts/backtest.py results)
* reports/voided.yaml          run_ids (exact or glob) + reason: excluded from every total,
                               listed in a "Voided runs" section

Outputs
-------
* reports/README.md            leaderboard (paper) + backtest table, short and scannable
* reports/equity_daily.csv     one row per (run_group, day): realized pnl, fees, fills, cum pnl

Runs are grouped by `run_group` = run_id with a trailing `-<digits>` / `-<date>`
stripped, so repeated GitHub-Actions runs of the same matrix entry roll up.

    python scripts/report.py [--ledger data/ledger] [--reports reports] [--out reports/README.md]
                             [--voided reports/voided.yaml]
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import glob
import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_RUN_SUFFIX = re.compile(r"(-\d{6,}|-\d{4}-?\d{2}-?\d{2}(T[\d:-]+)?|-gha-\d+|-\d+)$")


def run_group(run_id: str) -> str:
    g = run_id
    for _ in range(3):
        g2 = _RUN_SUFFIX.sub("", g)
        if g2 == g:
            break
        g = g2
    return g or run_id


def _load_json(p: Path):
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def _day(ts: float) -> str:
    return datetime.fromtimestamp(float(ts), tz=timezone.utc).strftime("%Y-%m-%d")


def load_voided(path: str | Path | None) -> dict[str, str]:
    """reports/voided.yaml -> {run_id or glob: reason}. Missing file -> {}."""
    if not path or not Path(path).exists():
        return {}
    import yaml

    data = yaml.safe_load(Path(path).read_text()) or {}
    rows = data.get("voided", data) if isinstance(data, dict) else data
    out: dict[str, str] = {}
    for r in rows or []:
        if isinstance(r, dict) and r.get("run_id"):
            out[str(r["run_id"])] = " ".join(str(r.get("reason", "")).split())
        elif isinstance(r, str):
            out[r] = ""
    return out


def void_reason(run_id: str, voided: dict[str, str] | None) -> str | None:
    """Reason if `run_id` is voided (exact match first, then glob), else None."""
    if not voided:
        return None
    if run_id in voided:
        return voided[run_id]
    for pat, reason in voided.items():
        if any(c in pat for c in "*?[") and fnmatch.fnmatchcase(run_id, pat):
            return reason
    return None


def load_paper(ledger_dir: Path, voided: dict[str, str] | None = None
               ) -> tuple[list[dict], dict[str, list[dict]]]:
    """-> (summaries, fills_by_group). Voided run_ids are dropped from both;
    their summaries are returned separately by `load_paper_voided`."""
    summaries = []
    fills: dict[str, list[dict]] = defaultdict(list)
    for sp in sorted(ledger_dir.glob("*.summary.json")):
        s = _load_json(sp)
        if not isinstance(s, dict):
            continue
        s.setdefault("run_id", sp.name.replace(".summary.json", ""))
        if void_reason(s["run_id"], voided) is not None:
            continue
        s["_group"] = run_group(s["run_id"])
        s["_file"] = sp.name
        summaries.append(s)
    for lp in sorted(ledger_dir.glob("*.jsonl")):
        if void_reason(lp.stem, voided) is not None:
            continue
        grp = run_group(lp.stem)
        with lp.open() as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("type") == "fill":
                    fills[grp].append(d)
    return summaries, fills


def load_paper_voided(ledger_dir: Path, voided: dict[str, str] | None) -> list[dict]:
    """Rows for the "Voided runs" section: one per voided summary file."""
    rows = []
    if not voided:
        return rows
    for sp in sorted(ledger_dir.glob("*.summary.json")):
        s = _load_json(sp)
        if not isinstance(s, dict):
            continue
        rid = s.get("run_id") or sp.name.replace(".summary.json", "")
        reason = void_reason(rid, voided)
        if reason is None:
            continue
        rows.append({"run_id": rid, "group": run_group(rid),
                     "strategy": ",".join(s.get("strategies") or []) or s.get("strategy", "?"),
                     "net_pnl": round(float(s.get("net_pnl", 0.0)), 2), "fills": int(s.get("fills", 0)),
                     "day": _day(s.get("started_at", 0)) if s.get("started_at") else "", "reason": reason})
    return rows


def _realized_by_day(fills: list[dict]) -> dict[str, dict]:
    """Realized pnl per UTC day from a fill ledger, replaying positions per market."""
    from pb.core.types import Action
    from pb.sim.engine import Position

    pos: dict[str, Position] = defaultdict(Position)
    out: dict[str, dict] = defaultdict(lambda: {"realized": 0.0, "fees": 0.0, "fills": 0, "contracts": 0.0})
    for d in sorted(fills, key=lambda x: float(x["ts"])):
        p = pos[d["market_id"]]
        before = p.realized
        p.apply(Action(d["action"]), float(d["price"]), float(d["size"]), float(d.get("fee", 0.0)))
        day = out[_day(d["ts"])]
        day["realized"] += p.realized - before
        day["fees"] += float(d.get("fee", 0.0))
        day["fills"] += 1
        day["contracts"] += float(d["size"])
    return dict(out)


def paper_leaderboard(summaries: list[dict], fills: dict[str, list[dict]]) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for s in summaries:
        groups[s["_group"]].append(s)
    rows = []
    for grp, ss in groups.items():
        ss.sort(key=lambda s: float(s.get("updated_at", 0)))
        latest = ss[-1]
        strategy = ",".join(latest.get("strategies") or []) or latest.get("strategy", "?")
        venue = latest.get("venue") or _venue_from_markets(latest.get("markets", []))
        days = sorted({_day(s.get("started_at", 0)) for s in ss if s.get("started_at")})
        # net pnl: ledgers resume per run_id, so each distinct run_id's latest summary is additive
        by_run: dict[str, dict] = {}
        for s in ss:
            by_run[s["run_id"]] = s
        net = sum(float(s.get("net_pnl", 0.0)) for s in by_run.values())
        fees = sum(float(s.get("fees", 0.0)) for s in by_run.values())
        n_fills = sum(int(s.get("fills", 0)) for s in by_run.values())
        maker = sum(int(s.get("maker_fills", 0)) for s in by_run.values())
        max_cap = max((float(s.get("max_capital_at_risk", 0.0)) for s in ss), default=0.0)
        uptime = sum(float(s.get("uptime_secs", 0.0)) for s in by_run.values())
        reality = latest.get("reality") or {}
        risk = latest.get("risk") or {}
        flags = []
        if reality.get("cross_assumed_fill_frac", 0) > 0.5:
            flags.append(f"cross-assumed {reality['cross_assumed_fill_frac']:.0%}")
        d = reality.get("max_fill_to_touch_depth", 0)
        if d == "inf" or (isinstance(d, (int, float)) and d > 1):
            flags.append(f"fill>touch {d}")
        if reality.get("top3_market_pnl_frac", 0) >= 0.9 and n_fills > 10:
            flags.append("top3 concentrated")
        if risk.get("halted"):
            flags.append(f"HALTED {risk.get('halt_reason', '')[:30]}")
        if risk.get("rejected", 0) > risk.get("accepted", 0) and risk.get("rejected", 0) > 0:
            flags.append("risk-rejected > accepted")
        rows.append({
            "run": grp, "strategy": strategy, "venue": venue, "net_pnl": round(net, 2), "fees": round(fees, 2),
            "ret_on_max_cap": (round(net / max_cap, 4) if max_cap > 0 else 0.0), "max_cap": round(max_cap, 2),
            "fills": n_fills, "maker_pct": (round(100.0 * maker / n_fills, 1) if n_fills else 0.0),
            "days": len(days), "hours": round(uptime / 3600.0, 1), "runs": len(by_run),
            "last_update": _day(latest.get("updated_at", 0)) if latest.get("updated_at") else "",
            "flags": "; ".join(flags) or "-",
            "markets": len(latest.get("markets", [])),
        })
    rows.sort(key=lambda r: r["net_pnl"], reverse=True)
    return rows


def _venue_from_markets(markets: list[str]) -> str:
    if not markets:
        return "?"
    return "kalshi" if str(markets[0]).upper().startswith("KX") else "polymarket"


def load_backtests(reports_dir: Path) -> list[dict]:
    rows = []
    for jp in sorted(reports_dir.glob("*.json")):
        if jp.name in ("equity_daily.json",):
            continue
        data = _load_json(jp)
        if not isinstance(data, list):
            continue
        for r in data:
            if not isinstance(r, dict) or r.get("error"):
                continue
            s = r.get("summary", {})
            f = r.get("reality", {})
            rows.append({
                "report": jp.stem, "strategy": r.get("strategy", "?"), "label": r.get("label", ""),
                "fidelity": "L2" if str(r.get("fidelity", "")).startswith("L2") else "low",
                "net_pnl": s.get("net_pnl", 0.0), "ret_on_max_cap": s.get("net_pnl_on_max_capital", 0.0),
                "maker_pct": s.get("maker_pct", 0.0), "fills": s.get("fills", 0),
                "max_dd": s.get("max_drawdown", 0.0), "win_rate": s.get("market_win_rate", 0.0),
                "cross": f.get("cross_assumed_fill_frac", 0.0), "top3": f.get("top3_market_pnl_frac", 0.0),
                "events": r.get("n_events", 0),
            })
    rows.sort(key=lambda r: (r["report"], -float(r["net_pnl"] or 0)))
    return rows


def write_equity_csv(fills: dict[str, list[dict]], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run", "day", "realized_pnl", "fees", "net_pnl", "cum_net_pnl", "fills", "contracts"])
        for grp in sorted(fills):
            cum = 0.0
            for day, d in sorted(_realized_by_day(fills[grp]).items()):
                net = d["realized"] - d["fees"]
                cum += net
                w.writerow([grp, day, round(d["realized"], 4), round(d["fees"], 4), round(net, 4), round(cum, 4),
                            d["fills"], round(d["contracts"], 2)])
                n += 1
    return n


def _f(v, nd=2) -> str:
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def render(paper: list[dict], backtests: list[dict], n_days: int, equity_csv: str,
           voided: list[dict] | None = None) -> str:
    L = [f"# Results", "", f"Updated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}. "
         "All numbers are PAPER (simulated fills against live books; no fantasy fills: takers only eat "
         "resting size, makers only fill on prints through / at the price after queue, or on adverse crossings). "
         "Positive pnl here is necessary, not sufficient.", ""]
    L += ["## Paper leaderboard", ""]
    if not paper:
        L += ["_No paper runs yet (data/ledger/*.summary.json)._", ""]
    else:
        L += ["| run | strategy | venue | net pnl $ | ret / max cap | max cap $ | fills | maker % | days | hours | flags |",
              "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
        for r in paper:
            L.append(f"| {r['run']} | {r['strategy']} | {r['venue']} | {_f(r['net_pnl'])} | {r['ret_on_max_cap']:.1%} | "
                     f"{_f(r['max_cap'])} | {r['fills']} | {_f(r['maker_pct'], 0)} | {r['days']} | {r['hours']} | {r['flags']} |")
        L += ["", f"Per-day equity: `{equity_csv}` ({n_days} run-days). "
              "`ret / max cap` = net pnl over the peak collateral locked. `flags` come from the simulator's reality "
              "checks (cross-assumed fills = maker fills inferred from the book crossing us without a print; "
              "fill>touch = a fill larger than the resting size at the touch; top3 = pnl concentrated in 3 markets) "
              "and from the RiskManager (HALTED = daily-loss / kill file).", ""]
    if voided:
        L += ["### Voided runs", "",
              "Excluded from every total above (`reports/voided.yaml`); listed so nothing disappears silently.", "",
              "| run_id | strategy | net pnl $ | fills | day | reason |", "|---|---|---:|---:|---|---|"]
        for v in voided:
            L.append(f"| {v['run_id']} | {v['strategy']} | {_f(v['net_pnl'])} | {v['fills']} | {v['day']} | "
                     f"{v['reason'].replace('|', '/')} |")
        L.append("")
    L += ["## Backtests", ""]
    if not backtests:
        L += ["_No backtest reports yet (reports/*.json from scripts/backtest.py)._", ""]
    else:
        L += ["| report | strategy | label | fidelity | net pnl $ | ret / max cap | maker % | fills | max DD | win rate | cross-assumed | top3 share |",
              "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for r in backtests:
            L.append(f"| {r['report']} | {r['strategy']} | {r['label']} | {r['fidelity']} | {_f(float(r['net_pnl'] or 0))} | "
                     f"{float(r['ret_on_max_cap'] or 0):.1%} | {_f(float(r['maker_pct'] or 0), 0)} | {r['fills']} | "
                     f"{_f(float(r['max_dd'] or 0))} | {float(r['win_rate'] or 0):.0%} | {float(r['cross'] or 0):.0%} | "
                     f"{float(r['top3'] or 0):.0%} |")
        L += ["", "`fidelity=low` = candle+tape history with `maker_requires_through` (maker fills only on prints "
              "strictly through our price); `L2` = our own recorded books. Walk-forward rows are labelled `oos<k>`.", ""]
    L += ["## How to read this", "",
          "1. A strategy earns a place only with L2 paper days: positive net pnl, maker % high for maker models, "
          "no `fill>touch` / high cross-assumed flags, pnl not concentrated in 3 markets.",
          "2. Taker baselines (`taker_lag`, `taker_momentum`) are expected to lose; they calibrate the fee drag.",
          "3. Backtest OOS (`oos*`) rows matter more than in-sample grid rows.", ""]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", default="data/ledger")
    ap.add_argument("--reports", default="reports")
    ap.add_argument("--out", default="reports/README.md")
    ap.add_argument("--equity-csv", default="reports/equity_daily.csv")
    ap.add_argument("--voided", default="reports/voided.yaml", help="YAML of voided run_ids (+ reason)")
    a = ap.parse_args()
    voided = load_voided(a.voided)
    summaries, fills = load_paper(Path(a.ledger), voided)
    paper = paper_leaderboard(summaries, fills)
    backtests = load_backtests(Path(a.reports))
    vrows = load_paper_voided(Path(a.ledger), voided)
    n_days = write_equity_csv(fills, Path(a.equity_csv))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(paper, backtests, n_days, a.equity_csv, vrows))
    print(out.read_text())
    print(f"wrote {out} and {a.equity_csv}: {len(paper)} paper groups, {len(backtests)} backtest rows, "
          f"{len(vrows)} voided runs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
