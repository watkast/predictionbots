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
import bisect
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
PHASES = [("pre", -30, 0), ("Q1", 0, 45), ("Q2", 45, 95), ("Q3", 110, 155), ("Q4 early", 155, 185), ("Q4 late", 185, 215)]
DEFICITS = [(-99, -17), (-16, -9), (-8, -4), (-3, -1), (0, 0), (1, 99)]      # team score minus opponent
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


ESPN = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
ALIAS = {"LA": "LAR", "JAC": "JAX", "WSH": "WAS", "LVR": "LV", "OAK": "LV", "SD": "LAC", "GNB": "GB", "KAN": "KC", "NWE": "NE",
         "NOR": "NO", "SFO": "SF", "TAM": "TB"}
MONTHS = {m: i for i, m in enumerate(("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"), 1)}


def espn_get(url: str, cache_path: str) -> Any:
    if os.path.exists(cache_path):
        with open(cache_path) as fh:
            return json.load(fh)
    for i in range(3):
        try:
            r = S.get(url, timeout=30)
            if r.status_code == 200:
                data = r.json()
                with open(cache_path, "w") as fh:
                    json.dump(data, fh, separators=(",", ":"))
                return data
        except requests.RequestException:
            pass
        time.sleep(2 * (i + 1))
    return None


def espn_game(event_ticker: str, codes: list[str], cache: str) -> Optional[dict]:
    """Find the ESPN game for a Kalshi NFL event (date in the ticker + team codes); return kickoff, home/away
    abbreviations and the play-by-play state timeline [(ts, period, clock_s, home, away)]."""
    m = re.match(r"[A-Z0-9]+-(\d\d)([A-Z]{3})(\d\d)", event_ticker)
    if not m or m.group(2) not in MONTHS:
        return None
    d0 = datetime(2000 + int(m.group(1)), MONTHS[m.group(2)], int(m.group(3)))
    want = {ALIAS.get(c, c) for c in codes}
    for dd in (0, -1, 1):
        day = (d0 + timedelta(days=dd)).strftime("%Y%m%d")
        sb = espn_get(f"{ESPN}/scoreboard?dates={day}", os.path.join(cache, f"espn_sb_{day}.json")) or {}
        for ev in sb.get("events") or []:
            comp = (ev.get("competitions") or [{}])[0]
            teams = {c.get("homeAway"): (c.get("team") or {}).get("abbreviation") for c in comp.get("competitors") or []}
            if set(teams.values()) != want:
                continue
            ko = datetime.fromisoformat(str(ev.get("date")).replace("Z", "+00:00")).timestamp()
            summ = espn_get(f"{ESPN}/summary?event={ev['id']}", os.path.join(cache, f"espn_sum_{ev['id']}.json")) or {}
            tl = []
            for dr in ((summ.get("drives") or {}).get("previous") or []):
                for pl in dr.get("plays") or []:
                    wc = pl.get("wallclock")
                    if not wc:
                        continue
                    try:
                        ts = datetime.fromisoformat(wc.replace("Z", "+00:00")).timestamp()
                    except ValueError:
                        continue
                    clk = str((pl.get("clock") or {}).get("displayValue") or "0:00")
                    mm_ = re.match(r"(\d+):(\d+)", clk)
                    cs = int(mm_.group(1)) * 60 + int(mm_.group(2)) if mm_ else 0
                    tl.append((ts, int((pl.get("period") or {}).get("number") or 0), cs,
                               int(pl.get("homeScore") or 0), int(pl.get("awayScore") or 0)))
            tl.sort()
            scores, prev = [], (0, 0)
            for ts, per, cs, hs, as_ in tl:
                if (hs, as_) != prev:
                    scores.append((ts, per, cs, hs - prev[0], as_ - prev[1]))
                    prev = (hs, as_)
            return {"ko": ko, "home": teams.get("home"), "away": teams.get("away"), "tl": tl, "scores": scores}
    return None


