#!/usr/bin/env python3
"""Mr. H — the Coinbase "hopper", PAPER ONLY. No key, no orders, public endpoints only.

The question it answers: does hopping $4 between coins that are pumping *right now* on Coinbase make money
after real taker fees (0.9% each way on the Intro tier = 1.8% per hop)? Two profiles run on the same data:

  aggressive  enter on ONE 5-min impulse candle (>= +2% close/open, volume >= 3x the 2-h median), all-in,
              exit only on a 4% trailing stop from the high-water mark. Fastest-increase profile.
  standard    enter only when that candle also closes above the prior 2-hour high; 3% trail. The control.

Both: one position at a time, full bankroll each hop (compounding), fills at the touch (ask in, bid out),
spread gate, 24-h USD volume gate. Coinbase's `price_percentage_change_24h` field is NOT used (it was wrong on
4 of 6 coins checked on Nov 6); everything comes from candles and the ticker.

Beyond the two paper books, every signal is logged and later scored with its forward return at +15 m / +1 h /
+4 h and its max run-up / drawdown. That table is the real verdict: it does not depend on which coin the
single-position book happened to be sitting in.

    python scripts/mrh_paper.py run --out data/mrh --minutes 335     # scan every 5 min, publish-friendly state
    python scripts/mrh_paper.py report --out data/mrh                # -> data/mrh/MRH.md
    python scripts/mrh_paper.py selftest                              # no network

Files in --out: state.json (bankrolls, open positions, universe), trades.jsonl, signals.jsonl, scans.jsonl,
MRH.md, errors.jsonl (pb.errlog).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

BOT = "mrh"
API = "https://api.coinbase.com/api/v3/brokerage/market"
CANDLE_S = 300                     # FIVE_MINUTE
LOOKBACK = 24                      # 2 hours of 5-min candles behind the signal candle
TAKER_FEE = 0.009                  # Coinbase Advanced US Intro tier taker, Sept 2026
START_BANKROLL = 4.0
MIN_USD_VOL_24H = 100_000.0        # universe gate: 24-h volume in USD
MAX_SPREAD = 0.006                 # 0.6%: a wider spread means the "touch" fill is fiction
EXCLUDE_BASES = {"USDC", "USDT", "DAI", "PAX", "PYUSD", "GUSD", "USDP", "TUSD", "EURC", "USDS", "RLUSD",
                 "WBTC", "CBBTC", "CBETH", "WETH", "WSTETH", "RETH", "STETH", "PAXG", "XAUT", "BUSD"}

PROFILES = {
    # name: (min impulse close/open, min vol multiple, require close > prior 2h high, trailing stop)
    "aggressive": dict(impulse=0.02, vol_mult=3.0, need_2h_high=False, trail=0.04),
    "standard":   dict(impulse=0.01, vol_mult=3.0, need_2h_high=True,  trail=0.03),
    # same signal and trail as aggressive (variant_of: shares its signals, logs none of its own), but a position that
    # has not made a new high for swap_after_h hours is SOLD at the bid to take a fresh signal in another coin
    "aggressive_swap": dict(impulse=0.02, vol_mult=3.0, need_2h_high=False, trail=0.04, variant_of="aggressive", swap_after_h=2),
}
BASE_PROFILES = {n: p for n, p in PROFILES.items() if not p.get("variant_of")}
HORIZONS = {"r15m": 3, "r1h": 12, "r4h": 48}   # forward candles after the signal candle


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(d: datetime) -> str:
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


# ----------------------------------------------------------------------------------------------- data access

class Coinbase:
    """Public market-data endpoints. Paced to stay well under Coinbase's ~10 req/s public limit."""

    def __init__(self, pace_s: float = 0.12):
        import httpx
        self.cli = httpx.Client(timeout=20, headers={"User-Agent": "predictionbots-mrh/1 (paper research)"})
        self.pace_s = pace_s
        self._last = 0.0
        self.calls = 0

    def get(self, path: str, **params) -> dict:
        wait = self._last + self.pace_s - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        for attempt in range(4):
            self._last = time.monotonic()
            self.calls += 1
            r = self.cli.get(f"{API}{path}", params=params)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(1.5 * (attempt + 1))
                continue
            r.raise_for_status()
            return r.json()
        r.raise_for_status()
        return r.json()

    def products(self) -> list[dict]:
        out: list[dict] = []
        offset = 0
        while True:
            j = self.get("/products", product_type="SPOT", limit=250, offset=offset)
            batch = j.get("products", [])
            out.extend(batch)
            total = int(j.get("num_products") or 0)
            offset += len(batch)
            if not batch or (total and offset >= total) or len(batch) < 250:
                break
        return out

    def candles(self, pid: str, start: int, end: int) -> list[dict]:
        j = self.get(f"/products/{pid}/candles", start=str(start), end=str(end), granularity="FIVE_MINUTE")
        cs = [{k: float(c[k]) for k in ("low", "high", "open", "close", "volume")} | {"start": int(c["start"])}
              for c in j.get("candles", [])]
        cs.sort(key=lambda c: c["start"])
        return cs

    def ticker(self, pid: str) -> dict:
        j = self.get(f"/products/{pid}/ticker", limit=1)
        bid = float(j.get("best_bid") or 0)
        ask = float(j.get("best_ask") or 0)
        return {"bid": bid, "ask": ask}


