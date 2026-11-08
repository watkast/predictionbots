"""Bot Benchmark: replay a vendor's PUBLISHED rule against our recorded Polymarket US BTC 15-minute books.

Input: the per-window JSON from mrp/mrp_extract_btc15.py (ptb, settle, prints, top-of-book per second for the Up side:
[ask, ask_qty, bid, bid_qty, state]). Fills only where the book showed size at that second, at the displayed price,
up to the displayed quantity. Fees from the venue's schedule in effect on the trade date (Polymarket US taker:
0.0695 before 6 Nov 2026 13:00 ET, 0.095 after for an ordinary account; resting orders are never assumed).
Every row reports its coverage: the share of 15-second buckets in the window for which we had a book.

Rules (as published by the vendors; where a rule is silent we state the assumption in the output):
  turbine_standard   The retail "buy at 45¢, sell at 70¢" rule on BTC 15-minute (seen in tutorials and vendor marketing; not a
                     specific vendor's product). Buy the first side offered at <= 45¢ (Up at its ask, or Down = 1 - Up bid),
                     sell when that side is bid >= 70¢; otherwise hold to settlement (assumption).
  astrotick_feeaware Fee-aware favorite: in the last 120 s, buy the side the running settlement average favours when it
                     is offered at <= 90¢ and the fee-adjusted edge (margin vs. price) is positive; hold to settlement.
                     (AstroTick is open source; this is the rule as summarised on its README. Assumption noted.)
  coinflip_open      Control: buy Up at the open at the ask, hold to settlement. Not a vendor; the baseline.

Usage:
  python scripts/benchmark_rules.py run --windows btc15.json --out data/benchmark [--size 10]
  python scripts/benchmark_rules.py selftest
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

FEE_CHANGE_TS = int(datetime(2026, 11, 6, 18, 0, tzinfo=timezone.utc).timestamp())  # 13:00 ET = 18:00 UTC (EST)
VENUE = {"name": "pmus"}   # set by run(); kalshi: 7% taker, rounded up to the cent per order (centicent in the schedule)


def theta(ts: int) -> float:
    if VENUE["name"] == "kalshi":
        return 0.07
    return 0.095 if ts >= FEE_CHANGE_TS else 0.0695


def fee(ts: int, contracts: float, p: float) -> float:
    raw = theta(ts) * contracts * p * (1 - p)
    return math.ceil(raw * 100 - 1e-9) / 100 if VENUE["name"] == "kalshi" else round(raw + 1e-12, 2)


def book_at(w: dict, sec: int):
    b = w["book"].get(str(sec))
    return b if b and (b[0] is not None or b[2] is not None) else None


def settle_side(w: dict) -> str | None:
    if w.get("settle") is None or w.get("ptb") is None:
        return None
    return "UP" if w["settle"] > w["ptb"] else "DOWN"


def coverage(w: dict) -> float:
    """Share of the window's 60 fifteen-second buckets with at least one book sample (the recorder polls every
    15 s outside the final three minutes and every second inside them)."""
    T0 = w["T0"]
    seen = {(int(k) - T0) // 15 for k in w["book"] if 0 <= int(k) - T0 < 900}
    return len(seen) / 60.0


# --- rules ---------------------------------------------------------------------------------------------------
def rule_turbine(w: dict, size: float):
    """Returns a trade dict or None."""
    T0, T = w["T0"], w["T"]
    entry = None
    for sec in range(T0, T):
        b = book_at(w, sec)
        if not b:
            continue
        up_ask, up_q, up_bid, bid_q = b[0], b[1], b[2], b[3]
        if up_ask is not None and up_ask <= 0.45 and up_q > 0:
            entry = ("UP", up_ask, min(size, up_q), sec)
            break
        if up_bid is not None and (1 - up_bid) <= 0.45 and bid_q > 0:           # Down offered at 1 - Up bid
            entry = ("DOWN", round(1 - up_bid, 4), min(size, bid_q), sec)
            break
    if not entry:
        return None
    side, px, qty, t_in = entry
    exit_px, t_out, how = None, None, "settlement"
    for sec in range(t_in + 1, T):
        b = book_at(w, sec)
        if not b:
            continue
        bid_for_side = b[2] if side == "UP" else (None if b[0] is None else round(1 - b[0], 4))
        if bid_for_side is not None and bid_for_side >= 0.70:
            exit_px, t_out, how = bid_for_side, sec, "target"
            break
    return finish(w, side, px, qty, t_in, exit_px, t_out, how)


def rule_astrotick(w: dict, size: float):
    T0, T = w["T0"], w["T"]
    prints = {int(k): v for k, v in w["prints"].items()}
    for sec in range(T - 120, T - 1):
        have = [prints[s] for s in range(T - 60, sec + 1) if s in prints]
        if len(have) < 10:
            continue
        avg = sum(have) / len(have)
        remaining = (T - 1) - sec
        # projected final average assumes the remaining prints equal the last print
        last = prints.get(sec)
        if last is None:
            continue
        proj = (sum(have) + last * remaining) / (len(have) + remaining)
        side = "UP" if proj > w["ptb"] else "DOWN"
        b = book_at(w, sec)
        if not b:
            continue
        if side == "UP":
            px, q = b[0], b[1]
        else:
            px, q = (None if b[2] is None else round(1 - b[2], 4)), b[3]
        if px is None or q <= 0 or px > 0.90:
            continue
        margin = abs(proj - w["ptb"]) / w["ptb"] * 1e4
        edge = (1 - px) - theta(sec) * px * (1 - px)          # gross win minus fee per contract
        if margin >= 5 and edge > 0:
            return finish(w, side, px, min(size, q), sec, None, None, "settlement")
    return None


def rule_turbine_reference(w: dict, size: float):
    """Turbine's published reference bot (turbine-py-client 'price action bot'), as documented: compare the live index
    to the strike; if price > strike by more than 10 bps buy YES, if below buy NO; confidence scales with distance
    from 0.6 to 0.9 and sets the limit price; $1 per order up to $10 per market by default (we use `size` dollars per
    order, 5× size max); stop trading with < 60 s left; hold to settlement. Documented on Pyth prices; we replay on the
    CF Benchmarks prints the market settles on."""
    T0, T = w["T0"], w["T"]
    prints = {int(k): v for k, v in w["prints"].items()}
    strike = w["ptb"]
    spent, legs = 0.0, []
    for sec in range(T0, T - 60):
        px_idx = prints.get(sec)
        b = book_at(w, sec)
        if px_idx is None or not b or spent >= size * 5:
            continue
        bps = (px_idx - strike) / strike * 1e4
        if abs(bps) < 10:
            continue
        conf = min(0.9, max(0.6, 0.6 + (abs(bps) - 10) / 100 * 0.3))     # 10 bps -> 0.6, 110 bps -> 0.9
        side = "UP" if bps > 0 else "DOWN"
        ask, q = (b[0], b[1]) if side == "UP" else ((None if b[2] is None else round(1 - b[2], 4)), b[3])
        if ask is None or q <= 0 or ask > conf:
            continue
        remaining = size * 5 - spent
        if remaining < ask:
            break
        qty = min(q, max(1.0, math.floor(min(size, remaining) / ask)))
        legs.append((side, ask, qty, sec))
        spent += ask * qty
    if not legs:
        return None
    res = settle_side(w)
    if res is None:
        return None
    pnl, fees, cost = 0.0, 0.0, 0.0
    for side, px, qty, sec in legs:
        f_in = fee(sec, qty, px); fees += f_in; cost += px * qty
        pnl += ((1 - px) * qty if res == side else -px * qty) - f_in
    first = legs[0]
    return {"slug": w["slug"], "side": "+".join(sorted({l[0] for l in legs})), "px": round(cost / sum(l[2] for l in legs), 4), "qty": round(sum(l[2] for l in legs), 2),
            "t_in": first[3], "t_out": None, "exit": "settlement", "exit_px": None, "fees": round(fees, 4), "pnl": round(pnl, 4), "won": pnl > 0,
            "cost": round(cost, 4), "coverage": round(coverage(w), 3), "legs": len(legs)}


def rule_coinflip(w: dict, size: float):
    for sec in range(w["T0"], w["T0"] + 60):
        b = book_at(w, sec)
        if b and b[0] is not None and b[1] > 0:
            return finish(w, "UP", b[0], min(size, b[1]), sec, None, None, "settlement")
    return None


def finish(w, side, px, qty, t_in, exit_px, t_out, how):
    f_in = fee(t_in, qty, px)
    if how == "target":
        gross = (exit_px - px) * qty
        f_out = fee(t_out, qty, exit_px)
        pnl = gross - f_in - f_out
        won = pnl > 0
    else:
        res = settle_side(w)
        if res is None:
            return None
        won = res == side
        gross = (1 - px) * qty if won else -px * qty
        f_out = 0.0
        pnl = gross - f_in
    return {"slug": w["slug"], "side": side, "px": px, "qty": round(qty, 2), "t_in": t_in, "t_out": t_out, "exit": how,
            "exit_px": exit_px, "fees": round(f_in + f_out, 4), "pnl": round(pnl, 4), "won": bool(won),
            "cost": round(px * qty, 4), "coverage": round(coverage(w), 3)}


RULES = {"turbine_standard": rule_turbine, "turbine_reference": rule_turbine_reference, "astrotick_feeaware": rule_astrotick, "coinflip_open": rule_coinflip}
LABELS = {"turbine_standard": "Retail rule: buy a side at 45¢ or less, sell at 70¢ (hold to settlement otherwise)", "turbine_reference": "Turbine reference bot: buy the side the live price favours vs. the strike (10 bps threshold, confidence-priced limits)", "astrotick_feeaware": "AstroTick, fee-aware favorite (last 120 s)",
          "coinflip_open": "Control: buy Up at the open, hold"}
ASSUMPTIONS = {"turbine_reference": "The 'price action bot' in Turbine's turbine-py-client docs, as documented there: 10 bps threshold, confidence 0.6 to 0.9 scaled with distance from the strike and used as the limit price, buy repeatedly up to a per-market maximum, stop with 60 s left, hold to settlement. Documented on Pyth prices; replayed on the CF Benchmarks prints the market settles on. A reference implementation, not a product the vendor sells as a strategy.",
               "turbine_standard": "A rule circulated in bot tutorials and vendor marketing for BTC 15-minute markets; it is not any one vendor's product (Turbine, where we first saw it quoted, is a bot-builder platform, not a fixed-rule bot). If 70¢ is never bid, the position is held to settlement.",
               "astrotick_feeaware": "Rule as summarised on the project README: favoured side by the running settlement average, offered at or below 90¢, margin >= 5 bps, positive fee-adjusted edge.",
               "coinflip_open": "Baseline, not a product."}


def run(windows: list[dict], size: float, min_cov: float = 0.5, venue: str = "pmus") -> dict:
    VENUE["name"] = venue
    usable = [w for w in windows if w.get("settle") is not None and w.get("ptb") is not None and coverage(w) >= min_cov]
    out = {"generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "venue": venue, "windows_total": len(windows), "windows_usable": len(usable),
           "min_coverage": min_cov, "size_contracts": size, "rules": {}}
    for name, fn in RULES.items():
        trades = [t for t in (fn(w, size) for w in usable) if t]
        pnls = [t["pnl"] for t in trades]
        costs = [t["cost"] for t in trades]
        worst, run_, cur = 0, 0, 0
        for t in trades:
            cur = cur + 1 if not t["won"] else 0
            worst = max(worst, cur)
        out["rules"][name] = {
            "label": LABELS[name], "assumption": ASSUMPTIONS[name], "trades": len(trades),
            "win_rate": round(sum(1 for t in trades if t["won"]) / len(trades), 4) if trades else None,
            "net_total": round(sum(pnls), 2), "net_per_trade": round(statistics.mean(pnls), 4) if pnls else None,
            "net_per_dollar": round(sum(pnls) / sum(costs), 4) if costs and sum(costs) > 0 else None,
            "fees_total": round(sum(t["fees"] for t in trades), 2), "worst_losing_run": worst,
            "mean_coverage": round(statistics.mean(t["coverage"] for t in trades), 3) if trades else None,
            "trades_detail": trades}
    return out


def report(res: dict) -> str:
    vn = "Kalshi" if res.get("venue") == "kalshi" else "Polymarket US"
    lines = [f"# Bot Benchmark — {vn} BTC 15-minute, recorded books\n",
             f"Generated {res['generated']}. Windows recorded: {res['windows_total']}; usable (settled, book coverage >= {res['min_coverage']:.0%}): {res['windows_usable']}. "
             f"Size per trade: {res['size_contracts']:g} contracts or the displayed quantity, whichever is smaller. Fees: {'Kalshi taker schedule (7%, rounded up)' if res.get('venue') == 'kalshi' else 'Polymarket US taker schedule in effect on the trade date'}. Paper fills at displayed depth; real fills can be worse.\n",
             "| Rule | Trades | Win rate | Net per trade | Net per $ staked | Fees paid | Worst losing run | Book coverage |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for name, r in res["rules"].items():
        if r["trades"]:
            lines.append(f"| {r['label']} | {r['trades']} | {r['win_rate']:.0%} | ${r['net_per_trade']:+.3f} | {r['net_per_dollar']:+.1%} | ${r['fees_total']:.2f} | {r['worst_losing_run']} | {r['mean_coverage']:.0%} |")
        else:
            lines.append(f"| {r['label']} | 0 | — | — | — | — | — | — |")
    lines.append("")
    for name, r in res["rules"].items():
        lines.append(f"- **{r['label']}**: {r['assumption']}")
    return "\n".join(lines) + "\n"


def selftest() -> None:
    T0 = 1_800_000_000
    def win(prefix, ptb, settle, book, prints=None):
        return {"slug": f"cpc-btc-updown-15m-{prefix}z", "T0": T0, "T": T0 + 900, "ptb": ptb, "settle": settle, "prints": prints or {},
                "book": {str(T0 + s): v for s, v in book.items()}}
    # Turbine: Up offered at 0.44 at +100 s, bid 0.72 at +400 s -> target exit
    w1 = win("a", 100.0, 101.0, {100: [0.44, 50, 0.42, 50, "OPEN"], 400: [0.73, 50, 0.72, 50, "OPEN"], **{s: [0.5, 10, 0.49, 10, "OPEN"] for s in range(0, 900, 15) if s not in (0, 100, 400)}})
    t = rule_turbine(w1, 10)
    assert t and t["side"] == "UP" and t["exit"] == "target" and t["exit_px"] == 0.72 and t["won"], t
    assert abs(t["pnl"] - ((0.72 - 0.44) * 10 - fee(T0 + 100, 10, 0.44) - fee(T0 + 400, 10, 0.72))) < 1e-6
    # Turbine: Down offered at 0.45 (Up bid 0.55), never 0.70 bid, settles DOWN -> win at settlement
    w2 = win("b", 100.0, 99.0, {s: [0.57, 10, 0.55, 10, "OPEN"] for s in range(0, 900, 15)})
    t2 = rule_turbine(w2, 10)
    assert t2 and t2["side"] == "DOWN" and t2["exit"] == "settlement" and t2["won"]
    # fee schedule date
    assert theta(FEE_CHANGE_TS - 1) == 0.0695 and theta(FEE_CHANGE_TS) == 0.095
    # coinflip control loses the fee on a losing window
    w3 = win("c", 100.0, 99.0, {0: [0.5, 10, 0.49, 10, "OPEN"]})
    t3 = rule_coinflip(w3, 10)
    assert t3 and not t3["won"] and t3["pnl"] < -5
    res = run([w1, w2, w3], 10, min_cov=0.0)
    assert res["rules"]["turbine_standard"]["trades"] == 2 and "45¢" in report(res)
    # reference bot: index 30 bps above the strike from the open, Up offered at 0.55 (<= confidence 0.66) -> buys, settles UP
    w4 = win("d", 100.0, 100.5, {s: [0.55, 50, 0.53, 50, "OPEN"] for s in range(0, 900, 15)}, prints={str(T0 + s): 100.3 for s in range(0, 900)})
    t4 = rule_turbine_reference(w4, 10)
    assert t4 and t4["won"] and t4["legs"] >= 1 and t4["cost"] <= 10 * 5 + 1, t4
    # kalshi fee path
    resk = run([w4], 10, min_cov=0.0, venue="kalshi")
    assert resk["venue"] == "kalshi" and "Kalshi" in report(resk)
    VENUE["name"] = "pmus"
    print("selftest ok")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--windows", required=True)
    r.add_argument("--out", default="data/benchmark")
    r.add_argument("--size", type=float, default=10)
    r.add_argument("--min-coverage", type=float, default=0.5)
    r.add_argument("--venue", default=None, choices=["pmus", "kalshi"], help="defaults to the windows file's venue, else pmus")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        selftest()
        return
    blob = json.load(open(a.windows))
    windows = blob["windows"]
    res = run(windows, a.size, a.min_coverage, a.venue or blob.get("venue") or "pmus")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "benchmark.json").write_text(json.dumps(res, separators=(",", ":")))
    (out / "BENCHMARK.md").write_text(report(res))
    print(report(res))


if __name__ == "__main__":
    main()
