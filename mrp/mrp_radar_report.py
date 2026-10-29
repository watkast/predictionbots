#!/usr/bin/env python3
"""
Mr. P — sports radar report. Reads the radar's sp.* records (JSONL / .jsonl.gz, recursively) and prints
a markdown report: catalogue inventory, every opportunity kind with margin / persistence / confirmation,
settlement and close latency by sport, and a participant fingerprint (human vs bot tells) per sport.

    python3 mrp_radar_report.py <data root> [--days 7] [--top 25]
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mrp_recorder import parse_ts  # noqa: E402


def load(root: str, days: float):
    since = (time.time() - days * 86400) * 1000
    files = sorted(glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True)
                   + glob.glob(os.path.join(root, "**", "*.jsonl.gz"), recursive=True))
    for path in files:
        opener = gzip.open if path.endswith(".gz") else open
        try:
            with opener(path, "rt", encoding="utf-8") as fh:
                for line in fh:
                    try:
                        r = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if r.get("t", 0) >= since and str(r.get("k", "")).startswith(("sp.", "err")):
                        yield r
        except (OSError, EOFError):
            continue


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def pct(xs, q):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    return xs[min(len(xs) - 1, int(q * (len(xs) - 1)))]


def fmt(x, nd=3):
    if x is None:
        return "-"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--days", type=float, default=7)
    ap.add_argument("--top", type=int, default=25)
    a = ap.parse_args()

    n = 0
    t_min = t_max = None
    inventories, starts, errs = [], [], defaultdict(int)
    opps: dict[str, dict] = {}                       # key -> {kind, hits, max_margin, max_persist, confirmed, last}
    pm_closed = defaultdict(list)                    # sport -> [close latency s]
    k_settled: dict[str, dict] = {}                  # ticker -> record
    pm_snaps = defaultdict(list)                     # (sport, market slug) -> [(t, bid, ask, score, live)]
    k_snaps = defaultdict(list)                      # (series, ticker) -> [(t, yb, ya, ybq, yaq, status)]
    samples = {}
    series_titles = {}
    matches = 0
    for r in load(a.root, a.days):
        n += 1
        t = r["t"]
        t_min = t if t_min is None or t < t_min else t_min
        t_max = t if t_max is None or t > t_max else t_max
        k, d = r["k"], r["d"]
        if k == "sp.inventory":
            inventories.append((t, d))
        elif k == "sp.start":
            starts.append(t)
        elif k == "err":
            errs[str(d.get("where"))] += 1
        elif k == "sp.opp":
            key = json.dumps({x: d.get(x) for x in ("kind", "event", "market", "pm_market", "k_market", "team", "dir", "type")}, sort_keys=True)
            o = opps.setdefault(key, {"kind": d["kind"], "hits": 0, "max_margin": None, "max_persist": 0, "confirmed": 0, "bbo_n": 0, "last": d})
            o["hits"] += 1
            o["last"] = d
            m = d.get("margin")
            if m is not None and (o["max_margin"] is None or m > o["max_margin"]):
                o["max_margin"] = m
            o["max_persist"] = max(o["max_persist"], d.get("persist_s") or 0)
            b = d.get("bbo")
            if b:
                o["bbo_n"] += 1
                bid, ask = b.get("bid"), b.get("ask")
                if (ask is not None and 0.03 < ask < 0.97) or (bid is not None and 0.03 < bid < 0.97):
                    o["confirmed"] += 1
        elif k == "sp.pm.closed":
            fin, cl = parse_ts(d.get("finished")), parse_ts(d.get("closedTime"))
            if fin and cl:
                pm_closed[d.get("sport") or "?"].append(cl - fin)
        elif k == "sp.k.settled":
            for m in d:
                if m.get("t"):
                    k_settled[m["t"]] = m
        elif k == "sp.pm.event":
            for m in d.get("markets") or []:
                pm_snaps[(d.get("sport") or "?", m.get("slug"))].append((t, m.get("bid"), m.get("ask"), d.get("score"), d.get("chg"), d.get("unch") or 0))
        elif k == "sp.k.market":
            k_snaps[(d.get("series"), d.get("t"))].append((t, d.get("yb"), d.get("ya"), d.get("ybq"), d.get("yaq"), d.get("status"), d.get("unch") or 0))
        elif k == "sp.k.series":
            for tk, s in (d.get("series") or {}).items():
                series_titles[tk] = s.get("title")
        elif k == "sp.sample":
            obj = d.get("event") or d.get("market") or {}
            samples[d.get("venue")] = sorted(obj.keys())[:60]
        elif k == "sp.match":
            matches += 1

    span = f"{datetime.fromtimestamp(t_min/1000, tz=timezone.utc):%Y-%m-%d %H:%M}Z → {datetime.fromtimestamp(t_max/1000, tz=timezone.utc):%H:%M}Z" if t_min else "no data"
    print(f"# Sports radar report\n\nrecords {n:,} | {span} | runs {len(starts)} | pairs matched {matches} | errors {dict(errs) or 'none'}\n")

    # ------------------------------------------------------------------ inventory
    if inventories:
        t_inv, inv = inventories[-1]
        print(f"## Catalogue (latest inventory, {datetime.fromtimestamp(t_inv/1000, tz=timezone.utc):%H:%M}Z)\n")
        print(f"Polymarket US sports events {inv.get('pm_events')} of {inv.get('pm_events_total')} active events; Kalshi near-term sports markets "
              f"{inv.get('k_markets')} in {inv.get('k_events')} events; calls so far {inv.get('calls')}; MB {inv.get('bytes')}\n")
        rows = sorted((inv.get("by") or {}).items(), key=lambda kv: -kv[1]["n"])
        print("| venue | sport / league / type | markets | two-sided | med spread | vol 24h |\n|---|---|---|---|---|---|")
        for key, d in rows[:60]:
            venue, rest = key.split("|", 1)
            ts = f"{100 * d['two_sided'] / d['n']:.0f}%" if d["n"] else "-"
            print(f"| {venue} | {rest.replace('|', ' / ')} | {d['n']} | {ts} | {fmt(d.get('med_spread'))} | {fmt(d.get('vol24'), 0)} |")
        print()

    # ------------------------------------------------------------------ opportunities
    print("## Opportunities\n")
    if not opps:
        print("none flagged yet\n")
    else:
        by_kind = defaultdict(list)
        for o in opps.values():
            by_kind[o["kind"]].append(o)
        print("| kind | distinct | hits | max margin $/contract | max persistence | fresh-BBO still open |\n|---|---|---|---|---|---|")
        for kind, os_ in sorted(by_kind.items()):
            mm = max((o["max_margin"] for o in os_ if o["max_margin"] is not None), default=None)
            mp = max(o["max_persist"] for o in os_)
            conf = sum(o["confirmed"] for o in os_)
            bb = sum(o["bbo_n"] for o in os_)
            print(f"| {kind} | {len(os_)} | {sum(o['hits'] for o in os_)} | {fmt(mm, 4)} | {mp // 60} min | {conf}/{bb} |")
        print("\nTop by persistence × hits:\n")
        ranked = sorted(opps.values(), key=lambda o: -(o["max_persist"] + 60 * o["hits"]))[: a.top]
        for o in ranked:
            d = o["last"]
            desc = d.get("title") or d.get("q") or d.get("pm_event") or d.get("event") or ""
            px = ""
            if d.get("bid") is not None or d.get("ask") is not None:
                px = f" bid {fmt(d.get('bid'), 2)} ask {fmt(d.get('ask'), 2)}"
            if d.get("sum_ask") is not None:
                px = f" Σask {fmt(d.get('sum_ask'))}"
            if d.get("sum_bid") is not None:
                px = f" Σbid {fmt(d.get('sum_bid'))}"
            if d.get("pm_bid") is not None or d.get("k_ask") is not None:
                px = f" pm {fmt(d.get('pm_bid'), 2)}/{fmt(d.get('pm_ask'), 2)} k {fmt(d.get('k_bid'), 2)}/{fmt(d.get('k_ask'), 2)} {d.get('dir') or ''}"
            bbo = d.get("bbo")
            bb = f" | fresh bbo {fmt(bbo.get('bid'), 2)}/{fmt(bbo.get('ask'), 2)} depth {bbo.get('bidDepth')}/{bbo.get('askDepth')}" if bbo else ""
            print(f"- **{o['kind']}** {d.get('sport') or ''} — {desc[:70]} —{px} | margin {fmt(o['max_margin'], 4)} | "
                  f"{o['max_persist'] // 60} min, {o['hits']} hits{bb} | score {d.get('score') or '-'} {d.get('period') or ''}")
        print()

    # ------------------------------------------------------------------ latency
    print("## Close / settlement latency (how clunky each venue is after the final whistle)\n")
    if pm_closed:
        print("Polymarket US: closedTime − finishedTimestamp per sport\n\n| sport | n | median | p90 |\n|---|---|---|---|")
        for sp, xs in sorted(pm_closed.items(), key=lambda kv: -len(kv[1])):
            print(f"| {sp} | {len(xs)} | {fmt(med(xs) / 60, 1)} min | {fmt(pct(xs, 0.9) / 60, 1)} min |")
        print()
    if k_settled:
        by_series = defaultdict(list)
        for m in k_settled.values():
            s, c, e = parse_ts(m.get("settled")), parse_ts(m.get("close")), parse_ts(m.get("exp"))
            if s and c:
                by_series[m.get("series")].append((s - c, (s - e) if e else None))
        print("Kalshi: settlement_ts − close_time per series (negative = settled before the scheduled close)\n\n| series | n | median | p90 |\n|---|---|---|---|")
        for s, xs in sorted(by_series.items(), key=lambda kv: -len(kv[1]))[:40]:
            a_ = [x[0] for x in xs]
            print(f"| {s} {series_titles.get(s, '')[:30]} | {len(xs)} | {fmt(med(a_) / 60, 1)} min | {fmt(pct(a_, 0.9) / 60, 1)} min |")
        print()
    if not pm_closed and not k_settled:
        print("no closed/settled records yet\n")

    # ------------------------------------------------------------------ fingerprints
    print("## Participant fingerprint (per sport; 60 s snapshots)\n")
    print("change% = share of scan cycles (60 s) where the best quote moved; react = median minutes from a score change to the "
          "next quote move (humans: slow, bursty, round sizes; bots: constant cadence, odd/constant sizes, instant reaction)\n")
    fp = defaultdict(lambda: {"mk": 0, "snaps": 0, "changes": 0, "pairs": 0, "spreads": [], "two": 0, "react": []})
    for (sport, slug), xs in pm_snaps.items():
        xs.sort(key=lambda x: x[0])
        d = fp[f"pm | {sport}"]
        d["mk"] += 1
        d["snaps"] += len(xs)
        prev = None
        pending_score = None
        for t, bid, ask, score, chg, unch in xs:
            if bid is not None and ask is not None:
                d["two"] += 1
                d["spreads"].append(ask - bid)
            if prev is not None and chg != "new":
                moved = (bid, ask) != (prev[1], prev[2])
                d["pairs"] += unch + (1 if moved or chg is True else 0)
                if moved:
                    d["changes"] += 1
                    if pending_score is not None:
                        d["react"].append((t - pending_score) / 60000)
                        pending_score = None
                if score != prev[3] and score is not None and prev[3] is not None and pending_score is None:
                    pending_score = t
            prev = (t, bid, ask, score)
    kfp = defaultdict(lambda: {"mk": 0, "snaps": 0, "changes": 0, "pairs": 0, "spreads": [], "two": 0, "round": 0, "sizes": 0, "sz": []})
    for (series, tk), xs in k_snaps.items():
        xs.sort(key=lambda x: x[0])
        d = kfp[f"k | {series} {series_titles.get(series, '')[:24]}"]
        d["mk"] += 1
        d["snaps"] += len(xs)
        prev = None
        for t, yb, ya, ybq, yaq, status, unch in xs:
            if status != "active":
                prev = None
                continue
            if yb is not None and ya is not None and 0 < yb < 1 and 0 < ya < 1:
                d["two"] += 1
                d["spreads"].append(ya - yb)
            for q in (ybq, yaq):
                if q:
                    d["sizes"] += 1
                    d["sz"].append(q)
                    if q % 10 == 0:
                        d["round"] += 1
            if prev is not None:
                moved = (yb, ya) != prev
                d["pairs"] += unch + (1 if moved else 0)
                if moved:
                    d["changes"] += 1
            prev = (yb, ya)
    print("| venue | sport | markets | snapshots | two-sided | med spread | change% | react (min) | round sizes | med size |\n|---|---|---|---|---|---|---|---|---|---|")
    for key, d in sorted(fp.items(), key=lambda kv: -kv[1]["snaps"])[:30]:
        venue, sport = key.split(" | ", 1)
        print(f"| {venue} | {sport} | {d['mk']} | {d['snaps']} | {100 * d['two'] / max(1, d['snaps']):.0f}% | {fmt(med(d['spreads']))} | "
              f"{100 * d['changes'] / max(1, d['pairs']):.0f}% | {fmt(med(d['react']), 1)} (n={len(d['react'])}) | - | - |")
    for key, d in sorted(kfp.items(), key=lambda kv: -kv[1]["snaps"])[:40]:
        venue, sport = key.split(" | ", 1)
        print(f"| {venue} | {sport} | {d['mk']} | {d['snaps']} | {100 * d['two'] / max(1, d['snaps']):.0f}% | {fmt(med(d['spreads']))} | "
              f"{100 * d['changes'] / max(1, d['pairs']):.0f}% | - | {100 * d['round'] / max(1, d['sizes']):.0f}% | {fmt(med(d['sz']), 0)} |")
    print()
    if samples:
        print("## Schema notes (raw keys seen)\n")
        for v, keys in samples.items():
            print(f"- {v}: {', '.join(keys)}")
        print()


if __name__ == "__main__":
    main()
