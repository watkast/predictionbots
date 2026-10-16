"""Integration-layer pieces: signal fan-in, recorded-signal replay, venue meta
population, OddsLink matcher, RiskManager, paper runner wiring, CLI helpers."""
import asyncio
import json

import pyarrow.parquet as pq
import pytest

from pb.core.fees import KALSHI_DEFAULT
from pb.core.types import Action, Book, Level, Market, Order, TIF, Venue
from pb.data import feeds as F
from pb.data import loaders as L
from pb.data import odds_link as OL
from pb.data.recorder import Recorder
from pb.live.paper import (PaperConfig, PaperRunner, build_signal_feeds, parse_signal_specs)
from pb.live.risk import RiskLimits, RiskManager
from pb.sim.engine import Engine, Signal, SimConfig, Strategy
from pb.venues import kalshi as K
from pb.venues import polymarket as P


def mkbook(ts, mid="M", bids=((0.45, 10), (0.44, 5)), asks=((0.47, 8),)):
    return Book(ts=ts, market_id=mid, bids=[Level(p, s) for p, s in bids], asks=[Level(p, s) for p, s in asks])


async def agen(items, delay=0.0):
    for it in items:
        if delay:
            await asyncio.sleep(delay)
        yield it


# ----------------------------------------------------------------------------
# merge_signals fan-in
# ----------------------------------------------------------------------------
async def test_merge_signals_fans_in_and_survives_a_failing_feed():
    a = agen([Signal(1, "btc_index", None, 1.0), Signal(3, "btc_index", None, 3.0)], delay=0.005)
    b = agen([Signal(2, "twap60", None, {"asset": "BTC", "twap": 2.0})], delay=0.008)

    async def bad():
        yield Signal(0, "x", None, 0)
        raise RuntimeError("boom")

    got = [s async for s in F.merge_signals(a, b, bad())]
    names = sorted(s.name for s in got)
    assert names == ["btc_index", "btc_index", "twap60", "x"]


async def test_merge_signals_raise_mode():
    async def bad():
        raise ValueError("nope")
        yield  # pragma: no cover

    with pytest.raises(ValueError):
        async for _ in F.merge_signals(bad(), on_error="raise"):
            pass


# ----------------------------------------------------------------------------
# recorder persists signals + meta_json; loader replays them
# ----------------------------------------------------------------------------
async def test_recorder_signals_roundtrip_through_loader(tmp_path):
    now = 1792152000.0
    m = Market(venue=Venue.KALSHI, market_id="KXBTC15M-26OCT161315-T100000", series="KXBTC15M",
               close_ts=now + 900, meta={"window_open_ts": now, "window_close_ts": now + 900, "asset": "BTC",
                                         "floor_strike": 100000.0, "status": "open", "volume": 5.0})
    sigs = agen([Signal(now + 1, "btc_index", None, {"price": 100100.0, "size": 0.1, "src": "coinbase"}),
                 Signal(now + 2, "fcst_prob", m.market_id, 0.42),
                 Signal(now + 3, "fcst_prob", "OTHER", 0.9)])
    rec = Recorder("kalshi", [m], tmp_path, signals=sigs, flush_secs=100, max_seconds=0.05, clock=lambda: now)
    rec.on_book(mkbook(now + 0.5, m.market_id))
    stats = await rec.run()
    assert stats.signals == 3
    sig_files = list((tmp_path / "kalshi").rglob("signals-*.parquet"))
    assert len(sig_files) == 1
    rows = pq.read_table(sig_files[0]).to_pylist()
    assert rows[0]["name"] == "btc_index" and json.loads(rows[0]["value_json"])["price"] == 100100.0
    assert rows[0]["market_id"] is None and rows[1]["market_id"] == m.market_id

    markets, events = L.load_recorded(str(tmp_path / "kalshi"))
    evs = list(events)
    assert [type(e).__name__ for e in evs] == ["Book", "Signal", "Signal", "Signal"]
    assert evs[1].value == {"price": 100100.0, "size": 0.1, "src": "coinbase"} and evs[1].market_id is None
    assert evs[2].value == 0.42
    # meta_json restored
    mk = markets[0]
    assert mk.meta["window_open_ts"] == now and mk.meta["asset"] == "BTC" and mk.meta["floor_strike"] == 100000.0
    assert "volume" not in mk.meta  # not a persisted key
    # market filter keeps global signals, drops other markets' signals
    _, ev2 = L.load_recorded(str(tmp_path / "kalshi"), markets=[m.market_id])
    names = [(e.name, e.market_id) for e in ev2 if isinstance(e, Signal)]
    assert names == [("btc_index", None), ("fcst_prob", m.market_id)]
    # signals=False drops them entirely
    _, ev3 = L.load_recorded(str(tmp_path / "kalshi"), signals=False)
    assert all(not isinstance(e, Signal) for e in ev3)


