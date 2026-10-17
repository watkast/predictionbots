"""Novig venue adapter (CFTC-regulated sports exchange): REST client, NOVIG-V3
request signing, WebSocket feed and normalisation to `pb.core.types`.

PAPER ONLY. Nothing here places a live order from the paper runner; the signer
and `order_payload` exist for a future live path.

Everything below was read from https://docs.novig.com on 2026-10-17 (all pages
reachable; the OpenAPI JSON files under /api-reference/spec-files/ were not
fetched). Each fact carries its page.

Environments  (https://docs.novig.com/api/environments)
  * Paper (play money, no location check): REST https://api.paper.novig.com,
    WS wss://api.paper.novig.com. Sign up at paper.novig.com, one button fills
    simulated KYC and funds $10,000 play money; create a key under
    Profile > Settings > Novig API. Same API as production.
  * Production: https://api.novig.com (real identity + location check).
  * Keys are environment-specific ("api key not found" across envs).

Account model / keys  (https://docs.novig.com/api/api-keys,
                       https://docs.novig.com/api/concepts/account-model)
  * `management` key (1 live, created in the web app): opens/funds/labels
    subaccounts, creates/revokes keys, reads wallets, CANNOT place orders.
  * `trading` key: one per subaccount (created with it by
    POST /v3/account/subaccounts {label, publicKey, algorithm}); places and
    cancels, streams book + fills. `trading::read` (128 live) read-only.
  * Keypair: `openssl genpkey -algorithm ed25519`; register the SPKI PEM public
    key; `algorithm` is `Ed25519` or `P-256`. `expiresAt` optional.
  * Eligibility: restricted states Arizona, Michigan, Nevada; VPN/proxy/Tor
    refused (451 ANONYMIZED_NETWORK); data-centre IPs allowed; placements need
    a passing device geolocation from the Novig app in the last 3 days
    (reads accept any passing check in that window; cancels skip checks).
    Production key creation needs a real identity check (403 KYC_REQUIRED).

Signing  (https://docs.novig.com/api/signing)
  Headers on every request incl. GET and the WS upgrade:
    Novig-Key-Id (key UUID, not signed), Novig-Timestamp (unix ms, unpadded
    decimal, +-30 s of server clock), Novig-Signature (raw signature bytes,
    standard base64 with padding). No algorithm header: server knows the key.
  Canonical string = six LF-joined lines, no trailing LF:
    "NOVIG-V3" / timestamp / METHOD uppercase / path (leading "/", incl. any
    mount prefix, not normalised or decoded) / canonical query ("" if none) /
    lowercase hex SHA-256 of the raw body bytes (empty body = hash of zero
    bytes e3b0c442...; a literal "{}" hashes differently). Send
    Content-Type: application/json, else the server hashes zero bytes.
  Canonical query: split on "&", split each pair at the FIRST "=", percent-
  decode both as UTF-8 (a bare "+" stays "+"), re-encode keeping A-Za-z0-9-._~
  and uppercase %XX for everything else, sort bytewise by name then value
  (keep repeats), join with "&". Never sign Expires/Key-Pair-Id/Policy/
  Signature (the edge strips them).
  Ed25519 signs the canonical string directly (64 bytes); P-256 = ECDSA/SHA-256
  with DER-encoded (r,s). Test: POST /v3/echo returns the body on a valid
  signature (401 SIGNATURE_REJECTED otherwise); 30 published vectors in
  signing-vectors.json (not fetched here).

Money / prices  (https://docs.novig.com/api/concepts/money)
  * Prices are PROBABILITIES as 3-decimal strings ("0.665"), not odds or cents.
    The counterparty buys the opposite outcome at 1-P.
  * Price grid (279 prices): 0.001-0.050 step 0.001; 0.055-0.945 step 0.005;
    0.950-0.999 step 0.001. Off-grid -> 400 INVALID_PRICE. `snap_price` here.
  * `qty` is an integer in MINIMAL UNITS: one unit pays $0.01 (110 @ 0.665
    costs $0.73150, pays $1.10000). Fee docs: contracts paying $1 = qty/100.
    This module converts: core `size` (contracts paying $1) = qty / 100.
  * Minimum order qty 1 (= 0.01 core contract). Balances 5-decimal strings,
    half-up rounding.

Universe  (https://docs.novig.com/api/concepts/universe-model)
  Sport -> League -> Event -> Market -> Outcome; orders name an `outcomeId`.
  Event: eventId, description (display only), sport (e.g. FOOTBALL), league
  (e.g. NFL), status (OPEN_PREGAME|CLOSED_PREGAME|OPEN_INGAME|SETTLED|FINAL|
  DELAYED|CANCELED), startsTs (unix ms). NO home/away fields; descriptions
  look like "Kansas City Chiefs at Buffalo Bills — Moneyline" (affiliates
  odds-screens page) and the deprecated API used "Away vs Home".
  Market: marketId, description, eventId, marketType (MONEY|SPREAD|TOTAL|
  TEAM_TOTAL|TOTAL_1H|MONEYLINE_3_WAY_WIN|MONEYLINE_3_WAY_DRAW|props), status
  (OPEN|CLOSED|SETTLED), voids (PUSH|FMV), startsTs, strike (decimal string,
  optional), fee {coefficient, makerCredit, charged ALWAYS|WHEN_LIVE},
  outcomes [{outcomeId, name, status TBD|WIN|LOSS|PUSH|<decimal FMV price>}]
  (array order NOT guaranteed; match by id).

Catalog REST  (https://docs.novig.com/api-reference/catalog/*)
  Signed routes under /v3/catalog/... ; unsigned PUBLIC twins under
  /v3/public/catalog/... (throttled per IP). Paging: `limit` 1-5000 (default
  500), `after` = previous page's `next`.
  * GET /v3/catalog/events?league=NFL,NBA&status=OPEN_PREGAME&startsAfter=&startsBefore=
  * GET /v3/catalog/events/{id}
  * GET /v3/catalog/markets?league=&marketType=MONEY,SPREAD&eventStatus=&event=&startsAfter=&startsBefore=
  * GET /v3/catalog/markets/{id}
  * GET /v3/catalog/markets/{id}/book?depth=1..20 -> {marketId, seq, orders:
    {outcomeId: [{orderId, price, qty}, ...best price first, FIFO within]}}.
    EVERY resting order is a BUY of that outcome: a bid on outcome A at p is
    the ask on outcome B at 1-p (affiliates/odds-screens). ETag/If-None-Match.
  * GET /v3/catalog/markets/{id}/trades?limit=&after= -> items [{tradeId,
    outcomeId, price, qty, ts(ms)}] newest first; no taker-side field.
  * GET /v3/types/sports, /v3/types/leagues, /v3/types/markets.
  * History: /v3/history/events|markets|positions (bucket `history`).

Orders  (https://docs.novig.com/api-reference/execution/place-an-order,
         https://docs.novig.com/api/concepts/order-lifecycle)
  POST /v3/orders {outcomeId, price "0.665", qty int>=1, tif GTC|GTT|IOC|FOK|PO,
  ttl ms (required for GTT, optional for PO), clientId uuid?} -> 201
  {orderId, clientId}. 201 = queued, not resting: the private-stream `open`
  event confirms. Post-only is the `PO` time-in-force. No `side` field: selling
  YES at p == buying the other outcome at 1-p. Batch: POST /v3/orders/batch
  (all-or-none), cancel DELETE /v3/orders/{id}, cancel-all, portfolio:
  /v3/portfolio/orders|fills|positions. Errors: 400 INVALID_PRICE, 403
  KYC_REQUIRED/SCOPE_INSUFFICIENT, 404 OUTCOME_NOT_FOUND, 409 MARKET_CLOSED,
  422 INSUFFICIENT_BALANCE, 423 SELF_EXCLUDED/ACCOUNT_LOCKED, 429
  RATE_LIMIT_EXCEEDED (+Retry-After), 451 ANONYMIZED_NETWORK, 503
  GEOLOCATION_SCREENING_UNAVAILABLE.

Fees  (https://docs.novig.com/api/concepts/fees, https://docs.novig.com/fees,
       https://docs.novig.com/maker-credit-program, changelog 2026-10-15)
  * ONLY THE TAKER PAYS: fee = c * P * (1-P) * N (N = $1-contracts = qty/100,
    P = fill price). No cent rounding, half-up to the millicent, no minimum.
  * MAKER PAYS ZERO and receives a Maker Credit = makerCredit * taker fee
    (0.5 on game markets, 0.7 on NFL/NCAAF futures), paid in cash within 7
    days, only on fills that were actually charged.
  * Game markets: c = 0.03 until 2026-10-15, c = 0.06 from 2026-10-15 (NCAAF,
    MLB, NHL on 0.06 since 2026-10-08); charged WHEN_LIVE only, i.e. PREGAME
    FILLS ARE FREE FOR BOTH SIDES. Futures: c = 0.06, credit 0.7, ALWAYS
    (PGA/ATP/WTA/UFC futures never charged). Read `market.fee` at runtime.
  * RFQ/parlays: taker 0.10, no credit (not used here).
  * Every GOLIVE voids ALL resting orders on the event's markets; a live window
    can reopen (DELAYED -> OPEN_INGAME), so fees switch on/off per window.

Streaming  (https://docs.novig.com/api/streaming/connection, .../book,
            .../tape, .../lifecycle, .../private,
            https://docs.novig.com/api-reference/streaming/open-the-websocket)
  * GET /v3/ws, upgrade signed with the same three headers (scope trading or
    trading::read; costs 32 `stream` tokens). Optional X-Novig-WS-Compress:
    deflate (raw DEFLATE binary frames). Server pings every 15 s; a missed
    pong drops the socket (1006). 1008 SLOW_CONSUMER = resubscribe.
  * Requests carry an increasing `nonce` (start 1; repeats -> STALE_NONCE):
    {"nonce":1,"subscribe":{"markets":{"<id>":"book"},"events":{},"private":["orders"]}}
    {"nonce":9,"unsubscribe":["market:<id>","PRIVATE"]}; verbs subscribe,
    unsubscribe, snapshot, status, query_markets, query_events, place, cancel,
    cancel_all. Channels: lifecycle (1), trades (4), bbo (8), book (16,
    includes lifecycle), orders (1), positions (1); 512-token stream bucket,
    8192 watched markets max.
  * Each subscription starts with a snapshot carrying `seq`; deltas have
    consecutive per-market `seq`. Gap -> buffer, send `snapshot`, replay.
  * book snapshot: {"seq":48120,"orders":{"<outcome>":[{"order":id,"price":"0.665","qty":110},...]}}
    book delta: {"seq":48121,"deltas":[{"kind":"add","order":id,"outcome":id,"price":"0.665","qty":40},
    {"kind":"remove","order":id,"reason":"fill"|"cancel"}]}; a partial fill is
    remove + add (same price, keeps queue position). GOLIVE: cancels for every
    order then the lifecycle transition.
  * trades: {"seq":9043,"deltas":[{"outcome":id,"price":"0.670","qty":60,"ts":1757894400456}]}
    (snapshot wraps recent batches under "trades"); no taker side given.
  * lifecycle: {"seq":12,"status":"OPEN"} / {"seq":13,"deltas":["GOLIVE"]};
    transitions OPEN, CLOSE, GRADE, START, END, GOLIVE, UNLIVE.
  * private orders: snapshot {"seq","open":[...]}; deltas kinds open|fill
    (price, qty, remaining; NO fee)|cancel (reason GO_LIVE|MARKET_CLOSED|
    SETTLED|NEUTRALIZED)|reject (also unfilled IOC/FOK/PO). positions:
    {marketId, outcomeId, qty, cost}.
  * The exact frame envelope (how the market id is attached to a "book" /
    "trades" object) is NOT shown on any page; `NovigWS.handle_raw` accepts
    `market`/`marketId`/`subject` keys and a `markets: {id: {...}}` map and
    logs anything it cannot place. Verify against the paper WS before trusting.

Throttling  (https://docs.novig.com/api/throttling; GET /v3/limits)
  Per-key token buckets (capacity / refill per s): place 256/8, cancel 256/16,
  read 64/16, account 64/8, stream 512/32, history 512/4. Edge: 2000 req/min
  per IP, 8 KiB bodies (403 HTML). 429 -> wait `Retry-After` seconds.

Public data  (https://docs.novig.com/public-data/overview): two daily
  anonymised CSVs (trades, markets) served as static files.

Conventions in this module
  * YES leg: for a two-outcome market the YES outcome is (in order) the
    outcome named "Yes", "Over", the HOME team when the event description
    reads "Away at|@ Home", else the first outcome by sorted outcomeId.
    `Market.meta["yes_outcome_id"]`/`["no_outcome_id"]` are authoritative;
    `meta["outcomes"]` = [yes_name, no_name] so `pb.data.odds_link`
    (`parse_polymarket_question`) links the market to Odds-API events.
  * Book: YES-outcome orders -> `Book.bids` (aggregated per price); NO-outcome
    orders -> `Book.asks` at 1-p. Sizes = qty/100 ($1 contracts).
  * Trade: a tape row names an outcome and a price. ASSUMPTION (undocumented):
    the row names the outcome the TAKER bought, so outcome == YES -> taker
    BUY at p, else taker SELL at 1-p.
  * Odds helpers (`american_to_prob`, `decimal_to_prob`, `prob_to_american`)
    exist for reference feeds that quote odds; Novig itself never does.
"""
from __future__ import annotations

