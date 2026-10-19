import asyncio
import json

import pyarrow.parquet as pq
import pytest

from pb.core.fees import KALSHI_DEFAULT
from pb.core.types import Action, Book, Level, Market, Order, TIF, Trade, Venue
from pb.data import loaders as L
from pb.data.recorder import Recorder, book_rows
from pb.live.paper import Ledger, PaperConfig, PaperRunner, build_strategy, load_params_yaml
from pb.sim.engine import Settlement, SimConfig, Strategy


def mkbook(ts, mid="M", bids=((0.45, 10), (0.44, 5)), asks=((0.47, 8),)):
    return Book(ts=ts, market_id=mid, bids=[Level(p, s) for p, s in bids], asks=[Level(p, s) for p, s in asks])


# ----------------------------------------------------------------------------
# Recorder
# ----------------------------------------------------------------------------
class FakeFeed:
    """Async iterator that yields queued events then blocks until cancelled."""

    def __init__(self, events):
        self.events = list(events)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.events:
            await asyncio.sleep(0)
            return self.events.pop(0)
        await asyncio.sleep(3600)
        raise StopAsyncIteration


async def test_recorder_flushes_books_trades_markets(tmp_path):
    now = [1792152000.0]
    m = Market(venue=Venue.KALSHI, market_id="M", series="S", close_ts=now[0] + 600, meta={"status": "open"})
    big = mkbook(now[0] + 1, bids=[(0.5 - i * 0.01, i + 1) for i in range(30)], asks=[(0.51 + i * 0.01, 1) for i in range(3)])
    feed = FakeFeed([mkbook(now[0]), Trade(now[0] + 0.5, "M", 0.47, 2, Action.BUY),
                     Trade(now[0] + 0.5, "M", 0.47, 2, Action.BUY),  # duplicate -> dropped
                     big, Trade(now[0] + 2, "OTHER", 0.5, 1, Action.SELL)])  # unknown market -> dropped
    rec = Recorder("kalshi", [m], tmp_path, feed=feed, poll_secs=0.01, flush_secs=0.05, max_seconds=0.3,
                   clock=lambda: now[0])
    stats = await rec.run()
    assert stats.books == 2 and stats.trades == 1 and stats.markets == 1
    day = tmp_path / "kalshi" / "20261016"
    bfiles = sorted(day.glob("books-*.parquet"))
    tfiles = sorted(day.glob("trades-*.parquet"))
    mfiles = sorted(day.glob("markets-*.parquet"))
    assert bfiles and tfiles and mfiles
    books = pq.read_table(bfiles[0]).to_pylist()
    assert {r["side"] for r in books} == {"bid", "ask"}
    # top-20 cap per side
    assert sum(1 for r in books if r["ts"] == now[0] + 1 and r["side"] == "bid") == 20
    assert books[0]["level"] == 0
    trades = pq.read_table(tfiles[0]).to_pylist()
    assert trades == [{"ts": now[0] + 0.5, "market_id": "M", "price": 0.47, "size": 2.0, "taker_action": "buy"}]
    mk = pq.read_table(mfiles[0]).to_pylist()[0]
    assert mk["market_id"] == "M" and mk["result"] is None and mk["status"] == "open"


async def test_recorder_polls_when_no_feed(tmp_path):
    now = [1792152000.0]
    polls = []

    async def poll(mid):
        polls.append(mid)
        return mkbook(now[0], mid)

    async def refresh(mid):
        return Market(venue=Venue.KALSHI, market_id=mid, result=1.0, settle_ts=now[0], meta={"status": "settled"})

    m = Market(venue=Venue.KALSHI, market_id="M")
    rec = Recorder("kalshi", [m], tmp_path, feed=None, poller=poll, market_refresher=refresh,
                   poll_secs=0.01, refresh_secs=0.02, flush_secs=10, max_seconds=0.15, clock=lambda: now[0])
    stats = await rec.run()
    assert polls and stats.books == len(polls)
    mrows = pq.read_table(sorted((tmp_path / "kalshi" / "20261016").glob("markets-*.parquet"))[0]).to_pylist()
    assert mrows[-1]["result"] == 1.0


