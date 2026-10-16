"""Live paper trading: the simulator Engine driven by real-time venue feeds.

The `Engine` from `pb.sim.engine` is reused unchanged so that paper fills
obey exactly the same liquidity rules as backtests (taker fills only against
resting size, maker fills only from prints / adverse crossings). The runner:

* pulls `Book`/`Trade` events from the venue WebSocket (or REST polling when
  the WS is unavailable, e.g. Kalshi without auth) and feeds them into the
  Engine in wall-clock order;
* advances engine timers on a heartbeat so latency/cancel callbacks fire
  even when the market is quiet;
* appends every fill to `data/ledger/{run_id}.jsonl` and writes
  `data/ledger/{run_id}.summary.json` every minute and at shutdown;
* resumes positions from a prior ledger with the same `run_id`;
* stops after `--duration` seconds or on SIGINT/SIGTERM.

Market selection helpers (`select_kalshi_markets`, `select_polymarket_markets`)
pick the top-N markets of a series/category by 24h volume.
"""
from __future__ import annotations

import asyncio
import json
import logging
import signal
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator, Awaitable, Callable, Iterable, Optional

from pb.core.fees import FeeSchedule
from pb.core.types import Action, Book, Fill, Market, Trade, Venue
from pb.sim.engine import Engine, Event, Settlement, Signal, SimConfig, Strategy

log = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# Engine driven one event at a time
# ----------------------------------------------------------------------------
class LiveEngine(Engine):
    """`Engine` with a public step API for real-time use."""

    def start(self) -> None:
        for s in self.strategies:
            s.on_start(self.api)

    def step(self, ev: Event) -> None:
        self._advance(ev.ts)
        self._dispatch(ev)

    def tick(self, now: float) -> None:
        """Fire due timers without an event (heartbeat)."""
        self._advance(now)

    def finish(self) -> None:
        self._advance(self.now + 1e-9)
        for s in self.strategies:
            s.on_end(self.api)


# ----------------------------------------------------------------------------
# Ledger
# ----------------------------------------------------------------------------
class Ledger:
    """Append-only JSONL of fills + periodic summary JSON."""

    def __init__(self, run_id: str, root: str | Path = "data/ledger"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.path = self.root / f"{run_id}.jsonl"
        self.summary_path = self.root / f"{run_id}.summary.json"

    def append(self, rec: dict) -> None:
        with self.path.open("a") as f:
            f.write(json.dumps(rec, default=str) + "\n")

    def append_fill(self, fill: Fill) -> None:
        d = {"type": "fill", **asdict(fill)}
        d["action"] = fill.action.value
        self.append(d)

    def load_fills(self) -> list[Fill]:
        out: list[Fill] = []
        if not self.path.exists():
            return out
        with self.path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("type") != "fill":
                    continue
                out.append(Fill(ts=float(d["ts"]), market_id=d["market_id"], order_id=str(d["order_id"]),
                                action=Action(d["action"]), price=float(d["price"]), size=float(d["size"]),
                                fee=float(d.get("fee", 0.0)), is_maker=bool(d.get("is_maker", False)),
                                strategy=d.get("strategy", "")))
        return out

    def write_summary(self, summary: dict) -> None:
        tmp = self.summary_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(summary, indent=2, default=str))
        tmp.replace(self.summary_path)


# ----------------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------------
@dataclass
class PaperConfig:
    run_id: str = "paper"
    duration: Optional[float] = None       # seconds; None = until stopped
    heartbeat: float = 0.25               # engine tick interval
    summary_secs: float = 60.0
    poll_secs: float = 2.0                # REST fallback cadence
    ledger_root: str = "data/ledger"
    sim: SimConfig = field(default_factory=SimConfig)
    resume: bool = True


