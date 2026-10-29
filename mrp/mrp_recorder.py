#!/usr/bin/env python3
"""
Mr. P — Recorder v0  (raw capture; parsing happens offline in mrp_analyze.py)

Captures, for the Polymarket US 15-minute BTC Up/Down market, everything needed to
answer the three entry gates empirically:

  1. SETTLEMENT gate  — the BRTI 1-second index (the exact series both venues settle on)
                        plus the running 60-sample settlement average in each window's
                        final minute, and the "average the remaining samples would need"
                        to flip the result.
  2. PRICE gate       — the live window's full order book at 1 Hz in the final N seconds
                        (10 s cadence before that), plus the next window's book.
  3. EXECUTION gate   — market state transitions (OPEN / SUSPENDED / HALTED /
                        MATCH_AND_CLOSE_AUCTION / EXPIRED ...) with timestamps.

Layers
  A  Polymarket US public REST   — NO KEYS NEEDED. Always on.
  B  Kalshi WebSocket            — on when KALSHI_KEY_ID + KALSHI_PRIVATE_KEY_PATH are set.
                                   Streams CF Benchmarks BRTI (push, 1/s, with Kalshi's own
                                   running 60 s average) + KXBTC15M order books.
  C  Polymarket US WebSocket     — on when POLYMARKET_KEY_ID + POLYMARKET_SECRET_KEY are set.
                                   Full book push for the live + next window.

Storage: JSONL, one file per UTC hour:  DATA_DIR/YYYY-MM-DD/HH.jsonl
Each line: {"t": <recv unix ms>, "k": <kind>, "d": <payload>}

Run:  python3 mrp_recorder.py            (Ctrl-C to stop; safe to restart any time)
Env:  see .env.example
"""
from __future__ import annotations

import asyncio
import base64
import json
import os
import signal
import sys
import threading
import time
import traceback
from datetime import datetime, timezone
from typing import Any, Optional

import requests

# ----------------------------------------------------------------------------- .env (optional, no dependency)
def _load_dotenv(path: str = os.environ.get("MRP_ENV_FILE", ".env")) -> None:
    """KEY=VALUE lines; '#' comments; optional quotes. Never overrides variables already set."""
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and v:
                    os.environ.setdefault(k, v)
    except FileNotFoundError:
        pass


_load_dotenv()

# ----------------------------------------------------------------------------- config
DATA_DIR = os.environ.get("MRP_DATA_DIR", "./data")
# Public (unauthenticated) endpoints are served by the gateway host; api.polymarket.us is for signed calls.
PMUS_BASE = os.environ.get("PMUS_BASE_URL", "https://gateway.polymarket.us")
BOOK_HOT_SECONDS = int(os.environ.get("MRP_BOOK_HOT_SECONDS", "180"))   # 1 Hz book polling inside this
BOOK_COLD_INTERVAL = float(os.environ.get("MRP_BOOK_COLD_INTERVAL", "10"))
IDX_INTERVAL = float(os.environ.get("MRP_IDX_INTERVAL", "1.0"))
DISCOVERY_INTERVAL = 60.0
SETTLE_POLL_INTERVAL = 5.0
SETTLE_POLL_MAX_SECONDS = 15 * 60
WINDOW = 900  # seconds

KALSHI_KEY_ID = os.environ.get("KALSHI_KEY_ID")
KALSHI_PRIVATE_KEY_PATH = os.environ.get("KALSHI_PRIVATE_KEY_PATH")
# Same conventions as pb/venues/kalshi.py: PEM text (with literal "\n" allowed) or base64 PEM.
KALSHI_PRIVATE_KEY_PEM = os.environ.get("KALSHI_PRIVATE_KEY_PEM")
KALSHI_PRIVATE_KEY_B64 = os.environ.get("KALSHI_PRIVATE_KEY_B64")
KALSHI_ON = bool(KALSHI_KEY_ID and (KALSHI_PRIVATE_KEY_PATH or KALSHI_PRIVATE_KEY_PEM or KALSHI_PRIVATE_KEY_B64))
KALSHI_REST = os.environ.get("KALSHI_REST_URL", "https://external-api.kalshi.com")
KALSHI_WS_URL = os.environ.get("KALSHI_WS_URL", "wss://external-api-ws.kalshi.com/trade-api/ws/v2")
KALSHI_SERIES = os.environ.get("KALSHI_SERIES", "KXBTC15M")