import asyncio
import base64
import bisect
import hashlib
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any, AsyncIterator, Awaitable, Callable, Iterable, Optional
from urllib.parse import quote, unquote

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519

from pb.core.fees import FeeSchedule
from pb.core.types import Action, Book, Level, Market, Order, TIF, Trade, Venue

log = logging.getLogger(__name__)

PAPER_BASE = "https://api.paper.novig.com"
PROD_BASE = "https://api.novig.com"
PAPER_WS = "wss://api.paper.novig.com/v3/ws"
PROD_WS = "wss://api.novig.com/v3/ws"
WS_PATH = "/v3/ws"
API_PREFIX = "/v3"

QTY_PER_CONTRACT = 100          # `qty` units per $1 contract (one unit pays $0.01)
MAX_PAGE = 5000
MAX_BOOK_DEPTH = 20
SIGNING_SCHEME = "NOVIG-V3"
TIMESTAMP_SKEW_SECS = 30

# Fee schedule defaults (https://docs.novig.com/api/concepts/fees, 2026-10-15 change)
GAME_TAKER_COEFFICIENT = 0.06
GAME_MAKER_CREDIT = 0.5
FUTURES_TAKER_COEFFICIENT = 0.06
FUTURES_MAKER_CREDIT = 0.7

# Buckets (https://docs.novig.com/api/throttling): capacity, refill/s
THROTTLE = {"read": (64, 16.0), "place": (256, 8.0), "cancel": (256, 16.0), "account": (64, 8.0),
            "stream": (512, 32.0), "history": (512, 4.0)}

LEAGUE_SPORT = {"NFL": "nfl", "NBA": "nba", "MLB": "mlb", "NHL": "nhl", "NCAAF": "ncaaf", "NCAAB": "ncaab",
                "WNBA": "wnba", "MLS": "mls", "EPL": "epl", "UFC": "ufc", "ATP": "atp", "WTA": "wta", "PGA": "pga"}

_SHA256_EMPTY = hashlib.sha256(b"").hexdigest()


