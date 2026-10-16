"""Backtest harness: run any registered strategy over recorded or historical
event streams, sweep parameter grids, walk-forward split, and write
markdown + JSON reports with "reality flags".

Entry points
------------
* `run_backtest(spec)`            -> BacktestResult (one strategy, one param set)
* `grid_sweep(spec, grid, ...)`   -> list[BacktestResult] (itertools.product, parallel)
* `walk_forward(spec, n_splits)`  -> list[BacktestResult] (time-ordered folds)
* `write_report(results, out_dir)` -> (md_path, json_path)

Data sources (`DataSpec.kind`):
* "recorded":  `pb.data.loaders.load_recorded(path_glob, markets)` (full L2)
* "history":   a `HistoryEvents` object (or a callable returning one); when
               `low_fidelity` is True we force `maker_requires_through=True`
* "synthetic": `pb.sim.synthetic.synthetic_events` (CI only)
* "events":    in-memory `(markets, events)` tuple

Signals: recorded runs carry their own `signals-*.parquet` (replayed by
default, `DataSpec.recorded_signals=False` to drop); extra `Signal` events
(e.g. from pb.data.feeds helpers or `scripts/backtest.py --signals`) are
merged into the stream by timestamp via `DataSpec.signals`.

Fees: `DataSpec.fee_for` (market_id -> FeeSchedule); default infers from the
market's venue/series (`pb.core.fees.kalshi_schedule` on the series prefix,
`polymarket_schedule` on meta["category"]).
"""
from __future__ import annotations

import concurrent.futures as cf
import dataclasses
import heapq
import itertools
import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Optional

from pb.core.fees import FeeSchedule, kalshi_schedule, polymarket_schedule
from pb.core.types import Book, Market, Trade, Venue
from pb.sim.engine import Engine, Event, Settlement, Signal, SimConfig


# ----------------------------------------------------------------------------
# Specs
# ----------------------------------------------------------------------------
@dataclass
class DataSpec:
    kind: str = "synthetic"
    path: str | list[str] | None = None            # recorded parquet glob(s)
    markets: Optional[list[str]] = None
    history: Any = None                             # HistoryEvents or callable -> HistoryEvents
    events: Any = None                              # (markets, events) for kind="events"
    signals: Optional[list[Signal]] = None
    synthetic_kwargs: dict = field(default_factory=dict)
    fee_for: Optional[Callable[[str], FeeSchedule]] = None
    low_fidelity: Optional[bool] = None             # override
    recorded_signals: bool = True                   # replay signals-*.parquet from the recorder


@dataclass
class BacktestSpec:
    strategy: str
    params: dict = field(default_factory=dict)
    data: DataSpec = field(default_factory=DataSpec)
    sim: dict = field(default_factory=dict)         # SimConfig overrides
    label: str = ""
    time_range: Optional[tuple[float, float]] = None  # restrict events to [t0, t1)


@dataclass
class BacktestResult:
    strategy: str
    params: dict
    label: str
    summary: dict
    reality: dict
    fidelity: str
    n_events: int
    t_start: float
    t_end: float
    elapsed: float
    per_market: dict
    error: str | None = None

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
def default_fee_for(markets: Iterable[Market]) -> Callable[[str], FeeSchedule]:
    table: dict[str, FeeSchedule] = {}
    for m in markets:
        if m.venue is Venue.KALSHI:
            table[m.market_id] = kalshi_schedule(m.series or m.market_id.split("-")[0],
                                                 fee_type=(m.meta or {}).get("fee_type"))
        else:
            table[m.market_id] = polymarket_schedule(str((m.meta or {}).get("category") or m.series or "other"))
    return lambda mid: table.get(mid, kalshi_schedule(mid.split("-")[0]))


