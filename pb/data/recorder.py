"""Market-data recorder: venue WS (or REST polling fallback) -> parquet.

Output layout::

    data/recorded/{venue}/{YYYYMMDD}/books-{HHMMSS}-{n}.parquet
    data/recorded/{venue}/{YYYYMMDD}/trades-{HHMMSS}-{n}.parquet
    data/recorded/{venue}/{YYYYMMDD}/markets-{HHMMSS}-{n}.parquet
    data/recorded/{venue}/{YYYYMMDD}/signals-{HHMMSS}-{n}.parquet

Schemas (all timestamps epoch seconds, float64):

* books:   ts, market_id, side ("bid"|"ask"), price, size, level (0 = touch)
           -- one row per level, top `max_levels` (default 20) per side per snapshot
* trades:  ts, market_id, price, size, taker_action ("buy"|"sell")
* markets: ts, market_id, venue, series, event_id, title, open_ts, close_ts,
           result (nullable float), settle_ts (nullable), status, meta_json
           (strategy-facing `Market.meta` keys as JSON, so backtests see the
           same window/strike/ladder metadata the paper run did)
* signals: ts, name, market_id (nullable), value_json -- every reference
           `Signal` the run received (`pb.data.feeds`), so a backtest can
           replay the exact feed (`loaders.load_recorded` merges them back)

The recorder is venue-agnostic: it consumes any async iterator of
`Book | Trade` (plus ignored `RawMessage`s) as the primary feed, and when no
feed is available (WS needs auth, or it errors out) it polls `poller(market_id)`
every `poll_secs` for REST book snapshots. Buffers are flushed every
`flush_secs` and at shutdown; `max_seconds` caps the run (CI jobs).
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Awaitable, Callable, Iterable, Optional

import pyarrow as pa
import pyarrow.parquet as pq

from pb.core.types import Action, Book, Market, Trade, Venue
from pb.sim.engine import Signal

log = logging.getLogger(__name__)

BOOK_SCHEMA = pa.schema([
    ("ts", pa.float64()), ("market_id", pa.string()), ("side", pa.string()),
    ("price", pa.float64()), ("size", pa.float64()), ("level", pa.int32()),
])
TRADE_SCHEMA = pa.schema([
    ("ts", pa.float64()), ("market_id", pa.string()), ("price", pa.float64()),
    ("size", pa.float64()), ("taker_action", pa.string()),
])
MARKET_SCHEMA = pa.schema([
    ("ts", pa.float64()), ("market_id", pa.string()), ("venue", pa.string()),
    ("series", pa.string()), ("event_id", pa.string()), ("title", pa.string()),
    ("open_ts", pa.float64()), ("close_ts", pa.float64()), ("result", pa.float64()),
    ("settle_ts", pa.float64()), ("status", pa.string()), ("meta_json", pa.string()),
])
SIGNAL_SCHEMA = pa.schema([
    ("ts", pa.float64()), ("name", pa.string()), ("market_id", pa.string()), ("value_json", pa.string()),
])
# Market.meta keys worth persisting (the rest is volume/price noise at record time).
META_KEYS = ("window_open_ts", "window_close_ts", "window_secs", "asset", "open_price", "floor_strike",
             "cap_strike", "rung_lo", "rung_hi", "ladder_group", "peak_ts", "mutually_exclusive", "pair_id",
             "category", "fee_type", "subtitle", "condition_id", "no_token", "neg_risk", "slug", "outcomes",
             "fees_enabled", "sport")


def book_rows(b: Book, max_levels: int = 20) -> list[dict]:
    rows = []
    for i, l in enumerate(b.bids[:max_levels]):
        rows.append({"ts": float(b.ts), "market_id": b.market_id, "side": "bid",
                     "price": float(l.price), "size": float(l.size), "level": i})
    for i, l in enumerate(b.asks[:max_levels]):
        rows.append({"ts": float(b.ts), "market_id": b.market_id, "side": "ask",
                     "price": float(l.price), "size": float(l.size), "level": i})
    return rows


def trade_row(t: Trade) -> dict:
    return {"ts": float(t.ts), "market_id": t.market_id, "price": float(t.price),
            "size": float(t.size), "taker_action": t.taker_action.value}


def market_row(m: Market, ts: float) -> dict:
    return {"ts": float(ts), "market_id": m.market_id, "venue": m.venue.value, "series": m.series,
            "event_id": m.event_id, "title": m.title, "open_ts": float(m.open_ts),
            "close_ts": float(m.close_ts), "result": None if m.result is None else float(m.result),
            "settle_ts": None if m.settle_ts is None else float(m.settle_ts),
            "status": str(m.meta.get("status", "") or ""),
            "meta_json": json.dumps({k: m.meta[k] for k in META_KEYS if k in m.meta and m.meta[k] is not None},
                                    default=str)}


def signal_row(s: Signal) -> dict:
    return {"ts": float(s.ts), "name": s.name, "market_id": s.market_id,
            "value_json": json.dumps(s.value, default=str)}


def write_parquet(rows: list[dict], schema: pa.Schema, path: Path) -> Optional[Path]:
    if not rows:
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = {f.name: [r.get(f.name) for r in rows] for f in schema}
    table = pa.table(cols, schema=schema)
    tmp = path.with_suffix(".tmp")
    pq.write_table(table, tmp, compression="zstd")
    os.replace(tmp, path)
    return path


@dataclass
class RecorderStats:
    books: int = 0
    trades: int = 0
    markets: int = 0
    signals: int = 0
    flushes: int = 0
    ws_events: int = 0
    polls: int = 0
    files: list[str] = field(default_factory=list)


class Recorder:
    """See module docstring.

    Parameters
    ----------
    venue:       "kalshi" | "polymarket" (used for the output folder)
    markets:     core Markets to record (metadata is written at start and on refresh)
    out_dir:     root folder (default data/recorded)
    feed:        optional async iterator yielding Book/Trade (WS); None => poll only
    poller:      optional coroutine `(market_id) -> Book` for REST snapshots
    trade_poller: optional coroutine `(market_id, since_ts) -> list[Trade]`
    market_refresher: optional coroutine `(market_id) -> Market` to pick up
                 settlement results; called every `refresh_secs`
    signals:     optional async iterator of `Signal` (e.g. `pb.data.feeds.merge_signals(...)`);
                 persisted to signals-*.parquet
    """

    def __init__(self, venue: str, markets: Iterable[Market], out_dir: str | Path = "data/recorded",
                 feed: Optional[AsyncIterator[Any]] = None,
                 poller: Optional[Callable[[str], Awaitable[Book]]] = None,
                 trade_poller: Optional[Callable[[str, float], Awaitable[list[Trade]]]] = None,
                 market_refresher: Optional[Callable[[str], Awaitable[Market]]] = None,
                 poll_secs: float = 5.0, flush_secs: float = 60.0, refresh_secs: float = 300.0,
                 max_seconds: Optional[float] = None, max_levels: int = 20,
                 clock: Callable[[], float] = time.time, ws_stale_secs: float = 30.0,
                 signals: Optional[AsyncIterator[Signal]] = None):
        self.venue = venue
        self.signals = signals
        self.markets: dict[str, Market] = {m.market_id: m for m in markets}
        self.out_dir = Path(out_dir)
        self.feed = feed
        self.poller = poller
        self.trade_poller = trade_poller
        self.market_refresher = market_refresher
        self.poll_secs = poll_secs
        self.flush_secs = flush_secs
        self.refresh_secs = refresh_secs
        self.max_seconds = max_seconds
        self.max_levels = max_levels
        self.clock = clock
        self.ws_stale_secs = ws_stale_secs
        self._books: list[dict] = []
        self._trades: list[dict] = []
        self._markets: list[dict] = []
        self._signals: list[dict] = []
        self._seen_trades: set[tuple] = set()
        self._flush_n = 0
        self._last_ws_event = 0.0
        self._last_trade_ts: dict[str, float] = {}
        self.stats = RecorderStats()
        self._stop = asyncio.Event()
        self.feed_alive = feed is not None

    # -- buffering -------------------------------------------------------------
    def on_book(self, b: Book) -> None:
        if b.market_id not in self.markets:
            return
        self._books.extend(book_rows(b, self.max_levels))
        self.stats.books += 1

    def on_trade(self, t: Trade) -> None:
        if t.market_id not in self.markets:
            return
        key = (t.market_id, round(t.ts, 3), t.price, t.size, t.taker_action.value)
        if key in self._seen_trades:
            return
        self._seen_trades.add(key)
        if len(self._seen_trades) > 50_000:
            self._seen_trades = set(list(self._seen_trades)[-10_000:])
        self._trades.append(trade_row(t))
        self._last_trade_ts[t.market_id] = max(self._last_trade_ts.get(t.market_id, 0.0), t.ts)
        self.stats.trades += 1

    def on_market(self, m: Market) -> None:
        self.markets[m.market_id] = m
        self._markets.append(market_row(m, self.clock()))
        self.stats.markets += 1

    def on_signal(self, s: Signal) -> None:
        self._signals.append(signal_row(s))
        self.stats.signals += 1

    def on_event(self, ev: Any) -> None:
        if isinstance(ev, Book):
            self.on_book(ev)
        elif isinstance(ev, Trade):
            self.on_trade(ev)
        elif isinstance(ev, Signal):
            self.on_signal(ev)
        # RawMessage etc. ignored

    # -- flushing ----------------------------------------------------------------
    def _paths(self) -> tuple[Path, Path, Path, Path]:
        now = datetime.fromtimestamp(self.clock(), tz=timezone.utc)
        d = self.out_dir / self.venue / now.strftime("%Y%m%d")
        stamp = f"{now.strftime('%H%M%S')}-{self._flush_n:04d}"
        return (d / f"books-{stamp}.parquet", d / f"trades-{stamp}.parquet", d / f"markets-{stamp}.parquet",
                d / f"signals-{stamp}.parquet")

    def flush(self) -> list[Path]:
        bp, tp, mp, sp = self._paths()
        self._flush_n += 1
        out = []
        for rows, schema, path in ((self._books, BOOK_SCHEMA, bp), (self._trades, TRADE_SCHEMA, tp),
                                   (self._markets, MARKET_SCHEMA, mp), (self._signals, SIGNAL_SCHEMA, sp)):
            p = write_parquet(rows, schema, path)
            if p is not None:
                out.append(p)
                self.stats.files.append(str(p))
        self._books, self._trades, self._markets, self._signals = [], [], [], []
        if out:
            self.stats.flushes += 1
            log.info("flushed %s", ", ".join(p.name for p in out))
        return out

    # -- run loop ----------------------------------------------------------------
    def stop(self) -> None:
        self._stop.set()

    async def run(self) -> RecorderStats:
        start = self.clock()
        for m in list(self.markets.values()):
            self.on_market(m)
        tasks = [asyncio.create_task(self._flusher()), asyncio.create_task(self._poll_loop()),
                 asyncio.create_task(self._refresh_loop())]
        if self.feed is not None:
            tasks.append(asyncio.create_task(self._feed_loop()))
        if self.signals is not None:
            tasks.append(asyncio.create_task(self._signal_loop()))
        if self.max_seconds is not None:
            tasks.append(asyncio.create_task(self._deadline(start)))
        try:
            await self._stop.wait()
        finally:
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            self.flush()
        return self.stats

    async def _deadline(self, start: float) -> None:
        # Wall-clock deadline (event-loop monotonic time, independent of `clock`).
        await asyncio.sleep(float(self.max_seconds))  # type: ignore[arg-type]
        self._stop.set()

    async def _flusher(self) -> None:
        while True:
            await asyncio.sleep(self.flush_secs)
            try:
                self.flush()
            except Exception as e:  # pragma: no cover
                log.exception("flush failed: %s", e)

    async def _feed_loop(self) -> None:
        try:
            async for ev in self.feed:  # type: ignore[union-attr]
                self.stats.ws_events += 1
                self._last_ws_event = self.clock()
                self.feed_alive = True
                self.on_event(ev)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.warning("feed ended with %s; falling back to polling", e)
        self.feed_alive = False

    async def _signal_loop(self) -> None:
        try:
            async for s in self.signals:  # type: ignore[union-attr]
                if isinstance(s, Signal):
                    self.on_signal(s)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.warning("signal feed ended with %s", e)

    def _ws_healthy(self) -> bool:
        return self.feed_alive and (self.clock() - self._last_ws_event) < self.ws_stale_secs

    async def _poll_loop(self) -> None:
        if self.poller is None and self.trade_poller is None:
            return
        while True:
            await asyncio.sleep(self.poll_secs)
            if self._ws_healthy():
                continue
            for mid in list(self.markets):
                try:
                    if self.poller is not None:
                        b = await self.poller(mid)
                        self.stats.polls += 1
                        if b is not None:
                            self.on_book(b)
                    if self.trade_poller is not None:
                        since = self._last_trade_ts.get(mid, self.clock() - 3600)
                        for t in await self.trade_poller(mid, since):
                            self.on_trade(t)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    log.warning("poll %s failed: %s", mid, e)

    async def _refresh_loop(self) -> None:
        if self.market_refresher is None:
            return
        while True:
            await asyncio.sleep(self.refresh_secs)
            for mid in list(self.markets):
                try:
                    m = await self.market_refresher(mid)
                    if m is not None:
                        self.on_market(m)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    log.warning("refresh %s failed: %s", mid, e)


# ----------------------------------------------------------------------------
# Venue wiring (network; used by scripts/record.py)
# ----------------------------------------------------------------------------
async def build_kalshi_recorder(tickers: Iterable[str], out_dir: str | Path = "data/recorded",
                                demo: bool = False, **kw) -> tuple[Recorder, Any]:
    """Create a Recorder for Kalshi tickers. Uses the WS feed when auth env is
    present, REST polling otherwise. Returns (recorder, client) so the caller
    can close the client."""
    from pb.venues import kalshi as K

    client = K.KalshiClient.from_env(demo=demo)
    markets = [await client.market(t) for t in tickers]
    feed = None
    if client.auth is not None:
        ws = K.KalshiWS(tickers, auth=client.auth, url=K.DEMO_WS if demo else K.PROD_WS)
        feed = ws.events()

    async def poll(mid: str) -> Book:
        return await client.book(mid, depth=kw.get("max_levels", 20))

    async def trades(mid: str, since: float) -> list[Trade]:
        resp = await client.get_trades(ticker=mid, limit=200, min_ts=int(since))
        return K.to_trades(resp, mid)

    async def refresh(mid: str) -> Market:
        return await client.market(mid)

    rec = Recorder("kalshi", markets, out_dir, feed=feed, poller=poll, trade_poller=trades,
                   market_refresher=refresh, **kw)
    return rec, client


async def build_polymarket_recorder(markets: Iterable[Market], out_dir: str | Path = "data/recorded",
                                    **kw) -> tuple[Recorder, Any]:
    from pb.venues import polymarket as P

    client = P.PolymarketClient()
    markets = list(markets)
    ws = P.PolymarketWS([m.market_id for m in markets])
    feed = ws.events()

    async def poll(mid: str) -> Book:
        return await client.book(mid)

    async def trades(mid: str, since: float) -> list[Trade]:
        m = next((x for x in markets if x.market_id == mid), None)
        cond = m.meta.get("condition_id") if m else None
        if not cond:
            return []
        page = await client.get_trades(cond, limit=200)
        out = []
        for row in page.get("trades", []):
            t = P.to_trade(row, mid, is_no_token=str(P._get(row, "asset", "asset_id", default="")) == m.meta.get("no_token"))
            if t.ts >= since:
                out.append(t)
        return out

    rec = Recorder("polymarket", markets, out_dir, feed=feed, poller=poll, trade_poller=trades, **kw)
    return rec, client