async def test_recorder_falls_back_when_feed_dies(tmp_path):
    now = [1000.0]

    class Dying:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise ConnectionError("ws down")

    polls = []

    async def poll(mid):
        polls.append(mid)
        return mkbook(now[0], mid)

    rec = Recorder("polymarket", [Market(venue=Venue.POLYMARKET, market_id="111")], tmp_path, feed=Dying(),
                   poller=poll, poll_secs=0.01, flush_secs=10, max_seconds=0.1, clock=lambda: now[0])
    await rec.run()
    assert polls


# ----------------------------------------------------------------------------
# Loaders
# ----------------------------------------------------------------------------
async def _record_fixture(tmp_path):
    now = 1792152000.0
    m = Market(venue=Venue.KALSHI, market_id="M", series="S", close_ts=now + 100)
    feed = FakeFeed([mkbook(now), Trade(now + 1, "M", 0.47, 2, Action.BUY), mkbook(now + 2, bids=((0.46, 3),))])
    rec = Recorder("kalshi", [m], tmp_path, feed=feed, flush_secs=100, max_seconds=0.1, clock=lambda: now)
    await rec.run()
    # second "file set" with later events + settlement metadata
    feed2 = FakeFeed([Trade(now + 3, "M", 0.46, 1, Action.SELL), mkbook(now + 4)])
    m2 = Market(venue=Venue.KALSHI, market_id="M", series="S", close_ts=now + 100, result=1.0, settle_ts=now + 50)
    rec2 = Recorder("kalshi", [m2], tmp_path, feed=feed2, flush_secs=100, max_seconds=0.1, clock=lambda: now + 10)
    await rec2.run()
    return now


async def test_load_recorded_merges_and_reconstructs(tmp_path):
    now = await _record_fixture(tmp_path)
    markets, events = L.load_recorded(str(tmp_path / "kalshi"))
    assert [m.market_id for m in markets] == ["M"]
    evs = list(events)
    ts = [e.ts for e in evs]
    assert ts == sorted(ts)
    kinds = [type(e).__name__ for e in evs]
    assert kinds == ["Book", "Trade", "Book", "Trade", "Book", "Settlement"]
    b0 = evs[0]
    assert b0.bids[0].price == 0.45 and b0.bids[1].price == 0.44 and b0.asks[0].size == 8
    assert evs[2].bids[0].price == 0.46
    assert evs[-1].result == 1.0 and evs[-1].ts == now + 50
    assert markets[0].result is None  # Engine sets it via Settlement
    # filtering by market
    _, ev2 = L.load_recorded(str(tmp_path / "kalshi" / "**" / "*.parquet"), markets=["NOPE"])
    assert [e for e in ev2 if not isinstance(e, Settlement)] == []


def test_candle_book_and_tape_events():
    b = L.candle_book("M", 10.0, 0.45, 0.47, 100.0)
    assert b.bids[0].size == 20 and b.asks[0].price == 0.47
    assert L.candle_book("M", 10.0, 0.45, 0.47, 0.0).bids[0].size == 1
    assert L.candle_book("M", 1.0, None, None, 1.0) is None
    crossed = L.candle_book("M", 1.0, 0.50, 0.49, 1.0)
    assert crossed.best_bid < crossed.best_ask
    evs = list(L.tape_events([L.candle_book("M", 2.0, 0.4, 0.5, 1)], [Trade(2.0, "M", 0.5, 1, Action.BUY)],
                             Settlement(9.0, "M", 0.0)))
    assert isinstance(evs[0], Book) and isinstance(evs[1], Trade) and isinstance(evs[2], Settlement)