def test_backtest_replays_recorded_signals(tmp_path):
    from pb.sim.backtest import DataSpec, load_data

    now = 1000.0
    m = Market(venue=Venue.KALSHI, market_id="M", meta={"status": "open"})
    rec = Recorder("kalshi", [m], tmp_path, flush_secs=100, clock=lambda: now)
    rec.on_book(mkbook(now))
    rec.on_signal(Signal(now + 1, "btc_index", None, 5.0))
    rec.flush()
    _, evs, _ = load_data(DataSpec(kind="recorded", path=str(tmp_path / "kalshi")))
    assert any(isinstance(e, Signal) and e.value == 5.0 for e in evs)
    _, evs2, _ = load_data(DataSpec(kind="recorded", path=str(tmp_path / "kalshi"), recorded_signals=False,
                                    signals=[Signal(now + 2, "btc_index", None, 7.0)]))
    vals = [e.value for e in evs2 if isinstance(e, Signal)]
    assert vals == [7.0]


# ----------------------------------------------------------------------------
# venue adapters populate strategy-facing meta
# ----------------------------------------------------------------------------
def test_kalshi_to_market_populates_window_strikes_ladder_and_flags():
    j = {"ticker": "KXBTC15M-26OCT161315-T100000", "event_ticker": "KXBTC15M-26OCT161315",
         "series_ticker": "KXBTC15M", "close_time": "2026-10-16T17:15:00Z", "floor_strike": "100000",
         "category": "Crypto", "fee_type": "quadratic", "status": "open"}
    m = K.to_market(j)
    w = F.KalshiCryptoWindow.from_market(m)
    assert m.meta["window_close_ts"] == w.close_ts and m.meta["window_open_ts"] == w.close_ts - 900
    assert m.meta["window_secs"] == 900 and m.meta["asset"] == "BTC"
    assert m.meta["floor_strike"] == 100000.0 and "cap_strike" not in m.meta
    assert m.meta["category"] == "crypto" and m.meta["fee_type"] == "quadratic"
    assert "ladder_group" not in m.meta

    j2 = {"ticker": "KXHIGHNY-26OCT16-B72", "event_ticker": "KXHIGHNY-26OCT16", "series_ticker": "KXHIGHNY",
          "floor_strike": 72, "cap_strike": 73, "subtitle": "72° to 73°", "close_time": "2026-10-17T04:00:00Z"}
    m2 = K.to_market(j2)
    assert m2.meta["ladder_group"] == "KXHIGHNY-26OCT16"
    assert F.parse_rung(m2) == (72.0, 73.0)
    assert "window_open_ts" not in m2.meta

    # series / event enrichment
    K.enrich_markets_with_series([m2], {"series": {"ticker": "KXHIGHNY", "fee_type": "quadratic_with_maker",
                                                   "category": "Climate and Weather"}})
    assert m2.meta["fee_type"] == "quadratic_with_maker" and m2.meta["category"] == "climate and weather"
    K.enrich_markets_with_event([m2, m], {"event": {"event_ticker": "KXHIGHNY-26OCT16", "mutually_exclusive": True}})
    assert m2.meta["mutually_exclusive"] is True and "mutually_exclusive" not in m.meta
    from pb.sim.backtest import default_fee_for

    assert default_fee_for([m2])(m2.market_id).maker_rate > 0


async def test_kalshi_client_enrich_uses_series_and_event(monkeypatch):
    c = K.KalshiClient()
    calls = []

    async def get_series(st):
        calls.append(("s", st))
        return {"ticker": st, "fee_type": "quadratic_with_maker", "category": "Sports"}

    async def get_event(ev):
        calls.append(("e", ev))
        return {"event_ticker": ev, "mutually_exclusive": True}

    monkeypatch.setattr(c, "get_series", get_series)
    monkeypatch.setattr(c, "get_event", get_event)
    ms = [Market(venue=Venue.KALSHI, market_id="KXNFLGAME-26OCT19DALWAS-DAL", series="KXNFLGAME",
                 event_id="KXNFLGAME-26OCT19DALWAS"),
          Market(venue=Venue.KALSHI, market_id="KXNFLGAME-26OCT19DALWAS-WAS", series="KXNFLGAME",
                 event_id="KXNFLGAME-26OCT19DALWAS")]
    await c.enrich(ms)
    assert calls == [("s", "KXNFLGAME"), ("e", "KXNFLGAME-26OCT19DALWAS")]
    assert all(m.meta["mutually_exclusive"] and m.meta["fee_type"] == "quadratic_with_maker" for m in ms)
    await c.aclose()


