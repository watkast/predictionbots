#!/usr/bin/env python3
"""
Dead Man's Ticket v2 — live Kalshi stream for markets in live games (read-only; never places orders).

Runs as a daemon thread inside the sports radar. The radar tells it which tickers matter (every Kalshi market
of a live/just-ended matched game) and which of them the decided-state engine has called certain. The stream:

  * keeps a live order book per ticker (orderbook_delta, yes-price form) and every trade (trade channel);
  * LATENCY MAP: for each decided market, how many seconds after the score changed until the certain side's
    book repriced (best ask >= 0.99, or no asks left, or the market closed)  -> sp.lat
  * RESTING-ORDER SIMULATION: every trade in which someone SOLD the certain side after the decision, at what
    price and size — a resting bid at level L would have been hit by every such trade priced <= L  -> sp.restfill
  * TAKER SIMULATION: every ask on the certain side below 0.99 that existed after the decision, with its size
    -> recorded in sp.lat as cheapest ask seen and size available

Needs KALSHI_KEY_ID + KALSHI_PRIVATE_KEY_PEM (read-only use of the WebSocket). Without them it stays off.
"""
from __future__ import annotations

import asyncio
import json
import threading
import time
from typing import Any, Optional

import mrp_recorder as R

W = R.W
LEVELS = (0.90, 0.95, 0.97, 0.98, 0.99)
WATCH_MAX_S = 20 * 60