class PaperRunner:
    """Parameters
    ----------
    markets:   core Markets to trade
    fee_for:   market_id -> FeeSchedule
    strategies: Strategy instances (constructed by `build_strategy`)
    feeds:     async iterators of Book/Trade (venue WS). May be empty.
    pollers:   optional {market_id: coroutine() -> Book} used when no feed
               produced an event for that market within `poll_secs`
    signals:   optional async iterator of `Signal`s (reference feeds)
    settlement_checker: optional coroutine(market_id) -> Market with result
    clock:     wall clock (injectable for tests)
    """

    def __init__(self, markets: Iterable[Market], fee_for: Callable[[str], FeeSchedule],
                 strategies: Iterable[Strategy], feeds: Iterable[AsyncIterator[Any]] = (),
                 pollers: Optional[dict[str, Callable[[], Awaitable[Book]]]] = None,
                 signals: Optional[AsyncIterator[Signal]] = None,
                 settlement_checker: Optional[Callable[[str], Awaitable[Optional[Market]]]] = None,
                 config: Optional[PaperConfig] = None, clock: Callable[[], float] = time.time):
        self.cfg = config or PaperConfig()
        self.clock = clock
        self.markets = list(markets)
        self.engine = LiveEngine(self.markets, fee_for, self.cfg.sim)
        for s in strategies:
            self.engine.add_strategy(s)
        self.feeds = list(feeds)
        self.pollers = pollers or {}
        self.signals = signals
        self.settlement_checker = settlement_checker
        self.ledger = Ledger(self.cfg.run_id, self.cfg.ledger_root)
        self._queue: asyncio.Queue = asyncio.Queue()
        self._stop = asyncio.Event()
        self._last_event: dict[str, float] = {}
        self._fills_logged = 0
        self.started_at = 0.0
        self._installed_signals = False

    # -- lifecycle ---------------------------------------------------------------
    def stop(self) -> None:
        self._stop.set()

    def _install_signal_handlers(self) -> None:
        try:
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, self.stop)
            self._installed_signals = True
        except (NotImplementedError, RuntimeError):  # pragma: no cover - windows / nested loops
            pass

    def _resume(self) -> None:
        if not self.cfg.resume:
            return
        fills = self.ledger.load_fills()
        for f in fills:
            self.engine.positions[f.market_id].apply(f.action, f.price, f.size, f.fee)
            self.engine.fills.append(f)
        self._fills_logged = len(fills)
        if fills:
            log.info("resumed %d prior fills from %s", len(fills), self.ledger.path)

    async def run(self) -> dict:
        self.started_at = self.clock()
        self._install_signal_handlers()
        self._resume()
        self.engine.now = self.clock()
        self.engine.start()
        self.ledger.append({"type": "start", "ts": self.started_at, "run_id": self.cfg.run_id,
                            "markets": [m.market_id for m in self.markets]})
        tasks = [asyncio.create_task(self._pump(f)) for f in self.feeds]
        if self.signals is not None:
            tasks.append(asyncio.create_task(self._pump(self.signals)))
        tasks += [asyncio.create_task(self._poll_loop()),
                  asyncio.create_task(self._summary_loop()),
                  asyncio.create_task(self._settlement_loop())]
        if self.cfg.duration is not None:
            tasks.append(asyncio.create_task(self._deadline()))
        try:
            await self._main_loop()
        finally:
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            self.engine.finish()
            self._log_new_fills()
            summary = self.summary()
            self.ledger.write_summary(summary)
            self.ledger.append({"type": "stop", "ts": self.clock(), "summary": summary})
        return summary

    async def _deadline(self) -> None:
        await asyncio.sleep(float(self.cfg.duration or 0))
        self.stop()

    async def _pump(self, feed: AsyncIterator[Any]) -> None:
        try:
            async for ev in feed:
                if isinstance(ev, (Book, Trade, Signal, Settlement)):
                    await self._queue.put(ev)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.warning("feed stopped: %s", e)

    async def _main_loop(self) -> None:
        while not self._stop.is_set():
            try:
                ev = await asyncio.wait_for(self._queue.get(), timeout=self.cfg.heartbeat)
            except asyncio.TimeoutError:
                self.engine.tick(self.clock())
                continue
            self.process(ev)

    def process(self, ev: Event) -> None:
        """Feed one event (synchronous; used directly by tests)."""
        now = self.clock()
        # Never let a feed timestamp run ahead of the wall clock or behind the engine.
        if ev.ts > now + 1.0 or ev.ts < self.engine.now - 300:
            ev.ts = now
        if ev.ts < self.engine.now:
            ev.ts = self.engine.now
        if isinstance(ev, (Book, Trade)):
            self._last_event[ev.market_id] = now
        self.engine.step(ev)
        self._log_new_fills()

    def _log_new_fills(self) -> None:
        new = self.engine.fills[self._fills_logged:]
        for f in new:
            self.ledger.append_fill(f)
        self._fills_logged = len(self.engine.fills)

    async def _poll_loop(self) -> None:
        if not self.pollers:
            return
        while True:
            await asyncio.sleep(self.cfg.poll_secs)
            now = self.clock()
            for mid, poll in list(self.pollers.items()):
                if now - self._last_event.get(mid, 0.0) < self.cfg.poll_secs:
                    continue
                try:
                    b = await poll()
                    if b is not None:
                        b.ts = self.clock()
                        await self._queue.put(b)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    log.warning("poll %s: %s", mid, e)

    async def _settlement_loop(self) -> None:
        if self.settlement_checker is None:
            return
        while True:
            await asyncio.sleep(60.0)
            for m in self.markets:
                if m.market_id in self.engine.settled:
                    continue
                if m.close_ts and self.clock() < m.close_ts:
                    continue
                try:
                    fresh = await self.settlement_checker(m.market_id)
                    if fresh is not None and fresh.result is not None:
                        await self._queue.put(Settlement(ts=self.clock(), market_id=m.market_id,
                                                         result=fresh.result))
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    log.warning("settlement check %s: %s", m.market_id, e)

    async def _summary_loop(self) -> None:
        while True:
            await asyncio.sleep(self.cfg.summary_secs)
            try:
                self.ledger.write_summary(self.summary())
            except Exception as e:  # pragma: no cover
                log.warning("summary write failed: %s", e)

    def summary(self) -> dict:
        from pb.sim.engine import Result

        s = Result(self.engine).summary()
        s.update({
            "run_id": self.cfg.run_id,
            "started_at": self.started_at,
            "updated_at": self.clock(),
            "uptime_secs": round(self.clock() - self.started_at, 1),
            "open_orders": len(self.engine.orders),
            "positions": {m: {"contracts": p.contracts, "avg_price": round(p.avg_price, 4),
                              "realized": round(p.realized, 4), "fees": round(p.fees, 4)}
                          for m, p in self.engine.positions.items() if p.contracts or p.realized},
            "markets": [m.market_id for m in self.markets],
            "last_event_age": {m: round(self.clock() - t, 1) for m, t in self._last_event.items()},
        })
        return s