PM_KEY_ID = os.environ.get("POLYMARKET_KEY_ID")
PM_SECRET = os.environ.get("POLYMARKET_SECRET_KEY")

STOP = threading.Event()
WS_DROPPED: dict[str, int] = {}      # throttled WebSocket frames, by kind (reported in the status line)


# ----------------------------------------------------------------------------- helpers
def now_ms() -> int:
    return int(time.time() * 1000)


def parse_ts(v: Any) -> Optional[float]:
    """ISO string / epoch s / epoch ms / {seconds: ..} -> unix seconds (float)."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v) / 1000.0 if v > 1e11 else float(v)
    if isinstance(v, dict):
        s = v.get("seconds") or v.get("unixSeconds")
        return float(s) if s is not None else None
    if isinstance(v, str):
        s = v.strip()
        if s.isdigit():
            return parse_ts(int(s))
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(s).timestamp()
        except ValueError:
            return None
    return None


def parse_amount(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, dict):
        v = v.get("value")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def window_start(ts: float) -> int:
    return int(ts // WINDOW) * WINDOW


def gen_slug(start: int) -> str:
    d = datetime.fromtimestamp(start, tz=timezone.utc)
    return f"cpc-btc-updown-15m-{d:%Y-%m-%d-%H%M}z"


# ----------------------------------------------------------------------------- writer
class Writer:
    """Thread-safe JSONL writer, one file per UTC hour. Flushes every line (crash-safe)."""

    def __init__(self, root: str):
        self.root = root
        self.lock = threading.Lock()
        self.fh = None
        self.fh_key = None
        self.count = 0

    ROTATE_BYTES = int(os.environ.get("MRP_ROTATE_BYTES", str(40 * 1024 * 1024)))

    def _file_for(self, t_ms: int):
        d = datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc)
        key = (d.strftime("%Y-%m-%d"), d.strftime("%H"))
        if key != self.fh_key or (self.fh and self.fh.tell() > self.ROTATE_BYTES):
            if self.fh:
                self.fh.close()
            path = os.path.join(self.root, key[0])
            os.makedirs(path, exist_ok=True)
            # HH.jsonl, then HH.1.jsonl, HH.2.jsonl ... once a part passes ROTATE_BYTES
            n = 0
            while True:
                name = f"{key[1]}.jsonl" if n == 0 else f"{key[1]}.{n}.jsonl"
                full = os.path.join(path, name)
                if not os.path.exists(full) or os.path.getsize(full) < self.ROTATE_BYTES:
                    break
                n += 1
            self.fh = open(full, "a", buffering=1, encoding="utf-8")
            self.fh_key = key
        return self.fh

    def write(self, kind: str, payload: Any, t_ms: Optional[int] = None):
        t_ms = t_ms or now_ms()
        line = json.dumps({"t": t_ms, "k": kind, "d": payload}, separators=(",", ":"), default=str)
        with self.lock:
            fh = self._file_for(t_ms)
            fh.write(line + "\n")
            self.count += 1

    def err(self, where: str, exc: BaseException):
        self.write("err", {"where": where, "type": type(exc).__name__, "msg": str(exc)[:500]})


W = Writer(DATA_DIR)


def log(msg: str):
    print(f"[{datetime.now(timezone.utc):%H:%M:%S}Z] {msg}", flush=True)


# ----------------------------------------------------------------------------- Polymarket US public REST
class PMUS:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers["User-Agent"] = "mrp-recorder/0.1"
        self.backoff_until = 0.0

    def get(self, path: str, params: Optional[dict] = None, timeout: float = 6.0) -> Any:
        if time.time() < self.backoff_until:
            raise RuntimeError("backoff")
        r = self.s.get(PMUS_BASE + path, params=params, timeout=timeout)
        if r.status_code == 429:
            self.backoff_until = time.time() + 2.0
            raise RuntimeError("429 rate limited")
        r.raise_for_status()
        return r.json()

    # --- markets
    def markets_by_slugs(self, slugs: list[str]) -> dict[str, dict]:
        out = {}
        if not slugs:
            return out
        data = self.get("/v1/markets", params=[("slug", s) for s in slugs] + [("limit", 50)])
        for m in data.get("markets", []):
            out[m.get("slug")] = m
        return out

    def market_by_slug(self, slug: str) -> Optional[dict]:
        try:
            data = self.get(f"/v1/market/slug/{slug}")
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                return None
            raise
        return data.get("market", data)

    def discover_btc15m(self, max_pages: int = 6) -> dict[int, dict]:
        """Broad discovery of all open 15m BTC up/down windows -> {window_start: market}."""
        found: dict[int, dict] = {}
        for page in range(max_pages):
            data = self.get("/v1/markets", params={"categories": "crypto", "closed": "false",
                                                   "limit": 200, "offset": page * 200})
            ms = data.get("markets", [])
            for m in ms:
                apt = m.get("assetPriceTerms") or {}
                if apt.get("marketType") != "ASSET_PRICE_MARKET_TYPE_UP_DOWN":
                    continue
                if (apt.get("asset") or {}).get("symbol", "").lower() != "btc":
                    continue
                if str(apt.get("horizon", "")).lower() != "15m":
                    continue
                ws = parse_ts(apt.get("windowStart"))
                if ws is None:
                    continue
                found[int(ws)] = m
            if len(ms) < 200:
                break
        return found

    def book(self, slug: str) -> dict:
        return self.get(f"/v1/markets/{slug}/book").get("marketData", {})

    def settlement(self, slug: str) -> Optional[dict]:
        try:
            return self.get(f"/v1/markets/{slug}/settlement")
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code in (404, 400):
                return None
            raise

    def brti_candles(self, frm: int, to: int = 0, bucket: str = "ASSET_PRICE_BUCKET_1S") -> list[dict]:
        data = self.get("/v1/asset-prices/history",
                        params={"assets": "crypto:btc", "from": frm, "to": to, "bucket": bucket},
                        timeout=8.0)
        for series in data.get("series", []):
            a = series.get("asset") or {}
            if str(a.get("symbol", "")).lower() == "btc":
                return series.get("candles", [])
        return []


PM = PMUS()


# ----------------------------------------------------------------------------- shared state
class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.markets: dict[int, dict] = {}        # window_start -> market object (latest)
        self.slug_pattern_ok: Optional[bool] = None
        self.last_book_state: dict[str, str] = {}
        self.brti: dict[int, float] = {}          # ts(sec) -> close  (bounded, see prune)
        self.brti_n: dict[int, int] = {}
        self.last_brti: Optional[tuple[int, float]] = None
        self.settled: set[str] = set()

    def market_for(self, start: int) -> Optional[dict]:
        with self.lock:
            return self.markets.get(start)

    def ptb(self, start: int) -> Optional[float]:
        m = self.market_for(start)
        if not m:
            return None
        return parse_amount((m.get("assetPriceTerms") or {}).get("priceToBeat"))

    def slug_for(self, start: int) -> str:
        m = self.market_for(start)
        return m.get("slug") if m else gen_slug(start)

    def prune_brti(self, keep_seconds: int = 7200):
        cut = int(time.time()) - keep_seconds
        with self.lock:
            for k in [k for k in self.brti if k < cut]:
                self.brti.pop(k, None)
                self.brti_n.pop(k, None)


S = State()


# ----------------------------------------------------------------------------- thread: discovery / market meta
def _market_fingerprint(m: dict) -> str:
    apt = m.get("assetPriceTerms") or {}
    return json.dumps({
        "ptb": apt.get("priceToBeat"), "sp": apt.get("settlementPrice"),
        "active": m.get("active"), "closed": m.get("closed"), "status": m.get("status"),
        "tick": m.get("orderPriceMinTickSize"), "minq": m.get("minimumTradeQty"),
    }, sort_keys=True, default=str)


def discovery_loop():
    fps: dict[str, str] = {}
    first = True
    while not STOP.is_set():
        t0 = time.time()
        try:
            now = time.time()
            starts = [window_start(now) + i * WINDOW for i in range(-1, 4)]   # prev, live, next 3
            found: dict[int, dict] = {}
            if first or int(now) % 600 < DISCOVERY_INTERVAL:
                found = PM.discover_btc15m()
                gen = {gen_slug(s) for s in starts}
                disc = {m.get("slug") for m in found.values()}
                ok = bool(gen & disc)
                if S.slug_pattern_ok != ok:
                    S.slug_pattern_ok = ok
                    W.write("rec.slug_pattern", {"generated_ok": ok, "sample_discovered": sorted(disc)[:5]})
                    log(f"slug pattern {'OK' if ok else 'MISMATCH'}: discovered {len(disc)} windows")
            # targeted refresh of the windows we care about (cheap, precise)
            slugs = [S.slug_for(s) for s in starts]
            by_slug = PM.markets_by_slugs(slugs)
            for s in starts:
                m = by_slug.get(S.slug_for(s)) or found.get(s)
                if m is None and first:
                    m = PM.market_by_slug(gen_slug(s))
                if m:
                    found[s] = m
            with S.lock:
                for s, m in found.items():
                    S.markets[s] = m
                for s in [k for k in S.markets if k < window_start(now) - 2 * WINDOW]:
                    S.markets.pop(s, None)
            for s, m in found.items():
                fp = _market_fingerprint(m)
                if fps.get(m.get("slug")) != fp:
                    fps[m.get("slug")] = fp
                    W.write("pmus.market", m)
            first = False
        except Exception as e:  # noqa
            W.err("discovery", e)
            log(f"discovery error: {e}")
        STOP.wait(max(0.0, DISCOVERY_INTERVAL - (time.time() - t0)))


# ----------------------------------------------------------------------------- thread: BRTI index poller
def index_loop():
    """Polls the public 1-second BRTI candle series (the settlement index) ~1 Hz, logs new
    candles, and in each window's final minute logs the running settlement average."""
    while not STOP.is_set():
        t0 = time.time()
        try:
            frm = int(t0) - 20
            candles = PM.brti_candles(frm, 0)
            new = 0
            with S.lock:
                for c in candles:
                    ts = int(c.get("timestamp", 0))
                    n = int(c.get("tickCount", 0) or 0)
                    if n <= 0:
                        continue  # gap-filled bucket: not a real print
                    close = float(c["close"])
                    if S.brti.get(ts) != close or S.brti_n.get(ts) != n:
                        S.brti[ts] = close
                        S.brti_n[ts] = n
                        new += 1
                        W.write("pmus.idx", {"ts": ts, "o": c.get("open"), "h": c.get("high"),
                                             "l": c.get("low"), "c": c.get("close"), "n": n})
                if S.brti:
                    k = max(S.brti)
                    S.last_brti = (k, S.brti[k])
            # running settlement average for the live window, final ~70 s
            live = window_start(t0)
            end = live + WINDOW
            rem = end - t0
            if rem <= 70:
                ptb = S.ptb(live)
                with S.lock:
                    pts = [(ts, S.brti[ts]) for ts in range(end - 60, end) if ts in S.brti]
                k = len(pts)
                tot = sum(v for _, v in pts)
                rec = {"slug": S.slug_for(live), "end": end, "rem": round(rem, 2), "n_done": k,
                       "sum_done": round(tot, 2), "avg_done": round(tot / k, 2) if k else None,
                       "ptb": ptb, "last": S.last_brti}
                if ptb is not None and k < 60:
                    # average the remaining (60-k) samples would need to flip the current leader
                    rec["need_rem_avg"] = round((60 * ptb - tot) / (60 - k), 2)
                    if S.last_brti:
                        rec["need_rem_move"] = round(rec["need_rem_avg"] - S.last_brti[1], 2)
                W.write("pmus.settle_avg", rec)
            if int(t0) % 300 == 0:
                S.prune_brti()
        except Exception as e:  # noqa
            W.err("index", e)
        STOP.wait(max(0.05, IDX_INTERVAL - (time.time() - t0)))


