"""Historical loaders -> Engine event streams.

Three fidelity tiers:

1. **Recorded L2** (`load_recorded`): our own parquet from `pb.data.recorder`.
   Full books (top-20) + prints. Highest fidelity; use the default `SimConfig`.
2. **Candle + tape** (`kalshi_history`, `polymarket_history`): venue history
   endpoints. Each candle becomes a one-level Book (bid = yes_bid close, ask =
   yes_ask close, size = `max(1, volume/5)` proxy) and prints come from the
   trade tape. The returned `HistoryEvents` has `low_fidelity=True`; runners
   MUST set `SimConfig(maker_requires_through=True)` for these.
3. **Jon Becker Polymarket dump** (`download_jon_becker` / `load_jon_becker`):
   external archive of markets + trades; tape only (books are synthesised from
   trades at the last print, so also low fidelity).
"""
from __future__ import annotations

import glob
import heapq
import itertools
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Optional

import pyarrow.parquet as pq

from pb.core.types import Action, Book, Level, Market, Trade, Venue
from pb.sim.engine import Event, Settlement, Signal

log = logging.getLogger(__name__)


@dataclass
class HistoryEvents:
    """Events plus the fidelity flag the runner needs to configure the Engine."""
    markets: list[Market]
    events: Iterator[Event]
    low_fidelity: bool = False
    source: str = ""
    notes: list[str] = field(default_factory=list)

    def __iter__(self) -> Iterator[Event]:
        return self.events


# ----------------------------------------------------------------------------
# Recorded parquet
# ----------------------------------------------------------------------------
def _read_rows(path: str | Path, columns: Optional[list[str]] = None) -> list[dict]:
    t = pq.read_table(str(path), columns=columns)
    return t.to_pylist()


def _books_from_rows(rows: Iterable[dict]) -> Iterator[Book]:
    """Group level rows (sorted by ts, market_id) back into Book objects."""
    cur_key: Optional[tuple] = None
    bids: list[Level] = []
    asks: list[Level] = []
    for r in rows:
        key = (float(r["ts"]), r["market_id"])
        if key != cur_key:
            if cur_key is not None:
                yield _mk_book(cur_key, bids, asks)
            cur_key, bids, asks = key, [], []
        lvl = Level(float(r["price"]), float(r["size"]))
        (bids if r["side"] == "bid" else asks).append(lvl)
    if cur_key is not None:
        yield _mk_book(cur_key, bids, asks)


def _mk_book(key: tuple, bids: list[Level], asks: list[Level]) -> Book:
    bids.sort(key=lambda l: -l.price)
    asks.sort(key=lambda l: l.price)
    return Book(ts=key[0], market_id=key[1], bids=bids, asks=asks)


def _file_events(path: str, markets: Optional[set[str]]) -> Iterator[Event]:
    name = Path(path).name
    rows = _read_rows(path)
    if markets is not None:
        # signal rows with a null market_id are global (index prices etc.) and always kept
        rows = [r for r in rows if r["market_id"] in markets or (name.startswith("signals") and not r["market_id"])]
    if name.startswith("books"):
        rows.sort(key=lambda r: (r["ts"], r["market_id"], r["side"], int(r.get("level", 0))))
        yield from _books_from_rows(rows)
    elif name.startswith("trades"):
        rows.sort(key=lambda r: r["ts"])
        for r in rows:
            yield Trade(ts=float(r["ts"]), market_id=r["market_id"], price=float(r["price"]),
                        size=float(r["size"]), taker_action=Action(r["taker_action"]))
    elif name.startswith("signals"):
        rows.sort(key=lambda r: r["ts"])
        yield from signals_from_signal_rows(rows)


def signals_from_signal_rows(rows: Iterable[dict]) -> Iterator[Signal]:
    """recorder `signals-*.parquet` rows (ts, name, market_id, value_json) -> Signals.
    Global signals (market_id null) are always kept; `_file_events` has already
    filtered per-market rows when a market subset was requested."""
    for r in rows:
        v = r.get("value_json")
        try:
            val = json.loads(v) if isinstance(v, str) else v
        except ValueError:
            val = v
        yield Signal(ts=float(r["ts"]), name=str(r["name"]), market_id=r.get("market_id") or None, value=val)


