import json

import httpx
import pytest
import respx

from pb.core.types import Action, Book, Market, Order, Trade, Venue
from pb.venues import polymarket as P

GAMMA_MARKET = {
    "id": "123456", "question": "Will BTC be above $110k on Oct 17?", "conditionId": "0xabc",
    "slug": "btc-110k", "endDate": "2026-10-17T12:00:00Z", "startDate": "2026-10-10T00:00:00Z",
    "outcomes": "[\"Yes\", \"No\"]", "outcomePrices": "[\"0.45\", \"0.55\"]",
    "clobTokenIds": "[\"111\", \"222\"]", "negRisk": False, "orderPriceMinTickSize": 0.001,
    "orderMinSize": 5, "feesEnabled": True, "feeSchedule": {"takerRate": 0.07},
    "volume24hr": 12345.6, "liquidity": "5000.5", "bestBid": 0.44, "bestAsk": 0.46,
    "active": True, "closed": False, "tags": [{"id": 1, "label": "Crypto", "slug": "crypto"}],
}


def test_to_market_gamma():
    m = P.to_market(GAMMA_MARKET)
    assert m.venue is Venue.POLYMARKET
    assert m.market_id == "111" and m.meta["no_token"] == "222"
    assert m.series == "crypto"
    assert m.tick == 0.001 and m.min_size == 5
    assert m.close_ts == pytest.approx(1792238400.0)
    assert m.meta["condition_id"] == "0xabc" and m.meta["volume_24h"] == pytest.approx(12345.6)
    assert m.meta["liquidity"] == pytest.approx(5000.5)
    assert m.result is None
    sched = P.fee_schedule_for(m)
    assert sched.taker_rate == pytest.approx(0.07) and sched.maker_rate == 0.0 and not sched.round_up_cents


def test_to_market_closed_result_and_category_fallback():
    j = dict(GAMMA_MARKET, closed=True, outcomePrices="[\"1\", \"0\"]", tags=[], category="Politics",
             feeSchedule=None)
    m = P.to_market(j)
    assert m.result == 1.0 and m.series == "politics"
    assert P.fee_schedule_for(m).taker_rate == pytest.approx(0.04)
    j2 = dict(GAMMA_MARKET, closed=True, outcomePrices="[\"0\", \"1\"]", feesEnabled=False)
    m2 = P.to_market(j2)
    assert m2.result == 0.0 and P.fee_schedule_for(m2).taker_rate == 0.0
    m3 = P.to_market({"conditionId": "0xdead", "clobTokenIds": ["9", "8"]})
    assert m3.market_id == "9" and m3.series == "other"


BOOK_JSON = {
    "market": "0xabc", "asset_id": "111", "timestamp": "1792152000123",
    "bids": [{"price": "0.40", "size": "100"}, {"price": "0.44", "size": "50"}, {"price": "0.42", "size": "10"}],
    "asks": [{"price": "0.50", "size": "70"}, {"price": "0.46", "size": "20"}],
}


def test_to_book_sorts_and_mirrors():
    b = P.to_book(BOOK_JSON)
    assert b.market_id == "111" and b.ts == pytest.approx(1792152000.123)
    assert [l.price for l in b.bids] == [0.44, 0.42, 0.40]
    assert [l.price for l in b.asks] == [0.46, 0.50]
    no = P.to_book(BOOK_JSON, market_id="YES", ts=1.0, is_no_token=True)
    # NO bids 0.44/0.42/0.40 -> YES asks 0.56/0.58/0.60; NO asks 0.46/0.50 -> YES bids 0.54/0.50
    assert [l.price for l in no.asks] == pytest.approx([0.56, 0.58, 0.60])
    assert [l.price for l in no.bids] == pytest.approx([0.54, 0.50])
    assert no.market_id == "YES"


def test_to_trade_yes_and_no_tokens():
    t = P.to_trade({"side": "BUY", "price": "0.45", "size": "10", "timestamp": 1792152000, "asset": "111",
                    "outcome": "Yes"}, "111")
    assert t == Trade(ts=1792152000.0, market_id="111", price=0.45, size=10.0, taker_action=Action.BUY)
    t2 = P.to_trade({"side": "BUY", "price": 0.55, "size": 4, "timestamp": "1792152000", "outcome": "No"}, "111")
    assert t2.price == pytest.approx(0.45) and t2.taker_action is Action.SELL
    t3 = P.to_trade({"side": "SELL", "price": 0.30, "size": 1, "timestamp": 5}, "111", is_no_token=True)
    assert t3.price == pytest.approx(0.70) and t3.taker_action is Action.BUY


