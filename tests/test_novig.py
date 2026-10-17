import asyncio
import base64
import hashlib
import json

import httpx
import pytest
import respx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519

from pb.core.types import Action, Market, Order, TIF, Venue
from pb.venues import novig as N

YES = "3f2504e0-4f89-11d3-9a0c-0305e82c3301"   # Buffalo Bills (home)
NO = "5a1c9e73-0000-4000-8000-000000000002"    # Kansas City Chiefs (away)
MID = "7c9e6679-7425-40de-944b-e07fc1f90ae7"
EID = "0b3f5f20-9c1b-4d6e-8f3a-5c2d1e7b4a90"

MARKET = {
    "marketId": MID, "eventId": EID, "marketType": "MONEY", "status": "OPEN", "voids": "PUSH",
    "description": "Kansas City Chiefs at Buffalo Bills — Moneyline", "startsTs": 1761505200000,
    "fee": {"coefficient": "0.06", "makerCredit": "0.5", "charged": "WHEN_LIVE"},
    "outcomes": [{"outcomeId": NO, "name": "Kansas City Chiefs", "status": "TBD"},
                 {"outcomeId": YES, "name": "Buffalo Bills", "status": "TBD"}],
}
EVENT = {"eventId": EID, "description": "Kansas City Chiefs at Buffalo Bills", "sport": "FOOTBALL",
         "league": "NFL", "status": "OPEN_PREGAME", "startsTs": 1761505200000}
BOOK = {"marketId": MID, "seq": 48120, "orders": {
    NO: [{"orderId": "o1", "price": "0.665", "qty": 110}, {"orderId": "o2", "price": "0.660", "qty": 250}],
    YES: [{"orderId": "o3", "price": "0.330", "qty": 180}, {"orderId": "o4", "price": "0.330", "qty": 20}],
}}


# ----------------------------------------------------------------------------
# signing
# ----------------------------------------------------------------------------
def test_canonical_query_rules():
    assert N.canonical_query("") == ""
    # sorted by name then value, repeats kept, first "=" splits, re-encoded uppercase %XX
    assert N.canonical_query("b=2&a=1&a=0") == "a=0&a=1&b=2"
    assert N.canonical_query("k=v=w") == "k=v%3Dw"
    assert N.canonical_query("flag") == "flag="
    assert N.canonical_query("q=a%20b") == "q=a%20b"
    assert N.canonical_query("q=a+b") == "q=a%2Bb"          # bare + stays +
    assert N.canonical_query("x=%7e") == "x=~"               # unreserved decoded


def test_canonical_string_six_lines_and_empty_body_hash():
    s = N.canonical_string(1700000000000, "get", "/v3/catalog/markets", "limit=5&league=NFL")
    lines = s.split("\n")
    assert lines == ["NOVIG-V3", "1700000000000", "GET", "/v3/catalog/markets", "league=NFL&limit=5",
                     hashlib.sha256(b"").hexdigest()]
    assert N.canonical_string(1, "POST", "/v3/echo", "", b'{"hello":"world"}').split("\n")[-1] == \
        hashlib.sha256(b'{"hello":"world"}').hexdigest()
    assert N.canonical_string(1, "GET", "/v3/ws").split("\n")[4] == ""


def test_ed25519_headers_verify():
    key = ed25519.Ed25519PrivateKey.generate()
    auth = N.NovigAuth("kid", key)
    assert auth.kind == "ed25519"
    h = auth.headers("GET", "/v3/catalog/markets", "league=NFL", ts_ms=1700000000000)
    assert set(h) == {"Novig-Key-Id", "Novig-Timestamp", "Novig-Signature"}
    assert h["Novig-Timestamp"] == "1700000000000"
    assert len(base64.b64decode(h["Novig-Signature"])) == 64
    pub = key.public_key()
    assert N.verify_signature(pub, h["Novig-Signature"], 1700000000000, "GET", "/v3/catalog/markets", "league=NFL")
    assert not N.verify_signature(pub, h["Novig-Signature"], 1700000000001, "GET", "/v3/catalog/markets", "league=NFL")
    assert not N.verify_signature(pub, h["Novig-Signature"], 1700000000000, "GET", "/v3/catalog/markets", "")
    assert len(auth.fingerprint()) == 64