def test_polymarket_crypto_window_and_neg_risk():
    j = {"question": "Bitcoin Up or Down - October 16, 1:00PM-1:15PM ET", "slug": "btc-updown-15m-1792152000",
         "clobTokenIds": ["1", "2"], "endDate": "2026-10-16T17:15:00Z", "negRisk": False,
         "tags": [{"label": "Crypto"}]}
    m = P.to_market(j)
    assert m.meta["window_open_ts"] == 1792152000.0 and m.meta["window_close_ts"] == 1792152900.0
    assert m.meta["asset"] == "BTC" and m.meta["window_secs"] == 900
    assert F.KalshiCryptoWindow.from_market(m).source == "meta"
    assert "mutually_exclusive" not in m.meta
    # title-only fallback (no slug convention)
    j2 = dict(j, slug="whatever-15m")
    m2 = P.to_market(j2)
    assert m2.meta["window_open_ts"] == m2.close_ts - 900 and m2.meta["asset"] == "BTC"
    assert P.crypto_window_from_slug("eth-updown-5m-1792152000")["window_secs"] == 300
    assert P.crypto_window_from_slug("will-x-happen") is None
    m3 = P.to_market({"question": "Who wins?", "clobTokenIds": ["5", "6"], "negRisk": True})
    assert m3.meta["mutually_exclusive"] is True and "window_open_ts" not in m3.meta


# ----------------------------------------------------------------------------
# OddsLink matcher
# ----------------------------------------------------------------------------
def test_normalize_team_aliases():
    assert OL.normalize_team("DAL", "nfl") == "Dallas Cowboys"
    assert OL.normalize_team("DAL", "nba") == "Dallas Mavericks"
    assert OL.normalize_team("DAL") is None            # ambiguous across leagues
    assert OL.normalize_team("Cowboys") == "Dallas Cowboys"
    assert OL.normalize_team("Dallas Cowboys (-3.5)") == "Dallas Cowboys"
    assert OL.normalize_team("LA Rams") == "Los Angeles Rams"
    assert OL.normalize_team("Oakland Raiders") == "Las Vegas Raiders"
    assert OL.normalize_team("Washington Football Team") == "Washington Commanders"
    assert OL.normalize_team("Chicago") is None        # two Chicago teams in several leagues
    assert OL.normalize_team("Green Bay") == "Green Bay Packers"
    assert OL.normalize_team("Sox") is None and OL.normalize_team("Red Sox") == "Boston Red Sox"
    assert OL.normalize_team("Blue Jays") == "Toronto Blue Jays"
    assert OL.normalize_team("TB", "nhl") == "Tampa Bay Lightning"
    assert OL.normalize_team("Habs") == "Montreal Canadiens"
    assert OL.normalize_team("") is None
    assert OL.team_eq("Dallas Cowboys", "DAL", "nfl") and not OL.team_eq("Cowboys", "Commanders")


def test_parse_kalshi_sports_ticker():
    g = OL.parse_kalshi_sports_ticker("KXNFLGAME-26OCT19DALWAS-DAL")
    assert g.sport == "nfl" and g.date == "2026-10-19"
    assert g.away == "Dallas Cowboys" and g.home == "Washington Commanders" and g.outcome == "Dallas Cowboys"
    g2 = OL.parse_kalshi_sports_ticker("KXNBAGAME-26OCT22LALGSW-GSW")
    assert g2.sport == "nba" and g2.home == "Golden State Warriors" and g2.outcome == "Golden State Warriors"
    g3 = OL.parse_kalshi_sports_ticker("KXMLBGAME-26OCT20NYYLAD-NYY")
    assert g3.away == "New York Yankees" and g3.home == "Los Angeles Dodgers"
    g4 = OL.parse_kalshi_sports_ticker("KXNHLGAME-26OCT20TORMTL-MTL")
    assert g4.sport == "nhl" and g4.outcome == "Montreal Canadiens"
    # 2-letter code at the front
    g5 = OL.parse_kalshi_sports_ticker("KXNFLGAME-26OCT19KCBUF-KC")
    assert g5.away == "Kansas City Chiefs" and g5.home == "Buffalo Bills"
    assert OL.parse_kalshi_sports_ticker("KXNFLGAME-26OCT19DALWAS-TIE").outcome == ""
    assert OL.parse_kalshi_sports_ticker("KXBTC15M-26OCT161315-T100000") is None
    assert OL.parse_kalshi_sports_ticker("KXHIGHNY-26OCT16-B72") is None
    assert OL.parse_kalshi_sports_ticker("") is None


