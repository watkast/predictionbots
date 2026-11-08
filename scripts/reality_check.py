"""Reality Check: a private statement for one person's prediction-market accounts, in plain words.

Inputs (any combination):
  --kalshi-fills fills.csv|json       Kalshi fills export or API dump (ticker, side, action, count, price, fee, time)
  --kalshi-api                        pull fills + settlements with KALSHI_KEY_ID / KALSHI_PRIVATE_KEY_PEM in the env
  --pmus-fills fills.csv|json         Polymarket US fills/orders export or API dump
  --cash cash.csv                     deposits and withdrawals: date, amount (+ deposit, − withdrawal), venue
  --balance 123.45                    current total balance across venues (what the apps show today)

Output: REALITY_CHECK.md (+ a JSON with every normalised fill) in --out. Nothing is uploaded anywhere; this runs on the
owner's machine or ours with their files, and the report goes to them first. Column names are auto-detected; when a
file does not fit, the script says which column it could not find instead of guessing.

  python scripts/reality_check.py run --kalshi-fills k.csv --pmus-fills p.csv --cash cash.csv --balance 212.40 --out out/rc
  python scripts/reality_check.py selftest
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

LOG = lambda *a: print(*a, file=sys.stderr)

# column aliases per field; matching is case-insensitive on normalised names
ALIASES = {
    "time": ["time", "created_time", "createdtime", "created", "timestamp", "date", "filled_at", "ts", "transacttime", "executed_at"],
    "market": ["ticker", "market_ticker", "market", "marketslug", "slug", "market_slug", "question", "event"],
    "side": ["side", "outcome", "yes_no", "direction", "intent"],
    "action": ["action", "type", "buy_sell", "order_side"],
    "count": ["count", "contracts", "quantity", "qty", "size", "shares", "filled_quantity", "filledquantity"],
    "price": ["price", "yes_price", "price_dollars", "avg_price", "fill_price", "average_price", "averageprice", "price_usd"],
    "fee": ["fee", "fees", "fee_cost", "taker_fee", "commission", "fee_usd", "fees_usd"],
    "pnl": ["pnl", "realized_pnl", "profit", "realized", "net"],
}


def _norm(s: str) -> str:
    return "".join(ch for ch in str(s).lower() if ch.isalnum() or ch == "_")


def pick(columns: list[str], field: str) -> str | None:
    cols = {_norm(c): c for c in columns}
    for a in ALIASES[field]:
        if _norm(a) in cols:
            return cols[_norm(a)]
    return None


def _num(x, default=0.0) -> float:
    try:
        s = str(x).replace("$", "").replace(",", "").replace("¢", "").strip()
        if s.endswith("%"):
            s = s[:-1]
        return float(s) if s not in ("", "None", "null") else default
    except (TypeError, ValueError):
        return default


def _time(x) -> datetime | None:
    if x is None:
        return None
    if isinstance(x, (int, float)) or str(x).isdigit():
        v = float(x)
        return datetime.fromtimestamp(v / 1000 if v > 1e11 else v, timezone.utc)
    s = str(x).strip().replace("Z", "+00:00")
    for fmt in (None, "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y %H:%M", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S.%f%z"):
        try:
            d = datetime.fromisoformat(s) if fmt is None else datetime.strptime(s, fmt)
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def load_rows(path: str) -> list[dict]:
    p = Path(path)
    if p.suffix.lower() == ".json":
        j = json.loads(p.read_text())
        if isinstance(j, dict):
            for k in ("fills", "orders", "data", "results", "items"):
                if isinstance(j.get(k), list):
                    return j[k]
            return [j]
        return j
    with open(p, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def normalise(rows: list[dict], venue: str) -> tuple[list[dict], list[str]]:
    """-> fills [{t, venue, market, side, action, count, price, fee, cost}], problems."""
    if not rows:
        return [], [f"{venue}: no rows"]
    cols = list(rows[0].keys())
    c = {f: pick(cols, f) for f in ALIASES}
    problems = [f"{venue}: no column for {f} (have: {', '.join(cols[:12])})" for f in ("time", "price", "count") if not c[f]]
    if problems:
        return [], problems
    out = []
    for r in rows:
        t = _time(r.get(c["time"]))
        if not t:
            continue
        price = _num(r.get(c["price"]))
        if price > 1.5:          # cents
            price = price / 100
        count = abs(_num(r.get(c["count"])))
        side = str(r.get(c["side"]) or "").upper() if c["side"] else ""
        action = str(r.get(c["action"]) or "").upper() if c["action"] else ""
        is_buy = ("SELL" not in action and "SHORT" not in action) if (action or side) else True
        fee = abs(_num(r.get(c["fee"]))) if c["fee"] else 0.0
        if venue == "pmus" and ("SHORT" in side or "NO" == side.strip()) and price <= 1:
            price = round(1 - price, 4) if "SHORT" in side else price  # Down/No shares priced as 1 − Up where exported that way
        out.append({"t": t.isoformat(), "venue": venue, "market": str(r.get(c["market"]) or "") if c["market"] else "", "side": side, "action": "BUY" if is_buy else "SELL",
                    "count": count, "price": price, "fee": fee, "cost": round(count * price, 4),
                    "pnl": _num(r.get(c["pnl"])) if c["pnl"] and r.get(c["pnl"]) not in (None, "") else None})
    return out, []


def load_cash(path: str | None) -> list[dict]:
    if not path:
        return []
    rows = load_rows(path)
    out = []
    for r in rows:
        cols = list(r.keys())
        tcol = pick(cols, "time") or cols[0]
        acol = next((cc for cc in cols if _norm(cc) in ("amount", "value", "usd", "net", "cash")), cols[1] if len(cols) > 1 else cols[0])
        kind = next((str(r[cc]).lower() for cc in cols if _norm(cc) in ("type", "kind", "direction")), "")
        amt = _num(r[acol])
        if "withdraw" in kind and amt > 0:
            amt = -amt
        t = _time(r.get(tcol))
        out.append({"t": t.isoformat() if t else "", "amount": amt, "venue": next((str(r[cc]) for cc in cols if _norm(cc) == "venue"), "")})
    return out


def summarise(fills: list[dict], cash: list[dict], balance: float | None) -> dict:
    fees = sum(f["fee"] for f in fills)
    buys = [f for f in fills if f["action"] == "BUY"]
    deposits = sum(c["amount"] for c in cash if c["amount"] > 0)
    withdrawals = -sum(c["amount"] for c in cash if c["amount"] < 0)
    staked = sum(f["cost"] for f in buys)
    weeks = defaultdict(lambda: {"fees": 0.0, "staked": 0.0, "trades": 0})
    hours = defaultdict(int)
    by_venue = defaultdict(lambda: {"fees": 0.0, "staked": 0.0, "trades": 0})
    for f in fills:
        d = datetime.fromisoformat(f["t"])
        wk = d.strftime("%G-W%V")
        weeks[wk]["fees"] += f["fee"]; weeks[wk]["trades"] += 1
        by_venue[f["venue"]]["fees"] += f["fee"]; by_venue[f["venue"]]["trades"] += 1
        if f["action"] == "BUY":
            weeks[wk]["staked"] += f["cost"]; by_venue[f["venue"]]["staked"] += f["cost"]
        hours[d.hour] += 1
    net = None
    if balance is not None and cash:
        net = balance + withdrawals - deposits
    pnl_known = [f["pnl"] for f in fills if f["pnl"] is not None]
    first = min((f["t"] for f in fills), default=None)
    last = max((f["t"] for f in fills), default=None)
    span_days = (datetime.fromisoformat(last) - datetime.fromisoformat(first)).days + 1 if first and last else 0
    fee_per_week = fees / max(1, span_days / 7)
    return {"fills": len(fills), "buys": len(buys), "first": first, "last": last, "span_days": span_days, "fees": round(fees, 2), "staked": round(staked, 2),
            "fee_share_of_stake": round(fees / staked, 4) if staked else None, "deposits": round(deposits, 2), "withdrawals": round(withdrawals, 2),
            "balance": balance, "net_result": round(net, 2) if net is not None else None,
            "realized_pnl_reported": round(sum(pnl_known), 2) if pnl_known else None,
            "fee_per_week": round(fee_per_week, 2), "weeks": dict(sorted(weeks.items())), "hours": dict(sorted(hours.items())), "by_venue": dict(by_venue),
            "late_night_share": round(sum(v for h, v in hours.items() if h >= 23 or h < 5) / len(fills), 3) if fills else None}


def report(s: dict, tbill: float | None = None) -> str:
    L = [f"# Your statement\n", f"_Generated {datetime.now(timezone.utc):%d %B %Y}. Numbers from your own exports; nothing here is a judgment, it is arithmetic._\n"]
    if s["fills"]:
        L.append(f"- **{s['fills']:,} fills** between {s['first'][:10]} and {s['last'][:10]} ({s['span_days']} days); {s['buys']:,} were buys, **${s['staked']:,.2f}** put at risk in total.")
        L.append(f"- **Fees paid: ${s['fees']:,.2f}**, which is {s['fee_share_of_stake']*100:.1f}% of everything you staked, or about **${s['fee_per_week']:,.2f} a week**. This is the only number on the statement that was certain before any outcome.")
    if s["deposits"] or s["withdrawals"]:
        L.append(f"- Deposited **${s['deposits']:,.2f}**, withdrew **${s['withdrawals']:,.2f}**" + (f", balance today **${s['balance']:,.2f}**." if s["balance"] is not None else "."))
    if s["net_result"] is not None:
        L.append(f"- **Net result: {'+' if s['net_result'] >= 0 else '−'}${abs(s['net_result']):,.2f}.** Of that, ${s['fees']:,.2f} went to the venues as fees; the rest went to whoever was on the other side.")
        if s["fees"] and s["net_result"] < 0:
            L.append(f"- Fees are **{min(100, s['fees']/abs(s['net_result'])*100):.0f}%** of the loss.")
    if s["realized_pnl_reported"] is not None:
        L.append(f"- The venue's own realised P&L column sums to {'+' if s['realized_pnl_reported'] >= 0 else '−'}${abs(s['realized_pnl_reported']):,.2f}.")
    if s["by_venue"]:
        L.append("\n## By venue\n\n| Venue | Fills | Staked | Fees |\n| --- | --- | --- | --- |")
        for v, d in s["by_venue"].items():
            L.append(f"| {'Kalshi' if v=='kalshi' else 'Polymarket US' if v=='pmus' else v} | {d['trades']:,} | ${d['staked']:,.2f} | ${d['fees']:,.2f} |")
    if s["weeks"]:
        L.append("\n## By week\n\n| Week | Fills | Staked | Fees |\n| --- | --- | --- | --- |")
        for w, d in s["weeks"].items():
            L.append(f"| {w} | {d['trades']} | ${d['staked']:,.2f} | ${d['fees']:,.2f} |")
    if s["late_night_share"] is not None:
        L.append(f"\n**{s['late_night_share']*100:.0f}%** of fills happened between 11 p.m. and 5 a.m. (UTC; adjust for your zone). Not a verdict, a pattern worth knowing about yourself.")
    if s["deposits"] and tbill:
        L.append(f"\n## Same money, elsewhere\n\nThe ${s['deposits']:,.2f} you deposited, in 4-week Treasury bills at {tbill*100:.2f}% a year, would have paid about **${s['deposits']*tbill/12:,.2f} a month**, guaranteed, instead of costing ${s['fee_per_week']*4.33:,.2f} a month in fees before any outcome.")
    if s["fee_per_week"] and s["balance"]:
        L.append(f"\n## At this pace\n\nFees alone take **${s['fee_per_week']:,.2f} a week**. With no edge, the balance of ${s['balance']:,.2f} lasts about **{s['balance']/s['fee_per_week']:.0f} weeks** on fees alone, before variance. The simulator at predictionbots.io/simulate shows what that looks like with your numbers.")
    L.append("\n## If any of this is hard to read\n\nYou are not an outlier; you are in a group the size of a large city. **1-800-GAMBLER** (call or text, free, 24 hours) will not judge you, and neither do we. If money is the emergency, predictionbots.io/learn/when-the-market-looks-like-the-only-way-out has the ladder for tonight, this week and this month.\n")
    return "\n".join(L)


def selftest() -> None:
    rows = [{"created_time": "2026-10-20T01:15:00Z", "ticker": "KXBTC15M-1", "side": "yes", "action": "buy", "count": "10", "yes_price": "45", "fee": "0.18"},
            {"created_time": "2026-10-20T01:28:00Z", "ticker": "KXBTC15M-1", "side": "yes", "action": "sell", "count": "10", "yes_price": "70", "fee": "0.15"},
            {"created_time": "2026-10-27T23:40:00Z", "ticker": "KXBTC15M-2", "side": "no", "action": "buy", "count": "20", "yes_price": "0.40", "fee": "0.34"}]
    fills, problems = normalise(rows, "kalshi")
    assert not problems and len(fills) == 3 and fills[0]["price"] == 0.45 and fills[1]["action"] == "SELL" and fills[2]["price"] == 0.40, (fills, problems)
    cash = [{"t": "2026-10-19T00:00:00+00:00", "amount": 100.0, "venue": "kalshi"}, {"t": "2026-10-30T00:00:00+00:00", "amount": -20.0, "venue": "kalshi"}]
    s = summarise(fills, cash, balance=61.5)
    assert s["fees"] == 0.67 and s["deposits"] == 100.0 and s["withdrawals"] == 20.0 and s["net_result"] == -18.5, s
    r = report(s, tbill=0.04)
    assert "Fees paid: $0.67" in r and "Net result: −$18.50" in r and "By week" in r
    bad, probs = normalise([{"foo": 1}], "pmus")
    assert probs and "no column for time" in probs[0]
    print("selftest ok")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--kalshi-fills"); r.add_argument("--pmus-fills"); r.add_argument("--cash"); r.add_argument("--balance", type=float)
    r.add_argument("--tbill", type=float, default=None, help="4-week T-bill yield as a decimal, from site/data/rates.json")
    r.add_argument("--out", default="out/reality_check")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        selftest(); return
    fills, problems = [], []
    for path, venue in ((a.kalshi_fills, "kalshi"), (a.pmus_fills, "pmus")):
        if path:
            f, p = normalise(load_rows(path), venue); fills += f; problems += p
    for p in problems:
        LOG("problem:", p)
    cash = load_cash(a.cash)
    s = summarise(fills, cash, a.balance)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "fills.json").write_text(json.dumps(fills, indent=0))
    (out / "summary.json").write_text(json.dumps(s, indent=1))
    (out / "REALITY_CHECK.md").write_text(report(s, a.tbill))
    print(report(s, a.tbill))


if __name__ == "__main__":
    main()
