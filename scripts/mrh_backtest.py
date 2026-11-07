#!/usr/bin/env python3
"""Mr. H BACKTEST — replay the hopper's signal rule over Coinbase's 5-minute history. Public data, no key.

Why: the paper twin scores one to three aggressive signals a day, so its 40-signal verdict is weeks away while the
live book pays tuition at 1.8% a hop. The same rule over `--days` of history for the whole universe yields hundreds
of signals in minutes. It is the same code path as paper and live: build_universe, evaluate, forward_score and
trail_pnl are imported from scripts/mrh_paper.py — nothing is re-implemented, so a bug there is a bug here.

What it scores, per signal (every signal, whether or not a one-position book could have taken it):
  +15 m / +1 h / +4 h return from the signal close, max run-up / drawdown over 4 h, and the net of a hop entered at
  the signal close and exited on a trailing stop of 3 / 4 / 6 / 8 / 12 % (fees both ways, like paper) — plus the
  hop's net for a *continuation* entry: wait one candle, enter at its close only if it held at or above the signal
  close (the hypothesis that the impulse candle itself is the local top).
  Each signal also carries hour_utc and BTC's own 1-h / 2-h move at that moment (regime), and `fresh` = no signal
  from the same coin in the previous hour (consecutive candles of one spike are one event, not twelve).

What it cannot see: the live spread gate (<= 0.6% needs a live ticker), so every historical signal is scored as if
the spread had passed — live takes fewer and pays up to the spread on top of the fees shown. Fills are at candle
closes, stops fire on closes (conservative on the way out, generous on the way in). Coinbase omits 5-min candles
with no trades, so on the thinnest coins "48 candles" can span more than 4 hours.

    python scripts/mrh_backtest.py run --out data/mrh-backtest [--days 30] [--top 0]   # 0 = whole universe
    python scripts/mrh_backtest.py report --out data/mrh-backtest                      # -> BACKTEST.md
    python scripts/mrh_backtest.py selftest                                          # no network

Files in --out: backtest_signals.jsonl (one line per signal, scored), coins.json (universe + candle counts),
BACKTEST.md (the report). Candles are cached in --out/candles/ and are not meant to be published.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mrh_paper as paper  # noqa: E402
from mrh_paper import (BASE_PROFILES, CANDLE_S, HORIZONS, LOOKBACK, TAKER_FEE, build_universe,  # noqa: E402
                       evaluate, forward_score, trail_pnl)

TRAILS = (0.03, 0.04, 0.06, 0.08, 0.12)
FWD = HORIZONS["r4h"]                 # candles scored after the signal candle
FRESH_GAP = 12                        # a signal is "fresh" if the coin had none in the previous hour
CHUNK = 300                           # candles per request (Coinbase allows 350)
ROUND_TRIP = (1 - TAKER_FEE) / (1 + TAKER_FEE)


def now() -> datetime:
    return datetime.now(timezone.utc)


# ----------------------------------------------------------------------------------------------- data

def fetch_history(cb, pid: str, start: int, end: int) -> list[dict]:
    """All 5-min candles for pid in [start, end), in CHUNK-sized requests, deduped and sorted."""
    seen: dict[int, dict] = {}
    t0 = start
    while t0 < end:
        t1 = min(end, t0 + CHUNK * CANDLE_S)
        for c in cb.candles(pid, t0, t1 - 1):
            seen[c["start"]] = c
        t0 = t1
    return [seen[k] for k in sorted(seen)]


def load_candles(cb, out: Path, pid: str, start: int, end: int) -> list[dict]:
    cache = out / "candles" / f"{pid}.json"
    if cache.exists():
        try:
            j = json.loads(cache.read_text())
            if j.get("start") == start and j.get("end") == end:
                return j["candles"]
        except (ValueError, KeyError):
            pass
    cs = fetch_history(cb, pid, start, end)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"start": start, "end": end, "candles": cs}))
    return cs


# ----------------------------------------------------------------------------------------------- replay

def continuation(cs_after: list[dict], sig_close: float) -> dict:
    """Wait one candle; enter at its close only if it held >= the signal close. Trail nets from that entry."""
    if not cs_after:
        return {}
    c1 = cs_after[0]
    out = {"r_next": round(c1["close"] / sig_close - 1, 4), "held": c1["close"] >= sig_close}
    rest = cs_after[1:1 + FWD]
    if out["held"] and len(rest) >= FWD:
        for t in TRAILS:
            out[f"cont_trail{int(t * 100)}_net"] = round(trail_pnl(rest, c1["close"], t), 4)
    return out


def replay(pid: str, cs: list[dict], btc_close: dict[int, float]) -> list[dict]:
    """Every signal of every base profile on this coin's history, scored where 48 forward candles exist."""
    sigs: list[dict] = []
    last_at: dict[str, int] = {}
    for i in range(LOOKBACK, len(cs)):
        window = cs[i - LOOKBACK:i + 1]
        for name, prof in BASE_PROFILES.items():
            s = evaluate(window, prof)
            if not s:
                continue
            fresh = (i - last_at.get(name, -10 ** 9)) > FRESH_GAP
            last_at[name] = i
            st0 = s["candle_start"]
            rec = {"pid": pid, "profile": name, "t": datetime.fromtimestamp(st0, timezone.utc).strftime("%Y-%m-%dT%H:%M"),
                   "hour_utc": datetime.fromtimestamp(st0, timezone.utc).hour, "fresh": fresh, **s}
            b0, b1, b2 = btc_close.get(st0), btc_close.get(st0 - 12 * CANDLE_S), btc_close.get(st0 - 24 * CANDLE_S)
            rec["btc_1h"] = round(b0 / b1 - 1, 4) if b0 and b1 else None
            rec["btc_2h"] = round(b0 / b2 - 1, 4) if b0 and b2 else None
            after = cs[i + 1:i + 1 + FWD + 1]
            fs = forward_score(after[:FWD], s["close"])
            if fs:
                rec.update(fs)
                for t in TRAILS:
                    rec[f"trail{int(t * 100)}_net"] = round(trail_pnl(after[:FWD], s["close"], t), 4)
                rec["hold4h_net"] = round((1 + fs["r4h"]) * ROUND_TRIP - 1, 4)
                rec.update(continuation(after, s["close"]))
                rec["scored"] = True
            else:
                rec["scored"] = False
            sigs.append(rec)
    return sigs