def test_parse_polymarket_question():
    assert OL.parse_polymarket_question("Cowboys vs. Commanders", ["Cowboys", "Commanders"]) == \
        ("Dallas Cowboys", "Washington Commanders", "Dallas Cowboys")
    assert OL.parse_polymarket_question("NFL: Dallas Cowboys @ Washington Commanders", ["Commanders", "Cowboys"]) == \
        ("Dallas Cowboys", "Washington Commanders", "Washington Commanders")
    assert OL.parse_polymarket_question("Will the Dallas Cowboys beat the Washington Commanders on October 19?",
                                        ["Yes", "No"]) == ("Dallas Cowboys", "Washington Commanders", "Dallas Cowboys")
    assert OL.parse_polymarket_question("Lakers vs Warriors", ["Lakers", "Warriors"])[2] == "Los Angeles Lakers"
    assert OL.parse_polymarket_question("Will Bitcoin hit 100k?", ["Yes", "No"]) is None


def test_build_links_against_odds_events():
    ev = [{"id": "e1", "home_team": "Washington Commanders", "away_team": "Dallas Cowboys",
           "commence_time": "2026-10-20T00:20:00Z"},
          {"id": "e2", "home_team": "Buffalo Bills", "away_team": "Kansas City Chiefs",
           "commence_time": "2026-10-19T20:25:00Z"}]
    ms = [Market(venue=Venue.KALSHI, market_id="KXNFLGAME-26OCT19DALWAS-DAL"),
          Market(venue=Venue.KALSHI, market_id="KXNFLGAME-26OCT19DALWAS-WAS"),
          Market(venue=Venue.KALSHI, market_id="KXNFLGAME-26OCT19KCBUF-BUF"),
          Market(venue=Venue.KALSHI, market_id="KXNFLGAME-26NOV19DALWAS-DAL"),      # wrong date
          Market(venue=Venue.POLYMARKET, market_id="tok", title="Cowboys vs. Commanders",
                 close_ts=1792454400.0, meta={"outcomes": ["Cowboys", "Commanders"]}),
          Market(venue=Venue.KALSHI, market_id="KXBTC15M-26OCT161315-T100000")]
    links = OL.build_links(ms, ev)
    by_id = {l.market_id: l for l in links}
    assert set(by_id) == {"KXNFLGAME-26OCT19DALWAS-DAL", "KXNFLGAME-26OCT19DALWAS-WAS",
                          "KXNFLGAME-26OCT19KCBUF-BUF", "tok"}
    assert by_id["KXNFLGAME-26OCT19DALWAS-DAL"].outcome == "Dallas Cowboys"
    assert by_id["KXNFLGAME-26OCT19DALWAS-WAS"].outcome == "Washington Commanders"
    assert by_id["tok"].home_team == "Washington Commanders" and by_id["tok"].outcome == "Dallas Cowboys"
    assert by_id["KXNFLGAME-26OCT19KCBUF-BUF"].sport == "nfl"
    # the links drive the existing odds-feed parser
    payload = [dict(ev[0], bookmakers=[{"key": "pinnacle", "markets": [{"key": "h2h", "outcomes": [
        {"name": "Dallas Cowboys", "price": 1.80}, {"name": "Washington Commanders", "price": 2.10}]}]}])]
    sigs = F.sharp_signals_from_odds(payload, links, now=1.0)
    sharp = {s.market_id: s.value["p"] for s in sigs if s.name == "sharp_prob"}
    assert sharp["KXNFLGAME-26OCT19DALWAS-DAL"] == pytest.approx(1 - sharp["KXNFLGAME-26OCT19DALWAS-WAS"])
    assert sharp["tok"] == pytest.approx(sharp["KXNFLGAME-26OCT19DALWAS-DAL"])
    # without events: links still built from the ticker alone
    assert len(OL.build_links(ms[:1])) == 1
    assert OL.sport_for_markets(ms) == "nfl"


