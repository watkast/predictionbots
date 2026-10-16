"""Reference-feed parsers, de-vig, ticker parsing, mocked async producers."""
import asyncio
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from pb.core.types import Market, Venue
from pb.data import feeds as F
from pb.sim.engine import Signal


# ----------------------------------------------------------------------------
# KalshiCryptoWindow
# ----------------------------------------------------------------------------
def test_parse_ticker_15m_eastern():
    w = F.KalshiCryptoWindow.parse_ticker("KXBTC15M-26OCT161315-T100000")
    assert w.ok and w.asset == "BTC" and w.duration == 900
    assert w.close_ts == datetime(2026, 10, 16, 13, 15, tzinfo=ZoneInfo("America/New_York")).timestamp()
    assert w.open_ts == w.close_ts - 900
    assert w.strike_signal == "btc_index"


def test_parse_ticker_variants_and_garbage():
    assert F.KalshiCryptoWindow.parse_ticker("KXETH15M-26OCT161330").asset == "ETH"
    assert F.KalshiCryptoWindow.parse_ticker("kxbtc15m-26oct161315-abc").ok
    assert not F.KalshiCryptoWindow.parse_ticker("KXHIGHNY-26OCT16-B70").ok
    assert not F.KalshiCryptoWindow.parse_ticker("").ok
    assert not F.KalshiCryptoWindow.parse_ticker("KXBTC15M-26XXX161315").ok
    assert not F.KalshiCryptoWindow.parse_ticker(None).ok


def test_from_market_prefers_meta_then_ticker_then_close_ts():
    m = Market(venue=Venue.KALSHI, market_id="KXBTC15M-26OCT161315-T", close_ts=1_000_000.0,
               meta={"window_open_ts": 100.0, "window_close_ts": 1000.0})
    w = F.KalshiCryptoWindow.from_market(m)
    assert w.source == "meta" and w.open_ts == 100.0 and w.duration == 900
    m2 = Market(venue=Venue.KALSHI, market_id="KXBTC15M-26OCT161315-T")
    assert F.KalshiCryptoWindow.from_market(m2).source == "ticker"
    m3 = Market(venue=Venue.KALSHI, market_id="weird", series="KXETH15M", close_ts=5000.0)
    w3 = F.KalshiCryptoWindow.from_market(m3)
    assert w3.source == "close_ts" and w3.open_ts == 4100.0 and w3.asset == "ETH"
    # ticker far from venue close_ts -> venue wins
    m4 = Market(venue=Venue.KALSHI, market_id="KXBTC15M-26OCT161315-T", close_ts=123456.0)
    w4 = F.KalshiCryptoWindow.from_market(m4)
    assert w4.source == "close_ts" and w4.close_ts == 123456.0
    assert not F.KalshiCryptoWindow.from_market(Market(venue=Venue.KALSHI, market_id="X")).ok


# ----------------------------------------------------------------------------
# crypto parsers
# ----------------------------------------------------------------------------
def test_parse_coinbase_and_kraken():
    cb = {"channel": "market_trades", "events": [{"trades": [
        {"product_id": "BTC-USD", "price": "100123.5", "size": "0.01", "time": "2026-10-16T13:00:00Z"},
        {"product_id": "DOGE-USD", "price": "0.1", "size": "1", "time": "2026-10-16T13:00:00Z"}]}]}
    out = F.parse_coinbase_trade(cb)
    assert len(out) == 1 and out[0].name == "btc_index" and out[0].value["price"] == 100123.5
    assert F.signal_price(out[0]) == 100123.5
    kr = {"channel": "trade", "data": [{"symbol": "ETH/USD", "price": 4000.0, "qty": 1, "timestamp": "2026-10-16T13:00:00.000Z"}]}
    out = F.parse_kraken_trade(kr)
    assert out[0].name == "eth_index" and out[0].value["src"] == "kraken"
    assert F.parse_coinbase_trade({"channel": "heartbeats"}) == []


def test_parse_poly_twap_shapes():
    assert F.parse_poly_twap("PONG") == []
    msg = json.dumps({"topic": "crypto_prices_twap_sixty", "type": "update",
                      "payload": {"symbol": "BTCUSDT", "twap": 100000.0, "timestamp": 1760620000000}})
    out = F.parse_poly_twap(msg)
    assert out[0].name == "twap60" and out[0].value["asset"] == "BTC" and out[0].ts == 1760620000.0
    assert F.parse_poly_twap({"topic": "other", "payload": {}}) == []


