#!/usr/bin/env python3
"""
Generalised window extractor: every coin and window length the recorder saw (cpc-btc-updown-5m/15m/1h, cpceth-…,
cpcsol-…, cpcxrp-…, cpcdoge-…, …), in one pass. Per window: price to beat, settlement, the coin's 1-second RTI prints
(Kalshi index feed, `sym`) from 130 s before the open to 2 s after the bell, and the Polymarket top of book whenever it
was seen. Output: one JSON per family, {family}.json in OUT_DIR, same shape as btc15_windows.json.

Usage:  python3 mrp_extract_windows.py DATA_DIR OUT_DIR
"""
from __future__ import annotations

import glob
import gzip
import json
import os
import re
import sys
from calendar import timegm

HEAD_RE = re.compile(r'^\{"t":(\d+),"k":"([^"]+)"')
SLUG_RE = re.compile(r'"(?:marketSlug|slug)":"(cpc[a-z]*-([a-z]+)-updown-(5m|15m|1h)-[0-9-]+z)"')
STAMP_RE = re.compile(r"-(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})z$")
SYM_RE = re.compile(r'"sym":"([a-z]+)"')
KEEP = ("kalshi.idx", "pmus.ws", "pmus.book", "pmus.settlement", "pmus.market")
LEN = {"5m": 300, "15m": 900, "1h": 3600}


def slug_t0(slug):
    m = STAMP_RE.search(slug)
    if not m:
        return None
    y, mo, d, hh, mm = (int(x) for x in m.groups())
    return timegm((y, mo, d, hh, mm, 0))


def amount(v):
    if isinstance(v, dict):
        v = v.get("value")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def top(book):
    offers = [(amount(o.get("px")), float(o.get("qty") or 0)) for o in (book.get("offers") or [])]
    bids = [(amount(b.get("px")), float(b.get("qty") or 0)) for b in (book.get("bids") or [])]
    offers = [(p, q) for p, q in offers if p is not None and q > 0]
    bids = [(p, q) for p, q in bids if p is not None and q > 0]
    ask = min(offers)[0] if offers else None
    bid = max(bids)[0] if bids else None
    return [ask, round(sum(q for p, q in offers if ask is not None and abs(p - ask) < 1e-9), 2),
            bid, round(sum(q for p, q in bids if bid is not None and abs(p - bid) < 1e-9), 2), book.get("state")]


def main(data_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(data_dir, "**", "*.jsonl"), recursive=True) + glob.glob(os.path.join(data_dir, "**", "*.jsonl.gz"), recursive=True))
    prints = {}     # sym -> {sec: value}
    books = {}      # slug -> {sec: top}
    markets = {}    # slug -> {ptb, settle, latency, sym, len}
    n = 0
    for f in files:
        opener = gzip.open if f.endswith(".gz") else open
        with opener(f, "rt", encoding="utf-8") as fh:
            for line in fh:
                m = HEAD_RE.match(line)
                if not m or m.group(2) not in KEEP:
                    continue
                kind = m.group(2)
                slug = sym = wl = None
                if kind != "kalshi.idx":
                    sm = SLUG_RE.search(line)
                    if not sm:
                        continue
                    slug, sym, wl = sm.group(1), sm.group(2), sm.group(3)
                try:
                    r = json.loads(line)
                except (json.JSONDecodeError, MemoryError):
                    continue
                d = r.get("d") or {}
                t = r.get("t", 0) / 1000.0
                n += 1
                if kind == "kalshi.idx":
                    try:
                        prints.setdefault(d["sym"], {})[int(d["t"])] = float(d["v"])
                    except (KeyError, TypeError, ValueError):
                        pass
                elif kind == "pmus.ws":
                    md = d.get("marketData") or {}
                    if md.get("marketSlug") == slug:
                        books.setdefault(slug, {})[int(t)] = top(md)
                elif kind == "pmus.book":
                    bk = d.get("book") or {}
                    sec = int(t)
                    if sec not in books.setdefault(slug, {}):
                        books[slug][sec] = top(bk)
                    elif bk.get("state"):
                        books[slug][sec][4] = bk.get("state")
                elif kind == "pmus.settlement":
                    mk = markets.setdefault(slug, {"sym": sym, "len": wl})
                    if d.get("settlementPrice") is not None:
                        mk["settle"] = float(d["settlementPrice"]); mk["latency"] = d.get("latency_s")
                    if d.get("priceToBeat") is not None:
                        mk.setdefault("ptb", float(d["priceToBeat"]))
                elif kind == "pmus.market":
                    apt = d.get("assetPriceTerms") or {}
                    mk = markets.setdefault(slug, {"sym": sym, "len": wl})
                    ptb = amount(apt.get("priceToBeat"))
                    if ptb is not None and "ptb" not in mk:
                        mk["ptb"] = ptb
                    sp = amount(apt.get("settlementPrice"))
                    if sp is not None:
                        mk["settle"] = sp
    fams = {}
    for slug, mk in sorted(markets.items()):
        t0 = slug_t0(slug)
        sym, wl = mk["sym"], mk["len"]
        if t0 is None or mk.get("ptb") is None or sym not in prints:
            continue
        L = LEN[wl]; T = t0 + L
        pr_all = prints[sym]
        pr = {str(s): pr_all[s] for s in range(t0 - 130, T + 3) if s in pr_all}
        cov = sum(1 for s in range(t0 - 60, T) if s in pr_all) / float(L + 60)
        mine = [pr_all[s] for s in range(T - 60, T) if s in pr_all]
        my_close = round(sum(mine) / 60, 6) if len(mine) == 60 else None
        bk = books.get(slug, {})
        fams.setdefault(f"{sym}{wl}", []).append({"slug": slug, "T0": t0, "T": T, "ptb": mk["ptb"], "settle": mk.get("settle"), "settle_latency": mk.get("latency"), "my_close": my_close,
                                                 "print_cov": round(cov, 3), "book_secs": len(bk), "prints": pr,
                                                 "book": {str(s): v for s, v in sorted(bk.items()) if t0 - 5 <= s <= T + 5}})
    for fam, windows in sorted(fams.items()):
        with open(os.path.join(out_dir, fam + ".json"), "w", encoding="utf-8") as fh:
            json.dump({"windows": windows, "n_records": n}, fh, separators=(",", ":"))
        full = [w for w in windows if w["print_cov"] >= 0.98 and w["settle"] is not None]
        ok = sum(1 for w in full if w["my_close"] is not None and abs(w["my_close"] - w["settle"]) <= max(0.006, abs(w["settle"]) * 1e-5))
        print(f"{fam:>8}: windows {len(windows)}  full {len(full)}  settlement reproduced {ok}/{sum(1 for w in full if w['my_close'] is not None)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