# ----------------------------------------------------------------------------------------------- pure logic

def build_universe(products: list[dict]) -> list[dict]:
    """USD spot pairs, online, not stablecoins/wrappers, >= MIN_USD_VOL_24H. Sorted by USD volume, desc."""
    uni = []
    for p in products:
        pid = p.get("product_id", "")
        if not pid.endswith("-USD") or p.get("status") != "online" or p.get("trading_disabled") or p.get("view_only"):
            continue
        base = pid[:-4].upper()
        if base in EXCLUDE_BASES:
            continue
        try:
            price = float(p.get("price") or 0)
            vol = float(p.get("volume_24h") or 0)
            qmin = float(p.get("quote_min_size") or 1)
        except ValueError:
            continue
        usd_vol = price * vol
        if price <= 0 or usd_vol < MIN_USD_VOL_24H:
            continue
        uni.append({"id": pid, "usd_vol_24h": round(usd_vol), "quote_min": qmin})
    uni.sort(key=lambda u: -u["usd_vol_24h"])
    return uni


def closed_candles(cs: list[dict], t: datetime) -> list[dict]:
    """Drop the candle still forming at time t (and anything after it)."""
    cutoff = int(t.timestamp()) // CANDLE_S * CANDLE_S
    return [c for c in cs if c["start"] + CANDLE_S <= cutoff]


def evaluate(cs: list[dict], profile: dict) -> dict | None:
    """Signal on the last closed candle. Returns the signal facts or None."""
    if len(cs) < LOOKBACK + 1:
        return None
    sig, win = cs[-1], cs[-LOOKBACK - 1:-1]
    if sig["open"] <= 0:
        return None
    impulse = sig["close"] / sig["open"] - 1
    vols = [c["volume"] for c in win]
    med = statistics.median(vols)
    if med <= 0:
        return None
    vol_mult = sig["volume"] / med
    hi2h = max(c["high"] for c in win)
    above_2h = sig["close"] > hi2h
    ok = impulse >= profile["impulse"] and vol_mult >= profile["vol_mult"] and (above_2h or not profile["need_2h_high"])
    if not ok:
        return None
    return {"candle_start": sig["start"], "impulse": round(impulse, 4), "vol_mult": round(vol_mult, 2),
            "above_2h_high": above_2h, "close": sig["close"]}


def forward_score(cs_after: list[dict], ref_px: float) -> dict | None:
    """Forward returns from ref_px using closes of the candles after the signal candle; needs 48 of them."""
    if len(cs_after) < HORIZONS["r4h"]:
        return None
    out = {k: round(cs_after[n - 1]["close"] / ref_px - 1, 4) for k, n in HORIZONS.items()}
    hi = max(c["high"] for c in cs_after[:HORIZONS["r4h"]])
    lo = min(c["low"] for c in cs_after[:HORIZONS["r4h"]])
    out["max_up_4h"] = round(hi / ref_px - 1, 4)
    out["max_down_4h"] = round(lo / ref_px - 1, 4)
    # what a 4%-trail hop would have made: walk the candles with a trailing stop
    out["trail4_net"] = round(trail_pnl(cs_after[:HORIZONS["r4h"]], ref_px, 0.04), 4)
    return out


