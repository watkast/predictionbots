#!/usr/bin/env python3
"""
Mr. P — Analyzer v0.  Reads the recorder's JSONL and answers, per completed window and
per "seconds-left" checkpoint:

  SETTLEMENT gate  did the leading side at T-tau end up winning?  (flip rate)
                   how far was BRTI from the price-to-beat?  (|d|)
                   what average would the remaining samples have needed to flip it?
  PRICE gate       was there an ask <= 0.99 on the leading side with >= LOT contracts?
                   what would 10 contracts net after the Polymarket US taker fee?
  EXECUTION gate   what state was the market in?  (OPEN vs anything else)
  PHYSICS          fastest BRTI moves observed over 1/5/10/15/30/60 s windows
                   (the "historical top speed", measured on the exact settlement series)

Usage:  python3 mrp_analyze.py [DATA_DIR] [--lot 10] [--csv windows.csv]
"""
from __future__ import annotations

import argparse
import csv
import glob
import gzip
import json
import math
import os
import statistics
from collections import defaultdict
from datetime import datetime, timezone

CHECKPOINTS = [600, 300, 180, 120, 90, 60, 45, 30, 20, 15, 10, 5, 3, 2, 1]
THETA = 0.0695  # Polymarket US standard taker fee coefficient
WINDOW = 900


def parse_amount(v):
    if v is None:
        return None
    if isinstance(v, dict):
        v = v.get("value")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse_ts(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v) / 1000.0 if v > 1e11 else float(v)
    if isinstance(v, str):
        s = v.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(s).timestamp()
        except ValueError:
            return None
    return None


def bankers_round_cents(x: float) -> float:
    return round(x + 0.0, 2)  # Python's round() is banker's rounding at exact ties


def taker_fee(contracts: float, p: float) -> float:
    return bankers_round_cents(THETA * contracts * p * (1 - p))


