#!/usr/bin/env python3
"""
Mr. P — Backfill v0.  Pulls historical 1-second BRTI (the exact settlement index) and derives
every 15-minute window's price-to-beat, close and outcome from the index alone, then
cross-checks the derived values against the exchange's stamped priceToBeat / settlementPrice
for every window Polymarket US has listed (a rule-mismatch detector).

Output is written in the recorder's JSONL format, so mrp_analyze.py runs on it unchanged
(no order books in backfill data, so only the settlement gate + physics are answered).

Sources
  pmus    Polymarket US public Asset Prices API — no keys, 1 hour per request, back to launch.
  kalshi  Kalshi's CF Benchmarks REST passthrough — needs KALSHI_KEY_ID + KALSHI_PRIVATE_KEY_PATH,
          reaches further back (CF Benchmarks history).

Usage:  python3 mrp_backfill.py --days 7 [--source pmus|kalshi] [--out ./data_backfill] [--no-verify]
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mrp_recorder as R  # reuse Writer, gen_slug, parsers, PMUS client, kalshi signer  # noqa: E402


def iter_hours(start: int, end: int):
    h = start - (start % 3600)
    while h < end:
        yield h
        h += 3600


def pull_pmus_hour(pm: R.PMUS, h: int) -> dict[int, tuple[float, int]]:
    out = {}
    for attempt in range(4):
        try:
            candles = pm.brti_candles(h, h + 3599)
            for c in candles:
                n = int(c.get("tickCount", 0) or 0)
                if n > 0:
                    out[int(c["timestamp"])] = (float(c["close"]), n)
            return out
        except Exception as e:  # noqa
            time.sleep(1.5 * (attempt + 1))
            last = e
    print(f"  ! hour {datetime.fromtimestamp(h, tz=timezone.utc):%Y-%m-%d %H}Z failed: {last}")
    return out


def _find_points(obj):
    """Tolerant extraction of [{time, value}] from a CF Benchmarks-style response."""
    if isinstance(obj, dict):
        if "time" in obj and "value" in obj:
            yield obj
        else:
            for v in obj.values():
                yield from _find_points(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _find_points(v)


def pull_kalshi_hour(sign, h: int) -> dict[int, tuple[float, int]]:
    path = "/trade-api/v2/cfbenchmarks/history/values"
    ts_iso = datetime.fromtimestamp(h, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    out: dict[int, tuple[float, int]] = {}
    for attempt in range(4):
        try:
            r = requests.get(R.KALSHI_REST + path, params={"id": "BRTI", "timespan": "HOUR", "timestamp": ts_iso},
                             headers=sign("GET", path), timeout=20)
            r.raise_for_status()
            counts: dict[int, int] = {}
            for p in _find_points(r.json()):
                t = int(p["time"]); t = t // 1000 if t > 1e11 else t
                out[t] = (float(p["value"]), counts.get(t, 0) + 1)   # last print in the second wins
                counts[t] = counts.get(t, 0) + 1
            return out
        except Exception as e:  # noqa
            time.sleep(1.5 * (attempt + 1)); last = e
    print(f"  ! hour {ts_iso} failed: {last}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=float, default=7)
    ap.add_argument("--source", choices=["pmus", "kalshi"], default="pmus")
    ap.add_argument("--out", default="./data_backfill")
    ap.add_argument("--no-verify", action="store_true", help="skip the exchange cross-check")
    ap.add_argument("--rate", type=float, default=2.0, help="max requests per second")
    args = ap.parse_args()

    W = R.Writer(args.out)
    pm = R.PMUS()
    sign = R._kalshi_signer() if args.source == "kalshi" else None
    now = int(time.time())
    start = now - int(args.days * 86400)
    start -= start % 3600
    brti: dict[int, float] = {}
    hours = list(iter_hours(start, now))
    print(f"backfilling {len(hours)} hours of 1-second BRTI from {args.source} -> {args.out}")
    t_last = 0.0
    for i, h in enumerate(hours):
        wait = (1.0 / args.rate) - (time.time() - t_last)
        if wait > 0:
            time.sleep(wait)
        t_last = time.time()
        pts = pull_pmus_hour(pm, h) if args.source == "pmus" else pull_kalshi_hour(sign, h)
        for ts, (c, n) in sorted(pts.items()):
            brti[ts] = c
            W.write("pmus.idx", {"ts": ts, "c": c, "n": n, "src": args.source}, t_ms=ts * 1000 + 999)
        if i % 24 == 23 or i == len(hours) - 1:
            print(f"  {i+1}/{len(hours)} hours, {len(brti)} prints")

    # derive every window from the index alone
    derived = {}
    s = R.window_start(start) + R.WINDOW
    while s + R.WINDOW + 60 <= now:
        e = s + R.WINDOW
        a = [brti[t] for t in range(s - 60, s) if t in brti]
        b = [brti[t] for t in range(e - 60, e) if t in brti]
        if len(a) == 60 and len(b) == 60:
            ptb, close = round(sum(a) / 60, 2), round(sum(b) / 60, 2)
            derived[s] = (ptb, close, 1.0 if close >= ptb else 0.0)
        s += R.WINDOW
    print(f"derived {len(derived)} complete windows from the index")

    # cross-check against the exchange's stamped values (public endpoint, batches of 50 slugs)
    mismatches = 0
    checked = 0
    if not args.no_verify:
        starts = sorted(derived)
        for i in range(0, len(starts), 50):
            batch = starts[i:i + 50]
            try:
                time.sleep(0.5)
                by_slug = pm.markets_by_slugs([R.gen_slug(x) for x in batch])
            except Exception as ex:  # noqa
                print(f"  ! verify batch failed: {ex}"); by_slug = {}
            for x in batch:
                ptb, close, outcome = derived[x]
                m = by_slug.get(R.gen_slug(x))
                rec = {"slug": R.gen_slug(x), "end": x + R.WINDOW, "priceToBeat": ptb, "settlementPrice": close,
                       "settlement": outcome, "derived": True}
                if m:
                    apt = m.get("assetPriceTerms") or {}
                    ex_ptb, ex_sp = R.parse_amount(apt.get("priceToBeat")), R.parse_amount(apt.get("settlementPrice"))
                    rec.update({"exchange_ptb": ex_ptb, "exchange_settlementPrice": ex_sp})
                    if ex_ptb is not None and ex_sp is not None:
                        checked += 1
                        ok = abs(ex_ptb - ptb) < 0.006 and abs(ex_sp - close) < 0.006
                        rec["match"] = ok
                        if not ok:
                            mismatches += 1
                            print(f"  MISMATCH {R.gen_slug(x)}: derived ptb/close {ptb}/{close} vs exchange {ex_ptb}/{ex_sp}")
                        # trust the exchange's stamped values for the analyzer
                        rec["priceToBeat"], rec["settlementPrice"] = ex_ptb, ex_sp
                        rec["settlement"] = 1.0 if ex_sp >= ex_ptb else 0.0
                W.write("pmus.settlement", rec, t_ms=(x + R.WINDOW + 60) * 1000)
    else:
        for x, (ptb, close, outcome) in derived.items():
            W.write("pmus.settlement", {"slug": R.gen_slug(x), "end": x + R.WINDOW, "priceToBeat": ptb,
                                        "settlementPrice": close, "settlement": outcome, "derived": True},
                    t_ms=(x + R.WINDOW + 60) * 1000)
    print(f"done. windows={len(derived)} verified_against_exchange={checked} mismatches={mismatches}  "
          f"lines={W.count}\n-> python3 mrp_analyze.py {args.out}")


if __name__ == "__main__":
    main()
