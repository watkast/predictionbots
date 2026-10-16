#!/usr/bin/env python
"""Network smoke test: hit PUBLIC venue endpoints and verify our parsers.

Run only where internet is available (GitHub Actions `ci.yml`); never in unit
tests. Exit code 1 on any parse failure. With Kalshi auth env present it also
checks the signed /portfolio/balance call and a short WS subscription.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pb.core.types import Book, Market, Trade  # noqa: E402


def check(cond: bool, msg: str, fails: list[str]) -> None:
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


async def kalshi(fails: list[str]) -> None:
    from pb.venues import kalshi as K

    async with K.KalshiClient.from_env() as c:
        page = await c.get_markets(status="open", limit=5)
        ms = [K.to_market(m) for m in page.get("markets", [])]
        check(len(ms) > 0 and all(isinstance(m, Market) and m.market_id for m in ms), "kalshi /markets parse", fails)
        if not ms:
            return
        t = ms[0]
        check(t.close_ts > time.time() - 86400 * 365, f"kalshi close_ts sane ({t.market_id})", fails)
        s = await c.get_series(t.series)
        sched = K.fee_schedule_for(s, t.series)
        check(sched.taker_rate > 0, f"kalshi series fee schedule {t.series}: {sched}", fails)
        ob = await c.get_orderbook(t.market_id, depth=10)
        b = K.to_book(ob, t.market_id, time.time())
        check(isinstance(b, Book), "kalshi orderbook parse", fails)
        if b.bids and b.asks:
            check(b.best_bid < b.best_ask, f"kalshi book not crossed {b.best_bid} < {b.best_ask}", fails)
        tr = await c.get_trades(ticker=t.market_id, limit=20)
        trades = K.to_trades(tr, t.market_id)
        check(all(isinstance(x, Trade) and 0 <= x.price <= 1 for x in trades), f"kalshi trades parse ({len(trades)})", fails)
        now = int(time.time())
        cs = await c.get_candlesticks(t.series, t.market_id, now - 3600, now, 1)
        cands = [K.candle_to_summary(x) for x in cs.get("candlesticks", [])]
        check(all(c_["ts"] > 0 for c_ in cands), f"kalshi candlesticks parse ({len(cands)})", fails)
        try:
            cut = await c.get_historical_cutoff()
            print("     historical cutoff:", json.dumps(cut)[:200])
        except Exception as e:
            print("     historical cutoff unavailable:", e)
        if c.auth is not None:
            bal = await c.get_balance()
            check("balance" in bal or "balance_dollars" in bal, f"kalshi auth balance {bal}", fails)
            ws = K.KalshiWS([t.market_id], auth=c.auth)
            got = []
            async def run():
                async for ev in ws.events():
                    got.append(ev)
                    if len(got) >= 3:
                        await ws.stop()
                        break
            try:
                await asyncio.wait_for(run(), timeout=30)
            except asyncio.TimeoutError:
                pass
            check(any(isinstance(e, Book) for e in got), f"kalshi WS snapshot ({len(got)} events)", fails)


async def polymarket(fails: list[str]) -> None:
    from pb.venues import polymarket as P

    async with P.PolymarketClient() as c:
        raw = await c.get_markets(limit=5, closed=False, active=True, order="volume24hr", ascending=False)
        ms = [P.to_market(m) for m in raw]
        check(len(ms) > 0 and all(m.market_id for m in ms), "gamma /markets parse", fails)
        if not ms:
            return
        m = ms[0]
        check(bool(m.meta.get("no_token")), f"clobTokenIds parsed ({m.title[:40]})", fails)
        ob = await c.get_book(m.market_id)
        b = P.to_book(ob, m.market_id)
        check(isinstance(b, Book) and (not (b.bids and b.asks) or b.best_bid < b.best_ask), "clob /book parse", fails)
        mid = await c.get_midpoint(m.market_id)
        check(mid is None or 0 <= mid <= 1, f"clob midpoint {mid}", fails)
        hist = await c.get_prices_history(m.market_id, interval="1d", fidelity=60)
        check(isinstance(hist, list), f"clob prices-history ({len(hist)})", fails)
        cond = m.meta.get("condition_id")
        if cond:
            tr = await c.get_trades(cond, limit=20)
            trades = [P.to_trade(r, m.market_id) for r in tr.get("trades", [])]
            check(all(0 <= t.price <= 1 for t in trades), f"data-api trades parse ({len(trades)})", fails)
        ws = P.PolymarketWS([m.market_id])
        got = []
        async def run():
            async for ev in ws.events():
                got.append(ev)
                if len(got) >= 2:
                    await ws.stop()
                    break
        try:
            await asyncio.wait_for(run(), timeout=30)
        except asyncio.TimeoutError:
            pass
        check(any(isinstance(e, Book) for e in got), f"polymarket WS book ({len(got)} events)", fails)


async def main() -> int:
    fails: list[str] = []
    for name, fn in (("kalshi", kalshi), ("polymarket", polymarket)):
        if os.environ.get("SMOKE_SKIP", "").find(name) >= 0:
            continue
        try:
            await fn(fails)
        except Exception as e:
            check(False, f"{name}: unexpected error {type(e).__name__}: {e}", fails)
    print("\n" + ("ALL OK" if not fails else f"{len(fails)} FAILURES"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
