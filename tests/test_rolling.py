"""Market rolling in the paper runner, strategy add/remove hooks, the
conservative risk mark, late WS subscription and the Polymarket window selector."""
import asyncio
import json

import httpx
import pytest
import respx

from pb.core.fees import KALSHI_DEFAULT
from pb.core.types import Action, Book, Level, Market, Order, TIF, Venue
from pb.live.paper import (PaperConfig, PaperRunner, build_strategy, crypto_window_slugs,
                           select_polymarket_crypto_windows)
from pb.live.risk import RiskLimits, RiskManager
from pb.sim.engine import Engine, Settlement, SimConfig, Strategy
from pb.venues import kalshi as K
from pb.venues import polymarket as P


def mkbook(ts, mid="M", bids=((0.45, 10), (0.44, 5)), asks=((0.47, 8),)):
    return Book(ts=ts, market_id=mid, bids=[Level(p, s) for p, s in bids], asks=[Level(p, s) for p, s in asks])


class Hooked(Strategy):
    """Rests a bid on every market it is told about; records the hooks."""
    name = "hooked"

    def __init__(self):
        self.added, self.removed, self.quoted = [], [], set()

    def on_market_added(self, api, m):
        self.added.append(m.market_id)

    def on_market_removed(self, api, mid):
        self.removed.append(mid)

    def on_book(self, api, b):
        if b.market_id not in self.quoted:
            self.quoted.add(b.market_id)
            api.place(Order(b.market_id, Action.BUY, 0.40, 5, tif=TIF.GTC, strategy=self.name))


class StubRecorder:
    def __init__(self):
        self.markets, self.events = [], []

    def on_market(self, m):
        self.markets.append(m.market_id)

    def on_event(self, ev):
        self.events.append(ev)


# ----------------------------------------------------------------------------
# Engine-level add / remove
# ----------------------------------------------------------------------------
def test_engine_add_remove_market_calls_hooks_and_drops_orders():
    e = Engine([Market(venue=Venue.KALSHI, market_id="A")], lambda m: KALSHI_DEFAULT,
               SimConfig(order_latency=0.0, cancel_latency=0.0))
    s = Hooked()
    e.add_strategy(s)
    assert e.add_market(Market(venue=Venue.KALSHI, market_id="B")) and not e.add_market(Market(venue=Venue.KALSHI, market_id="B"))
    assert s.added == ["B"] and "B" in e.markets
    e.now = 10.0
    e._dispatch(mkbook(10.0, "B"))
    e._advance(10.0)
    assert any(o.market_id == "B" for o in e.orders.values())
    assert e.remove_market("B") and not e.remove_market("B")
    assert s.removed == ["B"] and "B" not in e.markets and "B" not in e.books
    assert not any(o.market_id == "B" for o in e.orders.values())


# ----------------------------------------------------------------------------
# Runner rolling
# ----------------------------------------------------------------------------
async def test_paper_runner_rolls_in_new_markets_and_drops_settled(tmp_path):
    now = [1792152000.0]
    m1 = Market(venue=Venue.KALSHI, market_id="W1", close_ts=now[0] + 50)
    m2 = Market(venue=Venue.KALSHI, market_id="W2", close_ts=now[0] + 950)
    calls = {"select": 0, "wired": []}

    async def selector():
        calls["select"] += 1
        return [m1] if calls["select"] == 1 else [m1, m2]   # W2 gets listed on the second pass

    async def wiring(m):
        calls["wired"].append(m.market_id)
        r.pollers[m.market_id] = lambda mid=m.market_id: poll(mid)

    books = {"W1": 0, "W2": 0}

    async def poll(mid):
        books[mid] += 1
        return mkbook(now[0], mid)

    rec = StubRecorder()
    strat = Hooked()
    cfg = PaperConfig(run_id="roll", duration=0.5, heartbeat=0.01, poll_secs=0.02, roll_secs=0.05,
                      summary_secs=100, ledger_root=tmp_path, sim=SimConfig(order_latency=0.0, cancel_latency=0.0))
    r = PaperRunner([m1], lambda mid: KALSHI_DEFAULT, [strat], pollers={"W1": lambda: poll("W1")},
                    config=cfg, clock=lambda: now[0], recorder=rec, market_selector=selector, market_wiring=wiring)
    summary = await r.run()
    assert calls["select"] >= 2 and calls["wired"] == ["W2"]          # wired exactly once, before add
    assert strat.added == ["W2"] and rec.markets == ["W2"]            # strategy + recorder told
    assert books["W2"] > 0 and "W2" in strat.quoted                   # polled and quoted after the roll
    assert summary["markets"] == ["W1", "W2"] and set(summary["active_markets"]) == {"W1", "W2"}
    assert summary["rolls"] >= 2 and summary["last_roll"]["selected"] == 2
    recs = [json.loads(l) for l in (tmp_path / "roll.jsonl").read_text().splitlines()]
    assert [x["market_id"] for x in recs if x["type"] == "market_added"] == ["W2"]
    # settlement applied -> market dropped (orders gone, hooks fired, risk forgets it), position history kept
    r.process(Settlement(ts=now[0], market_id="W1", result=1.0))
    assert "W1" not in r.engine.markets and "W1" not in r.pollers and strat.removed == ["W1"]
    assert r.engine.settled["W1"] == 1.0 and [m.market_id for m in r.markets] == ["W2"]
    assert "W1" not in r.risk._last_book
    s2 = r.summary()
    assert s2["markets"] == ["W1", "W2"] and s2["active_markets"] == ["W2"]
    recs = [json.loads(l) for l in (tmp_path / "roll.jsonl").read_text().splitlines()]
    assert [x for x in recs if x["type"] == "market_removed"][-1]["market_id"] == "W1"
    # a settled market is never re-added by the selector
    calls["select"] = 5
    rep = await r.roll_markets()
    assert rep["added"] == [] and "W1" not in r.engine.markets