async def test_coinbase_index_generator_with_mock_ws():
    sent = []

    class WS:
        def __init__(self, url): self.url = url
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
        async def send(self, m): sent.append(m)
        def __aiter__(self):
            async def gen():
                yield json.dumps({"channel": "subscriptions"})
                yield json.dumps({"channel": "market_trades", "events": [{"trades": [
                    {"product_id": "BTC-USD", "price": "1", "size": "1", "time": "2026-10-16T13:00:00Z"}]}]})
                raise asyncio.CancelledError
            return gen()

    got = []
    with pytest.raises(asyncio.CancelledError):
        async for s in F.coinbase_index(ws_factory=WS):
            got.append(s)
    assert len(got) == 1 and got[0].name == "btc_index"
    assert json.loads(sent[0])["channel"] == "market_trades"


# ----------------------------------------------------------------------------
# weather
# ----------------------------------------------------------------------------
def test_ensemble_rung_probs_sum_to_one_and_bias_shifts():
    members = [70 + (i % 7) for i in range(31)]   # 70..76
    rungs = [(None, 69), (70, 71), (72, 73), (74, 75), (76, None)]
    p = F.ensemble_rung_probs(members, rungs, spread_scale=1.0)
    assert sum(p) == pytest.approx(1.0, abs=0.03)
    assert p[2] > p[0]
    p_bias = F.ensemble_rung_probs(members, rungs, bias=4.0, spread_scale=1.0)
    assert p_bias[4] > p[4]
    assert all(x != x for x in F.ensemble_rung_probs([], rungs))


def test_parse_rung_from_meta_and_title():
    assert F.parse_rung(Market(venue=Venue.KALSHI, market_id="a", meta={"floor_strike": 70, "cap_strike": 71})) == (70.0, 71.0)
    assert F.parse_rung(Market(venue=Venue.KALSHI, market_id="a", title="72° to 73°")) == (72.0, 73.0)
    assert F.parse_rung(Market(venue=Venue.KALSHI, market_id="a", title="74° or above")) == (74.0, None)
    assert F.parse_rung(Market(venue=Venue.KALSHI, market_id="a", meta={"subtitle": "69° or below"})) == (None, 69.0)
    assert F.parse_rung(Market(venue=Venue.KALSHI, market_id="a", title="nothing")) is None


class _Resp:
    def __init__(self, data): self._d = data
    def json(self): return self._d


class _Client:
    def __init__(self, data): self.data = data; self.calls = []
    async def get(self, url, params=None, headers=None):
        self.calls.append((url, params, headers))
        return _Resp(self.data)


async def test_open_meteo_fcst_prob_emits_per_rung():
    daily = {"time": ["2026-10-16", "2026-10-17"], "temperature_2m_max": [72.0, 60.0]}
    for i in range(1, 11):
        daily[f"temperature_2m_max_member{i:02d}"] = [70.0 + i * 0.5, 60.0]
    ms = [Market(venue=Venue.KALSHI, market_id="R1", meta={"rung_lo": 70, "rung_hi": 72}),
          Market(venue=Venue.KALSHI, market_id="R2", meta={"rung_lo": 73, "rung_hi": 75}),
          Market(venue=Venue.KALSHI, market_id="R3", title="no rung here")]
    c = _Client({"daily": daily})
    out = [s async for s in F.open_meteo_fcst_prob(c, ms, 40.7, -74.0, once=True)]
    probs = {s.market_id: s.value for s in out if s.name == "fcst_prob"}
    assert set(probs) == {"R1", "R2"} and 0 < probs["R1"] < 1
    assert c.calls[0][1]["temperature_unit"] == "fahrenheit"
    assert any(s.name == "fcst_members" and s.value["n"] == 11 for s in out)


async def test_nws_observation_requires_user_agent_and_converts_c_to_f():
    c = _Client({"properties": {"timestamp": "2026-10-16T13:00:00+00:00",
                                "temperature": {"value": 20.0, "unitCode": "wmoUnit:degC"}}})
    ob = await F.nws_latest_observation(c, "KNYC")
    assert ob["temp_f"] == pytest.approx(68.0)
    assert "User-Agent" in c.calls[0][2]
    sigs = [s async for s in F.nws_observation_signal(c, "KNYC", once=True)]
    assert {s.name for s in sigs} == {"obs_temp_f", "obs_high_f"}


