"""Kalshi venue adapter: REST client, request signing, WebSocket L2 feed and
normalisation to `pb.core.types`.

API notes (trade-api/v2, as documented Oct 2026; see ARCHITECTURE.md):

* Prices on the wire come in two flavours depending on endpoint age:
  legacy integer cents (`yes_price`, `yes_bid`, `price: 55`) and fixed-point
  dollar strings (`yes_price_dollars: "0.5500"`, `yes_dollars: [["0.55","12.00"]]`).
  Every parser here accepts both via `_get` / `_price_from` and emits YES
  probabilities in [0, 1].
* The order book is returned as BIDS on both legs: `yes_dollars` are YES bids,
  `no_dollars` are NO bids. A NO bid at p is a YES ask at 1-p, which is how we
  build `Book.asks`.
* Orders are always expressed on the YES leg (`side: "yes"`) with
  `action: buy|sell` (V1 `/portfolio/orders`) or `side: bid|ask` on the YES
  leg (V2 `/portfolio/events/orders`). A core `Order(action=SELL, price=p)`
  is a YES ask at p == a NO bid at 1-p.
* Signing: `KALSHI-ACCESS-KEY`, `KALSHI-ACCESS-TIMESTAMP` (ms) and
  `KALSHI-ACCESS-SIGNATURE` = base64(sign(ts_ms + METHOD + path_without_query)).
  RSA keys use PSS/SHA256/MGF1 with salt = digest length; Ed25519 keys sign
  the same message directly.
* Rate limits: basic tier ~ 20 writes/s and 200 reads/s. A token bucket is
  applied to every request and 429s are retried after `Retry-After`.

Nothing in this module performs network I/O at import time; tests mock httpx
with respx and feed the WS parser fake sockets.
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Awaitable, Callable, Iterable, Optional

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa

from pb.core.fees import FeeSchedule, kalshi_schedule
from pb.core.types import Action, Book, Level, Market, Order, TIF, Trade, Venue

log = logging.getLogger(__name__)

PROD_BASE = "https://external-api.kalshi.com/trade-api/v2"
DEMO_BASE = "https://external-api.demo.kalshi.co/trade-api/v2"
PROD_WS = "wss://external-api-ws.kalshi.com/trade-api/ws/v2"
DEMO_WS = "wss://external-api-ws.demo.kalshi.co/trade-api/ws/v2"
WS_SIGN_PATH = "/trade-api/ws/v2"

# Orders larger than 1000 trades per page are rejected by the API.
MAX_TRADES_PAGE = 1000


# ----------------------------------------------------------------------------
# Defensive field access / parsing helpers
# ----------------------------------------------------------------------------
def _get(d: Any, *names: str, default: Any = None) -> Any:
    """Return the first present, non-None key among `names` from mapping `d`."""
    if not isinstance(d, dict):
        return default
    for n in names:
        if n in d and d[n] is not None:
            return d[n]
    return default


def _num(v: Any, default: float = 0.0) -> float:
    """Parse a fixed-point string / int / float into float."""
    if v is None:
        return default
    if isinstance(v, bool):
        return float(v)
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return default


def _price_value(v: Any) -> Optional[float]:
    """Interpret a bare price value whose unit is ambiguous.

    * str  -> dollars ("0.5500")
    * int  -> cents (55)
    * float > 1 -> cents (55.0); float <= 1 -> dollars (0.55)
    """
    if v is None:
        return None
    if isinstance(v, bool):
        return None
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return None
    if isinstance(v, int):
        return v / 100.0
    if isinstance(v, float):
        return v / 100.0 if v > 1.0 else v
    return None


def _price_from(d: dict, dollar_names: Iterable[str], cent_names: Iterable[str]) -> Optional[float]:
    """Prefer `_dollars` fields; fall back to legacy integer-cent fields."""
    v = _get(d, *dollar_names)
    if v is not None:
        return _num(v)
    v = _get(d, *cent_names)
    if v is not None:
        return _price_value(v)
    return None


def _ts(v: Any, default: float = 0.0) -> float:
    """ISO-8601 string (with Z or offset), epoch seconds or epoch millis -> float seconds."""
    if v is None:
        return default
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        f = float(v)
        return f / 1000.0 if f > 1e11 else f  # millis heuristic
    s = str(v).strip()
    if not s:
        return default
    try:
        f = float(s)
        return f / 1000.0 if f > 1e11 else f
    except ValueError:
        pass
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        # Trim nanoseconds to microseconds for fromisoformat.
        if "." in s:
            head, tail = s.split(".", 1)
            frac = ""
            tz = ""
            for i, ch in enumerate(tail):
                if ch in "+-":
                    frac, tz = tail[:i], tail[i:]
                    break
            else:
                frac = tail
            s = f"{head}.{frac[:6].ljust(6, '0')}{tz}"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        return default


def _levels_from_pairs(pairs: Any) -> list[tuple[float, float]]:
    """[[price, size], ...] in either dollars-strings or cents-ints -> [(prob, size)]."""
    out: list[tuple[float, float]] = []
    if not pairs:
        return out
    for pair in pairs:
        if not pair or len(pair) < 2:
            continue
        p = _price_value(pair[0])
        if p is None:
            continue
        out.append((p, _num(pair[1])))
    return out


# ----------------------------------------------------------------------------
# Auth
# ----------------------------------------------------------------------------
class KalshiAuth:
    """Holds a key id and an RSA (PSS) or Ed25519 private key and signs requests."""

    def __init__(self, key_id: str, private_key: Any):
        self.key_id = key_id
        self.private_key = private_key
        if isinstance(private_key, rsa.RSAPrivateKey):
            self.kind = "rsa"
        elif isinstance(private_key, ed25519.Ed25519PrivateKey):
            self.kind = "ed25519"
        else:
            raise TypeError(f"unsupported private key type {type(private_key)!r}")

    # -- construction ----------------------------------------------------------
    @classmethod
    def from_pem(cls, key_id: str, pem: str | bytes, password: bytes | None = None) -> "KalshiAuth":
        if isinstance(pem, str):
            pem = pem.encode()
        key = serialization.load_pem_private_key(pem, password=password)
        return cls(key_id, key)

    @classmethod
    def from_env(cls, env: Optional[dict] = None) -> Optional["KalshiAuth"]:
        """Build from `KALSHI_KEY_ID` + (`KALSHI_PRIVATE_KEY_PEM` | `KALSHI_PRIVATE_KEY_B64`).
        Returns None when the variables are absent (public-data mode)."""
        env = os.environ if env is None else env
        key_id = env.get("KALSHI_KEY_ID")
        pem = env.get("KALSHI_PRIVATE_KEY_PEM")
        b64 = env.get("KALSHI_PRIVATE_KEY_B64")
        if not key_id or not (pem or b64):
            return None
        if pem:
            pem_bytes = pem.replace("\\n", "\n").encode()
        else:
            pem_bytes = base64.b64decode(b64)
        return cls.from_pem(key_id, pem_bytes)

    # -- signing ---------------------------------------------------------------
    @staticmethod
    def message(ts_ms: int, method: str, path: str) -> bytes:
        path = path.split("?", 1)[0]
        return f"{ts_ms}{method.upper()}{path}".encode()

    def sign(self, ts_ms: int, method: str, path: str) -> str:
        msg = self.message(ts_ms, method, path)
        if self.kind == "rsa":
            sig = self.private_key.sign(
                msg,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
                hashes.SHA256(),
            )
        else:
            sig = self.private_key.sign(msg)
        return base64.b64encode(sig).decode()

    def headers(self, method: str, path: str, ts_ms: Optional[int] = None) -> dict[str, str]:
        """`path` must be the full request path (e.g. /trade-api/v2/markets),
        without query string."""
        ts_ms = int(time.time() * 1000) if ts_ms is None else ts_ms
        return {
            "KALSHI-ACCESS-KEY": self.key_id,
            "KALSHI-ACCESS-TIMESTAMP": str(ts_ms),
            "KALSHI-ACCESS-SIGNATURE": self.sign(ts_ms, method, path),
        }


def verify_signature(public_key: Any, signature_b64: str, ts_ms: int, method: str, path: str) -> bool:
    """Known-answer helper (used by tests and `scripts/smoke_live.py`)."""
    msg = KalshiAuth.message(ts_ms, method, path)
    sig = base64.b64decode(signature_b64)
    try:
        if isinstance(public_key, rsa.RSAPublicKey):
            public_key.verify(
                sig, msg,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
                hashes.SHA256(),
            )
        else:
            public_key.verify(sig, msg)
        return True
    except Exception:  # InvalidSignature
        return False


# ----------------------------------------------------------------------------
# Rate limiting
# ----------------------------------------------------------------------------
class TokenBucket:
    """Simple asyncio token bucket (rate tokens/second, burst = capacity)."""

    def __init__(self, rate: float, capacity: Optional[float] = None,
                 clock: Callable[[], float] = time.monotonic):
        self.rate = float(rate)
        self.capacity = float(capacity if capacity is not None else rate)
        self.tokens = self.capacity
        self.clock = clock
        self._last = clock()

    def _refill(self) -> None:
        now = self.clock()
        self.tokens = min(self.capacity, self.tokens + (now - self._last) * self.rate)
        self._last = now

    def try_acquire(self, n: float = 1.0) -> float:
        """Return 0 if a token was taken, else seconds to wait."""
        self._refill()
        if self.tokens >= n:
            self.tokens -= n
            return 0.0
        return (n - self.tokens) / self.rate

    async def acquire(self, n: float = 1.0) -> None:
        while True:
            wait = self.try_acquire(n)
            if wait <= 0:
                return
            await asyncio.sleep(wait)


class KalshiError(RuntimeError):
    def __init__(self, status: int, body: Any, path: str):
        super().__init__(f"Kalshi {status} on {path}: {body}")
        self.status = status
        self.body = body
        self.path = path


# ----------------------------------------------------------------------------
# REST client
# ----------------------------------------------------------------------------
class KalshiClient:
    """Async REST client. All public market-data methods work without `auth`."""

    def __init__(self, auth: Optional[KalshiAuth] = None, base: str = PROD_BASE,
                 client: Optional[httpx.AsyncClient] = None, reads_per_sec: float = 200.0,
                 writes_per_sec: float = 20.0, max_retries: int = 4, timeout: float = 15.0):
        self.auth = auth
        self.base = base.rstrip("/")
        self._own_client = client is None
        self._client = client or httpx.AsyncClient(timeout=timeout)
        self._reads = TokenBucket(reads_per_sec)
        self._writes = TokenBucket(writes_per_sec)
        self.max_retries = max_retries
        self._series_cache: dict[str, dict] = {}

    @classmethod
    def from_env(cls, demo: bool = False, **kw) -> "KalshiClient":
        return cls(auth=KalshiAuth.from_env(), base=DEMO_BASE if demo else PROD_BASE, **kw)

    async def aclose(self) -> None:
        if self._own_client:
            await self._client.aclose()

    async def __aenter__(self) -> "KalshiClient":
        return self

    async def __aexit__(self, *exc) -> None:
        await self.aclose()

    @property
    def _path_prefix(self) -> str:
        return httpx.URL(self.base).path.rstrip("/")

    async def _request(self, method: str, path: str, *, params: Optional[dict] = None,
                       json_body: Optional[dict] = None, auth: bool = False) -> Any:
        if auth and self.auth is None:
            raise KalshiError(401, "endpoint requires auth; set KALSHI_KEY_ID/KALSHI_PRIVATE_KEY_PEM", path)
        bucket = self._reads if method.upper() == "GET" else self._writes
        params = {k: v for k, v in (params or {}).items() if v is not None}
        url = f"{self.base}{path}"
        full_path = f"{self._path_prefix}{path}"
        for attempt in range(self.max_retries + 1):
            await bucket.acquire()
            headers = {"Accept": "application/json"}
            if self.auth is not None:
                headers.update(self.auth.headers(method, full_path))
            resp = await self._client.request(method, url, params=params, json=json_body, headers=headers)
            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt < self.max_retries:
                    ra = resp.headers.get("Retry-After")
                    delay = _num(ra, 0.0) if ra else min(8.0, 0.5 * (2 ** attempt))
                    log.warning("Kalshi %s on %s; sleeping %.2fs", resp.status_code, path, delay)
                    await asyncio.sleep(delay)
                    continue
            if resp.status_code >= 400:
                try:
                    body = resp.json()
                except ValueError:
                    body = resp.text
                raise KalshiError(resp.status_code, body, path)
            if not resp.content:
                return {}
            try:
                return resp.json()
            except ValueError:
                return {"raw": resp.text}
        raise KalshiError(429, "retries exhausted", path)

    # -- public market data ----------------------------------------------------
    async def get_markets(self, series_ticker: Optional[str] = None, event_ticker: Optional[str] = None,
                          status: Optional[str] = None, limit: int = 100, cursor: Optional[str] = None,
                          min_close_ts: Optional[int] = None, max_close_ts: Optional[int] = None,
                          tickers: Optional[Iterable[str]] = None) -> dict:
        params = {"series_ticker": series_ticker, "event_ticker": event_ticker, "status": status,
                  "limit": limit, "cursor": cursor, "min_close_ts": min_close_ts,
                  "max_close_ts": max_close_ts,
                  "tickers": ",".join(tickers) if tickers else None}
        return await self._request("GET", "/markets", params=params)

    async def iter_markets(self, max_pages: int = 50, **kw) -> list[dict]:
        """Follow `cursor` pagination and return raw market dicts."""
        out: list[dict] = []
        cursor = None
        for _ in range(max_pages):
            page = await self.get_markets(cursor=cursor, **kw)
            out.extend(page.get("markets", []) or [])
            cursor = page.get("cursor")
            if not cursor:
                break
        return out

    async def get_market(self, ticker: str) -> dict:
        r = await self._request("GET", f"/markets/{ticker}")
        return r.get("market", r)

    async def get_series(self, series_ticker: str) -> dict:
        if series_ticker in self._series_cache:
            return self._series_cache[series_ticker]
        r = await self._request("GET", f"/series/{series_ticker}")
        s = r.get("series", r)
        self._series_cache[series_ticker] = s
        return s

    async def get_events(self, series_ticker: Optional[str] = None, status: Optional[str] = None,
                         limit: int = 100, cursor: Optional[str] = None,
                         with_nested_markets: bool = False) -> dict:
        params = {"series_ticker": series_ticker, "status": status, "limit": limit,
                  "cursor": cursor, "with_nested_markets": "true" if with_nested_markets else None}
        return await self._request("GET", "/events", params=params)

    async def get_event(self, event_ticker: str) -> dict:
        r = await self._request("GET", f"/events/{event_ticker}")
        return r.get("event", r)

    async def get_orderbook(self, ticker: str, depth: int = 20) -> dict:
        return await self._request("GET", f"/markets/{ticker}/orderbook", params={"depth": depth})

    async def get_trades(self, ticker: Optional[str] = None, limit: int = MAX_TRADES_PAGE,
                         cursor: Optional[str] = None, min_ts: Optional[int] = None,
                         max_ts: Optional[int] = None) -> dict:
        params = {"ticker": ticker, "limit": min(limit, MAX_TRADES_PAGE), "cursor": cursor,
                  "min_ts": min_ts, "max_ts": max_ts}
        return await self._request("GET", "/markets/trades", params=params)

    async def iter_trades(self, ticker: str, min_ts: Optional[int] = None, max_ts: Optional[int] = None,
                          max_pages: int = 200) -> list[dict]:
        out: list[dict] = []
        cursor = None
        for _ in range(max_pages):
            page = await self.get_trades(ticker=ticker, cursor=cursor, min_ts=min_ts, max_ts=max_ts)
            out.extend(page.get("trades", []) or [])
            cursor = page.get("cursor")
            if not cursor:
                break
        return out

    async def get_candlesticks(self, series_ticker: str, ticker: str, start_ts: int, end_ts: int,
                               period_interval: int = 1) -> dict:
        if period_interval not in (1, 60, 1440):
            raise ValueError("period_interval must be 1, 60 or 1440 minutes")
        params = {"start_ts": start_ts, "end_ts": end_ts, "period_interval": period_interval}
        return await self._request("GET", f"/series/{series_ticker}/markets/{ticker}/candlesticks",
                                   params=params)

    # -- historical ("cold storage") endpoints ---------------------------------
    async def get_historical_cutoff(self) -> dict:
        return await self._request("GET", "/historical/cutoff")

    async def get_historical_markets(self, series_ticker: Optional[str] = None, limit: int = 100,
                                     cursor: Optional[str] = None, min_close_ts: Optional[int] = None,
                                     max_close_ts: Optional[int] = None, **extra) -> dict:
        params = {"series_ticker": series_ticker, "limit": limit, "cursor": cursor,
                  "min_close_ts": min_close_ts, "max_close_ts": max_close_ts, **extra}
        return await self._request("GET", "/historical/markets", params=params)

    async def get_historical_trades(self, ticker: Optional[str] = None, limit: int = MAX_TRADES_PAGE,
                                    cursor: Optional[str] = None, min_ts: Optional[int] = None,
                                    max_ts: Optional[int] = None) -> dict:
        params = {"ticker": ticker, "limit": min(limit, MAX_TRADES_PAGE), "cursor": cursor,
                  "min_ts": min_ts, "max_ts": max_ts}
        return await self._request("GET", "/historical/trades", params=params)

    async def get_historical_candlesticks(self, ticker: str, start_ts: int, end_ts: int,
                                          period_interval: int = 1) -> dict:
        params = {"start_ts": start_ts, "end_ts": end_ts, "period_interval": period_interval}
        return await self._request("GET", f"/historical/markets/{ticker}/candlesticks", params=params)

    # -- portfolio (auth) --------------------------------------------------------
    async def get_balance(self) -> dict:
        return await self._request("GET", "/portfolio/balance", auth=True)

    async def get_positions(self, ticker: Optional[str] = None, event_ticker: Optional[str] = None,
                            limit: int = 100, cursor: Optional[str] = None,
                            settlement_status: Optional[str] = None) -> dict:
        params = {"ticker": ticker, "event_ticker": event_ticker, "limit": limit, "cursor": cursor,
                  "settlement_status": settlement_status}
        return await self._request("GET", "/portfolio/positions", params=params, auth=True)

    async def get_orders(self, ticker: Optional[str] = None, status: Optional[str] = None,
                         limit: int = 100, cursor: Optional[str] = None) -> dict:
        params = {"ticker": ticker, "status": status, "limit": limit, "cursor": cursor}
        return await self._request("GET", "/portfolio/orders", params=params, auth=True)

    async def get_fills(self, ticker: Optional[str] = None, limit: int = 100,
                        cursor: Optional[str] = None, min_ts: Optional[int] = None) -> dict:
        params = {"ticker": ticker, "limit": limit, "cursor": cursor, "min_ts": min_ts}
        return await self._request("GET", "/portfolio/fills", params=params, auth=True)

    async def create_order(self, order: Order, client_order_id: Optional[str] = None,
                           expiration_ts: Optional[int] = None,
                           self_trade_prevention: Optional[str] = None) -> dict:
        body = order_payload_v2(order, client_order_id=client_order_id, expiration_ts=expiration_ts,
                                self_trade_prevention=self_trade_prevention)
        return await self._request("POST", "/portfolio/events/orders", json_body=body, auth=True)

    async def create_order_v1(self, order: Order, client_order_id: Optional[str] = None) -> dict:
        body = order_payload_v1(order, client_order_id=client_order_id)
        return await self._request("POST", "/portfolio/orders", json_body=body, auth=True)

    async def cancel_order(self, order_id: str) -> dict:
        return await self._request("DELETE", f"/portfolio/orders/{order_id}", auth=True)

    async def batch_create_orders(self, orders: list[Order]) -> dict:
        body = {"orders": [order_payload_v1(o) for o in orders]}
        return await self._request("POST", "/portfolio/orders/batched", json_body=body, auth=True)

    async def batch_cancel_orders(self, order_ids: list[str]) -> dict:
        body = {"ids": list(order_ids)}
        return await self._request("DELETE", "/portfolio/orders/batched", json_body=body, auth=True)

    # -- convenience -------------------------------------------------------------
    async def fee_schedule(self, series_ticker: str) -> FeeSchedule:
        try:
            s = await self.get_series(series_ticker)
        except Exception as e:  # pragma: no cover - network failure path
            log.warning("series lookup failed for %s (%s); using offline default", series_ticker, e)
            return kalshi_schedule(series_ticker)
        return fee_schedule_for(s, series_ticker)

    async def book(self, ticker: str, depth: int = 20, ts: Optional[float] = None) -> Book:
        raw = await self.get_orderbook(ticker, depth=depth)
        return to_book(raw, ticker, ts if ts is not None else time.time())

    async def market(self, ticker: str) -> Market:
        return to_market(await self.get_market(ticker))


# ----------------------------------------------------------------------------
# Order payloads
# ----------------------------------------------------------------------------
_TIF_V2 = {TIF.GTC: "good_till_canceled", TIF.IOC: "immediate_or_cancel", TIF.FOK: "fill_or_kill"}


def order_payload_v2(order: Order, client_order_id: Optional[str] = None,
                     expiration_ts: Optional[int] = None,
                     self_trade_prevention: Optional[str] = None) -> dict:
    """POST /portfolio/events/orders body. Orders are on the YES leg:
    core BUY -> `side: bid`, core SELL -> `side: ask`."""
    body: dict[str, Any] = {
        "ticker": order.market_id,
        "side": "bid" if order.action is Action.BUY else "ask",
        "count": f"{order.remaining:.2f}",
        "price": f"{order.price:.4f}",
        "time_in_force": _TIF_V2[order.tif],
        "post_only": bool(order.post_only),
    }
    if client_order_id:
        body["client_order_id"] = client_order_id
    if expiration_ts is not None:
        body["expiration_time"] = int(expiration_ts)
    if self_trade_prevention:
        body["self_trade_prevention_type"] = self_trade_prevention
    return body


def order_payload_v1(order: Order, client_order_id: Optional[str] = None) -> dict:
    """Legacy POST /portfolio/orders body (also used for batched orders)."""
    body: dict[str, Any] = {
        "ticker": order.market_id,
        "side": "yes",
        "action": "buy" if order.action is Action.BUY else "sell",
        "type": "limit",
        "count": int(round(order.remaining)),
        "yes_price": int(round(order.price * 100)),
        "post_only": bool(order.post_only),
        "time_in_force": _TIF_V2[order.tif],
    }
    if client_order_id:
        body["client_order_id"] = client_order_id
    return body


# ----------------------------------------------------------------------------
# Normalisers
# ----------------------------------------------------------------------------
def _tick_from_market(m: dict) -> float:
    pr = _get(m, "price_ranges")
    if isinstance(pr, list) and pr:
        step = _get(pr[0], "step", "step_dollars", "tick")
        p = _price_value(step) if not isinstance(step, str) else _num(step)
        if p and 0 < p < 1:
            return p
    t = _get(m, "tick_size", "tick_size_dollars", "price_step")
    if t is not None:
        p = _price_value(t) if not isinstance(t, str) else _num(t)
        if p and 0 < p < 1:
            return p
    return 0.01


def _result_value(r: Any) -> Optional[float]:
    if r is None:
        return None
    s = str(r).strip().lower()
    if s == "yes":
        return 1.0
    if s == "no":
        return 0.0
    return None  # "", "void", "scalar" etc.


def to_market(m: dict) -> Market:
    """Market JSON (from /markets, /markets/{t}, /historical/markets) -> core Market."""
    m = m.get("market", m) if isinstance(m, dict) and "market" in m and isinstance(m["market"], dict) else m
    ticker = _get(m, "ticker", "market_ticker", default="")
    series = _get(m, "series_ticker", default="")
    event = _get(m, "event_ticker", default="")
    if not series and event:
        series = event.split("-", 1)[0]
    if not series and ticker:
        series = ticker.split("-", 1)[0]
    close_ts = _ts(_get(m, "close_time", "close_ts", "expiration_time", "expected_expiration_time"))
    open_ts = _ts(_get(m, "open_time", "open_ts"))
    settle_raw = _get(m, "settlement_time", "settled_time", "settlement_ts")
    settle_ts = _ts(settle_raw) if settle_raw is not None else None
    result = _result_value(_get(m, "result"))
    min_size = _num(_get(m, "min_order_size", "min_count"), 1.0) or 1.0
    status = _get(m, "status", default="")
    meta = {
        "status": status,
        "yes_bid": _price_from(m, ("yes_bid_dollars",), ("yes_bid",)),
        "yes_ask": _price_from(m, ("yes_ask_dollars",), ("yes_ask",)),
        "last_price": _price_from(m, ("last_price_dollars",), ("last_price",)),
        "volume": _num(_get(m, "volume_fp", "volume"), 0.0),
        "volume_24h": _num(_get(m, "volume_24h_fp", "volume_24h"), 0.0),
        "open_interest": _num(_get(m, "open_interest_fp", "open_interest"), 0.0),
        "liquidity": _num(_get(m, "liquidity_dollars", "liquidity"), 0.0),
        "market_type": _get(m, "market_type", default=""),
        "subtitle": _get(m, "subtitle", "yes_sub_title", default=""),
        "rules": _get(m, "rules_primary", default=""),
    }
    return Market(venue=Venue.KALSHI, market_id=ticker, event_id=event, series=series,
                  title=_get(m, "title", default=""), open_ts=open_ts, close_ts=close_ts,
                  tick=_tick_from_market(m), min_size=min_size, result=result,
                  settle_ts=settle_ts if (settle_ts and settle_ts > 0) else None, meta=meta)


def _book_sides(raw: dict) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """Return (yes_bids, no_bids) as (prob, size) lists from any orderbook shape."""
    ob = _get(raw, "orderbook_fp", "orderbook", default=raw)
    if not isinstance(ob, dict):
        ob = {}
    yes = _get(ob, "yes_dollars", "yes_fp", "yes", default=[])
    no = _get(ob, "no_dollars", "no_fp", "no", default=[])
    return _levels_from_pairs(yes), _levels_from_pairs(no)


def _assemble_book(ticker: str, ts: float, yes_bids: Iterable[tuple[float, float]],
                   no_bids: Iterable[tuple[float, float]]) -> Book:
    bids = [Level(p, s) for p, s in yes_bids if s > 0 and 0 < p < 1]
    asks = [Level(round(1.0 - p, 6), s) for p, s in no_bids if s > 0 and 0 < p < 1]
    bids.sort(key=lambda l: -l.price)
    asks.sort(key=lambda l: l.price)
    return Book(ts=ts, market_id=ticker, bids=bids, asks=asks)


def to_book(raw: dict, ticker: str, ts: float) -> Book:
    """GET /markets/{t}/orderbook response -> core Book (YES leg).

    `yes_dollars` are YES bids; `no_dollars` are NO bids == YES asks at 1-p."""
    yes_bids, no_bids = _book_sides(raw)
    return _assemble_book(ticker, ts, yes_bids, no_bids)


def to_trade(t: dict, ticker: Optional[str] = None) -> Trade:
    """Trade JSON (REST tape or WS `trade` message) -> core Trade."""
    mid = ticker or _get(t, "ticker", "market_ticker", default="")
    price = _price_from(t, ("yes_price_dollars", "price_dollars"), ("yes_price", "price"))
    if price is None:
        # Some payloads only carry the NO price.
        np_ = _price_from(t, ("no_price_dollars",), ("no_price",))
        price = (1.0 - np_) if np_ is not None else 0.0
    size = _num(_get(t, "count_fp", "count", "size"), 0.0)
    side = str(_get(t, "taker_outcome_side", "taker_side", "side", default="yes")).lower()
    action = Action.BUY if side in ("yes", "buy", "bid") else Action.SELL
    ts = _ts(_get(t, "created_time", "ts", "timestamp", "created_ts"), 0.0)
    return Trade(ts=ts, market_id=mid, price=float(price), size=size, taker_action=action)


def to_trades(resp: dict, ticker: Optional[str] = None) -> list[Trade]:
    return [to_trade(t, ticker) for t in (resp.get("trades", []) or [])]


def _ohlc(o: Any, key: str = "close") -> Optional[float]:
    if isinstance(o, dict):
        return _price_from(o, (f"{key}_dollars",), (key,))
    return _price_value(o)


def candle_to_summary(c: dict) -> dict:
    """Flatten a candlestick dict (either legacy cents or fp dollars) to floats."""
    yb = _get(c, "yes_bid", "yes_bid_dollars", default={})
    ya = _get(c, "yes_ask", "yes_ask_dollars", default={})
    pr = _get(c, "price", "price_dollars", default={})
    return {
        "ts": _ts(_get(c, "end_period_ts", "ts", "end_ts"), 0.0),
        "bid_open": _ohlc(yb, "open"), "bid_high": _ohlc(yb, "high"),
        "bid_low": _ohlc(yb, "low"), "bid_close": _ohlc(yb, "close"),
        "ask_open": _ohlc(ya, "open"), "ask_high": _ohlc(ya, "high"),
        "ask_low": _ohlc(ya, "low"), "ask_close": _ohlc(ya, "close"),
        "open": _ohlc(pr, "open"), "high": _ohlc(pr, "high"),
        "low": _ohlc(pr, "low"), "close": _ohlc(pr, "close"),
        "volume": _num(_get(c, "volume_fp", "volume"), 0.0),
        "open_interest": _num(_get(c, "open_interest_fp", "open_interest"), 0.0),
    }


def fee_schedule_for(series_json: dict, series_ticker: Optional[str] = None) -> FeeSchedule:
    """GET /series/{ticker} JSON -> FeeSchedule via `pb.core.fees.kalshi_schedule`."""
    s = series_json.get("series", series_json) if isinstance(series_json, dict) else {}
    ticker = series_ticker or _get(s, "ticker", "series_ticker", default="")
    fee_type = _get(s, "fee_type")
    mult = _get(s, "fee_multiplier")
    return kalshi_schedule(ticker, fee_type=fee_type,
                           fee_multiplier=_num(mult) if mult is not None else None)


# ----------------------------------------------------------------------------
# WebSocket
# ----------------------------------------------------------------------------
@dataclass(slots=True)
class RawMessage:
    """Non-normalised WS message passed through to the consumer (fills, ticker...)."""
    ts: float
    type: str
    msg: dict


class BookState:
    """Local L2 book for one Kalshi market built from snapshot + deltas.

    Internally keeps YES bids and NO bids keyed by probability (as the venue
    does); `to_book()` renders the YES-leg core Book."""

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.yes: dict[float, float] = {}
        self.no: dict[float, float] = {}
        self.seq: Optional[int] = None
        self.ready = False

    def snapshot(self, msg: dict) -> None:
        yes = _get(msg, "yes_dollars", "yes_fp", "yes", default=[])
        no = _get(msg, "no_dollars", "no_fp", "no", default=[])
        self.yes = {round(p, 6): s for p, s in _levels_from_pairs(yes) if s > 0}
        self.no = {round(p, 6): s for p, s in _levels_from_pairs(no) if s > 0}
        self.ready = True

    def delta(self, msg: dict) -> None:
        side = str(_get(msg, "side", default="yes")).lower()
        pv = _get(msg, "price_dollars", "price_fp")
        price = _num(pv) if pv is not None else _price_value(_get(msg, "price"))
        if price is None:
            return
        d = _num(_get(msg, "delta_fp", "delta"), 0.0)
        tbl = self.yes if side == "yes" else self.no
        key = round(price, 6)
        new = tbl.get(key, 0.0) + d
        if new <= 1e-9:
            tbl.pop(key, None)
        else:
            tbl[key] = new

    def to_book(self, ts: float) -> Book:
        return _assemble_book(self.ticker, ts, self.yes.items(), self.no.items())


def _seq_ok(state: BookState, seq: Any) -> bool:
    """Track `seq` numbers; return False on a gap (caller should resubscribe)."""
    if seq is None:
        return True
    try:
        seq = int(seq)
    except (TypeError, ValueError):
        return True
    if state.seq is not None and seq != state.seq + 1:
        state.seq = seq
        return False
    state.seq = seq
    return True


class KalshiWS:
    """Kalshi WebSocket feed. Yields core `Book` (after each snapshot/delta),
    `Trade`, and `RawMessage` for `fill`/`ticker`/other channels.

    `connect` is an injectable coroutine `(url, headers) -> socket` where the
    socket exposes `send(str)`, `recv() -> str` and `close()`; defaults to
    the `websockets` library. Tests pass a fake."""

    def __init__(self, tickers: Iterable[str], auth: Optional[KalshiAuth] = None,
                 url: str = PROD_WS, channels: Iterable[str] = ("orderbook_delta", "trade", "ticker"),
                 connect: Optional[Callable[..., Awaitable[Any]]] = None,
                 clock: Callable[[], float] = time.time, reconnect_delay: float = 2.0):
        self.tickers = list(tickers)
        self.auth = auth
        self.url = url
        self.channels = list(channels)
        self._connect = connect or _default_ws_connect
        self.clock = clock
        self.reconnect_delay = reconnect_delay
        self.books: dict[str, BookState] = {t: BookState(t) for t in self.tickers}
        self._cmd_id = 0
        self.stopped = False
        self._sock: Any = None

    def _auth_headers(self) -> dict[str, str]:
        if self.auth is None:
            return {}
        return self.auth.headers("GET", WS_SIGN_PATH)

    def subscribe_payload(self, channels: Optional[Iterable[str]] = None,
                          tickers: Optional[Iterable[str]] = None) -> dict:
        self._cmd_id += 1
        return {"id": self._cmd_id, "cmd": "subscribe",
                "params": {"channels": list(channels or self.channels),
                           "market_tickers": list(tickers or self.tickers)}}

    async def stop(self) -> None:
        self.stopped = True
        if self._sock is not None:
            try:
                await self._sock.close()
            except Exception:
                pass

    async def events(self) -> AsyncIterator[Book | Trade | RawMessage]:
        """Connect (reconnecting on failure) and yield normalised events forever
        until `stop()`."""
        while not self.stopped:
            try:
                self._sock = await self._connect(self.url, self._auth_headers())
                await self._sock.send(json.dumps(self.subscribe_payload()))
                async for ev in self._consume(self._sock):
                    yield ev
            except asyncio.CancelledError:
                raise
            except Exception as e:
                if self.stopped:
                    return
                log.warning("Kalshi WS error: %s; reconnecting in %.1fs", e, self.reconnect_delay)
                await asyncio.sleep(self.reconnect_delay)
            if self.stopped:
                return

    async def _consume(self, sock: Any) -> AsyncIterator[Book | Trade | RawMessage]:
        while not self.stopped:
            raw = await sock.recv()
            if raw is None:
                return
            for ev in self.handle_raw(raw):
                yield ev

    def handle_raw(self, raw: str | bytes | dict) -> list[Book | Trade | RawMessage]:
        """Parse one WS frame into zero or more events (pure; used by tests)."""
        if isinstance(raw, (str, bytes)):
            try:
                data = json.loads(raw)
            except ValueError:
                return []
        else:
            data = raw
        if not isinstance(data, dict):
            return []
        typ = str(_get(data, "type", default=""))
        msg = _get(data, "msg", default={}) or {}
        now = self.clock()
        if typ == "orderbook_snapshot":
            ticker = _get(msg, "market_ticker", "ticker", default="")
            st = self.books.setdefault(ticker, BookState(ticker))
            _seq_ok(st, _get(data, "seq"))
            st.snapshot(msg)
            return [st.to_book(_ts(_get(msg, "ts"), now))]
        if typ == "orderbook_delta":
            ticker = _get(msg, "market_ticker", "ticker", default="")
            st = self.books.setdefault(ticker, BookState(ticker))
            if not _seq_ok(st, _get(data, "seq")):
                log.warning("seq gap on %s; book may be stale until next snapshot", ticker)
            if not st.ready:
                return []  # delta before snapshot: ignore
            st.delta(msg)
            return [st.to_book(_ts(_get(msg, "ts"), now))]
        if typ == "trade":
            tr = to_trade(msg)
            if tr.ts <= 0:
                tr.ts = now
            return [tr]
        if typ in ("error",):
            log.warning("Kalshi WS error frame: %s", data)
            return [RawMessage(now, typ, msg if msg else data)]
        if typ in ("subscribed", "ok", "unsubscribed"):
            return []
        return [RawMessage(now, typ, msg if msg else data)]


async def _default_ws_connect(url: str, headers: dict[str, str]) -> Any:
    import websockets  # local import: optional at test time

    return await websockets.connect(url, additional_headers=headers, ping_interval=10, ping_timeout=10,
                                    max_size=2 ** 24)


__all__ = [
    "PROD_BASE", "DEMO_BASE", "PROD_WS", "DEMO_WS", "KalshiAuth", "KalshiClient", "KalshiError",
    "KalshiWS", "BookState", "RawMessage", "TokenBucket", "to_market", "to_book", "to_trade",
    "to_trades", "fee_schedule_for", "candle_to_summary", "order_payload_v2", "order_payload_v1",
    "verify_signature",
]
