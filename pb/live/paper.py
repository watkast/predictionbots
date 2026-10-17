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
* merges any number of reference `Signal` feeds (`signals=[...]`, see
  `pb.data.feeds.merge_signals`) into the same event queue;
* gates every strategy order through `pb.live.risk.RiskManager` (daily loss
  limit, capital caps, order rate, kill file `data/KILL`, stale-data guard)
  and reports `risk` in the summary;
* optionally records every Signal it saw to `signals-*.parquet` via a
  `pb.data.recorder.Recorder` (`recorder=`) so backtests replay the feed;
* **rolls markets**: every `roll_secs` (default 60) it re-runs the
  `market_selector` coroutine, wires and adds every market it has not seen
  (next KXBTC15M window, tomorrow's weather ladder...), keeps a closed market
  only until its settlement has been applied and then drops it (cancelling
  nothing that could still fill, because nothing can fill after close). The
  recorder, the risk manager and every strategy (`on_market_added` /
  `on_market_removed`) follow the same list;
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
from pb.live.risk import RiskLimits, RiskManager
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
    risk: Optional[RiskLimits] = field(default_factory=RiskLimits)   # None disables the RiskManager
    roll_secs: float = 60.0               # re-run the market selector this often (0 = never)
    # a closed market that never settles (venue lag) is dropped this long after close
    # once it is flat with no resting orders; a market with a position is kept
    drop_unsettled_after: float = 3600.0


class PaperRunner:
    """Parameters
    ----------
    markets:   core Markets to trade
    fee_for:   market_id -> FeeSchedule
    strategies: Strategy instances (constructed by `build_strategy`)
    feeds:     async iterators of Book/Trade (venue WS). May be empty.
    pollers:   optional {market_id: coroutine() -> Book} used when no feed
               produced an event for that market within `poll_secs`
    trade_pollers: optional {market_id: coroutine(since_ts: float) -> list[Trade]}
               polled every `poll_secs` (before the book) when there is no WS
               tape, so maker fills come from REAL prints and the
               book-crossed-us assumption becomes the exception. Prints are
               de-duplicated on (ts, price, size, side) and replayed in order.
    signals:   one async iterator of `Signal`s, or a list of them (fanned in)
    settlement_checker: optional coroutine(market_id) -> Market with result
    recorder:  optional `pb.data.recorder.Recorder`; every Signal (and Book/
               Trade) processed is handed to `recorder.on_event` so the run's
               exact feed lands in parquet. The caller runs/stops the recorder.
    market_selector: optional coroutine() -> list[Market]; re-run every
               `config.roll_secs` to discover newly listed markets (rolling)
    market_wiring: optional coroutine(market) -> None called once per NEW
               market before it is added: venue builders use it to register
               fee schedules, REST pollers and WS subscriptions
    clock:     wall clock (injectable for tests)
    """

    def __init__(self, markets: Iterable[Market], fee_for: Callable[[str], FeeSchedule],
                 strategies: Iterable[Strategy], feeds: Iterable[AsyncIterator[Any]] = (),
                 pollers: Optional[dict[str, Callable[[], Awaitable[Book]]]] = None,
                 signals: Optional[AsyncIterator[Signal] | Iterable[AsyncIterator[Signal]]] = None,
                 settlement_checker: Optional[Callable[[str], Awaitable[Optional[Market]]]] = None,
                 config: Optional[PaperConfig] = None, clock: Callable[[], float] = time.time,
                 recorder: Any = None,
                 trade_pollers: Optional[dict[str, Callable[[float], Awaitable[list[Trade]]]]] = None,
                 market_selector: Optional[Callable[[], Awaitable[list[Market]]]] = None,
                 market_wiring: Optional[Callable[[Market], Awaitable[None]]] = None):
        self.cfg = config or PaperConfig()
        self.clock = clock
        self.markets = list(markets)
        self.market_selector = market_selector
        self.market_wiring = market_wiring
        self.markets_seen: list[str] = [m.market_id for m in self.markets]   # every market this run traded
        self.rolls = 0
        self.last_roll: dict[str, Any] = {}
        self.engine = LiveEngine(self.markets, fee_for, self.cfg.sim)
        self.risk: Optional[RiskManager] = None
        if self.cfg.risk is not None:
            self.risk = RiskManager(self.engine, self.cfg.risk, clock=clock, name=self.cfg.run_id).install()
        for s in strategies:
            self.engine.add_strategy(s)
        self.feeds = list(feeds)
        self.pollers = pollers or {}
        self.trade_pollers = trade_pollers or {}
        self._trade_since: dict[str, float] = {}
        self._trade_seen: dict[str, set[tuple]] = {}
        if signals is None:
            self.signal_feeds: list[AsyncIterator[Signal]] = []
        elif hasattr(signals, "__aiter__"):
            self.signal_feeds = [signals]  # type: ignore[list-item]
        else:
            self.signal_feeds = list(signals)  # type: ignore[arg-type]
        self.recorder = recorder
        self.settlement_checker = settlement_checker
        self.ledger = Ledger(self.cfg.run_id, self.cfg.ledger_root)
        self._venue_hint = self.markets[0].venue.value if self.markets else ""
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
        tasks += [asyncio.create_task(self._pump(f)) for f in self.signal_feeds]
        tasks += [asyncio.create_task(self._poll_loop()),
                  asyncio.create_task(self._summary_loop()),
                  asyncio.create_task(self._settlement_loop()),
                  asyncio.create_task(self._roll_loop())]
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
                if self.risk is not None:
                    self.risk.check()
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
        if self.risk is not None:
            self.risk.on_event(ev)
        if self.recorder is not None:
            try:
                self.recorder.on_event(ev)
            except Exception as e:  # pragma: no cover
                log.warning("recorder: %s", e)
        self.engine.step(ev)
        self._log_new_fills()
        if isinstance(ev, Settlement):
            # settlement applied (position flat, strategies notified): the market is done
            self.remove_market(ev.market_id, reason=f"settled {ev.result:g}")

    # -- market rolling ------------------------------------------------------------
    def add_market(self, m: Market) -> bool:
        """Register a market discovered mid-run. Idempotent. Synchronous: wiring
        (fees / pollers / WS) must already have happened (`market_wiring`)."""
        if not self.engine.add_market(m):
            return False
        self.markets.append(m)
        if m.market_id not in self.markets_seen:
            self.markets_seen.append(m.market_id)
        if self.recorder is not None:
            try:
                self.recorder.on_market(m)
            except Exception as e:  # pragma: no cover
                log.warning("recorder: %s", e)
        self.ledger.append({"type": "market_added", "ts": self.clock(), "market_id": m.market_id,
                            "close_ts": m.close_ts, "title": m.title})
        log.info("market added: %s (closes %s)", m.market_id, _fmt_ts(m.close_ts))
        return True

    def remove_market(self, market_id: str, reason: str = "") -> bool:
        if not self.engine.remove_market(market_id):
            return False
        self.markets = [m for m in self.markets if m.market_id != market_id]
        self.pollers.pop(market_id, None)
        self.trade_pollers.pop(market_id, None)
        self._trade_since.pop(market_id, None)
        self._trade_seen.pop(market_id, None)
        self._last_event.pop(market_id, None)
        if self.risk is not None:
            self.risk.forget_market(market_id)
        self.ledger.append({"type": "market_removed", "ts": self.clock(), "market_id": market_id, "reason": reason})
        log.info("market removed: %s (%s)", market_id, reason)
        return True

    async def roll_markets(self) -> dict:
        """One selector pass: add unseen markets (after wiring), drop stale closed
        ones. Returns a small report (also kept as `last_roll`)."""
        rep: dict[str, Any] = {"ts": self.clock(), "selected": 0, "added": [], "dropped": [], "error": ""}
        if self.market_selector is not None:
            try:
                fresh = list(await self.market_selector())
            except asyncio.CancelledError:
                raise
            except Exception as e:
                rep["error"] = f"{type(e).__name__}: {e}"
                log.warning("market roll: selector failed: %s", e)
                fresh = []
            rep["selected"] = len(fresh)
            for m in fresh:
                if m.market_id in self.engine.markets or m.market_id in self.engine.settled:
                    continue
                if self.market_wiring is not None:
                    try:
                        await self.market_wiring(m)
                    except asyncio.CancelledError:
                        raise
                    except Exception as e:
                        log.warning("market roll: wiring %s failed: %s", m.market_id, e)
                        continue
                if self.add_market(m):
                    rep["added"].append(m.market_id)
        # closed markets that never settled: drop once flat and quiet
        now = self.clock()
        for m in list(self.markets):
            if not m.close_ts or now - m.close_ts < self.cfg.drop_unsettled_after:
                continue
            pos = self.engine.positions.get(m.market_id)
            if pos is not None and pos.contracts != 0:
                continue
            if any(o.market_id == m.market_id for o in self.engine.orders.values()):
                continue
            if self.remove_market(m.market_id, reason="closed, no settlement"):
                rep["dropped"].append(m.market_id)
        self.rolls += 1
        self.last_roll = rep
        if rep["added"] or rep["dropped"] or rep["error"]:
            log.info("market roll #%d: selected=%d added=%s dropped=%s %s", self.rolls, rep["selected"],
                     rep["added"], rep["dropped"], rep["error"])
        return rep

    async def _roll_loop(self) -> None:
        if self.market_selector is None or self.cfg.roll_secs <= 0:
            return
        while True:
            await asyncio.sleep(self.cfg.roll_secs)
            try:
                await self.roll_markets()
            except asyncio.CancelledError:
                raise
            except Exception as e:  # pragma: no cover
                log.warning("market roll failed: %s", e)

    def _log_new_fills(self) -> None:
        new = self.engine.fills[self._fills_logged:]
        for f in new:
            self.ledger.append_fill(f)
        self._fills_logged = len(self.engine.fills)

    async def _poll_loop(self) -> None:
        if not self.pollers and not self.trade_pollers:
            return
        while True:
            await asyncio.sleep(self.cfg.poll_secs)
            now = self.clock()
            # prints first: a print that hit us is credited at its size (queue model)
            # before the book snapshot can turn the same move into an assumed cross
            for mid, tpoll in list(self.trade_pollers.items()):
                if mid in self.engine.settled:
                    continue
                try:
                    for tr in self._new_trades(mid, await tpoll(self._trade_since.get(mid, self.started_at))):
                        await self._queue.put(tr)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    log.warning("trade poll %s: %s", mid, e)
            for mid, poll in list(self.pollers.items()):
                if mid in self.engine.settled:
                    continue
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

    def _new_trades(self, mid: str, trades: Iterable[Trade]) -> list[Trade]:
        """Drop prints already seen (REST tape pages overlap at `min_ts`
        second granularity) and advance the per-market watermark."""
        seen = self._trade_seen.setdefault(mid, set())
        since = self._trade_since.get(mid, self.started_at)
        out: list[Trade] = []
        for tr in sorted(trades, key=lambda t: t.ts):
            if tr.market_id != mid or tr.size <= 0 or tr.ts < since - 1.0:
                continue
            key = (round(tr.ts, 3), round(tr.price, 6), round(tr.size, 6), tr.taker_action.value)
            if key in seen:
                continue
            seen.add(key)
            out.append(tr)
        if out:
            newest = max(t.ts for t in out)
            if newest > since:
                self._trade_since[mid] = newest
                # keep only keys that can still collide with the next page
                self._trade_seen[mid] = {k for k in seen if k[0] >= newest - 2.0}
        return out

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
        from pb.sim.backtest import reality_flags
        from pb.sim.engine import Result

        s = Result(self.engine).summary()
        s["net_pnl_on_max_capital"] = round(s["net_pnl"] / s["max_capital_at_risk"], 4) \
            if s["max_capital_at_risk"] > 0 else 0.0
        s["maker_pct"] = round(100.0 * s["maker_fills"] / s["fills"], 1) if s["fills"] else 0.0
        s.update({
            "reality": reality_flags(self.engine),
            "run_id": self.cfg.run_id,
            "started_at": self.started_at,
            "updated_at": self.clock(),
            "uptime_secs": round(self.clock() - self.started_at, 1),
            "open_orders": len(self.engine.orders),
            "positions": {m: {"contracts": p.contracts, "avg_price": round(p.avg_price, 4),
                              "realized": round(p.realized, 4), "fees": round(p.fees, 4)}
                          for m, p in self.engine.positions.items() if p.contracts or p.realized},
            "markets": list(self.markets_seen),
            "active_markets": [m.market_id for m in self.markets],
            "rolls": self.rolls,
            "last_roll": self.last_roll,
            "last_event_age": {m: round(self.clock() - t, 1) for m, t in self._last_event.items()},
            "risk": self.risk.status() if self.risk is not None else None,
            "strategies": [getattr(st, "name", type(st).__name__) for st in self.engine.strategies],
            "venue": self._venue,
        })
        return s

    @property
    def _venue(self) -> str:
        if self.markets:
            return self.markets[0].venue.value
        for m in self.engine.markets.values():
            return m.venue.value
        return getattr(self, "_venue_hint", "")


def _fmt_ts(ts: float | None) -> str:
    if not ts:
        return "?"
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(float(ts)))


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


