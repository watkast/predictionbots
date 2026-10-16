"""Polymarket venue adapter: CLOB + Gamma + Data API clients, market WebSocket
and normalisation to `pb.core.types`.

Conventions
-----------
* A Polymarket binary market has two ERC-1155 outcome tokens (YES / NO, or
  "Up"/"Down" etc.). `clobTokenIds` from Gamma is a JSON-encoded string
  `"[\"<yes>\", \"<no>\"]"` in `outcomes` order. Our `Market.market_id` is the
  **YES token id** (first token). `Market.meta["no_token"]` carries the other.
* CLOB books are per token. We normalise to the YES-leg Book: a YES-token book
  is used directly; a NO-token book is mirrored (bid at p -> YES ask at 1-p).
* `/book` returns `bids`/`asks` arrays of `{price, size}` in arbitrary order
  (best is conventionally the last entry); we sort ourselves.
* WS `wss://ws-subscriptions-clob.polymarket.com/ws/market` pushes
  `book` (full snapshot), `price_change` (level updates), `last_trade_price`
  and `tick_size_change` events, each carrying `asset_id`.
* Trading needs `py_clob_client_v2` (optional dep, not installed in CI);
  `PolymarketTrader` raises `TradingUnavailable` with a clear message when
  it is missing.

No network I/O happens at import time; tests use respx and fake sockets.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any, AsyncIterator, Awaitable, Callable, Iterable, Optional

import httpx

from pb.core.fees import FeeSchedule, polymarket_schedule
from pb.core.types import Action, Book, Level, Market, Order, TIF, Trade, Venue
from pb.venues.kalshi import TokenBucket, _get, _num, _ts

log = logging.getLogger(__name__)

CLOB_BASE = "https://clob.polymarket.com"
GAMMA_BASE = "https://gamma-api.polymarket.com"
DATA_BASE = "https://data-api.polymarket.com/v2"
MARKET_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
USER_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/user"

try:  # optional trading dependency
    import py_clob_client_v2 as _pcc  # type: ignore
except Exception:  # pragma: no cover - not installed in CI
    _pcc = None


class PolymarketError(RuntimeError):
    def __init__(self, status: int, body: Any, path: str):
        super().__init__(f"Polymarket {status} on {path}: {body}")
        self.status = status
        self.body = body
        self.path = path


class TradingUnavailable(RuntimeError):
    pass


# ----------------------------------------------------------------------------
# Parsing helpers
# ----------------------------------------------------------------------------
def _json_list(v: Any) -> list:
    """Gamma encodes some list fields as JSON strings."""
    if v is None:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        try:
            out = json.loads(v)
            return out if isinstance(out, list) else []
        except ValueError:
            return []
    return []


def _levels(arr: Any) -> list[Level]:
    out: list[Level] = []
    for x in arr or []:
        if isinstance(x, dict):
            p, s = _num(_get(x, "price")), _num(_get(x, "size", "amount"))
        elif isinstance(x, (list, tuple)) and len(x) >= 2:
            p, s = _num(x[0]), _num(x[1])
        else:
            continue
        if s > 0 and 0 <= p <= 1:
            out.append(Level(p, s))
    return out


def _sort_book(b: Book) -> Book:
    b.bids.sort(key=lambda l: -l.price)
    b.asks.sort(key=lambda l: l.price)
    return b


def mirror_book(b: Book, market_id: str) -> Book:
    """A NO-token book expressed on the YES leg: NO bid at p == YES ask at 1-p."""
    return _sort_book(Book(ts=b.ts, market_id=market_id,
                           bids=[Level(round(1 - l.price, 6), l.size) for l in b.asks],
                           asks=[Level(round(1 - l.price, 6), l.size) for l in b.bids]))


# ----------------------------------------------------------------------------
# Normalisers
# ----------------------------------------------------------------------------
def _category(m: dict) -> str:
    c = _get(m, "category")
    if isinstance(c, str) and c:
        return c.lower()
    tags = _get(m, "tags", default=[]) or []
    for t in tags:
        label = t.get("label") or t.get("slug") if isinstance(t, dict) else str(t)
        if label:
            lab = str(label).lower()
            for known in ("crypto", "sports", "politics", "economics", "finance", "tech",
                          "culture", "weather", "geopolitics", "mentions"):
                if known in lab:
                    return known
    ev = _get(m, "events")
    if isinstance(ev, list) and ev and isinstance(ev[0], dict):
        return _category(ev[0])
    return "other"


def to_market(m: dict) -> Market:
    """Gamma market JSON -> core Market keyed by the YES token id."""
    tokens = _json_list(_get(m, "clobTokenIds", "clob_token_ids", "tokens"))
    tokens = [str(t.get("token_id") if isinstance(t, dict) else t) for t in tokens]
    outcomes = [str(o) for o in _json_list(_get(m, "outcomes", default=["Yes", "No"]))]
    yes_tok = tokens[0] if tokens else str(_get(m, "conditionId", "condition_id", "id", default=""))
    no_tok = tokens[1] if len(tokens) > 1 else ""
    fee_sched = _get(m, "feeSchedule", "fee_schedule")
    category = _category(m)
    meta = {
        "condition_id": _get(m, "conditionId", "condition_id", default=""),
        "no_token": no_tok,
        "outcomes": outcomes,
        "question": _get(m, "question", default=""),
        "slug": _get(m, "slug", default=""),
        "neg_risk": bool(_get(m, "negRisk", "neg_risk", default=False)),
        "fees_enabled": bool(_get(m, "feesEnabled", "fees_enabled", default=False)),
        "fee_schedule": fee_sched,
        "category": category,
        "volume_24h": _num(_get(m, "volume24hr", "volume24hrClob", "volume_24h"), 0.0),
        "volume": _num(_get(m, "volume", "volumeNum", "volumeClob"), 0.0),
        "liquidity": _num(_get(m, "liquidity", "liquidityNum", "liquidityClob"), 0.0),
        "best_bid": _num(_get(m, "bestBid"), 0.0) if _get(m, "bestBid") is not None else None,
        "best_ask": _num(_get(m, "bestAsk"), 0.0) if _get(m, "bestAsk") is not None else None,
        "active": bool(_get(m, "active", default=True)),
        "closed": bool(_get(m, "closed", default=False)),
        "gamma_id": str(_get(m, "id", default="")),
    }
    result = None
    if meta["closed"]:
        prices = [_num(p) for p in _json_list(_get(m, "outcomePrices", "outcome_prices"))]
        if prices and len(prices) >= 1:
            if prices[0] >= 0.999:
                result = 1.0
            elif prices[0] <= 0.001:
                result = 0.0
    event_id = ""
    ev = _get(m, "events")
    if isinstance(ev, list) and ev and isinstance(ev[0], dict):
        event_id = str(_get(ev[0], "id", "slug", default=""))
    event_id = event_id or str(_get(m, "eventId", "event_id", default=""))
    tick = _num(_get(m, "orderPriceMinTickSize", "minimum_tick_size", "tick_size"), 0.01) or 0.01
    min_size = _num(_get(m, "orderMinSize", "minimum_order_size", "min_size"), 1.0) or 1.0
    # multi-outcome neg-risk events are mutually exclusive & exhaustive (complete_set_arb)
    if meta["neg_risk"]:
        meta["mutually_exclusive"] = True
    close_ts = _ts(_get(m, "endDate", "end_date_iso", "end_date"))
    win = (crypto_window_from_slug(meta["slug"], close_ts)
           or crypto_window_from_slug(_get(m, "question", default=""), close_ts))
    if win is not None:
        meta.update(win)
    return Market(venue=Venue.POLYMARKET, market_id=yes_tok, event_id=event_id, series=category,
                  title=_get(m, "question", "title", default=""),
                  open_ts=_ts(_get(m, "startDate", "start_date", "createdAt")),
                  close_ts=close_ts, tick=tick, min_size=min_size, result=result, meta=meta)


_CRYPTO_WINDOW_RE = re.compile(
    r"^(?P<asset>btc|eth|sol|xrp|doge|bitcoin|ethereum|solana)-(?:updown|up-or-down)-(?P<n>5|15|60)m-(?P<ts>\d{9,13})$", re.I)
_CRYPTO_WINDOW_TITLE_RE = re.compile(
    r"^(?P<asset>bitcoin|ethereum|solana|btc|eth|sol)\s+up\s+or\s+down\s*-\s*(?P<mon>[a-z]+)\s+(?P<dd>\d{1,2}),?\s+"
    r"(?P<hh>\d{1,2}):(?P<mm>\d{2})\s*(?P<ampm>am|pm)?\s*-\s*(?P<hh2>\d{1,2}):(?P<mm2>\d{2})\s*(?P<ampm2>am|pm)?\s*(?P<tz>et|est|edt)?$",
    re.I)
_ASSET_CANON = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL", "btc": "BTC", "eth": "ETH", "sol": "SOL",
                "xrp": "XRP", "doge": "DOGE"}


def crypto_window_from_slug(slug: str, close_ts: float = 0.0) -> Optional[dict]:
    """Polymarket 5/15-minute up-or-down markets: `btc-updown-15m-1792152000`
    (slug ends in the window OPEN epoch) or the question "Bitcoin Up or Down -
    October 16, 1:00PM-1:15PM ET". Returns the meta keys mm_crypto_twap needs
    (`window_open_ts`, `window_close_ts`, `window_secs`, `asset`) or None."""
    s = (slug or "").strip()
    m = _CRYPTO_WINDOW_RE.match(s)
    if m:
        secs = int(m.group("n")) * 60
        t = float(m.group("ts"))
        if t > 1e11:
            t /= 1000.0
        asset = _ASSET_CANON.get(m.group("asset").lower(), m.group("asset").upper())
        open_ts = t
        # some slugs carry the close instead: trust endDate when it is within one window of t
        if close_ts and abs(close_ts - t) < secs / 2:
            open_ts = close_ts - secs
        return {"window_open_ts": open_ts, "window_close_ts": open_ts + secs, "window_secs": float(secs),
                "asset": asset}
    m = _CRYPTO_WINDOW_TITLE_RE.match(s)
    if m and close_ts:
        h1, h2 = int(m.group("hh")), int(m.group("hh2"))
        if (m.group("ampm") or "").lower() == "pm" and h1 < 12:
            h1 += 12
        if (m.group("ampm2") or m.group("ampm") or "").lower() == "pm" and h2 < 12:
            h2 += 12
        secs = (h2 * 60 + int(m.group("mm2"))) - (h1 * 60 + int(m.group("mm")))
        secs = secs * 60 if secs > 0 else 900
        asset = _ASSET_CANON.get(m.group("asset").lower(), m.group("asset").upper())
        return {"window_open_ts": close_ts - secs, "window_close_ts": close_ts, "window_secs": float(secs),
                "asset": asset}
    return None


def to_book(raw: dict, market_id: Optional[str] = None, ts: Optional[float] = None,
            is_no_token: bool = False) -> Book:
    """CLOB `/book` or WS `book` payload -> core Book (sorted). If the payload is
    for the NO token, pass `is_no_token=True` and the YES `market_id`."""
    asset = str(_get(raw, "asset_id", "token_id", default=""))
    mid = market_id or asset
    t = ts if ts is not None else _ts(_get(raw, "timestamp", "ts"), time.time())
    b = _sort_book(Book(ts=t, market_id=mid, bids=_levels(_get(raw, "bids", default=[])),
                        asks=_levels(_get(raw, "asks", default=[]))))
    if is_no_token:
        return mirror_book(b, mid)
    return b


def to_trade(t: dict, market_id: Optional[str] = None, is_no_token: bool = False) -> Trade:
    """Data-API `/trades` row or WS `last_trade_price` -> core Trade (YES leg)."""
    price = _num(_get(t, "price"), 0.0)
    size = _num(_get(t, "size", "amount", "shares"), 0.0)
    side = str(_get(t, "side", "taker_side", default="BUY")).upper()
    action = Action.BUY if side in ("BUY", "BID") else Action.SELL
    outcome = str(_get(t, "outcome", default="")).lower()
    asset = str(_get(t, "asset", "asset_id", "token_id", default=""))
    mid = market_id or asset
    if is_no_token or outcome in ("no", "down"):
        price = round(1.0 - price, 6)
        action = Action.SELL if action is Action.BUY else Action.BUY
    ts = _ts(_get(t, "timestamp", "ts", "created_at", "match_time"), 0.0)
    return Trade(ts=ts, market_id=mid, price=price, size=size, taker_action=action)


def fee_schedule_for(market: Market | dict, include_rebate: bool = False) -> FeeSchedule:
    """Fee schedule from category (and `feesEnabled`) via `polymarket_schedule`."""
    if isinstance(market, Market):
        cat = market.series or market.meta.get("category", "other")
        enabled = market.meta.get("fees_enabled", True)
        fs = market.meta.get("fee_schedule")
    else:
        cat = _category(market)
        enabled = bool(_get(market, "feesEnabled", "fees_enabled", default=True))
        fs = _get(market, "feeSchedule", "fee_schedule")
    override = None
    if isinstance(fs, dict):
        r = _get(fs, "takerRate", "taker_rate", "rate")
        if r is not None:
            override = _num(r)
    if not enabled:
        override = 0.0
    return polymarket_schedule(cat or "other", include_rebate=include_rebate, taker_rate_override=override)


# ----------------------------------------------------------------------------
# REST clients
# ----------------------------------------------------------------------------
class _Http:
    def __init__(self, base: str, client: Optional[httpx.AsyncClient], rps: float, timeout: float,
                 max_retries: int = 3):
        self.base = base.rstrip("/")
        self._own = client is None
        self._client = client or httpx.AsyncClient(timeout=timeout)
        self._bucket = TokenBucket(rps)
        self.max_retries = max_retries

    async def aclose(self) -> None:
        if self._own:
            await self._client.aclose()

    async def request(self, method: str, path: str, params: Optional[dict] = None,
                      json_body: Any = None, headers: Optional[dict] = None) -> Any:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        url = f"{self.base}{path}"
        for attempt in range(self.max_retries + 1):
            await self._bucket.acquire()
            resp = await self._client.request(method, url, params=params, json=json_body,
                                              headers=headers or {})
            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt < self.max_retries:
                    ra = resp.headers.get("Retry-After")
                    delay = _num(ra, 0.0) if ra else min(8.0, 0.5 * (2 ** attempt))
                    await asyncio.sleep(delay)
                    continue
            if resp.status_code >= 400:
                try:
                    body = resp.json()
                except ValueError:
                    body = resp.text
                raise PolymarketError(resp.status_code, body, path)
            if not resp.content:
                return {}
            try:
                return resp.json()
            except ValueError:
                return {"raw": resp.text}
        raise PolymarketError(429, "retries exhausted", path)


class PolymarketClient:
    """CLOB (books/prices), Gamma (metadata) and Data API (trades/positions)."""

    def __init__(self, client: Optional[httpx.AsyncClient] = None, clob_base: str = CLOB_BASE,
                 gamma_base: str = GAMMA_BASE, data_base: str = DATA_BASE, rps: float = 10.0,
                 timeout: float = 15.0):
        self.clob = _Http(clob_base, client, rps, timeout)
        self.gamma = _Http(gamma_base, self.clob._client, rps, timeout)
        self.data = _Http(data_base, self.clob._client, rps, timeout)

    async def aclose(self) -> None:
        await self.clob.aclose()

    async def __aenter__(self) -> "PolymarketClient":
        return self

    async def __aexit__(self, *exc) -> None:
        await self.aclose()

    # -- CLOB -------------------------------------------------------------------
    async def get_book(self, token_id: str) -> dict:
        return await self.clob.request("GET", "/book", params={"token_id": token_id})

    async def get_books(self, token_ids: Iterable[str]) -> list[dict]:
        body = [{"token_id": t} for t in token_ids]
        r = await self.clob.request("POST", "/books", json_body=body)
        return r if isinstance(r, list) else r.get("books", [])

    async def get_price(self, token_id: str, side: str = "BUY") -> Optional[float]:
        r = await self.clob.request("GET", "/price", params={"token_id": token_id, "side": side.upper()})
        v = _get(r, "price")
        return _num(v) if v is not None else None

    async def get_midpoint(self, token_id: str) -> Optional[float]:
        r = await self.clob.request("GET", "/midpoint", params={"token_id": token_id})
        v = _get(r, "mid", "midpoint")
        return _num(v) if v is not None else None

    async def get_last_trade_price(self, token_id: str) -> dict:
        return await self.clob.request("GET", "/last-trade-price", params={"token_id": token_id})

    async def get_prices_history(self, token_id: str, start_ts: Optional[int] = None,
                                 end_ts: Optional[int] = None, interval: Optional[str] = None,
                                 fidelity: Optional[int] = None) -> list[dict]:
        """CLOB `/prices-history?market=<token>` -> [{t, p}, ...]."""
        params = {"market": token_id, "startTs": start_ts, "endTs": end_ts,
                  "interval": interval, "fidelity": fidelity}
        r = await self.clob.request("GET", "/prices-history", params=params)
        return r.get("history", []) if isinstance(r, dict) else (r or [])

    async def get_tick_size(self, token_id: str) -> float:
        r = await self.clob.request("GET", "/tick-size", params={"token_id": token_id})
        return _num(_get(r, "minimum_tick_size", "tick_size"), 0.01)

    async def book(self, market: Market | str, ts: Optional[float] = None) -> Book:
        tok = market.market_id if isinstance(market, Market) else market
        raw = await self.get_book(tok)
        return to_book(raw, tok, ts)

    # -- Gamma ------------------------------------------------------------------
    async def get_markets(self, limit: int = 100, offset: int = 0, closed: Optional[bool] = None,
                          tag_id: Optional[int] = None, order: Optional[str] = None,
                          ascending: Optional[bool] = None, active: Optional[bool] = None,
                          **extra) -> list[dict]:
        params = {"limit": limit, "offset": offset,
                  "closed": _bool(closed), "tag_id": tag_id, "order": order,
                  "ascending": _bool(ascending), "active": _bool(active), **extra}
        r = await self.gamma.request("GET", "/markets", params=params)
        return r if isinstance(r, list) else r.get("markets", r.get("data", []))

    async def get_market(self, gamma_id: str) -> dict:
        return await self.gamma.request("GET", f"/markets/{gamma_id}")

    async def get_events(self, limit: int = 50, offset: int = 0, closed: Optional[bool] = None,
                         tag_id: Optional[int] = None, order: Optional[str] = None,
                         ascending: Optional[bool] = None, **extra) -> list[dict]:
        params = {"limit": limit, "offset": offset, "closed": _bool(closed), "tag_id": tag_id,
                  "order": order, "ascending": _bool(ascending), **extra}
        r = await self.gamma.request("GET", "/events", params=params)
        return r if isinstance(r, list) else r.get("events", r.get("data", []))

    async def markets(self, **kw) -> list[Market]:
        return [to_market(m) for m in await self.get_markets(**kw)]

    # -- Data API ---------------------------------------------------------------
    async def get_trades(self, condition_id: Optional[str] = None, limit: int = 500,
                         cursor: Optional[str] = None, token_id: Optional[str] = None,
                         offset: Optional[int] = None) -> dict:
        params = {"condition": condition_id, "asset": token_id,
                  "limit": limit, "cursor": cursor, "offset": offset}
        r = await self.data.request("GET", "/trades", params=params)
        if isinstance(r, list):
            return {"trades": r, "cursor": None}
        return {"trades": r.get("trades", r.get("data", [])), "cursor": _get(r, "cursor", "next_cursor")}

    async def iter_trades(self, condition_id: str, max_pages: int = 50, **kw) -> list[dict]:
        out: list[dict] = []
        cursor = None
        for _ in range(max_pages):
            page = await self.get_trades(condition_id, cursor=cursor, **kw)
            rows = page.get("trades", [])
            out.extend(rows)
            cursor = page.get("cursor")
            if not cursor or not rows:
                break
        return out

    async def get_data_prices_history(self, token_id: str, interval: Optional[str] = None,
                                      start: Optional[int] = None, end: Optional[int] = None,
                                      bucket_seconds: Optional[int] = None) -> list[dict]:
        params = {"token_id": token_id, "interval": interval, "start": start, "end": end,
                  "bucket_seconds": bucket_seconds}
        r = await self.data.request("GET", "/prices-history", params=params)
        return r.get("history", []) if isinstance(r, dict) else (r or [])

    async def get_positions(self, user: str, **extra) -> list[dict]:
        r = await self.data.request("GET", "/positions", params={"user": user, **extra})
        return r if isinstance(r, list) else r.get("positions", r.get("data", []))

    async def get_leaderboard(self, **params) -> Any:
        return await self.data.request("GET", "/leaderboard", params=params)

    # -- convenience -------------------------------------------------------------
    def fee_schedule(self, market: Market) -> FeeSchedule:
        return fee_schedule_for(market)


def _bool(v: Optional[bool]) -> Optional[str]:
    return None if v is None else ("true" if v else "false")


# ----------------------------------------------------------------------------
# Trading (optional dependency)
# ----------------------------------------------------------------------------
class PolymarketTrader:
    """Thin wrapper around `py_clob_client_v2`. Construction succeeds without
    the library; any order call raises `TradingUnavailable`."""

    def __init__(self, private_key: Optional[str] = None, funder: Optional[str] = None,
                 host: str = CLOB_BASE, chain_id: int = 137, signature_type: int = 1,
                 client: Any = None):
        self.private_key = private_key
        self.funder = funder
        self.host = host
        self.chain_id = chain_id
        self.signature_type = signature_type
        self._client = client

    def _c(self) -> Any:
        if self._client is not None:
            return self._client
        if _pcc is None:
            raise TradingUnavailable(
                "py_clob_client_v2 is not installed; `pip install py-clob-client-v2` and set "
                "POLY_PRIVATE_KEY / POLY_FUNDER to trade on Polymarket")
        if not self.private_key:
            raise TradingUnavailable("POLY_PRIVATE_KEY not set")
        ClobClient = getattr(_pcc, "ClobClient", None) or getattr(_pcc.client, "ClobClient")  # type: ignore[attr-defined]
        c = ClobClient(self.host, key=self.private_key, chain_id=self.chain_id,
                       signature_type=self.signature_type, funder=self.funder)
        try:
            c.set_api_creds(c.create_or_derive_api_creds())
        except Exception as e:  # pragma: no cover
            raise TradingUnavailable(f"could not derive CLOB API creds: {e}") from e
        self._client = c
        return c

    @staticmethod
    def order_args(order: Order, market: Market) -> dict:
        """Core YES-leg order -> (token_id, side, price, size). SELL YES is sent
        as a SELL on the YES token (needs YES inventory); when flat we instead
        BUY the NO token at 1-p, which is economically identical."""
        if order.action is Action.BUY:
            return {"token_id": market.market_id, "side": "BUY", "price": order.price,
                    "size": order.remaining}
        return {"token_id": market.market_id, "side": "SELL", "price": order.price,
                "size": order.remaining}

    def place_order(self, order: Order, market: Market, tif: Optional[str] = None) -> dict:
        c = self._c()
        a = self.order_args(order, market)
        tif = tif or {TIF.GTC: "GTC", TIF.IOC: "FAK", TIF.FOK: "FOK"}[order.tif]
        OrderArgs = getattr(_pcc, "OrderArgs", None) if _pcc else None
        if OrderArgs is None:  # pragma: no cover - lib layout changed or injected client
            return c.create_and_post_order(a, tif=tif, post_only=order.post_only)
        args = OrderArgs(token_id=a["token_id"], price=a["price"], size=a["size"], side=a["side"])
        signed = c.create_order(args)
        return c.post_order(signed, tif)

    def cancel(self, order_id: str) -> Any:
        return self._c().cancel(order_id)

    def cancel_all(self) -> Any:
        return self._c().cancel_all()


# ----------------------------------------------------------------------------
# WebSocket
# ----------------------------------------------------------------------------
@dataclass(slots=True)
class RawMessage:
    ts: float
    type: str
    msg: dict


class PolyBookState:
    def __init__(self, asset_id: str, market_id: str, is_no: bool = False):
        self.asset_id = asset_id
        self.market_id = market_id
        self.is_no = is_no
        self.bids: dict[float, float] = {}
        self.asks: dict[float, float] = {}
        self.ready = False

    def snapshot(self, msg: dict) -> None:
        self.bids = {l.price: l.size for l in _levels(_get(msg, "bids", "buys", default=[]))}
        self.asks = {l.price: l.size for l in _levels(_get(msg, "asks", "sells", default=[]))}
        self.ready = True

    def change(self, msg: dict) -> None:
        changes = _get(msg, "changes", "price_changes", default=None)
        if changes is None:
            changes = [msg]
        for ch in changes:
            p = _num(_get(ch, "price"))
            s = _num(_get(ch, "size"))
            side = str(_get(ch, "side", default="BUY")).upper()
            tbl = self.bids if side in ("BUY", "BID") else self.asks
            if s <= 0:
                tbl.pop(p, None)
            else:
                tbl[p] = s

    def to_book(self, ts: float) -> Book:
        b = _sort_book(Book(ts=ts, market_id=self.market_id,
                            bids=[Level(p, s) for p, s in self.bids.items()],
                            asks=[Level(p, s) for p, s in self.asks.items()]))
        return mirror_book(b, self.market_id) if self.is_no else b


class PolymarketWS:
    """Market-channel WebSocket. Subscribes to YES token ids and yields core
    `Book`/`Trade` plus `RawMessage` for tick-size changes etc."""

    def __init__(self, asset_ids: Iterable[str], url: str = MARKET_WS,
                 connect: Optional[Callable[..., Awaitable[Any]]] = None,
                 clock: Callable[[], float] = time.time, reconnect_delay: float = 2.0,
                 no_tokens: Optional[dict[str, str]] = None):
        """`no_tokens`: optional {no_token_id: yes_market_id} to also mirror NO books."""
        self.asset_ids = list(asset_ids)
        self.url = url
        self._connect = connect or _default_ws_connect
        self.clock = clock
        self.reconnect_delay = reconnect_delay
        self.stopped = False
        self._sock: Any = None
        self.books: dict[str, PolyBookState] = {a: PolyBookState(a, a) for a in self.asset_ids}
        for no_tok, yes_tok in (no_tokens or {}).items():
            self.books[no_tok] = PolyBookState(no_tok, yes_tok, is_no=True)

    def subscribe_payload(self) -> dict:
        return {"assets_ids": list(self.books.keys()), "type": "market"}

    async def stop(self) -> None:
        self.stopped = True
        if self._sock is not None:
            try:
                await self._sock.close()
            except Exception:
                pass

    async def events(self) -> AsyncIterator[Book | Trade | RawMessage]:
        while not self.stopped:
            try:
                self._sock = await self._connect(self.url, {})
                await self._sock.send(json.dumps(self.subscribe_payload()))
                while not self.stopped:
                    raw = await self._sock.recv()
                    if raw is None:
                        break
                    for ev in self.handle_raw(raw):
                        yield ev
            except asyncio.CancelledError:
                raise
            except Exception as e:
                if self.stopped:
                    return
                log.warning("Polymarket WS error: %s; reconnecting in %.1fs", e, self.reconnect_delay)
                await asyncio.sleep(self.reconnect_delay)
            if self.stopped:
                return

    def handle_raw(self, raw: str | bytes | dict | list) -> list[Book | Trade | RawMessage]:
        if isinstance(raw, (str, bytes)):
            if isinstance(raw, bytes):
                raw = raw.decode()
            if raw.strip().upper() in ("PONG", "PING"):
                return []
            try:
                data = json.loads(raw)
            except ValueError:
                return []
        else:
            data = raw
        msgs = data if isinstance(data, list) else [data]
        out: list[Book | Trade | RawMessage] = []
        for m in msgs:
            if isinstance(m, dict):
                out.extend(self._handle_one(m))
        return out

    def _handle_one(self, m: dict) -> list[Book | Trade | RawMessage]:
        typ = str(_get(m, "event_type", "type", default=""))
        now = self.clock()
        ts = _ts(_get(m, "timestamp", "ts"), now)
        if typ == "book":
            asset = str(_get(m, "asset_id", default=""))
            st = self.books.setdefault(asset, PolyBookState(asset, asset))
            st.snapshot(m)
            return [st.to_book(ts)]
        if typ == "price_change":
            out: list[Book | Trade | RawMessage] = []
            # Newer payloads group changes per asset under "price_changes".
            groups = _get(m, "price_changes")
            if isinstance(groups, list):
                touched: dict[str, PolyBookState] = {}
                for g in groups:
                    asset = str(_get(g, "asset_id", default=_get(m, "asset_id", default="")))
                    st = self.books.setdefault(asset, PolyBookState(asset, asset))
                    if not st.ready:
                        continue
                    st.change(g)
                    touched[asset] = st
                return [st.to_book(ts) for st in touched.values()]
            asset = str(_get(m, "asset_id", default=""))
            st = self.books.setdefault(asset, PolyBookState(asset, asset))
            if not st.ready:
                return []
            st.change(m)
            return [st.to_book(ts)]
        if typ == "last_trade_price":
            asset = str(_get(m, "asset_id", default=""))
            st = self.books.get(asset)
            mid = st.market_id if st else asset
            tr = to_trade(m, mid, is_no_token=bool(st and st.is_no))
            if tr.ts <= 0:
                tr.ts = now
            return [tr]
        if typ == "tick_size_change":
            return [RawMessage(ts, typ, m)]
        return [RawMessage(ts, typ or "unknown", m)]


async def _default_ws_connect(url: str, headers: dict[str, str]) -> Any:
    import websockets

    return await websockets.connect(url, additional_headers=headers or None, ping_interval=10,
                                    ping_timeout=10, max_size=2 ** 24)


__all__ = [
    "CLOB_BASE", "GAMMA_BASE", "DATA_BASE", "MARKET_WS", "PolymarketClient", "PolymarketError",
    "PolymarketTrader", "TradingUnavailable", "PolymarketWS", "PolyBookState", "RawMessage",
    "to_market", "to_book", "to_trade", "mirror_book", "fee_schedule_for",
]