def run(out: Path, days: int, top: int, cb=None) -> dict:
    cb = cb or paper.Coinbase()
    out.mkdir(parents=True, exist_ok=True)
    end = int(now().timestamp()) // CANDLE_S * CANDLE_S            # the candle still forming is excluded
    start = end - days * 86400 - (LOOKBACK + 1) * CANDLE_S         # lookback before the window
    uni = build_universe(cb.products())
    if top:
        uni = uni[:top]
    pids = [u["id"] for u in uni]
    if "BTC-USD" not in pids:
        pids.append("BTC-USD")
    btc = load_candles(cb, out, "BTC-USD", start, end)
    btc_close = {c["start"]: c["close"] for c in btc}
    coins, sigs = [], []
    t_start = time.monotonic()
    for n, u in enumerate(uni, 1):
        pid = u["id"]
        try:
            cs = btc if pid == "BTC-USD" else load_candles(cb, out, pid, start, end)
        except Exception as e:  # one dead product must not sink the run
            coins.append({**u, "candles": 0, "error": str(e)[:200]})
            continue
        found = replay(pid, cs, btc_close)
        sigs.extend(found)
        coins.append({**u, "candles": len(cs), "signals": len(found)})
        print(f"[{n}/{len(uni)}] {pid}: {len(cs)} candles, {len(found)} signals, {cb.calls} calls, "
              f"{time.monotonic() - t_start:.0f}s", flush=True)
    meta = {"generated": now().strftime("%Y-%m-%dT%H:%M:%SZ"), "days": days, "top": top,
            "window_start": datetime.fromtimestamp(start + (LOOKBACK + 1) * CANDLE_S, timezone.utc).strftime("%Y-%m-%d %H:%M"),
            "window_end": datetime.fromtimestamp(end, timezone.utc).strftime("%Y-%m-%d %H:%M"),
            "universe": len(uni), "calls": cb.calls, "seconds": round(time.monotonic() - t_start)}
    (out / "coins.json").write_text(json.dumps({"meta": meta, "coins": coins}, indent=1))
    (out / "backtest_signals.jsonl").write_text("".join(json.dumps(s) + "\n" for s in sigs))
    (out / "BACKTEST.md").write_text(report(out))
    return meta


# ----------------------------------------------------------------------------------------------- report

def pct(x: float | None, d: int = 2) -> str:
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x * 100:+.{d}f}%"


def pc(x: float | None) -> str:
    """A share (win rate, held rate): no sign."""
    return "—" if x is None else f"{x * 100:.0f}%"


def med(xs: list[float]) -> float | None:
    return statistics.median(xs) if xs else None


