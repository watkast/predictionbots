import asyncio
import base64
import json
import time

import httpx
import pytest
import respx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

from pb.core.types import Action, Book, Order, TIF, Trade
from pb.venues import kalshi as K


# ----------------------------------------------------------------------------
# signing
# ----------------------------------------------------------------------------
@pytest.fixture(scope="module")
def rsa_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def test_sign_message_strips_query():
    assert K.KalshiAuth.message(1700000000000, "get", "/trade-api/v2/markets?limit=5") == \
        b"1700000000000GET/trade-api/v2/markets"


def test_rsa_pss_signature_verifies_with_public_key(rsa_key):
    auth = K.KalshiAuth("kid", rsa_key)
    ts = 1700000000123
    path = "/trade-api/v2/portfolio/balance"
    h = auth.headers("GET", path, ts_ms=ts)
    assert h["KALSHI-ACCESS-KEY"] == "kid"
    assert h["KALSHI-ACCESS-TIMESTAMP"] == str(ts)
    sig = h["KALSHI-ACCESS-SIGNATURE"]
    base64.b64decode(sig)  # valid base64
    pub = rsa_key.public_key()
    assert K.verify_signature(pub, sig, ts, "GET", path)
    assert not K.verify_signature(pub, sig, ts + 1, "GET", path)
    assert not K.verify_signature(pub, sig, ts, "POST", path)


def test_ed25519_signature_verifies():
    key = ed25519.Ed25519PrivateKey.generate()
    auth = K.KalshiAuth("kid", key)
    assert auth.kind == "ed25519"
    sig = auth.sign(1, "GET", K.WS_SIGN_PATH)
    assert K.verify_signature(key.public_key(), sig, 1, "GET", K.WS_SIGN_PATH)


def test_auth_from_env_pem_and_b64(rsa_key):
    pem = rsa_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                serialization.NoEncryption())
    a = K.KalshiAuth.from_env({"KALSHI_KEY_ID": "k", "KALSHI_PRIVATE_KEY_PEM": pem.decode()})
    assert a is not None and a.kind == "rsa"
    # escaped newlines (common in CI secrets)
    a2 = K.KalshiAuth.from_env({"KALSHI_KEY_ID": "k", "KALSHI_PRIVATE_KEY_PEM": pem.decode().replace("\n", "\\n")})
    assert a2 is not None
    a3 = K.KalshiAuth.from_env({"KALSHI_KEY_ID": "k", "KALSHI_PRIVATE_KEY_B64": base64.b64encode(pem).decode()})
    assert a3 is not None
    assert K.KalshiAuth.from_env({}) is None


# ----------------------------------------------------------------------------
# normalisers
# ----------------------------------------------------------------------------
MARKET_JSON = {
    "ticker": "KXBTC15M-26OCT161200-T110000", "event_ticker": "KXBTC15M-26OCT161200",
    "series_ticker": "KXBTC15M", "title": "BTC above 110000?", "status": "open",
    "open_time": "2026-10-16T11:45:00Z", "close_time": "2026-10-16T12:00:00Z",
    "expiration_time": "2026-10-16T12:05:00.123456789Z",
    "yes_bid_dollars": "0.4500", "yes_ask_dollars": "0.4700", "last_price": 46,
    "volume_fp": "1234.50", "open_interest": 500, "result": "",
    "price_ranges": [{"start": "0.01", "end": "0.99", "step": "0.01"}],
}


def test_to_market_parses_times_and_prices():
    m = K.to_market(MARKET_JSON)
    assert m.market_id == "KXBTC15M-26OCT161200-T110000"
    assert m.series == "KXBTC15M" and m.event_id == "KXBTC15M-26OCT161200"
    assert m.close_ts == pytest.approx(1792152000.0)  # 2026-10-16T12:00Z
    assert m.open_ts < m.close_ts
    assert m.tick == 0.01
    assert m.result is None
    assert m.meta["yes_bid"] == pytest.approx(0.45)
    assert m.meta["yes_ask"] == pytest.approx(0.47)
    assert m.meta["last_price"] == pytest.approx(0.46)  # legacy cents
    assert m.meta["volume"] == pytest.approx(1234.5)
    assert m.meta["open_interest"] == 500


def test_to_market_settled_and_wrapped():
    j = dict(MARKET_JSON, result="yes", status="settled", settlement_time="2026-10-16T12:06:00Z")
    m = K.to_market({"market": j})
    assert m.result == 1.0 and m.settle_ts == pytest.approx(1792152360.0)
    assert K.to_market(dict(MARKET_JSON, result="no")).result == 0.0
    # series derived from ticker when missing
    m2 = K.to_market({"ticker": "KXETH-26OCT16-T4000", "close_time": "2026-10-16T12:00:00Z"})
    assert m2.series == "KXETH"