# ----------------------------------------------------------------------------- thread: order book poller
_book404_last: dict[str, float] = {}


def _poll_book(slug: str, tag: str):
    try:
        bk = PM.book(slug)
    except requests.HTTPError as e:
        # The gateway can answer 404 for a market that exists and is trading (early in the round,
        # per scripts/ef_autobuyer.py). Record it, but at most once a minute per slug.
        if e.response is not None and e.response.status_code == 404:
            if time.time() - _book404_last.get(slug, 0) > 60:
                _book404_last[slug] = time.time()
                W.write("pmus.book404", {"slug": slug, "tag": tag})
            return
        W.err(f"book:{slug}", e)
        return
    except Exception as e:  # noqa
        W.err(f"book:{slug}", e)
        return
    st = bk.get("state")
    prev = S.last_book_state.get(slug)
    if st != prev:
        S.last_book_state[slug] = st
        W.write("pmus.state", {"slug": slug, "from": prev, "to": st, "transactTime": bk.get("transactTime")})
        log(f"{slug} state {prev} -> {st}")
    W.write("pmus.book", {"slug": slug, "tag": tag, "book": bk})


def book_loop():
    last_cold = 0.0
    last_next = 0.0
    while not STOP.is_set():
        t0 = time.time()
        live = window_start(t0)
        rem = live + WINDOW - t0
        try:
            if rem <= BOOK_HOT_SECONDS:
                _poll_book(S.slug_for(live), "live")
                # keep polling the just-expired window briefly to catch the EXPIRED transition
            elif t0 - last_cold >= BOOK_COLD_INTERVAL:
                _poll_book(S.slug_for(live), "live")
                last_cold = t0
            if rem <= 15 or t0 - last_next >= 15:
                _poll_book(S.slug_for(live + WINDOW), "next")
                last_next = t0
            if rem > WINDOW - 20:   # first 20 s of a new window: watch the previous one expire/settle
                _poll_book(S.slug_for(live - WINDOW), "prev")
        except Exception as e:  # noqa
            W.err("book_loop", e)
        STOP.wait(max(0.05, 1.0 - (time.time() - t0)))   # loop ticks at 1 Hz; cold polls are gated above