def trail_pnl(cs: list[dict], entry: float, trail: float) -> float:
    """Net return (after both taker fees) of entering at `entry` and exiting on a trailing stop evaluated on
    candle closes, or at the last close if never stopped. Conservative: the stop fires on the close, not intrabar."""
    hw = entry
    exit_px = cs[-1]["close"]
    for c in cs:
        hw = max(hw, c["close"])
        if c["close"] <= hw * (1 - trail):
            exit_px = c["close"]
            break
    return (exit_px / entry) * (1 - TAKER_FEE) / (1 + TAKER_FEE) - 1


@dataclass
class Position:
    pid: str
    entry_px: float       # ask paid
    qty: float
    cost: float           # cash out incl. fee
    hw: float             # high-water mark on bid
    t_in: str
    signal: dict
    hw_t: str = ""        # when the high-water mark was last raised (swap variants: staleness clock)


@dataclass
class Book:
    name: str
    bankroll: float = START_BANKROLL
    peak: float = START_BANKROLL
    pos: dict | None = None
    hops: int = 0
    wins: int = 0
    fees: float = 0.0

    def enter(self, pid: str, ask: float, t: datetime, signal: dict, quote_min: float) -> dict | None:
        if self.pos or ask <= 0 or self.bankroll < max(quote_min, 1.0):
            return None
        cost = self.bankroll
        qty = cost * (1 - TAKER_FEE) / ask
        fee = cost * TAKER_FEE
        self.fees += fee
        self.bankroll = 0.0
        self.pos = asdict(Position(pid, ask, qty, cost, ask, iso(t), signal, iso(t)))
        return {"t": iso(t), "book": self.name, "ev": "buy", "pid": pid, "px": ask, "qty": qty, "cost": cost, "fee": fee,
                "signal": signal}

    def mark(self, bid: float, t: datetime, trail: float, reason_force: str | None = None) -> dict | None:
        p = self.pos
        if not p or bid <= 0:
            return None
        if bid > p["hw"]:
            p["hw"], p["hw_t"] = bid, iso(t)
        stop = p["hw"] * (1 - trail)
        if reason_force is None and bid > stop:
            return None
        gross = p["qty"] * bid
        fee = gross * TAKER_FEE
        proceeds = gross - fee
        net = proceeds - p["cost"]
        self.fees += fee
        self.bankroll = proceeds
        self.peak = max(self.peak, self.bankroll)
        self.hops += 1
        self.wins += net > 0
        held_min = (t - parse_iso(p["t_in"])).total_seconds() / 60
        rec = {"t": iso(t), "book": self.name, "ev": "sell", "pid": p["pid"], "px": bid, "qty": p["qty"], "proceeds": proceeds,
               "fee": fee, "net": round(net, 4), "net_pct": round(net / p["cost"], 4), "entry_px": p["entry_px"], "hw": p["hw"],
               "held_min": round(held_min, 1), "reason": reason_force or "trail", "bankroll": round(self.bankroll, 4)}
        self.pos = None
        return rec


# ----------------------------------------------------------------------------------------------- state & io

def load_state(out: Path) -> dict:
    f = out / "state.json"
    st = json.loads(f.read_text()) if f.exists() else {}
    st.setdefault("books", {})
    for name in PROFILES:
        st["books"].setdefault(name, asdict(Book(name)))
    st.setdefault("universe", [])
    st.setdefault("universe_t", None)
    st.setdefault("scans", 0)
    st.setdefault("started", iso(now()))
    return st