ORDERBOOK_JSON = {"orderbook_fp": {
    "yes_dollars": [["0.4000", "100.00"], ["0.4500", "50.00"], ["0.4400", "20.00"]],
    "no_dollars": [["0.5000", "80.00"], ["0.5300", "10.00"], ["0.5200", "30.00"]],
}}


def test_to_book_converts_no_bids_to_yes_asks_and_sorts():
    b = K.to_book(ORDERBOOK_JSON, "T", 100.0)
    assert [l.price for l in b.bids] == [0.45, 0.44, 0.40]
    assert [l.size for l in b.bids] == [50.0, 20.0, 100.0]
    assert [l.price for l in b.asks] == pytest.approx([0.47, 0.48, 0.50])
    assert [l.size for l in b.asks] == [10.0, 30.0, 80.0]
    assert b.best_bid < b.best_ask
    assert b.ts == 100.0 and b.market_id == "T"


def test_to_book_legacy_cents():
    b = K.to_book({"orderbook": {"yes": [[40, 10], [45, 5]], "no": [[50, 7]]}}, "T", 1.0)
    assert b.best_bid == pytest.approx(0.45) and b.best_ask == pytest.approx(0.50)
    assert K.to_book({}, "T", 1.0).bids == []


def test_to_trade_variants():
    t1 = K.to_trade({"ticker": "T", "yes_price_dollars": "0.4600", "count_fp": "12.5",
                     "taker_outcome_side": "yes", "created_time": "2026-10-16T12:00:00Z"})
    assert t1 == Trade(ts=1792152000.0, market_id="T", price=0.46, size=12.5, taker_action=Action.BUY)
    t2 = K.to_trade({"yes_price": 46, "count": 3, "taker_side": "no", "created_time": 1792152000}, "T")
    assert t2.price == pytest.approx(0.46) and t2.size == 3 and t2.taker_action is Action.SELL
    t3 = K.to_trade({"no_price": 54, "count": 1, "taker_side": "yes", "created_time": "2026-10-16T12:00:00+00:00"}, "T")
    assert t3.price == pytest.approx(0.46)


def test_fee_schedule_for_series():
    s = K.fee_schedule_for({"series": {"ticker": "KXNFLGAME", "fee_type": "quadratic_with_maker_fees",
                                       "fee_multiplier": 1.0}})
    assert s.maker_rate > 0 and s.taker_rate == pytest.approx(0.07)
    s2 = K.fee_schedule_for({"ticker": "KXBTC15M", "fee_type": "quadratic"})
    assert s2.maker_rate == 0.0
    s3 = K.fee_schedule_for({}, "KXNFLGAME")  # falls back to prefix default
    assert s3.maker_rate > 0


def test_candle_to_summary():
    c = {"end_period_ts": 1792152000, "yes_bid": {"open": 40, "close": 45, "high": 46, "low": 39},
         "yes_ask": {"open": "0.42", "close": "0.47"}, "price": {"close": 46}, "volume_fp": "100.0",
         "open_interest": 12}
    s = K.candle_to_summary(c)
    assert s["ts"] == 1792152000 and s["bid_close"] == pytest.approx(0.45)
    assert s["ask_close"] == pytest.approx(0.47) and s["close"] == pytest.approx(0.46)
    assert s["volume"] == 100.0 and s["open_interest"] == 12


def test_order_payloads():
    o = Order("T", Action.SELL, 0.55, 10, tif=TIF.GTC, post_only=True)
    v2 = K.order_payload_v2(o, client_order_id="c1", expiration_ts=123)
    assert v2 == {"ticker": "T", "side": "ask", "count": "10.00", "price": "0.5500",
                  "time_in_force": "good_till_canceled", "post_only": True, "client_order_id": "c1",
                  "expiration_time": 123}
    v1 = K.order_payload_v1(Order("T", Action.BUY, 0.55, 10, tif=TIF.IOC))
    assert v1["action"] == "buy" and v1["side"] == "yes" and v1["yes_price"] == 55
    assert v1["time_in_force"] == "immediate_or_cancel"


def test_ts_parsing():
    assert K._ts("2026-10-16T12:00:00Z") == 1792152000.0
    assert K._ts(1792152000) == 1792152000.0
    assert K._ts(1792152000123) == pytest.approx(1792152000.123)
    assert K._ts("garbage", 7.0) == 7.0
    assert K._ts(None, 1.0) == 1.0