@respx.mock
async def test_client_endpoints():
    respx.get(f"{P.CLOB_BASE}/book").mock(return_value=httpx.Response(200, json=BOOK_JSON))
    respx.get(f"{P.CLOB_BASE}/midpoint").mock(return_value=httpx.Response(200, json={"mid": "0.45"}))
    respx.get(f"{P.CLOB_BASE}/price").mock(return_value=httpx.Response(200, json={"price": "0.44"}))
    respx.get(f"{P.CLOB_BASE}/prices-history").mock(
        return_value=httpx.Response(200, json={"history": [{"t": 1792152000, "p": 0.45}]}))
    respx.post(f"{P.CLOB_BASE}/books").mock(return_value=httpx.Response(200, json=[BOOK_JSON]))
    gm = respx.get(f"{P.GAMMA_BASE}/markets").mock(return_value=httpx.Response(200, json=[GAMMA_MARKET]))
    respx.get(f"{P.DATA_BASE}/trades").mock(side_effect=[
        httpx.Response(200, json={"trades": [{"side": "BUY", "price": 0.45, "size": 1, "timestamp": 1}],
                                  "cursor": "n"}),
        httpx.Response(200, json=[{"side": "SELL", "price": 0.44, "size": 2, "timestamp": 2}]),
    ])
    async with P.PolymarketClient() as c:
        b = await c.book("111", ts=9.0)
        assert b.best_bid == 0.44 and b.ts == 9.0
        assert await c.get_midpoint("111") == 0.45
        assert await c.get_price("111", "BUY") == 0.44
        hist = await c.get_prices_history("111", start_ts=1, end_ts=2, fidelity=1)
        assert hist[0]["p"] == 0.45
        books = await c.get_books(["111"])
        assert json.loads(respx.calls[-1].request.content) == [{"token_id": "111"}]
        assert len(books) == 1
        ms = await c.markets(limit=5, closed=False, order="volume24hr", ascending=False)
        assert ms[0].market_id == "111"
        q = gm.calls[0].request.url.params
        assert q["closed"] == "false" and q["ascending"] == "false" and q["order"] == "volume24hr"
        rows = await c.iter_trades("0xabc")
        assert len(rows) == 2


@respx.mock
async def test_client_error_raises():
    respx.get(f"{P.CLOB_BASE}/book").mock(return_value=httpx.Response(404, json={"error": "no"}))
    async with P.PolymarketClient() as c:
        with pytest.raises(P.PolymarketError) as ei:
            await c.get_book("x")
    assert ei.value.status == 404


def test_trader_without_lib_raises_clearly():
    tr = P.PolymarketTrader(private_key="0x1", funder="0x2")
    if P._pcc is None:
        with pytest.raises(P.TradingUnavailable, match="py_clob_client_v2"):
            tr.place_order(Order("111", Action.BUY, 0.4, 5), Market(venue=Venue.POLYMARKET, market_id="111"))
        with pytest.raises(P.TradingUnavailable):
            tr.cancel("o")
    args = P.PolymarketTrader.order_args(Order("111", Action.SELL, 0.6, 5), Market(venue=Venue.POLYMARKET, market_id="111"))
    assert args == {"token_id": "111", "side": "SELL", "price": 0.6, "size": 5}


# ----------------------------------------------------------------------------
# WS
# ----------------------------------------------------------------------------
class FakeSocket:
    def __init__(self, frames):
        self.frames = list(frames)
        self.sent = []

    async def send(self, s):
        self.sent.append(json.loads(s))

    async def recv(self):
        if not self.frames:
            raise ConnectionError("eof")
        return self.frames.pop(0)

    async def close(self):
        pass


async def _ret(x):
    return x


async def test_ws_book_price_change_and_trade():
    frames = [
        json.dumps([{"event_type": "book", "asset_id": "111", "market": "0xabc", "timestamp": "1792152000000",
                     "bids": [{"price": "0.40", "size": "10"}, {"price": "0.44", "size": "5"}],
                     "asks": [{"price": "0.46", "size": "7"}]}]),
        json.dumps({"event_type": "price_change", "asset_id": "111", "timestamp": "1792152001000",
                    "changes": [{"price": "0.44", "side": "BUY", "size": "0"},
                                {"price": "0.47", "side": "SELL", "size": "3"}]}),
        json.dumps({"event_type": "price_change", "timestamp": "1792152002000", "price_changes": [
            {"asset_id": "111", "price": "0.45", "side": "BUY", "size": "2"},
            {"asset_id": "222", "price": "0.55", "side": "BUY", "size": "9"}]}),
        json.dumps({"event_type": "last_trade_price", "asset_id": "111", "price": "0.46", "size": "3",
                    "side": "BUY", "timestamp": "1792152003000"}),
        json.dumps({"event_type": "last_trade_price", "asset_id": "222", "price": "0.55", "size": "1",
                    "side": "BUY", "timestamp": "1792152004000"}),
        json.dumps({"event_type": "tick_size_change", "asset_id": "111", "old_tick_size": "0.01",
                    "new_tick_size": "0.001"}),
        "PONG",
    ]
    sock = FakeSocket(frames)
    ws = P.PolymarketWS(["111"], connect=lambda u, h: _ret(sock), clock=lambda: 7.0, no_tokens={"222": "111"})
    got = []
    async for ev in ws.events():
        got.append(ev)
        if len(got) == 6:
            await ws.stop()
    assert sock.sent[0] == {"assets_ids": ["111", "222"], "type": "market"}
    b0, b1, b2, t1, t2, raw = got
    assert isinstance(b0, Book) and b0.best_bid == 0.44 and b0.best_ask == 0.46 and b0.ts == 1792152000.0
    assert b1.best_bid == 0.40 and [l.price for l in b1.asks] == [0.46, 0.47]
    assert b2.best_bid == 0.45  # 222 delta ignored: no snapshot for NO token yet
    assert isinstance(t1, Trade) and t1.price == 0.46 and t1.taker_action is Action.BUY and t1.market_id == "111"
    # NO-token trade mirrored onto YES market
    assert t2.market_id == "111" and t2.price == pytest.approx(0.45) and t2.taker_action is Action.SELL
    assert isinstance(raw, P.RawMessage) and raw.type == "tick_size_change"
