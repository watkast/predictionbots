"""Early Favorite — forward (walk-forward) tracker on Polymarket US 15-minute BTC rounds.

The rule was found on Oct 6-22 2026 data (scripts in this repo, see reports) and is FROZEN here.
Nothing below may be tuned on forward results; change RULE only by starting a new forward test
with a new FORWARD_START.

TIMING NOTE (v2): each price_history point is labeled with the START of its 1-minute bucket but holds the
price at the END of that bucket (verified against BRTI candles: best match is +60 s after the label). So the
point labeled ws+60*k is the book at k+1 minutes elapsed. v1 read labels 2 and 3, which is really 3:00 and
4:00 elapsed (12:00 / 11:00 left), not the 13:00 / 12:00 left the playbook trades. v2 fixes that with LABEL_LAG.

RULE (paper only, no orders):
  At 2:00 elapsed (13:00 left), else 3:00 elapsed (12:00 left): find the leading side (Up if Up mid >= 0.50, else Down).
  If that side's ask is in [0.80, 0.95): buy $100 of it at the ask. One entry per round.
  Hold to settlement. Pay the Polymarket US taker fee 0.0695 * p * (1 - p) per contract.

Inputs: data/polyus/markets.json and data/polyus/price_history/*.json (from scripts/polyus_fetch.py).
Prices: longPrice = Up best ask, shortPrice = Down best ask, at the minute stamp.
Outputs (to --out): early_favorite_ledger.csv (one row per scored round), early_favorite.json
(summary), early_favorite.md (readable report). Rounds without settlement or without minute 2-3
prices yet are listed as pending and scored on a later run.
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import math
from datetime import datetime, timezone
from pathlib import Path

RULE = {
    "name": "Early Favorite v2",
    "minutes": [2, 3],        # minutes ELAPSED at the check (13:00 and 12:00 left)
    "label_lag": 1,           # history label = elapsed minutes - 1 (label is the bucket start)
    "ask_min": 0.80,
    "ask_max": 0.95,
    "stake_usd": 100.0,
    "fee_coef": 0.0695,
    "hold": "settlement",
}
# PARALLEL column, not part of the frozen rule: what if the position were sold at 5:00 left when the
# favorite's bid has fallen under CUT["bid_below"]? Scored next to hold-to-settlement on the same rounds.
# Backtest Oct 6-22 (272 trades): +$150-220 over holding, i.e. under 1% of the money staked, and found
# in-sample, so it is being forward-tested here, not traded. Exit = taker sell at bid - slippage, taker fee.
CUT = {"minute": 10, "bid_below": 0.45, "slippage": 0.02}
FORWARD_START = "2026-10-23T00:00:00Z"   # v2 forward test; v1 (wrong minutes) ran 2026-10-22T08:30Z to 10-23T00:00Z
# Re-tested at the true 2:00/3:00-elapsed timing on 2026-10-06 .. 2026-10-22 (1590 settled rounds)
BACKTEST = {"period": "2026-10-06 to 2026-10-22", "rounds": 272, "win_rate": 0.893, "avg_ask": 0.838,
            "edge_pct_per_round": 5.46, "net_usd_per_100": 1486, "max_drawdown_usd": -403}


def amount(v):
    if isinstance(v, dict):
        v = v.get("value")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pull_by_minute(root: Path, fast: int = 9, slow: int = 21, atr_len: int = 10, mult: float = 2.0) -> dict[int, int]:
    """Chart 'pull' per BRTI 1-minute candle, keyed by the candle's start: +1/-1 each for close vs EMA(slow), EMA(fast)
    vs EMA(slow) and the Supertrend side, so -3..+3. Mirrors research/market_pull.pine. A PARALLEL column for the
    ledger, not part of the frozen rule. Returns {} when brti_1m.json is not there."""
    f = root / "brti_1m.json"
    if not f.exists():
        return {}
    candles = {int(c["timestamp"]): c for c in json.loads(f.read_text())}
    out: dict[int, int] = {}
    kf, ks, ka = 2.0 / (fast + 1), 2.0 / (slow + 1), 1.0 / atr_len
    ef = es = atr = prev_close = None
    pu = pl = pst = None
    for ts in sorted(candles):
        c = candles[ts]
        h, lo, cl = float(c["high"]), float(c["low"]), float(c["close"])
        ef = cl if ef is None else ef + kf * (cl - ef)
        es = cl if es is None else es + ks * (cl - es)
        tr = h - lo if prev_close is None else max(h - lo, abs(h - prev_close), abs(lo - prev_close))
        atr = tr if atr is None else atr + ka * (tr - atr)
        up_b, lo_b = (h + lo) / 2 + mult * atr, (h + lo) / 2 - mult * atr
        if pu is None:
            pu, pl, pst, d = up_b, lo_b, up_b, 1
        else:
            lb = lo_b if (lo_b > pl or prev_close < pl) else pl
            ub = up_b if (up_b < pu or prev_close > pu) else pu
            d = (-1 if cl > ub else 1) if pst == pu else (1 if cl < lb else -1)   # -1 = up trend, like ta.supertrend
            pu, pl, pst = ub, lb, (lb if d == -1 else ub)
        p1 = (cl > es) - (cl < es)
        p2 = (ef > es) - (ef < es)
        out[ts] = int(p1 + p2 - d)
        prev_close = cl
    return out


def score(root: Path, start_ts: float):
    markets = {m.get("slug"): m for m in json.loads((root / "markets.json").read_text())}
    pulls = pull_by_minute(root)
    ledger, pending, skipped = [], [], 0
    for f in sorted(glob.glob(str(root / "price_history" / "*.json"))):
        d = json.loads(Path(f).read_text())
        ws, we = int(d["windowStart"]), int(d["windowEnd"])
        if ws < start_ts:
            continue
        hist = {int(h["timestamp"]): h for h in d.get("history") or []}
        terms = (markets.get(d["slug"]) or {}).get("assetPriceTerms") or {}
        ptb, sp = amount(terms.get("priceToBeat")), amount(terms.get("settlementPrice"))
        entry = None
        lag = RULE["label_lag"]
        have_minutes = all((ws + 60 * (m - lag)) in hist for m in RULE["minutes"])
        for m in RULE["minutes"]:
            h = hist.get(ws + 60 * (m - lag))
            if h is None:
                continue
            ua, da = float(h["longPrice"]), float(h["shortPrice"])
            up_mid = (ua + (1 - da)) / 2
            side = "Up" if up_mid >= 0.5 else "Down"
            ask = ua if side == "Up" else da
            if RULE["ask_min"] <= ask < RULE["ask_max"]:
                entry = dict(minute=m, side=side, ask=ask)
                break
        if entry is None:
            if have_minutes:
                skipped += 1          # rule did not trigger this round
            else:
                pending.append(dict(slug=d["slug"], window_start=iso(ws), reason="minute 2-3 prices not stored yet"))
            continue
        if ptb is None or sp is None:
            pending.append(dict(slug=d["slug"], window_start=iso(ws), reason="not settled yet", **entry))
            continue
        up_won = sp >= ptb
        won = up_won if entry["side"] == "Up" else not up_won
        n = RULE["stake_usd"] / entry["ask"]
        fee = RULE["fee_coef"] * entry["ask"] * (1 - entry["ask"]) * n
        pnl = (n if won else 0.0) - RULE["stake_usd"] - fee
        # chart pull at the check, signed against the favorite: +3 = all three trend parts with it, -3 = all against
        p = pulls.get(ws + 60 * (entry["minute"] - 1))      # the 1-minute candle that closes at the check
        pull = None if p is None else p * (1 if entry["side"] == "Up" else -1)
        # parallel column: the 5:00-left cut (see CUT). The favorite's bid = 1 - the other side's ask.
        bid_at_cut, pnl_cut, cut = None, pnl, 0
        hc = hist.get(ws + 60 * (CUT["minute"] - lag))
        if hc is not None:
            bid_at_cut = (1 - float(hc["shortPrice"])) if entry["side"] == "Up" else (1 - float(hc["longPrice"]))
            if bid_at_cut < CUT["bid_below"]:
                px = max(bid_at_cut - CUT["slippage"], 0.01)
                pnl_cut = n * px - RULE["stake_usd"] - fee - RULE["fee_coef"] * px * (1 - px) * n
                cut = 1
        ledger.append(dict(slug=d["slug"], window_start=iso(ws), minute=entry["minute"], side=entry["side"],
                           ask=round(entry["ask"], 3), price_to_beat=ptb, settlement=sp,
                           won=int(won), contracts=round(n, 2), fee=round(fee, 2), pnl=round(pnl, 2), pull=pull,
                           bid_at_cut=None if bid_at_cut is None else round(bid_at_cut, 2), cut=cut, pnl_cut=round(pnl_cut, 2)))
    ledger.sort(key=lambda r: r["window_start"])
    return ledger, pending, skipped


def summarize(ledger, pending, skipped, start_ts):
    eq, peak, dd, streak, worst_streak = 0.0, 0.0, 0.0, 0, 0
    by_day: dict[str, float] = {}
    for r in ledger:
        eq += r["pnl"]
        r["cum_pnl"] = round(eq, 2)
        peak = max(peak, eq)
        dd = min(dd, eq - peak)
        streak = streak + 1 if not r["won"] else 0
        worst_streak = max(worst_streak, streak)
        day = r["window_start"][:10]
        by_day[day] = by_day.get(day, 0.0) + r["pnl"]
    n = len(ledger)
    wins = sum(r["won"] for r in ledger)
    avg_ask = sum(r["ask"] for r in ledger) / n if n else None
    net = round(eq, 2)
    # how far is forward from backtest? one-sided z on win rate vs the backtest's win rate
    p0 = BACKTEST["win_rate"]
    z = ((wins / n) - p0) / math.sqrt(p0 * (1 - p0) / n) if n else None
    # break-even win rate at the average ask, after fees
    be = (avg_ask + RULE["fee_coef"] * avg_ask * (1 - avg_ask)) if avg_ask else None
    # parallel column: how the rounds went by chart pull at the check (see pull_by_minute)
    pull_rows = []
    for label, pick in (("with the favorite 3/3", lambda p: p >= 3), ("with the favorite 1/3", lambda p: 0 < p < 3),
                        ("against the favorite", lambda p: p < 0)):
        g = [r for r in ledger if r.get("pull") is not None and pick(r["pull"])]
        pull_rows.append({"pull": label, "rounds": len(g),
                          "win_rate": round(sum(r["won"] for r in g) / len(g), 4) if g else None,
                          "net_usd": round(sum(r["pnl"] for r in g), 2)})
    # parallel column: the 5:00-left cut vs holding, on the rounds where the 5:00-left price is known
    scored = [r for r in ledger if r.get("bid_at_cut") is not None]
    cuts = [r for r in scored if r.get("cut")]
    cut_row = {"rule": CUT, "rounds_with_price": len(scored), "cuts": len(cuts),
               "cuts_that_would_have_lost": sum(1 for r in cuts if not r["won"]),
               "cuts_that_would_have_won": sum(1 for r in cuts if r["won"]),
               "net_usd_hold": round(sum(r["pnl"] for r in scored), 2),
               "net_usd_cut": round(sum(r["pnl_cut"] for r in scored), 2)}
    cut_row["cut_minus_hold_usd"] = round(cut_row["net_usd_cut"] - cut_row["net_usd_hold"], 2)
    return {
        "rule": RULE, "forward_start": iso(start_ts), "generated": iso(datetime.now(timezone.utc).timestamp()),
        "rounds_scored": n, "rounds_skipped_rule_not_met": skipped, "rounds_pending": len(pending),
        "wins": wins, "win_rate": round(wins / n, 4) if n else None,
        "avg_ask": round(avg_ask, 4) if avg_ask else None,
        "breakeven_win_rate": round(be, 4) if be else None,
        "net_usd": net, "per_round_pct": round(net / (n * RULE["stake_usd"]) * 100, 2) if n else None,
        "max_drawdown_usd": round(dd, 2), "longest_losing_streak": worst_streak,
        "days": [{"day": k, "net_usd": round(v, 2)} for k, v in sorted(by_day.items())],
        "z_vs_backtest_win_rate": round(z, 2) if z is not None else None,
        "backtest": BACKTEST,
        "pull": pull_rows,
        "cut": cut_row,
    }


def verdict(s):
    n = s["rounds_scored"]
    if n < 50:
        return f"Too early to judge: {n} of the ~150 rounds (about a week) needed."
    if s["win_rate"] < s["breakeven_win_rate"]:
        return "Losing: forward win rate is below break-even at the prices paid."
    if s["z_vs_backtest_win_rate"] is not None and s["z_vs_backtest_win_rate"] < -2:
        return "Profitable but clearly weaker than the backtest (win rate more than 2 standard errors below it)."
    return "Holding up: forward win rate is above break-even and consistent with the backtest."


def write(out: Path, ledger, pending, s):
    out.mkdir(parents=True, exist_ok=True)
    cols = ["window_start", "slug", "minute", "side", "ask", "price_to_beat", "settlement", "won", "contracts", "fee", "pnl", "cum_pnl", "pull",
            "bid_at_cut", "cut", "pnl_cut"]
    with open(out / "early_favorite_ledger.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in ledger:
            w.writerow({k: r.get(k) for k in cols})
    s = dict(s, verdict=verdict(s), pending=pending[-20:])
    (out / "early_favorite.json").write_text(json.dumps(s, indent=1))
    pct = lambda v: "-" if v is None else f"{v * 100:.1f}%"
    ask_txt = "-" if s["avg_ask"] is None else f"{s['avg_ask']:.3f}"
    per_txt = "-" if s["per_round_pct"] is None else f"{s['per_round_pct']:+.2f}%"
    lines = [
        f"# {RULE['name']} - forward test",
        "",
        f"Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is {RULE['ask_min']:.2f}-{RULE['ask_max']:.2f}; "
        f"${RULE['stake_usd']:.0f} per round; hold to settlement; taker fee {RULE['fee_coef']}*p*(1-p). Paper only.",
        f"Forward test started {s['forward_start']}. Updated {s['generated']}.",
        "",
        f"**{s['verdict']}**",
        "",
        "| | Forward | Backtest (Oct 6-22) |",
        "|---|---|---|",
        f"| Rounds | {s['rounds_scored']} | {BACKTEST['rounds']} |",
        f"| Win rate | {pct(s['win_rate'])} | {pct(BACKTEST['win_rate'])} |",
        f"| Break-even win rate at prices paid | {pct(s['breakeven_win_rate'])} | - |",
        f"| Average ask | {ask_txt} | {BACKTEST['avg_ask']:.3f} |",
        f"| Net at $100/round | ${s['net_usd']:+,.2f} | ${BACKTEST['net_usd_per_100']:+,} |",
        f"| Per round | {per_txt} | +{BACKTEST['edge_pct_per_round']}% |",
        f"| Max drawdown | ${s['max_drawdown_usd']:,.2f} | ${BACKTEST['max_drawdown_usd']:,} |",
        f"| Longest losing streak | {s['longest_losing_streak']} | 2 |",
        "| Entry timing | 13:00 / 12:00 left | same |",
        "",
        f"Rounds where the rule did not trigger: {s['rounds_skipped_rule_not_met']}. Pending (not settled or not fetched yet): {s['rounds_pending']}.",
        "",
        "## By day (UTC)",
        "",
        "| Day | Net |",
        "|---|---|",
    ] + [f"| {d['day']} | ${d['net_usd']:+,.2f} |" for d in s["days"]] + [
        "",
        "## Chart pull at the check (parallel column - not part of the rule)",
        "",
        "Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. "
        "Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.",
        "",
        "| Pull at the check | Rounds | Win rate | Net |",
        "|---|---|---|---|",
    ] + [f"| {p['pull']} | {p['rounds']} | {pct(p['win_rate'])} | ${p['net_usd']:+,.2f} |" for p in s.get("pull", [])] + [
        "",
        "## Cut at 5:00 left (parallel column - not part of the rule)",
        "",
        f"What if the position were sold at {15 - CUT['minute']}:00 left whenever the favorite's bid is under {CUT['bid_below'] * 100:.0f}c "
        f"(sold {CUT['slippage'] * 100:.0f}c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money "
        "staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.",
        "",
        "| | Hold (the rule) | Cut under 45c at 5:00 left |",
        "|---|---|---|",
        f"| Rounds with a 5:00-left price | {s['cut']['rounds_with_price']} | same |",
        f"| Positions cut | - | {s['cut']['cuts']} ({s['cut']['cuts_that_would_have_lost']} would have lost, {s['cut']['cuts_that_would_have_won']} would have won) |",
        f"| Net at $100/round | ${s['cut']['net_usd_hold']:+,.2f} | ${s['cut']['net_usd_cut']:+,.2f} ({s['cut']['cut_minus_hold_usd']:+,.2f}) |",
        "",
        "## Last 20 rounds",
        "",
        "| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |",
        "|---|---|---|---|---|---|---|---|",
    ] + [f"| {r['window_start'][5:16].replace('T', ' ')} | {r['minute']} | {r['side']} | {r['ask']:.2f} | {'-' if r.get('pull') is None else f"{r['pull']:+d}"} | {'won' if r['won'] else 'LOST'} | ${r['pnl']:+.2f} | ${r['cum_pnl']:+.2f} |"
         for r in ledger[-20:]]
    (out / "early_favorite.md").write_text("\n".join(lines) + "\n")
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/polyus")
    ap.add_argument("--out", default="data/polyus/early_favorite")
    ap.add_argument("--start", default=FORWARD_START, help="override only to re-score a past period (not the forward test)")
    a = ap.parse_args()
    start_ts = datetime.fromisoformat(a.start.replace("Z", "+00:00")).timestamp()
    ledger, pending, skipped = score(Path(a.data), start_ts)
    s = write(Path(a.out), ledger, pending, summarize(ledger, pending, skipped, start_ts))
    print(f"{RULE['name']}: {s['rounds_scored']} scored, {s['rounds_pending']} pending, net ${s['net_usd']:+.2f}, "
          f"win {s['win_rate']}, verdict: {s['verdict']}")


if __name__ == "__main__":
    main()