def save_state(out: Path, st: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "state.json.tmp"
    tmp.write_text(json.dumps(st, indent=1))
    tmp.replace(out / "state.json")


def append(out: Path, name: str, rec: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    with (out / name).open("a") as fh:
        fh.write(json.dumps(rec) + "\n")


def read_jsonl(f: Path) -> list[dict]:
    if not f.exists():
        return []
    return [json.loads(l) for l in f.read_text().splitlines() if l.strip()]


# ----------------------------------------------------------------------------------------------- one scan

def swap_due(pos: dict, prof: dict, pid: str, t: datetime) -> bool:
    """Variant books only: the held coin has made no new high for swap_after_h hours and the signal is another coin."""
    h = prof.get("swap_after_h")
    if not h or pid == pos["pid"]:
        return False
    return (t - parse_iso(pos.get("hw_t") or pos["t_in"])) >= timedelta(hours=h)


def scan(cb: Coinbase, out: Path, st: dict, t: datetime | None = None) -> dict:
    t = t or now()
    books = {n: Book(**st["books"][n]) for n in PROFILES}
    # universe: refresh hourly
    if not st["universe"] or st["universe_t"] is None or (t - parse_iso(st["universe_t"])) > timedelta(hours=1):
        st["universe"] = build_universe(cb.products())
        st["universe_t"] = iso(t)
    uni = {u["id"]: u for u in st["universe"]}
    # 1) open positions first: mark on the live bid (an exit must not wait for the scan)
    tick_cache: dict[str, dict] = {}
    for name, bk in books.items():
        if bk.pos:
            pid = bk.pos["pid"]
            tick_cache.setdefault(pid, cb.ticker(pid))
            force = None if pid in uni else "delisted"
            rec = bk.mark(tick_cache[pid]["bid"], t, PROFILES[name]["trail"], force)
            if rec:
                append(out, "trades.jsonl", rec)
    # 2) scan candles for every coin in the universe
    end = int(t.timestamp()) // CANDLE_S * CANDLE_S
    start = end - CANDLE_S * (LOOKBACK + 3)
    n_sig = 0
    cand: dict[str, list[tuple[str, dict]]] = {}     # pid -> [(profile, signal)]
    regime: dict = {}                                 # BTC's own 1h / 2h move at scan time, stamped on every signal
    for u in st["universe"]:
        try:
            cs = closed_candles(cb.candles(u["id"], start, end), t)
        except Exception as e:  # one bad product must not kill the scan
            append(out, "scan_errors.jsonl", {"t": iso(t), "pid": u["id"], "err": str(e)[:300]})
            continue
        if u["id"] == "BTC-USD" and len(cs) >= 25 and cs[-13]["close"] > 0 and cs[-25]["close"] > 0:
            regime = {"btc_1h": round(cs[-1]["close"] / cs[-13]["close"] - 1, 4), "btc_2h": round(cs[-1]["close"] / cs[-25]["close"] - 1, 4)}
        for name, prof in BASE_PROFILES.items():
            sig = evaluate(cs, prof)
            if sig:
                cand.setdefault(u["id"], []).append((name, sig))
    # 3) per book, take the strongest candidate (biggest impulse) that passes the spread gate; variants share their base's signals
    for name, bk in books.items():
        prof = PROFILES[name]
        base = prof.get("variant_of", name)
        opts = sorted(((s["impulse"], pid, s) for pid, lst in cand.items() for n, s in lst if n == base), reverse=True)
        for _imp, pid, sig in opts:
            tick_cache.setdefault(pid, cb.ticker(pid))
            tk = tick_cache[pid]
            spread = (tk["ask"] - tk["bid"]) / tk["ask"] if tk["ask"] > 0 else 9
            taken, skip = False, None
            if spread > MAX_SPREAD:
                skip = "spread"
            elif bk.pos and not swap_due(bk.pos, prof, pid, t):
                skip = "in_position"
            else:
                if bk.pos:                                 # swap: dump the stale coin at the bid, take the fresh signal
                    cur = bk.pos["pid"]
                    tick_cache.setdefault(cur, cb.ticker(cur))
                    rec = bk.mark(tick_cache[cur]["bid"], t, prof["trail"], "swap")
                    if rec:
                        append(out, "trades.jsonl", rec)
                rec = bk.enter(pid, tk["ask"], t, {k: sig[k] for k in ("impulse", "vol_mult", "above_2h_high")}, uni[pid]["quote_min"])
                if rec:
                    append(out, "trades.jsonl", rec)
                    taken = True
            if base == name:                               # one signal record per base profile (variants log none)
                srec = {"t": iso(t), "profile": name, "pid": pid, **sig, "bid": tk["bid"], "ask": tk["ask"], "spread": round(spread, 4),
                        "hour_utc": t.hour, **regime, "taken": taken, "scored": False}
                if skip:
                    srec["skip"] = skip
                append(out, "signals.jsonl", srec)
                n_sig += 1
    st["books"] = {n: asdict(b) for n, b in books.items()}
    st["scans"] += 1
    st["last_scan"] = iso(t)
    summary = {"t": iso(t), "universe": len(st["universe"]), "signals": n_sig, "calls": cb.calls,
               "bankroll": {n: round(b.bankroll if not b.pos else b.pos["qty"] * tick_cache.get(b.pos["pid"], {}).get("bid", b.pos["entry_px"]), 4)
                            for n, b in books.items()}}
    append(out, "scans.jsonl", summary)
    save_state(out, st)
    return summary


def score_signals(cb: Coinbase, out: Path, t: datetime | None = None, limit: int = 60) -> int:
    """Fill in forward returns for signals older than 4 h. Rewrites signals.jsonl."""
    t = t or now()
    f = out / "signals.jsonl"
    sigs = read_jsonl(f)
    done = 0
    cache: dict[tuple[str, int], list[dict]] = {}
    for s in sigs:
        if s.get("scored") or done >= limit:
            continue
        st0 = int(s["candle_start"])
        if t.timestamp() < st0 + CANDLE_S * (HORIZONS["r4h"] + 2):
            continue
        key = (s["pid"], st0)
        try:
            if key not in cache:
                cache[key] = cb.candles(s["pid"], st0 + CANDLE_S, st0 + CANDLE_S * (HORIZONS["r4h"] + 1))
            after = [c for c in cache[key] if c["start"] > st0]
            fs = forward_score(after, s["ask"] if s.get("ask") else s["close"])
        except Exception as e:
            fs = None
            append(out, "scan_errors.jsonl", {"t": iso(t), "pid": s["pid"], "err": f"score: {e}"[:300]})
        if fs:
            s.update(fs)
            s["scored"] = True
            done += 1
    if done:
        f.write_text("".join(json.dumps(s) + "\n" for s in sigs))
    return done


# ----------------------------------------------------------------------------------------------- report

def report(out: Path) -> str:
    st = load_state(out)
    trades = read_jsonl(out / "trades.jsonl")
    sigs = read_jsonl(out / "signals.jsonl")
    scans = read_jsonl(out / "scans.jsonl")
    L = [f"# Mr. H — Coinbase hopper, PAPER\n", f"Updated {iso(now())} · scans {st['scans']} · universe {len(st['universe'])} coins "
         f"(USD pairs with ≥ ${MIN_USD_VOL_24H/1000:.0f}k 24-h volume) · fees {TAKER_FEE*100:.1f}% taker each way · start ${START_BANKROLL:.2f}\n"]
    L.append("## Books (one position at a time, all-in every hop)\n")
    L.append("| profile | bankroll | vs start | peak | hops | win % | avg net/hop | fees paid | open |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for name in PROFILES:
        b = st["books"][name]
        sells = [x for x in trades if x["book"] == name and x["ev"] == "sell"]
        last_mark = next((s["bankroll"].get(name) for s in reversed(scans) if s.get("bankroll")), None)
        val = last_mark if b["pos"] and last_mark is not None else b["bankroll"]
        avg = statistics.mean([x["net_pct"] for x in sells]) if sells else 0.0
        wr = (b["wins"] / b["hops"] * 100) if b["hops"] else 0.0
        open_s = f"{b['pos']['pid']} @ {b['pos']['entry_px']:.6g}" if b["pos"] else "—"
        L.append(f"| {name} | ${val:.2f} | {(val/START_BANKROLL-1)*100:+.1f}% | ${b['peak']:.2f} | {b['hops']} | {wr:.0f}% | {avg*100:+.2f}% | ${b['fees']:.3f} | {open_s} |")
    L.append("")
    L.append("## Signal forward returns (every signal, whether or not a book took it)\n")
    L.append("| profile | signals | scored | median +15m | median +1h | median +4h | % beat 1.8% at +1h | median 4%-trail hop net | max run-up (med) | max drawdown (med) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for name in BASE_PROFILES:
        ss = [s for s in sigs if s["profile"] == name]
        sc = [s for s in ss if s.get("scored")]
        def med(k): return statistics.median([s[k] for s in sc]) * 100 if sc else float("nan")
        beat = (sum(s["r1h"] > 2 * TAKER_FEE for s in sc) / len(sc) * 100) if sc else float("nan")
        L.append(f"| {name} | {len(ss)} | {len(sc)} | {med('r15m'):+.2f}% | {med('r1h'):+.2f}% | {med('r4h'):+.2f}% | {beat:.0f}% | {med('trail4_net'):+.2f}% | {med('max_up_4h'):+.2f}% | {med('max_down_4h'):+.2f}% |")
    L.append("")
    L.append("## Aggressive signals by BTC regime (BTC's own move in the hour before the signal)\n")
    L.append("| BTC 1h | signals | median +1h | median 4%-trail hop net | % beat 1.8% at +1h |")
    L.append("|---|---|---|---|---|")
    reg = [s for s in sigs if s["profile"] == "aggressive" and s.get("scored") and "btc_1h" in s]
    for label, lo, hi in (("≤ −0.5% (downdraft)", -9, -0.005), ("−0.5% … +0.5% (flat)", -0.005, 0.005), ("≥ +0.5% (bid under the market)", 0.005, 9)):
        g = [s for s in reg if lo <= s["btc_1h"] < hi]
        if not g:
            L.append(f"| {label} | 0 | — | — | — |")
            continue
        L.append(f"| {label} | {len(g)} | {statistics.median([s['r1h'] for s in g])*100:+.2f}% | {statistics.median([s['trail4_net'] for s in g])*100:+.2f}% | "
                 f"{sum(s['r1h'] > 2 * TAKER_FEE for s in g) / len(g) * 100:.0f}% |")
    L.append("")
    sc_all = [s for s in sigs if s.get("scored") and s["profile"] == "aggressive"]
    hops_all = [x for x in trades if x["ev"] == "sell" and x["book"] == "aggressive"]
    L.append("## Verdict\n")
    if len(sc_all) < 40 or len(hops_all) < 30:
        L.append(f"**Not yet.** Needs 40 scored aggressive signals ({len(sc_all)} so far) and 30 closed aggressive hops "
                 f"({len(hops_all)} so far) before this says anything. Until then every number above is noise.")
    else:
        m = statistics.median([s["trail4_net"] for s in sc_all]) * 100
        b = st["books"]["aggressive"]
        L.append(f"Median 4%-trail hop nets {m:+.2f}% after fees across {len(sc_all)} signals; the aggressive book is "
                 f"{(b['bankroll']/START_BANKROLL-1)*100:+.1f}% after {b['hops']} hops. "
                 + ("**Positive expectancy on paper — discuss funding the $4.**" if m > 0 and b["bankroll"] > START_BANKROLL
                    else "**No edge after fees. Do not fund.**"))
    L.append("")
    L.append("## Last 20 hops\n")
    L.append("| time (UTC) | book | coin | in | out | held | net | reason | bankroll |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for x in [x for x in trades if x["ev"] == "sell"][-20:]:
        L.append(f"| {x['t'][5:16]} | {x['book']} | {x['pid'][:-4]} | {x['entry_px']:.6g} | {x['px']:.6g} | {x['held_min']:.0f} m | {x['net_pct']*100:+.2f}% | {x['reason']} | ${x['bankroll']:.2f} |")
    L.append("")
    L.append("## Last 15 signals\n")
    L.append("| time (UTC) | profile | coin | impulse | vol× | >2h high | spread | taken | +1h | +4h |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for s in sigs[-15:]:
        r1 = f"{s['r1h']*100:+.1f}%" if s.get("scored") else "…"
        r4 = f"{s['r4h']*100:+.1f}%" if s.get("scored") else "…"
        L.append(f"| {s['t'][5:16]} | {s['profile']} | {s['pid'][:-4]} | {s['impulse']*100:+.1f}% | {s['vol_mult']:.1f} | {'y' if s['above_2h_high'] else 'n'} | {s['spread']*100:.2f}% | {'y' if s['taken'] else s.get('skip','n')} | {r1} | {r4} |")
    txt = "\n".join(L) + "\n"
    (out / "MRH.md").write_text(txt)
    return txt


# ----------------------------------------------------------------------------------------------- runner

def run(out: Path, minutes: float) -> None:
    from pb.errlog import guard
    with guard(BOT, out=out):
        cb = Coinbase()
        st = load_state(out)
        t_end = time.time() + minutes * 60
        while True:
            t0 = time.time()
            s = scan(cb, out, st)
            print(f"{s['t']} universe={s['universe']} signals={s['signals']} calls={s['calls']} bankroll={s['bankroll']}", flush=True)
            try:
                n = score_signals(cb, out)
                if n:
                    print(f"scored {n} signals", flush=True)
            except Exception as e:
                append(out, "scan_errors.jsonl", {"t": iso(now()), "err": f"score_signals: {e}"[:300]})
            report(out)
            if time.time() + CANDLE_S > t_end:
                break
            # sleep to 15 s after the next 5-min boundary (gives Coinbase time to close the candle)
            nxt = (int(time.time()) // CANDLE_S + 1) * CANDLE_S + 15
            time.sleep(max(1.0, nxt - time.time()))


# ----------------------------------------------------------------------------------------------- selftest

class FakeCB:
    """Deterministic fake: one coin pumps on the signal candle, then drifts; others flat."""

    def __init__(self):
        self.calls = 0
        self.t0 = 1_800_000_000
        self.bids = {"PUMP-USD": 1.10, "FLAT-USD": 10.0}

    def products(self):
        return [{"product_id": "PUMP-USD", "status": "online", "price": "1.1", "volume_24h": "500000", "quote_min_size": "1"},
                {"product_id": "FLAT-USD", "status": "online", "price": "10", "volume_24h": "500000", "quote_min_size": "1"},
                {"product_id": "USDC-USD", "status": "online", "price": "1", "volume_24h": "9e9", "quote_min_size": "1"},
                {"product_id": "TINY-USD", "status": "online", "price": "1", "volume_24h": "10", "quote_min_size": "1"},
                {"product_id": "BTC-EUR", "status": "online", "price": "90000", "volume_24h": "100", "quote_min_size": "1"}]

    def candles(self, pid, start, end):
        cs = []
        for s in range(start, end, CANDLE_S):
            i = (s - self.t0) // CANDLE_S
            if pid == "PUMP-USD":
                px = 1.0 if i < 40 else 1.10 if i == 40 else 1.10 * (1 + 0.002 * (i - 40))
                o = 1.0 if i <= 40 else px / (1 + 0.002)
                cs.append({"start": s, "open": o, "close": px, "high": max(o, px) * 1.001, "low": min(o, px) * 0.999,
                           "volume": 1000.0 if i == 40 else 100.0})
            else:
                cs.append({"start": s, "open": 10.0, "close": 10.0, "high": 10.01, "low": 9.99, "volume": 100.0})
        return cs

    def ticker(self, pid):
        b = self.bids[pid]
        return {"bid": b, "ask": b * 1.001}


def selftest() -> None:
    import tempfile
    out = Path(tempfile.mkdtemp()) / "mrh"
    cb = FakeCB()
    st = load_state(out)
    t = datetime.fromtimestamp(cb.t0 + CANDLE_S * 41 + 20, tz=timezone.utc)
    s = scan(cb, out, st, t)
    assert s["universe"] == 2, s                                   # USDC, TINY (volume) and BTC-EUR filtered
    assert s["signals"] == 2, s                                    # PUMP fires on both profiles
    for n in PROFILES:
        assert st["books"][n]["pos"] and st["books"][n]["pos"]["pid"] == "PUMP-USD", st["books"][n]
    # price runs to 1.30 then falls to 1.24 (-4.6%): aggressive (4%) and standard (3%) both exit
    cb.bids["PUMP-USD"] = 1.30
    scan(cb, out, st, t + timedelta(minutes=5))
    assert all(st["books"][n]["pos"] for n in PROFILES)
    cb.bids["PUMP-USD"] = 1.24
    scan(cb, out, st, t + timedelta(minutes=10))
    for n in PROFILES:
        b = st["books"][n]
        assert b["pos"] is None and b["hops"] == 1 and b["wins"] == 1, b
        expect = 4.0 * (1 - TAKER_FEE) / (1.10 * 1.001) * 1.24 * (1 - TAKER_FEE)
        assert abs(b["bankroll"] - expect) < 1e-9, (b["bankroll"], expect)
    # forward scoring: 48 candles after the signal exist in the fake
    n = score_signals(cb, out, t + timedelta(hours=5))
    assert n == 2, n
    sg = read_jsonl(out / "signals.jsonl")
    assert all(s["scored"] and s["r4h"] > 0 for s in sg), sg
    assert abs(trail_pnl([{"close": 1.0}, {"close": 1.2}, {"close": 1.1}], 1.0, 0.05) - (1.1 * (1 - TAKER_FEE) / (1 + TAKER_FEE) - 1)) < 1e-12
    txt = report(out)
    assert "Not yet." in txt and "PUMP" in txt and "BTC regime" in txt
    # swap variant: a stale FLAT position (no new high for 3 h) is swapped into a fresh PUMP signal; the plain
    # aggressive book, holding the same stale coin, just sits ("in_position"); signals.jsonl gets no variant records
    out2 = Path(tempfile.mkdtemp()) / "mrh"
    cb2 = FakeCB()
    cb2.bids["FLAT-USD"] = 10.0
    st2 = load_state(out2)
    t0 = datetime.fromtimestamp(cb2.t0 + CANDLE_S * 41 + 20, tz=timezone.utc)
    stale = t0 - timedelta(hours=3)
    for n in ("aggressive", "aggressive_swap"):
        bk = Book(**st2["books"][n])
        bk.enter("FLAT-USD", 10.0, stale, {"impulse": 0.02, "vol_mult": 3.0, "above_2h_high": False}, 1.0)
        st2["books"][n] = asdict(bk)
    st2["universe"] = build_universe(cb2.products()); st2["universe_t"] = iso(t0)
    scan(cb2, out2, st2, t0)
    assert st2["books"]["aggressive"]["pos"]["pid"] == "FLAT-USD", st2["books"]["aggressive"]
    sw = st2["books"]["aggressive_swap"]
    assert sw["pos"]["pid"] == "PUMP-USD" and sw["hops"] == 1, sw
    tr = [x for x in read_jsonl(out2 / "trades.jsonl") if x["book"] == "aggressive_swap"]
    assert [x["ev"] for x in tr[-2:]] == ["sell", "buy"] and tr[-2]["reason"] == "swap" and tr[-2]["pid"] == "FLAT-USD", tr
    sg = read_jsonl(out2 / "signals.jsonl")
    assert {x["profile"] for x in sg} == {"aggressive", "standard"} and all("hour_utc" in x for x in sg), sg
    assert next(x for x in sg if x["profile"] == "aggressive")["skip"] == "in_position"
    # a fresh high resets the staleness clock: no swap right after a new high
    cb2.bids["PUMP-USD"] = 1.30
    scan(cb2, out2, st2, t0 + timedelta(minutes=5))
    assert st2["books"]["aggressive_swap"]["pos"]["hw_t"] == iso(t0 + timedelta(minutes=5))
    print("selftest ok:", {n: round(st["books"][n]["bankroll"], 4) for n in PROFILES})


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--out", default="data/mrh"); r.add_argument("--minutes", type=float, default=335)
    p = sub.add_parser("report"); p.add_argument("--out", default="data/mrh")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        run(Path(a.out), a.minutes)
    elif a.cmd == "report":
        print(report(Path(a.out)))
    else:
        selftest()


if __name__ == "__main__":
    main()