CRYPTO_WINDOW_ASSETS = ("btc", "eth")
CRYPTO_WINDOW_MINUTES = (15, 5)


def crypto_window_slugs(now: float, assets: Iterable[str] = CRYPTO_WINDOW_ASSETS,
                        minutes: Iterable[int] = CRYPTO_WINDOW_MINUTES, lookahead: int = 2,
                        lookback: int = 0) -> list[str]:
    """Deterministic Polymarket slugs for the current and next `lookahead`
    windows: `btc-updown-15m-<epoch of the window open, aligned to 15 min>`."""
    out: list[str] = []
    for a in assets:
        for n in minutes:
            secs = int(n) * 60
            base = int(now // secs) * secs
            for k in range(-lookback, lookahead + 1):
                out.append(f"{a.lower()}-updown-{int(n)}m-{base + k * secs}")
    return out


async def select_polymarket_crypto_windows(client: Any, top: int = 2, assets: Iterable[str] = CRYPTO_WINDOW_ASSETS,
                                           minutes: Iterable[int] = CRYPTO_WINDOW_MINUTES, lookahead: int = 2,
                                           min_secs_to_close: float = 60.0, now: Optional[float] = None,
                                           fallback_scan: bool = True) -> list[Market]:
    """Polymarket 5/15-minute up-or-down markets, soonest-closing first.

    1. Probe `/events?slug=` then `/markets?slug=` for every deterministic slug
       (`crypto_window_slugs`), since these markets are not in the top-N by
       24h volume (each window lives minutes).
    2. If nothing came back, scan Gamma by `startDate` desc and by `volume24hr`
       and keep what `crypto_window_from_slug` recognises.
    Every step logs what it tried and found so a failing run explains itself."""
    from pb.venues import polymarket as P

    now = time.time() if now is None else now
    found: dict[str, Market] = {}
    slugs = crypto_window_slugs(now, assets, minutes, lookahead)
    hits: list[str] = []
    errors = 0
    for slug in slugs:
        raws: list[dict] = []
        for fn in (client.get_events_by_slug, client.get_markets_by_slug):
            try:
                res = await fn(slug)
            except Exception as e:
                errors += 1
                log.debug("poly crypto selector: %s(%s) failed: %s", getattr(fn, "__name__", fn), slug, e)
                continue
            for item in res:
                if "markets" in item and isinstance(item.get("markets"), list):
                    for raw in item["markets"]:
                        if isinstance(raw, dict):
                            raws.append(dict(raw, events=[{k: v for k, v in item.items() if k != "markets"}]))
                else:
                    raws.append(item)
            if raws:
                break
        for raw in raws:
            m = P.to_market(raw)
            if m.market_id and m.meta.get("window_close_ts"):
                if m.market_id not in found:
                    found[m.market_id] = m
                    hits.append(slug)
    log.info("poly crypto selector: probed %d slugs (%s..), %d hits%s: %s", len(slugs),
             slugs[0] if slugs else "-", len(hits), f", {errors} errors" if errors else "", hits or "-")
    if not found and fallback_scan:
        for kw in ({"order": "startDate", "ascending": False}, {"order": "volume24hr", "ascending": False}):
            try:
                raw = await client.get_markets(limit=300, closed=False, active=True, **kw)
            except Exception as e:
                log.warning("poly crypto selector: scan %s failed: %s", kw, e)
                continue
            n = 0
            for r in raw:
                m = P.to_market(r)
                if m.market_id and m.meta.get("window_close_ts") and m.market_id not in found:
                    found[m.market_id] = m
                    n += 1
            log.info("poly crypto selector: scan order=%s -> %d markets, %d crypto windows", kw["order"], len(raw), n)
            if found:
                break
    ms = [m for m in found.values() if m.meta["window_close_ts"] > now + min_secs_to_close]
    ms.sort(key=lambda m: (m.meta["window_close_ts"], -m.meta.get("volume_24h", 0.0)))
    log.info("poly crypto selector: %d tradable windows, taking %s", len(ms),
             [m.meta.get("slug") or m.market_id for m in ms[:top]] or "-")
    return ms[:top]


# ----------------------------------------------------------------------------
# Venue wiring
# ----------------------------------------------------------------------------
async def build_kalshi_runner(markets: list[Market], strategies: list[Strategy], config: PaperConfig,
                              demo: bool = False, signals: Optional[list[AsyncIterator[Signal]]] = None,
                              recorder: Any = None,
                              selector: Optional[Callable[[Any], Awaitable[list[Market]]]] = None,
                              client: Any = None) -> tuple[PaperRunner, Any]:
    """`selector(client) -> list[Market]` (optional) is re-run every
    `config.roll_secs` so new windows / ladders join the run."""
    from pb.venues import kalshi as K

    client = client or K.KalshiClient.from_env(demo=demo)
    fees: dict[str, FeeSchedule] = {}
    pollers: dict[str, Callable[[], Awaitable[Book]]] = {}
    trade_pollers: dict[str, Callable[[float], Awaitable[list[Trade]]]] = {}
    ws = None
    if client.auth is not None:
        ws = K.KalshiWS([m.market_id for m in markets], auth=client.auth,
                        url=K.DEMO_WS if demo else K.PROD_WS)

    async def wire(m: Market, enrich: bool = True) -> None:
        try:
            fees[m.market_id] = await client.fee_schedule(m.series)
        except Exception as e:  # pragma: no cover - network
            log.warning("fee schedule %s: %s", m.series, e)
        if enrich:
            try:
                await client.enrich([m])
            except Exception as e:  # pragma: no cover - network
                log.warning("market enrichment failed: %s", e)
        pollers[m.market_id] = (lambda mid=m.market_id: client.book(mid))
        if client.auth is None:
            # no WS tape without auth: poll the public trade tape so maker fills come from prints
            trade_pollers[m.market_id] = (lambda since, mid=m.market_id: client.trades_since(mid, since))
        elif ws is not None:
            await ws.subscribe_more([m.market_id])

    for m in markets:
        await wire(m, enrich=False)
    try:
        await client.enrich(markets)
    except Exception as e:  # pragma: no cover - network
        log.warning("market enrichment failed: %s", e)

    async def check(mid: str) -> Optional[Market]:
        return await client.market(mid)

    runner = PaperRunner(markets, lambda mid: fees.get(mid, K.kalshi_schedule(mid.split("-")[0])),
                         strategies, feeds=[ws.events()] if ws is not None else [], pollers=pollers,
                         settlement_checker=check, config=config, signals=signals, recorder=recorder,
                         trade_pollers=trade_pollers if client.auth is None else None,
                         market_selector=(lambda: selector(client)) if selector is not None else None,
                         market_wiring=wire)
    return runner, client


async def build_polymarket_runner(markets: list[Market], strategies: list[Strategy],
                                  config: PaperConfig, signals: Optional[list[AsyncIterator[Signal]]] = None,
                                  recorder: Any = None,
                                  selector: Optional[Callable[[Any], Awaitable[list[Market]]]] = None,
                                  client: Any = None) -> tuple[PaperRunner, Any]:
    from pb.venues import polymarket as P

    client = client or P.PolymarketClient()
    fees = {m.market_id: P.fee_schedule_for(m) for m in markets}
    ws = P.PolymarketWS([m.market_id for m in markets])
    pollers = {m.market_id: (lambda mid=m.market_id: client.book(mid)) for m in markets}

    async def settled(mid: str) -> Optional[Market]:
        m = runner.engine.markets.get(mid)
        gid = (m.meta or {}).get("gamma_id") if m is not None else None
        if not gid:
            return None
        fresh = P.to_market(await client.get_market(str(gid)))
        return fresh if fresh.result is not None else None

    async def wire(m: Market) -> None:
        fees[m.market_id] = P.fee_schedule_for(m)
        pollers[m.market_id] = (lambda mid=m.market_id: client.book(mid))
        await ws.subscribe_more([m.market_id])

    runner = PaperRunner(markets, lambda mid: fees.get(mid, P.polymarket_schedule("other")), strategies,
                         feeds=[ws.events()], pollers=pollers, config=config, signals=signals, recorder=recorder,
                         settlement_checker=settled,
                         market_selector=(lambda: selector(client)) if selector is not None else None,
                         market_wiring=wire)
    return runner, client


async def build_novig_runner(markets: list[Market], strategies: list[Strategy], config: PaperConfig,
                             signals: Optional[list[AsyncIterator[Signal]]] = None, recorder: Any = None,
                             selector: Optional[Callable[[Any], Awaitable[list[Market]]]] = None,
                             client: Any = None) -> tuple[PaperRunner, Any]:
    """Novig (paper env by default, `NOVIG_HOST` overrides). With a trading
    key the signed WS streams books + tape; without one the public REST
    catalog is polled (books) and the public tape feeds maker fills."""
    from pb.venues import novig as N

    client = client or N.NovigClient.from_env()
    fees: dict[str, FeeSchedule] = {}
    pollers: dict[str, Callable[[], Awaitable[Book]]] = {}
    trade_pollers: dict[str, Callable[[float], Awaitable[list[Trade]]]] = {}
    ws = N.NovigWS(markets, auth=client.auth, url=client.ws_url) if client.auth is not None else None

    async def wire(m: Market) -> None:
        client._markets[m.market_id] = m
        try:
            fees[m.market_id] = await client.fee_schedule(m.market_id)
        except Exception as e:  # pragma: no cover - network
            log.warning("fee schedule %s: %s", m.market_id, e)
            fees[m.market_id] = N.fee_schedule_for(m)
        pollers[m.market_id] = (lambda mid=m.market_id: client.book(mid))
        if ws is None:
            trade_pollers[m.market_id] = (lambda since, mid=m.market_id: client.trades_since(mid, since))
        else:
            await ws.subscribe_more([m])

    for m in markets:
        await wire(m)

    async def check(mid: str) -> Optional[Market]:
        fresh = await client.market(mid)
        return fresh if fresh.result is not None else None

    runner = PaperRunner(markets, lambda mid: fees.get(mid, N.novig_schedule()), strategies,
                         feeds=[ws.events()] if ws is not None else [], pollers=pollers,
                         settlement_checker=check, config=config, signals=signals, recorder=recorder,
                         trade_pollers=trade_pollers if ws is None else None,
                         market_selector=(lambda: selector(client)) if selector is not None else None,
                         market_wiring=wire)
    return runner, client


# ----------------------------------------------------------------------------
# Signal feed construction from CLI specs
# ----------------------------------------------------------------------------
SIGNAL_SPEC_HELP = (
    "comma-separated feeds: coinbase | kraken | twap | openmeteo[:LAT,LON[,BIAS]] | nws:STATION | "
    "odds[:SPORT] | espn[:SPORT]  (SPORT = nfl|nba|mlb|nhl; odds needs ODDS_API_KEY and is skipped without it)"
)


def parse_signal_specs(spec: str | None) -> list[tuple[str, list[str]]]:
    """'coinbase,twap,openmeteo:40.78,-73.97,1.5' -> [('coinbase', []), ('twap', []), ('openmeteo', ['40.78','-73.97','1.5'])]"""
    out: list[tuple[str, list[str]]] = []
    if not spec:
        return out
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        # a numeric argument continues the previous spec (openmeteo:LAT,LON,BIAS)
        if out and ":" not in part and _is_number(part):
            out[-1][1].append(part)
            continue
        name, _, arg = part.partition(":")
        out.append((name.strip().lower().replace("_", "").replace("-", ""), [arg] if arg else []))
    return out


def _is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def build_signal_feeds(spec: str | None, markets: list[Market], env: Optional[dict] = None,
                       http_client: Any = None) -> tuple[list[AsyncIterator[Signal]], list[str]]:
    """Instantiate `pb.data.feeds` generators for a `--signals` spec.
    Returns (feeds, notes); notes explain skipped feeds (e.g. missing
    ODDS_API_KEY or no linkable sports markets). Network only happens when the
    returned generators are iterated."""
    import os

    from pb.data import feeds as F
    from pb.data import odds_link as OL

    env = os.environ if env is None else env
    feeds: list[AsyncIterator[Signal]] = []
    notes: list[str] = []
    http = http_client

    def _http():
        nonlocal http
        if http is None:
            import httpx

            http = httpx.AsyncClient(timeout=20.0)
        return http

    for name, args in parse_signal_specs(spec):
        if name == "coinbase":
            feeds.append(F.index_with_fallback(F.coinbase_index(), lambda: F.kraken_index()))
        elif name == "kraken":
            feeds.append(F.kraken_index())
        elif name == "twap":
            feeds.append(F.polymarket_twap())
        elif name == "openmeteo":
            if len(args) < 2:
                notes.append("openmeteo needs LAT,LON (e.g. openmeteo:40.78,-73.97[,BIAS])")
                continue
            lat, lon = float(args[0]), float(args[1])
            bias = float(args[2]) if len(args) > 2 else 0.0
            rung_markets = [m for m in markets if F.parse_rung(m) is not None]
            if not rung_markets:
                notes.append("openmeteo: no ladder markets with rung bounds; skipped")
                continue
            feeds.append(F.open_meteo_fcst_prob(_http(), rung_markets, lat, lon, bias=bias))
        elif name == "nws":
            if not args:
                notes.append("nws needs a station id (nws:KNYC)")
                continue
            feeds.append(F.nws_observation_signal(_http(), args[0]))
        elif name in ("odds", "espn"):
            sport = (args[0] if args else OL.sport_for_markets(markets) or "").lower()
            if not sport:
                notes.append(f"{name}: could not infer the sport from the markets; pass {name}:nfl")
                continue
            links = OL.build_links(markets, sport=sport)
            if not links:
                notes.append(f"{name}: no market could be linked to a {sport} game; skipped")
                continue
            if name == "odds":
                key = env.get("ODDS_API_KEY", "")
                if not key:
                    notes.append("odds: ODDS_API_KEY not set; skipped")
                    continue
                feeds.append(F.odds_api_sharp_prob(_http(), key, OL.ODDS_API_SPORT_KEYS.get(sport, sport), links))
            else:
                feeds.append(F.espn_game_state(_http(), OL.ESPN_SPORT_PATHS.get(sport, sport), links))
        else:
            notes.append(f"unknown signal feed {name!r}")
    return feeds, notes


__all__ = ["LiveEngine", "Ledger", "PaperConfig", "PaperRunner", "build_strategy", "load_params_yaml",
           "select_kalshi_markets", "select_polymarket_markets", "select_polymarket_crypto_windows",
           "crypto_window_slugs", "build_kalshi_runner",
           "build_polymarket_runner", "build_novig_runner", "build_signal_feeds", "parse_signal_specs", "SIGNAL_SPEC_HELP"]