# ----------------------------------------------------------------------------
# Strategy construction
# ----------------------------------------------------------------------------
def build_strategy(name: str, params: Optional[dict] = None, markets: Optional[list[str]] = None) -> Strategy:
    """Instantiate `REGISTRY[name]`. Params are passed to the class's params
    dataclass when it declares one (`<Class>.__init__(params=...)`), else as kwargs."""
    import dataclasses
    import inspect

    from pb.strategies import base as B  # noqa: F401 - ensures modules register
    import pb.strategies  # noqa: F401

    _import_all_strategies()
    if name not in B.REGISTRY:
        raise KeyError(f"unknown strategy {name!r}; known: {sorted(B.REGISTRY)}")
    cls = B.REGISTRY[name]
    params = params or {}
    sig = inspect.signature(cls.__init__)
    kwargs: dict[str, Any] = {}
    if "params" in sig.parameters:
        ann = sig.parameters["params"].annotation
        ptype = _resolve_params_type(cls, ann)
        if ptype is not None and dataclasses.is_dataclass(ptype):
            fields = {f.name for f in dataclasses.fields(ptype)}
            unknown = set(params) - fields
            if unknown:
                raise KeyError(f"unknown params for {name}: {sorted(unknown)}")
            kwargs["params"] = ptype(**params)
        else:
            kwargs["params"] = params
    else:
        kwargs.update(params)
    if "markets" in sig.parameters and markets is not None:
        kwargs["markets"] = markets
    return cls(**kwargs)


def _resolve_params_type(cls: type, ann: Any) -> Optional[type]:
    import sys
    import typing

    mod = sys.modules.get(cls.__module__)
    if isinstance(ann, str):
        name = ann.split("|")[0].strip()
        return getattr(mod, name, None)
    args = typing.get_args(ann)
    if args:
        for a in args:
            if isinstance(a, type) and a is not type(None):
                return a
    return ann if isinstance(ann, type) else None


def _import_all_strategies() -> None:
    import importlib
    import pkgutil

    import pb.strategies as pkg

    for m in pkgutil.iter_modules(pkg.__path__):
        try:
            importlib.import_module(f"pb.strategies.{m.name}")
        except Exception as e:  # pragma: no cover
            log.warning("could not import strategy module %s: %s", m.name, e)


