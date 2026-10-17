#!/usr/bin/env python
"""Run one (or every) entry of configs/paper_matrix.yaml through scripts/paper.py.

    python scripts/paper_matrix.py --list
    python scripts/paper_matrix.py --entry mm_crypto_twap_kxbtc15m --duration 600
    python scripts/paper_matrix.py --all --duration 3300          # sequential
    python scripts/paper_matrix.py --entry x --dry-run             # print the command only

run_id = <entry>-<YYYYMMDDTHHMM> so scripts/report.py groups repeated runs per
entry. Entries with `requires_env` are skipped (exit 0) when a variable is
missing; a failing entry does not stop `--all` (its exit code is reported).
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NO_MARKETS_EXIT = 3   # scripts/paper.py: selector found nothing to trade (not a failure)
sys.path.insert(0, str(ROOT))


def load_matrix(path: str | Path) -> dict:
    import yaml

    data = yaml.safe_load(Path(path).read_text()) or {}
    data.setdefault("defaults", {})
    data.setdefault("runs", [])
    return data


def build_command(entry: dict, defaults: dict, duration: float | None = None, run_id: str | None = None,
                  python: str = sys.executable) -> list[str]:
    d = dict(defaults)
    d.update({k: v for k, v in entry.items() if k in ("duration", "max_position", "daily_loss_limit", "max_capital",
                                                      "max_capital_per_market", "record", "roll_secs")})
    if duration is not None:
        d["duration"] = duration
    rid = run_id or f"{entry['name']}-{time.strftime('%Y%m%dT%H%M', time.gmtime())}"
    cmd = [python, str(ROOT / "scripts" / "paper.py"), "--venue", entry["venue"], "--strategy", entry["strategy"],
           "--run-id", rid]
    if entry.get("params"):
        cmd += ["--params", entry["params"]]
    sel = entry.get("select") or {}
    if sel.get("kalshi_series"):
        cmd += ["--kalshi-series", *sel["kalshi_series"]]
    if sel.get("tickers"):
        cmd += ["--tickers", *sel["tickers"]]
    if sel.get("tokens"):
        cmd += ["--tokens", *sel["tokens"]]
    if sel.get("kalshi_scan"):
        cmd += ["--kalshi-scan", str(sel["kalshi_scan"])]
    if sel.get("poly_crypto_15m"):
        cmd += ["--poly-crypto-15m"]
    if sel.get("poly_events"):
        cmd += ["--poly-events"]
    if sel.get("top") is not None:
        cmd += ["--top", str(sel["top"])]
    if entry.get("signals"):
        cmd += ["--signals", str(entry["signals"])]
    for k, v in (entry.get("params_override") or {}).items():
        cmd += ["--set", f"{k}={json.dumps(v)}"]
    if d.get("duration") is not None:
        cmd += ["--duration", str(d["duration"])]
    for key, flag in (("max_position", "--max-position"), ("daily_loss_limit", "--daily-loss-limit"),
                      ("max_capital", "--max-capital"), ("max_capital_per_market", "--max-capital-per-market"),
                      ("roll_secs", "--roll-secs")):
        if d.get(key) is not None:
            cmd += [flag, str(d[key])]
    if d.get("record") is False:
        cmd += ["--no-record"]
    for k, v in (entry.get("args") or {}).items():
        flag = "--" + str(k).replace("_", "-")
        if v is True:
            cmd.append(flag)
        elif v is not False and v is not None:
            cmd += [flag, str(v)]
    return cmd


def missing_env(entry: dict, env: dict | None = None) -> list[str]:
    env = os.environ if env is None else env
    return [k for k in (entry.get("requires_env") or []) if not env.get(k)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--matrix", default=str(ROOT / "configs" / "paper_matrix.yaml"))
    ap.add_argument("--entry", action="append", default=[], help="entry name (repeatable)")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--duration", type=float, default=None, help="override seconds per entry")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    m = load_matrix(a.matrix)
    runs = {r["name"]: r for r in m["runs"]}
    if a.list:
        for r in m["runs"]:
            req = f" (requires {', '.join(r['requires_env'])})" if r.get("requires_env") else ""
            print(f"{r['name']:34s} {r['strategy']:24s} {r['venue']:11s} signals={r.get('signals') or '-'}{req}")
        return 0
    names = list(runs) if a.all else a.entry
    if not names:
        ap.error("--entry NAME, --all or --list")
    unknown = [n for n in names if n not in runs]
    if unknown:
        print(f"unknown entries: {unknown}; known: {list(runs)}", file=sys.stderr)
        return 2
    rc = 0
    for n in names:
        entry = runs[n]
        miss = missing_env(entry)
        if miss:
            print(f"[{n}] skipped: missing env {miss}")
            continue
        cmd = build_command(entry, m["defaults"], a.duration)
        print(f"[{n}] {shlex.join(cmd)}")
        if a.dry_run:
            continue
        r = subprocess.run(cmd, cwd=ROOT)
        if r.returncode == NO_MARKETS_EXIT:
            print(f"[{n}] skipped: selector found no markets")
            continue
        if r.returncode != 0:
            print(f"[{n}] exit {r.returncode}", file=sys.stderr)
            rc = rc or r.returncode
    return rc


if __name__ == "__main__":
    sys.exit(main())