def load(data_dir, days=None):
    """Every */YYYY-MM-DD/HH.jsonl under data_dir, any depth (one sub-folder per recorder run is fine).
    `days` keeps only date folders within the last N days."""
    files = sorted(glob.glob(os.path.join(data_dir, "**", "*.jsonl"), recursive=True)
                   + glob.glob(os.path.join(data_dir, "**", "*.jsonl.gz"), recursive=True))
    if days:
        cutoff = (datetime.now(timezone.utc).timestamp() - days * 86400)
        keep = []
        for f in files:
            day = os.path.basename(os.path.dirname(f))
            try:
                if datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() + 86400 >= cutoff:
                    keep.append(f)
            except ValueError:
                keep.append(f)
        files = keep
    if not files:
        raise SystemExit(f"no JSONL files under {data_dir}")
    for f in files:
        opener = gzip.open if f.endswith(".gz") else open
        with opener(f, "rt", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def book_sides(book: dict):
    """Polymarket US books are a single Up/Yes instrument: buying DOWN = going short Up at the bid.
    Returns (ask_up, depth_up, cum_up_le99, ask_down, depth_down, cum_down_le99)."""
    offers = [(parse_amount(o.get("px")), float(o.get("qty") or 0)) for o in (book.get("offers") or [])]
    bids = [(parse_amount(b.get("px")), float(b.get("qty") or 0)) for b in (book.get("bids") or [])]
    offers = [(p, q) for p, q in offers if p is not None and q > 0]
    bids = [(p, q) for p, q in bids if p is not None and q > 0]
    ask_up = min(offers)[0] if offers else None
    depth_up = sum(q for p, q in offers if ask_up is not None and abs(p - ask_up) < 1e-9)
    cum_up = sum(q for p, q in offers if p <= 0.99 + 1e-9)
    best_bid = max(bids)[0] if bids else None
    ask_down = round(1 - best_bid, 4) if best_bid is not None else None
    depth_down = sum(q for p, q in bids if best_bid is not None and abs(p - best_bid) < 1e-9)
    cum_down = sum(q for p, q in bids if (1 - p) <= 0.99 + 1e-9)
    return ask_up, depth_up, cum_up, ask_down, depth_down, cum_down


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data_dir", nargs="?", default=os.environ.get("MRP_DATA_DIR", "./data"))
    ap.add_argument("--lot", type=float, default=10, help="contracts per entry (default 10)")
    ap.add_argument("--csv", default="windows.csv")
    ap.add_argument("--min-depth", type=float, default=None, help="required contracts at the ask (default = lot)")
    ap.add_argument("--days", type=float, default=None, help="only analyze the last N days of data (default all)")
    ap.add_argument("--min-d", type=float, default=0.0,
                    help="settlement-gate threshold: require |BRTI - priceToBeat| >= this ($) for entry_ok (default 0 = off)")
    args = ap.parse_args()
    lot = args.lot
    min_depth = args.min_depth if args.min_depth is not None else lot
    min_d = args.min_d

    brti: dict[int, float] = {}
    markets: dict[str, dict] = {}
    books: dict[str, list] = defaultdict(list)
    states: dict[str, list] = defaultdict(list)
    settle_avg: dict[str, list] = defaultdict(list)
    errors = 0

    for r in load(args.data_dir, args.days):
        k, d, t = r.get("k"), r.get("d"), r.get("t")
        if k == "pmus.idx":
            try:
                brti[int(d["ts"])] = float(d["c"])
            except (KeyError, TypeError, ValueError):
                pass
        elif k == "pmus.market":
            slug = d.get("slug")
            apt = d.get("assetPriceTerms") or {}
            m = markets.setdefault(slug, {"slug": slug})
            m["start"] = parse_ts(apt.get("windowStart")) or m.get("start")
            m["end"] = parse_ts(apt.get("windowEnd")) or m.get("end")
            ptb = parse_amount(apt.get("priceToBeat"))
            if ptb is not None and m.get("ptb") is None:
                m["ptb"], m["ptb_stamp_t"] = ptb, t / 1000.0
            sp = parse_amount(apt.get("settlementPrice"))
            if sp is not None:
                m["settlementPrice"] = sp
            m["tick"] = d.get("orderPriceMinTickSize", m.get("tick"))
            m["minq"] = d.get("minimumTradeQty", m.get("minq"))
        elif k == "pmus.settlement":
            slug = d.get("slug")
            m = markets.setdefault(slug, {"slug": slug})
            if d.get("settlementPrice") is not None:
                m["settlementPrice"] = d["settlementPrice"]
            if d.get("priceToBeat") is not None and m.get("ptb") is None:
                m["ptb"] = d["priceToBeat"]
            if d.get("settlement") is not None:
                m["settlement"] = parse_amount(d["settlement"])
            m["settle_latency_s"] = d.get("latency_s")
            if d.get("end"):
                m["end"] = d["end"]
        elif k == "pmus.book":
            books[d.get("slug")].append((t / 1000.0, d.get("book") or {}))
        elif k == "pmus.state":
            states[d.get("slug")].append((t / 1000.0, d.get("from"), d.get("to")))
        elif k == "pmus.settle_avg":
            settle_avg[d.get("slug")].append((t / 1000.0, d))
        elif k == "err":
            errors += 1

    # ---------------------------------------------------------------- per-window table
    rows = []
    for slug, m in sorted(markets.items()):
        ptb, end = m.get("ptb"), m.get("end")
        if ptb is None or end is None:
            continue
        end = int(round(end))
        sp = m.get("settlementPrice")
        settle = m.get("settlement")
        if sp is None and settle is None:
            continue  # not settled yet
        if settle is not None:
            outcome = "UP" if settle >= 0.5 else "DOWN"
        else:
            outcome = "UP" if sp >= ptb else "DOWN"
        # settlement-minute check from our own BRTI capture
        mine = [brti[ts] for ts in range(end - 60, end) if ts in brti]
        my_close = round(sum(mine) / len(mine), 2) if len(mine) == 60 else None
        bl = sorted(books.get(slug, []))
        for tau in CHECKPOINTS:
            t = end - tau
            # BRTI at t (fallback: nearest earlier print within 3 s)
            px = None
            for back in range(0, 4):
                if (t - back) in brti:
                    px = brti[t - back]
                    break
            if px is None:
                continue
            d = px - ptb
            leader = "UP" if d >= 0 else "DOWN"
            # latest book at or before t (+0.5 s slack), not older than 3 s
            bk = None
            bt = None
            for tb, b in reversed(bl):
                if tb <= t + 0.5:
                    if tb >= t - 3.0:
                        bk, bt = b, tb
                    break
            state = bk.get("state") if bk else None
            ask_up = depth_up = cum_up = ask_dn = depth_dn = cum_dn = None
            if bk:
                ask_up, depth_up, cum_up, ask_dn, depth_dn, cum_dn = book_sides(bk)
            l_ask = ask_up if leader == "UP" else ask_dn
            l_depth = depth_up if leader == "UP" else depth_dn
            l_cum = cum_up if leader == "UP" else cum_dn
            fee = taker_fee(lot, l_ask) if l_ask else None
            net_win = round(lot * (1 - l_ask) - fee, 2) if l_ask else None
            entry_ok = bool(bk and state == "MARKET_STATE_OPEN" and l_ask is not None and l_ask <= 0.99
                            and (l_depth or 0) >= min_depth and net_win is not None and net_win > 0
                            and abs(d) >= min_d)
            # required remaining-average move (from recorder's running-average records), tau <= 60
            need = None
            if tau <= 60:
                best = None
                for ta, sa in settle_avg.get(slug, []):
                    if abs(ta - t) <= 1.5 and (best is None or abs(ta - t) < abs(best[0] - t)):
                        best = (ta, sa)
                if best:
                    need = best[1].get("need_rem_move")
            rows.append({
                "slug": slug, "end_utc": datetime.fromtimestamp(end, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),
                "tau": tau, "ptb": ptb, "brti": px, "d": round(d, 2), "leader": leader, "outcome": outcome,
                "flip": int(leader != outcome), "state": state, "book_age_s": round(t - bt, 1) if bt else None,
                "ask_up": ask_up, "ask_down": ask_dn, "leader_ask": l_ask, "leader_depth": l_depth,
                "leader_cum_le99": l_cum, "fee": fee, "net_if_win": net_win, "entry_ok": int(entry_ok),
                "need_rem_move": need, "settlementPrice": sp, "my_close_avg": my_close,
                "close_match": (None if (sp is None or my_close is None) else int(abs(sp - my_close) < 0.006)),
            })

    if not rows:
        print("No completed windows with price-to-beat + settlement yet. Let the recorder run longer.")
        return

    with open(args.csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---------------------------------------------------------------- report
    windows = sorted({r["slug"] for r in rows})
    print(f"\nMr. P — gate report   windows={len(windows)}  lot={lot:g}  errors_logged={errors}")
    print(f"data: {args.data_dir}   csv: {args.csv}\n")
    flips_total = sum(1 for r in rows if r["tau"] == 60 and r["flip"])
    cm = [r["close_match"] for r in rows if r["tau"] == 60 and r["close_match"] is not None]
    if cm:
        print(f"settlement reproduction: our 60-sample average matched the exchange's settlementPrice "
              f"in {sum(cm)}/{len(cm)} windows  (anything < 100% means a feed gap or a rule mismatch)\n")
    hdr = f"{'T-left':>6} {'n':>4} {'flip%':>6} {'open%':>6} {'ask<=99':>8} {'entry_ok':>8} {'ok&flip':>8} " \
          f"{'min|d|ok':>9} {'med|d|':>7} {'ask p50':>7} {'ask p90':>7} {'net/lot':>8}"
    print(hdr)
    print("-" * len(hdr))
    for tau in CHECKPOINTS:
        rr = [r for r in rows if r["tau"] == tau]
        if not rr:
            continue
        n = len(rr)
        flip = sum(r["flip"] for r in rr)
        openp = sum(1 for r in rr if r["state"] == "MARKET_STATE_OPEN")
        cheap = sum(1 for r in rr if r["leader_ask"] is not None and r["leader_ask"] <= 0.99)
        ok = [r for r in rr if r["entry_ok"]]
        ok_flip = sum(r["flip"] for r in ok)
        min_d_ok = min((abs(r["d"]) for r in ok), default=None)
        med_d = statistics.median(abs(r["d"]) for r in rr)
        asks = sorted(r["leader_ask"] for r in rr if r["leader_ask"] is not None)
        p50 = asks[len(asks) // 2] if asks else None
        p90 = asks[int(len(asks) * 0.9)] if asks else None
        nets = [r["net_if_win"] for r in ok]
        net_med = statistics.median(nets) if nets else None
        print(f"{tau:>6} {n:>4} {100*flip/n:>5.1f}% {100*openp/n:>5.1f}% {cheap:>8} {len(ok):>8} {ok_flip:>8} "
              f"{(f'{min_d_ok:.0f}' if min_d_ok is not None else '-'):>9} {med_d:>7.0f} "
              f"{(f'{p50:.2f}' if p50 is not None else '-'):>7} {(f'{p90:.2f}' if p90 is not None else '-'):>7} "
              f"{(f'{net_med:.2f}' if net_med is not None else '-'):>8}")
    print(f"\nflip% = leading side at T-left lost.  entry_ok = state OPEN, leader ask <= 0.99 with >= {min_depth:g} "
          f"contracts, positive net after fee{f', |d| >= ${min_d:g}' if min_d else ''} (re-run with --min-d to test a "
          f"settlement-gate threshold).\nok&flip = entries that would have been taken AND lost — this column must be "
          f"ZERO, with margin, before anything goes live.")

    # ---------------------------------------------------------------- physics: BRTI speed
    ts_sorted = sorted(brti)
    if len(ts_sorted) > 120:
        print("\nBRTI speed (max absolute move observed over a span, $):")
        for span in (1, 5, 10, 15, 30, 60):
            moves = []
            for ts in ts_sorted:
                if (ts + span) in brti:
                    moves.append(abs(brti[ts + span] - brti[ts]))
            if moves:
                moves.sort()
                p99 = moves[int(len(moves) * 0.99)]
                print(f"  {span:>3}s  max={moves[-1]:>8.2f}  p99.9={moves[int(len(moves)*0.999)]:>8.2f}  "
                      f"p99={p99:>7.2f}  median={moves[len(moves)//2]:>6.2f}  (n={len(moves)})")
        print("  -> a flip at T-left=k needs the remaining k prints to average 60/k x |d| away. "
              "Compare need_rem_move in windows.csv to the max k-second move above.")

    # ---------------------------------------------------------------- state transitions summary
    trans = defaultdict(int)
    for slug, lst in states.items():
        m = markets.get(slug, {})
        end = m.get("end")
        for t, a, b in lst:
            rel = round(t - end) if end else None
            trans[(a, b, "before_end" if (rel is not None and rel < 0) else "after_end")] += 1
    if trans:
        print("\nmarket state transitions seen (from -> to, relative to window end):")
        for (a, b, when), n in sorted(trans.items(), key=lambda x: -x[1]):
            print(f"  {str(a):>36} -> {str(b):<36} {when:>10}  x{n}")


if __name__ == "__main__":
    main()