# ----------------------------------------------------------------------------- thread: settlement poller
def settlement_loop():
    pending: dict[str, int] = {}  # slug -> window end
    while not STOP.is_set():
        t0 = time.time()
        try:
            prev = window_start(t0) - WINDOW
            for s in (prev, prev - WINDOW):
                slug = S.slug_for(s)
                if slug not in S.settled and slug not in pending:
                    pending[slug] = s + WINDOW
            for slug, end in list(pending.items()):
                if t0 < end + 2:
                    continue
                if t0 - end > SETTLE_POLL_MAX_SECONDS:
                    W.write("pmus.settlement", {"slug": slug, "timeout": True})
                    pending.pop(slug, None)
                    S.settled.add(slug)
                    continue
                m = PM.market_by_slug(slug) or {}
                apt = m.get("assetPriceTerms") or {}
                sp = parse_amount(apt.get("settlementPrice"))
                st = PM.settlement(slug)
                settle_val = (st or {}).get("settlement")
                if sp is not None or settle_val is not None:
                    W.write("pmus.settlement", {"slug": slug, "end": end, "settlementPrice": sp,
                                                "priceToBeat": parse_amount(apt.get("priceToBeat")),
                                                "settlement": settle_val, "market": m, "raw": st,
                                                "latency_s": round(t0 - end, 1)})
                    log(f"{slug} settled: ptb={parse_amount(apt.get('priceToBeat'))} close={sp} -> {settle_val}")
                    pending.pop(slug, None)
                    S.settled.add(slug)
        except Exception as e:  # noqa
            W.err("settlement", e)
        STOP.wait(SETTLE_POLL_INTERVAL)