# ----------------------------------------------------------------------------
# Price grid and odds conversions
# ----------------------------------------------------------------------------
def _grid() -> list[float]:
    out = [round(i / 1000, 3) for i in range(1, 51)]                 # 0.001..0.050 step 0.001
    out += [round(55 / 1000 + i * 0.005, 3) for i in range(0, 179)]   # 0.055..0.945 step 0.005
    out += [round(i / 1000, 3) for i in range(950, 1000)]             # 0.950..0.999 step 0.001
    return out


PRICE_GRID: tuple[float, ...] = tuple(_grid())
_GRID_SET = frozenset(PRICE_GRID)


def on_grid(p: float) -> bool:
    return round(p, 3) in _GRID_SET and abs(p - round(p, 3)) < 1e-9


def snap_price(p: float, direction: str = "down") -> float:
    """Nearest grid price at or below (`down`, the docs' advice for buys: never
    pays more than intended) / at or above (`up`) / nearest (`nearest`)."""
    p = min(max(float(p), PRICE_GRID[0]), PRICE_GRID[-1])
    if direction == "nearest":
        return min(PRICE_GRID, key=lambda g: (abs(g - p), -g))
    if direction == "up":
        i = bisect.bisect_left(PRICE_GRID, p - 1e-9)
        return PRICE_GRID[min(i, len(PRICE_GRID) - 1)]
    i = bisect.bisect_right(PRICE_GRID, p + 1e-9) - 1
    return PRICE_GRID[max(i, 0)]


def price_str(p: float) -> str:
    """Wire format: three decimals ("0.665")."""
    return f"{p:.3f}"


def american_to_prob(odds: float) -> float:
    """American odds -> implied probability (with vig). -150 -> 0.6, +200 -> 1/3."""
    odds = float(odds)
    if odds == 0:
        raise ValueError("american odds cannot be 0")
    if odds < 0:
        return -odds / (-odds + 100.0)
    return 100.0 / (odds + 100.0)


def decimal_to_prob(odds: float) -> float:
    odds = float(odds)
    if odds <= 1.0:
        raise ValueError("decimal odds must be > 1")
    return 1.0 / odds


def prob_to_american(p: float) -> float:
    if not 0 < p < 1:
        raise ValueError("probability must be in (0,1)")
    return -100.0 * p / (1 - p) if p >= 0.5 else 100.0 * (1 - p) / p


def prob_to_decimal(p: float) -> float:
    if not 0 < p < 1:
        raise ValueError("probability must be in (0,1)")
    return 1.0 / p


def devig_two_way(p_a: float, p_b: float) -> tuple[float, float]:
    """Multiplicative de-vig of a two-way line."""
    s = p_a + p_b
    return p_a / s, p_b / s


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def _get(d: Any, *names: str, default: Any = None) -> Any:
    if not isinstance(d, dict):
        return default
    for n in names:
        if n in d and d[n] is not None:
            return d[n]
    return default


def _num(v: Any, default: float = 0.0) -> float:
    if v is None or isinstance(v, bool):
        return default
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return default


def _ms_to_s(v: Any, default: float = 0.0) -> float:
    f = _num(v, default)
    if f and f > 1e11:
        return f / 1000.0
    return f


def qty_to_size(qty: Any) -> float:
    return _num(qty) / QTY_PER_CONTRACT


def size_to_qty(size: float) -> int:
    return max(1, int(round(float(size) * QTY_PER_CONTRACT)))


# ----------------------------------------------------------------------------
# Auth (NOVIG-V3)
# ----------------------------------------------------------------------------
_UNRESERVED = "-._~"


def _enc(s: str) -> str:
    return quote(s, safe=_UNRESERVED)


def canonical_query(raw_query: str) -> str:
    """Canonical query per https://docs.novig.com/api/signing (see docstring)."""
    if not raw_query:
        return ""
    pairs: list[tuple[str, str]] = []
    for part in raw_query.split("&"):
        if part == "":
            continue
        name, eq, value = part.partition("=")
        name_d = unquote(name)      # bare "+" stays "+": unquote does not touch it
        value_d = unquote(value) if eq else ""
        pairs.append((_enc(name_d), _enc(value_d)))
    pairs.sort(key=lambda kv: (kv[0].encode(), kv[1].encode()))
    return "&".join(f"{k}={v}" for k, v in pairs)


def canonical_string(ts_ms: int, method: str, path: str, query: str = "", body: bytes = b"") -> str:
    body_hash = hashlib.sha256(body or b"").hexdigest()
    return "\n".join([SIGNING_SCHEME, str(int(ts_ms)), method.upper(), path, canonical_query(query), body_hash])


class NovigAuth:
    """Key id + Ed25519 (or P-256) private key; builds the three signed headers."""

    def __init__(self, key_id: str, private_key: Any):
        self.key_id = key_id
        self.private_key = private_key
        if isinstance(private_key, ed25519.Ed25519PrivateKey):
            self.kind = "ed25519"
        elif isinstance(private_key, ec.EllipticCurvePrivateKey):
            if private_key.curve.name not in ("secp256r1", "prime256v1"):
                raise TypeError("Novig P-256 keys must be on secp256r1")
            self.kind = "p256"
        else:
            raise TypeError(f"unsupported private key type {type(private_key)!r}")

    @classmethod
    def from_pem(cls, key_id: str, pem: str | bytes, password: bytes | None = None) -> "NovigAuth":
        if isinstance(pem, str):
            pem = pem.encode()
        return cls(key_id, serialization.load_pem_private_key(pem, password=password))

    @classmethod
    def from_env(cls, env: Optional[dict] = None) -> Optional["NovigAuth"]:
        """`NOVIG_API_KEY` (key id) + `NOVIG_SECRET` (PKCS#8 PEM private key,
        `\\n`-escaped allowed) or `NOVIG_SECRET_B64` (base64 of the PEM).
        None when absent (public-route mode)."""
        env = os.environ if env is None else env
        key_id = env.get("NOVIG_API_KEY") or env.get("NOVIG_KEY_ID")
        pem = env.get("NOVIG_SECRET") or env.get("NOVIG_PRIVATE_KEY_PEM")
        b64 = env.get("NOVIG_SECRET_B64") or env.get("NOVIG_PRIVATE_KEY_B64")
        if not key_id or not (pem or b64):
            return None
        pem_bytes = pem.replace("\\n", "\n").encode() if pem else base64.b64decode(b64)
        return cls.from_pem(key_id, pem_bytes)

    def sign(self, ts_ms: int, method: str, path: str, query: str = "", body: bytes = b"") -> str:
        msg = canonical_string(ts_ms, method, path, query, body).encode()
        if self.kind == "ed25519":
            sig = self.private_key.sign(msg)
        else:
            sig = self.private_key.sign(msg, ec.ECDSA(hashes.SHA256()))  # DER (r,s)
        return base64.b64encode(sig).decode()

    def headers(self, method: str, path: str, query: str = "", body: bytes = b"",
                ts_ms: Optional[int] = None) -> dict[str, str]:
        ts_ms = int(time.time() * 1000) if ts_ms is None else ts_ms
        return {"Novig-Key-Id": self.key_id, "Novig-Timestamp": str(ts_ms),
                "Novig-Signature": self.sign(ts_ms, method, path, query, body)}

    def public_key_pem(self) -> str:
        return self.private_key.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()

    def fingerprint(self) -> str:
        """SHA-256 of the SPKI DER (what the API reports as `fingerprint`)."""
        der = self.private_key.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
        return hashlib.sha256(der).hexdigest()


def verify_signature(public_key: Any, signature_b64: str, ts_ms: int, method: str, path: str,
                     query: str = "", body: bytes = b"") -> bool:
    msg = canonical_string(ts_ms, method, path, query, body).encode()
    sig = base64.b64decode(signature_b64)
    try:
        if isinstance(public_key, ec.EllipticCurvePublicKey):
            public_key.verify(sig, msg, ec.ECDSA(hashes.SHA256()))
        else:
            public_key.verify(sig, msg)
        return True
    except Exception:
        return False


