#!/usr/bin/env python3
"""
Mr. P — Recorder v2  (multi-coin, multi-timeframe, both venues, 1 Hz snapshots)

Captures what is needed to test "zero-risk" entries on short crypto Up/Down windows:

  Polymarket US (public REST, no keys):
    every UP_DOWN market the exchange lists for the next 2 hours, any coin, 5m/15m/1h
    -> pmus.market   market object whenever price-to-beat / settlement / status changes
    -> pmus.book     full book: 1 Hz in the final BOOK_HOT_SECONDS of each window
                     (5 s when the WebSocket layer is on), 15 s cadence before that
    -> pmus.state    every market-state transition (OPEN / HALTED / AUCTION / EXPIRED ...)
    -> pmus.settlement  stamped settlement price + result + latency after window end
    -> pmus.idx      [fallback only] the exchange's public 1-second index candles (smoothed)
  Kalshi (KALSHI_KEY_ID + PEM; read-only):
    -> kalshi.idx    CF Benchmarks index prints for every coin, 1/s — the true settlement
                     series — with Kalshi's running final-minute settlement average
    -> kalshi.book   1 Hz top-10 snapshots of each open KX<COIN>15M book (yes-leg pricing)
    -> kalshi.ticker raw ticker frames (small)
  Polymarket US WebSocket (POLYMARKET_KEY_ID + SECRET):
    -> pmus.ws       full-book pushes for live + next windows, 1 per second per market
  Derived:
    -> settle_avg    in each window's final 70 s: samples collected, running average, and
                     the average the remaining samples would need to flip the leader

Storage: JSONL per UTC hour under DATA_DIR/YYYY-MM-DD/HH[.n].jsonl (rotates at 40 MB).
Each line: {"t": <recv unix ms>, "k": <kind>, "d": <payload>}
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import re
import signal
import sys
import threading
import time
import traceback
from datetime import datetime, timezone
from typing import Any, Optional

import requests


# ----------------------------------------------------------------------------- .env (optional)
def _load_dotenv(path: str = os.environ.get("MRP_ENV_FILE", ".env")) -> None:
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
PMUS_BASE = os.environ.get("PMUS_BASE_URL", "https://gateway.polymarket.us")   # public host
BOOK_HOT_SECONDS = int(os.environ.get("MRP_BOOK_HOT_SECONDS", "180"))
BOOK_COLD_INTERVAL = float(os.environ.get("MRP_BOOK_COLD_INTERVAL", "15"))
MAX_REST_PER_SEC = int(os.environ.get("MRP_MAX_REST_PER_SEC", "6"))
DISCOVERY_INTERVAL = 60.0
SETTLE_POLL_INTERVAL = 5.0
SETTLE_POLL_MAX_SECONDS = 15 * 60
LOOKAHEAD = int(os.environ.get("MRP_LOOKAHEAD_SECONDS", "7200"))
MAX_HORIZON = int(os.environ.get("MRP_MAX_HORIZON_SECONDS", "3600"))
COINS = [c.strip().lower() for c in os.environ.get("MRP_COINS", "btc,eth,sol,xrp,doge,bnb,hype").split(",") if c.strip()]

KALSHI_KEY_ID = os.environ.get("KALSHI_KEY_ID")
KALSHI_PRIVATE_KEY_PATH = os.environ.get("KALSHI_PRIVATE_KEY_PATH")
KALSHI_PRIVATE_KEY_PEM = os.environ.get("KALSHI_PRIVATE_KEY_PEM")       # as in pb/venues/kalshi.py
KALSHI_PRIVATE_KEY_B64 = os.environ.get("KALSHI_PRIVATE_KEY_B64")
KALSHI_ON = bool(KALSHI_KEY_ID and (KALSHI_PRIVATE_KEY_PATH or KALSHI_PRIVATE_KEY_PEM or KALSHI_PRIVATE_KEY_B64))
KALSHI_REST = os.environ.get("KALSHI_REST_URL", "https://external-api.kalshi.com")
KALSHI_WS_URL = os.environ.get("KALSHI_WS_URL", "wss://external-api-ws.kalshi.com/trade-api/ws/v2")

PM_KEY_ID = os.environ.get("POLYMARKET_KEY_ID")
PM_SECRET = os.environ.get("POLYMARKET_SECRET_KEY")
PM_WS_ON = bool(PM_KEY_ID and PM_SECRET)
WS_MAX_SUBS = int(os.environ.get("MRP_WS_MAX_SUBS", "8"))          # gateway caps subscriptions per connection
WS_WINDOW_SECONDS = int(os.environ.get("MRP_WS_WINDOW_SECONDS", "420"))
WS_RECONNECT_SECONDS = int(os.environ.get("MRP_WS_RECONNECT_SECONDS", "1800"))

# CF Benchmarks index id <-> coin symbol
RTI_TO_SYM = {"BRTI": "btc"}
for _c in ("eth", "sol", "xrp", "doge", "bnb", "hype", "near", "zec", "ltc", "link", "ada", "sui", "wld", "xlm", "bch", "dot", "hbar", "aave", "shib", "vvv"):
    RTI_TO_SYM[f"{_c.upper()}USD_RTI"] = _c
SYM_TO_RTI = {v: k for k, v in RTI_TO_SYM.items()}

STOP = threading.Event()
COUNTS: dict[str, int] = {}     # dropped / throttled frames by kind, for the status line


# ----------------------------------------------------------------------------- helpers
def now_ms() -> int:
    return int(time.time() * 1000)


def parse_ts(v: Any) -> Optional[float]:
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


def horizon_seconds(h: Any) -> Optional[int]:
    m = re.fullmatch(r"\s*(\d+)\s*([mh])\s*", str(h or "").lower())
    if not m:
        return {"hourly": 3600, "daily": 86400}.get(str(h).lower())
    n, u = int(m.group(1)), m.group(2)
    return n * 60 if u == "m" else n * 3600


def bump(k: str, n: int = 1):
    COUNTS[k] = COUNTS.get(k, 0) + n


def log(msg: str):
    print(f"[{datetime.now(timezone.utc):%H:%M:%S}Z] {msg}", flush=True)


# ----------------------------------------------------------------------------- writer
class Writer:
    """Thread-safe JSONL writer, one file per UTC hour, rotated at ROTATE_BYTES, line-flushed."""
    ROTATE_BYTES = int(os.environ.get("MRP_ROTATE_BYTES", str(40 * 1024 * 1024)))

    def __init__(self, root: str):
        self.root = root
        self.lock = threading.Lock()
        self.fh = None
        self.fh_key = None
        self.count = 0

    def _file_for(self, t_ms: int):
        d = datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc)
        key = (d.strftime("%Y-%m-%d"), d.strftime("%H"))
        if key != self.fh_key or (self.fh and self.fh.tell() > self.ROTATE_BYTES):
            if self.fh:
                self.fh.close()
            path = os.path.join(self.root, key[0])
            os.makedirs(path, exist_ok=True)
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
            self._file_for(t_ms).write(line + "\n")
            self.count += 1

    def err(self, where: str, exc: BaseException):
        self.write("err", {"where": where, "type": type(exc).__name__, "msg": str(exc)[:500]})

    def size(self) -> int:
        try:
            return self.fh.tell() if self.fh else 0
        except Exception:  # noqa
            return 0


W = Writer(DATA_DIR)


# ----------------------------------------------------------------------------- Polymarket US public REST
class PMUS:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers["User-Agent"] = "mrp-recorder/0.2"
        self.backoff_until = 0.0
        self.lock = threading.Lock()
        self.stamps: list[float] = []     # token bucket for MAX_REST_PER_SEC

    def _throttle(self):
        with self.lock:
            now = time.time()
            self.stamps = [t for t in self.stamps if now - t < 1.0]
            if len(self.stamps) >= MAX_REST_PER_SEC:
                raise RuntimeError("local rate cap")
            self.stamps.append(now)

    def get(self, path: str, params: Any = None, timeout: float = 6.0, counted: bool = True) -> Any:
        if time.time() < self.backoff_until:
            raise RuntimeError("backoff")
        if counted:
            self._throttle()
        r = self.s.get(PMUS_BASE + path, params=params, timeout=timeout)
        if r.status_code == 429:
            self.backoff_until = time.time() + 2.0
            raise RuntimeError("429 rate limited")
        if r.status_code >= 500:
            self.backoff_until = time.time() + 5.0
        r.raise_for_status()
        return r.json()

    def market_by_slug(self, slug: str) -> Optional[dict]:
        try:
            data = self.get(f"/v1/market/slug/{slug}")
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                return None
            raise
        return data.get("market", data)

    def discover_updown(self, max_pages: int = 8) -> dict[str, dict]:
        """All open UP_DOWN crypto markets starting within LOOKAHEAD, any coin, horizon <= MAX_HORIZON."""
        found: dict[str, dict] = {}
        now = time.time()
        for page in range(max_pages):
            if page:
                time.sleep(0.3)
            data = self.get("/v1/markets", params={"categories": "crypto", "closed": "false",
                                                   "limit": 200, "offset": page * 200}, timeout=12.0, counted=False)
            ms = data.get("markets", [])
            for m in ms:
                apt = m.get("assetPriceTerms") or {}
                if apt.get("marketType") != "ASSET_PRICE_MARKET_TYPE_UP_DOWN":
                    continue
                hz = horizon_seconds(apt.get("horizon"))
                ws, we = parse_ts(apt.get("windowStart")), parse_ts(apt.get("windowEnd"))
                if not hz or hz > MAX_HORIZON or ws is None or we is None:
                    continue
                if ws > now + LOOKAHEAD or we < now - 1200:
                    continue
                found[m["slug"]] = m
            if len(ms) < 200:
                break
        return found

    def markets_by_slugs(self, slugs: list[str]) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for i in range(0, len(slugs), 50):
            data = self.get("/v1/markets", params=[("slug", x) for x in slugs[i:i + 50]] + [("limit", 50)],
                            timeout=10.0, counted=False)
            for m in data.get("markets", []):
                out[m.get("slug")] = m
        return out

    def book(self, slug: str) -> dict:
        return self.get(f"/v1/markets/{slug}/book").get("marketData", {})

    def settlement(self, slug: str) -> Optional[dict]:
        try:
            return self.get(f"/v1/markets/{slug}/settlement")
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code in (404, 400):
                return None
            raise

    def index_candles(self, syms: list[str], frm: int, to: int = 0) -> dict[str, list[dict]]:
        params = [("assets", f"crypto:{s}") for s in syms[:10]] + [("from", frm), ("to", to), ("bucket", "ASSET_PRICE_BUCKET_1S")]
        data = self.get("/v1/asset-prices/history", params=params, timeout=8.0)
        out = {}
        for series in data.get("series", []):
            a = series.get("asset") or {}
            out[str(a.get("symbol", "")).lower()] = series.get("candles", [])
        return out


PM = PMUS()


# ----------------------------------------------------------------------------- shared state
class Mkt:
    __slots__ = ("slug", "sym", "hz", "start", "end", "m")

    def __init__(self, m: dict):
        apt = m.get("assetPriceTerms") or {}
        self.slug = m["slug"]
        self.sym = str((apt.get("asset") or {}).get("symbol", "")).lower()
        self.hz = horizon_seconds(apt.get("horizon")) or 0
        self.start = int(parse_ts(apt.get("windowStart")) or 0)
        self.end = int(parse_ts(apt.get("windowEnd")) or 0)
        self.m = m

    @property
    def ptb(self) -> Optional[float]:
        return parse_amount((self.m.get("assetPriceTerms") or {}).get("priceToBeat"))


class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.pm: dict[str, Mkt] = {}                       # slug -> market
        self.idx: dict[str, dict[int, float]] = {}         # sym -> {sec: value}   (Kalshi prints or PM candles)
        self.idx_src: dict[str, str] = {}                  # sym -> "kalshi" | "pmus"
        self.last_idx: dict[str, tuple[int, float]] = {}
        self.last_book_state: dict[str, str] = {}
        self.settled: set[str] = set()
        self.kalshi_mkts: dict[str, dict] = {}             # ticker -> {sym, open, close, strike}

    def live(self, now: float) -> list[Mkt]:
        with self.lock:
            return [m for m in self.pm.values() if m.start <= now < m.end]

    def upcoming(self, now: float, within: float) -> list[Mkt]:
        with self.lock:
            return [m for m in self.pm.values() if now < m.start <= now + within]

    def ended(self, now: float, within: float) -> list[Mkt]:
        with self.lock:
            return [m for m in self.pm.values() if m.end <= now < m.end + within]

    def set_idx(self, sym: str, sec: int, v: float, src: str):
        with self.lock:
            d = self.idx.setdefault(sym, {})
            d[sec] = v
            self.idx_src[sym] = src
            if sym not in self.last_idx or sec >= self.last_idx[sym][0]:
                self.last_idx[sym] = (sec, v)

    def prune(self, keep_seconds: int = 7200):
        cut = int(time.time()) - keep_seconds
        with self.lock:
            for d in self.idx.values():
                for k in [k for k in d if k < cut]:
                    d.pop(k, None)
            for slug in [s for s, m in self.pm.items() if m.end < cut]:
                self.pm.pop(slug, None)


S = State()


# ----------------------------------------------------------------------------- thread: Polymarket discovery
def _fingerprint(m: dict) -> str:
    apt = m.get("assetPriceTerms") or {}
    return json.dumps({"ptb": apt.get("priceToBeat"), "sp": apt.get("settlementPrice"), "active": m.get("active"),
                       "closed": m.get("closed"), "status": m.get("status"), "tick": m.get("orderPriceMinTickSize"),
                       "minq": m.get("minimumTradeQty")}, sort_keys=True, default=str)


def gen_slugs(now: float) -> list[str]:
    """Expected slugs for prev/live/next/next2 windows: cpc-btc-updown-15m-...z, cpceth-eth-updown-5m-...z, ..."""
    out = []
    for sym in PM_COINS:
        prefix = "cpc" if sym == "btc" else f"cpc{sym}"
        for hz, label in ((300, "5m"), (900, "15m"), (3600, "1h")):
            base = int(now // hz) * hz
            for k in (-1, 0, 1, 2):
                d = datetime.fromtimestamp(base + k * hz, tz=timezone.utc)
                out.append(f"{prefix}-{sym}-updown-{label}-{d:%Y-%m-%d-%H%M}z")
    return out


PM_COINS = [c.strip().lower() for c in os.environ.get("MRP_PM_COINS", "btc,eth,sol,xrp").split(",") if c.strip()]


def discovery_loop():
    fps: dict[str, str] = {}
    last_universe = 0.0
    last_broad = 0.0
    while not STOP.is_set():
        t0 = time.time()
        try:
            found: dict[str, dict] = {}
            if t0 - last_broad > 600:          # broad paged discovery every 10 min (learns new coins/patterns)
                last_broad = t0
                try:
                    found.update(PM.discover_updown())
                except Exception as e:  # noqa
                    W.err("discovery.broad", e)
            try:                                # targeted refresh every minute: cheap, precise, cap-exempt
                found.update(PM.markets_by_slugs(gen_slugs(t0)))
            except Exception as e:  # noqa
                W.err("discovery.slugs", e)
            with S.lock:
                for slug, m in found.items():
                    mk = Mkt(m)
                    if mk.start and mk.end and mk.hz:
                        S.pm[slug] = mk
            for slug, m in found.items():
                fp = _fingerprint(m)
                if fps.get(slug) != fp:
                    fps[slug] = fp
                    W.write("pmus.market", m)
            if t0 - last_universe > 600:
                last_universe = t0
                summary: dict[str, int] = {}
                for m in S.pm.values():
                    key = f"{m.sym}:{m.hz // 60}m"
                    summary[key] = summary.get(key, 0) + 1
                W.write("pmus.universe", summary)
                log(f"universe: {summary}")
            S.prune()
        except Exception as e:  # noqa
            W.err("discovery", e)
            log(f"discovery error: {e}")
        STOP.wait(max(1.0, DISCOVERY_INTERVAL - (time.time() - t0)))


# ----------------------------------------------------------------------------- thread: Polymarket books (REST)
_book404_last: dict[str, float] = {}
_book_last: dict[str, float] = {}


def _poll_book(slug: str, tag: str):
    try:
        bk = PM.book(slug)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            if time.time() - _book404_last.get(slug, 0) > 60:      # gateway quirk: 404 on a live market
                _book404_last[slug] = time.time()
                W.write("pmus.book404", {"slug": slug, "tag": tag})
            return
        W.err(f"book:{slug}", e)
        return
    except RuntimeError:
        bump("rest_capped")
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
    _book_last[slug] = time.time()


def book_loop():
    hot_interval = 5.0 if PM_WS_ON else 1.0
    while not STOP.is_set():
        t0 = time.time()
        try:
            due: list[tuple[float, str, str]] = []     # (priority, slug, tag)
            for m in S.live(t0):
                rem = m.end - t0
                last = _book_last.get(m.slug, 0)
                if rem <= BOOK_HOT_SECONDS:
                    if t0 - last >= hot_interval - 0.05:
                        due.append((rem, m.slug, "live"))
                elif t0 - last >= BOOK_COLD_INTERVAL:
                    due.append((1e6 + rem, m.slug, "live"))
            for m in S.upcoming(t0, 150):
                if t0 - _book_last.get(m.slug, 0) >= 30:
                    due.append((2e6, m.slug, "next"))
            for m in S.ended(t0, 20):
                if t0 - _book_last.get(m.slug, 0) >= 1.0:
                    due.append((0, m.slug, "prev"))
            due.sort()
            for _, slug, tag in due[:MAX_REST_PER_SEC - 1]:
                _poll_book(slug, tag)
        except Exception as e:  # noqa
            W.err("book_loop", e)
        STOP.wait(max(0.05, 1.0 - (time.time() - t0)))


# ----------------------------------------------------------------------------- thread: index (fallback) + settle_avg
def index_loop():
    """Kalshi feeds the index when on. Otherwise poll the exchange's public candles (smoothed).
    Either way, log the running settlement average for every live window in its final 70 s."""
    while not STOP.is_set():
        t0 = time.time()
        try:
            syms = sorted({m.sym for m in S.live(t0)} | {m.sym for m in S.upcoming(t0, 600)})
            if syms and (not KALSHI_ON or any(S.idx_src.get(s) != "kalshi" for s in syms)):
                need = [s for s in syms if S.idx_src.get(s) != "kalshi"]
                try:
                    for sym, candles in PM.index_candles(need, int(t0) - 20, 0).items():
                        for c in candles:
                            n = int(c.get("tickCount", 0) or 0)
                            if n <= 0:
                                continue
                            ts, close = int(c.get("timestamp", 0)), float(c["close"])
                            if S.idx.get(sym, {}).get(ts) != close:
                                S.set_idx(sym, ts, close, "pmus")
                                W.write("pmus.idx", {"sym": sym, "ts": ts, "c": close, "n": n})
                except RuntimeError:
                    pass
            for m in S.live(t0):
                rem = m.end - t0
                if rem > 70:
                    continue
                ptb = m.ptb
                with S.lock:
                    d = S.idx.get(m.sym, {})
                    pts = [d[ts] for ts in range(m.end - 60, m.end) if ts in d]
                    last = S.last_idx.get(m.sym)
                k, tot = len(pts), sum(pts)
                rec = {"slug": m.slug, "sym": m.sym, "end": m.end, "rem": round(rem, 2), "n_done": k,
                       "sum_done": round(tot, 4), "avg_done": round(tot / k, 4) if k else None, "ptb": ptb,
                       "last": last, "src": S.idx_src.get(m.sym)}
                if ptb is not None and k < 60:
                    rec["need_rem_avg"] = round((60 * ptb - tot) / (60 - k), 4)
                    if last:
                        rec["need_rem_move"] = round(rec["need_rem_avg"] - last[1], 4)
                W.write("settle_avg", rec)
        except Exception as e:  # noqa
            W.err("index", e)
        STOP.wait(max(0.05, 1.0 - (time.time() - t0)))


# ----------------------------------------------------------------------------- thread: settlements
def settlement_loop():
    pending: dict[str, float] = {}
    while not STOP.is_set():
        t0 = time.time()
        try:
            for m in S.ended(t0, SETTLE_POLL_MAX_SECONDS):
                if m.slug not in S.settled:
                    pending.setdefault(m.slug, m.end)
            for slug, end in list(pending.items()):
                if t0 < end + 2:
                    continue
                if t0 - end > SETTLE_POLL_MAX_SECONDS:
                    W.write("pmus.settlement", {"slug": slug, "end": end, "timeout": True})
                    pending.pop(slug, None); S.settled.add(slug)
                    continue
                try:
                    m = PM.market_by_slug(slug) or {}
                    st = PM.settlement(slug)
                except RuntimeError:
                    continue
                apt = m.get("assetPriceTerms") or {}
                sp = parse_amount(apt.get("settlementPrice"))
                val = (st or {}).get("settlement")
                if sp is not None or val is not None:
                    W.write("pmus.settlement", {"slug": slug, "end": end, "settlementPrice": sp,
                                                "priceToBeat": parse_amount(apt.get("priceToBeat")),
                                                "settlement": val, "latency_s": round(t0 - end, 1), "market": m, "raw": st})
                    log(f"{slug} settled: ptb={parse_amount(apt.get('priceToBeat'))} close={sp} -> {val}")
                    pending.pop(slug, None); S.settled.add(slug)
        except Exception as e:  # noqa
            W.err("settlement", e)
        STOP.wait(SETTLE_POLL_INTERVAL)


# ----------------------------------------------------------------------------- Kalshi (optional, read-only)
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
            sig = key.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
        elif isinstance(key, ed25519.Ed25519PrivateKey):
            sig = key.sign(msg)
        else:
            raise RuntimeError("unsupported Kalshi key type")
        return {"KALSHI-ACCESS-KEY": KALSHI_KEY_ID, "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
                "KALSHI-ACCESS-TIMESTAMP": ts}
    return headers


def kalshi_open_markets(sign) -> dict[str, dict]:
    """Open KX<COIN>15M markets for every coin in COINS -> {ticker: {sym, open, close, strike}}."""
    out: dict[str, dict] = {}
    path = "/trade-api/v2/markets"
    for sym in COINS:
        series = f"KX{sym.upper()}15M"
        try:
            r = requests.get(KALSHI_REST + path, params={"series_ticker": series, "status": "open", "limit": 100},
                             headers=sign("GET", path), timeout=8)
            if r.status_code == 404:
                continue
            r.raise_for_status()
            for m in r.json().get("markets", []):
                if m.get("ticker"):
                    out[m["ticker"]] = {"sym": sym, "open": m.get("open_time"), "close": m.get("close_time"),
                                        "strike": m.get("floor_strike"), "status": m.get("status")}
        except Exception as e:  # noqa
            W.err(f"kalshi.markets:{series}", e)
    return out


class KBook:
    """Kalshi book in yes-leg pricing: 'yes' levels are bids for Yes, 'no' levels (use_yes_price) are asks for Yes."""

    def __init__(self):
        self.yes: dict[float, float] = {}
        self.no: dict[float, float] = {}
        self.dirty = True

    def snapshot(self, msg: dict):
        self.yes = {float(p): float(q) for p, q in msg.get("yes_dollars_fp", []) or []}
        self.no = {float(p): float(q) for p, q in msg.get("no_dollars_fp", []) or []}
        self.dirty = True

    def delta(self, msg: dict):
        side = self.yes if msg.get("side") == "yes" else self.no
        p = float(msg["price_dollars"]); q = side.get(p, 0.0) + float(msg["delta_fp"])
        if q <= 1e-9:
            side.pop(p, None)
        else:
            side[p] = q
        self.dirty = True

    def top(self, n: int = 10) -> dict:
        yb = sorted(self.yes.items(), reverse=True)[:n]
        ya = sorted(self.no.items())[:n]
        return {"yb": [[p, round(q, 2)] for p, q in yb], "ya": [[p, round(q, 2)] for p, q in ya]}


async def kalshi_ws_main():
    import websockets
    sign = _kalshi_signer()
    path = "/trade-api/ws/v2"
    books: dict[str, KBook] = {}
    while not STOP.is_set():
        try:
            async with websockets.connect(KALSHI_WS_URL, additional_headers=sign("GET", path), ping_interval=None, max_size=2**23) as ws:
                log("Kalshi WS connected")
                cmd = 1
                await ws.send(json.dumps({"id": cmd, "cmd": "subscribe", "params": {"channels": ["cfbenchmarks_value"], "index_ids": ["all"]}})); cmd += 1
                mkts = kalshi_open_markets(sign)
                S.kalshi_mkts = mkts
                W.write("kalshi.markets", mkts)
                tickers = sorted(mkts)
                sids: dict[str, int] = {}
                if tickers:
                    await ws.send(json.dumps({"id": cmd, "cmd": "subscribe", "params": {"channels": ["orderbook_delta"], "market_tickers": tickers, "use_yes_price": True}})); cmd += 1
                    await ws.send(json.dumps({"id": cmd, "cmd": "subscribe", "params": {"channels": ["ticker"], "market_tickers": tickers, "send_initial_snapshot": True}})); cmd += 1
                subscribed = set(tickers)
                last_refresh = last_snap = time.time()
                while not STOP.is_set():
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=20)
                    except asyncio.TimeoutError:
                        raw = None
                    if raw is not None:
                        try:
                            msg = json.loads(raw)
                        except Exception:
                            W.write("kalshi.ws", {"raw": raw[:1000]}); msg = {}
                        typ = msg.get("type"); m = msg.get("msg") or {}
                        if typ == "cfbenchmarks_value":
                            try:
                                d = json.loads(m.get("data") or "{}")
                                idx_id = m.get("index_id") or d.get("id")
                                sym = RTI_TO_SYM.get(idx_id, str(idx_id).lower())
                                sec = int(int(d.get("time", 0)) // 1000)
                                v = float(d.get("value"))
                                S.set_idx(sym, sec, v, "kalshi")
                                fin = m.get("last_60s_windowed_average_15min")
                                W.write("kalshi.idx", {"id": idx_id, "sym": sym, "t": sec, "v": v,
                                                       "avg60": (m.get("avg_60s_data") or {}).get("value"),
                                                       "fin": ({"v": fin.get("value"), "n": fin.get("window_size")} if fin else None)})
                            except Exception as e:  # noqa
                                W.err("kalshi.idx", e)
                        elif typ == "orderbook_snapshot":
                            books.setdefault(m.get("market_ticker", "?"), KBook()).snapshot(m)
                        elif typ == "orderbook_delta":
                            books.setdefault(m.get("market_ticker", "?"), KBook()).delta(m)
                            bump("kalshi_deltas")
                        elif typ == "ticker":
                            W.write("kalshi.ticker", m)
                        elif typ == "subscribed":
                            if m.get("channel") in ("orderbook_delta", "ticker"):
                                sids[m["channel"]] = m.get("sid")
                            W.write("kalshi.ws", msg)
                        elif typ in ("error", "ok", "unsubscribed"):
                            W.write("kalshi.ws", msg)
                    now = time.time()
                    # 1 Hz book snapshots in a market's final 3 minutes, else every 10 s; only when changed
                    if now - last_snap >= 1.0:
                        last_snap = now
                        for tk, bk in books.items():
                            info = S.kalshi_mkts.get(tk) or {}
                            close = parse_ts(info.get("close")) or 0
                            rem = close - now
                            hot = 0 <= rem <= BOOK_HOT_SECONDS
                            if not bk.dirty or (not hot and int(now) % 10):
                                continue
                            bk.dirty = False
                            W.write("kalshi.book", {"ticker": tk, "sym": info.get("sym"), "close": int(close), **bk.top(10)})
                    if now - last_refresh > 60:
                        last_refresh = now
                        cur = kalshi_open_markets(sign)
                        if cur:
                            S.kalshi_mkts = cur
                        add, rem_ = set(cur) - subscribed, subscribed - set(cur)
                        if add or rem_:
                            W.write("kalshi.markets", cur)
                        for sid in sids.values():
                            if add:
                                await ws.send(json.dumps({"id": cmd, "cmd": "update_subscription", "params": {"sid": sid, "market_tickers": sorted(add), "action": "add_markets"}})); cmd += 1
                            if rem_:
                                await ws.send(json.dumps({"id": cmd, "cmd": "update_subscription", "params": {"sid": sid, "market_tickers": sorted(rem_), "action": "delete_markets"}})); cmd += 1
                        for tk in rem_:
                            books.pop(tk, None)
                        subscribed = (subscribed | add) - rem_
        except Exception as e:  # noqa
            W.err("kalshi.ws", e)
            log(f"Kalshi WS error: {e} (reconnect in 5s)")
            await asyncio.sleep(5)


# ----------------------------------------------------------------------------- Polymarket US WebSocket (optional)
async def pmus_ws_main():
    from polymarket_us import PolymarketUS
    client = PolymarketUS(key_id=PM_KEY_ID, secret_key=PM_SECRET)
    while not STOP.is_set():
        try:
            ws = client.ws.markets()
            last_ws: dict[str, float] = {}

            def throttled(kind: str):
                def cb(d):
                    try:
                        slug = (d.get(kind) or {}).get("marketSlug") or ""
                    except AttributeError:
                        slug = ""
                    now = time.time(); k = f"{kind}:{slug}"
                    if now - last_ws.get(k, 0) >= 1.0:
                        last_ws[k] = now
                        W.write("pmus.ws", d)
                    else:
                        bump(f"ws_throttled_{kind}")
                return cb
            ws.on("market_data", throttled("marketData"))
            ws.on("market_data_lite", throttled("marketDataLite"))
            ws.on("trade", lambda d: W.write("pmus.ws", d))
            ws.on("error", lambda e: W.write("err", {"where": "pmus.ws", "msg": str(e)[:500]}))
            await ws.connect()
            log("Polymarket US WS connected")
            subs: dict[str, str] = {}     # slug -> request id
            n = 0
            connected_at = time.time()
            while not STOP.is_set():
                now = time.time()
                # nearest expiries first; the gateway caps subscriptions per connection
                cand = sorted([m for m in S.live(now) if m.end - now <= WS_WINDOW_SECONDS] + S.upcoming(now, 60),
                              key=lambda m: m.end)
                want = {m.slug for m in cand[:WS_MAX_SUBS]}
                for slug in sorted(set(subs) - want):
                    rid = subs.pop(slug)
                    try:
                        await ws.unsubscribe("md-" + rid)
                    except Exception as e:  # noqa
                        W.err("pmus.ws.unsub", e)
                for slug in sorted(want - set(subs)):
                    n += 1
                    await ws.subscribe(f"md-{n}", "SUBSCRIPTION_TYPE_MARKET_DATA", [slug])
                    subs[slug] = f"{n}"
                if now - connected_at > WS_RECONNECT_SECONDS and not any(m.end - now < 240 for m in cand):
                    log("Polymarket US WS: periodic reconnect")
                    try:
                        await ws.close()
                    finally:
                        break
                await asyncio.sleep(5)
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
        now = time.time()
        live = S.live(now)
        parts = []
        for m in sorted(live, key=lambda x: x.end)[:6]:
            li = S.last_idx.get(m.sym)
            d = round(li[1] - m.ptb, 2) if (li and m.ptb is not None) else None
            parts.append(f"{m.sym}{m.hz // 60}m:{int(m.end - now)}s d={d} {str(S.last_book_state.get(m.slug, ''))[13:]}")
        log(f"status: lines={W.count} (+{W.count - last}/min) file={W.size()/1e6:.1f}MB counts={COUNTS} "
            f"idx={ {s: S.idx_src.get(s) for s in sorted(S.idx_src)} } kalshi_mkts={len(S.kalshi_mkts)} live={' | '.join(parts)}")
        last = W.count


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    W.write("rec.start", {"v": 2, "data_dir": DATA_DIR, "book_hot_s": BOOK_HOT_SECONDS, "coins": COINS,
                          "kalshi": KALSHI_ON, "pmus_ws": PM_WS_ON, "pid": os.getpid()})
    log(f"Mr. P recorder v2 -> {DATA_DIR}  (Polymarket REST on; Kalshi {'ON' if KALSHI_ON else 'off'}; PM-US WS {'ON' if PM_WS_ON else 'off'}; coins {COINS})")
    threads = [threading.Thread(target=f, name=f.__name__, daemon=True)
               for f in (discovery_loop, index_loop, book_loop, settlement_loop, status_loop)]
    if KALSHI_ON:
        threads.append(threading.Thread(target=run_async, args=(kalshi_ws_main(),), name="kalshi_ws", daemon=True))
    if PM_WS_ON:
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
