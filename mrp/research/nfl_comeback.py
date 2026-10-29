#!/usr/bin/env python3
"""
Research: are in-game NFL underdogs underpriced? ("the 25c team in the 3rd quarter comes back more often
than 25%" — Noah's hypothesis: emotional bettors overreact to leads.)

Data: Kalshi KXNFLGAME (one market per team per game, YES = that team wins), every settled game Kalshi has
(current + historical endpoints, public, no keys), 1-minute candles of yes_bid / yes_ask / trade price.
Kickoff is parsed from the market rules ("originally scheduled for Oct 19, 2026 at 1:00 PM EDT").
Game phase is approximated by wall-clock minutes since kickoff (Q1 ~0-45, Q2 ~45-95 incl. 2-min warning,
halftime ~95-110, Q3 ~110-155, Q4 ~155-210); the live 15 s radar tape replaces this proxy going forward.

Tests (one entry per team per game per rule, so games are independent samples):
  A. calibration: in each phase, the FIRST minute a team's yes_ask is inside a price bucket -> did it win?
     win rate vs average price paid (+ taker fee) = edge; Wilson 95% lower bound so luck is not called edge.
  B. hail-mary hold: buy at the ask the first time it is <= P in phase X, hold to settlement.
  C. bounce: same entry, sell at the bid the first time it reaches entry + D (or 2x entry), else hold.
     "Almost came back" pays here even when the comeback fails.
Outputs: <out>/NFL.md (report), <out>/nfl_trades.csv (every simulated entry), <out>/cache/*.json (candles).

    python3 nfl_comeback.py --out mrp/research/nfl [--series KXNFLGAME] [--max-games 0]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import requests

BASE = os.environ.get("KALSHI_REST_URL", "https://external-api.kalshi.com") + "/trade-api/v2"
S = requests.Session()
S.headers["User-Agent"] = "mrp-research/0.1 (read-only)"
THETA = 0.07
PHASES = [("Q1", 0, 45), ("Q2", 45, 95), ("Q3", 110, 155), ("Q4 early", 155, 185), ("Q4 late", 185, 215)]
BUCKETS = [(0.05, 0.10), (0.10, 0.15), (0.15, 0.20), (0.20, 0.25), (0.25, 0.30), (0.30, 0.35), (0.35, 0.40), (0.40, 0.50)]
HOLD_P = [0.15, 0.20, 0.25, 0.30, 0.35]
BOUNCE_D = [0.10, 0.15, 0.20]
THETA_MAKER = 0.0175            # resting sell orders: Kalshi maker fee (conservative; 0 on many series)
LEVELS = [round(0.05 * i, 2) for i in range(1, 20)]          # 0.05 .. 0.95 absolute sell prices
LADDERS = {                                                    # name -> weights per 10c step above entry, up to 0.90
    "heavy-low": lambda k: [k - i for i in range(k)],            # 7,6,5,...,1
    "equal": lambda k: [1] * k,
    "halving": lambda k: [2 ** (k - i) for i in range(k)],       # 64,32,...,1
    "heavy-high": lambda k: [i + 1 for i in range(k)],
}
_last = [0.0]


def get(path: str, params: Optional[dict] = None, tries: int = 4) -> Any:
    for i in range(tries):
        wait = 0.12 - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            r = S.get(BASE + path, params=params, timeout=30)
        except requests.RequestException:
            time.sleep(2 * (i + 1))
            continue
        if r.status_code == 200:
            return r.json()
        if r.status_code == 404:
            return None
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(2 * (i + 1))
            continue
        print(f"  {path} {params} -> {r.status_code} {r.text[:150]}", file=sys.stderr)
        return None
    return None


def paged(path: str, params: dict, key: str = "markets", max_pages: int = 50) -> list:
    out, cursor = [], ""
    for _ in range(max_pages):
        data = get(path, dict(params, cursor=cursor)) or {}
        items = data.get(key) or []
        out.extend(items)
        cursor = data.get("cursor") or ""
        if not cursor or not items:
            break
    return out


TZ = {"EDT": -4, "EST": -5, "CDT": -5, "CST": -6, "MDT": -6, "MST": -7, "PDT": -7, "PST": -8, "ET": -5, "UTC": 0, "GMT": 0, "BST": 1}


def kickoff(m: dict) -> Optional[float]:
    txt = " ".join(str(m.get(k) or "") for k in ("rules_primary", "rules_secondary", "title"))
    mm = re.search(r"([A-Z][a-z]{2,8})\.? (\d{1,2}), (\d{4}) at (\d{1,2})(?::(\d\d))? ?([AP]M) ?([A-Z]{2,3})", txt)
    if not mm:
        return None
    mon, day, yr, hh, mi, ap, tz = mm.groups()
    try:
        d = datetime.strptime(f"{mon[:3]} {day} {yr}", "%b %d %Y")
    except ValueError:
        return None
    h = int(hh) % 12 + (12 if ap == "PM" else 0)
    off = TZ.get(tz, -5)
    return (d.replace(hour=h, minute=int(mi or 0), tzinfo=timezone(timedelta(hours=off)))).timestamp()


def px_hi(o: Any) -> Optional[float]:
    if isinstance(o, dict):
        for k in ("high", "high_dollars"):
            if o.get(k) is not None:
                return px(o[k])
    return None


def px(o: Any) -> Optional[float]:
    if o is None:
        return None
    if isinstance(o, dict):
        for k in ("close", "close_dollars", "close_price"):
            if o.get(k) is not None:
                return px(o[k])
        return None
    try:
        v = float(o)
    except (TypeError, ValueError):
        return None
    return v / 100.0 if v > 1.5 else v


def candles(ticker: str, series: str, t0: int, t1: int, cache_dir: str) -> list[dict]:
    path = os.path.join(cache_dir, f"{ticker}.v2.json")
    if os.path.exists(path):
        with open(path) as fh:
            return json.load(fh)
    out = []
    for p, q in ((f"/historical/markets/{ticker}/candlesticks", None), (f"/series/{series}/markets/{ticker}/candlesticks", None)):
        data = get(p, {"start_ts": t0, "end_ts": t1, "period_interval": 1})
        cs = (data or {}).get("candlesticks") or []
        if cs:
            for c in cs:
                out.append({"t": int(c.get("end_period_ts") or 0), "b": px(c.get("yes_bid")), "a": px(c.get("yes_ask")),
                            "bh": px_hi(c.get("yes_bid")),
                            "p": px(c.get("price")), "v": float(c.get("volume") or c.get("volume_fp") or 0)})
            break
    out.sort(key=lambda x: x["t"])
    with open(path, "w") as fh:
        json.dump(out, fh, separators=(",", ":"))
    return out


def fee_m(p: float) -> float:
    return THETA_MAKER * p * (1 - p)


def fee(p: float) -> float:
    return THETA * p * (1 - p)


def wilson_lo(k: int, n: int, z: float = 1.96) -> float:
    if n == 0:
        return 0.0
    ph = k / n
    return (ph + z * z / (2 * n) - z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n))) / (1 + z * z / n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="mrp/research/nfl")
    ap.add_argument("--series", default="KXNFLGAME")
    ap.add_argument("--max-games", type=int, default=0)
    a = ap.parse_args()
    cache = os.path.join(a.out, "cache")
    os.makedirs(cache, exist_ok=True)

    ms = paged("/markets", {"series_ticker": a.series, "status": "settled", "limit": 1000, "mve_filter": "exclude"})
    ms += paged("/historical/markets", {"series_ticker": a.series, "limit": 1000, "mve_filter": "exclude"})
    seen, markets = set(), []
    for m in ms:
        if m.get("ticker") in seen or m.get("result") not in ("yes", "no"):
            continue
        seen.add(m["ticker"])
        markets.append(m)
    print(f"{len(markets)} settled team-markets in {a.series}", file=sys.stderr)
    games = defaultdict(list)
    for m in markets:
        games[m.get("event_ticker")].append(m)
    gkeys = sorted(games)
    if a.max_games:
        gkeys = gkeys[-a.max_games:]

    trades = []          # every simulated entry
    calib = defaultdict(lambda: [0, 0, 0.0])     # (phase, bucket) -> [n, wins, sum entry]
    no_kick = no_candles = used = 0
    for gi, ek in enumerate(gkeys):
        for m in games[ek]:
            ko = kickoff(m)
            if not ko:
                no_kick += 1
                continue
            cs = candles(m["ticker"], a.series, int(ko - 1800), int(ko + 5 * 3600), cache)
            if len(cs) < 30:
                no_candles += 1
                continue
            used += 1
            won = 1 if m["result"] == "yes" else 0
            team = m.get("yes_sub_title") or m["ticker"].rsplit("-", 1)[-1]
            series = [(int((c["t"] - ko) // 60), c) for c in cs]
            # A. calibration: first minute in each (phase, bucket)
            for ph, lo, hi in PHASES:
                hit = set()
                for mn, c in series:
                    if not (lo <= mn < hi) or c["a"] is None or not (0 < c["a"] < 1):
                        continue
                    for b in BUCKETS:
                        if b not in hit and b[0] <= c["a"] < b[1]:
                            hit.add(b)
                            d = calib[(ph, b)]
                            d[0] += 1; d[1] += won; d[2] += c["a"]
            # B/C. hold and bounce strategies
            for ph, lo, hi in PHASES:
                for P in HOLD_P:
                    entry = None
                    for i, (mn, c) in enumerate(series):
                        if lo <= mn < hi and c["a"] is not None and 0 < c["a"] <= P and (c["b"] or 0) > 0:
                            entry = (i, mn, c["a"])
                            break
                    if not entry:
                        continue
                    i0, mn0, e = entry
                    pnl_hold = won - e - fee(e)
                    row = {"game": ek, "team": team, "phase": ph, "P": P, "entry_min": mn0, "entry": e, "won": won,
                           "pnl_hold": round(pnl_hold, 4)}
                    for D in BOUNCE_D + ["x2"]:
                        tgt = 2 * e if D == "x2" else e + D
                        exit_px = None
                        for mn, c in series[i0 + 1:]:
                            if c["b"] is not None and c["b"] >= tgt:
                                exit_px = c["b"]
                                break
                        if exit_px is not None:
                            pnl = exit_px - e - fee(e) - fee(exit_px)
                        else:
                            pnl = pnl_hold
                        row[f"pnl_b{D}"] = round(pnl, 4)
                        row[f"hit_b{D}"] = int(exit_px is not None)
                    # sell-limit study: highest bid reached after entry (a resting sell at L fills if bid >= L)
                    hi = max([(c.get("bh") or c.get("b") or 0) for _, c in series[i0 + 1:]] or [0])
                    row["max_bid_after"] = round(hi, 3)
                    for L in LEVELS:
                        if L > e:
                            row[f"L{L:.2f}"] = round((L - fee_m(L)) if hi >= L else won, 4) - e - fee(e)
                    steps = [round(e + 0.10 * (j + 1), 2) for j in range(20) if e + 0.10 * (j + 1) <= 0.905]
                    for lname, wf in LADDERS.items():
                        if not steps:
                            row[f"lad_{lname}"] = row["pnl_hold"]
                            continue
                        w = wf(len(steps)); tw = sum(w)
                        val = sum(wi / tw * ((L - fee_m(L)) if hi >= L else won) for wi, L in zip(w, steps))
                        row[f"lad_{lname}"] = round(val - e - fee(e), 4)
                    trades.append(row)
        if gi % 20 == 0:
            print(f"  {gi}/{len(gkeys)} games, {used} team-markets used", file=sys.stderr)

    with open(os.path.join(a.out, "nfl_trades.csv"), "w", newline="") as fh:
        if trades:
            cols = list(dict.fromkeys(k for t in trades for k in t))
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader(); w.writerows(trades)

    L = []
    L.append(f"# NFL in-game underdog study ({a.series})\n")
    L.append(f"Updated {datetime.now(timezone.utc):%Y-%m-%d %H:%MZ}. {len(gkeys)} games, {used} team-markets with 1-min candles "
             f"(skipped: {no_kick} no kickoff time, {no_candles} no candles). Buying at the ask, Kalshi taker fee 0.07·p·(1−p). "
             "Phase = minutes since scheduled kickoff (proxy). One entry per team per game per rule.\n")
    L.append("## A. Calibration — does a team priced X actually win X% of the time?\n")
    L.append("| phase | ask bucket | n | avg paid | win rate | 95% low | edge/contract (after fee) |\n|---|---|---|---|---|---|---|")
    for ph, _, _ in PHASES:
        for b in BUCKETS:
            n, k, s = calib[(ph, b)]
            if n < 5:
                continue
            avg = s / n
            edge = k / n - avg - fee(avg)
            L.append(f"| {ph} | {b[0]:.2f}–{b[1]:.2f} | {n} | {avg:.3f} | {k / n:.3f} | {wilson_lo(k, n):.3f} | {edge:+.3f} |")
    L.append("\nEdge is real only where the **95% low** win rate is above avg paid + fee. Positive edge with a low bound below the price = not proven yet.\n")
    L.append("## B/C. Strategies — buy the first time the ask is ≤ P in the phase\n")
    L.append("| phase | P | n | win% | hold: avg P&L/contract | bounce +10c | +15c | +20c | double | hit% (+15c) | worst-10 sum |\n|---|---|---|---|---|---|---|---|---|---|---|")
    grp = defaultdict(list)
    for t in trades:
        grp[(t["phase"], t["P"])].append(t)
    for ph, _, _ in PHASES:
        for P in HOLD_P:
            ts = grp.get((ph, P), [])
            if len(ts) < 5:
                continue
            n = len(ts)
            avg = lambda k: sum(t[k] for t in ts) / n
            worst = sum(sorted(t["pnl_hold"] for t in ts)[:10])
            L.append(f"| {ph} | {P:.2f} | {n} | {100 * sum(t['won'] for t in ts) / n:.0f}% | {avg('pnl_hold'):+.3f} | {avg('pnl_b0.1'):+.3f} | "
                     f"{avg('pnl_b0.15'):+.3f} | {avg('pnl_b0.2'):+.3f} | {avg('pnl_bx2'):+.3f} | {100 * avg('hit_b0.15'):.0f}% | {worst:+.2f} |")
    L.append("\nP&L is per $1 contract. A +0.03 average on 25c entries is +12% per trade. Bounce columns sell at the bid the "
             "first time it reaches the target and otherwise hold to the final whistle.\n")
    L.append("## D. Sell limits — place a resting sell right after buying\n")
    L.append("Each cell: average P&L per contract if the whole position rests one sell at that price (unfilled -> held to the final "
             "whistle). The best level is the most profitable single exit; a ladder spreads across levels to smooth results.\n")
    for ph, _, _ in PHASES:
        for P in (0.20, 0.25, 0.30):
            ts = grp.get((ph, P), [])
            if len(ts) < 10:
                continue
            cells = []
            for Lv in LEVELS:
                k = f"L{Lv:.2f}"
                vals = [t[k] for t in ts if k in t]
                if len(vals) >= 10:
                    fill = sum(1 for t in ts if k in t and t["max_bid_after"] >= Lv) / len(vals)
                    cells.append(f"{Lv:.2f}: {sum(vals) / len(vals):+.3f} ({100 * fill:.0f}% fill)")
            best = max(cells, key=lambda c: float(c.split(": ")[1].split(" ")[0])) if cells else "-"
            L.append(f"- **{ph}, entry ≤ {P:.2f}** (n={len(ts)}): best single exit {best}")
            L.append("  - " + " · ".join(cells[:10]))
            lad = " · ".join(f"{nm} {sum(t['lad_' + nm] for t in ts) / len(ts):+.3f}" for nm in LADDERS)
            hold = sum(t["pnl_hold"] for t in ts) / len(ts)
            L.append(f"  - ladders (10c steps to 0.90): {lad} · hold {hold:+.3f}")
    L.append("")
    with open(os.path.join(a.out, "NFL.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