# ----------------------------------------------------------------------------
# Rate limiting
# ----------------------------------------------------------------------------
class TokenBucket:
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


class NovigError(RuntimeError):
    def __init__(self, status: int, body: Any, path: str):
        super().__init__(f"Novig {status} on {path}: {body}")
        self.status = status
        self.body = body
        self.path = path
        self.code = body.get("code") if isinstance(body, dict) else None


# ----------------------------------------------------------------------------
# Fees
# ----------------------------------------------------------------------------
def novig_schedule(coefficient: float = GAME_TAKER_COEFFICIENT, maker_credit: float = GAME_MAKER_CREDIT,
                   charged: str = "WHEN_LIVE", live: Optional[bool] = None,
                   include_credit: bool = False) -> FeeSchedule:
    """`market.fee` -> FeeSchedule. Taker = c*P*(1-P)*N; maker 0; the maker
    credit (a cash rebate of `maker_credit` x taker fee) is ignored unless
    `include_credit`. `charged == WHEN_LIVE` with `live=False` means a free
    phase for both sides; with `live=None` (unknown) the taker coefficient is
    kept as the conservative assumption."""
    c = float(coefficient)
    if str(charged).upper() == "WHEN_LIVE" and live is False:
        c = 0.0
    if str(charged).upper() == "NEVER":
        c = 0.0
    return FeeSchedule(taker_rate=c, maker_rate=0.0,
                       maker_rebate_frac=(float(maker_credit) if include_credit else 0.0),
                       round_up_cents=False)


def fee_schedule_for(market: Market | dict, live: Optional[bool] = None,
                     include_credit: bool = False) -> FeeSchedule:
    """Core Market (meta from `to_market`) or raw market JSON -> FeeSchedule."""
    if isinstance(market, Market):
        meta = market.meta or {}
        return novig_schedule(_num(meta.get("fee_coefficient"), GAME_TAKER_COEFFICIENT),
                              _num(meta.get("maker_credit"), GAME_MAKER_CREDIT),
                              str(meta.get("fee_charged") or "WHEN_LIVE"), live, include_credit)
    fee = _get(market, "fee", default={}) or {}
    return novig_schedule(_num(_get(fee, "coefficient"), GAME_TAKER_COEFFICIENT),
                          _num(_get(fee, "makerCredit"), GAME_MAKER_CREDIT),
                          str(_get(fee, "charged", default="WHEN_LIVE")), live, include_credit)


# ----------------------------------------------------------------------------
# Normalisers
# ----------------------------------------------------------------------------
_AT_RE = re.compile(r"^\s*(?P<away>.+?)\s+(?:@|at)\s+(?P<home>.+?)\s*(?:[—–\-:(]|$)", re.I)
_VS_RE = re.compile(r"^\s*(?P<a>.+?)\s+(?:vs\.?|v\.?)\s+(?P<b>.+?)\s*(?:[—–\-:(]|$)", re.I)


def parse_description(desc: str) -> dict:
    """"Kansas City Chiefs at Buffalo Bills — Moneyline" -> {away, home, title}.
    "A vs B" gives {a, b, title} (orientation unknown)."""
    desc = desc or ""
    m = _AT_RE.match(desc)
    if m:
        return {"away": m.group("away").strip(), "home": m.group("home").strip(),
                "title": f"{m.group('away').strip()} at {m.group('home').strip()}"}
    m = _VS_RE.match(desc)
    if m:
        return {"a": m.group("a").strip(), "b": m.group("b").strip(),
                "title": f"{m.group('a').strip()} vs {m.group('b').strip()}"}
    return {"title": desc.strip()}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def choose_yes_outcome(outcomes: list[dict], market_type: str = "", description: str = "") -> tuple[dict, dict]:
    """Deterministic (YES, NO) outcome pair for a two-outcome market (see
    module docstring). Raises ValueError unless exactly two outcomes."""
    outs = [o for o in outcomes if isinstance(o, dict) and _get(o, "outcomeId")]
    if len(outs) != 2:
        raise ValueError(f"expected 2 outcomes, got {len(outs)}")
    outs = sorted(outs, key=lambda o: str(o["outcomeId"]))
    names = [str(_get(o, "name", default="")) for o in outs]
    for pref in ("yes", "over"):
        for i, n in enumerate(names):
            if n.strip().lower().startswith(pref):
                return outs[i], outs[1 - i]
    info = parse_description(description)
    home = info.get("home")
    if home:
        hk = _norm(home)
        for i, n in enumerate(names):
            nk = _norm(n)
            if nk and (nk in hk or hk in nk):
                return outs[i], outs[1 - i]
    return outs[0], outs[1]


def _result_from_outcome(status: Any) -> Optional[float]:
    s = str(status or "").strip().upper()
    if s == "WIN":
        return 1.0
    if s == "LOSS":
        return 0.0
    return None  # TBD / PUSH / FMV price


def to_market(m: dict, event: Optional[dict] = None) -> Market:
    """Catalog market JSON (+ its event JSON if known) -> core Market."""
    mid = str(_get(m, "marketId", "id", default=""))
    event = event or _get(m, "event", default=None) or {}
    league = str(_get(m, "league", default="") or _get(event, "league", default=""))
    sport_raw = str(_get(event, "sport", default=""))
    desc = str(_get(m, "description", default=""))
    mtype = str(_get(m, "marketType", "type", default=""))
    outs = _get(m, "outcomes", default=[]) or []
    try:
        yes, no = choose_yes_outcome(outs, mtype, desc or str(_get(event, "description", default="")))
    except ValueError:
        yes, no = (outs[0] if outs else {}), (outs[1] if len(outs) > 1 else {})
    starts = _ms_to_s(_get(m, "startsTs") or _get(event, "startsTs"))
    fee = _get(m, "fee", default={}) or {}
    info = parse_description(desc) if desc else {}
    ev_info = parse_description(str(_get(event, "description", default=""))) if event else {}
    home = info.get("home") or ev_info.get("home") or ""
    away = info.get("away") or ev_info.get("away") or ""
    strike = _get(m, "strike")
    meta: dict[str, Any] = {
        "status": str(_get(m, "status", default="")),
        "event_status": str(_get(event, "status", default="")),
        "league": league,
        "sport": LEAGUE_SPORT.get(league.upper(), sport_raw.lower()),
        "sport_raw": sport_raw,
        "market_type": mtype,
        "line_type": mtype.lower(),
        "strike": _num(strike) if strike is not None and str(strike) != "" else None,
        "voids": str(_get(m, "voids", default="")),
        "commence_ts": starts,
        "home": home,
        "away": away,
        "question": desc,
        "yes_outcome_id": str(_get(yes, "outcomeId", default="")),
        "no_outcome_id": str(_get(no, "outcomeId", default="")),
        "yes_name": str(_get(yes, "name", default="")),
        "no_name": str(_get(no, "name", default="")),
        "outcomes": [str(_get(yes, "name", default="")), str(_get(no, "name", default=""))],
        "outcome_ids": {str(_get(o, "outcomeId", default="")): str(_get(o, "name", default="")) for o in outs
                        if isinstance(o, dict)},
        "fee_coefficient": _num(_get(fee, "coefficient"), GAME_TAKER_COEFFICIENT),
        "maker_credit": _num(_get(fee, "makerCredit"), GAME_MAKER_CREDIT),
        "fee_charged": str(_get(fee, "charged", default="WHEN_LIVE")),
        "price_grid": "novig",
        "category": "sports",
    }
    result = _result_from_outcome(_get(yes, "status"))
    if result is None and _result_from_outcome(_get(no, "status")) is not None:
        result = 1.0 - _result_from_outcome(_get(no, "status"))  # type: ignore[operator]
    settled = str(_get(m, "status", default="")).upper() == "SETTLED"
    return Market(venue=Venue.NOVIG, market_id=mid, event_id=str(_get(m, "eventId", default="")),
                  series=league or mtype, title=info.get("title") or desc, open_ts=0.0, close_ts=starts,
                  tick=0.005, min_size=1.0 / QTY_PER_CONTRACT, result=result,
                  settle_ts=(time.time() if settled and result is not None else None), meta=meta)