# ----------------------------------------------------------------------------- Layer B: Kalshi WS (optional)
def _kalshi_signer():
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa

    if KALSHI_PRIVATE_KEY_PATH:
        with open(KALSHI_PRIVATE_KEY_PATH, "rb") as f:
            pem = f.read()
    elif KALSHI_PRIVATE_KEY_PEM:
        pem = KALSHI_PRIVATE_KEY_PEM.replace("\\n", "\n").encode()
    else:
        pem = base64.b64decode(KALSHI_PRIVATE_KEY_B64 or "")
    key = serialization.load_pem_private_key(pem, password=None)

    def headers(method: str, path: str) -> dict:
        ts = str(now_ms())
        msg = (ts + method.upper() + path).encode()
        if isinstance(key, rsa.RSAPrivateKey):
            sig = key.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                           salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
        elif isinstance(key, ed25519.Ed25519PrivateKey):
            sig = key.sign(msg)
        else:
            raise RuntimeError("unsupported Kalshi key type")
        return {"KALSHI-ACCESS-KEY": KALSHI_KEY_ID,
                "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
                "KALSHI-ACCESS-TIMESTAMP": ts}
    return headers


def kalshi_open_markets(sign) -> list[str]:
    path = "/trade-api/v2/markets"
    r = requests.get(KALSHI_REST + path, params={"series_ticker": KALSHI_SERIES, "status": "open", "limit": 100},
                     headers=sign("GET", path), timeout=8)
    r.raise_for_status()
    ms = r.json().get("markets", [])
    W.write("kalshi.markets", [{k: m.get(k) for k in ("ticker", "open_time", "close_time", "status", "title",
                                                       "yes_ask", "yes_bid", "floor_strike", "strike_type")} for m in ms])
    return [m["ticker"] for m in ms if m.get("ticker")]


