#!/usr/bin/env python
"""Paper-trade a registered strategy against live venue data (never real money).

Examples
--------
    python scripts/paper.py --venue kalshi --strategy mm_crypto_twap --kalshi-series KXBTC15M --top 2 \
        --params configs/mm_crypto_twap.yaml --signals coinbase,twap --duration 3300 --run-id gha-$(date +%s)
    python scripts/paper.py --venue kalshi --strategy mm_weather_ladder --kalshi-series KXHIGHNY \
        --signals openmeteo:40.78,-73.97 --duration 3300
    python scripts/paper.py --venue kalshi --strategy sharp_line_maker --kalshi-series KXNFLGAME --signals odds,espn
    python scripts/paper.py --venue kalshi --strategy favorite_maker --kalshi-scan nonsports --top 20
    python scripts/paper.py --venue polymarket --strategy mm_inventory --poly-crypto-15m --top 2 --signals coinbase

Fills obey the simulator's liquidity rules; the ledger is written to
data/ledger/{run_id}.jsonl and data/ledger/{run_id}.summary.json. Every
Signal the run sees is recorded to data/recorded/<venue>/.../signals-*.parquet
(`--no-record` to skip) so `scripts/backtest.py --data data/recorded` replays it.
A RiskManager gates every order (`--daily-loss-limit`, `--max-capital`,
`--max-capital-per-market`, kill file data/KILL).

The market selector is re-run every `--roll-secs` (default 60): newly listed
markets (the next KXBTC15M window, the next day's weather ladder) join the run,
settled ones leave it, so an hour-long run is continuous instead of one window.
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

KALSHI_SPORTS_PREFIXES = ("KXNFL", "KXNBA", "KXMLB", "KXNHL", "KXNCAA", "KXUFC", "KXMMA", "KXSOCCER", "KXEPL",
                          "KXUCL", "KXLALIGA", "KXSERIEA", "KXBUNDES", "KXTENNIS", "KXATP", "KXWTA", "KXPGA",
                          "KXGOLF", "KXF1", "KXNASCAR", "KXWNBA", "KXMLS", "KXCFB", "KXCBB")


def parse() -> argparse.Namespace:
    from pb.live.paper import SIGNAL_SPEC_HELP

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--venue", choices=["kalshi", "polymarket", "novig"], required=True)
    p.add_argument("--strategy", required=True, help="name in pb.strategies.base.REGISTRY")
    p.add_argument("--params", help="YAML file with strategy params ({strategy: {...}} or flat)")
    p.add_argument("--tickers", nargs="*", default=[])
    p.add_argument("--kalshi-series", nargs="*", default=[], help="one or more Kalshi series tickers")
    p.add_argument("--kalshi-scan", choices=["nonsports", "all"], help="scan open Kalshi markets by volume")
    p.add_argument("--tokens", nargs="*", default=[])
    p.add_argument("--poly-crypto-15m", action="store_true", help="Polymarket 5/15-min up-or-down markets")
    p.add_argument("--poly-events", action="store_true", help="Polymarket top events (all markets of each)")
    p.add_argument("--novig-league", nargs="*", default=[], help="Novig league(s), e.g. NFL NBA")
    p.add_argument("--novig-market-type", default="MONEY", help="Novig marketType filter (MONEY, SPREAD, TOTAL)")
    p.add_argument("--top", type=int, default=3)
    p.add_argument("--signals", default="", help=SIGNAL_SPEC_HELP)
    p.add_argument("--set", action="append", default=[], metavar="PARAM=VALUE",
                   help="override a strategy param (JSON value), e.g. --set size=1")
    p.add_argument("--duration", type=float, default=None, help="seconds")
    p.add_argument("--run-id", default=f"paper-{int(time.time())}")
    p.add_argument("--ledger", default="data/ledger")
    p.add_argument("--record-dir", default="data/recorded")
    p.add_argument("--no-record", action="store_true")
    p.add_argument("--poll-secs", type=float, default=2.0)
    p.add_argument("--roll-secs", type=float, default=60.0,
                   help="re-run the market selector this often to pick up new markets (0 = never)")
    p.add_argument("--no-resume", action="store_true")
    p.add_argument("--demo", action="store_true")
    p.add_argument("--max-position", type=float, default=200.0)
    p.add_argument("--daily-loss-limit", type=float, default=50.0)
    p.add_argument("--max-capital", type=float, default=2000.0)
    p.add_argument("--max-capital-per-market", type=float, default=500.0)
    p.add_argument("--max-orders-per-min", type=int, default=120)
    p.add_argument("--stale-secs", type=float, default=60.0)
    p.add_argument("--kill-file", default="data/KILL")
    p.add_argument("--no-risk", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


async def select_kalshi(a, c) -> list:
    from pb.live.paper import select_kalshi_markets
    from pb.venues import kalshi as K

    markets = [await c.market(t) for t in a.tickers]
    for s in a.kalshi_series:
        markets += await select_kalshi_markets(c, s, a.top)
    if a.kalshi_scan:
        raw = await c.iter_markets(status="open", limit=200, max_pages=10)
        now = time.time()
        ms = [K.to_market(m) for m in raw]
        ms = [m for m in ms if m.close_ts and m.close_ts - now > 600]
        if a.kalshi_scan == "nonsports":
            ms = [m for m in ms if not m.series.upper().startswith(KALSHI_SPORTS_PREFIXES)]
        ms.sort(key=lambda m: (m.meta.get("volume_24h", 0.0), m.meta.get("open_interest", 0.0)), reverse=True)
        markets += ms[: a.top]
    seen: set[str] = set()
    out = []
    for m in markets:
        if m.market_id not in seen:
            seen.add(m.market_id)
            out.append(m)
    return out


async def select_polymarket(a, c) -> list:
    from pb.live.paper import select_polymarket_markets
    from pb.venues.polymarket import to_market

    if a.tokens:
        raw = await c.get_markets(limit=200, closed=False, active=True)
        by_tok = {m.market_id: m for m in map(to_market, raw)}
        return [by_tok[t] for t in a.tokens if t in by_tok]
    if a.poly_crypto_15m:
        from pb.live.paper import select_polymarket_crypto_windows

        return await select_polymarket_crypto_windows(c, top=a.top)
    if a.poly_events:
        evs = await c.get_events(limit=a.top, closed=False, order="volume24hr", ascending=False)
        out = []
        for ev in evs:
            for raw in ev.get("markets", []) or []:
                m = to_market(raw)
                if m.market_id:
                    m.event_id = m.event_id or str(ev.get("id") or ev.get("slug") or "")
                    if ev.get("negRisk"):
                        m.meta["mutually_exclusive"] = True
                    out.append(m)
        return out
    return await select_polymarket_markets(c, top=a.top)


async def select_novig(a, c) -> list:
    """`--tickers` are Novig market ids; `--novig-league` picks the soonest-starting
    open pregame markets of that league (orders are voided at GOLIVE)."""
    markets = [await c.market(t) for t in a.tickers]
    for lg in a.novig_league or ([] if a.tickers else ["NFL"]):
        markets += await c.select_markets(league=lg, top=a.top, market_type=a.novig_market_type)
    seen: set[str] = set()
    out = []
    for m in markets:
        if m.market_id not in seen:
            seen.add(m.market_id)
            out.append(m)
    return out


async def main() -> int:
    a = parse()
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    from pb.live.paper import (PaperConfig, build_kalshi_runner, build_novig_runner, build_polymarket_runner,
                               build_signal_feeds, build_strategy, load_params_yaml)
    from pb.live.risk import RiskLimits
    from pb.sim.engine import SimConfig

    risk = None if a.no_risk else RiskLimits(daily_loss_limit=a.daily_loss_limit, max_capital_total=a.max_capital,
                                             max_capital_per_market=a.max_capital_per_market,
                                             max_orders_per_min=a.max_orders_per_min, stale_secs=a.stale_secs,
                                             kill_file=a.kill_file)
    cfg = PaperConfig(run_id=a.run_id, duration=a.duration, ledger_root=a.ledger, poll_secs=a.poll_secs,
                      resume=not a.no_resume, sim=SimConfig(max_position_per_market=a.max_position), risk=risk,
                      roll_secs=a.roll_secs)
    params = load_params_yaml(a.params, a.strategy)
    for kv in a.set:
        k, _, v = kv.partition("=")
        try:
            params[k.strip()] = json.loads(v)
        except ValueError:
            params[k.strip()] = v
    # one client for the whole run: the selector is re-run on it every --roll-secs
    if a.venue == "kalshi":
        from pb.venues.kalshi import KalshiClient

        client = KalshiClient.from_env(demo=a.demo)
        selector = lambda c: select_kalshi(a, c)  # noqa: E731
    elif a.venue == "novig":
        from pb.venues.novig import NovigClient

        client = NovigClient.from_env()
        selector = lambda c: select_novig(a, c)  # noqa: E731
    else:
        from pb.venues.polymarket import PolymarketClient

        client = PolymarketClient()
        selector = lambda c: select_polymarket(a, c)  # noqa: E731
    try:
        markets = await selector(client)
    except Exception:
        await client.aclose()
        raise
    if not markets:
        # exit 3 = nothing to trade right now (selector found no market); the matrix
        # runner reports it as skipped rather than failing the whole workflow
        print("no markets", file=sys.stderr)
        await client.aclose()
        return 3
    strat = build_strategy(a.strategy, params, [m.market_id for m in markets])
    feeds, notes = build_signal_feeds(a.signals, markets)
    for n in notes:
        logging.warning("signals: %s", n)
    recorder = None
    if not a.no_record:
        from pb.data.recorder import Recorder

        recorder = Recorder(a.venue, markets, a.record_dir, flush_secs=60.0)
    roll = selector if a.roll_secs > 0 else None
    if a.venue == "kalshi":
        runner, client = await build_kalshi_runner(markets, [strat], cfg, demo=a.demo, signals=feeds,
                                                   recorder=recorder, selector=roll, client=client)
    elif a.venue == "novig":
        runner, client = await build_novig_runner(markets, [strat], cfg, signals=feeds, recorder=recorder,
                                                  selector=roll, client=client)
    else:
        runner, client = await build_polymarket_runner(markets, [strat], cfg, signals=feeds, recorder=recorder,
                                                       selector=roll, client=client)
    print(f"paper run {a.run_id}: {a.strategy} on {[m.market_id for m in markets]} signals={a.signals or '-'} "
          f"roll_secs={a.roll_secs}")
    rec_task = asyncio.create_task(recorder.run()) if recorder is not None else None
    try:
        summary = await runner.run()
    finally:
        if recorder is not None:
            recorder.stop()
            if rec_task is not None:
                try:
                    await asyncio.wait_for(rec_task, timeout=30)
                except Exception as e:  # pragma: no cover
                    logging.warning("recorder shutdown: %s", e)
        await client.aclose()
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        pass
