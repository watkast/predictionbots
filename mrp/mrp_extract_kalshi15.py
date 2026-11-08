#!/usr/bin/env python3
"""
Extract per-window datasets for Kalshi KX<COIN>15M markets from Mr. P recorder files, in the same shape as
mrp_extract_btc15.py so scripts/benchmark_rules.py can replay rules on them:
  {"slug": ticker, "T0": open, "T": close, "ptb": strike, "settle": <BRTI 60-s average at the close, reproduced from
   the prints>, "prints": {sec: value}, "book": {sec: [yes_ask, ask_qty, yes_bid, bid_qty, state]}}

Settlement: Kalshi's BTC 15-minute markets settle on the CF Benchmarks index averaged over the final minute; we
reproduce that from the recorded 1-second prints (needs >= 58 of 60 prints; otherwise the window is skipped).

Usage:  python3 mrp_extract_kalshi15.py DATA_DIR OUT.json [--sym btc]
"""
from __future__ import annotations

import glob
import gzip
import json
import os
import re
import sys
from datetime import datetime, timezone

HEAD_RE = re.compile(r'^\{"t":(\d+),"k":"([^"]+)"')


def ts(s):
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return int(s)
    try:
        return int(datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp())
    except ValueError:
        return None


def main(data_dir, out, sym="btc"):
    files = sorted(glob.glob(os.path.join(data_dir, "**", "*.jsonl"), recursive=True) + glob.glob(os.path.join(data_dir, "**", "*.jsonl.gz"), recursive=True))
    prints = {}                   # sec -> index value for sym
    markets = {}                  # ticker -> {open, close, strike}
    books = {}                    # ticker -> {sec: top}
    n = 0
    tag = f'"sym":"{sym}"'
    for f in files:
        opener = gzip.open if f.endswith(".gz") else open
        with opener(f, "rt", encoding="utf-8") as fh:
            for line in fh:
                m = HEAD_RE.match(line)
                if not m:
                    continue
                kind = m.group(2)
                if kind == "kalshi.idx":
                    if tag not in line:
                        continue
                elif kind == "kalshi.book":
                    if tag not in line:
                        continue
                elif kind != "kalshi.markets":
                    continue
                try:
                    r = json.loads(line)
                except (json.JSONDecodeError, MemoryError):
                    continue
                d = r.get("d") or {}
                n += 1
                if kind == "kalshi.idx":
                    try:
                        prints[int(d["t"])] = float(d["v"])
                    except (KeyError, TypeError, ValueError):
                        pass
                elif kind == "kalshi.markets":
                    for tk, info in (d.items() if isinstance(d, dict) else []):
                        if not isinstance(info, dict) or str(info.get("sym", "")).lower() != sym:
                            continue
                        mk = markets.setdefault(tk, {})
                        for k in ("open", "close", "strike"):
                            if info.get(k) is not None and k not in mk:
                                mk[k] = info[k]
                elif kind == "kalshi.book":
                    tk = d.get("ticker")
                    if not tk:
                        continue
                    yb, ya = d.get("yb") or [], d.get("ya") or []
                    ask = ya[0][0] if ya else None
                    bid = yb[0][0] if yb else None
                    books.setdefault(tk, {})[int(r.get("t", 0) / 1000)] = [ask, round(sum(q for p, q in ya if ask is not None and abs(p - ask) < 1e-9), 2),
                                                                             bid, round(sum(q for p, q in yb if bid is not None and abs(p - bid) < 1e-9), 2), "OPEN"]
    windows = []
    for tk, mk in sorted(markets.items()):
        t0, T, strike = ts(mk.get("open")), ts(mk.get("close")), mk.get("strike")
        if not t0 or not T or strike is None:
            continue
        try:
            strike = float(strike)
        except (TypeError, ValueError):
            continue
        final = [prints[s] for s in range(T - 60, T) if s in prints]
        if len(final) < 58:
            continue
        settle = round(sum(final) / len(final), 4)
        pr = {str(s): prints[s] for s in range(t0 - 130, T + 3) if s in prints}
        bk = books.get(tk, {})
        windows.append({"slug": tk, "T0": t0, "T": T, "ptb": strike, "settle": settle, "settle_latency": None, "my_close": settle,
                        "print_cov": round(sum(1 for s in range(t0 - 60, T) if s in prints) / max(1, T - t0 + 60), 3), "book_secs": len(bk), "prints": pr,
                        "book": {str(s): v for s, v in sorted(bk.items()) if t0 - 5 <= s <= T + 5}})
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"windows": windows, "n_records": n, "venue": "kalshi", "sym": sym}, fh, separators=(",", ":"))
    withbook = sum(1 for w in windows if w["book_secs"] > 30)
    print(f"records used {n:,}  kalshi {sym} windows with strike + reproduced settlement {len(windows)}  with books {withbook}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sym = "btc"
    if "--sym" in sys.argv:
        sym = sys.argv[sys.argv.index("--sym") + 1]
    main(args[0], args[1], sym)