def mean(xs: list[float]) -> float | None:
    return statistics.fmean(xs) if xs else None


def geo(xs: list[float]) -> float | None:
    """Geometric mean net per hop — what all-in compounding actually earns (a +10% then -10% pair is -1%)."""
    if not xs or any(x <= -1 for x in xs):
        return None
    return math.exp(statistics.fmean(math.log1p(x) for x in xs)) - 1


def share(xs: list[float], thr: float = 0.0) -> float | None:
    return (sum(1 for x in xs if x > thr) / len(xs)) if xs else None


def vals(rows: list[dict], key: str) -> list[float]:
    return [r[key] for r in rows if r.get(key) is not None]


def trail_table(rows: list[dict], prefix: str = "trail") -> list[str]:
    lines = ["| trail | hops | win % | mean net/hop | median net/hop | geo mean/hop (compounding) | worst | best |",
             "|---|---|---|---|---|---|---|---|"]
    for t in TRAILS:
        xs = vals(rows, f"{prefix}{int(t * 100)}_net")
        if not xs:
            continue
        lines.append(f"| {int(t * 100)}% | {len(xs)} | {pc(share(xs))} | {pct(mean(xs))} | {pct(med(xs))} | "
                     f"{pct(geo(xs))} | {pct(min(xs))} | {pct(max(xs))} |")
    xs = vals(rows, "hold4h_net")
    if xs and prefix == "trail":
        lines.append(f"| hold 4 h, no stop | {len(xs)} | {pc(share(xs))} | {pct(mean(xs))} | {pct(med(xs))} | "
                     f"{pct(geo(xs))} | {pct(min(xs))} | {pct(max(xs))} |")
    return lines


def breakdown(rows: list[dict], label: str, keyf, order: list[str]) -> list[str]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        k = keyf(r)
        if k is not None:
            groups[k].append(r)
    lines = [f"| {label} | signals | median +1h | median +4h | mean trail-4% net | win % (4% trail) | mean trail-8% net |",
             "|---|---|---|---|---|---|---|"]
    for k in order:
        g = groups.get(k)
        if not g:
            continue
        t4, t8 = vals(g, "trail4_net"), vals(g, "trail8_net")
        lines.append(f"| {k} | {len(g)} | {pct(med(vals(g, 'r1h')))} | {pct(med(vals(g, 'r4h')))} | {pct(mean(t4))} | "
                     f"{pc(share(t4))} | {pct(mean(t8))} |")
    return lines


def bucket(x: float | None, edges: list[tuple[float, str]], last: str) -> str | None:
    if x is None:
        return None
    for edge, name in edges:
        if x < edge:
            return name
    return last


def verdict(rows: list[dict]) -> list[str]:
    """Plain words from the fresh aggressive signals. Says what the numbers say, nothing more."""
    if len(rows) < 30:
        return [f"**Too few fresh aggressive signals ({len(rows)}) to say anything.** Widen `--days`."]
    out = []
    t4 = vals(rows, "trail4_net")
    best_t, best_g = None, None
    for t in TRAILS:
        g = geo(vals(rows, f"trail{int(t * 100)}_net"))
        if g is not None and (best_g is None or g > best_g):
            best_t, best_g = t, g
    sign = "positive" if (mean(t4) or 0) > 0 else "negative"
    out.append(f"- The live rule (4% trail) nets a **{sign}** mean of **{pct(mean(t4))}** per hop over {len(t4)} fresh "
               f"signals, {pc(share(t4))} of them winners; compounding all-in that is **{pct(geo(t4))}** per hop.")
    if best_t is not None:
        out.append(f"- Best trail width by compounded net: **{int(best_t * 100)}%** at **{pct(best_g)}** per hop"
                   + (" — the live 4% is already the best." if best_t == 0.04 else " (live uses 4%)."))
    held = [r for r in rows if r.get("held")]
    c4 = vals(held, "cont_trail4_net")
    if c4:
        out.append(f"- Continuation entry (wait one candle, enter only if it held): {len(held)}/{len(rows)} "
                   f"({pc(len(held) / len(rows))}) held; those net **{pct(mean(c4))}** mean / **{pct(geo(c4))}** "
                   f"compounded per hop on the 4% trail vs {pct(mean(t4))} / {pct(geo(t4))} entering on the spike.")
    rn = vals(rows, "r_next")
    if rn:
        out.append(f"- The candle right after the impulse closes a median **{pct(med(rn))}** from the signal close "
                   f"({pc(share(rn))} of the time above it) — the size of the immediate give-back.")
    r1 = vals(rows, "r1h")
    out.append(f"- {pc(share(r1, 2 * TAKER_FEE))} of signals beat the 1.8% round-trip fee at +1 h.")
    return out