def merge_streams(*streams: Iterable[Event]) -> Iterator[Event]:
    """Merge ts-sorted event iterables (stable on ties by stream order)."""
    heap = []
    its = [iter(s) for s in streams]
    for i, it in enumerate(its):
        for ev in it:
            heapq.heappush(heap, (ev.ts, i, 0, ev))
            break
    counters = [1] * len(its)
    while heap:
        ts, i, _, ev = heapq.heappop(heap)
        yield ev
        for nxt in its[i]:
            heapq.heappush(heap, (nxt.ts, i, counters[i], nxt))
            counters[i] += 1
            break


def load_data(d: DataSpec) -> tuple[list[Market], list[Event], bool]:
    low = False
    if d.kind == "recorded":
        from pb.data.loaders import load_recorded

        markets, events = load_recorded(d.path, d.markets, signals=d.recorded_signals)
        events = list(events)
    elif d.kind == "history":
        h = d.history() if callable(d.history) else d.history
        markets = list(h.markets)
        events = list(h.events)
        low = bool(getattr(h, "low_fidelity", False))
    elif d.kind == "events":
        markets, events = d.events
        markets, events = list(markets), list(events)
    elif d.kind == "synthetic":
        from pb.sim.synthetic import synthetic_events

        markets, events = synthetic_events(**d.synthetic_kwargs)
    else:
        raise ValueError(f"unknown data kind {d.kind!r}")
    if d.signals:
        events = list(merge_streams(events, sorted(d.signals, key=lambda s: s.ts)))
    if d.low_fidelity is not None:
        low = d.low_fidelity
    return markets, events, low


# ----------------------------------------------------------------------------
# Running
# ----------------------------------------------------------------------------
def _slice(events: list[Event], rng: Optional[tuple[float, float]]) -> list[Event]:
    if rng is None:
        return events
    t0, t1 = rng
    out = [e for e in events if t0 <= e.ts < t1]
    # keep settlements that fall after the slice for markets touched inside it
    touched = {e.market_id for e in out if getattr(e, "market_id", None)}
    tail = [e for e in events if isinstance(e, Settlement) and e.ts >= t1 and e.market_id in touched]
    return out + tail


def reality_flags(engine: Engine) -> dict:
    fills = engine.fills
    ctx = engine.fill_context
    n = len(fills)
    cross = sum(1 for c in ctx if c.get("assumed_cross"))
    maker = sum(1 for f in fills if f.is_maker)
    ratio_max = 0.0
    for f, c in zip(fills, ctx):
        d = c.get("touch_depth", 0.0)
        if d > 0:
            ratio_max = max(ratio_max, f.size / d)
        elif f.size > 0:
            ratio_max = max(ratio_max, math.inf)
    pm = {m: p.realized - p.fees for m, p in engine.positions.items()}
    pos_total = sum(v for v in pm.values() if v > 0)
    top3 = sum(sorted((v for v in pm.values() if v > 0), reverse=True)[:3])
    return {
        "cross_assumed_fill_frac": round(cross / n, 4) if n else 0.0,
        "cross_assumed_fills": cross,
        "maker_frac": round(maker / n, 4) if n else 0.0,
        "max_fill_to_touch_depth": (round(ratio_max, 3) if math.isfinite(ratio_max) else "inf"),
        "top3_market_pnl_frac": round(top3 / pos_total, 4) if pos_total > 0 else 0.0,
        "pnl_per_contract": round(engine.equity() / max(1e-9, sum(f.size for f in fills)), 5) if n else 0.0,
    }