def _orders_by_outcome(raw: dict) -> dict[str, list[tuple[float, float]]]:
    """{outcomeId: [(price, size)...]} from a REST book or WS snapshot."""
    orders = _get(raw, "orders", default={}) or {}
    out: dict[str, list[tuple[float, float]]] = {}
    for oid, lst in orders.items():
        lv: list[tuple[float, float]] = []
        for o in lst or []:
            p = _num(_get(o, "price"), -1.0)
            q = qty_to_size(_get(o, "qty"))
            if 0 < p < 1 and q > 0:
                lv.append((p, q))
        out[str(oid)] = lv
    return out


def _aggregate(levels: Iterable[tuple[float, float]]) -> dict[float, float]:
    agg: dict[float, float] = {}
    for p, s in levels:
        k = round(p, 6)
        agg[k] = agg.get(k, 0.0) + s
    return agg


def _assemble_book(market_id: str, ts: float, yes_levels: Iterable[tuple[float, float]],
                   no_levels: Iterable[tuple[float, float]]) -> Book:
    bids = [Level(p, s) for p, s in _aggregate(yes_levels).items() if s > 0]
    asks = [Level(round(1.0 - p, 6), s) for p, s in _aggregate(no_levels).items() if s > 0]
    bids.sort(key=lambda l: -l.price)
    asks.sort(key=lambda l: l.price)
    return Book(ts=ts, market_id=market_id, bids=bids, asks=asks)


def _yes_no_ids(market: Market | dict | None, raw_outcomes: Iterable[str]) -> tuple[str, str]:
    if isinstance(market, Market):
        y, n = market.meta.get("yes_outcome_id", ""), market.meta.get("no_outcome_id", "")
    elif isinstance(market, dict):
        y, n = str(market.get("yes_outcome_id", "")), str(market.get("no_outcome_id", ""))
    else:
        y = n = ""
    if y and n:
        return y, n
    ids = sorted(str(o) for o in raw_outcomes)
    if y and not n:
        n = next((i for i in ids if i != y), "")
    elif n and not y:
        y = next((i for i in ids if i != n), "")
    elif len(ids) >= 2:
        y, n = ids[0], ids[1]
    elif len(ids) == 1:
        y = ids[0]
    return y, n


def to_book(raw: dict, market: Market | dict | str, ts: float) -> Book:
    """GET /v3/catalog/markets/{id}/book -> core Book (YES leg). `market` is the
    core Market (for the YES/NO outcome ids) or a market id (ids then come from
    sorted outcome ids, which is only right if `to_market` chose the same)."""
    by = _orders_by_outcome(raw)
    if isinstance(market, str):
        mid = market
        yes_id, no_id = _yes_no_ids(None, by.keys())
    else:
        mid = market.market_id if isinstance(market, Market) else str(market.get("market_id", ""))
        yes_id, no_id = _yes_no_ids(market, by.keys())
    return _assemble_book(mid, ts, by.get(yes_id, []), by.get(no_id, []))


def to_trade(t: dict, market: Market | dict | str, ts_default: float = 0.0) -> Trade:
    """Tape row -> core Trade (see module docstring for the taker-side assumption)."""
    if isinstance(market, str):
        mid, yes_id = market, ""
    elif isinstance(market, Market):
        mid, yes_id = market.market_id, str(market.meta.get("yes_outcome_id", ""))
    else:
        mid, yes_id = str(market.get("market_id", "")), str(market.get("yes_outcome_id", ""))
    oid = str(_get(t, "outcomeId", "outcome", default=""))
    p = _num(_get(t, "price"), 0.0)
    size = qty_to_size(_get(t, "qty"))
    ts = _ms_to_s(_get(t, "ts", "timestamp"), ts_default) or ts_default
    if yes_id and oid != yes_id:
        return Trade(ts=ts, market_id=mid, price=round(1.0 - p, 6), size=size, taker_action=Action.SELL)
    return Trade(ts=ts, market_id=mid, price=p, size=size, taker_action=Action.BUY)


def to_trades(resp: dict, market: Market | dict | str) -> list[Trade]:
    return [to_trade(t, market) for t in (_get(resp, "items", "trades", default=[]) or [])]


# ----------------------------------------------------------------------------
# Order payloads (future live path; nothing calls them from the paper runner)
# ----------------------------------------------------------------------------
_TIF = {TIF.GTC: "GTC", TIF.IOC: "IOC", TIF.FOK: "FOK"}


def order_payload(order: Order, market: Market, client_id: Optional[str] = None,
                  ttl_ms: Optional[int] = None) -> dict:
    """Core YES-leg order -> POST /v3/orders body. BUY YES at p -> buy the YES
    outcome at p; SELL YES at p -> buy the NO outcome at 1-p. Prices snap DOWN
    to the grid (never pay more); post-only GTC -> tif PO."""
    if order.action is Action.BUY:
        outcome, px = market.meta["yes_outcome_id"], order.price
    else:
        outcome, px = market.meta["no_outcome_id"], 1.0 - order.price
    tif = "PO" if (order.post_only and order.tif is TIF.GTC) else _TIF[order.tif]
    body: dict[str, Any] = {"outcomeId": outcome, "price": price_str(snap_price(px, "down")),
                            "qty": size_to_qty(order.remaining), "tif": tif}
    if ttl_ms is not None:
        body["ttl"] = int(ttl_ms)
    if client_id:
        body["clientId"] = client_id
    return body