def _market_from_row(r: dict) -> Market:
    meta: dict = {"status": r.get("status") or ""}
    mj = r.get("meta_json")
    if isinstance(mj, str) and mj:
        try:
            extra = json.loads(mj)
            if isinstance(extra, dict):
                meta.update(extra)
        except ValueError:
            pass
    return Market(venue=Venue(r.get("venue") or "kalshi"), market_id=r["market_id"],
                  event_id=r.get("event_id") or "", series=r.get("series") or "",
                  title=r.get("title") or "", open_ts=float(r.get("open_ts") or 0.0),
                  close_ts=float(r.get("close_ts") or 0.0),
                  result=None if r.get("result") is None else float(r["result"]),
                  settle_ts=None if r.get("settle_ts") is None else float(r["settle_ts"]),
                  meta=meta)


def _merge(iters: list[Iterator[Event]]) -> Iterator[Event]:
    """Merge-sort already-sorted event iterators by ts (stable, heapq)."""
    counter = itertools.count()
    heap: list[tuple[float, int, Event, Iterator[Event]]] = []
    for it in iters:
        for ev in it:
            heapq.heappush(heap, (ev.ts, next(counter), ev, it))
            break
    while heap:
        ts, _, ev, it = heapq.heappop(heap)
        yield ev
        for nxt in it:
            heapq.heappush(heap, (nxt.ts, next(counter), nxt, it))
            break


def _tail_with_settlements(events: Iterator[Event], settlements: list[Settlement]) -> Iterator[Event]:
    """Yield events and inject settlements once the stream passes their ts."""
    pending = sorted(settlements, key=lambda s: s.ts)
    for ev in events:
        while pending and pending[0].ts <= ev.ts:
            yield pending.pop(0)
        yield ev
    yield from pending


def load_recorded(path_glob: str | Iterable[str], markets: Optional[Iterable[str]] = None,
                  signals: bool = True) -> tuple[list[Market], Iterator[Event]]:
    """Load recorder parquet files matching `path_glob` (a glob or list of globs;
    a directory is expanded to `<dir>/**/*.parquet`).

    Returns `(markets, events)` where events are `Book | Trade | Signal |
    Settlement` in ts order (files merged with heapq). Books are rebuilt from
    level rows; `signals-*.parquet` rows become `Signal`s (set `signals=False`
    to drop them, e.g. when supplying a different feed via `--signals`).
    Market metadata comes from `markets-*.parquet` (incl. `meta_json`); a
    market whose latest metadata row carries a result gets a `Settlement` at
    `settle_ts` (or `close_ts`, or after the last event)."""
    globs = [path_glob] if isinstance(path_glob, str) else list(path_glob)
    files: list[str] = []
    for g in globs:
        if Path(g).is_dir():
            g = str(Path(g) / "**" / "*.parquet")
        files.extend(glob.glob(g, recursive=True))
    files = sorted(set(files))
    wanted = set(markets) if markets is not None else None
    market_rows: dict[str, dict] = {}
    data_files = []
    for f in files:
        name = Path(f).name
        if name.startswith("markets"):
            for r in _read_rows(f):
                if wanted is not None and r["market_id"] not in wanted:
                    continue
                prev = market_rows.get(r["market_id"])
                if prev is None or float(r["ts"]) >= float(prev["ts"]):
                    market_rows[r["market_id"]] = r
        elif name.startswith(("books", "trades")) or (signals and name.startswith("signals")):
            data_files.append(f)
    mkts = [_market_from_row(r) for r in market_rows.values()]
    if wanted is not None:
        known = {m.market_id for m in mkts}
        for mid in wanted - known:
            mkts.append(Market(venue=Venue.KALSHI, market_id=mid))
    last_ts = 0.0
    settlements = []
    for m in mkts:
        if m.result is not None:
            settlements.append(Settlement(ts=m.settle_ts or m.close_ts or float("inf"),
                                          market_id=m.market_id, result=m.result))
            m.result = None  # Engine sets it at settlement
    merged = _merge([_file_events(f, wanted) for f in data_files])

    def gen() -> Iterator[Event]:
        nonlocal last_ts
        for ev in _tail_with_settlements(merged, [s for s in settlements if s.ts != float("inf")]):
            last_ts = max(last_ts, ev.ts)
            yield ev
        for s in settlements:
            if s.ts == float("inf"):
                s.ts = last_ts + 1.0
                yield s

    return mkts, gen()


