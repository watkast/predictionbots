"""ORACLE-LAG v4 — the 15-minute BTC rule from `15_Min_BTC_Automation.docx` and the
"Polymarket US Alpha Engine v4" Pine script, as a taker strategy for the paper runner.

Rule (per 15-minute window, all times relative to the window open):
  anchor      spot index at the window open (Pine: the round's first 1-min open; Kalshi
              supplies `floor_strike`, used when `anchor="strike"`).
  twap        SMA of the last 15 one-minute closes, the forming minute = live spot
              (`twap="doc"`: locked minute closes + live spot for the unknown minutes).
  entry window  elapsed `entry_from`..`entry_to` seconds (doc: 10:00-13:45).
  BUY UP      spot > anchor and twap > anchor + `buffer` ($20)
  BUY DOWN    spot < anchor and twap < anchor - `buffer`
  chop band   no trade while |spot - anchor| < `chop_band` ($10)
  ATR guard   ATR(14) on 1-min bars > `atr_mult` x SMA(ATR, 100) -> abort the round
  v4 veto     "Reversal expected soon": twap slope over 3 min against the price's side
              of the twap -> no entry
  entry       one IOC per window, `size_usd` ($300) walked against the asks with a
              price ceiling `cap` (0.85); skipped when the ask >= `ceasefire` (0.93) or
              <= `kill_secs` (45) remain.
  exit        resting GTC sell at `target` (0.88) placed on fill; otherwise held to
              settlement. `LIVE_TRADING_ENABLED` is never read here: this repo has no
              live-money path, the paper runner is the only executor.

Evidence (reports/oracle_lag_backtest.md, recorded Polymarket + Kalshi books 2026-10-16..19):
the direction call is right 60-80% of the time but the book already prices it — the
signalled side asks >= 0.93 in ~70% of signals, and the entries that clear the 0.85 cap
are the marginal (|dev| 10-15 $) moves, which lost. Expected to lose; paper-traded to
confirm on more days.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

from pb.core.types import Action, Book, Market, Order, TIF
from pb.data.feeds import KalshiCryptoWindow, signal_price
from pb.sim.engine import Fill, Settlement, Signal, SimAPI, Strategy
from pb.strategies.base import register


@dataclass
class OracleLagParams:
    size_usd: float = 300.0
    buffer: float = 20.0
    chop_band: float = 10.0
    entry_from: float = 600.0
    entry_to: float = 825.0
    kill_secs: float = 45.0
    cap: float = 0.85
    ceasefire: float = 0.93
    target: float = 0.88
    twap: str = "pine"              # "pine" | "doc"
    anchor: str = "spot"            # "spot" | "strike"
    atr_guard: bool = True
    atr_mult: float = 2.5
    v4_veto: bool = True
    depth_frac: float = 1.0         # share of resting depth we allow ourselves to take
    signal_max_age: float = 30.0
    index_signal: str = "btc_index"
    max_contracts: float = 400.0


@dataclass
class _Round:
    window: KalshiCryptoWindow
    anchor: float | None = None
    entered: bool = False
    done: bool = False
    reason: str = ""


@register
class OracleLag(Strategy):
    name = "oracle_lag"

    def __init__(self, params: OracleLagParams | None = None, markets: list[str] | None = None):
        self.p = params or OracleLagParams()
        self.markets = set(markets or [])
        self.ticks: deque[tuple[float, float]] = deque(maxlen=200000)   # (ts, spot)
        self.bars: deque[list] = deque(maxlen=400)                      # [ts, o, h, l, c]
        self.rounds: dict[str, _Round] = {}
        self.decisions: list[dict] = []

    # -- lifecycle ----------------------------------------------------------------
    def on_market_added(self, api: SimAPI, market: Market) -> None:
        if self.markets:
            self.markets.add(market.market_id)
        self.rounds.pop(market.market_id, None)

    def on_market_removed(self, api: SimAPI, market_id: str) -> None:
        self.markets.discard(market_id)
        self.rounds.pop(market_id, None)

    def on_settlement(self, api: SimAPI, s: Settlement) -> None:
        self.rounds.pop(s.market_id, None)

    def on_fill(self, api: SimAPI, f: Fill) -> None:
        r = self.rounds.get(f.market_id)
        if r is None or not r.entered:
            return
        pos = api.position(f.market_id).contracts
        if pos == 0 or api.open_orders(f.market_id):
            return
        # resting take-profit on the whole position (YES leg: long -> sell at target;
        # short YES == long NO -> buy back at 1 - target)
        if pos > 0:
            api.place(Order(f.market_id, Action.SELL, self.p.target, pos, tif=TIF.GTC, post_only=True,
                            strategy=self.name))
        else:
            api.place(Order(f.market_id, Action.BUY, 1 - self.p.target, -pos, tif=TIF.GTC, post_only=True,
                            strategy=self.name))

    # -- spot tape -> 1-min bars --------------------------------------------------
    def on_signal(self, api: SimAPI, sig: Signal) -> None:
        if sig.name != self.p.index_signal:
            return
        px = signal_price(sig)
        if px is None or px <= 0:
            return
        self.ticks.append((sig.ts, px))
        m = int(sig.ts // 60) * 60
        if self.bars and self.bars[-1][0] == m:
            b = self.bars[-1]
            b[2] = max(b[2], px); b[3] = min(b[3], px); b[4] = px
        else:
            if self.bars and m - self.bars[-1][0] > 60:
                self.bars.clear()        # tape gap: ATR history is stale
            self.bars.append([m, px, px, px, px])
        for mid in list(self.rounds) or list(self.markets):
            b = api.book(mid)
            if b is not None:
                self._evaluate(api, b, px, sig.ts)

    def on_book(self, api: SimAPI, b: Book) -> None:
        if self.markets and b.market_id not in self.markets:
            return
        if not self.ticks:
            return
        ts, px = self.ticks[-1]
        if api.now - ts > self.p.signal_max_age:
            return
        self._evaluate(api, b, px, api.now)

    # -- helpers ------------------------------------------------------------------
    def _spot_at(self, t: float) -> float | None:
        """Last tick at or before t (None if none within signal_max_age)."""
        best = None
        for ts, px in reversed(self.ticks):
            if ts <= t:
                best = (ts, px)
                break
        if best is None or t - best[0] > self.p.signal_max_age:
            return None
        return best[1]

    def _minute_closes(self, open_ts: float, k0: int, k1: int) -> list[float] | None:
        out = []
        for k in range(k0, k1):
            c = self._spot_at(open_ts + 60 * (k + 1) - 0.001)
            if c is None:
                return None
            out.append(c)
        return out

    def _twap(self, open_ts: float, m: int, spot: float) -> float | None:
        if self.p.twap == "doc":
            closes = self._minute_closes(open_ts, 0, m)
            if closes is None:
                return None
            return (sum(closes) + spot * (15 - m)) / 15
        hist = self._minute_closes(open_ts, m - 14, m)
        if hist is None:
            return None
        return (sum(hist) + spot) / 15

    def _atr_danger(self) -> bool | None:
        if len(self.bars) < 115:
            return None
        trs = []
        prev_c = None
        for ts, o, h, l, c in self.bars:
            tr = h - l if prev_c is None else max(h - l, abs(h - prev_c), abs(l - prev_c))
            trs.append(tr)
            prev_c = c
        atr = [sum(trs[i - 13:i + 1]) / 14 for i in range(13, len(trs))]
        if len(atr) < 100:
            return None
        return atr[-1] > self.p.atr_mult * (sum(atr[-100:]) / 100)

    def _round(self, api: SimAPI, mid: str) -> _Round | None:
        r = self.rounds.get(mid)
        if r is None:
            m = api.market(mid)
            if m is None:
                return None
            w = KalshiCryptoWindow.from_market(m)
            if not w.ok:
                return None
            r = _Round(window=w)
            if self.p.anchor == "strike":
                fs = (m.meta or {}).get("floor_strike")
                if fs:
                    r.anchor = float(fs)
            self.rounds[mid] = r
        if r.anchor is None:
            r.anchor = self._spot_at(r.window.open_ts + 1)
        return r

    # -- the rule -----------------------------------------------------------------
    def _evaluate(self, api: SimAPI, b: Book, spot: float, now: float) -> None:
        p = self.p
        mid = b.market_id
        r = self._round(api, mid)
        if r is None or r.done or r.anchor is None:
            return
        w = r.window
        el = now - w.open_ts
        if el < p.entry_from or el > p.entry_to:
            return
        if w.close_ts - now <= p.kill_secs:
            return
        m = int(el // 60)
        twap = self._twap(w.open_ts, m, spot)
        if twap is None:
            return
        if p.atr_guard and self._atr_danger():
            r.done, r.reason = True, "atr_abort"
            api.log(f"[oracle_lag] {mid}: ABORT / SYSTEM LOCK (ATR)")
            return
        dev = spot - r.anchor
        if abs(dev) < p.chop_band:
            return
        if p.v4_veto and m >= 3:
            s3 = self._spot_at(w.open_ts + 60 * (m - 3) - 0.001)
            twap3 = self._twap(w.open_ts, m - 3, s3) if s3 is not None else None
            if twap3 is not None:
                slope = twap - twap3
                if (slope > 0 and spot < twap) or (slope < 0 and spot > twap):
                    return
        if dev > 0 and twap > r.anchor + p.buffer:
            side = Action.BUY
        elif dev < 0 and twap < r.anchor - p.buffer:
            side = Action.SELL
        else:
            return
        # YES-leg prices: BUY UP lifts asks; BUY DOWN == sell YES into bids at 1-p
        if side is Action.BUY:
            if not b.asks:
                return
            best = b.best_ask
            levels = [(l.price, l.size) for l in b.asks if l.price <= p.cap]
        else:
            if not b.bids:
                return
            best = 1 - b.best_bid
            levels = [(1 - l.price, l.size) for l in b.bids if 1 - l.price <= p.cap]
        if best >= p.ceasefire:
            r.done, r.reason = True, f"ceasefire_{best:.2f}"
            api.log(f"[oracle_lag] {mid}: signal {'UP' if side is Action.BUY else 'DOWN'} dev={dev:+.1f} "
                    f"but ask {best:.2f} >= ceasefire")
            self.decisions.append({"ts": now, "market": mid, "signal": side.name, "dev": dev, "ask": best,
                                   "action": "ceasefire"})
            return
        if best > p.cap or not levels:
            return  # keep watching; the ask may come down inside the window
        cash, n = p.size_usd, 0.0
        for px, sz in levels:
            take = min(sz * p.depth_frac, cash / px)
            n += take
            cash -= take * px
            if cash <= 0:
                break
        n = min(math.floor(n), p.max_contracts)
        if n < 1:
            return
        limit = p.cap if side is Action.BUY else 1 - p.cap
        api.place(Order(mid, side, limit, n, tif=TIF.IOC, strategy=self.name))
        r.entered, r.done = True, True
        self.decisions.append({"ts": now, "market": mid, "signal": side.name, "dev": dev, "twap": twap,
                               "anchor": r.anchor, "ask": best, "contracts": n, "action": "entry"})
        api.log(f"[oracle_lag] {mid}: BUY {'UP' if side is Action.BUY else 'DOWN'} NOW dev={dev:+.1f} "
                f"twap={twap:.2f} anchor={r.anchor:.2f} ask={best:.2f} n={n}")