class Stream:
    def __init__(self):
        self.on = R.KALSHI_ON
        self.lock = threading.Lock()
        self.want: set[str] = set()                 # tickers to subscribe (set by the radar)
        self.books: dict[str, Any] = {}
        self.watch: dict[str, dict] = {}            # ticker -> decided-market watch record
        self.status: dict[str, str] = {}
        self.stats = {"trades": 0, "deltas": 0, "reconnects": 0}
        self.thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------ radar-facing API (thread-safe)
    def set_tickers(self, tickers: set[str]):
        with self.lock:
            self.want = set(tickers) | set(self.watch)

    def decided(self, ticker: str, certain_yes: bool, t_score: float, meta: dict):
        """Register a market the engine has called certain (idempotent)."""
        with self.lock:
            if ticker in self.watch:
                return
            self.watch[ticker] = {"ticker": ticker, "certain_yes": certain_yes, "t_score": t_score, "t_dec": time.time(),
                                  "min_ask": None, "min_ask_q": 0.0, "ask_seen_s": 0, "fills": {str(l): [0.0, 0.0] for l in LEVELS},
                                  "sells": 0, **meta}
            self.want.add(ticker)

    def mark_status(self, ticker: str, status: str):
        with self.lock:
            self.status[ticker] = status

    def start(self):
        if not self.on or self.thread:
            return
        self.thread = threading.Thread(target=lambda: asyncio.run(self._main()), daemon=True, name="kalshi-stream")
        self.thread.start()
        R.log("kalshi stream: on")

    # ------------------------------------------------------------------ helpers
    def _certain_px(self, w: dict, yes_px: float) -> float:
        return yes_px if w["certain_yes"] else round(1 - yes_px, 4)

    def _book_state(self, w: dict) -> tuple[Optional[float], float]:
        """(cheapest ask on the certain side, its size) from the live book."""
        bk = self.books.get(w["ticker"])
        if not bk:
            return None, 0.0
        if w["certain_yes"]:                          # asks on YES = 'no' side in yes-price form
            if not bk.no:
                return None, 0.0
            p = min(bk.no)
            return p, bk.no[p]
        if not bk.yes:                                # certain NO: buying NO = selling into YES bids
            return None, 0.0
        p = max(bk.yes)
        return round(1 - p, 4), bk.yes[p]

    def _on_trade(self, m: dict):
        tk = m.get("market_ticker")
        w = self.watch.get(tk)
        if not w:
            return
        try:
            yp = float(m.get("yes_price_dollars") if m.get("yes_price_dollars") is not None else m.get("yes_price", 0) / 100)
            q = float(m.get("count_fp") if m.get("count_fp") is not None else m.get("count", 0))
        except (TypeError, ValueError):
            return
        side = m.get("taker_outcome_side") or m.get("taker_side")
        # someone SOLD the certain side: taker bought the opposite outcome
        sold_certain = (side == "no") if w["certain_yes"] else (side == "yes")
        if not sold_certain:
            return
        c = self._certain_px(w, yp)
        if c >= 0.995:
            return
        w["sells"] += 1
        for l in LEVELS:
            if c <= l:
                f = w["fills"][str(l)]
                f[0] += q
                f[1] += q * (1 - l)
        W.write("sp.restfill", {"ticker": tk, "sport": w.get("sport"), "series": w.get("series"), "px": c, "q": q,
                                "s_after_score": round(time.time() - w["t_score"], 1), "s_after_dec": round(time.time() - w["t_dec"], 1)})

    def _check_watches(self, now: float):
        done = []
        for tk, w in self.watch.items():
            ask, q = self._book_state(w)
            if ask is not None and ask < 0.99:
                if w["min_ask"] is None or ask < w["min_ask"]:
                    w["min_ask"], w["min_ask_q"] = ask, q
                w["ask_seen_s"] += 1
            repriced = (ask is None or ask >= 0.99) and tk in self.books
            closed = self.status.get(tk) in ("closed", "determined", "finalized", "settled")
            age = now - w["t_dec"]
            if repriced or closed or age > WATCH_MAX_S:
                rec = {k: v for k, v in w.items() if k != "fills"}
                rec.update(fills={l: {"q": round(v[0], 2), "profit": round(v[1], 2)} for l, v in w["fills"].items()},
                           how="repriced" if repriced else ("closed" if closed else "timeout"),
                           latency_s=round(now - w["t_score"], 1), after_dec_s=round(age, 1))
                W.write("sp.lat", rec)
                done.append(tk)
        for tk in done:
            self.watch.pop(tk, None)

    # ------------------------------------------------------------------ websocket loop
    async def _main(self):
        import websockets
        sign = R._kalshi_signer()
        path = "/trade-api/ws/v2"
        while not R.STOP.is_set():
            try:
                async with websockets.connect(R.KALSHI_WS_URL, additional_headers=sign("GET", path), ping_interval=20,
                                              max_size=2 ** 23) as ws:
                    cmd, sids, subscribed = 1, {}, set()
                    last_check = 0.0
                    while not R.STOP.is_set():
                        with self.lock:
                            want = set(self.want)
                        add, rem = want - subscribed, subscribed - want
                        if add:
                            if not sids:
                                for ch, extra in (("orderbook_delta", {"use_yes_price": True}), ("trade", {})):
                                    await ws.send(json.dumps({"id": cmd, "cmd": "subscribe", "params": dict(
                                        {"channels": [ch], "market_tickers": sorted(add)}, **extra)})); cmd += 1
                                sids["pending"] = 1
                            else:
                                for sid in [v for k, v in sids.items() if k != "pending"]:
                                    await ws.send(json.dumps({"id": cmd, "cmd": "update_subscription", "params": {
                                        "sid": sid, "market_tickers": sorted(add), "action": "add_markets"}})); cmd += 1
                            subscribed |= add
                        if rem and len(sids) > 1:
                            for sid in [v for k, v in sids.items() if k != "pending"]:
                                await ws.send(json.dumps({"id": cmd, "cmd": "update_subscription", "params": {
                                    "sid": sid, "market_tickers": sorted(rem), "action": "delete_markets"}})); cmd += 1
                            subscribed -= rem
                            for tk in rem:
                                self.books.pop(tk, None)
                        try:
                            raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        except asyncio.TimeoutError:
                            raw = None
                        if raw is not None:
                            try:
                                msg = json.loads(raw)
                            except ValueError:
                                msg = {}
                            typ, m = msg.get("type"), msg.get("msg") or {}
                            with self.lock:
                                if typ == "orderbook_snapshot":
                                    self.books.setdefault(m.get("market_ticker", "?"), R.KBook()).snapshot(m)
                                elif typ == "orderbook_delta":
                                    self.books.setdefault(m.get("market_ticker", "?"), R.KBook()).delta(m)
                                    self.stats["deltas"] += 1
                                elif typ == "trade":
                                    self.stats["trades"] += 1
                                    self._on_trade(m)
                                elif typ == "subscribed":
                                    sids.pop("pending", None)
                                    sids[m.get("channel")] = m.get("sid")
                                elif typ == "error":
                                    W.write("sp.stream.err", msg)
                        now = time.time()
                        if now - last_check >= 1.0:
                            last_check = now
                            with self.lock:
                                self._check_watches(now)
            except Exception as e:  # noqa
                self.stats["reconnects"] += 1
                W.err("sp.stream", e)
                await asyncio.sleep(5)