# ----------------------------------------------------------------------------
# Low-fidelity candle + tape builders (venue agnostic core)
# ----------------------------------------------------------------------------
def candle_book(market_id: str, ts: float, bid: Optional[float], ask: Optional[float],
                volume: float) -> Optional[Book]:
    """One-level Book from a candle close. Size proxy: max(1, volume/5)."""
    size = max(1.0, float(volume or 0.0) / 5.0)
    bids = [Level(bid, size)] if bid is not None and 0 < bid < 1 else []
    asks = [Level(ask, size)] if ask is not None and 0 < ask < 1 else []
    if not bids and not asks:
        return None
    if bids and asks and asks[0].price <= bids[0].price:
        # crossed candle data: widen around mid by one tick
        mid = (bids[0].price + asks[0].price) / 2
        bids, asks = [Level(round(mid - 0.005, 4), size)], [Level(round(mid + 0.005, 4), size)]
    return Book(ts=ts, market_id=market_id, bids=bids, asks=asks)


def tape_events(books: Iterable[Book], trades: Iterable[Trade],
                settlement: Optional[Settlement] = None) -> Iterator[Event]:
    evs: list[Event] = list(books) + list(trades)
    evs.sort(key=lambda e: (e.ts, 0 if isinstance(e, Book) else 1))
    yield from evs
    if settlement is not None:
        yield settlement


# ----------------------------------------------------------------------------
# Kalshi history
# ----------------------------------------------------------------------------
async def kalshi_history(series: str, start: float, end: float, client: Any,
                         tickers: Optional[Iterable[str]] = None,
                         period_interval: int = 1, use_historical: Optional[bool] = None
                         ) -> HistoryEvents:
    """Build low-fidelity events for all markets of `series` closing in
    [start, end] (epoch secs) using `/historical/*` where the window is older
    than the cutoff, else `/markets`, `/series/.../candlesticks`, `/markets/trades`.

    `client` is a `pb.venues.kalshi.KalshiClient` (or a duck-typed fake)."""
    from pb.venues import kalshi as K

    start_i, end_i = int(start), int(end)
    cutoff = None
    if use_historical is None:
        try:
            c = await client.get_historical_cutoff()
            cutoff = K._ts(K._get(c, "cutoff_ts", "cutoff", "ts"), 0.0) or None
        except Exception as e:  # endpoint may not exist on demo
            log.info("historical cutoff unavailable: %s", e)
        use_historical = bool(cutoff and end_i < cutoff)
    raw_markets: list[dict] = []
    if tickers:
        for t in tickers:
            try:
                raw_markets.append(await client.get_market(t))
            except Exception as e:
                log.warning("market %s: %s", t, e)
    else:
        cursor = None
        for _ in range(100):
            if use_historical:
                page = await client.get_historical_markets(series_ticker=series, cursor=cursor,
                                                           min_close_ts=start_i, max_close_ts=end_i)
            else:
                page = await client.get_markets(series_ticker=series, cursor=cursor,
                                                min_close_ts=start_i, max_close_ts=end_i)
            raw_markets.extend(page.get("markets", []) or [])
            cursor = page.get("cursor")
            if not cursor:
                break
    markets = [K.to_market(m) for m in raw_markets]
    per_market: list[Iterator[Event]] = []
    notes = []
    for m in markets:
        m_start = int(m.open_ts or start_i)
        m_end = int(m.close_ts or end_i)
        lo = max(start_i, m_start - 60)
        hi = min(end_i, m_end + 60) if m_end else end_i
        books: list[Book] = []
        try:
            if use_historical:
                cs = await client.get_historical_candlesticks(m.market_id, lo, hi, period_interval)
            else:
                cs = await client.get_candlesticks(m.series or series, m.market_id, lo, hi, period_interval)
            for c in cs.get("candlesticks", []) or []:
                s = K.candle_to_summary(c)
                b = candle_book(m.market_id, s["ts"], s["bid_close"], s["ask_close"], s["volume"])
                if b is not None:
                    books.append(b)
        except Exception as e:
            notes.append(f"candles {m.market_id}: {e}")
        trades: list[Trade] = []
        try:
            cursor = None
            for _ in range(200):
                if use_historical:
                    page = await client.get_historical_trades(ticker=m.market_id, cursor=cursor,
                                                              min_ts=lo, max_ts=hi)
                else:
                    page = await client.get_trades(ticker=m.market_id, cursor=cursor, min_ts=lo, max_ts=hi)
                trades.extend(K.to_trades(page, m.market_id))
                cursor = page.get("cursor")
                if not cursor:
                    break
        except Exception as e:
            notes.append(f"trades {m.market_id}: {e}")
        settlement = None
        if m.result is not None:
            settlement = Settlement(ts=m.settle_ts or m.close_ts or (books[-1].ts + 1 if books else hi),
                                    market_id=m.market_id, result=m.result)
            m.result = None
        per_market.append(tape_events(books, trades, settlement))
    return HistoryEvents(markets=markets, events=_merge(per_market), low_fidelity=True,
                         source=f"kalshi:{series}", notes=notes)


