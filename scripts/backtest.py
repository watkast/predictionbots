#!/usr/bin/env python
"""Backtest a registered strategy over recorded parquet / venue history /
synthetic data, optionally sweeping a parameter grid and walk-forward.

Examples
--------
    # recorded L2 parquet, params from YAML
    python scripts/backtest.py --strategy mm_inventory --data data/recorded --params configs/mm_inventory.yaml

    # grid sweep (YAML `grid:` section or --grid 'size=5,10,20;gamma=0.01,0.03'), 4 threads
    python scripts/backtest.py --strategy mm_crypto_twap --data data/recorded --params configs/mm_crypto_twap.yaml \
        --grid 'min_half_spread=0.01,0.02,0.03' --workers 4

    # walk-forward: pick the best grid point on fold k, evaluate on fold k+1
    python scripts/backtest.py --strategy favorite_maker --data data/recorded --walk-forward 4 --grid 'edge=0.01,0.02'

    # Kalshi candle+tape history (low fidelity -> maker_requires_through forced on)
    python scripts/backtest.py --strategy mm_inventory --kalshi-series KXBTC15M --start 2026-10-01 --end 2026-10-08

    # CI smoke on synthetic data
    python scripts/backtest.py --strategy mm_inventory --synthetic --report-name smoke

Params YAML: `{strategy: {param: value}}` or flat; an optional top-level
`grid: {param: [v1, v2]}` and `sim: {order_latency: 0.3, ...}` are honoured.
Reports go to reports/<name>.md and .json.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def parse_grid(s: str | None) -> dict:
    out: dict = {}
    if not s:
        return out
    for part in s.split(";"):
        if not part.strip():
            continue
        k, v = part.split("=", 1)
        vals = []
        for x in v.split(","):
            x = x.strip()
            try:
                vals.append(json.loads(x))
            except ValueError:
                vals.append(x)
        out[k.strip()] = vals
    return out


def _ts(s: str | None) -> float | None:
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--params", help="YAML params file")
    ap.add_argument("--data", help="recorded parquet dir/glob (pb.data.loaders.load_recorded)")
    ap.add_argument("--markets", nargs="*", help="restrict to these market ids")
    ap.add_argument("--kalshi-series", help="low-fidelity Kalshi history for this series")
    ap.add_argument("--poly-token", help="low-fidelity Polymarket history for this YES token")
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--signals", help="parquet/CSV of signals (ts,name,market_id,value) to merge")
    ap.add_argument("--grid", help="'a=1,2;b=x,y' parameter grid")
    ap.add_argument("--walk-forward", type=int, default=0, help="number of folds")
    ap.add_argument("--metric", default="net_pnl")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--processes", action="store_true")
    ap.add_argument("--out", default="reports")
    ap.add_argument("--report-name")
    ap.add_argument("--title", default=None)
    ap.add_argument("--latency", type=float, default=None)
    a = ap.parse_args()

    from pb.live.paper import load_params_yaml
    from pb.sim.backtest import (BacktestSpec, DataSpec, grid_sweep, load_data, run_backtest,
                                 walk_forward, write_report)

    params = load_params_yaml(a.params, a.strategy)
    raw = {}
    if a.params:
        import yaml

        raw = yaml.safe_load(Path(a.params).read_text()) or {}
    grid = dict(raw.get("grid") or {})
    grid.update(parse_grid(a.grid))
    sim = dict(raw.get("sim") or {})
    if a.latency is not None:
        sim["order_latency"] = sim["cancel_latency"] = a.latency

    signals = None
    if a.signals:
        signals = _load_signals(a.signals)

    if a.synthetic:
        data = DataSpec(kind="synthetic", synthetic_kwargs={"seed": a.seed}, signals=signals)
    elif a.data:
        data = DataSpec(kind="recorded", path=a.data, markets=a.markets, signals=signals)
    elif a.kalshi_series or a.poly_token:
        data = DataSpec(kind="history", history=lambda: asyncio.run(_history(a)), signals=signals)
    else:
        ap.error("one of --data / --kalshi-series / --poly-token / --synthetic is required")
    spec = BacktestSpec(strategy=a.strategy, params=params, data=data, sim=sim, label="base")
    loaded = load_data(data)
    t0 = time.time()
    if a.walk_forward:
        results = walk_forward(spec, a.walk_forward, grid or None, a.metric, a.workers, loaded)
    elif grid:
        results = grid_sweep(spec, grid, a.workers, loaded, use_processes=a.processes)
    else:
        results = [run_backtest(spec, loaded)]
    md, js = write_report(results, a.out, a.report_name, a.title or f"{a.strategy} backtest")
    print(md.read_text())
    print(f"\nwrote {md} and {js} in {time.time() - t0:.1f}s")
    return 0 if all(not r.error for r in results) else 1


def _load_signals(path: str):
    from pb.data.feeds import signals_from_rows

    p = Path(path)
    rows: list[dict] = []
    if p.suffix == ".parquet":
        import pyarrow.parquet as pq

        rows = pq.read_table(p).to_pylist()
    else:
        import csv

        with p.open() as f:
            rows = list(csv.DictReader(f))
    out = []
    by_name: dict[str, list[dict]] = {}
    for r in rows:
        by_name.setdefault(str(r["name"]), []).append(r)
    for name, rs in by_name.items():
        for r in rs:
            v = r.get("value")
            try:
                r["value"] = float(v)
            except (TypeError, ValueError):
                try:
                    r["value"] = json.loads(v)
                except (TypeError, ValueError):
                    pass
            if r.get("market_id") in ("", "None"):
                r["market_id"] = None
        out += signals_from_rows(rs, name)
    out.sort(key=lambda s: s.ts)
    return out


async def _history(a):
    from pb.data import loaders

    start, end = _ts(a.start), _ts(a.end)
    if start is None or end is None:
        raise SystemExit("--start and --end are required with --kalshi-series/--poly-token")
    if a.kalshi_series:
        from pb.venues.kalshi import KalshiClient

        async with KalshiClient.from_env() as c:
            return await loaders.kalshi_history(a.kalshi_series, start, end, c)
    from pb.venues.polymarket import PolymarketClient

    async with PolymarketClient() as c:
        return await loaders.polymarket_history(a.poly_token, start, end, c)


if __name__ == "__main__":
    sys.exit(main())