def test_p256_der_signature_verifies():
    key = ec.generate_private_key(ec.SECP256R1())
    auth = N.NovigAuth("kid", key)
    assert auth.kind == "p256"
    sig = auth.sign(5, "POST", "/v3/orders", "", b"{}")
    raw = base64.b64decode(sig)
    assert raw[0] == 0x30 and 68 <= len(raw) <= 72   # DER SEQUENCE
    assert N.verify_signature(key.public_key(), sig, 5, "POST", "/v3/orders", "", b"{}")


def test_auth_from_env():
    key = ed25519.Ed25519PrivateKey.generate()
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption()).decode()
    assert N.NovigAuth.from_env({}) is None
    assert N.NovigAuth.from_env({"NOVIG_API_KEY": "k"}) is None
    a = N.NovigAuth.from_env({"NOVIG_API_KEY": "k", "NOVIG_SECRET": pem.replace("\n", "\\n")})
    assert a is not None and a.key_id == "k"
    b = N.NovigAuth.from_env({"NOVIG_API_KEY": "k", "NOVIG_SECRET_B64": base64.b64encode(pem.encode()).decode()})
    assert b is not None and b.kind == "ed25519"


# ----------------------------------------------------------------------------
# prices, odds, sizes
# ----------------------------------------------------------------------------
def test_price_grid_has_279_prices_and_complements():
    assert len(N.PRICE_GRID) == 279
    assert N.PRICE_GRID[0] == 0.001 and N.PRICE_GRID[-1] == 0.999
    assert N.on_grid(0.665) and N.on_grid(0.05) and N.on_grid(0.055) and N.on_grid(0.951)
    assert not N.on_grid(0.667) and not N.on_grid(0.052) and not N.on_grid(0.5001)
    for p in N.PRICE_GRID:
        assert N.on_grid(round(1 - p, 3))


def test_snap_price():
    assert N.snap_price(0.667) == 0.665
    assert N.snap_price(0.667, "up") == 0.67
    assert N.snap_price(0.6676, "nearest") == 0.67
    assert N.snap_price(0.0523) == 0.05 and N.snap_price(0.0523, "up") == 0.055
    assert N.snap_price(1.5) == 0.999 and N.snap_price(-1) == 0.001
    assert N.price_str(0.67) == "0.670"


def test_odds_conversions():
    assert N.american_to_prob(-150) == pytest.approx(0.6)
    assert N.american_to_prob(200) == pytest.approx(1 / 3)
    assert N.american_to_prob(100) == pytest.approx(0.5)
    assert N.decimal_to_prob(2.5) == pytest.approx(0.4)
    assert N.prob_to_american(0.6) == pytest.approx(-150)
    assert N.prob_to_american(1 / 3) == pytest.approx(200)
    assert N.prob_to_decimal(0.25) == pytest.approx(4.0)
    a, b = N.devig_two_way(N.american_to_prob(-120), N.american_to_prob(+100))
    assert a + b == pytest.approx(1.0) and a > b
    with pytest.raises(ValueError):
        N.american_to_prob(0)
    with pytest.raises(ValueError):
        N.decimal_to_prob(1.0)


def test_qty_units():
    assert N.qty_to_size(110) == pytest.approx(1.10)
    assert N.size_to_qty(1.10) == 110
    assert N.size_to_qty(0.001) == 1


# ----------------------------------------------------------------------------
# fees
# ----------------------------------------------------------------------------
def test_fee_schedule_matches_docs_examples():
    live = N.novig_schedule(0.03, 0.5, "WHEN_LIVE", live=True)
    assert live.fee(0.50, 100, is_maker=False) == pytest.approx(0.75)
    assert live.fee(0.30, 100, is_maker=False) == pytest.approx(0.63)
    assert live.fee(0.10, 100, is_maker=False) == pytest.approx(0.27)
    assert live.fee(0.50, 1, is_maker=False) == pytest.approx(0.0075)    # no cent rounding
    assert live.fee(0.50, 100, is_maker=True) == 0.0                     # maker pays nothing
    credit = N.novig_schedule(0.06, 0.5, "WHEN_LIVE", live=True, include_credit=True)
    assert credit.fee(0.50, 100, is_maker=True) == pytest.approx(-0.75)  # 50% of 1.50 rebated
    pregame = N.novig_schedule(0.06, 0.5, "WHEN_LIVE", live=False)
    assert pregame.fee(0.5, 100, is_maker=False) == 0.0
    unknown = N.novig_schedule(0.06, 0.5, "WHEN_LIVE")                   # conservative
    assert unknown.taker_rate == 0.06
    fut = N.fee_schedule_for({"fee": {"coefficient": "0.06", "makerCredit": "0.7", "charged": "ALWAYS"}})
    assert fut.taker_rate == 0.06 and fut.maker_rate == 0.0