async def kalshi_ws_main():
    import websockets
    sign = _kalshi_signer()
    path = "/trade-api/ws/v2"
    while not STOP.is_set():
        try:
            async with websockets.connect(KALSHI_WS_URL, additional_headers=sign("GET", path),
                                          ping_interval=None, max_size=2**22) as ws:
                log("Kalshi WS connected")
                cmd_id = 1
                await ws.send(json.dumps({"id": cmd_id, "cmd": "subscribe",
                                          "params": {"channels": ["cfbenchmarks_value"], "index_ids": ["BRTI"]}}))
                cmd_id += 1
                tickers = kalshi_open_markets(sign)
                sids: dict[str, int] = {}     # channel -> sid (for later add/delete of markets)
                if tickers:
                    await ws.send(json.dumps({"id": cmd_id, "cmd": "subscribe",
                                              "params": {"channels": ["orderbook_delta"],
                                                         "market_tickers": tickers, "use_yes_price": True}}))
                    cmd_id += 1
                    await ws.send(json.dumps({"id": cmd_id, "cmd": "subscribe",
                                              "params": {"channels": ["ticker"], "market_tickers": tickers,
                                                         "send_initial_snapshot": True}}))
                    cmd_id += 1
                subscribed = set(tickers)
                last_refresh = time.time()
                while not STOP.is_set():
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=30)
                    except asyncio.TimeoutError:
                        await ws.send(json.dumps({"id": cmd_id, "cmd": "list_subscriptions"})); cmd_id += 1
                        continue
                    try:
                        msg = json.loads(raw)
                    except Exception:
                        W.write("kalshi.ws", {"raw": raw[:2000]})
                        continue
                    W.write("kalshi.ws", msg)
                    if msg.get("type") == "subscribed":
                        m = msg.get("msg") or {}
                        if m.get("channel") in ("orderbook_delta", "ticker"):
                            sids[m["channel"]] = m.get("sid")
                    if time.time() - last_refresh > 60:
                        last_refresh = time.time()
                        try:
                            cur = set(kalshi_open_markets(sign))
                        except Exception as e:  # noqa
                            W.err("kalshi.markets", e); cur = subscribed
                        add, rem = cur - subscribed, subscribed - cur
                        for sid in sids.values():
                            if add:
                                await ws.send(json.dumps({"id": cmd_id, "cmd": "update_subscription",
                                                          "params": {"sid": sid, "market_tickers": sorted(add), "action": "add_markets"}}))
                                cmd_id += 1
                            if rem:
                                await ws.send(json.dumps({"id": cmd_id, "cmd": "update_subscription",
                                                          "params": {"sid": sid, "market_tickers": sorted(rem), "action": "delete_markets"}}))
                                cmd_id += 1
                        subscribed = cur
        except Exception as e:  # noqa
            W.err("kalshi.ws", e)
            log(f"Kalshi WS error: {e} (reconnect in 5s)")
            await asyncio.sleep(5)


