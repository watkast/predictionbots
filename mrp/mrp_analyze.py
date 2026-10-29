#!/usr/bin/env python3
"""
Mr. P — Analyzer v2.  Reads recorder JSONL (v1 or v2) and answers, per coin/timeframe and per
seconds-left checkpoint:

  SETTLEMENT gate  did the leader at T-tau win?  how far was the index from the open (|d|, $ and bps)?
  PRICE gate       Polymarket: leader ask <= 0.99 / <= 0.95 with >= LOT contracts?  net after taker fee?
                   Kalshi:     leader bid/ask at the same instant (yes-leg pricing, 0.001 ticks)
  CROSS-VENUE      lock margin = best(pm_bid - kalshi_ask, kalshi_bid - pm_ask) - fees
  EXECUTION gate   Polymarket market state at the checkpoint
  PHYSICS          fastest index moves over 1/5/10/15/30/60 s from the true (Kalshi) prints

Usage:  python3 mrp_analyze.py [DATA_DIR] [--lot 10] [--days 7] [--min-d-bps 0] [--csv windows.csv]
"""
from __future__ import annotations

import argparse
import csv
import glob
import gzip
import json
import os
import re
import statistics
from collections import defaultdict
from datetime import datetime, timezone

CHECKPOINTS = [600, 300, 180, 120, 90, 60, 45, 30, 20, 15, 10, 5, 3, 2, 1]
THETA_PM = 0.0695      # Polymarket US taker
THETA_K = 0.07         # Kalshi taker
SLUG_RE = re.compile(r"^cpc[a-z0-9]*-([a-z0-9]+)-updown-(\d+)([mh])-")   # cpc-btc-..., cpceth-eth-..., cpcsol-sol-...


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


def slug_parts(slug):
    m = SLUG_RE.match(slug or "")
    if not m:
        return "btc", 900
    n, u = int(m.group(2)), m.group(3)
    return m.group(1), n * (60 if u == "m" else 3600)


def fee(theta, contracts, p):
    return round(theta * contracts * p * (1 - p) + 1e-12, 2)


def load(data_dir, days=None):
    files = sorted(glob.glob(os.path.join(data_dir, "**", "*.jsonl"), recursive=True)
                   + glob.glob(os.path.join(data_dir, "**", "*.jsonl.gz"), recursive=True))
    if days:
        cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
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


def pm_sides(book):
    """Polymarket books quote one Up instrument: buying DOWN = shorting Up at the bid."""
    offers = [(parse_amount(o.get("px")), float(o.get("qty") or 0)) for o in (book.get("offers") or [])]
    bids = [(parse_amount(b.get("px")), float(b.get("qty") or 0)) for b in (book.get("bids") or [])]
    offers = [(p, q) for p, q in offers if p is not None and q > 0]
    bids = [(p, q) for p, q in bids if p is not None and q > 0]
    ask_up = min(offers)[0] if offers else None
    bid_up = max(bids)[0] if bids else None
    return {"ask_up": ask_up, "ask_up_q": sum(q for p, q in offers if ask_up is not None and abs(p - ask_up) < 1e-9),
            "bid_up": bid_up, "bid_up_q": sum(q for p, q in bids if bid_up is not None and abs(p - bid_up) < 1e-9),
            "ask_down": round(1 - bid_up, 4) if bid_up is not None else None,
            "ask_down_q": sum(q for p, q in bids if bid_up is not None and abs(p - bid_up) < 1e-9),
            "bid_down": round(1 - ask_up, 4) if ask_up is not None else None,
            "bid_down_q": sum(q for p, q in offers if ask_up is not None and abs(p - ask_up) < 1e-9)}


def k_sides(snap):
    yb = snap.get("yb") or []
    ya = snap.get("ya") or []
    out = {"ask_up": ya[0][0] if ya else None, "ask_up_q": ya[0][1] if ya else 0,
           "bid_up": yb[0][0] if yb else None, "bid_up_q": yb[0][1] if yb else 0}
    out["ask_down"] = round(1 - out["bid_up"], 4) if out["bid_up"] is not None else None
    out["ask_down_q"] = out["bid_up_q"]
    out["bid_down"] = round(1 - out["ask_up"], 4) if out["ask_up"] is not None else None
    out["bid_down_q"] = out["ask_up_q"]
    return out