# ----------------------------------------------------------------------------
# REST client
# ----------------------------------------------------------------------------
class NovigClient:
    """Async REST client. Catalog reads work without `auth` through the
    `/v3/public/catalog/...` twins; everything else needs a signed key."""

    def __init__(self, auth: Optional[NovigAuth] = None, base: str = PAPER_BASE,
                 client: Optional[httpx.AsyncClient] = None, max_retries: int = 4, timeout: float = 15.0):
        self.auth = auth
        self.base = base.rstrip("/")
        self._own_client = client is None
        self._client = client or httpx.AsyncClient(timeout=timeout)
        self.max_retries = max_retries
        self._buckets = {k: TokenBucket(rate, cap) for k, (cap, rate) in THROTTLE.items()}
        self._markets: dict[str, Market] = {}
        self._events: dict[str, dict] = {}

    @classmethod
    def from_env(cls, env: Optional[dict] = None, **kw) -> "NovigClient":
        """`NOVIG_HOST` picks the environment (default paper)."""
        env = os.environ if env is None else env
        base = env.get("NOVIG_HOST") or PAPER_BASE
        return cls(auth=NovigAuth.from_env(env), base=base, **kw)

    @property
    def ws_url(self) -> str:
        return self.base.replace("https://", "wss://").replace("http://", "ws://") + WS_PATH

    async def aclose(self) -> None:
        if self._own_client:
            await self._client.aclose()

    async def __aenter__(self) -> "NovigClient":
        return self

    async def __aexit__(self, *exc) -> None:
        await self.aclose()

    @property
    def _path_prefix(self) -> str:
        return httpx.URL(self.base).path.rstrip("/")

    @staticmethod
    def _bucket_for(method: str, path: str) -> str:
        if path.startswith("/v3/history"):
            return "history"
        if method == "GET":
            return "read" if not path.startswith(("/v3/account", "/v3/keys")) else "account"
        if method == "DELETE" or path.endswith("cancel") or "/cancel" in path:
            return "cancel"
        if path.startswith("/v3/orders"):
            return "place"
        return "account"

    async def _request(self, method: str, path: str, *, params: Optional[dict] = None,
                       json_body: Optional[dict] = None, auth: bool = False, public_ok: bool = False) -> Any:
        method = method.upper()
        if self.auth is None:
            if public_ok and path.startswith("/v3/catalog/"):
                path = "/v3/public/catalog/" + path[len("/v3/catalog/"):]
            elif auth:
                raise NovigError(401, "endpoint requires auth; set NOVIG_API_KEY/NOVIG_SECRET", path)
        params = {k: v for k, v in (params or {}).items() if v is not None}
        query = str(httpx.QueryParams(params)) if params else ""
        url = f"{self.base}{path}" + (f"?{query}" if query else "")
        full_path = f"{self._path_prefix}{path}"
        body = json.dumps(json_body, separators=(",", ":")).encode() if json_body is not None else b""
        bucket = self._buckets[self._bucket_for(method, path)]
        for attempt in range(self.max_retries + 1):
            await bucket.acquire()
            headers = {"Accept": "application/json"}
            if body:
                headers["Content-Type"] = "application/json"
            if self.auth is not None:
                headers.update(self.auth.headers(method, full_path, query, body))
            resp = await self._client.request(method, url, content=body if body else None, headers=headers)
            if resp.status_code == 429 or resp.status_code in (502, 503, 504):
                if attempt < self.max_retries:
                    ra = resp.headers.get("Retry-After")
                    delay = _num(ra, 0.0) if ra else min(8.0, 0.5 * (2 ** attempt))
                    log.warning("Novig %s on %s; sleeping %.2fs", resp.status_code, path, delay)
                    await asyncio.sleep(delay)
                    continue
            if resp.status_code >= 400:
                try:
                    b = resp.json()
                except ValueError:
                    b = resp.text
                raise NovigError(resp.status_code, b, path)
            if not resp.content:
                return {}
            try:
                return resp.json()
            except ValueError:
                return {"raw": resp.text}
        raise NovigError(429, "retries exhausted", path)

    # -- catalog ---------------------------------------------------------------
    async def _page_all(self, path: str, params: dict, max_pages: int) -> list[dict]:
        out: list[dict] = []
        after = None
        for _ in range(max_pages):
            page = await self._request("GET", path, params=dict(params, after=after), public_ok=True)
            out.extend(_get(page, "items", default=[]) or [])
            after = _get(page, "next")
            if not after:
                break
        return out

    async def get_sports(self) -> list:
        r = await self._request("GET", "/v3/types/sports", public_ok=True)
        return _get(r, "items", default=r) or []

    async def get_leagues(self) -> list:
        r = await self._request("GET", "/v3/types/leagues", public_ok=True)
        return _get(r, "items", default=r) or []

    async def get_market_types(self) -> list:
        r = await self._request("GET", "/v3/types/markets", public_ok=True)
        return _get(r, "items", default=r) or []

    async def get_events(self, league: Optional[str | Iterable[str]] = None, status: Optional[str | Iterable[str]] = None,
                         starts_after_ms: Optional[int] = None, starts_before_ms: Optional[int] = None,
                         limit: int = 500, after: Optional[str] = None) -> dict:
        params = {"league": _csv(league), "status": _csv(status), "startsAfter": starts_after_ms,
                  "startsBefore": starts_before_ms, "limit": min(limit, MAX_PAGE), "after": after}
        return await self._request("GET", "/v3/catalog/events", params=params, public_ok=True)

    async def iter_events(self, max_pages: int = 10, **kw) -> list[dict]:
        params = {"league": _csv(kw.get("league")), "status": _csv(kw.get("status")),
                  "startsAfter": kw.get("starts_after_ms"), "startsBefore": kw.get("starts_before_ms"),
                  "limit": min(kw.get("limit", 500), MAX_PAGE)}
        evs = await self._page_all("/v3/catalog/events", params, max_pages)
        for e in evs:
            self._events[str(_get(e, "eventId", default=""))] = e
        return evs

    async def get_event(self, event_id: str) -> dict:
        if event_id in self._events:
            return self._events[event_id]
        e = await self._request("GET", f"/v3/catalog/events/{event_id}", public_ok=True)
        self._events[event_id] = e
        return e

    async def get_markets(self, league: Optional[str | Iterable[str]] = None,
                          market_type: Optional[str | Iterable[str]] = None,
                          event_status: Optional[str | Iterable[str]] = None, event: Optional[str] = None,
                          starts_after_ms: Optional[int] = None, starts_before_ms: Optional[int] = None,
                          limit: int = 500, after: Optional[str] = None) -> dict:
        params = {"league": _csv(league), "marketType": _csv(market_type), "eventStatus": _csv(event_status),
                  "event": event, "startsAfter": starts_after_ms, "startsBefore": starts_before_ms,
                  "limit": min(limit, MAX_PAGE), "after": after}
        return await self._request("GET", "/v3/catalog/markets", params=params, public_ok=True)

    async def iter_markets(self, max_pages: int = 10, **kw) -> list[dict]:
        params = {"league": _csv(kw.get("league")), "marketType": _csv(kw.get("market_type")),
                  "eventStatus": _csv(kw.get("event_status")), "event": kw.get("event"),
                  "startsAfter": kw.get("starts_after_ms"), "startsBefore": kw.get("starts_before_ms"),
                  "limit": min(kw.get("limit", 500), MAX_PAGE)}
        return await self._page_all("/v3/catalog/markets", params, max_pages)

    async def get_market(self, market_id: str) -> dict:
        return await self._request("GET", f"/v3/catalog/markets/{market_id}", public_ok=True)

    async def get_orderbook(self, market_id: str, depth: int = MAX_BOOK_DEPTH) -> dict:
        depth = max(1, min(int(depth), MAX_BOOK_DEPTH))
        return await self._request("GET", f"/v3/catalog/markets/{market_id}/book", params={"depth": depth},
                                   public_ok=True)

    async def get_trades(self, market_id: str, limit: int = 500, after: Optional[str] = None) -> dict:
        return await self._request("GET", f"/v3/catalog/markets/{market_id}/trades",
                                   params={"limit": min(limit, MAX_PAGE), "after": after}, public_ok=True)

    # -- account / portfolio (signed) ------------------------------------------
    async def echo(self, body: Optional[dict] = None) -> dict:
        return await self._request("POST", "/v3/echo", json_body=body or {"hello": "world"}, auth=True)

    async def get_limits(self) -> dict:
        return await self._request("GET", "/v3/limits", auth=True)

    async def get_balance(self) -> dict:
        return await self._request("GET", "/v3/account/balance", auth=True)

    async def get_subaccounts(self) -> dict:
        return await self._request("GET", "/v3/account/subaccounts", auth=True)

    async def get_orders(self, **params) -> dict:
        return await self._request("GET", "/v3/portfolio/orders", params=params, auth=True)

    async def get_resting_orders(self) -> dict:
        return await self._request("GET", "/v3/portfolio/orders/resting", auth=True)

    async def get_fills(self, **params) -> dict:
        return await self._request("GET", "/v3/portfolio/fills", params=params, auth=True)

    async def get_positions(self, **params) -> dict:
        return await self._request("GET", "/v3/portfolio/positions", params=params, auth=True)

    async def create_order(self, order: Order, market: Market, client_id: Optional[str] = None,
                           ttl_ms: Optional[int] = None) -> dict:
        """Live order placement (NOT used by the paper runner)."""
        return await self._request("POST", "/v3/orders", json_body=order_payload(order, market, client_id, ttl_ms),
                                   auth=True)

    async def cancel_order(self, order_id: str) -> dict:
        return await self._request("DELETE", f"/v3/orders/{order_id}", auth=True)

    async def cancel_all(self, market_id: Optional[str] = None) -> dict:
        return await self._request("POST", "/v3/orders/cancel-all", json_body={"marketId": market_id} if market_id
                                   else {}, auth=True)

    # -- convenience (the surface the paper runner uses) ------------------------
    async def market(self, market_id: str) -> Market:
        raw = await self.get_market(market_id)
        ev = None
        eid = str(_get(raw, "eventId", default=""))
        if eid:
            try:
                ev = await self.get_event(eid)
            except NovigError as e:
                log.warning("event %s lookup failed: %s", eid, e)
        m = to_market(raw, ev)
        self._markets[m.market_id] = m
        return m

    def cached_market(self, market_id: str) -> Optional[Market]:
        return self._markets.get(market_id)

    async def book(self, market_id: str, depth: int = MAX_BOOK_DEPTH, ts: Optional[float] = None) -> Book:
        raw = await self.get_orderbook(market_id, depth)
        m = self._markets.get(market_id)
        if m is None:
            m = await self.market(market_id)
        return to_book(raw, m, ts if ts is not None else time.time())

    async def trades_since(self, market_id: str, since_ts: float, max_pages: int = 3) -> list[Trade]:
        """Public tape since `since_ts` (epoch s), oldest first. Pages are
        newest-first so paging stops once a page's oldest print is older."""
        m = self._markets.get(market_id) or await self.market(market_id)
        out: list[Trade] = []
        after = None
        for _ in range(max_pages):
            page = await self.get_trades(market_id, after=after)
            items = _get(page, "items", default=[]) or []
            trades = [to_trade(t, m) for t in items]
            out.extend(t for t in trades if t.ts > since_ts)
            after = _get(page, "next")
            if not after or not trades or min(t.ts for t in trades) <= since_ts:
                break
        out.sort(key=lambda t: t.ts)
        return out

    async def fee_schedule(self, market_id: str, live: Optional[bool] = None) -> FeeSchedule:
        m = self._markets.get(market_id) or await self.market(market_id)
        if live is None:
            st = str(m.meta.get("event_status", "")).upper()
            live = True if st == "OPEN_INGAME" else (False if st in ("OPEN_PREGAME", "CLOSED_PREGAME") else None)
        return fee_schedule_for(m, live=live)

    async def list_markets(self, league: str | Iterable[str] = "NFL", market_type: str | Iterable[str] = "MONEY",
                           event_status: str | Iterable[str] = "OPEN_PREGAME", max_pages: int = 5) -> list[Market]:
        """Open markets of a league/type as core Markets, events attached."""
        raws = await self.iter_markets(league=league, market_type=market_type, event_status=event_status,
                                       max_pages=max_pages)
        eids = {str(_get(r, "eventId", default="")) for r in raws} - {""}
        missing = [e for e in eids if e not in self._events]
        if missing:
            try:
                await self.iter_events(league=league, status=event_status, max_pages=max_pages)
            except NovigError as e:
                log.warning("event listing failed: %s", e)
        out: list[Market] = []
        for r in raws:
            m = to_market(r, self._events.get(str(_get(r, "eventId", default=""))))
            if not m.market_id:
                continue
            if m.meta.get("yes_outcome_id") and m.meta.get("no_outcome_id"):
                self._markets[m.market_id] = m
                out.append(m)
        return out

    async def select_markets(self, league: str | Iterable[str] = "NFL", top: int = 6,
                             market_type: str | Iterable[str] = "MONEY", min_secs_to_start: float = 600.0,
                             now: Optional[float] = None) -> list[Market]:
        """Soonest-starting open pregame markets (Novig voids every resting
        order at GOLIVE, so pregame is the maker window)."""
        now = time.time() if now is None else now
        ms = await self.list_markets(league, market_type)
        ms = [m for m in ms if str(m.meta.get("status", "OPEN")).upper() == "OPEN"
              and (not m.close_ts or m.close_ts - now > min_secs_to_start)]
        ms.sort(key=lambda m: (m.close_ts or float("inf"), m.market_id))
        return ms[:top]

    async def enrich(self, markets: list[Market]) -> list[Market]:
        for m in markets:
            if m.meta.get("event_status") or not m.event_id:
                continue
            try:
                ev = await self.get_event(m.event_id)
            except NovigError as e:
                log.warning("event %s lookup failed: %s", m.event_id, e)
                continue
            m.meta["event_status"] = str(_get(ev, "status", default=""))
            if not m.meta.get("sport"):
                m.meta["sport"] = LEAGUE_SPORT.get(str(_get(ev, "league", default="")).upper(),
                                                   str(_get(ev, "sport", default="")).lower())
        return markets