# ----------------------------------------------------------------------------- Layer C: Polymarket US WS (optional)
async def pmus_ws_main():
    from polymarket_us import PolymarketUS  # pip install polymarket-us
    client = PolymarketUS(key_id=PM_KEY_ID, secret_key=PM_SECRET)
    while not STOP.is_set():
        try:
            ws = client.ws.markets()
            last_ws: dict[str, float] = {}

            def throttled(kind: str):
                # full-book frames can arrive many times per second; one per second per market is all we need
                def cb(d):
                    try:
                        slug = (d.get(kind) or {}).get("marketSlug") or ""
                    except AttributeError:
                        slug = ""
                    now = time.time()
                    k = f"{kind}:{slug}"
                    if now - last_ws.get(k, 0) >= 1.0:
                        last_ws[k] = now
                        W.write("pmus.ws", d)
                    else:
                        WS_DROPPED[kind] = WS_DROPPED.get(kind, 0) + 1
                return cb
            ws.on("market_data", throttled("marketData"))
            ws.on("market_data_lite", throttled("marketDataLite"))
            ws.on("trade", lambda d: W.write("pmus.ws", d))
            ws.on("error", lambda e: W.write("err", {"where": "pmus.ws", "msg": str(e)[:500]}))
            await ws.connect()
            log("Polymarket US WS connected")
            subscribed: set[str] = set()
            n = 0
            while not STOP.is_set():
                live = window_start(time.time())
                want = {S.slug_for(live), S.slug_for(live + WINDOW)}
                for slug in want - subscribed:
                    n += 1
                    await ws.subscribe(f"md-{n}", "SUBSCRIPTION_TYPE_MARKET_DATA", [slug])
                    await ws.subscribe(f"tr-{n}", "SUBSCRIPTION_TYPE_TRADE", [slug])
                    subscribed.add(slug)
                await asyncio.sleep(5)
                if len(subscribed) > 6:   # resubscribe fresh every few windows to drop expired slugs
                    try:
                        await ws.close()
                    finally:
                        break
        except Exception as e:  # noqa
            W.err("pmus.ws", e)
            log(f"Polymarket US WS error: {e} (reconnect in 5s)")
            await asyncio.sleep(5)


def run_async(coro):
    asyncio.run(coro)


# ----------------------------------------------------------------------------- status + main
def status_loop():
    last = 0
    while not STOP.is_set():
        STOP.wait(60)
        live = window_start(time.time())
        lb = S.last_brti
        ptb = S.ptb(live)
        d = round(lb[1] - ptb, 2) if (lb and ptb is not None) else None
        try:
            size = W.fh.tell() if W.fh else 0
        except Exception:  # noqa
            size = 0
        log(f"status: lines={W.count} (+{W.count - last}/min) file={size/1e6:.1f}MB ws_throttled={WS_DROPPED} "
            f"brti={lb} ptb={ptb} d={d} live={S.slug_for(live)} state={S.last_book_state.get(S.slug_for(live))}")
        last = W.count


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    W.write("rec.start", {"data_dir": DATA_DIR, "book_hot_s": BOOK_HOT_SECONDS,
                          "kalshi": KALSHI_ON, "pmus_ws": bool(PM_KEY_ID and PM_SECRET), "pid": os.getpid()})
    log(f"Mr. P recorder starting -> {DATA_DIR}  (Layer A on; "
        f"Kalshi {'ON' if KALSHI_ON else 'off'}; "
        f"PM-US WS {'ON' if PM_KEY_ID and PM_SECRET else 'off'})")
    threads = [threading.Thread(target=f, name=f.__name__, daemon=True)
               for f in (discovery_loop, index_loop, book_loop, settlement_loop, status_loop)]
    if KALSHI_ON:
        threads.append(threading.Thread(target=run_async, args=(kalshi_ws_main(),), name="kalshi_ws", daemon=True))
    if PM_KEY_ID and PM_SECRET:
        threads.append(threading.Thread(target=run_async, args=(pmus_ws_main(),), name="pmus_ws", daemon=True))
    for t in threads:
        t.start()

    def _stop(*_):
        log("stopping...")
        STOP.set()
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    while not STOP.is_set():
        time.sleep(0.5)
    time.sleep(1.5)
    W.write("rec.stop", {"lines": W.count})
    log(f"stopped. {W.count} lines written.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
