"""ORACLE-LAG rule on Polymarket US's own data (data branch, polyus/): per-window priceToBeat +
settlementPrice, 1-minute Yes/No display prices (longPrice = Up best ask, shortPrice = 1 - Up best
bid), and BRTI 1-minute candles (the settlement index).

Two execution models, same signal:
  taker  (doc)  : at the first signalled minute in [entry_from, entry_to], buy the side at its ask if
                  ask <= cap; rest a sell at `target`; else hold to settlement. Taker fee 0.0695*p*(1-p).
  maker  (user) : at the first signalled minute, rest a bid `bid_off` below the ask; filled only when a
                  later minute's ask trades at/through our bid (conservative). Then: sell at `target`
                  when the bid gets there; cash out at the bid when the index comes back inside the chop
                  band ("sell for less"); else settlement. Maker fee 0.
Size: `size_usd` notional, no depth data -> flagged in the report (depth unknown at this fidelity).
"""
from __future__ import annotations

import argparse
import glob
import json
import math
from datetime import datetime, timezone

import numpy as np
import pandas as pd


def load(root: str):
    mk = {m["slug"]: m for m in json.load(open(f"{root}/markets.json"))}
    ph = {}
    for f in glob.glob(f"{root}/price_history/*.json"):
        d = json.load(open(f))
        if d.get("history"):
            ph[d["slug"]] = d
    br = pd.DataFrame(json.load(open(f"{root}/brti_1m.json")))
    br["ts"] = br.timestamp.astype(int)
    for c in ("open", "high", "low", "close"):
        br[c] = br[c].astype(float)
    br = br.drop_duplicates("ts").set_index("ts").sort_index()
    return mk, ph, br