# ----------------------------------------------------------------------------
# RiskManager
# ----------------------------------------------------------------------------
def _engine(now):
    e = Engine([Market(venue=Venue.KALSHI, market_id="A"), Market(venue=Venue.KALSHI, market_id="B")],
               lambda m: KALSHI_DEFAULT, SimConfig(order_latency=0.0, cancel_latency=0.0))
    e.now = now[0]
    return e


def _order(mid, price, size, action=Action.BUY):
    return Order(mid, action, price, size, tif=TIF.GTC, post_only=True)


def test_risk_capital_caps_and_rate_limit(tmp_path):
    now = [1000.0]
    e = _engine(now)
    rm = RiskManager(e, RiskLimits(max_capital_per_market=12.0, max_capital_total=20.0, max_orders_per_min=2,
                                   kill_file=str(tmp_path / "KILL")), clock=lambda: now[0]).install()
    assert e.submit(_order("A", 0.50, 10))                               # locks $5 (in flight)
    e.submit(_order("A", 0.50, 20))                                      # $10 more -> 15 > 12 market cap
    assert rm.state.reject_reasons == {"market_capital_cap": 1}
    e._advance(now[0])
    assert len(e.orders) == 1
    e.submit(_order("B", 0.50, 20))                                      # $10: total 15 -> ok
    e._advance(now[0])
    assert len(e.orders) == 2
    e.submit(_order("A", 0.50, 1))                                       # rate limit (2 accepted in a minute)
    assert rm.state.reject_reasons.get("rate_limit") == 1
    now[0] += 61
    e.submit(_order("A", 0.50, 10))                                      # A = 10, total = 20 -> ok
    e.submit(_order("B", 0.10, 1))                                       # total cap: 20 + 0.1
    assert rm.state.reject_reasons.get("total_capital_cap") == 1
    # a reducing order always passes the capital checks
    e.positions["A"].apply(Action.BUY, 0.5, 10, 0.0)
    e.submit(_order("A", 0.60, 10, Action.SELL))
    assert rm.state.accepted == 4
    st = rm.status()
    assert st["rejected"] == 3 and st["capital_in_use"] >= 20.0 and not st["halted"]


def test_risk_daily_loss_halts_and_cancels(tmp_path):
    now = [1000.0]
    e = _engine(now)
    rm = RiskManager(e, RiskLimits(daily_loss_limit=5.0, kill_file=str(tmp_path / "KILL")),
                     clock=lambda: now[0]).install()
    e.submit(_order("A", 0.40, 10))
    e._advance(now[0])
    assert len(e.orders) == 1
    e.positions["A"].realized = -6.0
    rm.check()
    e._advance(now[0])
    assert rm.state.halted and rm.state.halt_reason.startswith("daily_loss") and e.orders == {}
    e.submit(_order("A", 0.40, 10))
    assert rm.state.reject_reasons == {"halted": 1}
    # next day without auto_resume: still halted
    now[0] += 86400
    rm.check()
    assert rm.state.halted
    rm.limits.auto_resume = True
    now[0] += 86400
    rm.check()
    assert not rm.state.halted and rm.pnl_today() == 0.0


def test_risk_kill_file_and_stale_guard(tmp_path):
    now = [1000.0]
    e = _engine(now)
    kill = tmp_path / "KILL"
    rm = RiskManager(e, RiskLimits(stale_secs=30.0, kill_file=str(kill)), clock=lambda: now[0]).install()
    rm.on_event(mkbook(now[0], "A"))
    e.submit(_order("A", 0.40, 10))
    e._advance(now[0])
    now[0] += 31
    rm.check()
    e._advance(now[0])
    assert rm.state.stale and e.orders == {} and rm.state.cancel_all_count == 1
    assert e.submit(_order("A", 0.40, 10)) and rm.state.reject_reasons == {"stale_data": 1}
    rm.on_event(mkbook(now[0], "A"))
    assert not rm.state.stale
    e.submit(_order("A", 0.40, 10))
    assert rm.state.accepted == 2
    kill.write_text("stop")
    rm.check()
    e._advance(now[0])
    assert rm.state.halted and "kill_file" in rm.state.halt_reason and e.orders == {}
    assert rm.status()["kill_file_present"]
    kill.unlink()
    rm.check()
    assert rm.state.halted  # sticky
    rm.uninstall()
    assert e.submit is not rm.submit