async def test_roll_drops_closed_unsettled_flat_markets_only(tmp_path):
    now = [1000.0]
    stale = Market(venue=Venue.KALSHI, market_id="OLD", close_ts=now[0] - 5000)
    held = Market(venue=Venue.KALSHI, market_id="HELD", close_ts=now[0] - 5000)
    cfg = PaperConfig(run_id="drop", ledger_root=tmp_path, roll_secs=1, drop_unsettled_after=3600, risk=None)

    async def selector():
        raise RuntimeError("venue down")

    r = PaperRunner([stale, held], lambda mid: KALSHI_DEFAULT, [], config=cfg, clock=lambda: now[0],
                    market_selector=selector)
    r.engine.positions["HELD"].apply(Action.BUY, 0.5, 3, 0.0)
    rep = await r.roll_markets()
    assert rep["error"].startswith("RuntimeError") and rep["dropped"] == ["OLD"]
    assert "HELD" in r.engine.markets and "OLD" not in r.engine.markets


# ----------------------------------------------------------------------------
# Strategy hooks
# ----------------------------------------------------------------------------
def _api_engine(markets):
    e = Engine(markets, lambda m: KALSHI_DEFAULT, SimConfig(order_latency=0.0, cancel_latency=0.0))
    e.now = 1792152000.0
    return e


def test_strategy_hooks_keep_market_filters_and_caches_in_sync():
    e = _api_engine([Market(venue=Venue.KALSHI, market_id="A", meta={"ladder_group": "NY"}, close_ts=2e9)])
    s = build_strategy("mm_weather_ladder", {}, ["A"])
    e.add_strategy(s)
    s.on_start(e.api)
    b = Market(venue=Venue.KALSHI, market_id="B", meta={"ladder_group": "NY"}, close_ts=2e9)
    assert e.add_market(b)
    assert s.markets == {"A", "B"} and s.groups["NY"] == {"A", "B"} and s.group_of["B"] == "NY"
    e.remove_market("B")
    assert s.markets == {"A"} and s.groups["NY"] == {"A"} and "B" not in s.group_of

    # crypto MM: window cache dropped on removal; taker_lag forwards to its model
    w = Market(venue=Venue.KALSHI, market_id="KXBTC15M-26OCT161930-30", series="KXBTC15M",
               open_ts=1792152000.0 - 900, close_ts=1792152000.0, meta={"window_open_ts": 1792152000.0 - 900,
               "window_close_ts": 1792152000.0, "window_secs": 900, "asset": "BTC"})
    e2 = _api_engine([])
    tl = build_strategy("taker_lag", {"size": 1}, [])
    e2.add_strategy(tl)
    tl.on_start(e2.api)
    e2.add_market(w)
    assert tl.model._window(e2.api, w.market_id) is not None and w.market_id in tl.model.windows
    e2.remove_market(w.market_id)
    assert w.market_id not in tl.model.windows and tl.markets == set()

    # complete_set_arb: event membership follows the market list
    e3 = _api_engine([])
    cs = build_strategy("complete_set_arb", {}, ["X"])
    e3.add_strategy(cs)
    cs.on_start(e3.api)
    e3.add_market(Market(venue=Venue.POLYMARKET, market_id="Y", event_id="ev"))
    assert cs.events["ev"] == {"Y"} and "Y" in cs.markets
    e3.remove_market("Y")
    assert "ev" not in cs.events and "Y" not in cs.markets

    # every registered strategy accepts both hooks (defaults or overrides)
    from pb.live.paper import _import_all_strategies
    from pb.strategies.base import REGISTRY

    _import_all_strategies()
    for name in REGISTRY:
        st = build_strategy(name, {}, ["A"])
        e4 = _api_engine([Market(venue=Venue.KALSHI, market_id="A")])
        e4.add_strategy(st)
        st.on_start(e4.api)
        e4.add_market(Market(venue=Venue.KALSHI, market_id="Z", close_ts=2e9))
        e4.remove_market("Z")
        assert "Z" not in getattr(st, "markets", set()), name