def _csv(v: Any) -> Optional[str]:
    if v is None:
        return None
    if isinstance(v, str):
        return v
    return ",".join(str(x) for x in v)


# ----------------------------------------------------------------------------
# WebSocket
# ----------------------------------------------------------------------------
@dataclass(slots=True)
class RawMessage:
    ts: float
    type: str
    msg: dict


class BookState:
    """Order-level book for one Novig market: order id -> (outcome, price, size)."""

    def __init__(self, market_id: str, yes_id: str = "", no_id: str = ""):
        self.market_id = market_id
        self.yes_id, self.no_id = yes_id, no_id
        self.orders: dict[str, tuple[str, float, float]] = {}
        self.seq: Optional[int] = None
        self.ready = False
        self.status = ""

    def _ensure_ids(self) -> None:
        if self.yes_id and self.no_id:
            return
        outs = {o for o, _, _ in self.orders.values()}
        self.yes_id, self.no_id = _yes_no_ids({"yes_outcome_id": self.yes_id, "no_outcome_id": self.no_id}, outs)

    def snapshot(self, msg: dict) -> None:
        self.orders = {}
        for oid, lst in (_get(msg, "orders", default={}) or {}).items():
            for o in lst or []:
                order_id = str(_get(o, "order", "orderId", default=""))
                p, q = _num(_get(o, "price"), -1.0), qty_to_size(_get(o, "qty"))
                if order_id and 0 < p < 1 and q > 0:
                    self.orders[order_id] = (str(oid), p, q)
        self.ready = True

    def delta(self, deltas: list[dict]) -> None:
        for d in deltas or []:
            kind = str(_get(d, "kind", default="")).lower()
            order_id = str(_get(d, "order", "orderId", default=""))
            if kind == "add":
                p, q = _num(_get(d, "price"), -1.0), qty_to_size(_get(d, "qty"))
                if order_id and 0 < p < 1 and q > 0:
                    self.orders[order_id] = (str(_get(d, "outcome", "outcomeId", default="")), p, q)
            elif kind == "remove":
                self.orders.pop(order_id, None)

    def to_book(self, ts: float) -> Book:
        self._ensure_ids()
        yes = [(p, q) for o, p, q in self.orders.values() if o == self.yes_id]
        no = [(p, q) for o, p, q in self.orders.values() if o == self.no_id]
        return _assemble_book(self.market_id, ts, yes, no)


def _seq_ok(state: BookState, seq: Any) -> bool:
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


