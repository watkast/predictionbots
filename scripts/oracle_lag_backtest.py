"""Backtest of the "Project ORACLE-LAG v3" 15-minute BTC rule (15_Min_BTC_Automation.docx)
against the recorded Polymarket / Kalshi 15-minute BTC books and the recorded Coinbase
spot tape on the `data` branch.

Rule (doc + Pine, parameterised):
  anchor      = spot at window open (Pine: round's first 1-min open; Kalshi: floor_strike)
  twap        = "pine": SMA of the last 15 one-minute closes (current minute = live spot)
                "doc" : mean of locked minute closes + live spot for the unknown minutes
  window      = elapsed [entry_from, entry_to] seconds of the 15-min round (doc: 600..825)
  BUY UP      spot > anchor and twap > anchor + buffer  (buffer $20)
  BUY DOWN    spot < anchor and twap < anchor - buffer
  ATR guard   ATR(14, 1-min) > 2.5 * SMA(ATR, 100)  -> no trade
  entry       IOC $300 against the recorded asks, ceiling 0.85, skip if best ask >= 0.93,
              skip if <= 45 s to close
  exit        resting sell at 0.88: filled when a later print at >= 0.88 occurs or the best
              bid reaches 0.88 (we hit it); otherwise held to settlement
  settlement  final recorded book (>= 0.9 -> UP won, <= 0.1 -> DOWN won); falls back to
              spot(close) vs anchor; both reported
  fees        venue taker fee on entry (Polymarket crypto 0.07*p(1-p), Kalshi 0.07*p(1-p)),
              exit as maker = free (Polymarket) / free (KXBTC15M)

No fantasy fills: entry size is capped by the resting depth at <= 0.85 and the exit only
happens where the tape or the book proves a buyer at 0.88.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
from collections import defaultdict

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


def load_markets(root: str) -> pd.DataFrame:
    rows = []
    for f in sorted(glob.glob(f"{root}/*/*/markets-*.parquet")):
        try:
            rows.append(pd.read_parquet(f))
        except Exception:
            pass
    df = pd.concat(rows).drop_duplicates("market_id", keep="last")
    out = []
    for _, r in df.iterrows():
        meta = json.loads(r.meta_json) if isinstance(r.meta_json, str) else {}
        if r.venue == "polymarket":
            slug = str(meta.get("slug", ""))
            if not slug.startswith("btc-updown-15m-"):
                continue
            out.append(dict(venue="polymarket", market_id=r.market_id, open=float(meta["window_open_ts"]),
                            close=float(meta["window_close_ts"]), strike=None, title=r.title,
                            no_token=meta.get("no_token")))
        elif r.venue == "kalshi" and r.series == "KXBTC15M":
            out.append(dict(venue="kalshi", market_id=r.market_id, open=float(meta["window_open_ts"]),
                            close=float(meta["window_close_ts"]), strike=meta.get("floor_strike"),
                            title=r.title, no_token=None, result=r.result))
    return pd.DataFrame(out).sort_values("open").reset_index(drop=True)


def load_spot(root: str) -> pd.DataFrame:
    rows = []
    for f in sorted(glob.glob(f"{root}/*/*/signals-*.parquet")):
        try:
            t = pq.read_table(f, filters=[("name", "=", "btc_index")]).to_pandas()
        except Exception:
            continue
        if len(t):
            rows.append(t)
    s = pd.concat(rows).drop_duplicates("ts").sort_values("ts")
    s["price"] = s.value_json.map(lambda v: json.loads(v).get("price"))
    return s[["ts", "price"]].dropna().reset_index(drop=True)


def load_rows(root: str, kind: str, ids: set[str], cols: list[str]) -> pd.DataFrame:
    rows = []
    for f in sorted(glob.glob(f"{root}/*/*/{kind}-*.parquet")):
        try:
            t = pq.read_table(f, columns=cols, filters=[("market_id", "in", list(ids))]).to_pandas()
        except Exception:
            continue
        if len(t):
            rows.append(t)
    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.concat(rows).sort_values("ts").reset_index(drop=True)


def minute_bars(spot: pd.DataFrame) -> pd.DataFrame:
    m = (spot.ts // 60).astype(int) * 60
    g = spot.groupby(m).price
    bars = pd.DataFrame({"open": g.first(), "high": g.max(), "low": g.min(), "close": g.last()})
    bars.index.name = "ts"
    bars = bars.reset_index()
    prev = bars.close.shift(1)
    tr = np.maximum(bars.high - bars.low, np.maximum((bars.high - prev).abs(), (bars.low - prev).abs()))
    bars["atr14"] = tr.rolling(14).mean()
    bars["atr_sma100"] = bars.atr14.rolling(100).mean()
    gap = bars.ts.diff() > 60
    # a bar after a tape gap must not reuse stale ATR history
    bars.loc[gap, ["atr14", "atr_sma100"]] = np.nan
    return bars.set_index("ts")


def taker_fee(venue: str, p: float, n: float) -> float:
    base = n * p * (1 - p)
    if venue == "kalshi":
        return math.ceil(0.07 * base * 100 - 1e-9) / 100
    return 0.07 * base  # Polymarket crypto taker rate


def run(args):
    mk = load_markets(args.data)
    spot = load_spot(args.data)
    bars = minute_bars(spot)
    ts_arr = spot.ts.values
    px_arr = spot.price.values
    ids = set(mk.market_id)
    books = load_rows(args.data, "books", ids, ["ts", "market_id", "side", "price", "size", "level"])
    trades = load_rows(args.data, "trades", ids, ["ts", "market_id", "price", "size", "taker_action"])
    books_by = {k: g for k, g in books.groupby("market_id")}
    trades_by = {k: g for k, g in trades.groupby("market_id")}

    def spot_at(t: float):
        i = np.searchsorted(ts_arr, t, side="right") - 1
        if i < 0 or t - ts_arr[i] > args.max_spot_age:
            return None
        return float(px_arr[i])

    results = []
    skipped = defaultdict(int)
    for _, w in mk.iterrows():
        b = books_by.get(w.market_id)
        if b is None or len(b) == 0:
            skipped["no_books"] += 1
            continue
        snaps = {t: g for t, g in b.groupby("ts")}
        snap_ts = np.array(sorted(snaps))
        in_win = snap_ts[(snap_ts >= w.open + args.entry_from) & (snap_ts <= w.open + args.entry_to)]
        if len(in_win) == 0:
            skipped["no_books_in_window"] += 1
            continue
        open_spot = spot_at(w.open + 1)
        if open_spot is None:
            skipped["no_spot_at_open"] += 1
            continue
        anchor = float(w.strike) if (args.anchor == "strike" and w.strike) else open_spot
        # minute closes for the round
        rec = dict(venue=w.venue, market=w.market_id[:12], title=w.title, open=w.open, anchor=anchor,
                   signal=None, signal_ts=None, entered=False)
        sig = None
        for t in in_win:
            s = spot_at(t)
            if s is None:
                continue
            m = int((t - w.open) // 60)  # locked minutes
            closes = [spot_at(w.open + 60 * (k + 1) - 0.001) for k in range(m)]
            if any(c is None for c in closes):
                continue
            if args.twap == "doc":
                twap = (sum(closes) + s * (15 - m)) / 15
            else:  # pine: SMA(close,15) on 1-min bars, current bar = live spot
                # previous 15 minute bars incl. the forming one
                hist = [spot_at(w.open + 60 * (k + 1) - 0.001) for k in range(m - 14, m)]
                hist = [h for h in hist if h is not None]
                twap = (sum(hist) + s) / (len(hist) + 1)
            bar_ts = int(t // 60) * 60
            atr = bars.atr14.get(bar_ts, np.nan)
            atr_avg = bars.atr_sma100.get(bar_ts, np.nan)
            danger = (not np.isnan(atr)) and (not np.isnan(atr_avg)) and atr > args.atr_mult * atr_avg
            if args.atr_guard and danger:
                rec["atr_abort"] = True
                continue
            if abs(s - anchor) < args.chop_band:
                continue
            # v4 Rule D veto: TWAP slope (vs 3 bars ago) against the price's side of the TWAP
            veto = False
            if args.v4:
                hist3 = [spot_at(w.open + 60 * (k + 1) - 0.001) for k in range(m - 17, m - 3)]
                hist3 = [h for h in hist3 if h is not None]
                s3 = spot_at(w.open + 60 * (m - 3) - 0.001) if m >= 3 else None
                if hist3 and s3 is not None:
                    twap3 = (sum(hist3) + s3) / (len(hist3) + 1)
                    slope = twap - twap3
                    veto = (slope > 0 and s < twap) or (slope < 0 and s > twap)
            if s > anchor and twap > anchor + args.buffer and not veto:
                sig = "UP"
            elif s < anchor and twap < anchor - args.buffer and not veto:
                sig = "DOWN"
            else:
                if veto:
                    rec["vetoed"] = True
                continue
            rec.update(signal=sig, signal_ts=t, signal_min=round((t - w.open) / 60, 2), spot=s, twap=twap,
                       dev=s - anchor)
            if w.close - t <= args.kill_secs:
                rec["reason"] = "kill_switch_45s"
                break
            snap = snaps[t]
            # YES-leg book: UP = buy YES asks; DOWN = buy NO = sell YES into bids (price 1-bid)
            if sig == "UP":
                lv = snap[snap.side == "ask"].sort_values("price")
                lv = lv.assign(p=lv.price)
            else:
                lv = snap[snap.side == "bid"].sort_values("price", ascending=False)
                lv = lv.assign(p=1 - lv.price)
            if len(lv) == 0:
                rec["reason"] = "empty_book"
                break
            best = float(lv.p.iloc[0])
            rec["best_ask_side"] = best
            if best >= args.ceasefire:
                rec["reason"] = f"ceasefire_{best:.2f}"
                break
            if best > args.cap:
                rec["reason"] = f"ask_above_cap_{best:.2f}"
                if args.retry_until_cap:
                    sig = None
                    continue
                break
            # walk the asks up to the cap with $300
            cash = args.size_usd
            filled = 0.0
            cost = 0.0
            for _, l in lv.iterrows():
                if l.p > args.cap or cash <= 0:
                    break
                n = min(float(l.size) * args.depth_frac, cash / l.p)
                filled += n
                cost += n * l.p
                cash -= n * l.p
            if filled < 1:
                rec["reason"] = "no_depth"
                break
            avg = cost / filled
            fee = taker_fee(w.venue, avg, filled)
            rec.update(entered=True, entry_ts=t, entry_px=avg, contracts=filled, cost=cost, fee=fee)
            # exit: resting sell at target. Proof of a buyer: a print at >= target on the side's leg,
            # or the side's best bid >= target.
            exit_px = None
            exit_ts = None
            tr = trades_by.get(w.market_id)
            later_ts = snap_ts[snap_ts > t]
            if tr is not None:
                tr = tr[tr.ts > t]
                tp = tr.price if sig == "UP" else 1 - tr.price
                hit = tr[tp >= args.target]
                if len(hit):
                    exit_ts = float(hit.ts.iloc[0])
                    exit_px = args.target
            stop_hit = None
            for t2 in later_ts:
                if exit_ts is not None and t2 >= exit_ts:
                    break
                s2 = snaps[t2]
                if sig == "UP":
                    bb = s2[s2.side == "bid"].price.max()
                else:
                    ba = s2[s2.side == "ask"].price.min()
                    bb = 1 - ba if not np.isnan(ba) else np.nan
                if not np.isnan(bb) and bb >= args.target:
                    exit_ts, exit_px = float(t2), args.target
                    break
                # discretionary "sell for less": the move is coming back (spot re-enters the chop band
                # or crosses the anchor) or the side's bid has dropped `stop` below our entry
                if args.revert_exit or args.stop > 0:
                    s_now = spot_at(t2)
                    revert = args.revert_exit and s_now is not None and (
                        (sig == "UP" and s_now - anchor < args.chop_band) or (sig == "DOWN" and anchor - s_now < args.chop_band))
                    stopped = args.stop > 0 and not np.isnan(bb) and bb <= avg - args.stop
                    if (revert or stopped) and not np.isnan(bb) and bb > 0:
                        exit_ts, exit_px = float(t2), float(bb)
                        stop_hit = "revert" if revert else "stop"
                        break
            # settlement
            last = snaps[snap_ts[-1]]
            bid = last[last.side == "bid"].price.max()
            ask = last[last.side == "ask"].price.min()
            mid = np.nanmean([bid, ask])
            close_spot = spot_at(w.close - 0.001)
            settle_book = None
            if not np.isnan(mid):
                settle_book = "UP" if mid >= 0.9 else "DOWN" if mid <= 0.1 else None
            settle_spot = None if close_spot is None else ("UP" if close_spot > anchor else "DOWN")
            if w.venue == "kalshi" and not pd.isna(w.get("result", np.nan)):
                settle_book = "UP" if float(w.result) >= 0.5 else "DOWN"
            settle = settle_book or settle_spot
            rec.update(settle_book=settle_book, settle_spot=settle_spot, close_spot=close_spot)
            if exit_px is not None:
                pnl = filled * (exit_px - avg) - fee
                rec.update(exit=stop_hit or "target", exit_px=exit_px, exit_ts=exit_ts,
                           exit_min=round((exit_ts - w.open) / 60, 2), pnl=pnl)
            elif settle is not None:
                pay = filled * (1.0 if settle == sig else 0.0)
                rec.update(exit="settle", won=(settle == sig), pnl=pay - cost - fee)
            else:
                rec.update(exit="unknown", pnl=np.nan)
            break
        results.append(rec)

    df = pd.DataFrame(results)
    ent = df[df.entered == True]
    print(f"windows with books: {len(df)}  signals: {df.signal.notna().sum()}  entered: {len(ent)}  skipped: {dict(skipped)}")
    if "reason" in df:
        print("no-entry reasons:", df[df.signal.notna() & (df.entered != True)].reason.value_counts().to_dict())
    if "atr_abort" in df:
        print("rounds with an ATR abort at some point:", int(df.atr_abort.fillna(False).sum()))
    if len(ent):
        for v, g in ent.groupby("venue"):
            tgt = (g.exit == "target").sum()
            early = g[g.exit.isin(["revert", "stop"])]
            st = g[g.exit == "settle"]
            print(f"[{v}] entries {len(g)}  avg entry {g.entry_px.mean():.3f}  hit 0.88 target: {tgt}  "
                  f"settled: {len(st)} (won {int(st.won.sum()) if len(st) else 0})  early exits: {len(early)} (${early.pnl.sum():.2f})  "
                  f"net pnl ${g.pnl.sum():.2f}  per trade ${g.pnl.mean():.2f}  fees ${g.fee.sum():.2f}")
        # signal accuracy regardless of entry
    sg = df[df.signal.notna() & df.settle_spot.notna()] if "settle_spot" in df else df.iloc[0:0]
    if len(sg):
        acc = (sg.signal == sg.settle_spot).mean()
        print(f"signal direction accuracy vs spot-at-close (all signals incl. unfilled): {acc:.1%} on {len(sg)}")
    if "best_ask_side" in df:
        bs = df[df.signal.notna()].best_ask_side.dropna()
        print("ask on signalled side at signal time: " + ", ".join(f"p{q}={bs.quantile(q/100):.2f}" for q in (10, 25, 50, 75, 90)))
    if args.out:
        df.to_csv(args.out, index=False)
        print("wrote", args.out)
    return df


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/recorded")
    ap.add_argument("--twap", choices=["doc", "pine"], default="pine")
    ap.add_argument("--anchor", choices=["spot", "strike"], default="spot")
    ap.add_argument("--buffer", type=float, default=20.0)
    ap.add_argument("--chop-band", type=float, default=10.0)
    ap.add_argument("--entry-from", type=float, default=600.0)
    ap.add_argument("--entry-to", type=float, default=825.0)
    ap.add_argument("--kill-secs", type=float, default=45.0)
    ap.add_argument("--cap", type=float, default=0.85)
    ap.add_argument("--ceasefire", type=float, default=0.93)
    ap.add_argument("--target", type=float, default=0.88)
    ap.add_argument("--size-usd", type=float, default=300.0)
    ap.add_argument("--depth-frac", type=float, default=1.0)
    ap.add_argument("--atr-guard", type=int, default=1)
    ap.add_argument("--atr-mult", type=float, default=2.5)
    ap.add_argument("--retry-until-cap", type=int, default=1,
                    help="keep evaluating later seconds of the window if the ask is above the cap")
    ap.add_argument("--max-spot-age", type=float, default=30.0)
    ap.add_argument("--stop", type=float, default=0.0, help="exit at the bid once it is this far below entry (0 = off)")
    ap.add_argument("--revert-exit", type=int, default=0, help="exit at the bid when spot comes back inside the chop band")
    ap.add_argument("--v4", type=int, default=1, help="apply the v4 'Reversal expected soon' veto")
    ap.add_argument("--out", default="")
    run(ap.parse_args())
