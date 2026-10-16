#!/usr/bin/env python
"""Paper-trade a registered strategy against live venue data.

Examples
--------
    python scripts/paper.py --venue kalshi --strategy mm_inventory --kalshi-series KXBTC15M --top 3 \
        --params configs/mm.yaml --duration 3300 --run-id gha-$(date +%s)
    python scripts/paper.py --venue polymarket --strategy mm_inventory --tokens <yes_token> --duration 600

Fills obey the simulator's liquidity rules; the ledger is written to
data/ledger/{run_id}.jsonl and data/ledger/{run_id}.summary.json.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def parse() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--venue", choices=["kalshi", "polymarket"], required=True)
    p.add_argument("--strategy", required=True, help="name in pb.strategies.base.REGISTRY")
    p.add_argument("--params", help="YAML file with strategy params ({strategy: {...}} or flat)")
    p.add_argument("--tickers", nargs="*", default=[])
    p.add_argument("--kalshi-series")
    p.add_argument("--tokens", nargs="*", default=[])
    p.add_argument("--top", type=int, default=3)
    p.add_argument("--duration", type=float, default=None, help="seconds")
    p.add_argument("--run-id", default=f"paper-{int(time.time())}")
    p.add_argument("--ledger", default="data/ledger")
    p.add_argument("--poll-secs", type=float, default=2.0)
    p.add_argument("--no-resume", action="store_true")
    p.add_argument("--demo", action="store_true")
    p.add_argument("--max-position", type=float, default=200.0)
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


async def main() -> int:
    a = parse()
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    from pb.live.paper import (PaperConfig, build_kalshi_runner, build_polymarket_runner, build_strategy,
                               load_params_yaml, select_kalshi_markets, select_polymarket_markets)
    from pb.sim.engine import SimConfig

    cfg = PaperConfig(run_id=a.run_id, duration=a.duration, ledger_root=a.ledger, poll_secs=a.poll_secs,
                      resume=not a.no_resume,
                      sim=SimConfig(max_position_per_market=a.max_position))
    params = load_params_yaml(a.params, a.strategy)
    if a.venue == "kalshi":
        from pb.venues.kalshi import KalshiClient

        async with KalshiClient.from_env(demo=a.demo) as c:
            markets = [await c.market(t) for t in a.tickers]
            if a.kalshi_series:
                markets += await select_kalshi_markets(c, a.kalshi_series, a.top)
        if not markets:
            print("no markets", file=sys.stderr)
            return 2
        strat = build_strategy(a.strategy, params, [m.market_id for m in markets])
        runner, client = await build_kalshi_runner(markets, [strat], cfg, demo=a.demo)
    else:
        from pb.venues.polymarket import PolymarketClient, to_market

        async with PolymarketClient() as c:
            if a.tokens:
                raw = await c.get_markets(limit=200, closed=False, active=True)
                by_tok = {m.market_id: m for m in map(to_market, raw)}
                markets = [by_tok[t] for t in a.tokens if t in by_tok]
            else:
                markets = await select_polymarket_markets(c, top=a.top)
        if not markets:
            print("no markets", file=sys.stderr)
            return 2
        strat = build_strategy(a.strategy, params, [m.market_id for m in markets])
        runner, client = await build_polymarket_runner(markets, [strat], cfg)
    print(f"paper run {a.run_id}: {a.strategy} on {[m.market_id for m in markets]}")
    try:
        summary = await runner.run()
    finally:
        await client.aclose()
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        pass