class NovigWS:
    """Novig WebSocket feed with the same `events()` / `subscribe_more()`
    surface as `KalshiWS`. Yields `Book`, `Trade`, `RawMessage`.

    Needs a `trading` or `trading::read` key (the upgrade is signed). Without
    `auth` the paper runner polls REST instead."""

    def __init__(self, markets: Iterable[Market | str], auth: Optional[NovigAuth] = None, url: str = PAPER_WS,
                 channels: Iterable[str] = ("book", "trades"), private: Iterable[str] = (),
                 connect: Optional[Callable[..., Awaitable[Any]]] = None,
                 clock: Callable[[], float] = time.time, reconnect_delay: float = 2.0):
        self.auth = auth
        self.url = url
        self.channels = list(channels)
        self.private = list(private)
        self._connect = connect or _default_ws_connect
        self.clock = clock
        self.reconnect_delay = reconnect_delay
        self.books: dict[str, BookState] = {}
        self.market_ids: list[str] = []
        self._nonce = 0
        self.stopped = False
        self._sock: Any = None
        self._pending: dict[int, str] = {}
        for m in markets:
            self._add(m)

    def _add(self, m: Market | str) -> bool:
        if isinstance(m, Market):
            mid, y, n = m.market_id, str(m.meta.get("yes_outcome_id", "")), str(m.meta.get("no_outcome_id", ""))
        else:
            mid, y, n = str(m), "", ""
        if mid in self.books:
            return False
        self.books[mid] = BookState(mid, y, n)
        self.market_ids.append(mid)
        return True

    def _auth_headers(self) -> dict[str, str]:
        if self.auth is None:
            return {}
        path = httpx.URL(self.url.replace("wss://", "https://").replace("ws://", "http://")).path
        return self.auth.headers("GET", path or WS_PATH)

    def subscribe_payloads(self, market_ids: Optional[Iterable[str]] = None) -> list[dict]:
        """One `subscribe` frame per channel (the `markets` map holds one
        channel per id); private channels ride on the first frame."""
        ids = list(market_ids if market_ids is not None else self.market_ids)
        out: list[dict] = []
        for i, ch in enumerate(self.channels):
            self._nonce += 1
            sub: dict[str, Any] = {"markets": {mid: ch for mid in ids}}
            if i == 0 and self.private:
                sub["private"] = list(self.private)
            out.append({"nonce": self._nonce, "subscribe": sub})
            self._pending[self._nonce] = ch
        if not out and self.private:
            self._nonce += 1
            out.append({"nonce": self._nonce, "subscribe": {"private": list(self.private)}})
        return out

    async def stop(self) -> None:
        self.stopped = True
        if self._sock is not None:
            try:
                await self._sock.close()
            except Exception:
                pass

    async def subscribe_more(self, markets: Iterable[Market | str]) -> list[str]:
        new = [m.market_id if isinstance(m, Market) else str(m) for m in markets if self._add(m)]
        if new and self._sock is not None and not self.stopped:
            try:
                for payload in self.subscribe_payloads(new):
                    await self._sock.send(json.dumps(payload))
            except Exception as e:  # pragma: no cover - socket races
                log.warning("Novig WS late subscribe failed (%s); will resubscribe on reconnect", e)
        return new

    async def events(self) -> AsyncIterator[Book | Trade | RawMessage]:
        while not self.stopped:
            try:
                self._sock = await self._connect(self.url, self._auth_headers())
                for payload in self.subscribe_payloads():
                    await self._sock.send(json.dumps(payload))
                async for ev in self._consume(self._sock):
                    yield ev
            except asyncio.CancelledError:
                raise
            except Exception as e:
                if self.stopped:
                    return
                log.warning("Novig WS error: %s; reconnecting in %.1fs", e, self.reconnect_delay)
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

    # -- parsing ---------------------------------------------------------------
    @staticmethod
    def _market_of(d: dict) -> str:
        mid = _get(d, "market", "marketId", "market_id")
        if mid:
            return str(mid)
        subj = str(_get(d, "subject", default=""))
        if subj.startswith("market:"):
            return subj.split(":", 1)[1]
        return ""

    def handle_raw(self, raw: str | bytes | dict) -> list[Book | Trade | RawMessage]:
        if isinstance(raw, bytes):
            try:
                import zlib

                raw = zlib.decompress(raw, -15)
            except zlib.error:
                pass
        if isinstance(raw, (str, bytes)):
            try:
                data = json.loads(raw)
            except ValueError:
                return []
        else:
            data = raw
        if not isinstance(data, dict):
            return []
        now = self.clock()
        out: list[Book | Trade | RawMessage] = []
        if "error" in data or _get(data, "code") is not None and "message" in data:
            log.warning("Novig WS error frame: %s", data)
            return [RawMessage(now, "error", data)]
        # {"markets": {"<id>": {"book": ..., "trades": ...}}} or a flat frame with a market key
        nested = _get(data, "markets")
        handled = False
        if isinstance(nested, dict) and not any(k in data for k in ("book", "trades", "lifecycle")):
            for mid, payload in nested.items():
                if isinstance(payload, dict):
                    handled = True
                    out.extend(self._handle_market(str(mid), payload, now))
        elif any(k in data for k in ("book", "trades", "lifecycle", "bbo")):
            handled = True
            out.extend(self._handle_market(self._market_of(data), data, now))
        for key in ("orders", "positions"):
            if isinstance(data.get(key), dict):
                handled = True
                out.append(RawMessage(now, key, data[key]))
        if not out and (handled or "nonce" in data):
            return []  # ack, or a delta before its snapshot
        if not out:
            out.append(RawMessage(now, str(_get(data, "type", default="unknown")), data))
        return out

    def _handle_market(self, mid: str, payload: dict, now: float) -> list[Book | Trade | RawMessage]:
        out: list[Book | Trade | RawMessage] = []
        if not mid:
            if len(self.books) == 1:
                mid = next(iter(self.books))
            else:
                log.warning("Novig WS frame without market id: %s", list(payload)[:4])
                return [RawMessage(now, "unplaced", payload)]
        st = self.books.setdefault(mid, BookState(mid))
        book = payload.get("book")
        if isinstance(book, dict):
            if "orders" in book:
                _seq_ok(st, _get(book, "seq"))
                st.snapshot(book)
                out.append(st.to_book(now))
            elif "deltas" in book:
                if not _seq_ok(st, _get(book, "seq")):
                    log.warning("seq gap on %s; book may be stale until next snapshot", mid)
                if st.ready:
                    st.delta(book.get("deltas") or [])
                    out.append(st.to_book(now))
        trades = payload.get("trades")
        if isinstance(trades, dict):
            st._ensure_ids()
            ref = {"market_id": mid, "yes_outcome_id": st.yes_id}
            batches = trades.get("trades") if isinstance(trades.get("trades"), list) else [trades]
            for b in batches:
                for t in (b.get("deltas") or []) if isinstance(b, dict) else []:
                    tr = to_trade(t, ref, now)
                    out.append(tr)
        lc = payload.get("lifecycle")
        if isinstance(lc, dict):
            if "status" in lc:
                st.status = str(lc["status"])
            for tr in lc.get("deltas") or []:
                if tr in ("GOLIVE", "CLOSE", "GRADE"):
                    st.orders = {}  # GOLIVE voids every resting order
                    out.append(st.to_book(now))
                st.status = {"OPEN": "OPEN", "CLOSE": "CLOSED", "GRADE": "SETTLED"}.get(tr, st.status)
            out.append(RawMessage(now, "lifecycle", {"market": mid, **lc}))
        return out


async def _default_ws_connect(url: str, headers: dict[str, str]) -> Any:
    import websockets  # local import: optional at test time

    return await websockets.connect(url, additional_headers=headers, ping_interval=None, max_size=2 ** 24)


__all__ = [
    "PAPER_BASE", "PROD_BASE", "PAPER_WS", "PROD_WS", "PRICE_GRID", "QTY_PER_CONTRACT", "NovigAuth", "NovigClient",
    "NovigError", "NovigWS", "BookState", "RawMessage", "TokenBucket", "canonical_query", "canonical_string",
    "verify_signature", "snap_price", "on_grid", "price_str", "american_to_prob", "decimal_to_prob",
    "prob_to_american", "prob_to_decimal", "devig_two_way", "qty_to_size", "size_to_qty", "novig_schedule",
    "fee_schedule_for", "to_market", "to_book", "to_trade", "to_trades", "order_payload", "parse_description",
    "choose_yes_outcome",
]
