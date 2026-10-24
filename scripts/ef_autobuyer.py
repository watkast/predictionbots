"""Early Favorite auto-buyer, PAPER mode, on Polymarket US 15-minute BTC up/down markets.

Purpose: settle the one open question from the backtest, which used 1-minute display prices:
can the Early Favorite entry actually be FILLED at those prices, and in what size?

Rule (same as the manual playbook, real clock):
  Check 1 at 2:00 elapsed (13:00 left), else check 2 at 3:00 elapsed (12:00 left).
  Favorite = Up if the Up mid >= 0.50, else Down.
  If the favorite's best ask is in [0.80, 0.95): paper-buy with a limit at that ask (+1c tolerance),
  filled only against resting size on the live book. One entry per round. Hold to settlement.
  Taker fee: feeCoefficient * p * (1 - p) per contract (0.0695 on Polymarket US).

Nothing here places orders. It reads the public book (GET /v1/markets/{slug}/book, no key),
records what a real order would have filled, and scores it when the round settles.

The book is quoted on the Up (long) side: offers = Up asks; buying Down = selling Up into the
bids, so a Down ask is 1 - Up bid and its size is that bid's size.

Usage:
  python scripts/ef_autobuyer.py run --out data/polyus/ef_autobuyer --minutes 170
  python scripts/ef_autobuyer.py report --out data/polyus/ef_autobuyer --history data/polyus/price_history
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://gateway.polymarket.us"
RULE = {
    "name": "Early Favorite auto-buyer v1 (paper)",
    "checks_elapsed_s": [120, 180],      # 13:00 left, then 12:00 left
    "ask_min": 0.80,
    "ask_max": 0.95,
    "limit_tolerance": 0.01,             # limit = best ask + 1c
    "stakes_usd": [50.0, 100.0, 250.0],  # fill tested at each size
    "fee_coef_default": 0.0695,
}
ROUND_S = 900
BOOK_PATH = "/v1/markets/{slug}/book"
# The gateway answers 404 "market with slug ... not found" for a market that exists (and is trading) at
# 2:00 and often still at 3:00 elapsed; it clears later in the round. Oct 22-24: 45% of 13:00-left reads
# and 23% of rounds (both checks) were lost that way. So each check keeps re-reading the book for up to
# RETRY_WINDOW_S after its target second. This is read reliability, not a rule change: the entry still
# happens at the first qualifying read after the 13:00 / 12:00-left target, and the ledger records the
# actual elapsed time ('t') and the number of tries.
RETRY_WINDOW_S = 45
RETRY_EVERY_S = 5


# ---------- pure helpers (unit-tested) ----------

def _f(v):
    if isinstance(v, dict):
        v = v.get("value")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse_book(j: dict) -> dict | None:
    """GetMarketBookResponse -> {'bids': [(px, qty) desc], 'offers': [(px, qty) asc], 'state', 'long_px', 'short_px'}."""
    md = (j or {}).get("marketData") or j or {}
    def side(key):
        out = []
        for e in md.get(key) or []:
            px, q = _f(e.get("px")), _f(e.get("qty"))
            if px is not None and q and q > 0:
                out.append((px, q))
        return out
    bids = sorted(side("bids"), key=lambda x: -x[0])
    offers = sorted(side("offers"), key=lambda x: x[0])
    if not bids and not offers:
        return None
    lps = ((md.get("stats") or {}).get("lastPriceSample")) or {}
    return {"bids": bids, "offers": offers, "state": md.get("state"),
            "long_px": _f(lps.get("longPx")), "short_px": _f(lps.get("shortPx"))}


def side_asks(book: dict, side: str) -> list[tuple[float, float]]:
    """Ask ladder (price asc, qty) for buying `side` ('Up' or 'Down')."""
    if side == "Up":
        return list(book["offers"])
    return [(round(1.0 - px, 4), q) for px, q in book["bids"]]


def favorite(book: dict) -> tuple[str, float] | None:
    """(side, best ask) of the leading side, or None if the book is one-sided."""
    if not book["bids"] or not book["offers"]:
        return None
    up_mid = (book["bids"][0][0] + book["offers"][0][0]) / 2
    side = "Up" if up_mid >= 0.5 else "Down"
    return side, side_asks(book, side)[0][0]


def fill(asks: list[tuple[float, float]], stake: float, limit: float) -> dict:
    """Walk the ask ladder up to `limit` spending at most `stake` dollars (pre-fee)."""
    spent = shares = 0.0
    for px, q in asks:
        if px > limit + 1e-9:
            break
        take = min(q, (stake - spent) / px)
        if take <= 0:
            break
        spent += take * px
        shares += take
        if spent >= stake - 1e-6:
            break
    return {"shares": round(shares, 4), "spent": round(spent, 4),
            "vwap": round(spent / shares, 4) if shares else None,
            "fill_frac": round(spent / stake, 4) if stake else 0.0}


def pnl(shares: float, vwap: float, won: bool, fee_coef: float) -> float:
    fee = fee_coef * vwap * (1 - vwap) * shares
    return round((shares if won else 0.0) - shares * vwap - fee, 4)


def decide(book: dict) -> dict | None:
    """Apply the rule to one book snapshot. Returns an entry dict or None (no trade at this check)."""
    fav = favorite(book)
    if not fav:
        return None
    side, ask = fav
    if not (RULE["ask_min"] <= ask < RULE["ask_max"]):
        return None
    asks = side_asks(book, side)
    limit = round(ask + RULE["limit_tolerance"], 4)
    fills = {str(int(s)): fill(asks, s, limit) for s in RULE["stakes_usd"]}
    depth_at_best = sum(q for px, q in asks if px <= ask + 1e-9)
    return {"side": side, "ask": ask, "limit": limit, "depth_at_best": round(depth_at_best, 2),
            "top5": asks[:5], "fills": fills}


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slug_for(ws: int) -> str:
    d = datetime.fromtimestamp(ws, timezone.utc)
    return f"cpc-btc-updown-15m-{d:%Y-%m-%d-%H%M}z"


def read_book(get, slug: str, until: float, every: float = RETRY_EVERY_S, clock=time.time, sleep=time.sleep):
    """Read the book, re-trying every `every` s while it fails, until a read would end after `until`.

    Returns (json_or_None, tries, time_of_last_read, latency_of_last_read_s)."""
    tries = 0
    while True:
        tries += 1
        t0 = clock()
        j = get(BOOK_PATH.format(slug=slug))
        latency = clock() - t0
        if j is not None or clock() + every >= until:
            return j, tries, t0, latency
        sleep(every)


# ---------- ledger ----------

def load(out: Path) -> dict:
    p = out / "ledger.json"
    return json.loads(p.read_text()) if p.exists() else {}


def save(out: Path, led: dict):
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "ledger.json.tmp"
    tmp.write_text(json.dumps(led, indent=0))
    tmp.replace(out / "ledger.json")


# ---------- live loop ----------

def run(out: Path, minutes: float):
    import httpx
    client = httpx.Client(base_url=BASE, headers={"User-Agent": "predictionbots/0.1 (paper research)"}, timeout=10)

    errors = []

    def get(path):
        for i in range(2):
            try:
                r = client.get(path)
                if r.status_code == 200:
                    return r.json()
                errors.append({"t": iso(time.time()), "path": path, "status": r.status_code, "body": r.text[:300]})
                if r.status_code in (400, 404):
                    return None
            except Exception as e:  # network blip
                errors.append({"t": iso(time.time()), "path": path, "error": repr(e)[:300]})
            time.sleep(0.5)
        return None

    led = load(out)
    end = time.time() + minutes * 60
    first_book_logged = False
    while time.time() < end:
        now = time.time()
        ws = int(now // ROUND_S * ROUND_S)
        slug = slug_for(ws)
        rec = led.setdefault(slug, {"slug": slug, "window_start": ws, "checks": [], "entry": None})
        # checkpoints for this round
        for chk in RULE["checks_elapsed_s"]:
            t_chk = ws + chk
            if rec["entry"] or any(c["at"] == chk for c in rec["checks"]):
                continue
            if time.time() > t_chk + 20:      # missed it (started late)
                continue
            while time.time() < t_chk:
                time.sleep(min(0.2, t_chk - time.time()) if t_chk > time.time() else 0)
            j, tries, t_read, latency = read_book(get, slug, t_chk + RETRY_WINDOW_S)
            book = parse_book(j) if j else None
            if book and not first_book_logged:
                (out / "sample_book.json").parent.mkdir(parents=True, exist_ok=True)
                (out / "sample_book.json").write_text(json.dumps(j)[:20000])
                first_book_logged = True
            c = {"at": chk, "t": round(t_read - ws, 2), "latency_s": round(latency, 3),
                 "ok": bool(book), "tries": tries}
            if book:
                fav = favorite(book)
                c.update(state=book["state"], fav=fav and fav[0], fav_ask=fav and fav[1],
                         long_px=book["long_px"], short_px=book["short_px"],
                         up_bid=book["bids"][0][0] if book["bids"] else None,
                         up_ask=book["offers"][0][0] if book["offers"] else None)
                e = decide(book)
                if e:
                    e["check"] = chk
                    rec["entry"] = e
            rec["checks"].append(c)
            print(f"{iso(t0)} {slug} check@{chk}s -> {c.get('fav')} {c.get('fav_ask')} "
                  f"{'ENTRY ' + json.dumps(rec['entry']['fills']['100']) if rec['entry'] else 'no entry'}", flush=True)
            save(out, led)
            if errors:
                (out / "errors.json").write_text(json.dumps(errors[-50:], indent=1))
        settle(out, led, get)
        # sleep until the next checkpoint in this or the next round
        nxt = ws + ROUND_S + RULE["checks_elapsed_s"][0]
        for chk in RULE["checks_elapsed_s"]:
            if ws + chk > time.time():
                nxt = ws + chk
                break
        time.sleep(max(1.0, min(nxt - time.time() - 1.0, 60)))
    settle(out, led, get)
    report(out, None)


def settle(out: Path, led: dict, get):
    changed = False
    for slug, rec in led.items():
        if rec.get("settled") or time.time() < rec["window_start"] + ROUND_S + 30:
            continue
        if not rec.get("entry"):
            rec["settled"] = "no_entry"
            changed = True
            continue
        j = get(f"/v1/market/slug/{slug}")
        m = (j or {}).get("market") or j or {}
        t = m.get("assetPriceTerms") or {}
        ptb, sp = _f(t.get("priceToBeat")), _f(t.get("settlementPrice"))
        if ptb is None or sp is None:
            continue
        up_won = sp >= ptb
        e = rec["entry"]
        won = up_won if e["side"] == "Up" else not up_won
        fee = _f(m.get("feeCoefficient")) or RULE["fee_coef_default"]
        rec.update(settled=iso(time.time()), price_to_beat=ptb, settlement=sp, won=won, fee_coef=fee)
        for k, fl in e["fills"].items():
            fl["pnl"] = pnl(fl["shares"], fl["vwap"], won, fee) if fl["shares"] else 0.0
        changed = True
    if changed:
        save(out, led)


# ---------- report ----------

def report(out: Path, history: Path | None):
    led = load(out)
    recs = sorted(led.values(), key=lambda r: r["window_start"])
    observed = [r for r in recs if r.get("checks")]
    entries = [r for r in recs if r.get("entry")]
    scored = [r for r in entries if "won" in r]
    lines = [f"# {RULE['name']}", "",
             "Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite "
             "if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.",
             f"Updated {iso(time.time())}.", ""]
    summary = {"rounds_observed": len(observed), "entries": len(entries), "scored": len(scored), "by_stake": {}}
    lines += [f"Rounds watched: {len(observed)}. Entries: {len(entries)}. Settled: {len(scored)}.", ""]
    if scored:
        wins = sum(r["won"] for r in scored)
        lines += [f"Win rate: {wins}/{len(scored)} = {wins / len(scored):.1%}", "",
                  "| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |", "|---|---|---|---|---|---|"]
        for k in [str(int(s)) for s in RULE["stakes_usd"]]:
            fl = [r["entry"]["fills"][k] for r in scored]
            full = sum(f["fill_frac"] >= 0.99 for f in fl) / len(fl)
            spent = sum(f["spent"] for f in fl)
            net = sum(f.get("pnl", 0.0) for f in fl)
            px = [f["vwap"] for f in fl if f["vwap"]]
            summary["by_stake"][k] = {"full_fill_rate": round(full, 3), "net": round(net, 2),
                                      "ret_per_dollar": round(net / spent, 4) if spent else None}
            lines.append(f"| ${k} | {full:.0%} | {sum(f['fill_frac'] for f in fl) / len(fl):.0%} | "
                         f"{(sum(px) / len(px)) if px else 0:.3f} | ${net:+,.2f} | "
                         f"{(net / spent * 100) if spent else 0:+.2f}% |")
        lines.append("")
    # live ask vs the 1-minute display price the backtest used
    if history and history.exists():
        gaps = []
        for r in entries:
            f = history / f"{r['slug']}.json"
            if not f.exists():
                continue
            d = json.loads(f.read_text())
            h = {int(x["timestamp"]) - int(d["windowStart"]): x for x in d.get("history") or []}
            # display snapshot labeled one minute earlier reflects the end of that minute (see research notes)
            snap = h.get(r["entry"]["check"] - 60)
            if not snap:
                continue
            disp = snap["longPrice"] if r["entry"]["side"] == "Up" else snap["shortPrice"]
            gaps.append(r["entry"]["fills"]["100"]["vwap"] - disp if r["entry"]["fills"]["100"]["vwap"] else None)
        gaps = [g for g in gaps if g is not None]
        if gaps:
            gm = sum(gaps) / len(gaps)
            summary["live_minus_display_c"] = round(gm * 100, 2)
            lines += [f"Live $100 fill price minus the backtest's display price: {gm * 100:+.2f}c average over "
                      f"{len(gaps)} entries (the backtest edge was about +4.2c, so this gap is what it must survive).", ""]
    lines += ["## Last 20 entries", "", "| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |",
              "|---|---|---|---|---|---|---|---|"]
    for r in entries[-20:]:
        e, f100 = r["entry"], r["entry"]["fills"]["100"]
        res = "-" if "won" not in r else ("WIN" if r["won"] else "LOSS")
        lines.append(f"| {iso(r['window_start'])[5:16]} | {15 - e['check'] // 60}:00 | {e['side']} | {e['ask']:.2f} | "
                     f"{e['depth_at_best']:.0f} | {f100['fill_frac']:.0%} @ {f100['vwap'] or 0:.3f} | {res} | "
                     f"{f100.get('pnl', 0):+.2f} |")
    ok = [c for r in observed for c in r["checks"]]
    if ok:
        lines += ["", f"Book reads: {len(ok)}, failed: {sum(not c['ok'] for c in ok)}, "
                      f"re-tried: {sum(c.get('tries', 1) > 1 for c in ok)}, "
                      f"median latency {sorted(c['latency_s'] for c in ok)[len(ok) // 2]:.2f}s."]
        # how late after the 13:00 / 12:00-left target the entries were actually read
        lateness = [c["t"] - c["at"] for r in entries for c in r["checks"] if c["at"] == r["entry"]["check"]]
        if lateness:
            late = [x for x in lateness if x > 20]
            summary["entries_read_late"] = len(late)
            lines.append(f"Entries read more than 20 s after their target second: {len(late)} of {len(lateness)}"
                         + (f" (avg {sum(late) / len(late):.0f} s late)." if late else "."))
    out.mkdir(parents=True, exist_ok=True)
    (out / "README.md").write_text("\n".join(lines) + "\n")
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print("\n".join(lines[:30]))


def probe(out: Path):
    """Try candidate book/BBO paths for the current round and save raw responses."""
    import httpx
    c = httpx.Client(base_url=BASE, headers={"User-Agent": "predictionbots/0.1 (paper research)"}, timeout=10)
    ws = int(time.time() // ROUND_S * ROUND_S)
    res = []
    for slug in [slug_for(ws), slug_for(ws - ROUND_S)]:
        for path in ["/v1/markets/{s}/book", "/v1/markets/{s}/bbo", "/v1/market/slug/{s}/book",
                     "/v1/markets/book/{s}", "/v1/book/{s}", "/v1/markets/{s}", "/v1/market/slug/{s}"]:
            p = path.format(s=slug)
            try:
                r = c.get(p)
                res.append({"path": p, "status": r.status_code, "body": r.text[:1500]})
            except Exception as e:
                res.append({"path": p, "error": repr(e)[:300]})
    out.mkdir(parents=True, exist_ok=True)
    (out / "probe.json").write_text(json.dumps(res, indent=1))
    for x in res:
        print(x.get("status"), x["path"], (x.get("body") or x.get("error", ""))[:120])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "report", "probe"])
    ap.add_argument("--out", default="data/polyus/ef_autobuyer")
    ap.add_argument("--minutes", type=float, default=170)
    ap.add_argument("--history", default="data/polyus/price_history")
    a = ap.parse_args()
    out = Path(a.out)
    if a.cmd == "probe":
        probe(out)
        return 0
    if a.cmd == "run":
        run(out, a.minutes)
    report(out, Path(a.history))
    return 0


if __name__ == "__main__":
    sys.exit(main())
