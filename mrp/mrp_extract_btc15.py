#!/usr/bin/env python3
"""
Extract a compact per-window dataset for the BTC 15-minute Up/Down market from Mr. P recorder files, for the
cockpit replay (scripts/pm15_human_sim.js): one JSON with, per window, the price to beat, the settlement price,
every 1-second index print from 130 s before the open to 2 s after the bell, and the top of the Polymarket book
(Up ask / qty / bid / qty) for every second it was seen.

Usage:  python3 mrp_extract_btc15.py DATA_DIR OUT.json     (DATA_DIR holds <run>/<YYYY-MM-DD>/HH.jsonl[.gz])
Streams file by file; memory stays small.
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
SLUG_RE = re.compile(r'"(?:marketSlug|slug)":"(cpc-btc-updown-15m-[0-9-]+z)"')
STAMP_RE = re.compile(r"-(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})z$")
KEEP = ("kalshi.idx", "pmus.ws", "pmus.book", "pmus.settlement", "pmus.market", "pmus.idx")


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


def main(data_dir, out):
    files = sorted(glob.glob(os.path.join(data_dir, "**", "*.jsonl"), recursive=True) + glob.glob(os.path.join(data_dir, "**", "*.jsonl.gz"), recursive=True))
    prints = {}            # sec -> BRTI value (kalshi) ; pmus.idx (smoothed) is NOT a raw print, kept apart
    smooth = {}            # sec -> gateway 1-s series value (already the 60-print average)
    books = {}             # slug -> {sec: top}
    markets = {}           # slug -> {ptb, settle, latency}
    n = 0
    for f in files:
        opener = gzip.open if f.endswith(".gz") else open
        with opener(f, "rt", encoding="utf-8") as fh:
            for line in fh:
                m = HEAD_RE.match(line)
                if not m or m.group(2) not in KEEP:
                    continue
                kind = m.group(2)
                if kind in ("pmus.ws", "pmus.book", "pmus.settlement", "pmus.market"):
                    sm = SLUG_RE.search(line)
                    if not sm:
                        continue
                    slug = sm.group(1)
                elif kind == "kalshi.idx" and '"sym":"btc"' not in line:
                    continue
                elif kind == "pmus.idx" and '"sym":"btc"' not in line and '"sym"' in line:
                    continue
                try:
                    r = json.loads(line)
                except (json.JSONDecodeError, MemoryError):
                    continue
                d = r.get("d") or {}
                t = r.get("t", 0) / 1000.0
                n += 1
                if kind == "kalshi.idx":
                    try:
                        prints[int(d["t"])] = float(d["v"])
                    except (KeyError, TypeError, ValueError):
                        pass
                elif kind == "pmus.idx":
                    try:
                        smooth[int(d["ts"])] = float(d["c"])
                    except (KeyError, TypeError, ValueError):
                        pass
                elif kind == "pmus.ws":
                    md = d.get("marketData") or {}
                    if md.get("marketSlug") == slug:
                        books.setdefault(slug, {})[int(t)] = top(md)
                elif kind == "pmus.book":
                    bk = d.get("book") or {}
                    sec = int(t)
                    if sec not in books.setdefault(slug, {}):       # WebSocket frames win; REST fills gaps (and carries state)
                        books[slug][sec] = top(bk)
                    elif bk.get("state"):
                        books[slug][sec][4] = bk.get("state")
                elif kind == "pmus.settlement":
                    mk = markets.setdefault(slug, {})
                    if d.get("settlementPrice") is not None:
                        mk["settle"] = float(d["settlementPrice"]); mk["latency"] = d.get("latency_s")
                    if d.get("priceToBeat") is not None:
                        mk.setdefault("ptb", float(d["priceToBeat"]))
                elif kind == "pmus.market":
                    apt = d.get("assetPriceTerms") or {}
                    mk = markets.setdefault(slug, {})
                    ptb = amount(apt.get("priceToBeat"))
                    if ptb is not None and "ptb" not in mk:
                        mk["ptb"] = ptb
                    sp = amount(apt.get("settlementPrice"))
                    if sp is not None:
                        mk["settle"] = sp
    windows = []
    for slug, mk in sorted(markets.items()):
        t0 = slug_t0(slug)
        if t0 is None or mk.get("ptb") is None:
            continue
        T = t0 + 900
        pr = {str(s): prints[s] for s in range(t0 - 130, T + 3) if s in prints}
        cov = sum(1 for s in range(t0 - 60, T) if s in prints) / 960.0
        settle = mk.get("settle")
        mine = [prints[s] for s in range(T - 60, T) if s in prints]
        my_close = round(sum(mine) / 60, 4) if len(mine) == 60 else None
        bk = books.get(slug, {})
        windows.append({"slug": slug, "T0": t0, "T": T, "ptb": mk["ptb"], "settle": settle, "settle_latency": mk.get("latency"), "my_close": my_close,
                        "print_cov": round(cov, 3), "book_secs": len(bk), "prints": pr,
                        "book": {str(s): v for s, v in sorted(bk.items()) if t0 - 5 <= s <= T + 5}})
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"windows": windows, "n_records": n}, fh, separators=(",", ":"))
    full = [w for w in windows if w["print_cov"] >= 0.98 and w["settle"] is not None]
    print(f"records used {n:,}  windows {len(windows)}  with full prints + settlement {len(full)}  "
          f"settlement reproduced {sum(1 for w in full if w['my_close'] is not None and abs(w['my_close'] - w['settle']) < 0.006)}/{sum(1 for w in full if w['my_close'] is not None)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