# ----------------------------------------------------------------------------
# normalisation
# ----------------------------------------------------------------------------
def test_to_market_picks_home_as_yes_and_links_to_odds():
    m = N.to_market(MARKET, EVENT)
    assert m.venue is Venue.NOVIG and m.market_id == MID and m.event_id == EID
    assert m.series == "NFL" and m.meta["sport"] == "nfl" and m.meta["league"] == "NFL"
    assert m.meta["yes_outcome_id"] == YES and m.meta["no_outcome_id"] == NO
    assert m.meta["outcomes"] == ["Buffalo Bills", "Kansas City Chiefs"]
    assert m.meta["home"] == "Buffalo Bills" and m.meta["away"] == "Kansas City Chiefs"
    assert m.close_ts == 1761505200.0 and m.meta["commence_ts"] == m.close_ts
    assert m.meta["fee_coefficient"] == 0.06 and m.meta["fee_charged"] == "WHEN_LIVE"
    assert m.min_size == 0.01 and m.tick == 0.005 and m.result is None
    assert m.title == "Kansas City Chiefs at Buffalo Bills"
    from pb.data import odds_link as OL

    links = OL.build_links([m], sport="nfl")
    assert len(links) == 1
    ln = links[0]
    assert ln.home_team == "Buffalo Bills" and ln.away_team == "Kansas City Chiefs" and ln.outcome == "Buffalo Bills"
    assert OL.sport_for_markets([m]) == "nfl"


def test_to_market_totals_and_yes_no_and_settlement():
    tot = dict(MARKET, marketType="TOTAL", strike="48.5", description="KC v BUF Total",
               outcomes=[{"outcomeId": "u", "name": "Under 48.5", "status": "LOSS"},
                         {"outcomeId": "o", "name": "Over 48.5", "status": "WIN"}], status="SETTLED")
    m = N.to_market(tot, EVENT)
    assert m.meta["yes_name"].startswith("Over") and m.result == 1.0 and m.meta["strike"] == 48.5
    assert m.settle_ts is not None
    yn = dict(MARKET, marketType="MONEYLINE_3_WAY_WIN",
              outcomes=[{"outcomeId": "n", "name": "No", "status": "WIN"}, {"outcomeId": "y", "name": "Yes", "status": "LOSS"}])
    m2 = N.to_market(yn, EVENT)
    assert m2.meta["yes_outcome_id"] == "y" and m2.result == 0.0
    # unknown orientation falls back to sorted outcome ids, deterministically
    vs = dict(MARKET, description="Chiefs vs Bills",
              outcomes=[{"outcomeId": "zz", "name": "A", "status": "TBD"}, {"outcomeId": "aa", "name": "B", "status": "TBD"}])
    assert N.to_market(vs, EVENT).meta["yes_outcome_id"] == "aa"


def test_to_book_yes_leg_from_per_outcome_buy_orders():
    m = N.to_market(MARKET, EVENT)
    b = N.to_book(BOOK, m, ts=1.0)
    # YES (Bills) buys are bids, aggregated per price; NO (Chiefs) buys are asks at 1-p
    assert [(l.price, l.size) for l in b.bids] == [(0.33, pytest.approx(2.0))]
    assert [(round(l.price, 3), l.size) for l in b.asks] == [(0.335, pytest.approx(1.1)), (0.34, pytest.approx(2.5))]
    assert b.best_bid == 0.33 and round(b.best_ask, 3) == 0.335 and round(b.spread, 3) == 0.005
    assert b.depth_within(Action.BUY, 0.01) == pytest.approx(3.6)
    # market id only: falls back to sorted outcome ids (YES = smaller id = the Bills here)
    b2 = N.to_book(BOOK, MID, ts=1.0)
    assert b2.best_bid == 0.33


def test_to_trade_outcome_mapping_and_trades_since_paging():
    m = N.to_market(MARKET, EVENT)
    t = N.to_trade({"tradeId": "t1", "outcomeId": YES, "price": "0.335", "qty": 100, "ts": 1757894400120}, m)
    assert t.price == 0.335 and t.taker_action is Action.BUY and t.size == 1.0 and t.ts == 1757894400.12
    t2 = N.to_trade({"tradeId": "t2", "outcomeId": NO, "price": "0.665", "qty": 40, "ts": 1757894399870}, m)
    assert t2.price == pytest.approx(0.335) and t2.taker_action is Action.SELL and t2.size == 0.4