class FakeKalshi:
    def __init__(self):
        self.calls = []

    async def get_historical_cutoff(self):
        return {"cutoff_ts": 1792152000}

    async def get_markets(self, **kw):
        self.calls.append(("markets", kw))
        return {"markets": [{"ticker": "S-1", "series_ticker": "S", "open_time": 1792152000,
                             "close_time": 1792152600, "result": "no"}], "cursor": ""}

    async def get_candlesticks(self, series, ticker, start, end, period):
        self.calls.append(("candles", series, ticker, start, end, period))
        return {"candlesticks": [
            {"end_period_ts": 1792152060, "yes_bid": {"close": 45}, "yes_ask": {"close": 47}, "volume": 10},
            {"end_period_ts": 1792152120, "yes_bid": {"close": "0.46"}, "yes_ask": {"close": "0.48"}, "volume_fp": "50"},
        ]}

    async def get_trades(self, **kw):
        self.calls.append(("trades", kw))
        return {"trades": [{"yes_price": 47, "count": 3, "taker_side": "yes", "created_time": 1792152090}],
                "cursor": ""}


async def test_kalshi_history_low_fidelity():
    c = FakeKalshi()
    h = await L.kalshi_history("S", 1792152000, 1792153000, c)
    assert h.low_fidelity is True
    assert [m.market_id for m in h.markets] == ["S-1"]
    evs = list(h.events)
    assert [type(e).__name__ for e in evs] == ["Book", "Trade", "Book", "Settlement"]
    assert evs[0].bids[0].price == 0.45 and evs[0].bids[0].size == 2.0
    assert evs[2].asks[0].price == 0.48 and evs[2].asks[0].size == 10.0
    assert evs[1].price == 0.47 and evs[-1].result == 0.0
    cfg = SimConfig(maker_requires_through=h.low_fidelity)
    assert cfg.maker_requires_through
    assert any(k[0] == "markets" and k[1]["series_ticker"] == "S" for k in c.calls)


class FakePoly:
    async def get_prices_history(self, token_id, **kw):
        return [{"t": 1792152000, "p": 0.45}, {"t": 1792152060, "p": 0.46}]

    async def iter_trades(self, cond, **kw):
        return [{"side": "BUY", "price": 0.46, "size": 5, "timestamp": 1792152030, "asset": "111"},
                {"side": "BUY", "price": 0.55, "size": 2, "timestamp": 1792152040, "asset": "222"}]


async def test_polymarket_history():
    m = Market(venue=Venue.POLYMARKET, market_id="111", meta={"condition_id": "0xabc", "no_token": "222"},
               result=1.0, close_ts=1792153000)
    h = await L.polymarket_history("111", 1792151000, 1792154000, FakePoly(), market=m)
    evs = list(h.events)
    assert h.low_fidelity
    kinds = [type(e).__name__ for e in evs]
    assert kinds == ["Book", "Trade", "Trade", "Book", "Settlement"]
    assert evs[0].best_bid == pytest.approx(0.445) and evs[0].best_ask == pytest.approx(0.455)
    assert evs[0].bids[0].size == pytest.approx(7 / 5)  # volume in bucket 0 = 5+2
    assert evs[2].price == pytest.approx(0.45) and evs[2].taker_action is Action.SELL  # NO trade mirrored


def test_jon_becker_loader(tmp_path):
    import pyarrow as pa

    mk = pa.table({"condition_id": ["0x1"], "question": ["Q?"], "clob_token_ids": ['["y1", "n1"]'],
                   "end_date": ["2026-10-17T00:00:00Z"], "outcome": ["Yes"], "category": ["Sports"]})
    tr = pa.table({"timestamp": [1792152000, 1792152010], "asset_id": ["y1", "n1"],
                   "price": [0.6, 0.45], "size": [10.0, 3.0], "side": ["BUY", "SELL"]})
    pq.write_table(mk, tmp_path / "markets.parquet")
    pq.write_table(tr, tmp_path / "trades.parquet")
    h = L.load_jon_becker(tmp_path / "markets.parquet", tmp_path / "trades.parquet")
    assert h.markets[0].market_id == "y1" and h.markets[0].series == "sports"
    evs = list(h.events)
    trades = [e for e in evs if isinstance(e, Trade)]
    assert trades[0].price == 0.6 and trades[1].price == pytest.approx(0.55) and trades[1].taker_action is Action.BUY
    assert isinstance(evs[-1], Settlement) and evs[-1].result == 1.0
    cmds = L.download_jon_becker("data/raw/jb")
    assert any("curl" in c for c in cmds)


