"""Early Favorite — forward (walk-forward) tracker on Polymarket US 15-minute BTC rounds.

The rule was found on Oct 6-22 2026 data (scripts in this repo, see reports) and is FROZEN here.
Nothing below may be tuned on forward results; change RULE only by starting a new forward test
with a new FORWARD_START.

RULE (paper only, no orders):
  At minute 2, else minute 3, of a round: find the leading side (Up if Up mid >= 0.50, else Down).
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
    "name": "Early Favorite v1",
    "minutes": [2, 3],
    "ask_min": 0.80,
    "ask_max": 0.95,
    "stake_usd": 100.0,
    "fee_coef": 0.0695,
    "hold": "settlement",
}
FORWARD_START = "2026-10-22T08:30:00Z"   # first round scored = first windowStart at/after this
BACKTEST = {"period": "2026-10-06 to 2026-10-22", "rounds": 371, "win_rate": 0.889, "avg_ask": 0.842,
            "edge_pct_per_round": 4.44, "net_usd_per_100": 1649, "max_drawdown_usd": -498}


def amount(v):
    if isinstance(v, dict):
        v = v.get("value")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def score(root: Path, start_ts: float):
    markets = {m.get("slug"): m for m in json.loads((root / "markets.json").read_text())}
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
        have_minutes = all((ws + 60 * m) in hist for m in RULE["minutes"])
        for m in RULE["minutes"]:
            h = hist.get(ws + 60 * m)
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
        ledger.append(dict(slug=d["slug"], window_start=iso(ws), minute=entry["minute"], side=entry["side"],
                           ask=round(entry["ask"], 3), price_to_beat=ptb, settlement=sp,
                           won=int(won), contracts=round(n, 2), fee=round(fee, 2), pnl=round(pnl, 2)))
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
    cols = ["window_start", "slug", "minute", "side", "ask", "price_to_beat", "settlement", "won", "contracts", "fee", "pnl", "cum_pnl"]
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
        f"Rule (frozen): at minute 2, else 3, buy the leading side if its ask is {RULE['ask_min']:.2f}-{RULE['ask_max']:.2f}; "
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
        "",
        f"Rounds where the rule did not trigger: {s['rounds_skipped_rule_not_met']}. Pending (not settled or not fetched yet): {s['rounds_pending']}.",
        "",
        "## By day (UTC)",
        "",
        "| Day | Net |",
        "|---|---|",
    ] + [f"| {d['day']} | ${d['net_usd']:+,.2f} |" for d in s["days"]] + [
        "",
        "## Last 20 rounds",
        "",
        "| Window (UTC) | Min | Side | Ask | Result | P&L | Running |",
        "|---|---|---|---|---|---|---|",
    ] + [f"| {r['window_start'][5:16].replace('T', ' ')} | {r['minute']} | {r['side']} | {r['ask']:.2f} | {'won' if r['won'] else 'LOST'} | ${r['pnl']:+.2f} | ${r['cum_pnl']:+.2f} |"
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