def state_at(g: dict, t: float) -> Optional[tuple]:
    """(period, clock_s, home, away) of the last play at or before t."""
    tl = g["tl"]
    lo, hi = 0, len(tl)
    while lo < hi:
        mid = (lo + hi) // 2
        if tl[mid][0] <= t:
            lo = mid + 1
        else:
            hi = mid
    return tl[lo - 1][1:] if lo else None


def phase_of(period: int, clock_s: int) -> Optional[str]:
    if period == 1:
        return "Q1"
    if period == 2:
        return "Q2"
    if period == 3:
        return "Q3"
    if period == 4:
        return "Q4 early" if clock_s > 450 else "Q4 late"
    return "OT" if period >= 5 else None


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
    ms += paged("/historical/markets", {"series_ticker": a.series, "limit": 1000})
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
    state_cal = defaultdict(lambda: [0, 0, 0.0])    # (period, deficit bucket, price bucket) -> [n, wins, sum paid]
    season_cal = defaultdict(lambda: [0, 0, 0.0])   # (season, phase, bucket)
    fav_cal = defaultdict(lambda: [0, 0, 0.0])      # (period, pregame role, score state, coarse bucket)
    fav_season = defaultdict(lambda: [0, 0, 0.0])
    final2 = defaultdict(lambda: [0, 0, 0.0])          # H1: last 2:00 of Q4, bucket -> [n, wins, paid]
    halftime = []                                      # H2: (season, drift, q3 ask, won)
    team_bias = defaultdict(lambda: [0, 0.0, 0, 0.0])  # H3: team -> [n in-game samples, sum(won-ask-fee), n games pregame, sum(won-pre)]
    react = []                                         # H4: (game volume, absorbed@1, @2, @3, move size, season)
    blowout = defaultdict(lambda: [0, 0, 0.0])         # H5: (season, deficit band, price band) -> [n, wins, paid]
    seen_rule: set = set()
    rule_trades: list = []
    COARSE = [(0.05, 0.20), (0.20, 0.35), (0.35, 0.50), (0.50, 0.65), (0.65, 0.80), (0.80, 0.95)]
    espn_hits = 0
    for gi, ek in enumerate(gkeys):
        codes = [mm_["ticker"].rsplit("-", 1)[-1] for mm_ in games[ek]]
        g = espn_game(ek, codes, cache)
        espn_hits += 1 if g else 0
        for m in games[ek]:
            ko = g["ko"] if g else kickoff(m)
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
            kdt = datetime.fromtimestamp(ko, tz=timezone.utc)
            season = kdt.year if kdt.month >= 8 else kdt.year - 1
            pre = [c for mn, c in series if -30 <= mn < 0 and c["a"] is not None and c["b"] is not None and 0 < c["b"] <= c["a"] < 1]
            pre_mid = (pre[-1]["a"] + pre[-1]["b"]) / 2 if pre else None
            role = None if pre_mid is None else ("pregame fav" if pre_mid >= 0.5 else "pregame dog")
            code = ALIAS.get(m["ticker"].rsplit("-", 1)[-1], m["ticker"].rsplit("-", 1)[-1])
            if g and g["tl"] and code in (g["home"], g["away"]):
                is_home = code == g["home"]
                st_series = []
                for mn, c in series:
                    st = state_at(g, c["t"])
                    if st is None:
                        st_series.append((None, None, c))
                        continue
                    per, clk, hs, as_ = st
                    diff = (hs - as_) if is_home else (as_ - hs)
                    st_series.append((phase_of(per, clk), (per, clk, diff), c))
                # state calibration: first minute in each (period, deficit, price) cell
                seen_cells = set()
                for ph_, st, c in st_series:
                    if st is None or c["a"] is None or not (0 < c["a"] < 1):
                        continue
                    per, clk, diff = st
                    db = next((d for d in DEFICITS if d[0] <= diff <= d[1]), None)
                    pb = next((b for b in BUCKETS if b[0] <= c["a"] < b[1]), None)
                    if db is None or pb is None or per > 4:
                        continue
                    cell = (per, db, pb)
                    if cell not in seen_cells:
                        seen_cells.add(cell)
                        sc = state_cal[cell]
                        sc[0] += 1; sc[1] += won; sc[2] += c["a"]
                    cb = next((b for b in COARSE if b[0] <= c["a"] < b[1]), None)
                    if role and cb:
                        ss = "trailing" if diff < 0 else ("tied" if diff == 0 else "leading")
                        fcell = (per, role, ss, cb)
                        if fcell not in seen_cells:
                            seen_cells.add(fcell)
                            fc = fav_cal[fcell]
                            fc[0] += 1; fc[1] += won; fc[2] += c["a"]
                            fs = fav_season[(season,) + fcell]
                            fs[0] += 1; fs[1] += won; fs[2] += c["a"]
                        # the anchoring rule as a strategy: first time in Q2-Q3 the pregame favourite trails and is
                        # priced 35-50c -> (for the favourite's own market) record; underdog side handled via its market
                        if per in (2, 3) and role == "pregame dog" and ss == "leading" and 0.35 <= c["a"] < 0.65 \
                                and ("anchor", ek) not in seen_rule:
                            seen_rule.add(("anchor", ek))
                            rule_trades.append({"season": season, "game": ek, "q": per, "entry": c["a"], "won": won,
                                                "pnl": won - c["a"] - fee(c["a"])})
                # H1 final two minutes / H5 blowouts / H3 in-game team bias samples
                f2_seen, bo_seen, last_tb = set(), set(), -999
                for ph_, st, c in st_series:
                    if st is None or c["a"] is None or not (0 < c["a"] < 1):
                        continue
                    per, clk, diff = st
                    if per == 4 and clk <= 120:
                        pb = next((b for b in BUCKETS if b[0] <= c["a"] < b[1]), None)
                        if pb and pb not in f2_seen:
                            f2_seen.add(pb); d_ = final2[pb]; d_[0] += 1; d_[1] += won; d_[2] += c["a"]
                    if per in (2, 3) and c["a"] < 0.20 and diff <= -10:
                        band = ("<=-17" if diff <= -17 else "-16..-10", "<0.10" if c["a"] < 0.10 else "0.10-0.20")
                        if band not in bo_seen:
                            bo_seen.add(band); d_ = blowout[(season,) + band]; d_[0] += 1; d_[1] += won; d_[2] += c["a"]
                    if 1 <= per <= 4 and c["t"] - last_tb >= 900:
                        last_tb = c["t"]; tb = team_bias[code]; tb[0] += 1; tb[1] += won - c["a"] - fee(c["a"])
                if pre_mid is not None:
                    tb = team_bias[code]; tb[2] += 1; tb[3] += won - pre_mid
                # H2 halftime drift: last Q2 minute vs first Q3 minute
                q2 = [c for ph_, st, c in st_series if st and st[0] == 2 and c["a"] and c["b"]]
                q3 = [c for ph_, st, c in st_series if st and st[0] == 3 and c["a"] and c["b"]]
                if q2 and q3:
                    m2 = (q2[-1]["a"] + q2[-1]["b"]) / 2; m3 = (q3[0]["a"] + q3[0]["b"]) / 2
                    halftime.append((season, m3 - m2, q3[0]["a"], won))
                # H4 repricing latency after scores (home market only, so each score counts once)
                if is_home and g.get("scores"):
                    vol = sum(c.get("v") or 0 for _, c in series if 0 <= _ <= 240)
                    ct = [c["t"] for _, c in series]
                    mids = [((c["a"] + c["b"]) / 2 if c["a"] and c["b"] else None) for _, c in series]
                    def mid_at(t):
                        i = bisect.bisect_right(ct, t) - 1
                        return mids[i] if 0 <= i < len(mids) else None
                    for ts, per, cs_, dh, da in g["scores"]:
                        p0, p1, p2, p3, p5 = (mid_at(ts - 60), mid_at(ts + 60), mid_at(ts + 120), mid_at(ts + 180), mid_at(ts + 300))
                        if None in (p0, p1, p2, p3, p5) or abs(p5 - p0) < 0.03:
                            continue
                        mv = p5 - p0
                        react.append((vol, (p1 - p0) / mv, (p2 - p0) / mv, (p3 - p0) / mv, abs(mv), season))
                # real phases replace the wall-clock proxy
                series_ph = [(ph_ or "pre", c) for ph_, st, c in st_series]
            else:
                series_ph = None
            # A. calibration: first minute in each (phase, bucket)
            def in_phase(idx, ph, lo, hi):
                if series_ph is not None:
                    return series_ph[idx][0] == ph
                return lo <= series[idx][0] < hi
            for ph, lo, hi in PHASES:
                hit = set()
                for idx, (mn, c) in enumerate(series):
                    if not in_phase(idx, ph, lo, hi) or c["a"] is None or not (0 < c["a"] < 1):
                        continue
                    for b in BUCKETS:
                        if b not in hit and b[0] <= c["a"] < b[1]:
                            hit.add(b)
                            d = calib[(ph, b)]
                            d[0] += 1; d[1] += won; d[2] += c["a"]
                            d2 = season_cal[(season, ph, b)]
                            d2[0] += 1; d2[1] += won; d2[2] += c["a"]
            # B/C. hold and bounce strategies
            for ph, lo, hi in PHASES:
                for P in HOLD_P:
                    entry = None
                    for i, (mn, c) in enumerate(series):
                        if in_phase(i, ph, lo, hi) and c["a"] is not None and 0 < c["a"] <= P and (c["b"] or 0) > 0:
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
             f"(skipped: {no_kick} no kickoff time, {no_candles} no candles). ESPN play-by-play matched for {espn_hits} games: "
             "their phases come from the real quarter and clock (Q4 late = under 7:30 left); others use minutes since kickoff. "
             "Buying at the ask, Kalshi taker fee 0.07·p·(1−p). One entry per team per game per rule.\n")
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
    L.append("## A2. Game state — team trailing by X in quarter Q, priced in bucket B: how often does it win?\n")
    L.append("| quarter | score diff | ask bucket | n | avg paid | win rate | 95% low | edge (after fee) |\n|---|---|---|---|---|---|---|---|")
    for (per, db, pb), (n, k, sp) in sorted(state_cal.items()):
        if n < 8:
            continue
        avg = sp / n
        dl = f"{db[0]}..{db[1]}" if db[0] != db[1] else "tied"
        L.append(f"| Q{per} | {dl} | {pb[0]:.2f}–{pb[1]:.2f} | {n} | {avg:.3f} | {k / n:.3f} | {wilson_lo(k, n):.3f} | {k / n - avg - fee(avg):+.3f} |")
    L.append("")
    L.append("## A3. Pregame favourite vs underdog, by in-game score state (anchoring test)\n")
    L.append("Role = which side the market favoured in the 30 min before kickoff. If bettors anchor on the pregame favourite, "
             "trailing favourites are overpriced (negative edge) and leading underdogs underpriced (positive edge).\n")
    L.append("| quarter | pregame role | score | ask | n | avg paid | win rate | 95% low | edge |\n|---|---|---|---|---|---|---|---|---|")
    for (per, role, ss, cb), (n, k, sp) in sorted(fav_cal.items()):
        if n < 15:
            continue
        avg = sp / n
        L.append(f"| Q{per} | {role} | {ss} | {cb[0]:.2f}–{cb[1]:.2f} | {n} | {avg:.3f} | {k / n:.3f} | {wilson_lo(k, n):.3f} | {k / n - avg - fee(avg):+.3f} |")
    L.append("")
    L.append("### A3 by season (anchoring cells only)\n")
    L.append("| quarter | pregame role | score | ask | " + " | ".join(f"{yr} n / win / paid / edge" for yr in sorted({k[0] for k in fav_season})) + " |")
    L.append("|---|---|---|---|" + "---|" * len({k[0] for k in fav_season}))
    for (per, role, ss, cb) in sorted(fav_cal):
        if not ((role == "pregame fav" and ss == "trailing") or (role == "pregame dog" and ss == "leading")) or cb[0] < 0.35 or cb[0] > 0.50:
            continue
        cells = []
        for yr in sorted({k[0] for k in fav_season}):
            n, k, sp = fav_season.get((yr, per, role, ss, cb), [0, 0, 0.0])
            cells.append(f"{n} / {k / n:.3f} / {sp / n:.3f} / {k / n - sp / n - fee(sp / n):+.3f}" if n >= 10 else f"{n} / -")
        L.append(f"| Q{per} | {role} | {ss} | {cb[0]:.2f}–{cb[1]:.2f} | " + " | ".join(cells) + " |")
    if rule_trades:
        L.append("\n### Anchoring rule as a strategy\n")
        L.append("Rule: the first time in Q2 or Q3 that the pregame underdog is LEADING and its ask is 35-65c, buy it at the ask and hold. "
                 "One trade per game.\n")
        L.append("| season | trades | win% | avg entry | avg P&L / contract | ROI | worst 10-trade run | weeks | trades / week |\n|---|---|---|---|---|---|---|---|---|")
        for yr in sorted({t["season"] for t in rule_trades}) + ["all"]:
            ts = [t for t in rule_trades if yr == "all" or t["season"] == yr]
            ts.sort(key=lambda t: t["game"])
            n = len(ts); pn = [t["pnl"] for t in ts]
            worst = min(sum(pn[i:i + 10]) for i in range(max(1, n - 9))) if n >= 10 else sum(pn)
            weeks = max(1, len({t["game"].split("-")[1][:7] for t in ts}) / 3)
            avg_e = sum(t["entry"] for t in ts) / n
            L.append(f"| {yr} | {n} | {100 * sum(t['won'] for t in ts) / n:.0f}% | {avg_e:.3f} | {sum(pn) / n:+.3f} | "
                     f"{100 * sum(pn) / n / avg_e:+.0f}% | {worst:+.2f} | {weeks:.0f} | {n / weeks:.1f} |")
    L.append("")
    L.append("## H. Hypotheses from the forced-spend exercise\n")
    L.append("### H1. Forced sellers — last 2:00 of the 4th quarter (does the deadline push prices below the truth?)\n")
    L.append("| ask bucket | n | avg paid | win rate | 95% low | edge |\n|---|---|---|---|---|---|")
    for b in BUCKETS:
        n, k, sp = final2[b]
        if n >= 8:
            L.append(f"| {b[0]:.2f}–{b[1]:.2f} | {n} | {sp / n:.3f} | {k / n:.3f} | {wilson_lo(k, n):.3f} | {k / n - sp / n - fee(sp / n):+.3f} |")
    L.append("\n### H2. Halftime drift — nothing happens on the field; does the price move mean-revert?\n")
    L.append("| halftime drift | n | avg Q3-start ask | win rate | edge buying at Q3 start |\n|---|---|---|---|---|")
    for lab, lo, hi in (("fell > 3c", -9, -0.03), ("flat ±3c", -0.03, 0.03), ("rose > 3c", 0.03, 9)):
        xs = [h for h in halftime if lo <= h[1] < hi and 0 < h[2] < 1]
        if len(xs) >= 10:
            n = len(xs); k = sum(h[3] for h in xs); ap = sum(h[2] for h in xs) / n
            L.append(f"| {lab} | {n} | {ap:.3f} | {k / n:.3f} | {sum(h[3] - h[2] - fee(h[2]) for h in xs) / n:+.3f} |")
    L.append("\n### H3. Team bias — popular teams overpriced? (in-game samples every 15 min; pregame mid)\n")
    L.append("| team | in-game samples | in-game edge | games | pregame edge (won − pregame mid) |\n|---|---|---|---|---|")
    tb_rows = sorted(((t, v) for t, v in team_bias.items() if v[0] >= 20), key=lambda kv: kv[1][1] / kv[1][0])
    for t, (n, se, ng, sp) in tb_rows[:8] + [("…", (0, 0, 0, 0))] + tb_rows[-8:]:
        if t == "…":
            L.append("| … | | | | |"); continue
        L.append(f"| {t} | {n} | {se / n:+.3f} | {ng} | {(sp / ng if ng else 0):+.3f} |")
    L.append("\nNegative = the market overpays for that team. ~30 teams × noise: only trust large, consistent gaps.\n")
    L.append("### H4. Repricing speed after a score (share of the 5-minute move already in the price)\n")
    if react:
        vs = sorted(r[0] for r in react); t1, t2 = vs[len(vs) // 3], vs[2 * len(vs) // 3]
        L.append("| game attention (Kalshi volume tercile) | scores | median absorbed +1 min | +2 min | +3 min | share still < 50% at +1 min |\n|---|---|---|---|---|---|")
        for lab, lo, hi in (("low", -1, t1), ("mid", t1, t2), ("high", t2, 1e18)):
            xs = [r for r in react if lo < r[0] <= hi]
            if xs:
                med = lambda i: sorted(x[i] for x in xs)[len(xs) // 2]
                L.append(f"| {lab} | {len(xs)} | {100 * med(1):.0f}% | {100 * med(2):.0f}% | {100 * med(3):.0f}% | {100 * sum(1 for x in xs if x[1] < 0.5) / len(xs):.0f}% |")
        L.append("\nMinute candles + ESPN wallclock (play start, can lag the snap): a coarse first look. If low-attention games "
                 "absorb < 50% in the first minute, a fast score feed has an edge there; the live 15 s radar tape measures it properly.\n")
    L.append("### H5. Blowout overreaction — trailing by 10+ in Q2/Q3 and priced under 20c (the curling shot)\n")
    L.append("| season | deficit | ask | n | avg paid | win rate | 95% low | payoff multiple (win/paid) |\n|---|---|---|---|---|---|---|---|")
    for key in sorted(blowout):
        n, k, sp = blowout[key]
        if n >= 5:
            L.append(f"| {key[0]} | {key[1]} | {key[2]} | {n} | {sp / n:.3f} | {k / n:.3f} | {wilson_lo(k, n):.3f} | {(k / n) / (sp / n):.2f}x |")
    L.append("")
    L.append("## A4. Out-of-sample check — calibration edge by season (same cells, split)\n")
    L.append("An edge that is real should show in BOTH seasons. One season positive and the other flat = likely noise.\n")
    L.append("| phase | ask bucket | " + " | ".join(f"{yr} n / edge" for yr in sorted({k[0] for k in season_cal})) + " |")
    L.append("|---|---|" + "---|" * len({k[0] for k in season_cal}))
    for ph, _, _ in PHASES:
        for b in BUCKETS:
            cells = []
            for yr in sorted({k[0] for k in season_cal}):
                n, k, sp = season_cal.get((yr, ph, b), [0, 0, 0.0])
                cells.append(f"{n} / {k / n - sp / n - fee(sp / n):+.3f}" if n >= 10 else f"{n} / -")
            L.append(f"| {ph} | {b[0]:.2f}–{b[1]:.2f} | " + " | ".join(cells) + " |")
    L.append("\n" + f"Note: about {sum(1 for v in calib.values() if v[0] >= 5) + sum(1 for v in state_cal.values() if v[0] >= 8)} cells are tested; "
             "at 95% confidence ~5% of them look significant by chance. Trust only patterns that repeat across neighbouring cells AND both seasons.\n")
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