def nearest_before(lst, t, max_age):
    """lst sorted by time; latest element with time <= t + 0.5 and >= t - max_age."""
    best = None
    for tb, b in reversed(lst):
        if tb <= t + 0.5:
            if tb >= t - max_age:
                best = b
            break
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data_dir", nargs="?", default=os.environ.get("MRP_DATA_DIR", "./data"))
    ap.add_argument("--lot", type=float, default=10)
    ap.add_argument("--days", type=float, default=None)
    ap.add_argument("--min-depth", type=float, default=None)
    ap.add_argument("--min-d-bps", type=float, default=0.0, help="settlement-gate threshold in basis points of price")
    ap.add_argument("--csv", default="windows.csv")
    args = ap.parse_args()
    lot = args.lot
    min_depth = args.min_depth if args.min_depth is not None else lot

    idx = defaultdict(dict)          # sym -> {sec: value}
    idx_src = {}                     # sym -> kalshi|pmus
    markets = {}                     # slug -> dict
    books = defaultdict(list)        # slug -> [(t, book)]   REST + WebSocket (state, asks, depth)
    books_ws = defaultdict(list)     # slug -> [(t, book)]   WebSocket only (real-time; used for cross-venue locks)
    kbooks = defaultdict(list)       # (sym, close) -> [(t, snap)]
    states = defaultdict(list)
    settle_avg = defaultdict(list)
    errors = 0
    n_rec = 0
    for r in load(args.data_dir, args.days):
        n_rec += 1
        k, d, t = r.get("k"), r.get("d"), r.get("t")
        if k == "kalshi.idx":
            try:
                idx[d["sym"]][int(d["t"])] = float(d["v"]); idx_src[d["sym"]] = "kalshi"
            except (KeyError, TypeError, ValueError):
                pass
        elif k == "pmus.idx":
            try:
                sym = d.get("sym", "btc")
                if idx_src.get(sym) != "kalshi":
                    idx[sym][int(d["ts"])] = float(d["c"]); idx_src.setdefault(sym, "pmus")
            except (KeyError, TypeError, ValueError):
                pass
        elif k == "pmus.market":
            slug = d.get("slug"); apt = d.get("assetPriceTerms") or {}
            m = markets.setdefault(slug, {"slug": slug})
            m["start"] = parse_ts(apt.get("windowStart")) or m.get("start")
            m["end"] = parse_ts(apt.get("windowEnd")) or m.get("end")
            ptb = parse_amount(apt.get("priceToBeat"))
            if ptb is not None and m.get("ptb") is None:
                m["ptb"], m["ptb_stamp_t"] = ptb, t / 1000.0
            sp = parse_amount(apt.get("settlementPrice"))
            if sp is not None:
                m["settlementPrice"] = sp
        elif k == "pmus.settlement":
            slug = d.get("slug"); m = markets.setdefault(slug, {"slug": slug})
            if d.get("settlementPrice") is not None:
                m["settlementPrice"] = d["settlementPrice"]
            if d.get("priceToBeat") is not None and m.get("ptb") is None:
                m["ptb"] = d["priceToBeat"]
            if d.get("settlement") is not None:
                m["settlement"] = parse_amount(d["settlement"])
            if d.get("end"):
                m["end"] = d["end"]
            m["settle_latency_s"] = d.get("latency_s")
        elif k == "pmus.book":
            books[d.get("slug")].append((t / 1000.0, d.get("book") or {}))
        elif k == "pmus.ws":
            md = d.get("marketData")
            if md and md.get("marketSlug"):
                books[md["marketSlug"]].append((t / 1000.0, md))
                books_ws[md["marketSlug"]].append((t / 1000.0, md))
        elif k == "kalshi.book":
            kbooks[(d.get("sym"), int(d.get("close") or 0))].append((t / 1000.0, d))
        elif k == "pmus.state":
            states[d.get("slug")].append((t / 1000.0, d.get("from"), d.get("to")))
        elif k in ("settle_avg", "pmus.settle_avg"):
            settle_avg[d.get("slug")].append((t / 1000.0, d))
        elif k == "err":
            errors += 1
    for lst in books.values():
        lst.sort(key=lambda x: x[0])
    for lst in books_ws.values():
        lst.sort(key=lambda x: x[0])
    for lst in kbooks.values():
        lst.sort(key=lambda x: x[0])

    rows = []
    for slug, m in sorted(markets.items()):
        ptb, end = m.get("ptb"), m.get("end")
        if ptb is None or end is None:
            continue
        end = int(round(end))
        sym, hz = slug_parts(slug)
        sp, settle = m.get("settlementPrice"), m.get("settlement")
        if sp is None and settle is None:
            continue
        outcome = ("UP" if settle >= 0.5 else "DOWN") if settle is not None else ("UP" if sp >= ptb else "DOWN")
        series = idx.get(sym, {})
        mine = [series[ts] for ts in range(end - 60, end) if ts in series]
        my_close = round(sum(mine) / 60, 2) if len(mine) == 60 else None
        bl = books.get(slug, [])
        kl = kbooks.get((sym, end), [])
        for tau in CHECKPOINTS:
            if tau >= hz:
                continue
            t = end - tau
            px = next((series[t - b] for b in range(0, 4) if (t - b) in series), None)
            if px is None:
                continue
            d = px - ptb
            if tau <= 60:
                done = [series[ts] for ts in range(end - 60, t + 1) if ts in series]
                proj = (sum(done) + (60 - len(done)) * px) / 60 if done else px
                leader = "UP" if proj >= ptb else "DOWN"
            else:
                leader = "UP" if d >= 0 else "DOWN"
            max_age = 6.0 if tau < 180 else 20.0
            bk = nearest_before(bl, t, max_age)
            ks = nearest_before(kl, t, 3.0) if hz == 900 else None       # Kalshi only lists 15-minute windows
            bw = nearest_before(books_ws.get(slug, []), t, 1.5)
            pm = pm_sides(bk) if bk else {}
            pw = pm_sides(bw) if bw else {}
            kk = k_sides(ks) if ks else {}
            side = "up" if leader == "UP" else "down"
            l_ask, l_q = pm.get(f"ask_{side}"), pm.get(f"ask_{side}_q") or 0
            l_bid = pm.get(f"bid_{side}")
            k_ask, k_q, k_bid = kk.get(f"ask_{side}"), kk.get(f"ask_{side}_q") or 0, kk.get(f"bid_{side}")
            f_pm = fee(THETA_PM, lot, l_ask) if l_ask else None
            net = round(lot * (1 - l_ask) - f_pm, 2) if l_ask else None
            state = bk.get("state") if bk else None
            d_bps = 1e4 * d / ptb if ptb else 0
            entry_ok = bool(bk and state == "MARKET_STATE_OPEN" and l_ask is not None and l_ask <= 0.99 and l_q >= min_depth
                            and net is not None and net > 0 and abs(d_bps) >= args.min_d_bps)
            # cross-venue lock on the leader: buy on one venue, sell on the other (same settlement index)
            lock = None      # real-time (WebSocket) Polymarket book vs Kalshi, same second, same contract
            w_bid, w_ask = pw.get(f"bid_{side}"), pw.get(f"ask_{side}")
            if w_bid is not None and k_ask is not None:
                lock = round(w_bid - k_ask - THETA_PM * w_bid * (1 - w_bid) - THETA_K * k_ask * (1 - k_ask), 4)
            if w_ask is not None and k_bid is not None:
                alt = round(k_bid - w_ask - THETA_PM * w_ask * (1 - w_ask) - THETA_K * k_bid * (1 - k_bid), 4)
                lock = alt if lock is None else max(lock, alt)
            need = None
            if tau <= 60:
                best = None
                for ta, sa in settle_avg.get(slug, []):
                    if abs(ta - t) <= 1.5 and (best is None or abs(ta - t) < abs(best[0] - t)):
                        best = (ta, sa)
                if best:
                    need = best[1].get("need_rem_move")
            rows.append({"slug": slug, "sym": sym, "hz_min": hz // 60,
                         "end_utc": datetime.fromtimestamp(end, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),
                         "tau": tau, "ptb": ptb, "idx": px, "idx_src": idx_src.get(sym), "d": round(d, 4), "d_bps": round(d_bps, 1),
                         "leader": leader, "outcome": outcome, "flip": int(leader != outcome), "state": state,
                         "pm_leader_ask": l_ask, "pm_leader_ask_q": l_q, "pm_leader_bid": l_bid,
                         "k_leader_ask": k_ask, "k_leader_ask_q": k_q, "k_leader_bid": k_bid, "lock_margin": lock,
                         "fee": f_pm, "net_if_win": net, "entry_ok": int(entry_ok), "need_rem_move": need,
                         "settlementPrice": sp, "my_close_avg": my_close,
                         "close_match": (None if (sp is None or my_close is None) else int(abs(sp - my_close) < 0.006))})

    print(f"\nMr. P — gate report   records={n_rec:,}  windows={len({r['slug'] for r in rows})}  lot={lot:g}  errors_logged={errors}")
    print(f"data: {args.data_dir}   index sources: {dict(idx_src) or 'none'}")
    if not rows:
        print("No completed windows with price-to-beat + settlement yet.")
        return
    with open(args.csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    groups = sorted({(r["sym"], r["hz_min"]) for r in rows})
    for sym, hzm in groups:
        rr_all = [r for r in rows if r["sym"] == sym and r["hz_min"] == hzm]
        wins = sorted({r["slug"] for r in rr_all})
        cm = [r["close_match"] for r in rr_all if r["tau"] == 60 and r["close_match"] is not None]
        print(f"\n=== {sym.upper()} {hzm}-minute   windows={len(wins)}   index={idx_src.get(sym, '?')}"
              + (f"   settlement reproduced {sum(cm)}/{len(cm)}" if cm else ""))
        hdr = (f"{'T-left':>6} {'n':>4} {'flip%':>6} {'open%':>6} {'med|d|bps':>9} {'PM ask<=.99':>11} {'<=.95':>6} "
               f"{'entry_ok':>8} {'ok&flip':>7} {'min|d|ok$':>9} {'PM ask p50':>10} {'K ask p50':>9} {'K bid p50':>9} {'lock>0':>6} {'maxlock':>7}")
        print(hdr); print("-" * len(hdr))
        for tau in CHECKPOINTS:
            rr = [r for r in rr_all if r["tau"] == tau]
            if not rr:
                continue
            n = len(rr); flips = sum(r["flip"] for r in rr)
            openp = sum(1 for r in rr if r["state"] == "MARKET_STATE_OPEN")
            cheap = sum(1 for r in rr if r["pm_leader_ask"] is not None and r["pm_leader_ask"] <= 0.99)
            cheap95 = sum(1 for r in rr if r["pm_leader_ask"] is not None and r["pm_leader_ask"] <= 0.95)
            ok = [r for r in rr if r["entry_ok"]]
            okflip = sum(r["flip"] for r in ok)
            mind = min((abs(r["d"]) for r in ok), default=None)
            med_bps = statistics.median(abs(r["d_bps"]) for r in rr)
            pa = sorted(r["pm_leader_ask"] for r in rr if r["pm_leader_ask"] is not None)
            ka = sorted(r["k_leader_ask"] for r in rr if r["k_leader_ask"] is not None)
            kb = sorted(r["k_leader_bid"] for r in rr if r["k_leader_bid"] is not None)
            locks = [r["lock_margin"] for r in rr if r["lock_margin"] is not None]
            f = lambda xs, fmt="{:.3f}": (fmt.format(xs[len(xs) // 2]) if xs else "-")
            print(f"{tau:>6} {n:>4} {100*flips/n:>5.1f}% {100*openp/n:>5.0f}% {med_bps:>9.1f} {cheap:>11} {cheap95:>6} "
                  f"{len(ok):>8} {okflip:>7} {(f'{mind:.0f}' if mind is not None else '-'):>9} {f(pa):>10} {f(ka):>9} {f(kb):>9} "
                  f"{sum(1 for x in locks if x > 0):>6} {(f'{max(locks):+.3f}' if locks else '-'):>7}")
        # physics from the true prints
        series = idx.get(sym, {})
        if len(series) > 600:
            ks = sorted(series)
            out = []
            for span in (1, 5, 10, 15, 30, 60):
                mv = sorted(abs(series[t + span] - series[t]) for t in ks if (t + span) in series)
                if mv:
                    out.append(f"{span}s max {mv[-1]:.2f} p99.9 {mv[int(len(mv)*.999)]:.2f}")
            print(f"  index speed ({idx_src.get(sym)}, {len(series)} prints): " + " | ".join(out))
    print("\nColumns: PM = Polymarket US (0.01 ticks, leader ask / count with >= lot contracts), K = Kalshi (0.001 ticks). "
          "lock>0 = checkpoints where buying the leader on one venue and selling it on the other cleared both fees.\n"
          "entry_ok = state OPEN, PM leader ask <= 0.99 with >= lot contracts, positive net"
          + (f", |d| >= {args.min_d_bps:g} bps" if args.min_d_bps else "") + ". ok&flip must be ZERO with margin before anything goes live.")
    print("\nCross-venue lock scan — every second of the last 5 minutes, Polymarket WebSocket book vs Kalshi "
          "snapshot (15-minute windows, same index):")
    print(f"{'coin':>5} {'windows':>7} {'seconds':>8} {'lock>0.4c':>9} {'lock>1c':>8} {'longest run':>11} {'max margin':>10} {'max depth':>9}")
    for sym in sorted({slug_parts(s_)[0] for s_ in markets}):
        secs = hits1 = hits2 = 0; longest = run = 0; maxm = None; maxd = 0; nwin = 0
        for slug, m in markets.items():
            s_sym, hz = slug_parts(slug)
            if s_sym != sym or hz != 900 or not m.get("end") or slug not in books_ws:
                continue
            end = int(round(m["end"]))
            kl = kbooks.get((sym, end), [])
            if not kl:
                continue
            kd = {int(tb): b for tb, b in kl}
            nwin += 1
            last_sec = None
            for tb, bk in books_ws[slug]:
                sec = int(tb); rem = end - tb
                if rem > 300 or rem < 0 or sec == last_sec:
                    continue
                last_sec = sec
                snap = kd.get(sec) or kd.get(sec - 1)
                if not snap:
                    continue
                secs += 1
                p_ = pm_sides(bk); k_ = k_sides(snap)
                best = None; depth = 0
                for pbid, kask, pq, kq in ((p_["bid_up"], k_["ask_up"], p_["bid_up_q"], k_["ask_up_q"]),):
                    if pbid is not None and kask is not None:
                        mg = pbid - kask - THETA_PM * pbid * (1 - pbid) - THETA_K * kask * (1 - kask)
                        if best is None or mg > best:
                            best, depth = mg, min(pq, kq)
                for pask, kbid, pq, kq in ((p_["ask_up"], k_["bid_up"], p_["ask_up_q"], k_["bid_up_q"]),):
                    if pask is not None and kbid is not None:
                        mg = kbid - pask - THETA_PM * pask * (1 - pask) - THETA_K * kbid * (1 - kbid)
                        if best is None or mg > best:
                            best, depth = mg, min(pq, kq)
                if best is not None and best > 0.004 and depth >= 10:
                    hits1 += 1; run += 1; longest = max(longest, run)
                    if best > 0.01:
                        hits2 += 1
                    if maxm is None or best > maxm:
                        maxm, maxd = best, depth
                else:
                    run = 0
        if nwin:
            print(f"{sym:>5} {nwin:>7} {secs:>8} {hits1:>9} {hits2:>8} {longest:>11} {(f'{maxm:+.3f}' if maxm is not None else '-'):>10} {int(maxd):>9}")
    print("A lock is a same-second pair where buying the Up side on one venue and selling it on the other clears both taker fees "
          "with >= 10 contracts on both sides. 'longest run' = consecutive seconds it persisted.")

    trans = defaultdict(int)
    for slug, lst in states.items():
        end = (markets.get(slug) or {}).get("end")
        for t, a, b in lst:
            trans[(str(a)[13:] or str(a), str(b)[13:] or str(b), "before_end" if (end and t < end) else "after_end")] += 1
    if trans:
        print("\nPolymarket state transitions:")
        for (a, b, when), n in sorted(trans.items(), key=lambda x: -x[1])[:12]:
            print(f"  {a:>22} -> {b:<24} {when:>10}  x{n}")


if __name__ == "__main__":
    main()
