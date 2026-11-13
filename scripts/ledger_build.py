#!/usr/bin/env python3
"""The public ledger: every real-money round trip our bots made (2 to 8 November 2026), rebuilt from the bots' own
public log and state files into site/data/bot_trades.json, which the home page reads.

    python scripts/ledger_build.py --git .       # read the logs from origin/data and origin/mrp-data of this clone
    python scripts/ledger_build.py --raw         # or from raw.githubusercontent.com
    python scripts/ledger_build.py --dir DIR     # or from DIR/data/... and DIR/mrp-data/...
    add --check to compare with the committed file instead of writing it

Sources (public branches of github.com/watkast/predictionbots):
    data      mrh-live/live_trades.jsonl               Mr H, Coinbase spot: one line per fill
    mrp-data  mre/state.json, mre/live.jsonl           Mr E, Polymarket US ETH 15-minute: one record per round, and the log
    mrp-data  mre-btc/state.json, mre-btc/live.jsonl   Mr E, Polymarket US BTC 15-minute
    mrp-data  mrp/live/live.jsonl                      Mr P, Polymarket US BTC 15-minute: order and fill lines
    mrp-data  mrt/state.json, mrs/state.json           Mr T and Mr S: switched on, never filled

How each number is made (nothing is typed in except the UNLOGGED table below, which cites its evidence):
    Mr H   net per trade is the bot's own `net` on each sell line: proceeds minus cost, after Coinbase's fees.
    Mr E   net per round is the bot's own `pnl`: proceeds minus cost. Its buys and its capped sell rest on the book
           (no fee on Polymarket US); an early exit takes liquidity and is booked net of the taker fee
           (6.95% x price x (1 - price), the rate for the account at the time).
    Mr P   from the fill lines of its live runs: cost is quantity x (price + taker fee), proceeds are as logged
           (already net of the fee), exactly as scripts/pm15_live.js books a trade.
    Nine Mr E rounds have a buy on record and no result: the run was restarted or ended first. They are settled here
    from what the log does show (a sale, or the position held with seconds left) and the venue's own result.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "data" / "bot_trades.json"
RAW = "https://raw.githubusercontent.com/watkast/predictionbots"
FILES = {"mrh": ("data", "mrh-live/live_trades.jsonl"),
         "mre_state": ("mrp-data", "mre/state.json"), "mre_log": ("mrp-data", "mre/live.jsonl"),
         "mreb_state": ("mrp-data", "mre-btc/state.json"), "mreb_log": ("mrp-data", "mre-btc/live.jsonl"),
         "mrp_log": ("mrp-data", "mrp/live/live.jsonl"), "mrt_state": ("mrp-data", "mrt/state.json"), "mrs_state": ("mrp-data", "mrs/state.json")}
PM_TAKER = 0.0695                    # Polymarket US taker coefficient the bots booked with (the account's rate, 2 to 4 Nov 2026)
fee = lambda p: PM_TAKER * p * (1 - p)

# Mr E rounds with a buy on record and no result (the run was restarted, or ended, before the bot wrote it).
#   result/ptb/settle: the venue's record for the round (gateway.polymarket.us/v1/market/slug/<slug>, read 13 Nov 2026;
#     for the BTC round of 4 Nov 04:15 that endpoint now returns no prices, so the figures are the settlement our
#     recorder stored at the time: mrp-data, mrp/data/run-20261104T0137-41749386804/2026-11-04/04*.jsonl.gz).
#   how: what the public record shows about the position between the buy and the bell. "held" = the bot's own log line
#     with the position 2 seconds before the close. Where a sell was still resting, the order book the recorder stored
#     for that round (mrp-data, mrp/data/<run>/<date>/<hour>*.jsonl.gz) shows the price never reached it.
UNLOGGED = {
    "cpceth-eth-updown-15m-2026-11-02-2230z": {"result": "DOWN", "ptb": 2249.97, "settle": 2247.37,
        "how": "its 55¢ sell never filled: after the buy the best bid for Up was 35¢ (recorded books)"},
    "cpceth-eth-updown-15m-2026-11-03-0200z": {"result": "DOWN", "ptb": 2255.32, "settle": 2252.29,
        "how": "its 55¢ sell never filled: after the buy the best bid for Up was 36¢ (recorded books)"},
    "cpceth-eth-updown-15m-2026-11-03-0445z": {"result": "UP", "ptb": 2252.82, "settle": 2253.84,
        "how": "its 45¢ sell never filled: Down was never bid above 36¢ after the buys (recorded books)"},
    "cpceth-eth-updown-15m-2026-11-03-0645z": {"result": "DOWN", "ptb": 2246.95, "settle": 2242.37, "how": "held with 2 seconds left (log)"},
    "cpceth-eth-updown-15m-2026-11-04-0415z": {"result": "DOWN", "ptb": 2263.04, "settle": 2257.65, "how": "held with 2 seconds left (log)"},
    "cpc-btc-updown-15m-2026-11-03-0700z": {"result": "UP", "ptb": 76452.11, "settle": 76461.96, "how": "sold before the restart (log)"},
    "cpc-btc-updown-15m-2026-11-03-0715z": {"result": "UP", "ptb": 76461.96, "settle": 76743.29, "how": "held with 2 seconds left (log)"},
    "cpc-btc-updown-15m-2026-11-03-0800z": {"result": "DOWN", "ptb": 76699.50, "settle": 76664.90,
        "how": "its 60¢ sell never filled: after the buys the best bid for Up was 27¢ (recorded books)"},
    "cpc-btc-updown-15m-2026-11-04-0415z": {"result": "DOWN", "ptb": 76756.76, "settle": 76670.93, "how": "held with 2 seconds left (log)"},
}


# ----------------------------------------------------------------------------- reading
def _reader(args):
    if args.dir:
        return lambda br, path: (Path(args.dir) / br / path).read_text()
    if args.raw:
        def get(br, path):
            with urllib.request.urlopen(f"{RAW}/{br}/{path}", timeout=120) as r:
                return r.read().decode()
        return get
    repo = args.git or str(ROOT)
    return lambda br, path: subprocess.run(["git", "-C", repo, "show", f"origin/{br}:{path}"], check=True, capture_output=True, text=True).stdout


def _lines(txt: str) -> list[dict]:
    out = []
    for l in txt.splitlines():
        l = l.strip()
        if l:
            try:
                out.append(json.loads(l))
            except ValueError:
                pass
    return out


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _c(x: float) -> str:
    """A share price in cents, without a trailing .0: 0.275 -> '27.5', 0.6 -> '60'."""
    return f"{round(x * 100, 1):g}"


# ----------------------------------------------------------------------------- the bots
def mr_h(txt: str) -> list[dict]:
    rows = []
    for r in _lines(txt):
        if r.get("ev") != "sell":
            continue
        net = round(float(r["net"]), 2)
        rows.append({"t": r["t"], "m": r["pid"].replace("-USD", "") + " · Coinbase", "s": "long", "u": "$", "i": r["entry_px"], "o": r["px"],
                     "cost": round(float(r["proceeds"]) - float(r["net"]), 4), "n": net, "w": r.get("reason") or "sold"})
    return rows


def mr_e(state_txt: str, log_txt: str, coin: str) -> list[dict]:
    state, log = json.loads(state_txt), _lines(log_txt)
    assert state.get("mode") == "live", "Mr E state is not from a live run"
    sold_by_slug: dict[str, list[tuple[float, float]]] = {}
    for r in log:
        d = r.get("d") or {}
        if r.get("k") == "fill" and "sold" in d:
            px = float(d["sold"])
            sold_by_slug.setdefault(d["slug"], []).append((px - fee(px) if d.get("exit") == "stall" else px, float(d.get("qty", 1))))   # early lines: one share, no qty
    rows = []
    for rec in state["rounds"]:
        if rec.get("buyPx") is None:
            continue                                     # the ladder rested and nothing filled: no trade
        qty = float(rec.get("qty") or 1)
        cost = float(rec["buyPx"]) * qty
        side = "Up" if rec["side"] == "UP" else "Down"
        row = {"t": _iso(rec["T0"] + 900), "m": f"{coin} 15m · Polymarket US", "s": side + (f" ×{qty:g}" if qty != 1 else ""), "u": "c",
               "i": round(float(rec["buyPx"]), 4), "cost": round(cost, 4)}
        if rec.get("pnl") is not None:
            net, why = float(rec["pnl"]), rec.get("exit") or "closed"
        else:
            ev = UNLOGGED.get(rec["slug"])
            assert ev, f"round with a buy and no result, not in UNLOGGED: {rec['slug']}"
            sold = sold_by_slug.get(rec["slug"], [])
            sold_q, proceeds = sum(q for _, q in sold), sum(p * q for p, q in sold)
            left = qty - sold_q
            won = rec["side"] == ev["result"]
            net = proceeds + (left if won and left > 1e-9 else 0.0) - cost
            if left <= 1e-9:
                why = f"sold at {_c(proceeds / sold_q)}¢"
            else:
                n = f"{left:g} " if qty != 1 else ""
                why = (f"{sold_q:g} sold at {_c(proceeds / sold_q)}¢ + " if sold_q else "") + n + ("won at the bell" if won else "lost at the bell")
            row["f"] = 1
            row["e"] = (f"The bot was restarted before it wrote this result. Venue record: settled {ev['result'].title()}, "
                        f"{ev['settle']:,.2f} against {ev['ptb']:,.2f}. Position: {ev['how']}.")
        row["n"] = round(net, 2)
        row["o"] = round((cost + net) / qty, 4)          # what each share came back as, after any fee
        row["w"] = why
        rows.append(row)
    return rows


def mr_p(log_txt: str) -> list[dict]:
    rows, live, pos = [], False, None
    for r in _lines(log_txt):
        k, d = r.get("k"), r.get("d") or {}
        if k == "start":
            live = d.get("mode") == "live"
        if not live or k != "fill":
            continue
        px, q = float(d["px"]), float(d["qty"])
        if d.get("kind") == "buy":
            assert pos is None, "Mr P bought while holding"
            pos = {"side": d["side"], "px": px, "qty": q, "spent": q * (px + fee(px)), "proceeds": 0.0, "sold": 0.0, "sell_val": 0.0}
        elif d.get("kind") == "sell" and pos:
            pos["proceeds"] += float(d["proceeds"]); pos["sold"] += q; pos["sell_val"] += px * q
            if pos["sold"] >= pos["qty"] - 1e-9:
                net = round(pos["proceeds"] - pos["spent"], 2)
                rows.append({"t": _iso(r["t"] / 1000), "m": "BTC 15m · Polymarket US", "s": ("Up" if pos["side"] == "UP" else "Down") + f" ×{pos['qty']:g}", "u": "c",
                             "i": pos["px"], "o": round(pos["sell_val"] / pos["sold"], 4), "cost": round(pos["spent"], 4), "n": net,
                             "w": f"sold at {_c(pos['sell_val'] / pos['sold'])}¢ (taker, fees both ways)"})
                pos = None
    assert pos is None, "Mr P ended a live run holding a position the log never closed"
    return rows


# ----------------------------------------------------------------------------- assembly
BOTS = [  # id, name, where, the idea in a line, sources
    ("mre", "Mr E (ETH)", "Polymarket US, ETH 15-minute", "Rest a buy at 25 to 30¢ on both sides each round; sell the bounce or hold to the bell.", ["mrp-data/mre/state.json", "mrp-data/mre/live.jsonl"]),
    ("mreb", "Mr E (BTC)", "Polymarket US, BTC 15-minute", "The same rule on the BTC market.", ["mrp-data/mre-btc/state.json", "mrp-data/mre-btc/live.jsonl"]),
    ("mrp", "Mr P", "Polymarket US, BTC 15-minute", "Buy the favorite when a fair-value model says the price is too low; sell when it catches up.", ["mrp-data/mrp/live/live.jsonl"]),
    ("mrh", "Mr H", "Coinbase spot", "Buy a 5-minute spike, trail a stop.", ["data/mrh-live/live_trades.jsonl"]),
    ("mrt", "Mr T", "Polymarket US, final seconds", "Buy the already-decided side in the last 5 seconds.", ["mrp-data/mrt/state.json"]),
    ("mrs", "Mr S", "Kalshi soccer", "Buy contracts the score has already decided.", ["mrp-data/mrs/state.json"]),
]


def build(read) -> dict:
    got = {k: read(br, path) for k, (br, path) in FILES.items()}
    per = {"mre": mr_e(got["mre_state"], got["mre_log"], "ETH"), "mreb": mr_e(got["mreb_state"], got["mreb_log"], "BTC"),
           "mrp": mr_p(got["mrp_log"]), "mrh": mr_h(got["mrh"]), "mrt": [], "mrs": []}
    mrt, mrs = json.loads(got["mrt_state"]), json.loads(got["mrs_state"])
    assert not mrt.get("fills") and not mrt.get("trades"), "Mr T has fills: add a parser"
    assert not mrs.get("trades"), "Mr S has trades: add a parser"
    notes = {"mrt": f"{int(mrt.get('attempts', 0))} orders sent, none filled: the winning side was never offered.",
             "mrs": "Switched on 3 to 4 Nov. Every decided contract it saw failed one of its checks, most often because nobody was still selling. No order placed.",
             "mrh": "The first position was bought by hand and handed to the bot to manage.",
             "mre": "", "mreb": "", "mrp": ""}
    bots, rows = [], []
    for i, (bid, name, where, idea, src) in enumerate(BOTS):
        rs = per[bid]
        for r in rs:
            r["b"] = i
        rows += rs
        ts = sorted(r["t"] for r in rs)
        bots.append({"bot": name, "where": where, "idea": idea, "src": src, "note": notes[bid], "trips": len(rs),
                     "won": sum(r["n"] > 0 for r in rs), "lost": sum(r["n"] < 0 for r in rs), "flat": sum(r["n"] == 0 for r in rs),
                     "net": round(sum(r["n"] for r in rs), 2), "staked": round(sum(r["cost"] for r in rs), 2),
                     "first": ts[0][:10] if ts else None, "last": ts[-1][:10] if ts else None, "unlogged": sum(1 for r in rs if r.get("f"))})
    rows.sort(key=lambda r: r["t"], reverse=True)
    for r in rows:
        r["cost"] = round(r["cost"], 2)
    total = {"trips": len(rows), "won": sum(b["won"] for b in bots), "lost": sum(b["lost"] for b in bots), "flat": sum(b["flat"] for b in bots),
             "net": round(sum(b["net"] for b in bots), 2), "staked": round(sum(b["staked"] for b in bots), 2), "unlogged": sum(b["unlogged"] for b in bots)}
    return {"window": ["2026-11-02", "2026-11-08"], "closed": "2026-11-08",
            "method": "Built by scripts/ledger_build.py from the bots' own log and state files on this repository's public data branches. "
                      "One row is one round trip: a position opened and closed. Net is after venue fees.",
            "repo": "https://github.com/watkast/predictionbots", "bots": bots, "total": total, "rows": rows}


def selfcheck(d: dict) -> None:
    """The totals the bots themselves reported, so a parsing slip cannot pass quietly."""
    by = {b["bot"]: b for b in d["bots"]}
    logged = lambda name: round(sum(r["n"] for r in d["rows"] if d["bots"][r["b"]]["bot"] == name and not r.get("f")), 2)
    assert logged("Mr E (ETH)") == -9.61 and logged("Mr E (BTC)") == -7.13, "Mr E rounds no longer match the bots' own MRE.md totals"
    assert by["Mr H"]["net"] == -0.53 and by["Mr H"]["trips"] == 6, "Mr H no longer matches its LIVE.md"
    assert d["total"]["unlogged"] == len(UNLOGGED) == 9
    assert d["total"]["trips"] == sum(b["trips"] for b in d["bots"]) == len(d["rows"])
    assert abs(d["total"]["net"] - sum(r["n"] for r in d["rows"])) < 0.005


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--git", help="a clone with origin/data and origin/mrp-data fetched (default: this repo)")
    ap.add_argument("--raw", action="store_true", help="read from raw.githubusercontent.com")
    ap.add_argument("--dir", help="read from DIR/<branch>/<path>")
    ap.add_argument("--check", action="store_true", help="compare with the committed file; exit 1 if it differs")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    d = build(_reader(a))
    selfcheck(d)
    txt = json.dumps(d, ensure_ascii=False, separators=(",", ":")) + "\n"
    t = d["total"]
    print(f"{t['trips']} round trips · {t['won']} won · {t['lost']} lost · {t['flat']} flat · net {t['net']:+.2f} on {t['staked']:.2f} staked", file=sys.stderr)
    for b in d["bots"]:
        print(f"  {b['bot']:<11} {b['trips']:>4} trips  net {b['net']:+7.2f}  staked {b['staked']:>7.2f}  {b['first']} to {b['last']}", file=sys.stderr)
    if a.check:
        if Path(a.out).read_text() != txt:
            sys.exit(f"{a.out} is not what the logs produce: run scripts/ledger_build.py and commit the result")
        print("matches the committed file", file=sys.stderr)
        return
    Path(a.out).write_text(txt)
    print(f"wrote {a.out} ({len(txt):,} bytes)", file=sys.stderr)


if __name__ == "__main__":
    main()