def report(out: Path) -> str:
    sigs = [json.loads(l) for l in (out / "backtest_signals.jsonl").read_text().splitlines() if l.strip()]
    meta = json.loads((out / "coins.json").read_text())["meta"]
    scored = [s for s in sigs if s.get("scored")]
    L = [f"# Mr. H — Coinbase hopper, BACKTEST ({meta['days']} days)", "",
         f"Generated {meta['generated']} · window {meta['window_start']} → {meta['window_end']} UTC · universe "
         f"{meta['universe']} coins · {len(sigs)} signals, {len(scored)} scored · fees {TAKER_FEE * 100:.1f}% taker each way "
         f"(the ≤0.6% live spread comes on top) · fills and stops on 5-min closes · {meta['calls']} API calls in {meta['seconds']}s",
         "", "## Signal forward returns (every signal)", "",
         "| profile | signals | fresh | median +15m | median +1h | median +4h | % beat 1.8% at +1h | mean trail-4% net | "
         "median trail-4% net | max run-up (med) | max drawdown (med) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name in BASE_PROFILES:
        g = [s for s in scored if s["profile"] == name]
        allg = [s for s in sigs if s["profile"] == name]
        if not allg:
            continue
        L.append(f"| {name} | {len(allg)} | {sum(1 for s in allg if s['fresh'])} | {pct(med(vals(g, 'r15m')))} | "
                 f"{pct(med(vals(g, 'r1h')))} | {pct(med(vals(g, 'r4h')))} | {pc(share(vals(g, 'r1h'), 2 * TAKER_FEE))} | "
                 f"{pct(mean(vals(g, 'trail4_net')))} | {pct(med(vals(g, 'trail4_net')))} | {pct(med(vals(g, 'max_up_4h')))} | "
                 f"{pct(med(vals(g, 'max_down_4h')))} |")
    fresh = [s for s in scored if s["profile"] == "aggressive" and s["fresh"]]
    L += ["", "## Verdict (fresh aggressive signals — one per spike)", ""] + verdict(fresh)
    L += ["", "## Trail width — fresh aggressive signals, entered at the signal close", ""] + trail_table(fresh)
    held = [s for s in fresh if s.get("held")]
    L += ["", f"## Continuation entry — wait one candle, enter only if it held ({len(held)} of {len(fresh)} held)", ""]
    L += trail_table(held, "cont_trail")
    L += ["", "## Where the edge is (or isn't) — fresh aggressive signals, 4% trail", ""]
    L += breakdown(fresh, "BTC 2-h regime at signal", lambda r: bucket(r.get("btc_2h"), [(-0.01, "BTC down >1%"), (0.01, "BTC flat")], "BTC up >1%"),
                   ["BTC down >1%", "BTC flat", "BTC up >1%"]) + [""]
    L += breakdown(fresh, "impulse size", lambda r: bucket(r.get("impulse"), [(0.03, "2–3%"), (0.05, "3–5%"), (0.10, "5–10%")], "10%+"),
                   ["2–3%", "3–5%", "5–10%", "10%+"]) + [""]
    L += breakdown(fresh, "volume multiple", lambda r: bucket(r.get("vol_mult"), [(5, "3–5×"), (10, "5–10×"), (30, "10–30×")], "30×+"),
                   ["3–5×", "5–10×", "10–30×", "30×+"]) + [""]
    L += breakdown(fresh, "closed above prior 2-h high", lambda r: "yes" if r.get("above_2h_high") else "no", ["yes", "no"]) + [""]
    L += breakdown(fresh, "hour (UTC)", lambda r: bucket(r.get("hour_utc"), [(6, "00–05"), (12, "06–11"), (18, "12–17")], "18–23"),
                   ["00–05", "06–11", "12–17", "18–23"])
    per: dict[str, list[dict]] = defaultdict(list)
    for s in fresh:
        per[s["pid"]].append(s)
    top = sorted(per.items(), key=lambda kv: -len(kv[1]))[:15]
    L += ["", "## Noisiest coins (fresh aggressive signals)", "", "| coin | signals | mean trail-4% net | win % | median +4h |", "|---|---|---|---|---|"]
    for pid, g in top:
        t4 = vals(g, "trail4_net")
        L.append(f"| {pid[:-4]} | {len(g)} | {pct(mean(t4))} | {pc(share(t4))} | {pct(med(vals(g, 'r4h')))} |")
    L += ["", "Same signal code as paper and live (`scripts/mrh_paper.py`: evaluate / forward_score / trail_pnl). "
          "Spread is not modelled; subtract up to 0.6% per hop. Paper twin and live book: `mrh/MRH.md`, `mrh-live/LIVE.md`.", ""]
    return "\n".join(L)


# ----------------------------------------------------------------------------------------------- selftest

def _synthetic(spike_at: int, n: int = 400, run_candles: int = 10, step: float = 0.01) -> list[dict]:
    """Flat tape, one +5% impulse on 10x volume at spike_at, then `run_candles` of +step each, then a slow fade."""
    cs, px = [], 1.0
    for i in range(n):
        o = px
        if i == spike_at:
            px = o * 1.05
            vol = 10.0
        elif spike_at < i <= spike_at + run_candles:
            px = o * (1 + step)
            vol = 2.0
        elif i > spike_at + run_candles:
            px = o * 0.998
            vol = 1.0
        else:
            vol = 1.0
        cs.append({"start": 1_700_000_000 + i * CANDLE_S, "open": o, "close": px, "high": max(o, px) * 1.001,
                   "low": min(o, px) * 0.999, "volume": vol})
    return cs


def selftest() -> None:
    cs = _synthetic(100)
    btc = {c["start"]: 1.0 for c in cs}
    sigs = replay("TEST-USD", cs, btc)
    agg = [s for s in sigs if s["profile"] == "aggressive"]
    assert len(agg) == 1 and agg[0]["fresh"] and agg[0]["scored"], agg
    s = agg[0]
    assert abs(s["impulse"] - 0.05) < 1e-9 and s["vol_mult"] == 10.0 and s["hour_utc"] == datetime.fromtimestamp(s["candle_start"], timezone.utc).hour
    assert s["btc_1h"] == 0.0 and s["btc_2h"] == 0.0
    # ten +1% candles then a slow fade: the 4% trail exits in the fade well above entry; the 12% trail never fires and
    # rides the whole fade down to the last close, so it keeps less — but still more than the fees
    assert s["trail4_net"] > 0.03 and 0 < s["trail12_net"] < s["trail4_net"], s
    assert s["held"] and abs(s["r_next"] - 0.01) < 1e-9 and s["cont_trail4_net"] > 0, s
    assert s["r1h"] > 0.09 and s["max_down_4h"] <= 0 <= s["max_up_4h"], s
    # a spike too close to the end has no 48 forward candles: logged, not scored
    late = [x for x in replay("LATE-USD", _synthetic(380, 400), btc) if x["profile"] == "aggressive"]
    assert len(late) == 1 and not late[0]["scored"], late
    # consecutive spikes: the second within an hour is not fresh
    two = _synthetic(100)
    two[103] = {**two[103], "open": two[102]["close"], "close": two[102]["close"] * 1.03, "volume": 10.0}
    twos = [x for x in replay("TWO-USD", two, btc) if x["profile"] == "aggressive"]
    assert [x["fresh"] for x in twos] == [True, False], twos
    # report renders end to end from a scratch dir
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        out = Path(d)
        rows = sigs * 40                                           # enough rows for the verdict to speak
        (out / "backtest_signals.jsonl").write_text("".join(json.dumps(x) + "\n" for x in rows))
        (out / "coins.json").write_text(json.dumps({"meta": {"generated": "t", "days": 1, "top": 0, "window_start": "a",
                                                             "window_end": "b", "universe": 1, "calls": 0, "seconds": 0}}))
        md = report(out)
        assert "## Verdict" in md and "positive" in md and "| 4% |" in md and "TEST |" in md, md[:800]
    print("selftest ok:", {"trail4_net": s["trail4_net"], "cont_trail4_net": s["cont_trail4_net"], "r1h": s["r1h"]})


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--out", type=Path, default=Path("data/mrh-backtest"))
    r.add_argument("--days", type=int, default=30)
    r.add_argument("--top", type=int, default=0, help="only the N most liquid coins (0 = whole universe)")
    p = sub.add_parser("report")
    p.add_argument("--out", type=Path, default=Path("data/mrh-backtest"))
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        selftest()
    elif a.cmd == "run":
        meta = run(a.out, a.days, a.top)
        print(json.dumps(meta))
    else:
        (a.out / "BACKTEST.md").write_text(report(a.out))
        print((a.out / "BACKTEST.md").read_text())


if __name__ == "__main__":
    main()