class Quoter(Strategy):
    name = "quoter"

    def __init__(self):
        self.signals = []

    def on_book(self, api, b):
        if not api.open_orders(b.market_id):
            api.place(Order(b.market_id, Action.BUY, 0.40, 10, post_only=True, strategy=self.name))

    def on_signal(self, api, s):
        self.signals.append(s)


async def test_paper_runner_fans_in_signals_and_reports_risk(tmp_path):
    now = [1792152000.0]
    m = Market(venue=Venue.KALSHI, market_id="M")

    class Feed:
        def __init__(self, evs):
            self.evs = list(evs)

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.evs:
                await asyncio.sleep(0.001)
                return self.evs.pop(0)
            await asyncio.sleep(3600)
            raise StopAsyncIteration

    feed = Feed([mkbook(now[0])])
    s1 = Feed([Signal(now[0], "btc_index", None, 1.0)])
    s2 = Feed([Signal(now[0], "twap60", None, {"asset": "BTC", "twap": 2.0})])
    cfg = PaperConfig(run_id="t-sig", duration=0.2, heartbeat=0.01, summary_secs=100, poll_secs=10,
                      ledger_root=tmp_path, sim=SimConfig(order_latency=0.0),
                      risk=RiskLimits(kill_file=str(tmp_path / "KILL"), max_capital_total=3.0))
    q = Quoter()
    rec = Recorder("kalshi", [m], tmp_path / "rec", flush_secs=100, clock=lambda: now[0])
    r = PaperRunner([m], lambda mid: KALSHI_DEFAULT, [q], feeds=[feed], signals=[s1, s2], config=cfg,
                    clock=lambda: now[0], recorder=rec)
    summary = await r.run()
    assert sorted(s.name for s in q.signals) == ["btc_index", "twap60"]
    assert summary["risk"]["accepted"] == 0 and summary["risk"]["reject_reasons"] == {"total_capital_cap": 1}
    assert summary["strategies"] == ["quoter"] and summary["venue"] == "kalshi"
    rec.flush()
    assert rec.stats.signals == 2 and rec.stats.books == 1
    # no-risk config
    r2 = PaperRunner([m], lambda mid: KALSHI_DEFAULT, [], config=PaperConfig(run_id="t2", ledger_root=tmp_path, risk=None),
                     clock=lambda: now[0])
    assert r2.risk is None and r2.summary()["risk"] is None


# ----------------------------------------------------------------------------
# CLI signal specs
# ----------------------------------------------------------------------------
def test_parse_signal_specs():
    assert parse_signal_specs("coinbase,twap,openmeteo:40.78,-73.97,1.5,odds:nfl") == [
        ("coinbase", []), ("twap", []), ("openmeteo", ["40.78", "-73.97", "1.5"]), ("odds", ["nfl"])]
    assert parse_signal_specs("") == [] and parse_signal_specs(None) == []
    assert parse_signal_specs("open_meteo:1,2") == [("openmeteo", ["1", "2"])]


def test_build_signal_feeds_skips_without_key_and_links():
    nfl = Market(venue=Venue.KALSHI, market_id="KXNFLGAME-26OCT19DALWAS-DAL")
    feeds, notes = build_signal_feeds("odds,espn,bogus", [nfl], env={}, http_client=object())
    assert len(feeds) == 1 and any("ODDS_API_KEY" in n for n in notes) and any("bogus" in n for n in notes)
    feeds, notes = build_signal_feeds("odds", [nfl], env={"ODDS_API_KEY": "k"}, http_client=object())
    assert len(feeds) == 1 and notes == []
    feeds, notes = build_signal_feeds("odds:nfl", [Market(venue=Venue.KALSHI, market_id="KXBTC15M-26OCT161315-T1")],
                                      env={"ODDS_API_KEY": "k"}, http_client=object())
    assert feeds == [] and "linked" in notes[0]
    feeds, notes = build_signal_feeds("openmeteo", [], env={}, http_client=object())
    assert feeds == [] and "LAT,LON" in notes[0]
    rung = Market(venue=Venue.KALSHI, market_id="KXHIGHNY-26OCT16-B72", meta={"floor_strike": 72, "cap_strike": 73})
    feeds, notes = build_signal_feeds("openmeteo:40.78,-73.97,coinbase,twap", [rung], env={}, http_client=object())
    assert len(feeds) == 3 and notes == []
