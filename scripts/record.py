#!/usr/bin/env python
"""Record live order books + trades to parquet.

Examples
--------
    python scripts/record.py --venue kalshi --kalshi-series KXBTC15M --top 3 --max-seconds 3000
    python scripts/record.py --venue kalshi --tickers KXBTC15M-26OCT161200-T110000 --poll-secs 2
    python scripts/record.py --venue polymarket --tokens <yes_token_id> ... --max-seconds 3000
    python scripts/record.py --venue polymarket --top 5 --max-seconds 3000

Kalshi uses the WebSocket when KALSHI_KEY_ID / KALSHI_PRIVATE_KEY_PEM are set,
otherwise REST polling (public endpoints). Polymarket's market WS is public.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def parse() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--venue", choices=["kalshi", "polymarket"], required=True)
    p.add_argument("--tickers", nargs="*", default=[], help="Kalshi market tickers")
    p.add_argument("--kalshi-series", help="select top markets of this series by volume")
    p.add_argument("--tokens", nargs="*", default=[], help="Polymarket YES token ids")
    p.add_argument("--top", type=int, default=3)
    p.add_argument("--out", default="data/recorded")
    p.add_argument("--poll-secs", type=float, default=5.0)
    p.add_argument("--flush-secs", type=float, default=60.0)
    p.add_argument("--max-seconds", type=float, default=None)
    p.add_argument("--demo", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


async def main() -> int:
    a = parse()
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    from pb.data.recorder import build_kalshi_recorder, build_polymarket_recorder

    if a.venue == "kalshi":
        tickers = list(a.tickers)
        if a.kalshi_series:
            from pb.live.paper import select_kalshi_markets
            from pb.venues.kalshi import KalshiClient

            async with KalshiClient.from_env(demo=a.demo) as c:
                tickers += [m.market_id for m in await select_kalshi_markets(c, a.kalshi_series, a.top)]
        if not tickers:
            print("no tickers selected", file=sys.stderr)
            return 2
        rec, client = await build_kalshi_recorder(tickers, a.out, demo=a.demo, poll_secs=a.poll_secs,
                                                  flush_secs=a.flush_secs, max_seconds=a.max_seconds)
    else:
        from pb.core.types import Market, Venue
        from pb.venues.polymarket import PolymarketClient, to_market

        async with PolymarketClient() as c:
            if a.tokens:
                raw = await c.get_markets(limit=200, closed=False, active=True)
                by_tok = {m.market_id: m for m in map(to_market, raw)}
                markets = [by_tok.get(t) or Market(venue=Venue.POLYMARKET, market_id=t) for t in a.tokens]
            else:
                from pb.live.paper import select_polymarket_markets

                markets = await select_polymarket_markets(c, top=a.top)
        if not markets:
            print("no markets selected", file=sys.stderr)
            return 2
        rec, client = await build_polymarket_recorder(markets, a.out, poll_secs=a.poll_secs,
                                                      flush_secs=a.flush_secs, max_seconds=a.max_seconds)
    print(f"recording {sorted(rec.markets)} to {a.out}")
    try:
        stats = await rec.run()
    finally:
        await client.aclose()
    print(f"done: books={stats.books} trades={stats.trades} flushes={stats.flushes} files={len(stats.files)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        pass