# ----------------------------------------------------------------------------
# Polymarket history
# ----------------------------------------------------------------------------
async def polymarket_history(token_id: str, start: float, end: float, client: Any,
                             market: Optional[Market] = None, fidelity_minutes: int = 1,
                             spread: float = 0.01) -> HistoryEvents:
    """Low-fidelity events for one YES token from CLOB `/prices-history` (mid
    series -> one-level synthetic book at mid +/- spread/2, size proxy from
    nearby trade volume) and Data-API trades."""
    from pb.venues import polymarket as P

    hist = await client.get_prices_history(token_id, start_ts=int(start), end_ts=int(end),
                                           fidelity=fidelity_minutes)
    trades: list[Trade] = []
    cond = market.meta.get("condition_id") if market else None
    if cond:
        try:
            rows = await client.iter_trades(cond)
            no_tok = market.meta.get("no_token") if market else None
            for r in rows:
                asset = str(P._get(r, "asset", "asset_id", default=""))
                t = P.to_trade(r, token_id, is_no_token=(no_tok is not None and asset == no_tok))
                if start <= t.ts <= end:
                    trades.append(t)
        except Exception as e:
            log.warning("polymarket trades for %s: %s", cond, e)
    trades.sort(key=lambda t: t.ts)
    # volume proxy: trades within the candle bucket
    bucket = max(60, fidelity_minutes * 60)
    vol: dict[int, float] = {}
    for t in trades:
        vol[int(t.ts // bucket)] = vol.get(int(t.ts // bucket), 0.0) + t.size
    books = []
    for h in hist:
        ts = P._ts(P._get(h, "t", "ts", "timestamp"), 0.0)
        p = P._num(P._get(h, "p", "price"), 0.0)
        if ts <= 0 or not (0 < p < 1):
            continue
        b = candle_book(token_id, ts, round(max(0.001, p - spread / 2), 4),
                        round(min(0.999, p + spread / 2), 4), vol.get(int(ts // bucket), 0.0))
        if b is not None:
            books.append(b)
    mk = market or Market(venue=Venue.POLYMARKET, market_id=token_id)
    settlement = None
    if mk.result is not None:
        settlement = Settlement(ts=mk.settle_ts or mk.close_ts or end, market_id=token_id, result=mk.result)
        mk.result = None
    return HistoryEvents(markets=[mk], events=tape_events(books, trades, settlement), low_fidelity=True,
                         source=f"polymarket:{token_id}")


# ----------------------------------------------------------------------------
# Jon Becker Polymarket dataset
# ----------------------------------------------------------------------------
JON_BECKER_URLS = {
    # Public archive of Polymarket markets and trade history (HuggingFace).
    "markets": "https://huggingface.co/datasets/jon-becker/polymarket-markets/resolve/main/markets.parquet",
    "trades": "https://huggingface.co/datasets/jon-becker/polymarket-trades/resolve/main/trades.parquet",
}
JON_BECKER_README = """\
Jon Becker's Polymarket dataset (HuggingFace: jon-becker/polymarket-*).

Download manually (or with `huggingface_hub`) into `data/raw/jon_becker/`:

    huggingface-cli download jon-becker/polymarket-markets --repo-type dataset --local-dir data/raw/jon_becker/markets
    huggingface-cli download jon-becker/polymarket-trades  --repo-type dataset --local-dir data/raw/jon_becker/trades

Expected columns (defensively mapped by `load_jon_becker`):
  markets: condition_id / id, question, clob_token_ids | token_ids, end_date, outcome / result
  trades:  timestamp, asset_id | token_id, price, size, side, condition_id | market
"""


def download_jon_becker(dest: str | Path) -> list[str]:
    """Return the shell commands / URLs needed to fetch the dataset into `dest`.
    No network call is made here (CI has no internet locally)."""
    dest = Path(dest)
    cmds = [f"mkdir -p {dest}"]
    for name, url in JON_BECKER_URLS.items():
        cmds.append(f"curl -L -o {dest / (name + '.parquet')} {url}")
    return cmds


def _first(d: dict, *names: str, default: Any = None) -> Any:
    for n in names:
        if n in d and d[n] is not None:
            return d[n]
    return default


def load_jon_becker(markets_path: str | Path, trades_path: str | Path,
                    condition_ids: Optional[Iterable[str]] = None, spread: float = 0.02
                    ) -> HistoryEvents:
    """Read the dataset parquet files and produce tape-only low-fidelity events.
    Books are synthesised at each print (last price +/- spread/2, size = print size)."""
    import json as _json

    wanted = set(condition_ids) if condition_ids else None
    mrows = _read_rows(markets_path)
    markets: dict[str, Market] = {}
    tok_to_mid: dict[str, tuple[str, bool]] = {}
    for r in mrows:
        cond = str(_first(r, "condition_id", "conditionId", "id", default=""))
        if wanted is not None and cond not in wanted:
            continue
        toks = _first(r, "clob_token_ids", "clobTokenIds", "token_ids", "tokens", default=[])
        if isinstance(toks, str):
            try:
                toks = _json.loads(toks)
            except ValueError:
                toks = [x.strip() for x in toks.strip("[]").split(",") if x.strip()]
        toks = [str(t) for t in (toks or [])]
        yes = toks[0] if toks else cond
        res = _first(r, "result", "outcome", "winner")
        result = None
        if res is not None:
            s = str(res).lower()
            result = 1.0 if s in ("yes", "1", "1.0", "true") else 0.0 if s in ("no", "0", "0.0", "false") else None
        m = Market(venue=Venue.POLYMARKET, market_id=yes, event_id=cond,
                   series=str(_first(r, "category", default="other")).lower(),
                   title=str(_first(r, "question", "title", default="")),
                   close_ts=_safe_ts(_first(r, "end_date", "endDate", "end_ts")), result=result,
                   meta={"condition_id": cond, "no_token": toks[1] if len(toks) > 1 else ""})
        markets[yes] = m
        tok_to_mid[yes] = (yes, False)
        if len(toks) > 1:
            tok_to_mid[toks[1]] = (yes, True)
    trows = _read_rows(trades_path)
    trades: list[Trade] = []
    for r in trows:
        asset = str(_first(r, "asset_id", "token_id", "asset", default=""))
        if asset not in tok_to_mid:
            cond = str(_first(r, "condition_id", "market", default=""))
            yes = next((m for m in markets if markets[m].event_id == cond), None)
            if yes is None:
                continue
            mid, is_no = yes, False
        else:
            mid, is_no = tok_to_mid[asset]
        price = float(_first(r, "price", default=0.0))
        side = str(_first(r, "side", default="BUY")).upper()
        act = Action.BUY if side in ("BUY", "BID") else Action.SELL
        if is_no:
            price, act = round(1 - price, 6), (Action.SELL if act is Action.BUY else Action.BUY)
        trades.append(Trade(ts=_safe_ts(_first(r, "timestamp", "ts", "time")), market_id=mid, price=price,
                            size=float(_first(r, "size", "amount", default=0.0)), taker_action=act))
    trades.sort(key=lambda t: t.ts)
    books = [Book(ts=t.ts - 1e-3, market_id=t.market_id,
                  bids=[Level(round(max(0.001, t.price - spread / 2), 4), max(1.0, t.size))],
                  asks=[Level(round(min(0.999, t.price + spread / 2), 4), max(1.0, t.size))])
             for t in trades]
    settlements = []
    last = trades[-1].ts if trades else 0.0
    for m in markets.values():
        if m.result is not None:
            settlements.append(Settlement(ts=m.close_ts or last + 1, market_id=m.market_id, result=m.result))
            m.result = None

    def gen() -> Iterator[Event]:
        yield from _tail_with_settlements(tape_events(books, trades), settlements)

    return HistoryEvents(markets=list(markets.values()), events=gen(), low_fidelity=True,
                         source="jon_becker")


def _safe_ts(v: Any) -> float:
    from pb.venues.kalshi import _ts

    if hasattr(v, "timestamp"):
        try:
            return float(v.timestamp())
        except Exception:
            pass
    return _ts(v, 0.0)


__all__ = ["HistoryEvents", "load_recorded", "kalshi_history", "polymarket_history",
           "candle_book", "tape_events", "download_jon_becker", "load_jon_becker",
           "JON_BECKER_URLS", "JON_BECKER_README"]