def load_params_yaml(path: Optional[str | Path], strategy: Optional[str] = None) -> dict:
    """Load `{strategy: {param: value}}` or a flat mapping from YAML."""
    if not path:
        return {}
    import yaml

    data = yaml.safe_load(Path(path).read_text()) or {}
    if strategy and isinstance(data.get(strategy), dict):
        return dict(data[strategy])
    if "params" in data and isinstance(data["params"], dict):
        return dict(data["params"])
    return dict(data)


# ----------------------------------------------------------------------------
# Market selection
# ----------------------------------------------------------------------------
async def select_kalshi_markets(client: Any, series: str, top: int = 3, status: str = "open",
                                min_secs_to_close: float = 120.0) -> list[Market]:
    """Top-N open markets of a Kalshi series by 24h volume (then volume),
    skipping those closing within `min_secs_to_close`."""
    from pb.venues import kalshi as K

    raw = await client.iter_markets(series_ticker=series, status=status, limit=200, max_pages=5)
    now = time.time()
    ms = [K.to_market(m) for m in raw]
    ms = [m for m in ms if not m.close_ts or m.close_ts - now > min_secs_to_close]
    ms.sort(key=lambda m: (m.meta.get("volume_24h", 0.0), m.meta.get("volume", 0.0),
                           m.meta.get("open_interest", 0.0)), reverse=True)
    return ms[:top]


async def select_polymarket_markets(client: Any, top: int = 3, tag_id: Optional[int] = None,
                                    category: Optional[str] = None, min_liquidity: float = 0.0) -> list[Market]:
    from pb.venues import polymarket as P

    raw = await client.get_markets(limit=200, closed=False, active=True, tag_id=tag_id,
                                   order="volume24hr", ascending=False)
    ms = [P.to_market(m) for m in raw]
    if category:
        ms = [m for m in ms if m.series == category.lower()]
    ms = [m for m in ms if m.meta.get("liquidity", 0.0) >= min_liquidity and m.market_id]
    ms.sort(key=lambda m: m.meta.get("volume_24h", 0.0), reverse=True)
    return ms[:top]


# ----------------------------------------------------------------------------
# Venue wiring
# ----------------------------------------------------------------------------
async def build_kalshi_runner(markets: list[Market], strategies: list[Strategy], config: PaperConfig,
                              demo: bool = False) -> tuple[PaperRunner, Any]:
    from pb.venues import kalshi as K

    client = K.KalshiClient.from_env(demo=demo)
    fees: dict[str, FeeSchedule] = {}
    for m in markets:
        fees[m.market_id] = await client.fee_schedule(m.series)
    feeds = []
    if client.auth is not None:
        ws = K.KalshiWS([m.market_id for m in markets], auth=client.auth,
                        url=K.DEMO_WS if demo else K.PROD_WS)
        feeds.append(ws.events())
    pollers = {m.market_id: (lambda mid=m.market_id: client.book(mid)) for m in markets}

    async def check(mid: str) -> Optional[Market]:
        return await client.market(mid)

    runner = PaperRunner(markets, lambda mid: fees.get(mid, K.kalshi_schedule(mid.split("-")[0])),
                         strategies, feeds=feeds, pollers=pollers, settlement_checker=check, config=config)
    return runner, client


async def build_polymarket_runner(markets: list[Market], strategies: list[Strategy],
                                  config: PaperConfig) -> tuple[PaperRunner, Any]:
    from pb.venues import polymarket as P

    client = P.PolymarketClient()
    fees = {m.market_id: P.fee_schedule_for(m) for m in markets}
    ws = P.PolymarketWS([m.market_id for m in markets])
    pollers = {m.market_id: (lambda mid=m.market_id: client.book(mid)) for m in markets}
    runner = PaperRunner(markets, lambda mid: fees.get(mid, P.polymarket_schedule("other")), strategies,
                         feeds=[ws.events()], pollers=pollers, config=config)
    return runner, client


__all__ = ["LiveEngine", "Ledger", "PaperConfig", "PaperRunner", "build_strategy", "load_params_yaml",
           "select_kalshi_markets", "select_polymarket_markets", "build_kalshi_runner",
           "build_polymarket_runner"]