# ----------------------------------------------------------------------------
# Conservative risk mark
# ----------------------------------------------------------------------------
def test_risk_daily_loss_marks_at_conservative_side(tmp_path):
    now = [1000.0]
    e = Engine([Market(venue=Venue.KALSHI, market_id="A"), Market(venue=Venue.KALSHI, market_id="B")],
               lambda m: KALSHI_DEFAULT, SimConfig(order_latency=0.0, cancel_latency=0.0))
    e.now = now[0]
    rm = RiskManager(e, RiskLimits(daily_loss_limit=5.0, kill_file=str(tmp_path / "KILL")),
                     clock=lambda: now[0]).install()
    # long 100 @ 0.50; book 0.44 / 0.56: mid says flat, bid says -6
    e.positions["A"].apply(Action.BUY, 0.50, 100, 0.0)
    e.books["A"] = mkbook(now[0], "A", bids=((0.44, 50),), asks=((0.56, 50),))
    assert e.equity() == pytest.approx(0.0)
    assert rm.mark_conservative("A") == 0.44 and rm.pnl_today() == pytest.approx(-6.0)
    rm.check()
    assert rm.state.halted and rm.state.halt_reason.startswith("daily_loss")
    # short side marks at the ask
    e.positions["B"].apply(Action.SELL, 0.50, 10, 0.0)
    e.books["B"] = mkbook(now[0], "B", bids=((0.40, 5),), asks=((0.58, 5),))
    assert rm.mark_conservative("B") == 0.58
    # one-sided book -> engine mark (the one side); settled -> result
    e.books["B"] = mkbook(now[0], "B", bids=(), asks=((0.58, 5),))
    assert rm.mark_conservative("B") == e.mark("B") == 0.58
    e.settled["A"] = 1.0
    assert rm.mark_conservative("A") == 1.0
    rm.forget_market("A")
    assert "A" not in rm._last_book


# ----------------------------------------------------------------------------
# Late WS subscription
# ----------------------------------------------------------------------------
class FakeSock:
    def __init__(self):
        self.sent = []

    async def send(self, s):
        self.sent.append(json.loads(s))

    async def close(self):
        pass


async def test_ws_subscribe_more_sends_and_remembers():
    ws = K.KalshiWS(["A"], channels=("orderbook_delta",))
    ws._sock = FakeSock()
    assert await ws.subscribe_more(["A", "B"]) == ["B"]
    assert ws.tickers == ["A", "B"] and "B" in ws.books
    assert ws._sock.sent[-1]["params"]["market_tickers"] == ["B"]
    assert ws.subscribe_payload()["params"]["market_tickers"] == ["A", "B"]   # reconnect resubscribes both
    pw = P.PolymarketWS(["1"])
    pw._sock = FakeSock()
    assert await pw.subscribe_more(["2"], no_tokens={"3": "2"}) == ["2", "3"]
    assert pw._sock.sent[-1] == {"assets_ids": ["2", "3"], "type": "market"}
    assert pw.books["3"].is_no and set(pw.subscribe_payload()["assets_ids"]) == {"1", "2", "3"}