# ----------------------------------------------------------------------------
# Paper runner
# ----------------------------------------------------------------------------
class BuyOnce(Strategy):
    name = "buy_once"

    def __init__(self):
        self.done = False

    def on_book(self, api, b):
        if not self.done:
            self.done = True
            api.place(Order(b.market_id, Action.BUY, 0.60, 500, tif=TIF.IOC, strategy=self.name))


async def test_paper_runner_fills_obey_liquidity_and_logs_ledger(tmp_path):
    now = [1792152000.0]
    m = Market(venue=Venue.KALSHI, market_id="M")
    feed = FakeFeed([mkbook(now[0], asks=((0.47, 8), (0.49, 2), (0.70, 1000)))])
    cfg = PaperConfig(run_id="t1", duration=0.3, heartbeat=0.01, summary_secs=0.05, poll_secs=10,
                      ledger_root=tmp_path, sim=SimConfig(order_latency=0.0))
    r = PaperRunner([m], lambda mid: KALSHI_DEFAULT, [BuyOnce()], feeds=[feed], config=cfg,
                    clock=lambda: now[0])
    summary = await r.run()
    assert summary["contracts_traded"] == 10  # only 10 within 5c of touch at <= 0.60
    assert summary["fills"] == 2 and summary["taker_fills"] == 2
    led = Ledger("t1", tmp_path)
    fills = led.load_fills()
    assert len(fills) == 2 and fills[0].price == 0.47 and fills[1].price == 0.49
    assert (tmp_path / "t1.summary.json").exists()
    lines = [json.loads(l) for l in (tmp_path / "t1.jsonl").read_text().splitlines()]
    assert lines[0]["type"] == "start" and lines[-1]["type"] == "stop"

    # resume: positions restored from ledger, no new fills
    r2 = PaperRunner([m], lambda mid: KALSHI_DEFAULT, [], feeds=[], config=cfg, clock=lambda: now[0])
    r2._resume()
    assert r2.engine.positions["M"].contracts == 10
    assert r2.engine.positions["M"].avg_price == pytest.approx((8 * 0.47 + 2 * 0.49) / 10)


async def test_paper_runner_polls_and_handles_settlement(tmp_path):
    now = [500.0]
    polled = []

    async def poll():
        polled.append(1)
        return mkbook(now[0])

    async def check(mid):
        return Market(venue=Venue.KALSHI, market_id=mid, result=1.0)

    m = Market(venue=Venue.KALSHI, market_id="M", close_ts=100.0)
    cfg = PaperConfig(run_id="t2", duration=0.1, heartbeat=0.01, poll_secs=0.01, ledger_root=tmp_path,
                      summary_secs=100)
    r = PaperRunner([m], lambda mid: KALSHI_DEFAULT, [], pollers={"M": poll}, settlement_checker=check,
                    config=cfg, clock=lambda: now[0])
    await r.run()
    assert polled and r.engine.books["M"].best_bid == 0.45
    # settlement path exercised synchronously
    r.process(Settlement(ts=now[0], market_id="M", result=1.0))
    assert r.engine.settled["M"] == 1.0


def test_process_clamps_bad_timestamps(tmp_path):
    now = [1000.0]
    r = PaperRunner([Market(venue=Venue.KALSHI, market_id="M")], lambda mid: KALSHI_DEFAULT, [],
                    config=PaperConfig(run_id="t3", ledger_root=tmp_path), clock=lambda: now[0])
    r.engine.now = 999.0
    r.process(mkbook(5000.0))  # far future -> clamped to now
    assert r.engine.books["M"].ts == 1000.0
    r.process(mkbook(1.0))     # far past -> clamped
    assert r.engine.books["M"].ts == 1000.0