# ----------------------------------------------------------------------------
# odds / de-vig
# ----------------------------------------------------------------------------
def test_devig_methods():
    implied = [1 / 1.80, 1 / 2.10]   # 0.5556 + 0.4762 = 1.03
    m = F.devig_multiplicative(implied)
    p = F.devig_power(implied)
    assert sum(m) == pytest.approx(1.0) and sum(p) == pytest.approx(1.0, abs=1e-6)
    assert m[0] > m[1] and p[0] > p[1]
    # power method pushes more of the vig onto the longshot than multiplicative
    assert p[0] > m[0]
    assert F.american_to_prob(-150) == pytest.approx(0.6)
    assert F.american_to_prob(+200) == pytest.approx(1 / 3)
    assert F.devig_power([0.5, 0.5]) == pytest.approx([0.5, 0.5])


def test_sharp_signals_from_odds_pinnacle_first_then_consensus():
    ev = [{"home_team": "Kansas City Chiefs", "away_team": "Buffalo Bills", "commence_time": "2026-10-19T20:00:00Z",
           "bookmakers": [
               {"key": "pinnacle", "markets": [{"key": "h2h", "outcomes": [
                   {"name": "Kansas City Chiefs", "price": 1.80}, {"name": "Buffalo Bills", "price": 2.10}]}]},
               {"key": "draftkings", "markets": [{"key": "h2h", "outcomes": [
                   {"name": "Kansas City Chiefs", "price": 1.75}, {"name": "Buffalo Bills", "price": 2.15}]}]}]}]
    links = [F.OddsLink("KXNFL-KC", "Kansas City Chiefs", "Buffalo Bills", "Kansas City Chiefs")]
    out = F.sharp_signals_from_odds(ev, links, now=1.0)
    names = {s.name for s in out}
    assert {"sharp_prob", "book_prob_pinnacle", "book_prob_draftkings"} <= names
    sharp = next(s for s in out if s.name == "sharp_prob")
    pin = next(s for s in out if s.name == "book_prob_pinnacle")
    assert sharp.value["p"] == pytest.approx(pin.value) and sharp.market_id == "KXNFL-KC"
    # no pinnacle -> consensus mean
    ev[0]["bookmakers"] = ev[0]["bookmakers"][1:]
    out2 = F.sharp_signals_from_odds(ev, links, now=2.0)
    sharp2 = next(s for s in out2 if s.name == "sharp_prob")
    dk = next(s for s in out2 if s.name == "book_prob_draftkings")
    assert sharp2.value["p"] == pytest.approx(dk.value)
    # american odds also handled
    ev[0]["bookmakers"][0]["markets"][0]["outcomes"] = [{"name": "Kansas City Chiefs", "price": -150},
                                                        {"name": "Buffalo Bills", "price": 130}]
    out3 = F.sharp_signals_from_odds(ev, links, now=3.0)
    assert 0.5 < next(s for s in out3 if s.name == "sharp_prob").value["p"] < 0.7


async def test_odds_api_and_espn_generators_mocked():
    odds = [{"home_team": "A", "away_team": "B", "bookmakers": [{"key": "pinnacle", "markets": [{"key": "h2h", "outcomes": [
        {"name": "A", "price": 2.0}, {"name": "B", "price": 2.0}]}]}]}]
    links = [F.OddsLink("M-A", "A", "B", "A")]
    c = _Client(odds)
    out = [s async for s in F.odds_api_sharp_prob(c, "k", "americanfootball_nfl", links, once=True)]
    assert any(s.name == "sharp_prob" and abs(s.value["p"] - 0.5) < 1e-9 for s in out)
    assert c.calls[0][1]["apiKey"] == "k" and c.calls[0][1]["markets"] == "h2h"
    espn = {"events": [{"id": "1", "date": "2026-10-19T20:00Z", "competitions": [{
        "status": {"type": {"state": "in", "completed": False}, "period": 2, "displayClock": "3:00"},
        "competitors": [{"homeAway": "home", "team": {"displayName": "A"}}, {"homeAway": "away", "team": {"displayName": "B"}}]}]}]}
    out = [s async for s in F.espn_game_state(_Client(espn), "football/nfl", links, once=True)]
    assert out and out[0].name == "game_state" and out[0].value == "in" and out[0].market_id == "M-A"
    assert F.parse_espn_scoreboard(espn)["1"]["period"] == 2


def test_backtest_signal_helpers():
    rows = [{"ts": 2, "market_id": "", "value": 0.4}, {"ts": 1, "market_id": None, "value": 0.3}]
    s = F.signals_from_rows(rows, "fcst_prob")
    assert [x.ts for x in s] == [1, 2]
    idx = F.index_signals_from_prices([(1, 100.0), (2, 101.0)])
    assert idx[1].name == "btc_index" and idx[1].value == 101.0