def test_order_payload_yes_leg_to_outcome_buy():
    m = N.to_market(MARKET, EVENT)
    buy = Order(market_id=MID, action=Action.BUY, price=0.337, size=2.5, post_only=True)
    body = N.order_payload(buy, m, client_id="cid")
    assert body == {"outcomeId": YES, "price": "0.335", "qty": 250, "tif": "PO", "clientId": "cid"}
    sell = Order(market_id=MID, action=Action.SELL, price=0.34, size=1.0, tif=TIF.IOC)
    body = N.order_payload(sell, m)
    assert body["outcomeId"] == NO and body["price"] == "0.660" and body["tif"] == "IOC" and body["qty"] == 100
    assert set(body) == {"outcomeId", "price", "qty", "tif"}
    gtt = N.order_payload(Order(market_id=MID, action=Action.BUY, price=0.5, size=1.0), m, ttl_ms=5000)
    assert gtt["tif"] == "GTC" and gtt["ttl"] == 5000


# ----------------------------------------------------------------------------
# REST client (respx)
# ----------------------------------------------------------------------------
def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro) if False else asyncio.run(coro)


@respx.mock
def test_client_unauthenticated_uses_public_routes_and_pages():
    page1 = {"items": [MARKET], "next": "c1"}
    page2 = {"items": [dict(MARKET, marketId="m2", status="CLOSED")]}
    r1 = respx.get(f"{N.PAPER_BASE}/v3/public/catalog/markets").mock(
        side_effect=[httpx.Response(200, json=page1), httpx.Response(200, json=page2)])
    respx.get(f"{N.PAPER_BASE}/v3/public/catalog/events").mock(return_value=httpx.Response(200, json={"items": [EVENT]}))
    respx.get(f"{N.PAPER_BASE}/v3/public/catalog/markets/{MID}/book").mock(return_value=httpx.Response(200, json=BOOK))

    async def go():
        async with N.NovigClient() as c:
            ms = await c.select_markets("NFL", top=5, now=1761505200 - 3600)
            assert [m.market_id for m in ms] == [MID]          # closed one filtered out
            assert ms[0].meta["event_status"] == "OPEN_PREGAME"
            b = await c.book(MID)
            assert b.best_bid == 0.33
            sched = await c.fee_schedule(MID)
            assert sched.taker_rate == 0.0 and sched.maker_rate == 0.0   # pregame: free
            return c

    c = _run(go())
    assert r1.call_count == 2
    q1, q2 = (dict(c.request.url.params) for c in r1.calls)
    assert q1 == {"league": "NFL", "marketType": "MONEY", "eventStatus": "OPEN_PREGAME", "limit": "500"}
    assert q2["after"] == "c1"
    for call in respx.calls:
        assert "Novig-Signature" not in call.request.headers


@respx.mock
def test_client_signed_requests_carry_headers_and_query_in_signature():
    key = ed25519.Ed25519PrivateKey.generate()
    auth = N.NovigAuth("kid", key)
    route = respx.get(f"{N.PAPER_BASE}/v3/catalog/markets/{MID}/trades").mock(
        return_value=httpx.Response(200, json={"items": [
            {"tradeId": "t3", "outcomeId": YES, "price": "0.340", "qty": 100, "ts": 1757894500000},
            {"tradeId": "t2", "outcomeId": NO, "price": "0.665", "qty": 40, "ts": 1757894400000},
            {"tradeId": "t1", "outcomeId": YES, "price": "0.330", "qty": 10, "ts": 1757894300000}]}))
    respx.get(f"{N.PAPER_BASE}/v3/catalog/markets/{MID}").mock(return_value=httpx.Response(200, json=MARKET))
    respx.get(f"{N.PAPER_BASE}/v3/catalog/events/{EID}").mock(return_value=httpx.Response(200, json=EVENT))

    async def go():
        async with N.NovigClient(auth=auth) as c:
            return await c.trades_since(MID, since_ts=1757894350.0)

    trades = _run(go())
    assert [t.ts for t in trades] == [1757894400.0, 1757894500.0]   # oldest first, since filter applied
    assert trades[0].taker_action is Action.SELL and trades[1].price == 0.34
    req = route.calls[0].request
    assert req.url.path == f"/v3/catalog/markets/{MID}/trades"
    sig = req.headers["Novig-Signature"]
    ts = int(req.headers["Novig-Timestamp"])
    assert req.headers["Novig-Key-Id"] == "kid"
    assert N.verify_signature(key.public_key(), sig, ts, "GET", req.url.path, req.url.query.decode())