def run_backtest(spec: BacktestSpec, data: Optional[tuple[list[Market], list[Event], bool]] = None
                 ) -> BacktestResult:
    from pb.live.paper import build_strategy

    t0 = time.time()
    try:
        markets, events, low = data if data is not None else load_data(spec.data)
        events = _slice(events, spec.time_range)
        simkw = dict(spec.sim)
        if low and "maker_requires_through" not in simkw:
            simkw["maker_requires_through"] = True
        cfg = SimConfig(**simkw)
        fee_for = spec.data.fee_for or default_fee_for(markets)
        # fresh Market objects per run (engine mutates result/settle_ts; books are mutated by takes)
        mk = [dataclasses.replace(m, meta=dict(m.meta)) for m in markets]
        eng = Engine(mk, fee_for, cfg)
        strat = build_strategy(spec.strategy, dict(spec.params), [m.market_id for m in mk] or None)
        eng.add_strategy(strat)
        res = eng.run(_clone_events(events))
        summ = res.summary()
        summ["net_pnl_on_max_capital"] = round(summ["net_pnl"] / summ["max_capital_at_risk"], 4) \
            if summ["max_capital_at_risk"] > 0 else 0.0
        summ["maker_pct"] = round(100.0 * summ["maker_fills"] / summ["fills"], 1) if summ["fills"] else 0.0
        ts = [e.ts for e in events]
        return BacktestResult(strategy=spec.strategy, params=dict(spec.params), label=spec.label,
                              summary=summ, reality=reality_flags(eng),
                              fidelity="low (candle+tape, maker_requires_through)" if cfg.maker_requires_through else "L2",
                              n_events=len(events), t_start=min(ts) if ts else 0.0, t_end=max(ts) if ts else 0.0,
                              elapsed=round(time.time() - t0, 3),
                              per_market={m: round(p.realized - p.fees, 4) for m, p in eng.positions.items()})
    except Exception as e:  # keep sweeps alive
        return BacktestResult(strategy=spec.strategy, params=dict(spec.params), label=spec.label, summary={},
                              reality={}, fidelity="", n_events=0, t_start=0.0, t_end=0.0,
                              elapsed=round(time.time() - t0, 3), per_market={}, error=f"{type(e).__name__}: {e}")


def _clone_events(events: list[Event]) -> Iterator[Event]:
    """Books are mutated by taker fills in the engine; hand each run its own copies."""
    for e in events:
        if isinstance(e, Book):
            yield Book(ts=e.ts, market_id=e.market_id,
                       bids=[dataclasses.replace(l) for l in e.bids], asks=[dataclasses.replace(l) for l in e.asks])
        else:
            yield e


# ----------------------------------------------------------------------------
# Sweeps & walk-forward
# ----------------------------------------------------------------------------
def expand_grid(grid: dict[str, list]) -> list[dict]:
    keys = list(grid)
    return [dict(zip(keys, vals)) for vals in itertools.product(*[grid[k] for k in keys])] if keys else [{}]


def _run_one(args: tuple) -> BacktestResult:
    spec, data = args
    return run_backtest(spec, data)


def grid_sweep(spec: BacktestSpec, grid: dict[str, list], workers: int = 1,
               data: Optional[tuple[list[Market], list[Event], bool]] = None,
               use_processes: bool = False) -> list[BacktestResult]:
    data = data if data is not None else load_data(spec.data)
    specs = []
    for i, g in enumerate(expand_grid(grid)):
        p = dict(spec.params)
        p.update(g)
        specs.append(dataclasses.replace(spec, params=p, label=spec.label or f"grid{i}"))
    if workers <= 1 or len(specs) <= 1:
        return [run_backtest(s, data) for s in specs]
    pool = cf.ProcessPoolExecutor if use_processes else cf.ThreadPoolExecutor
    with pool(max_workers=workers) as ex:
        return list(ex.map(_run_one, [(s, data) for s in specs]))