# ----------------------------------------------------------------------------
# REST client (respx)
# ----------------------------------------------------------------------------
@respx.mock
async def test_client_public_get_and_pagination():
    base = K.PROD_BASE
    route = respx.get(f"{base}/markets").mock(side_effect=[
        httpx.Response(200, json={"markets": [MARKET_JSON], "cursor": "c2"}),
        httpx.Response(200, json={"markets": [dict(MARKET_JSON, ticker="X2")], "cursor": ""}),
    ])
    async with K.KalshiClient() as c:
        ms = await c.iter_markets(series_ticker="KXBTC15M", status="open")
    assert [m["ticker"] for m in ms] == [MARKET_JSON["ticker"], "X2"]
    first = route.calls[0].request
    assert first.url.params["series_ticker"] == "KXBTC15M"
    assert "cursor" not in first.url.params
    assert route.calls[1].request.url.params["cursor"] == "c2"
    assert "KALSHI-ACCESS-KEY" not in first.headers


@respx.mock
async def test_client_signs_auth_requests(rsa_key):
    base = K.PROD_BASE
    respx.get(f"{base}/portfolio/balance").mock(return_value=httpx.Response(200, json={"balance": 10000}))
    auth = K.KalshiAuth("kid", rsa_key)
    async with K.KalshiClient(auth=auth) as c:
        r = await c.get_balance()
    assert r["balance"] == 10000
    req = respx.calls.last.request
    sig = req.headers["KALSHI-ACCESS-SIGNATURE"]
    ts = int(req.headers["KALSHI-ACCESS-TIMESTAMP"])
    assert K.verify_signature(rsa_key.public_key(), sig, ts, "GET", "/trade-api/v2/portfolio/balance")


async def test_client_auth_required_without_key():
    async with K.KalshiClient() as c:
        with pytest.raises(K.KalshiError) as ei:
            await c.get_balance()
    assert ei.value.status == 401


@respx.mock
async def test_client_retries_on_429(monkeypatch):
    sleeps = []

    async def fake_sleep(d):
        sleeps.append(d)

    monkeypatch.setattr(K.asyncio, "sleep", fake_sleep)
    respx.get(f"{K.PROD_BASE}/markets/T").mock(side_effect=[
        httpx.Response(429, headers={"Retry-After": "0.5"}),
        httpx.Response(200, json={"market": MARKET_JSON}),
    ])
    async with K.KalshiClient() as c:
        m = await c.get_market("T")
    assert m["ticker"] == MARKET_JSON["ticker"]
    assert sleeps == [0.5]


@respx.mock
async def test_client_book_and_trades_and_candles():
    base = K.PROD_BASE
    respx.get(f"{base}/markets/T/orderbook").mock(return_value=httpx.Response(200, json=ORDERBOOK_JSON))
    respx.get(f"{base}/markets/trades").mock(return_value=httpx.Response(200, json={
        "trades": [{"ticker": "T", "yes_price_dollars": "0.46", "count_fp": "2", "taker_outcome_side": "no",
                    "created_time": "2026-10-16T12:00:00Z"}], "cursor": ""}))
    cs = respx.get(f"{base}/series/S/markets/T/candlesticks").mock(
        return_value=httpx.Response(200, json={"candlesticks": []}))
    async with K.KalshiClient() as c:
        b = await c.book("T", ts=5.0)
        trades = K.to_trades(await c.get_trades(ticker="T", limit=5000), "T")
        await c.get_candlesticks("S", "T", 1, 2, 60)
        with pytest.raises(ValueError):
            await c.get_candlesticks("S", "T", 1, 2, 5)
    assert b.best_bid == 0.45 and b.ts == 5.0
    assert trades[0].taker_action is Action.SELL
    assert respx.calls[1].request.url.params["limit"] == "1000"
    assert cs.calls[0].request.url.params["period_interval"] == "60"


@respx.mock
async def test_create_order_v2_posts_body(rsa_key):
    route = respx.post(f"{K.PROD_BASE}/portfolio/events/orders").mock(
        return_value=httpx.Response(201, json={"order": {"order_id": "abc"}}))
    async with K.KalshiClient(auth=K.KalshiAuth("k", rsa_key)) as c:
        r = await c.create_order(Order("T", Action.BUY, 0.4, 5, post_only=True), client_order_id="x")
    assert r["order"]["order_id"] == "abc"
    body = json.loads(route.calls[0].request.content)
    assert body["side"] == "bid" and body["price"] == "0.4000" and body["count"] == "5.00"


def test_token_bucket():
    t = [0.0]
    tb = K.TokenBucket(rate=2, capacity=2, clock=lambda: t[0])
    assert tb.try_acquire() == 0 and tb.try_acquire() == 0
    assert tb.try_acquire() == pytest.approx(0.5)
    t[0] += 0.5
    assert tb.try_acquire() == 0