@respx.mock
def test_client_post_body_is_signed_and_429_retries():
    key = ed25519.Ed25519PrivateKey.generate()
    auth = N.NovigAuth("kid", key)
    route = respx.post(f"{N.PAPER_BASE}/v3/echo").mock(side_effect=[
        httpx.Response(429, json={"code": "RATE_LIMIT_EXCEEDED", "message": "wait"}, headers={"Retry-After": "0"}),
        httpx.Response(200, json={"hello": "world"})])

    async def go():
        async with N.NovigClient(auth=auth) as c:
            return await c.echo({"hello": "world"})

    assert _run(go()) == {"hello": "world"}
    assert route.call_count == 2
    req = route.calls[1].request
    assert req.headers["Content-Type"] == "application/json"
    assert N.verify_signature(key.public_key(), req.headers["Novig-Signature"], int(req.headers["Novig-Timestamp"]),
                              "POST", "/v3/echo", "", req.content)


@respx.mock
def test_client_errors_carry_code_and_auth_required():
    respx.get(f"{N.PAPER_BASE}/v3/public/catalog/markets/nope").mock(
        return_value=httpx.Response(404, json={"code": "MARKET_NOT_FOUND", "message": "Market not found"}))

    async def go():
        async with N.NovigClient() as c:
            with pytest.raises(N.NovigError) as ei:
                await c.get_market("nope")
            assert ei.value.status == 404 and ei.value.code == "MARKET_NOT_FOUND"
            with pytest.raises(N.NovigError) as ei2:
                await c.get_balance()
            assert ei2.value.status == 401

    _run(go())


# ----------------------------------------------------------------------------
# WebSocket parsing
# ----------------------------------------------------------------------------
def test_ws_subscribe_payloads_and_nonces():
    m = N.to_market(MARKET, EVENT)
    ws = N.NovigWS([m], channels=("book", "trades"), private=("orders",), clock=lambda: 7.0)
    pl = ws.subscribe_payloads()
    assert [p["nonce"] for p in pl] == [1, 2]
    assert pl[0]["subscribe"] == {"markets": {MID: "book"}, "private": ["orders"]}
    assert pl[1]["subscribe"] == {"markets": {MID: "trades"}}
    assert ws.subscribe_payloads(["x"])[0]["nonce"] == 3


def test_ws_book_snapshot_delta_trades_lifecycle():
    m = N.to_market(MARKET, EVENT)
    ws = N.NovigWS([m], clock=lambda: 7.0)
    snap = {"market": MID, "book": {"seq": 48120, "orders": {
        NO: [{"order": "o1", "price": "0.665", "qty": 110}],
        YES: [{"order": "o3", "price": "0.330", "qty": 180}]}}}
    evs = ws.handle_raw(json.dumps(snap))
    assert len(evs) == 1 and evs[0].best_bid == 0.33 and round(evs[0].best_ask, 3) == 0.335 and evs[0].ts == 7.0
    # partial fill of o1: remove + add remainder; new YES order at a better price
    delta = {"market": MID, "book": {"seq": 48121, "deltas": [
        {"kind": "remove", "order": "o1", "reason": "fill"},
        {"kind": "add", "order": "o1", "outcome": NO, "price": "0.665", "qty": 70},
        {"kind": "add", "order": "o5", "outcome": YES, "price": "0.335", "qty": 50}]}}
    (b,) = ws.handle_raw(delta)
    assert b.best_bid == 0.335 and b.bids[0].size == 0.5 and b.asks[0].size == pytest.approx(0.7)
    # gap in seq is logged but applied
    (b2,) = ws.handle_raw({"market": MID, "book": {"seq": 48125, "deltas": [{"kind": "remove", "order": "o5"}]}})
    assert b2.best_bid == 0.33
    # trades batch (taker side inferred from the outcome named)
    tr = ws.handle_raw({"market": MID, "trades": {"seq": 9043, "deltas": [
        {"outcome": YES, "price": "0.335", "qty": 60, "ts": 1757894400456},
        {"outcome": NO, "price": "0.670", "qty": 100, "ts": 1757894400500}]}})
    assert [(t.price, t.taker_action, t.size) for t in tr] == [(0.335, Action.BUY, 0.6), (pytest.approx(0.33), Action.SELL, 1.0)]
    assert tr[0].ts == pytest.approx(1757894400.456)
    # GOLIVE voids every resting order: an empty book is emitted plus the raw lifecycle
    evs = ws.handle_raw({"market": MID, "lifecycle": {"seq": 13, "deltas": ["GOLIVE"]}})
    assert isinstance(evs[0], N.RawMessage) or evs[0].bids == []
    books = [e for e in evs if hasattr(e, "bids")]
    assert books and books[0].bids == [] and books[0].asks == []
    raws = [e for e in evs if isinstance(e, N.RawMessage)]
    assert raws and raws[0].type == "lifecycle" and raws[0].msg["market"] == MID