def walk_forward(spec: BacktestSpec, n_splits: int = 3, grid: Optional[dict[str, list]] = None,
                 metric: str = "net_pnl", workers: int = 1,
                 data: Optional[tuple[list[Market], list[Event], bool]] = None) -> list[BacktestResult]:
    """Split the event range into `n_splits` contiguous folds. With a `grid`,
    pick the best param set on fold k (in-sample) and evaluate it on fold k+1
    (out-of-sample); the OOS results are returned with label "oos{k}". Without
    a grid, each fold is simply run with `spec.params` (label "fold{k}")."""
    data = data if data is not None else load_data(spec.data)
    markets, events, low = data
    ts = sorted({e.ts for e in events if not isinstance(e, Settlement)})
    if not ts or n_splits < 1:
        return []
    edges = [ts[int(i * len(ts) / n_splits)] for i in range(n_splits)] + [ts[-1] + 1.0]
    folds = [(edges[i], edges[i + 1]) for i in range(n_splits)]
    out: list[BacktestResult] = []
    if not grid:
        for k, rng in enumerate(folds):
            out.append(run_backtest(dataclasses.replace(spec, time_range=rng, label=f"fold{k}"), data))
        return out
    for k in range(len(folds) - 1):
        ins = grid_sweep(dataclasses.replace(spec, time_range=folds[k], label=f"is{k}"), grid, workers, data)
        ok = [r for r in ins if not r.error]
        if not ok:
            continue
        best = max(ok, key=lambda r: r.summary.get(metric, -math.inf))
        oos = run_backtest(dataclasses.replace(spec, params=best.params, time_range=folds[k + 1],
                                               label=f"oos{k + 1}"), data)
        oos.reality["selected_in_sample"] = {metric: best.summary.get(metric), "params": best.params}
        out.append(oos)
    return out


# ----------------------------------------------------------------------------
# Reports
# ----------------------------------------------------------------------------
_COLS = [("strategy", "strategy"), ("label", "label"), ("net_pnl", "net pnl"), ("fees", "fees"),
         ("fills", "fills"), ("maker_pct", "maker %"), ("max_drawdown", "max DD"),
         ("max_capital_at_risk", "max capital"), ("net_pnl_on_max_capital", "ret/maxcap"),
         ("markets_traded", "markets"), ("market_win_rate", "win rate")]


def _fmt(v: Any) -> str:
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


def results_markdown(results: list[BacktestResult], title: str = "Backtest report") -> str:
    lines = [f"# {title}", "", f"Generated {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}", ""]
    lines.append("| " + " | ".join(h for _, h in _COLS) + " | params |")
    lines.append("|" + "---|" * (len(_COLS) + 1))
    for r in results:
        if r.error:
            lines.append(f"| {r.strategy} | {r.label} | ERROR: {r.error} |" + " |" * (len(_COLS) - 2) + f" {json.dumps(r.params)} |")
            continue
        row = []
        for key, _ in _COLS:
            if key == "strategy":
                row.append(r.strategy)
            elif key == "label":
                row.append(r.label)
            else:
                row.append(_fmt(r.summary.get(key, "")))
        row.append("`" + json.dumps(r.params, default=str) + "`")
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## Reality flags", "",
              "| strategy | label | fidelity | events | cross-assumed fills | max fill/touch depth | top-3 market pnl share | pnl/contract |",
              "|---|---|---|---|---|---|---|---|"]
    for r in results:
        if r.error:
            continue
        f = r.reality
        lines.append(f"| {r.strategy} | {r.label} | {r.fidelity} | {r.n_events} | "
                     f"{f.get('cross_assumed_fill_frac', 0):.1%} ({f.get('cross_assumed_fills', 0)}) | "
                     f"{f.get('max_fill_to_touch_depth', 0)} | {f.get('top3_market_pnl_frac', 0):.0%} | "
                     f"{f.get('pnl_per_contract', 0)} |")
    lines += ["", "Interpretation: a high cross-assumed-fill fraction means most maker fills were "
              "inferred from the book moving through our price without a print (adverse assumption, "
              "but also the least certain). A max fill/touch-depth ratio > 1 means a single fill "
              "exceeded the resting size at the touch at fill time. A top-3 share near 100% means "
              "the result is concentrated and probably not robust.", ""]
    return "\n".join(lines)


def write_report(results: list[BacktestResult], out_dir: str | Path = "reports", name: str | None = None,
                 title: str = "Backtest report") -> tuple[Path, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    name = name or f"backtest-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"
    md = out / f"{name}.md"
    js = out / f"{name}.json"
    md.write_text(results_markdown(results, title))
    js.write_text(json.dumps([r.to_dict() for r in results], indent=2, default=str))
    return md, js