# ----------------------------------------------------------------------------
# WebSocket book maintenance
# ----------------------------------------------------------------------------
class FakeSocket:
    def __init__(self, frames):
        self.frames = list(frames)
        self.sent = []
        self.closed = False

    async def send(self, s):
        self.sent.append(json.loads(s))

    async def recv(self):
        if not self.frames:
            raise ConnectionError("eof")
        return self.frames.pop(0)

    async def close(self):
        self.closed = True


def _frames():
    return [
        json.dumps({"type": "subscribed", "id": 1, "msg": {"channel": "orderbook_delta", "sid": 1}}),
        json.dumps({"type": "orderbook_snapshot", "sid": 1, "seq": 1, "msg": {
            "market_ticker": "T", "yes_dollars": [["0.40", "10"], ["0.45", "5"]], "no_dollars": [["0.50", "8"]]}}),
        json.dumps({"type": "orderbook_delta", "sid": 1, "seq": 2, "msg": {
            "market_ticker": "T", "price_dollars": "0.45", "delta_fp": "-5", "side": "yes"}}),
        json.dumps({"type": "orderbook_delta", "sid": 1, "seq": 3, "msg": {
            "market_ticker": "T", "price": 52, "delta": 3, "side": "no"}}),
        json.dumps({"type": "trade", "sid": 2, "msg": {
            "market_ticker": "T", "yes_price_dollars": "0.46", "count_fp": "2", "taker_outcome_side": "yes",
            "ts": 1792152000}}),
        json.dumps({"type": "fill", "sid": 3, "msg": {"order_id": "o1", "count": 1}}),
    ]


async def test_ws_builds_book_from_snapshot_and_deltas():
    sock = FakeSocket(_frames())
    ws = K.KalshiWS(["T"], auth=None, connect=lambda url, headers: _ret(sock), clock=lambda: 1000.0,
                    reconnect_delay=0.0)
    got = []
    async for ev in ws.events():
        got.append(ev)
        if len(got) == 5:
            await ws.stop()
    assert sock.sent[0]["cmd"] == "subscribe"
    assert sock.sent[0]["params"]["market_tickers"] == ["T"]
    assert "orderbook_delta" in sock.sent[0]["params"]["channels"]
    b0, b1, b2, tr, fill = got
    assert isinstance(b0, Book) and b0.best_bid == 0.45 and b0.best_ask == pytest.approx(0.50)
    assert b1.best_bid == 0.40  # 0.45 level removed
    assert [l.price for l in b2.asks] == pytest.approx([0.48, 0.50]) and b2.asks[0].size == 3
    assert isinstance(tr, Trade) and tr.price == 0.46 and tr.taker_action is Action.BUY and tr.ts == 1792152000
    assert isinstance(fill, K.RawMessage) and fill.type == "fill"


async def _ret(x):
    return x


def test_ws_delta_before_snapshot_ignored_and_auth_headers(rsa_key):
    ws = K.KalshiWS(["T"], auth=K.KalshiAuth("k", rsa_key))
    h = ws._auth_headers()
    assert K.verify_signature(rsa_key.public_key(), h["KALSHI-ACCESS-SIGNATURE"],
                              int(h["KALSHI-ACCESS-TIMESTAMP"]), "GET", "/trade-api/ws/v2")
    out = ws.handle_raw({"type": "orderbook_delta", "msg": {"market_ticker": "T", "price": 50, "delta": 1, "side": "yes"}})
    assert out == []
    assert ws.handle_raw("not json") == []


@respx.mock
async def test_client_trades_since_pages_oldest_first():
    base = K.PROD_BASE
    route = respx.get(f"{base}/markets/trades").mock(side_effect=[
        httpx.Response(200, json={"trades": [
            {"ticker": "T", "yes_price_dollars": "0.46", "count_fp": "2", "taker_outcome_side": "no",
             "created_time": "2026-10-16T12:00:05Z"}], "cursor": "c1"}),
        httpx.Response(200, json={"trades": [
            {"ticker": "T", "yes_price_dollars": "0.45", "count_fp": "1", "taker_outcome_side": "yes",
             "created_time": "2026-10-16T12:00:01Z"}], "cursor": ""}),
    ])
    async with K.KalshiClient() as c:
        trades = await c.trades_since("T", 1792152000.7)
    assert [t.price for t in trades] == [0.45, 0.46] and trades[0].taker_action is Action.BUY
    assert route.calls[0].request.url.params["min_ts"] == "1792152000"
    assert route.calls[0].request.url.params["ticker"] == "T"