def test_ws_nested_envelope_private_and_acks():
    m = N.to_market(MARKET, EVENT)
    ws = N.NovigWS([m], clock=lambda: 1.0)
    evs = ws.handle_raw({"nonce": 1, "markets": {MID: {"book": {"seq": 1, "orders": {YES: [{"order": "a", "price": "0.5", "qty": 100}]}}}}})
    assert len(evs) == 1 and evs[0].best_bid == 0.5
    assert ws.handle_raw({"nonce": 2, "ok": True}) == []                     # ack
    evs = ws.handle_raw({"orders": {"seq": 3, "deltas": [{"kind": "fill", "orderId": "x", "price": "0.5", "qty": 10, "remaining": 0}]}})
    assert len(evs) == 1 and evs[0].type == "orders"
    err = ws.handle_raw({"code": "STALE_NONCE", "message": "nonce", "nonce": 1})
    assert err[0].type == "error"
    # delta before snapshot on a market we only know by id is ignored
    ws2 = N.NovigWS(["m-x"], clock=lambda: 1.0)
    assert ws2.handle_raw({"market": "m-x", "book": {"seq": 2, "deltas": [{"kind": "remove", "order": "q"}]}}) == []


def test_ws_subscribe_more_and_events_with_fake_socket():
    m = N.to_market(MARKET, EVENT)
    sent: list[dict] = []

    class Sock:
        def __init__(self):
            self.frames = [json.dumps({"market": MID, "book": {"seq": 1, "orders": {YES: [{"order": "a", "price": "0.5", "qty": 100}]}}}),
                           None]

        async def send(self, s):
            sent.append(json.loads(s))

        async def recv(self):
            return self.frames.pop(0)

        async def close(self):
            pass

    async def connect(url, headers):
        assert url == N.PAPER_WS and "Novig-Signature" in headers
        return Sock()

    key = ed25519.Ed25519PrivateKey.generate()
    ws = N.NovigWS([m], auth=N.NovigAuth("kid", key), connect=connect, channels=("book",), reconnect_delay=0.0)

    async def go():
        out = []
        async for ev in ws.events():
            out.append(ev)
            await ws.subscribe_more(["m-2"])
            await ws.stop()
        return out

    out = _run(go())
    assert len(out) == 1 and out[0].best_bid == 0.5
    assert sent[0]["subscribe"]["markets"] == {MID: "book"}
    assert sent[1]["subscribe"]["markets"] == {"m-2": "book"} and sent[1]["nonce"] == 2
    assert "m-2" in ws.books


# ----------------------------------------------------------------------------
# paper runner wiring
# ----------------------------------------------------------------------------
@respx.mock
def test_build_novig_runner_polls_without_auth():
    from pb.live.paper import PaperConfig, build_novig_runner
    from pb.sim.engine import SimConfig

    respx.get(f"{N.PAPER_BASE}/v3/public/catalog/markets/{MID}").mock(return_value=httpx.Response(200, json=MARKET))
    respx.get(f"{N.PAPER_BASE}/v3/public/catalog/events/{EID}").mock(return_value=httpx.Response(200, json=EVENT))
    m = N.to_market(MARKET, EVENT)

    async def go():
        client = N.NovigClient()
        cfg = PaperConfig(run_id="t", duration=0.0, ledger_root="data/ledger_test_novig", sim=SimConfig(), risk=None,
                          roll_secs=0)
        runner, c = await build_novig_runner([m], [], cfg, client=client)
        try:
            assert c is client and MID in runner.pollers
            assert runner.engine.fee_for(MID).taker_rate == 0.0        # pregame -> free
            assert runner.engine.fee_for("unknown").taker_rate == N.GAME_TAKER_COEFFICIENT
        finally:
            await client.aclose()

    _run(go())