# ----------------------------------------------------------------------------
# Polymarket 5/15-min selector
# ----------------------------------------------------------------------------
def test_crypto_window_slugs_align_to_window():
    now = 1792152000.0 + 400           # 6:40 into a 15-min window
    s = crypto_window_slugs(now, assets=("btc",), minutes=(15,), lookahead=1)
    assert s == ["btc-updown-15m-1792152000", "btc-updown-15m-1792152900"]
    s5 = crypto_window_slugs(now, assets=("eth",), minutes=(5,), lookahead=0)
    assert s5 == ["eth-updown-5m-1792152300"]


def _gamma_window(slug, yes, no, vol=100.0):
    from datetime import datetime, timezone
    n, epoch = int(slug.split("-")[2][:-1]), int(slug.split("-")[3])
    end = datetime.fromtimestamp(epoch + n * 60, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"id": "9" + yes, "question": "Bitcoin Up or Down", "conditionId": "0x" + yes, "slug": slug,
            "endDate": end, "outcomes": "[\"Up\", \"Down\"]",
            "clobTokenIds": json.dumps([yes, no]), "volume24hr": vol, "active": True, "closed": False,
            "tags": [{"label": "Crypto", "slug": "crypto"}]}


@respx.mock
async def test_select_polymarket_crypto_windows_by_slug():
    now = 1792152000.0 + 100                      # 2026-10-16T12:01:40Z; current 15m window opened at 12:00
    cur, nxt = f"btc-updown-15m-{1792152000}", f"btc-updown-15m-{1792152900}"

    def events(request):
        slug = request.url.params["slug"]
        if slug == cur:
            ev = {"id": "e1", "slug": slug, "markets": [_gamma_window(slug, "111", "222", 500.0)]}
            return httpx.Response(200, json=[ev])
        return httpx.Response(200, json=[])

    def markets(request):
        slug = request.url.params.get("slug")
        if slug == nxt:
            return httpx.Response(200, json=[_gamma_window(slug, "333", "444", 1.0)])
        return httpx.Response(200, json=[])

    respx.get(f"{P.GAMMA_BASE}/events").mock(side_effect=events)
    respx.get(f"{P.GAMMA_BASE}/markets").mock(side_effect=markets)
    async with P.PolymarketClient() as c:
        ms = await select_polymarket_crypto_windows(c, top=2, assets=("btc",), minutes=(15,), lookahead=2, now=now)
    assert [m.market_id for m in ms] == ["111", "333"]            # soonest close first, not by volume
    assert ms[0].meta["window_open_ts"] == 1792152000.0 and ms[0].meta["window_close_ts"] == 1792152900.0
    assert ms[0].event_id == "e1" and ms[1].meta["asset"] == "BTC" and ms[1].meta["slug"] == nxt
    # a window closing within min_secs_to_close is skipped
    async with P.PolymarketClient() as c:
        ms = await select_polymarket_crypto_windows(c, top=2, assets=("btc",), minutes=(15,), lookahead=2,
                                                    now=1792152900.0 - 30)
    assert [m.market_id for m in ms] == ["333"]


@respx.mock
async def test_select_polymarket_crypto_windows_falls_back_to_scan(caplog):
    respx.get(f"{P.GAMMA_BASE}/events").mock(return_value=httpx.Response(200, json=[]))

    def markets(request):
        if request.url.params.get("slug"):
            return httpx.Response(200, json=[])
        assert request.url.params["order"] in ("startDate", "volume24hr")
        return httpx.Response(200, json=[_gamma_window("eth-updown-5m-1792152600", "555", "666"),
                                         {"id": "1", "slug": "btc-110k", "clobTokenIds": "[\"7\",\"8\"]",
                                          "endDate": "2026-10-17T12:00:00Z"}])

    respx.get(f"{P.GAMMA_BASE}/markets").mock(side_effect=markets)
    import logging
    with caplog.at_level(logging.INFO, logger="pb.live.paper"):
        async with P.PolymarketClient() as c:
            ms = await select_polymarket_crypto_windows(c, top=3, now=1792152000.0)
    assert [m.market_id for m in ms] == ["555"] and ms[0].meta["window_secs"] == 300.0
    assert "0 hits" in caplog.text and "scan order=startDate" in caplog.text
    # nothing anywhere -> empty, no exception
    respx.get(f"{P.GAMMA_BASE}/markets").mock(return_value=httpx.Response(200, json=[]))
    async with P.PolymarketClient() as c:
        assert await select_polymarket_crypto_windows(c, now=1792152000.0) == []