def test_build_strategy_from_registry_and_yaml(tmp_path):
    from pb.live.paper import _import_all_strategies
    from pb.strategies.base import REGISTRY

    import dataclasses
    _import_all_strategies()
    # any registered strategy whose params dataclass has a `size` field (registry order
    # depends on test-collection import order, so don't rely on the first entry)
    name = next(n for n, c in REGISTRY.items()
                if any(f.name == "size" for f in dataclasses.fields(build_strategy(n, {}, ["M"]).p)))
    s = build_strategy(name, {}, ["M"])
    assert isinstance(s, Strategy)
    with pytest.raises(KeyError):
        build_strategy("does_not_exist")
    y = tmp_path / "p.yaml"
    y.write_text(f"{name}:\n  size: 7\n")
    params = load_params_yaml(y, name)
    assert params == {"size": 7}
    s2 = build_strategy(name, params, ["M"])
    assert getattr(getattr(s2, "p", None), "size", 7) == 7
    with pytest.raises(KeyError):
        build_strategy(name, {"not_a_param": 1})
    assert load_params_yaml(None) == {}


class RestAsk(Strategy):
    """Rests one ask at 0.47 (joins the touch) and never requotes."""
    name = "rest_ask"

    def __init__(self):
        self.done = False

    def on_book(self, api, b):
        if not self.done:
            self.done = True
            api.place(Order(b.market_id, Action.SELL, 0.47, 5, strategy=self.name))


async def test_paper_runner_polls_trade_tape_so_maker_fills_come_from_prints(tmp_path):
    now = [1792152000.0]
    asked: list[float] = []

    async def poll():
        return mkbook(now[0])                      # 0.45 / 0.47 x 8, never crosses our ask

    async def tpoll(since):
        asked.append(since)
        # one new print per poll, and the REST page repeats it (overlap at min_ts)
        ts = now[0] - 0.5 + 0.001 * len(asked)
        return [Trade(ts, "M", 0.47, 20, Action.BUY), Trade(ts, "M", 0.47, 20, Action.BUY)]

    m = Market(venue=Venue.KALSHI, market_id="M")
    cfg = PaperConfig(run_id="t-tape", duration=0.15, heartbeat=0.01, poll_secs=0.01, ledger_root=tmp_path,
                      summary_secs=100, sim=SimConfig(order_latency=0.0))
    r = PaperRunner([m], lambda mid: KALSHI_DEFAULT, [RestAsk()], pollers={"M": poll}, trade_pollers={"M": tpoll},
                    config=cfg, clock=lambda: now[0])
    summary = await r.run()
    assert asked and asked[0] == r.started_at
    # queue ahead (8) consumed, then our 5 filled by one print; the book never crossed us
    assert summary["fills"] == 1 and summary["maker_fills"] == 1 and summary["contracts_traded"] == 5
    assert summary["reality"]["cross_assumed_fills"] == 0
    assert r.engine.fill_context[0]["touch_depth"] == 20


def test_new_trades_dedupes_and_advances_watermark(tmp_path):
    r = PaperRunner([Market(venue=Venue.KALSHI, market_id="M")], lambda mid: KALSHI_DEFAULT, [],
                    config=PaperConfig(run_id="t-dd", ledger_root=tmp_path, risk=None), clock=lambda: 1000.0)
    r.started_at = 900.0
    a = Trade(950.0, "M", 0.5, 1, Action.BUY)
    b = Trade(951.0, "M", 0.5, 1, Action.SELL)
    assert [t.ts for t in r._new_trades("M", [b, a])] == [950.0, 951.0]
    assert r._trade_since["M"] == 951.0
    assert r._new_trades("M", [a, b]) == []                                  # overlap page
    c = Trade(951.0, "M", 0.5, 2, Action.SELL)                                # same second, different print
    assert r._new_trades("M", [b, c]) == [c]
    assert r._new_trades("M", [Trade(100.0, "M", 0.5, 1, Action.BUY)]) == []  # before the watermark