def amount(v):
    if isinstance(v, dict):
        v = v.get("value")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def run(a):
    mk, ph, br = load(a.data)
    closes = br.close
    rows = []
    for slug, d in ph.items():
        m = mk.get(slug) or {}
        t = m.get("assetPriceTerms") or {}
        ptb = amount(t.get("priceToBeat"))
        sp = amount(t.get("settlementPrice"))
        ws, we = int(d["windowStart"]), int(d["windowEnd"])
        if ptb is None or sp is None:
            continue
        hist = {int(h["timestamp"]): h for h in d["history"]}
        # need BRTI for the 15 minutes before the window through the window
        need = [ws + 60 * k for k in range(-15, 15)]
        if not all(ts in closes.index for ts in need):
            continue
        settle = "UP" if sp >= ptb else "DOWN"
        rec = dict(slug=slug, open=ws, anchor=ptb, settle=settle, signal=None)
        # realised 1-min vol over the prior 60 minutes (for the fair-value readout)
        prev = closes.loc[ws - 3600:ws]
        sig_usd = float(np.std(np.diff(np.log(prev.values))) * ptb) if len(prev) > 10 else 30.0
        for mmin in range(int(a.entry_from), int(a.entry_to) + 1):
            T = ws + 60 * mmin
            if T not in hist or (we - T) <= a.kill_secs:
                continue
            spot = closes[T - 60]                     # candle ending at T
            twap = closes.loc[T - 60 * 15:T - 60].mean()
            dev = spot - ptb
            if abs(dev) < a.chop_band:
                continue
            veto = False
            if a.v4:
                twap3 = closes.loc[T - 60 * 18:T - 60 * 4].mean()
                slope = twap - twap3
                veto = (slope > 0 and spot < twap) or (slope < 0 and spot > twap)
            if dev > 0 and twap > ptb + a.buffer and not veto:
                side = "UP"
            elif dev < 0 and twap < ptb - a.buffer and not veto:
                side = "DOWN"
            else:
                continue
            h = hist[T]
            up_ask, up_bid = float(h["longPrice"]), 1 - float(h["shortPrice"])
            ask = up_ask if side == "UP" else 1 - up_bid
            bid = up_bid if side == "UP" else 1 - up_ask
            tau = max((we - T) / 60 - 0.5, 0.25)
            z = dev / (sig_usd * math.sqrt(tau)) if sig_usd > 0 else 0
            p = 0.5 * (1 + math.erf(z / math.sqrt(2)))
            fair = p if side == "UP" else 1 - p
            rec.update(signal=side, sig_min=mmin, dev=dev, ask=ask, bid=bid, fair=fair, sigma=sig_usd)

            def side_px(T2):
                h2 = hist.get(T2)
                if h2 is None:
                    return None, None
                ua, ub = float(h2["longPrice"]), 1 - float(h2["shortPrice"])
                return (ua, ub) if side == "UP" else (1 - ub, 1 - ua)

            later = [ws + 60 * k for k in range(mmin + 1, 15)]
            # ---- taker (doc) ----
            if ask <= a.cap and ask < a.ceasefire and ask > 0:
                n = a.size_usd / ask
                fee = 0.0695 * ask * (1 - ask) * n
                pnl = None
                for T2 in later:
                    a2, b2 = side_px(T2)
                    if b2 is not None and b2 >= a.target:
                        pnl = n * (a.target - ask) - fee
                        rec["taker_exit"] = "target"
                        break
                if pnl is None:
                    pnl = n * (1.0 if settle == side else 0.0) - a.size_usd - fee
                    rec["taker_exit"] = "settle_win" if settle == side else "settle_loss"
                rec.update(taker_px=ask, taker_pnl=pnl)
            else:
                rec["taker_exit"] = "no_fill_ask_%.2f" % ask
            # ---- maker (user) ----
            bid_px = round(min(ask - a.bid_off, a.cap), 2)
            fill_T = None
            for T2 in later:
                a2, b2 = side_px(T2)
                if a2 is not None and a2 <= bid_px:
                    fill_T = T2
                    break
            if fill_T is None:
                rec["maker_exit"] = "no_fill"
            else:
                n = a.size_usd / bid_px
                pnl = None
                for T2 in [x for x in later if x > fill_T]:
                    a2, b2 = side_px(T2)
                    if b2 is None:
                        continue
                    spot2 = closes[T2 - 60]
                    dev2 = spot2 - ptb if side == "UP" else ptb - spot2
                    if b2 >= a.target:
                        pnl = n * (a.target - bid_px)
                        rec["maker_exit"] = "target"
                        break
                    if a.revert_exit and dev2 < a.chop_band and b2 > 0:
                        pnl = n * (b2 - bid_px)
                        rec["maker_exit"] = "revert_%.2f" % b2
                        break
                if pnl is None:
                    pnl = n * (1.0 if settle == side else 0.0) - a.size_usd
                    rec["maker_exit"] = "settle_win" if settle == side else "settle_loss"
                rec.update(maker_px=bid_px, maker_fill_min=(fill_T - ws) // 60, maker_pnl=pnl)
            break
        rows.append(rec)

    df = pd.DataFrame(rows)
    sg = df[df.signal.notna()]
    print(f"windows with BRTI+prices: {len(df)}   signals: {len(sg)}   "
          f"direction right: {(sg.signal == sg.settle).mean():.1%}")
    print("ask on signalled side at signal: " + ", ".join(f"p{q}={sg.ask.quantile(q/100):.2f}" for q in (10, 25, 50, 75, 90)))
    print(f"fair (model) vs ask: fair median {sg.fair.median():.2f}, ask median {sg.ask.median():.2f}; "
          f"ask <= {a.cap}: {(sg.ask <= a.cap).sum()}")
    for model in ("taker", "maker"):
        col = f"{model}_pnl"
        e = sg[sg[col].notna()]
        if not len(e):
            print(f"[{model}] no fills")
            continue
        ex = e[f"{model}_exit"].value_counts().to_dict()
        print(f"[{model}] fills {len(e)}  net ${e[col].sum():.2f}  per fill ${e[col].mean():.2f}  "
              f"win rate {(e[col] > 0).mean():.0%}  worst ${e[col].min():.2f}  exits {ex}")
    if a.out:
        df.to_csv(a.out, index=False)
    return df


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/polyus")
    ap.add_argument("--buffer", type=float, default=20.0)
    ap.add_argument("--chop-band", type=float, default=10.0)
    ap.add_argument("--entry-from", type=float, default=10)
    ap.add_argument("--entry-to", type=float, default=13)
    ap.add_argument("--kill-secs", type=float, default=45)
    ap.add_argument("--cap", type=float, default=0.85)
    ap.add_argument("--ceasefire", type=float, default=0.93)
    ap.add_argument("--target", type=float, default=0.88)
    ap.add_argument("--size-usd", type=float, default=300.0)
    ap.add_argument("--bid-off", type=float, default=0.05, help="maker: rest this far below the ask")
    ap.add_argument("--revert-exit", type=int, default=1)
    ap.add_argument("--v4", type=int, default=1)
    ap.add_argument("--out", default="")
    run(ap.parse_args())
