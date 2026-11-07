#!/usr/bin/env python3
"""Mr. H LIVE — the Coinbase hopper with a real key. REAL MONEY, hard-capped. MAKER ON EVERY ORDER.

Runs the paper bot's *aggressive* profile (scripts/mrh_paper.py — same universe, same signal, same spread gate)
with real orders on Coinbase Advanced Trade, every one of them a post-only limit order (maker fee 0.5% instead of
the 0.9% taker fee: a 1.0% round trip instead of 1.8%):

  enter   ONE 5-min impulse candle (>= +2% close/open, volume >= 3x the 2-h median), spread <= 0.6%, strongest
          candidate first. A post-only limit BUY rests at the best bid for the whole USD bankroll (capped at
          MRH_LIVE_MAX_USD). If the bid runs away it is re-priced up to the bid, never above the signal close times
          (1 + MRH_LIVE_ENTRY_CHASE); if it has not filled after MRH_LIVE_ENTRY_TTL_MIN minutes it is cancelled —
          the spike is either giving back (we fill on the pullback) or gone (we pass).
  exit    4% trailing stop from the high-water mark, watched every MRH_LIVE_FAST_S seconds while in a position.
          When the bid touches it, a post-only limit SELL is posted at the best ask and chased DOWN to the new ask
          whenever the market moves away from it (never crossing the book). Two safety exceptions, both optional:
          a stop-limit sell PARKED ON THE EXCHANGE far below the trail (MRH_LIVE_DISASTER_GAP under it; 0 parks
          nothing) for the minutes the runner is not there, and a market "panic" sell if the bid falls
          MRH_LIVE_PANIC_GAP under the trail while a maker exit is still resting (0 = never take).
  swap    a coin that has made no new high for MRH_LIVE_SWAP_AFTER_H hours (or one that was adopted rather than
          signalled) is sold — maker — to take a fresh signal in another coin with the whole stack: proceeds plus
          any USD that arrived meanwhile. The paper twin runs this as its aggressive_swap book.

Guards: switch file mrh/LIVE_ON on main and no mrh/PAUSED (checked every cycle); one position (or one resting
buy); at most MRH_LIVE_MAX_HOPS_DAY sells per UTC day; MRH_LIVE_MAX_USD per entry; halts below MRH_LIVE_FLOOR_USD
total (Coinbase's $1 minimum would strand anything smaller); never touches any asset other than USD and the one
coin it holds.

The exchange is the truth: every cycle reconciles balances, open orders and fills. A position bought by hand is
adopted and trailed; a sell that filled while the bot slept is booked from its fill; deposits and withdrawals are
detected and kept out of the P&L.

    python scripts/mrh_live.py run --out data/mrh-live --minutes 335 [--dry]   # --dry: everything but sending orders
    python scripts/mrh_live.py report --out data/mrh-live                      # -> data/mrh-live/LIVE.md
    python scripts/mrh_live.py selftest                                      # no network, no key

Env: COINBASE_API_KEY  = CDP key name, organizations/{org}/apiKeys/{id}   (permission: View + Trade. NOT Transfer.)
     COINBASE_API_SECRET = the key's private key: EC PEM (ES256) or base64 Ed25519 (EdDSA); "\\n" escapes are fine.
Files in --out: live_state.json, live_trades.jsonl, live_events.jsonl, LIVE.md, errors.jsonl (pb.errlog).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import secrets as _secrets
import sys
import time
import uuid
from datetime import datetime, timezone
from decimal import ROUND_FLOOR, Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mrh_paper as paper  # noqa: E402  (shared universe / signal / candle logic)

BOT = "mrh-live"
HOST = "api.coinbase.com"
PRIV = "/api/v3/brokerage"
PROFILE = paper.PROFILES["aggressive"]
TRAIL = PROFILE["trail"]
CID_PREFIX = "mrh-live-"
MAKER_FEE = 0.005                  # Coinbase Advanced Intro-tier maker fee (the 0.9% in paper is the taker fee)
FEE_BUFFER = 0.012                 # USD headroom left out of a limit buy: Coinbase holds size*price*(1+fee) and rejects if short
STOP_LIMIT_GAP = 0.015             # the disaster stop-limit's limit sits 1.5% under its stop so it fills on a thin book
STOP_REPLACE_MIN = 0.001           # re-park the disaster stop when the high-water mark moved >= 0.1%
PRICE_EPS = 0.0005                 # ignore touch moves smaller than this (5 bps) when deciding to re-price a resting order
TRAIL_CONFIRM = 2                  # fast ticks in a row at/under the trail before the exit is posted (one blip on a thin book is not a dump) …
TRAIL_HARD = 0.01                  # … unless the bid is already this far under the trail: then one tick is enough
DUST_USD = 1.00                    # holdings worth less than this are not "a position"
STABLES = {"USD", "USDC", "USDT", "DAI", "PYUSD", "GUSD", "USDP", "TUSD", "EURC", "USDS", "RLUSD", "PAX", "EUR", "GBP"}

MAX_USD = float(os.environ.get("MRH_LIVE_MAX_USD", "200"))         # per entry: the whole stack goes in, up to this
FLOOR_USD = float(os.environ.get("MRH_LIVE_FLOOR_USD", "1.20"))    # halt below this total
MAX_HOPS_DAY = int(os.environ.get("MRH_LIVE_MAX_HOPS_DAY", "6"))
SWAP_AFTER_H = float(os.environ.get("MRH_LIVE_SWAP_AFTER_H", "2"))  # a coin with no new high for this long gives way to a
                                                                     # fresh signal (0 = never swap); adopted coins always do
FAST_S = float(os.environ.get("MRH_LIVE_FAST_S", "20"))             # seconds between ticks while in a position or an order rests
ENTRY_TTL_MIN = float(os.environ.get("MRH_LIVE_ENTRY_TTL_MIN", "15"))   # a resting buy unfilled after this is cancelled
ENTRY_CHASE = float(os.environ.get("MRH_LIVE_ENTRY_CHASE", "0.02"))     # re-price the resting buy up to the bid, never above signal close*(1+this)
DISASTER_GAP = float(os.environ.get("MRH_LIVE_DISASTER_GAP", "0.06"))   # parked stop-limit sits this far UNDER the trail (0 = park nothing)
PANIC_GAP = float(os.environ.get("MRH_LIVE_PANIC_GAP", "0.03"))         # bid this far under the trail with a maker exit still resting -> market sell (0 = never)
SIG_TTL_MIN = 15.0                 # a swap's target signal is still worth buying this long after the sell fills
REPO = os.environ.get("GITHUB_REPOSITORY", "watkast/predictionbots")

now, iso, parse_iso, CANDLE_S, LOOKBACK = paper.now, paper.iso, paper.parse_iso, paper.CANDLE_S, paper.LOOKBACK


# ----------------------------------------------------------------------------------------------- numbers

def floor_to(x: float, inc: str | float) -> str:
    """Round x DOWN to a multiple of inc, as the plain-decimal string Coinbase wants."""
    q = Decimal(str(inc))
    d = (Decimal(repr(float(x))) / q).to_integral_value(rounding=ROUND_FLOOR) * q
    s = format(d, "f")
    return s if "." not in s else (s.rstrip("0").rstrip(".") or "0")


def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


# ----------------------------------------------------------------------------------------------- CDP auth + client

def load_key(secret: str):
    """CDP API secrets come as an EC PEM (ES256) or, for newer keys, a base64 Ed25519 private key (EdDSA)."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec, ed25519
    s = secret.strip().replace("\\n", "\n")
    if "BEGIN" in s:
        key = serialization.load_pem_private_key(s.encode(), password=None)
        if isinstance(key, ec.EllipticCurvePrivateKey):
            return key, "ES256"
        if isinstance(key, ed25519.Ed25519PrivateKey):
            return key, "EdDSA"
        raise ValueError("unsupported PEM key type")
    raw = base64.b64decode(s)
    if len(raw) not in (32, 64):
        raise ValueError(f"Ed25519 secret must decode to 32 or 64 bytes, got {len(raw)}")
    return ed25519.Ed25519PrivateKey.from_private_bytes(raw[:32]), "EdDSA"


def build_jwt(key_name: str, key, alg: str, method: str, path: str, t: int | None = None) -> str:
    """Per-request JWT for the Advanced Trade API: uri = 'METHOD host/path' (no query), 120 s life."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
    t = int(time.time()) if t is None else t
    header = {"alg": alg, "kid": key_name, "nonce": _secrets.token_hex(16), "typ": "JWT"}
    payload = {"sub": key_name, "iss": "cdp", "nbf": t, "exp": t + 120, "uri": f"{method} {HOST}{path}"}
    msg = b64u(json.dumps(header, separators=(",", ":")).encode()) + "." + b64u(json.dumps(payload, separators=(",", ":")).encode())
    if alg == "ES256":
        r, s = decode_dss_signature(key.sign(msg.encode(), ec.ECDSA(hashes.SHA256())))
        sig = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    else:
        sig = key.sign(msg.encode())
    return msg + "." + b64u(sig)


class CDP:
    """Authenticated Advanced Trade REST client (accounts, orders, fills). Public market data stays on paper.Coinbase."""

    def __init__(self, key_name: str, secret: str, pace_s: float = 0.15):
        import httpx
        self.key_name = key_name
        self.key, self.alg = load_key(secret)
        self.cli = httpx.Client(timeout=20, headers={"User-Agent": "predictionbots-mrh-live/1"})
        self.pace_s, self._last, self.calls = pace_s, 0.0, 0

    def _req(self, method: str, path: str, params: dict | None = None, body: dict | None = None) -> dict:
        wait = self._last + self.pace_s - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        for attempt in range(4):
            self._last = time.monotonic()
            self.calls += 1
            tok = build_jwt(self.key_name, self.key, self.alg, method, path)
            r = self.cli.request(method, f"https://{HOST}{path}", params=params, json=body,
                                 headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(1.5 * (attempt + 1))
                continue
            if r.status_code >= 400:
                raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:400]}")
            return r.json() if r.content else {}
        raise RuntimeError(f"{method} {path} -> {r.status_code} after retries: {r.text[:400]}")

    def accounts(self) -> list[dict]:
        out, cursor = [], None
        while True:
            j = self._req("GET", f"{PRIV}/accounts", params={"limit": 250, **({"cursor": cursor} if cursor else {})})
            for a in j.get("accounts", []):
                try:
                    out.append({"currency": a["currency"], "available": float(a["available_balance"]["value"]),
                                "hold": float(a.get("hold", {}).get("value") or 0)})
                except (KeyError, ValueError):
                    continue
            cursor = j.get("cursor") if j.get("has_next") else None
            if not cursor:
                return out

    def create_order(self, body: dict) -> dict:
        return self._req("POST", f"{PRIV}/orders", body=body)

    def cancel(self, order_ids: list[str]) -> list[dict]:
        return self._req("POST", f"{PRIV}/orders/batch_cancel", body={"order_ids": order_ids}).get("results", [])

    def order(self, order_id: str) -> dict:
        try:
            return self._req("GET", f"{PRIV}/orders/historical/{order_id}").get("order", {})
        except RuntimeError as e:
            if " -> 404" in str(e):      # a just-placed order can take a beat to be readable
                return {}
            raise

    def open_orders(self, pid: str) -> list[dict]:
        j = self._req("GET", f"{PRIV}/orders/historical/batch", params={"order_status": "OPEN", "product_type": "SPOT", "limit": 100})
        return [o for o in j.get("orders", []) if o.get("product_id") == pid]

    def fills(self, pid: str, limit: int = 50) -> list[dict]:
        j = self._req("GET", f"{PRIV}/orders/historical/fills", params={"product_ids": pid, "limit": limit})
        return [f for f in j.get("fills", []) if f.get("product_id") == pid]


# ----------------------------------------------------------------------------------------------- state & io

def load_state(out: Path) -> dict:
    f = out / "live_state.json"
    st = json.loads(f.read_text()) if f.exists() else {}
    st.setdefault("started", iso(now()))
    st.setdefault("pos", None)
    st.setdefault("start_usd", None)      # first observed total value: the live book's "$4"
    st.setdefault("hops", 0)
    st.setdefault("wins", 0)
    st.setdefault("fees", 0.0)
    st.setdefault("peak", 0.0)
    st.setdefault("hops_by_day", {})
    st.setdefault("cycles", 0)
    st.setdefault("halted", None)
    st.setdefault("universe", [])
    st.setdefault("universe_t", None)
    st.setdefault("products", {})
    st.setdefault("last", {})
    st.setdefault("entry", None)          # the resting maker buy, if any
    st.setdefault("pending_sig", None)    # the coin a swap is heading for, once its sell fills
    st.setdefault("flows", 0.0)           # deposits (+) and withdrawals (-) seen since start: not P&L
    st.setdefault("last_trade_t", None)
    return st


def save_state(out: Path, st: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "live_state.json.tmp"
    tmp.write_text(json.dumps(st, indent=1))
    tmp.replace(out / "live_state.json")


def event(out: Path, kind: str, **kw) -> None:
    rec = {"t": iso(now()), "ev": kind, **kw}
    paper.append(out, "live_events.jsonl", rec)
    print(f"{rec['t']} {kind} {json.dumps(kw, default=str)[:300]}", flush=True)


# ----------------------------------------------------------------------------------------------- switches

def switch_on(out: Path, repo: str = REPO) -> tuple[bool, str]:
    """mrh/LIVE_ON exists on main and mrh/PAUSED does not. Contents API with the run's token (no CDN cache), raw as fallback."""
    import httpx
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

    def exists(path: str) -> bool | None:
        try:
            if tok:
                r = httpx.get(f"https://api.github.com/repos/{repo}/contents/{path}", params={"ref": "main"},
                              headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"}, timeout=10)
                if r.status_code in (200, 404):
                    return r.status_code == 200
            r = httpx.get(f"https://raw.githubusercontent.com/{repo}/main/{path}", timeout=10)
            if r.status_code in (200, 404):
                return r.status_code == 200
        except Exception as e:  # network blip: don't flip the switch on a guess
            event(out, "switch_check_error", path=path, err=str(e)[:200])
        return None

    on, paused = exists("mrh/LIVE_ON"), exists("mrh/PAUSED")
    if on is None or paused is None:
        return False, "unknown"
    if paused:
        return False, "PAUSED"
    return on, "on" if on else "LIVE_ON missing"


# ----------------------------------------------------------------------------------------------- market data

def product_map(products: list[dict]) -> dict[str, dict]:
    m = {}
    for p in products:
        pid = p.get("product_id", "")
        if not pid.endswith("-USD") or p.get("status") != "online" or p.get("trading_disabled") or p.get("view_only"):
            continue
        m[pid] = {"base_inc": p.get("base_increment") or "0.00000001", "quote_inc": p.get("quote_increment") or "0.01",
                  "quote_min": float(p.get("quote_min_size") or 1), "base_min": float(p.get("base_min_size") or 0),
                  "price": float(p.get("price") or 0)}
    return m


def refresh_universe(cb, st: dict, t: datetime) -> None:
    if st["universe"] and st["universe_t"] and (t - parse_iso(st["universe_t"])).total_seconds() < 3600:
        return
    prods = cb.products()
    st["universe"] = paper.build_universe(prods)
    st["products"] = product_map(prods)
    st["universe_t"] = iso(t)


def best_signal(cb, out: Path, st: dict, t: datetime) -> dict | None:
    """Strongest aggressive signal on the last closed 5-min candle that passes the spread gate. Same logic as paper."""
    end = int(t.timestamp()) // CANDLE_S * CANDLE_S
    start = end - CANDLE_S * (LOOKBACK + 3)
    cands = []
    for u in st["universe"]:
        try:
            cs = paper.closed_candles(cb.candles(u["id"], start, end), t)
        except Exception as e:
            paper.append(out, "live_scan_errors.jsonl", {"t": iso(t), "pid": u["id"], "err": str(e)[:300]})
            continue
        sig = paper.evaluate(cs, PROFILE)
        if sig:
            cands.append((sig["impulse"], u["id"], sig))
    for _imp, pid, sig in sorted(cands, reverse=True):
        tk = cb.ticker(pid)
        spread = (tk["ask"] - tk["bid"]) / tk["ask"] if tk["ask"] > 0 else 9
        rec = {"t": iso(t), "pid": pid, **sig, "bid": tk["bid"], "ask": tk["ask"], "spread": round(spread, 4)}
        if spread > paper.MAX_SPREAD:
            event(out, "signal_skipped", reason="spread", **rec)
            continue
        return rec
    return None



# ----------------------------------------------------------------------------------------------- exchange ops

def holdings(ex: CDP, cb, st: dict) -> tuple[float, list[dict]]:
    """(available USD, [{pid, qty, available, hold, bid, value}] for every tradable coin worth >= DUST_USD).
    qty counts coins under a resting sell (hold); available USD excludes what a resting buy holds."""
    usd, held = 0.0, []
    for a in ex.accounts():
        cur, qty = a["currency"].upper(), a["available"] + a["hold"]
        if cur == "USD":
            usd = a["available"]
            continue
        if cur in STABLES or qty <= 0:
            continue
        pid = f"{cur}-USD"
        p = st["products"].get(pid)
        if not p or qty * p["price"] < DUST_USD * 0.5:     # dust and dead listings (LOOM...) are ignored
            continue
        bid = cb.ticker(pid)["bid"]
        val = qty * bid
        if val >= DUST_USD:
            held.append({"pid": pid, "qty": qty, "available": a["available"], "hold": a["hold"], "bid": bid, "value": val})
    held.sort(key=lambda h: -h["value"])
    return usd, held


def wait_done(ex: CDP, order_id: str, timeout_s: float = 12.0) -> dict:
    t_end = time.time() + timeout_s
    while True:
        o = ex.order(order_id)
        if o.get("status") in ("FILLED", "CANCELLED", "EXPIRED", "FAILED") or time.time() > t_end:
            return o
        time.sleep(1.0)


def fill_facts(o: dict) -> dict:
    return {"order_id": o.get("order_id"), "status": o.get("status"), "qty": float(o.get("filled_size") or 0),
            "px": float(o.get("average_filled_price") or 0), "fee": float(o.get("total_fees") or 0),
            "value": float(o.get("filled_value") or 0)}


def place(ex: CDP, out: Path, dry: bool, pid: str, side: str, cfg: dict, label: str) -> dict | None:
    """Send one order. {"order_id"} when accepted, {"error"} when the exchange rejected it, None in dry mode."""
    body = {"client_order_id": CID_PREFIX + uuid.uuid4().hex[:20], "product_id": pid, "side": side, "order_configuration": cfg}
    if dry:
        event(out, "dry_order", label=label, body=body)
        return None
    try:
        j = ex.create_order(body)
    except RuntimeError as e:            # HTTP 4xx rejection: log it, let the cycle go on (auth errors still raise)
        if " -> 401" in str(e) or " -> 403" in str(e):
            raise
        event(out, "order_rejected", label=label, pid=pid, side=side, cfg=cfg, err=str(e)[:300])
        return {"error": str(e)[:300]}
    if not j.get("success"):
        err = j.get("error_response") or j
        event(out, "order_rejected", label=label, pid=pid, side=side, cfg=cfg, err=err)
        return {"error": json.dumps(err, default=str)[:300]}
    oid = (j.get("success_response") or {}).get("order_id")
    event(out, "order_sent", label=label, pid=pid, side=side, cfg=cfg, order_id=oid)
    return {"order_id": oid}


def accepted(r: dict | None) -> bool:
    return bool(r and r.get("order_id"))


def cancel_and_confirm(ex: CDP, out: Path, order_id: str) -> dict:
    """Cancel a resting order; return its final order record (status CANCELLED / FILLED / ...). A FILLED one did its job."""
    try:
        ex.cancel([order_id])
    except Exception as e:
        event(out, "cancel_error", order_id=order_id, err=str(e)[:200])
    return wait_done(ex, order_id, timeout_s=8)


def add_fill(acc: dict, f: dict) -> None:
    """Accumulate one finished order's fills into {qty, value, fee} (each order id exactly once, at its end)."""
    if f["qty"] <= 0:
        return
    acc.setdefault("filled", {"qty": 0.0, "value": 0.0, "fee": 0.0})
    acc["filled"]["qty"] += f["qty"]
    acc["filled"]["value"] += f["value"] if f["value"] else f["qty"] * f["px"]
    acc["filled"]["fee"] += f["fee"]


def filled_qty(acc: dict) -> float:
    return (acc.get("filled") or {}).get("qty", 0.0)


def touch_price(cb, pid: str, side: str, p: dict, cap: float | None = None) -> tuple[float, dict]:
    """The maker price at the touch: a buy joins the best bid, a sell joins the best ask (or one tick over the bid)."""
    tk = cb.ticker(pid)
    tick = float(p["quote_inc"])
    if side == "BUY":
        px = tk["bid"]
        if cap is not None:
            px = min(px, cap)
    else:
        px = max(tk["ask"], tk["bid"] + tick) if tk["ask"] > 0 else tk["bid"] + tick
    return float(floor_to(px, p["quote_inc"])) if px > 0 else 0.0, tk


def post(ex: CDP, cb, out: Path, st: dict, dry: bool, pid: str, side: str, label: str, qty: float | None = None,
         budget: float | None = None, cap: float | None = None) -> dict | None:
    """A post-only limit order at the touch. Buys size themselves from `budget` USD (fee headroom kept), sells take `qty`.
    A post-only order the exchange would have to cross is rejected; we re-read the touch and try again, three times.
    Returns {"order_id", "px", "qty"} or None (rejected / dry)."""
    p = st["products"].get(pid) or {"base_inc": "0.00000001", "quote_inc": "0.01", "quote_min": 1.0, "base_min": 0.0}
    for attempt in range(3):
        px, tk = touch_price(cb, pid, side, p, cap)
        if px <= 0:
            event(out, "post_skipped", label=label, pid=pid, reason="no price", ticker=tk)
            return None
        if side == "BUY":
            q = float(floor_to(budget / (px * (1 + FEE_BUFFER)), p["base_inc"]))
            if q * px < max(p["quote_min"], 1.0) or q < p["base_min"] or q <= 0:
                event(out, "entry_skipped", reason="below_min", budget=budget, px=px, pid=pid)
                return None
        else:
            q = float(floor_to(qty, p["base_inc"]))
            if q <= 0:
                return None
        cfg = {"limit_limit_gtc": {"base_size": floor_to(q, p["base_inc"]), "limit_price": floor_to(px, p["quote_inc"]), "post_only": True}}
        r = place(ex, out, dry, pid, side, cfg, label)
        if dry:
            return None
        if accepted(r):
            o = ex.order(r["order_id"])                       # a post-only order that crossed comes back already cancelled
            if o.get("status") in ("CANCELLED", "FAILED", "EXPIRED") and float(o.get("filled_size") or 0) <= 0:
                event(out, "post_crossed", label=label, pid=pid, px=px, status=o.get("status"))
                time.sleep(1.0)
                continue
            return {"order_id": r["order_id"], "px": px, "qty": q}
        if side == "BUY" and "INSUFFICIENT" in (r or {}).get("error", "").upper():
            budget *= 0.99                                  # fee rounding: 1% less, once more
        time.sleep(1.0)
    return None


def book_sell(out: Path, st: dict, f: dict, reason: str) -> dict:
    """Close the position with the aggregated sell fills f = {qty, px, fee, value, order_id}."""
    pos = st["pos"]
    proceeds = f["value"] - f["fee"] if f["value"] else f["qty"] * f["px"] - f["fee"]
    net = proceeds - pos["cost"]
    st["fees"] += f["fee"]
    st["hops"] += 1
    st["wins"] += net > 0
    day = iso(now())[:10]
    st["hops_by_day"][day] = st["hops_by_day"].get(day, 0) + 1
    held_min = (now() - parse_iso(pos["t_in"])).total_seconds() / 60
    rec = {"t": iso(now()), "ev": "sell", "pid": pos["pid"], "px": f["px"], "qty": f["qty"], "proceeds": round(proceeds, 4), "fee": f["fee"],
           "net": round(net, 4), "net_pct": round(net / pos["cost"], 4) if pos["cost"] else 0.0, "entry_px": pos["entry_px"], "hw": pos["hw"],
           "held_min": round(held_min, 1), "reason": reason, "order_id": f.get("order_id"), "maker": f.get("maker")}
    paper.append(out, "live_trades.jsonl", rec)
    event(out, "sold", pid=pos["pid"], px=f["px"], net=rec["net"], net_pct=rec["net_pct"], reason=reason, fee=round(f["fee"], 4))
    st["last_trade_t"] = rec["t"]
    st["pos"] = None
    return rec


def open_position(out: Path, st: dict, e: dict) -> None:
    """Turn a (fully or partly) filled entry into the position."""
    fl = e["filled"]
    px = fl["value"] / fl["qty"]
    cost = fl["value"] + fl["fee"]
    st["fees"] += fl["fee"]
    sig = e["sig"]
    st["pos"] = {"pid": e["pid"], "qty": fl["qty"], "entry_px": px, "cost": cost, "hw": px, "t_in": iso(now()), "hw_t": iso(now()),
                 "signal": {k: sig[k] for k in ("impulse", "vol_mult", "above_2h_high") if k in sig}, "stop": None, "exit": None,
                 "order_id": e.get("order_id"), "last_bid": px, "trail_hits": 0}
    rec = {"t": iso(now()), "ev": "buy", "pid": e["pid"], "px": px, "qty": fl["qty"], "cost": round(cost, 4), "fee": fl["fee"],
           "signal": st["pos"]["signal"], "order_id": e.get("order_id"), "maker": True, "limit_px": e.get("px"), "signal_close": sig.get("close")}
    paper.append(out, "live_trades.jsonl", rec)
    event(out, "bought", pid=e["pid"], px=round(px, 8), qty=fl["qty"], cost=round(cost, 4), fee=round(fl["fee"], 4))
    st["last_trade_t"] = rec["t"]
    st["entry"] = None


# ----------------------------------------------------------------------------------------------- entry (maker buy)

def start_entry(ex: CDP, cb, out: Path, st: dict, dry: bool, sig: dict, usd: float) -> bool:
    budget = min(usd, MAX_USD)
    if budget < 1.0:
        event(out, "entry_skipped", reason="below_min", usd=usd, pid=sig["pid"])
        return False
    cap = sig["close"] * (1 + ENTRY_CHASE) if sig.get("close") else None
    r = post(ex, cb, out, st, dry, sig["pid"], "BUY", "buy", budget=budget, cap=cap)
    if dry:
        st["entry"] = {"order_id": None, "pid": sig["pid"], "px": 0.0, "qty": 0.0, "t": iso(now()), "sig": sig, "cap_px": cap, "budget": budget}
        return True
    if not r:
        return False
    st["entry"] = {"order_id": r["order_id"], "pid": sig["pid"], "px": r["px"], "qty": r["qty"], "t": iso(now()), "sig": sig,
                   "cap_px": cap, "budget": budget, "filled": {"qty": 0.0, "value": 0.0, "fee": 0.0}, "reposts": 0}
    event(out, "entry_posted", pid=sig["pid"], px=r["px"], qty=r["qty"], cap=cap, ttl_min=ENTRY_TTL_MIN)
    return True


def finish_entry(ex: CDP, out: Path, st: dict, why: str) -> None:
    """The resting buy is over (filled / expired / cancelled): open the position if anything filled, else drop it."""
    e = st["entry"]
    if filled_qty(e) > 0 and e["filled"]["value"] >= DUST_USD:
        open_position(out, st, e)
    else:
        if filled_qty(e) > 0:
            event(out, "entry_dust", pid=e["pid"], qty=filled_qty(e), note="a crumb filled; below the dust line, ignored")
        event(out, "entry_ended", pid=e["pid"], why=why, px=e["px"])
        st["entry"] = None


def tend_entry(ex: CDP, cb, out: Path, st: dict, dry: bool) -> bool:
    """Look after the resting buy: book a fill, cancel it when stale, re-price it up to the bid within the cap."""
    e = st["entry"]
    age = (now() - parse_iso(e["t"])).total_seconds()
    if dry:
        if age >= ENTRY_TTL_MIN * 60:
            st["entry"] = None
            return True
        return False
    o = ex.order(e["order_id"])
    f = fill_facts(o)
    status = o.get("status") or "UNKNOWN"
    if status == "FILLED":
        add_fill(e, f)
        finish_entry(ex, out, st, "filled")
        return True
    if status in ("CANCELLED", "EXPIRED", "FAILED"):
        add_fill(e, f)
        finish_entry(ex, out, st, status.lower())
        return True
    if age >= ENTRY_TTL_MIN * 60:
        add_fill(e, fill_facts(cancel_and_confirm(ex, out, e["order_id"])))
        finish_entry(ex, out, st, "expired")
        return True
    tk = cb.ticker(e["pid"])
    cap = e.get("cap_px") or float("inf")
    if tk["bid"] > e["px"] * (1 + PRICE_EPS) and e["px"] < cap * (1 - 1e-9):
        p = st["products"].get(e["pid"]) or {"quote_inc": "0.01"}
        new_px = float(floor_to(min(tk["bid"], cap), p["quote_inc"]))      # on the price grid, like the order will be
        if new_px > e["px"] * (1 + PRICE_EPS):
            o2 = cancel_and_confirm(ex, out, e["order_id"])
            add_fill(e, fill_facts(o2))
            if o2.get("status") == "FILLED":
                finish_entry(ex, out, st, "filled")
                return True
            usd, _ = holdings(ex, cb, st)                   # what is really left to spend after any partial fill
            budget = min(usd, MAX_USD)
            if budget < 1.0:
                finish_entry(ex, out, st, "spent")
                return True
            r = post(ex, cb, out, st, dry, e["pid"], "BUY", "buy", budget=budget, cap=cap)
            if not r:
                finish_entry(ex, out, st, "repost_failed")
                return True
            e.update(order_id=r["order_id"], px=r["px"], qty=r["qty"], reposts=e.get("reposts", 0) + 1)
            event(out, "entry_repriced", pid=e["pid"], px=r["px"], qty=r["qty"], bid=tk["bid"], cap=cap)
            return True
    return False


# ----------------------------------------------------------------------------------------------- exit (maker sell)

def clear_resting_sell(ex: CDP, out: Path, st: dict) -> dict | None:
    """Cancel whatever sell is resting (disaster stop or maker exit) so the coins are free. Returns its final record."""
    pos = st["pos"]
    for key in ("exit", "stop"):
        cur = pos.get(key)
        if cur and cur.get("order_id"):
            o = cancel_and_confirm(ex, out, cur["order_id"])
            f = fill_facts(o)
            if key == "exit":
                add_fill(pos["exit"], f)
                pos["exit"]["order_id"] = None
            elif f["qty"] > 0:
                pos["stop"]["filled"] = True
                pos["stop"]["facts"] = f
            else:
                pos["stop"] = None
            return o
    return None


def start_exit(ex: CDP, cb, out: Path, st: dict, dry: bool, reason: str, sig: dict | None = None) -> bool:
    """Post the maker sell for the whole position at the ask (first cancelling the parked disaster stop)."""
    pos = st["pos"]
    if pos.get("stop") and pos["stop"].get("order_id"):
        o = cancel_and_confirm(ex, out, pos["stop"]["order_id"])
        f = fill_facts(o)
        if f["qty"] > 0:                                   # the exchange already sold it: reconcile books it
            pos["stop"]["filled"] = True
            pos["stop"]["facts"] = f
            return True
        pos["stop"] = None
    pos["exit"] = {"order_id": None, "px": 0.0, "qty": pos["qty"], "reason": reason, "t": iso(now()), "sig": sig,
                   "filled": {"qty": 0.0, "value": 0.0, "fee": 0.0}, "reposts": 0}
    return repost_exit(ex, cb, out, st, dry)


def repost_exit(ex: CDP, cb, out: Path, st: dict, dry: bool) -> bool:
    pos, x = st["pos"], st["pos"]["exit"]
    remaining = pos["qty"] - filled_qty(x)
    r = post(ex, cb, out, st, dry, pos["pid"], "SELL", f"sell:{x['reason']}", qty=remaining)
    if dry:
        return True
    if not r:
        event(out, "exit_post_failed", pid=pos["pid"], reason=x["reason"], note="will retry next tick")
        return False
    x.update(order_id=r["order_id"], px=r["px"], qty=r["qty"], t_posted=iso(now()))
    event(out, "exit_posted", pid=pos["pid"], px=r["px"], qty=r["qty"], reason=x["reason"], reposts=x.get("reposts", 0))
    return True


def book_exit(out: Path, st: dict, taker_facts: dict | None = None) -> None:
    pos, x = st["pos"], st["pos"]["exit"]
    fl = dict(x["filled"])
    maker = fl["qty"] > 0
    if taker_facts and taker_facts["qty"] > 0:
        fl["qty"] += taker_facts["qty"]
        fl["value"] += taker_facts["value"] if taker_facts["value"] else taker_facts["qty"] * taker_facts["px"]
        fl["fee"] += taker_facts["fee"]
        maker = maker and False
    if fl["qty"] <= 0:
        return
    f = {"qty": fl["qty"], "value": fl["value"], "fee": fl["fee"], "px": fl["value"] / fl["qty"], "order_id": x.get("order_id"),
         "maker": maker if not taker_facts else ("mixed" if x["filled"]["qty"] > 0 else False)}
    reason = x["reason"] if not taker_facts else f"{x['reason']}+panic"
    sig = x.get("sig")
    book_sell(out, st, f, reason)
    if sig:
        st["pending_sig"] = {**sig, "t_sell": iso(now())}


def market_sell(ex: CDP, cb, out: Path, st: dict, dry: bool, qty: float, reason: str) -> dict | None:
    """The one taker order left: the panic sell. Returns fill facts."""
    pos = st["pos"]
    p = st["products"].get(pos["pid"]) or {"base_inc": "0.00000001"}
    r = None
    for attempt in range(3):      # just-cancelled orders can hold the coins for a moment
        r = place(ex, out, dry, pos["pid"], "SELL", {"market_market_ioc": {"base_size": floor_to(qty, p["base_inc"])}}, f"sell:{reason}")
        if accepted(r) or dry:
            break
        time.sleep(2.0)
    if dry or not accepted(r):
        return None
    return fill_facts(wait_done(ex, r["order_id"]))


def tend_exit(ex: CDP, cb, out: Path, st: dict, dry: bool) -> bool:
    """Look after the resting maker sell: book it when filled, chase the ask down, panic-sell if run over."""
    pos, x = st["pos"], st["pos"]["exit"]
    if dry:
        return False
    if not x.get("order_id"):                                  # last post failed: try again
        return repost_exit(ex, cb, out, st, dry)
    o = ex.order(x["order_id"])
    f = fill_facts(o)
    status = o.get("status") or "UNKNOWN"
    if status == "FILLED":
        add_fill(x, f)
        x["order_id"] = o.get("order_id")
        book_exit(out, st)
        return True
    if status in ("CANCELLED", "EXPIRED", "FAILED"):
        add_fill(x, f)
        remaining = pos["qty"] - filled_qty(x)
        if remaining * (f["px"] or x["px"] or pos["last_bid"]) < DUST_USD:
            book_exit(out, st)
        else:
            x["reposts"] = x.get("reposts", 0) + 1
            repost_exit(ex, cb, out, st, dry)
        return True
    tk = cb.ticker(pos["pid"])
    pos["last_bid"] = tk["bid"]
    panic_px = pos["hw"] * (1 - TRAIL - PANIC_GAP)
    posted_age = (now() - parse_iso(x.get("t_posted") or x["t"])).total_seconds()
    if PANIC_GAP > 0 and tk["bid"] > 0 and tk["bid"] <= panic_px and posted_age >= FAST_S:
        add_fill(x, fill_facts(cancel_and_confirm(ex, out, x["order_id"])))
        remaining = pos["qty"] - filled_qty(x)
        event(out, "panic", pid=pos["pid"], bid=tk["bid"], trail=round(pos["hw"] * (1 - TRAIL), 8), panic_px=round(panic_px, 8), remaining=remaining)
        tf = market_sell(ex, cb, out, st, dry, remaining, "panic") if remaining * tk["bid"] >= DUST_USD * 0.5 else None
        book_exit(out, st, tf)
        return True
    if tk["ask"] > 0 and tk["ask"] < x["px"] * (1 - PRICE_EPS):   # the market left us behind: chase down to the new ask
        add_fill(x, fill_facts(cancel_and_confirm(ex, out, x["order_id"])))
        remaining = pos["qty"] - filled_qty(x)
        if remaining * tk["bid"] < DUST_USD:
            book_exit(out, st)
            return True
        x["reposts"] = x.get("reposts", 0) + 1
        repost_exit(ex, cb, out, st, dry)
        return True
    return False


# ----------------------------------------------------------------------------------------------- disaster stop

def park_stop(ex: CDP, cb, out: Path, st: dict, dry: bool) -> None:
    """Keep a stop-limit sell resting on the exchange DISASTER_GAP under the trail — insurance for the minutes nobody
    is watching (between runs). The trail itself is worked as a maker sell by the fast loop. DISASTER_GAP 0 = none."""
    pos = st["pos"]
    if DISASTER_GAP <= 0 or pos.get("exit"):
        return
    p = st["products"].get(pos["pid"]) or {"base_inc": "0.00000001", "quote_inc": "0.01"}
    stop_px = pos["hw"] * (1 - TRAIL - DISASTER_GAP)
    cur = pos.get("stop")
    if cur and cur.get("order_id"):
        o = ex.order(cur["order_id"]) or {}
        status = o.get("status") or "UNKNOWN"
        if status == "FILLED":
            pos["stop"]["filled"] = True       # booked by reconcile next cycle
            pos["stop"]["facts"] = fill_facts(o)
            return
        if status in ("CANCELLED", "EXPIRED", "FAILED"):
            event(out, "stop_missing", order_id=cur["order_id"], status=status, note="re-parking")
            pos["stop"] = None
        elif abs(stop_px / cur["stop_px"] - 1) < STOP_REPLACE_MIN:
            return                             # resting at the right level: nothing to do
        else:
            o = cancel_and_confirm(ex, out, cur["order_id"])
            if o.get("status") == "FILLED":
                pos["stop"]["filled"] = True
                pos["stop"]["facts"] = fill_facts(o)
                return
            pos["stop"] = None
    qty = pos["qty"]
    for attempt in range(2):
        cfg = {"stop_limit_stop_limit_gtc": {"base_size": floor_to(qty, p["base_inc"]), "limit_price": floor_to(stop_px * (1 - STOP_LIMIT_GAP), p["quote_inc"]),
                                             "stop_price": floor_to(stop_px, p["quote_inc"]), "stop_direction": "STOP_DIRECTION_STOP_DOWN"}}
        r = place(ex, out, dry, pos["pid"], "SELL", cfg, "park_stop")
        if accepted(r) or dry:
            pos["stop"] = {"order_id": r["order_id"] if r else None, "stop_px": stop_px, "t": iso(now())}
            return
        time.sleep(2.0)   # funds from a just-cancelled order may take a moment to release


# ----------------------------------------------------------------------------------------------- reconcile

def reconcile(ex: CDP, cb, out: Path, st: dict) -> tuple[float, list[dict]]:
    """Make the state agree with the exchange. Returns (usd available, held coins)."""
    usd, held = holdings(ex, cb, st)
    pos = st["pos"]
    on_ex = {h["pid"]: h for h in held}
    pending_pid = st["entry"]["pid"] if st.get("entry") else None
    if pos and pos["pid"] not in on_ex:
        # we think we hold it, the exchange says no: a resting sell (ours) or a human sold it while we slept
        x = pos.get("exit")
        if x and x.get("order_id"):
            try:
                add_fill(x, fill_facts(ex.order(x["order_id"])))
            except Exception as e:
                event(out, "reconcile_error", err=str(e)[:200])
        if x and filled_qty(x) > 0:
            book_exit(out, st)
        else:
            f = (pos.get("stop") or {}).get("facts")
            if not f and pos.get("stop") and pos["stop"].get("order_id"):
                try:
                    f = fill_facts(ex.order(pos["stop"]["order_id"]))
                except Exception as e:
                    event(out, "reconcile_error", err=str(e)[:200])
            if f and f["qty"] > 0:
                book_sell(out, st, {**f, "maker": False}, "disaster_stop")
            else:
                event(out, "position_gone", pid=pos["pid"], note="sold outside the bot; booked at last known bid")
                book_sell(out, st, {"order_id": None, "status": "EXTERNAL", "qty": pos["qty"], "px": pos.get("last_bid", pos["entry_px"]),
                                    "fee": 0.0, "value": 0.0, "maker": None}, "external")
        pos = None
    if pos and pos["pid"] in on_ex:
        h = on_ex[pos["pid"]]
        expected = pos["qty"] - (filled_qty(pos["exit"]) if pos.get("exit") else 0.0)
        if expected > 0 and abs(h["qty"] - expected) / max(expected, 1e-12) > 0.01 and not pos.get("exit"):
            event(out, "qty_adjusted", pid=pos["pid"], was=pos["qty"], now=h["qty"])
            pos["qty"] = h["qty"]
        pos["last_bid"] = h["bid"]
    if not pos and held and held[0]["pid"] != pending_pid:
        h = held[0]
        if len(held) > 1:
            event(out, "multiple_holdings", held=[(x["pid"], round(x["value"], 2)) for x in held], note="adopting the largest; others untouched")
        entry, cost = h["bid"], h["qty"] * h["bid"]
        try:
            buys = [f for f in ex.fills(h["pid"]) if f.get("side") == "BUY"]
            if buys:
                entry = float(buys[0].get("price") or entry)
                cost = h["qty"] * entry
        except Exception as e:
            event(out, "fills_error", err=str(e)[:200])
        stop, exit_ = None, None
        try:   # adopt a sell we posted in an earlier run whose state was lost
            for o in ex.open_orders(h["pid"]):
                if o.get("side") != "SELL" or not str(o.get("client_order_id", "")).startswith(CID_PREFIX):
                    continue
                oc = o.get("order_configuration") or {}
                if "stop_limit_stop_limit_gtc" in oc:
                    stop = {"order_id": o["order_id"], "stop_px": float(oc["stop_limit_stop_limit_gtc"].get("stop_price") or 0), "t": iso(now())}
                elif "limit_limit_gtc" in oc:
                    exit_ = {"order_id": o["order_id"], "px": float(oc["limit_limit_gtc"].get("limit_price") or 0), "qty": h["qty"],
                             "reason": "trail", "t": iso(now()), "t_posted": iso(now()), "sig": None,
                             "filled": {"qty": 0.0, "value": 0.0, "fee": 0.0}, "reposts": 0}
        except Exception as e:
            event(out, "open_orders_error", err=str(e)[:200])
        st["pos"] = {"pid": h["pid"], "qty": h["qty"], "entry_px": entry, "cost": cost, "hw": max(entry, h["bid"]), "t_in": iso(now()), "hw_t": iso(now()),
                     "signal": {"adopted": True}, "stop": stop, "exit": exit_, "last_bid": h["bid"], "trail_hits": 0}
        event(out, "adopted", pid=h["pid"], qty=h["qty"], entry_px=entry, value=round(h["value"], 2), stop=bool(stop), exit=bool(exit_))
    # deposits / withdrawals: idle USD moved with no trade of ours and no buy holding funds -> a flow, kept out of the P&L
    prev = (st.get("last") or {}).get("usd")
    if prev is not None and not st.get("entry") and st.get("last", {}).get("t"):
        traded = st.get("last_trade_t") and st["last_trade_t"] >= st["last"]["t"]
        if not traded and abs(usd - prev) > 0.25:
            st["flows"] = round(st.get("flows", 0.0) + (usd - prev), 4)
            event(out, "cash_flow", amount=round(usd - prev, 4), usd=round(usd, 4), total_flows=st["flows"])
    total = usd + (st["pos"]["qty"] * st["pos"]["last_bid"] if st["pos"] else 0.0)
    if st.get("entry") and st["entry"].get("budget"):
        total += st["entry"]["budget"] - st["entry"]["filled"]["value"] - st["entry"]["filled"]["fee"] if st["entry"].get("filled") else st["entry"]["budget"]
    if st["start_usd"] is None:
        st["start_usd"] = round(total, 4)
    st["peak"] = max(st["peak"], total)
    st["last"] = {"t": iso(now()), "usd": round(usd, 4), "total": round(total, 4), "pos": st["pos"]["pid"] if st["pos"] else None,
                  "entry": st["entry"]["pid"] if st.get("entry") else None}
    return usd, held


# ----------------------------------------------------------------------------------------------- one cycle

def swap_due(pos: dict) -> bool:
    """Adopted coins (never a signal) are always swappable; signalled ones once they stop making highs."""
    if not SWAP_AFTER_H:
        return False
    if pos.get("signal", {}).get("adopted"):
        return True
    return (now() - parse_iso(pos.get("hw_t") or pos["t_in"])).total_seconds() >= SWAP_AFTER_H * 3600


def trail_hit(pos: dict, bid: float) -> bool:
    """The bid is at/under the trail. One tick is enough when it is clearly under; a touch needs TRAIL_CONFIRM ticks in a row."""
    stop_px = pos["hw"] * (1 - TRAIL)
    if bid <= 0 or bid > stop_px:
        pos["trail_hits"] = 0
        return False
    pos["trail_hits"] = pos.get("trail_hits", 0) + 1
    return bid <= stop_px * (1 - TRAIL_HARD) or pos["trail_hits"] >= TRAIL_CONFIRM


def pending_signal(cb, out: Path, st: dict) -> dict | None:
    """The coin a swap was heading for, if the sell filled recently enough and the spread still passes."""
    sig = st.get("pending_sig")
    if not sig:
        return None
    st["pending_sig"] = None
    if (now() - parse_iso(sig["t_sell"])).total_seconds() > SIG_TTL_MIN * 60:
        event(out, "pending_signal_stale", pid=sig["pid"])
        return None
    tk = cb.ticker(sig["pid"])
    spread = (tk["ask"] - tk["bid"]) / tk["ask"] if tk["ask"] > 0 else 9
    if spread > paper.MAX_SPREAD:
        event(out, "signal_skipped", reason="spread", pid=sig["pid"], bid=tk["bid"], ask=tk["ask"], spread=round(spread, 4))
        return None
    return {k: v for k, v in sig.items() if k != "t_sell"} | {"bid": tk["bid"], "ask": tk["ask"]}


def take_signal(ex: CDP, cb, out: Path, st: dict, dry: bool, usd: float, sig: dict) -> None:
    event(out, "signal", **{k: v for k, v in sig.items() if k != "t_sell"})
    start_entry(ex, cb, out, st, dry, sig, usd)


def cycle(ex: CDP, cb, out: Path, st: dict, dry: bool, t: datetime | None = None) -> dict:
    t = t or now()
    refresh_universe(cb, st, t)
    if st.get("entry"):
        tend_entry(ex, cb, out, st, dry)
    usd, held = reconcile(ex, cb, out, st)
    pos = st["pos"]
    total = st["last"]["total"]
    hops_today = st["hops_by_day"].get(iso(now())[:10], 0)         # same clock as book_sell
    if st.get("entry"):
        pass                                                       # a buy is resting: nothing else this cycle
    elif pos:
        if pos.get("exit"):
            tend_exit(ex, cb, out, st, dry)
        else:
            bid = pos["last_bid"] if pos.get("last_bid") else cb.ticker(pos["pid"])["bid"]
            if bid > pos["hw"]:
                pos["hw"], pos["hw_t"] = bid, iso(now())
            if trail_hit(pos, bid):
                start_exit(ex, cb, out, st, dry, "trail")
            elif pos.get("stop") and pos["stop"].get("filled"):
                pass                                               # reconcile books it next cycle
            else:
                park_stop(ex, cb, out, st, dry)
            # swap: a dead or adopted coin gives way to a fresh signal; the buy follows once the sell has filled
            if st["pos"] and not st["pos"].get("exit") and swap_due(st["pos"]) and not st["halted"] and hops_today < MAX_HOPS_DAY:
                sig = best_signal(cb, out, st, t)
                if sig and sig["pid"] != st["pos"]["pid"]:
                    event(out, "signal", swap_from=st["pos"]["pid"], **sig)
                    start_exit(ex, cb, out, st, dry, "swap", sig=sig)
    elif st["halted"]:
        pass
    elif total < FLOOR_USD:
        st["halted"] = f"floor: ${total:.2f} < ${FLOOR_USD:.2f}"
        event(out, "halted", reason=st["halted"])
    elif hops_today >= MAX_HOPS_DAY:
        st.setdefault("last", {})["note"] = "daily hop cap"
    else:
        sig = pending_signal(cb, out, st) or best_signal(cb, out, st, t)
        if sig:
            take_signal(ex, cb, out, st, dry, usd, sig)
    st["cycles"] += 1
    save_state(out, st)
    return st["last"]


def need_fast(st: dict) -> bool:
    return bool(st.get("entry") or st.get("pos") or st.get("pending_sig"))


def quick(ex: CDP, cb, out: Path, st: dict, dry: bool) -> bool:
    """Fast tick between cycles: tend the resting order, follow the bid, post the exit the moment the trail is hit.
    Returns True when the state changed (the caller saves and republishes)."""
    if st.get("entry"):
        return tend_entry(ex, cb, out, st, dry)
    pos = st["pos"]
    if not pos:
        if st.get("pending_sig") and not st["halted"]:
            sig = pending_signal(cb, out, st)
            if sig:
                usd, _ = holdings(ex, cb, st)
                take_signal(ex, cb, out, st, dry, usd, sig)
            return True
        return False
    if pos.get("exit"):
        changed = tend_exit(ex, cb, out, st, dry)
        if st["pos"] is None and st.get("pending_sig"):
            sig = pending_signal(cb, out, st)
            if sig:
                usd, _ = holdings(ex, cb, st)
                take_signal(ex, cb, out, st, dry, usd, sig)
        return changed
    tk = cb.ticker(pos["pid"])
    bid = tk["bid"]
    if bid <= 0:
        return False
    pos["last_bid"] = bid
    if bid > pos["hw"]:
        pos["hw"], pos["hw_t"] = bid, iso(now())
    if trail_hit(pos, bid):
        start_exit(ex, cb, out, st, dry, "trail")
        return True
    return False


# ----------------------------------------------------------------------------------------------- report

def report(out: Path) -> str:
    st = load_state(out)
    trades = paper.read_jsonl(out / "live_trades.jsonl")
    events = paper.read_jsonl(out / "live_events.jsonl")
    last, pos, entry = st.get("last") or {}, st.get("pos"), st.get("entry")
    start = st.get("start_usd") or 0.0
    total = last.get("total", 0.0)
    flows = st.get("flows", 0.0)
    L = ["# Mr. H — Coinbase hopper, LIVE (real money, maker on every order)\n",
         f"Updated {iso(now())} · cycles {st['cycles']} · universe {len(st['universe'])} coins · profile aggressive "
         f"(+{PROFILE['impulse']*100:.0f}% impulse, {PROFILE['vol_mult']:.0f}× volume, {TRAIL*100:.0f}% trail) · post-only limit orders at the touch "
         f"(maker {MAKER_FEE*100:.1f}%) · entry TTL {ENTRY_TTL_MIN:g} min, chase cap +{ENTRY_CHASE*100:g}% · disaster stop {DISASTER_GAP*100:g}% under the trail · "
         f"panic sell {PANIC_GAP*100:g}% under it · caps ${MAX_USD:.2f}/entry, {MAX_HOPS_DAY} hops/day, floor ${FLOOR_USD:.2f}, swap after {SWAP_AFTER_H:g} h\n"]
    if st.get("halted"):
        L.append(f"**HALTED: {st['halted']}** — remove mrh/LIVE_ON, fix, delete `halted` in live_state.json on the data branch, restore.\n")
    L.append("## Book\n")
    L.append("| now | start | deposits | P&L | peak | USD free | hops | win % | fees paid | position / order |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    wr = (st["wins"] / st["hops"] * 100) if st["hops"] else 0.0
    pnl = total - start - flows
    pos_s = "—"
    if pos:
        x, stop = pos.get("exit") or {}, pos.get("stop") or {}
        state = (f"SELLING @ {x.get('px', 0):.6g} ({x.get('reason')}, {filled_qty(x):.4g} filled)" if x else
                 f"stop {pos['hw']*(1-TRAIL):.6g}" + (f" · disaster {stop['stop_px']:.6g} parked" if stop.get("order_id") else ""))
        pos_s = f"{pos['pid'][:-4]} {pos['qty']:.6g} @ {pos['entry_px']:.6g} · hw {pos['hw']:.6g} · {state}"
    elif entry:
        pos_s = f"BUYING {entry['pid'][:-4]} @ {entry['px']:.6g} (cap {entry.get('cap_px') or 0:.6g}, {filled_qty(entry):.4g} filled)"
    L.append(f"| ${total:.2f} | ${start:.2f} | ${flows:+.2f} | ${pnl:+.2f} ({(pnl/(start+max(flows,0))*100) if start else 0:+.1f}%) | ${st['peak']:.2f} | "
             f"${last.get('usd', 0):.2f} | {st['hops']} | {wr:.0f}% | ${st['fees']:.3f} | {pos_s} |")
    L.append("")
    L.append("## Hops\n")
    L.append("| time (UTC) | coin | in | out | held | net | fee | reason |")
    L.append("|---|---|---|---|---|---|---|---|")
    buys = {b["pid"]: b for b in trades if b["ev"] == "buy"}
    for x in [x for x in trades if x["ev"] == "sell"][-25:]:
        mk = x.get("maker")
        tag = "maker" if mk is True else "mixed" if mk == "mixed" else "taker" if mk is False else ""
        L.append(f"| {x['t'][5:16]} | {x['pid'][:-4]} | {x['entry_px']:.6g} | {x['px']:.6g} | {x['held_min']:.0f} m | {x['net_pct']*100:+.2f}% (${x['net']:+.3f}) | "
                 f"${x.get('fee', 0):.3f} {tag} | {x['reason']} |")
    L.append("")
    L.append("## Last 25 events\n")
    for e in events[-25:]:
        L.append(f"- `{e['t'][5:19]}` **{e['ev']}** " + ", ".join(f"{k}={json.dumps(v, default=str)[:60]}" for k, v in e.items() if k not in ("t", "ev")))
    L.append("")
    L.append("Paper twin: mrh/MRH.md · the 30-day replay (the real verdict): mrh-backtest/BACKTEST.md on this branch.\n")
    txt = "\n".join(L) + "\n"
    (out / "LIVE.md").write_text(txt)
    return txt


# ----------------------------------------------------------------------------------------------- runner

def run(out: Path, minutes: float, dry: bool) -> None:
    from pb.errlog import guard, record
    with guard(BOT, out=out):
        key, sec = os.environ.get("COINBASE_API_KEY", ""), os.environ.get("COINBASE_API_SECRET", "")
        if not key or not sec:
            print("no COINBASE_API_KEY / COINBASE_API_SECRET — nothing to do", flush=True)
            return
        ex, cb = CDP(key, sec), paper.Coinbase()
        st = load_state(out)
        event(out, "start", mode="dry" if dry else "live", key=key[-12:], alg=ex.alg, max_usd=MAX_USD, floor=FLOOR_USD, max_hops_day=MAX_HOPS_DAY,
              maker=True, fast_s=FAST_S, entry_ttl_min=ENTRY_TTL_MIN, entry_chase=ENTRY_CHASE, disaster_gap=DISASTER_GAP, panic_gap=PANIC_GAP)
        t_end = time.time() + minutes * 60
        bad = 0
        while True:
            on, why = switch_on(out)
            if not on:
                event(out, "switch_off", why=why, note="no new orders; a resting sell or parked stop stays on the exchange")
                report(out)
                return
            try:
                s = cycle(ex, cb, out, st, dry)
                bad = 0
                print(f"{s.get('t')} usd={s.get('usd')} total={s.get('total')} pos={s.get('pos')} entry={s.get('entry')} calls={ex.calls}+{cb.calls}", flush=True)
            except Exception as e:   # a transient exchange/network error must not end the run; auth errors must
                msg = str(e)
                if " -> 401" in msg or " -> 403" in msg or bad >= 4:
                    raise
                bad += 1
                record(BOT, type(e).__name__, msg, out, cycle=st.get("cycles"), consecutive=bad)
                save_state(out, st)
            report(out)
            if time.time() + CANDLE_S > t_end:
                break
            nxt = (int(time.time()) // CANDLE_S + 1) * CANDLE_S + 15
            while time.time() < nxt - 1:
                if not need_fast(st):
                    time.sleep(max(1.0, nxt - time.time()))
                    break
                try:
                    if quick(ex, cb, out, st, dry):
                        save_state(out, st)
                        report(out)
                    bad = 0
                except Exception as e:
                    msg = str(e)
                    if " -> 401" in msg or " -> 403" in msg or bad >= 8:
                        raise
                    bad += 1
                    record(BOT, type(e).__name__, msg, out, cycle=st.get("cycles"), consecutive=bad, where="quick")
                    save_state(out, st)
                time.sleep(max(1.0, min(FAST_S, nxt - time.time())))


# ----------------------------------------------------------------------------------------------- selftest

class FakeEx:
    """Exchange double: balances with holds, market fills at the fake touch, resting post-only limits that fill when
    the market trades through them (maker fee), resting stops that fill when the bid crosses (taker fee)."""

    def __init__(self, cb, usd: float = 0.0, coins: dict | None = None, fee: float = paper.TAKER_FEE, maker_fee: float = MAKER_FEE):
        self.cb, self.fee, self.maker_fee = cb, fee, maker_fee
        self.bal = {"USD": usd, **(coins or {})}
        self.hold: dict[str, float] = {}
        self.orders: dict[str, dict] = {}
        self.holds_by_order: dict[str, tuple[str, float]] = {}
        self.fills_: list[dict] = []
        self.alg, self.calls = "fake", 0
        self.rejects = 0

    def accounts(self):
        return [{"currency": c, "available": v - self.hold.get(c, 0.0), "hold": self.hold.get(c, 0.0)} for c, v in self.bal.items()]

    def _px(self, pid):
        return self.cb.bids[pid]

    def _avail(self, cur):
        return self.bal.get(cur, 0.0) - self.hold.get(cur, 0.0)

    def _hold(self, oid, cur, amt):
        self.hold[cur] = self.hold.get(cur, 0.0) + amt
        self.holds_by_order[oid] = (cur, amt)

    def _release(self, oid):
        cur, amt = self.holds_by_order.pop(oid, (None, 0.0))
        if cur:
            self.hold[cur] -= amt

    def create_order(self, body):
        oid = "o" + uuid.uuid4().hex[:8]
        pid, side, cfg = body["product_id"], body["side"], body["order_configuration"]
        base = pid[:-4]
        bid = self._px(pid)
        ask = bid * 1.001
        o = {"order_id": oid, "product_id": pid, "side": side, "client_order_id": body["client_order_id"], "order_configuration": cfg,
             "status": "OPEN", "filled_size": "0", "average_filled_price": "0", "total_fees": "0", "filled_value": "0"}
        if "market_market_ioc" in cfg:
            if side == "BUY":
                quote = float(cfg["market_market_ioc"]["quote_size"])
                if quote > self._avail("USD") + 1e-9:
                    return {"success": False, "error_response": {"error": "INSUFFICIENT_FUND"}}
                fee = quote * self.fee
                qty = (quote - fee) / ask
                self.bal["USD"] -= quote
                self.bal[base] = self.bal.get(base, 0) + qty
                o.update(status="FILLED", filled_size=str(qty), average_filled_price=str(ask), total_fees=str(fee), filled_value=str(quote - fee))
                self.fills_.append({"product_id": pid, "side": "BUY", "price": str(ask), "size": str(qty)})
            else:
                qty = float(cfg["market_market_ioc"]["base_size"])
                if qty > self._avail(base) + 1e-9:
                    return {"success": False, "error_response": {"error": "INSUFFICIENT_FUND"}}
                gross = qty * bid
                fee = gross * self.fee
                self.bal[base] -= qty
                self.bal["USD"] = self.bal.get("USD", 0) + gross - fee
                o.update(status="FILLED", filled_size=str(qty), average_filled_price=str(bid), total_fees=str(fee), filled_value=str(gross))
        elif "limit_limit_gtc" in cfg:
            c = cfg["limit_limit_gtc"]
            qty, px = float(c["base_size"]), float(c["limit_price"])
            if side == "BUY":
                if c.get("post_only") and px >= ask:
                    self.rejects += 1
                    return {"success": False, "error_response": {"error": "INVALID_LIMIT_PRICE_POST_ONLY"}}
                need = qty * px * (1 + self.fee)
                if need > self._avail("USD") + 1e-9:
                    return {"success": False, "error_response": {"error": "INSUFFICIENT_FUND"}}
                self._hold(oid, "USD", need)
            else:
                if c.get("post_only") and px <= bid:
                    self.rejects += 1
                    return {"success": False, "error_response": {"error": "INVALID_LIMIT_PRICE_POST_ONLY"}}
                if qty > self._avail(base) + 1e-9:
                    return {"success": False, "error_response": {"error": "INSUFFICIENT_FUND"}}
                self._hold(oid, base, qty)
        else:
            c = cfg["stop_limit_stop_limit_gtc"]
            qty = float(c["base_size"])
            if qty > self._avail(base) + 1e-9:
                return {"success": False, "error_response": {"error": "INSUFFICIENT_FUND"}}
            self._hold(oid, base, qty)
        self.orders[oid] = o
        return {"success": True, "success_response": {"order_id": oid}}

    def tick(self):
        """Fill resting orders the market has traded through: limits at their price (maker fee), stops at the stop (taker)."""
        for oid, o in self.orders.items():
            if o["status"] != "OPEN":
                continue
            pid, base = o["product_id"], o["product_id"][:-4]
            bid = self._px(pid)
            ask = bid * 1.001
            cfg = o["order_configuration"]
            if "limit_limit_gtc" in cfg:
                c = cfg["limit_limit_gtc"]
                qty, px = float(c["base_size"]), float(c["limit_price"])
                if o["side"] == "BUY" and ask <= px:
                    fee = qty * px * self.maker_fee
                    self._release(oid)
                    self.bal["USD"] -= qty * px + fee
                    self.bal[base] = self.bal.get(base, 0) + qty
                    o.update(status="FILLED", filled_size=str(qty), average_filled_price=str(px), total_fees=str(fee), filled_value=str(qty * px))
                    self.fills_.append({"product_id": pid, "side": "BUY", "price": str(px), "size": str(qty)})
                elif o["side"] == "SELL" and bid >= px:
                    fee = qty * px * self.maker_fee
                    self._release(oid)
                    self.bal[base] -= qty
                    self.bal["USD"] = self.bal.get("USD", 0) + qty * px - fee
                    o.update(status="FILLED", filled_size=str(qty), average_filled_price=str(px), total_fees=str(fee), filled_value=str(qty * px))
            elif "stop_limit_stop_limit_gtc" in cfg:
                c = cfg["stop_limit_stop_limit_gtc"]
                if bid <= float(c["stop_price"]):
                    qty, px = float(c["base_size"]), float(c["stop_price"])
                    gross, fee = qty * px, qty * px * self.fee
                    self._release(oid)
                    self.bal[base] -= qty
                    self.bal["USD"] = self.bal.get("USD", 0) + gross - fee
                    o.update(status="FILLED", filled_size=str(qty), average_filled_price=str(px), total_fees=str(fee), filled_value=str(gross))

    def cancel(self, ids):
        res = []
        for i in ids:
            o = self.orders.get(i)
            if o and o["status"] == "OPEN":
                o["status"] = "CANCELLED"
                self._release(i)
                res.append({"order_id": i, "success": True})
            else:
                res.append({"order_id": i, "success": False})
        return res

    def order(self, oid):
        return self.orders.get(oid, {})

    def open_orders(self, pid):
        return [o for o in self.orders.values() if o["status"] == "OPEN" and o["product_id"] == pid]

    def fills(self, pid, limit=50):
        return [f for f in reversed(self.fills_) if f["product_id"] == pid]


def selftest() -> None:
    import tempfile
    from datetime import timedelta
    global MAX_HOPS_DAY
    # --- JWT: both key types sign a verifiable token with the right claims
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec, ed25519
    from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
    k = ec.generate_private_key(ec.SECP256R1())
    pem = k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
    key, alg = load_key(pem.replace("\n", "\\n"))
    assert alg == "ES256"
    tok = build_jwt("organizations/x/apiKeys/y", key, alg, "GET", f"{PRIV}/accounts", t=1_800_000_000)
    h, p, s = tok.split(".")
    hdr, pay = json.loads(base64.urlsafe_b64decode(h + "==")), json.loads(base64.urlsafe_b64decode(p + "=="))
    assert hdr["alg"] == "ES256" and hdr["kid"] == "organizations/x/apiKeys/y" and len(hdr["nonce"]) == 32
    assert pay == {"sub": "organizations/x/apiKeys/y", "iss": "cdp", "nbf": 1_800_000_000, "exp": 1_800_000_120, "uri": f"GET {HOST}{PRIV}/accounts"}
    sig = base64.urlsafe_b64decode(s + "==")
    k.public_key().verify(encode_dss_signature(int.from_bytes(sig[:32], "big"), int.from_bytes(sig[32:], "big")), f"{h}.{p}".encode(), ec.ECDSA(hashes.SHA256()))
    ek = ed25519.Ed25519PrivateKey.generate()
    raw = ek.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
    key2, alg2 = load_key(base64.b64encode(raw + ek.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode())
    assert alg2 == "EdDSA"
    tok2 = build_jwt("k", key2, alg2, "POST", f"{PRIV}/orders")
    h2, p2, s2 = tok2.split(".")
    ek.public_key().verify(base64.urlsafe_b64decode(s2 + "=="), f"{h2}.{p2}".encode())
    # --- rounding
    assert floor_to(3.456789, "0.01") == "3.45" and floor_to(0.00259558, "0.00000001") == "0.00259558"
    assert floor_to(1234.999, "1") == "1234" and floor_to(0.1 + 0.2, "0.01") == "0.3" and floor_to(39.99999, "0.1") == "39.9"

    # --- the book against the fake exchange. 1) adopt a hand-bought coin, park the disaster stop, re-park on a new high
    out = Path(tempfile.mkdtemp()) / "mrh"
    cb = paper.FakeCB()
    cb.bids["FLAT-USD"] = 10.0
    ex = FakeEx(cb, usd=0.0, coins={"FLAT": 0.345, "DUST": 0.001})
    st = load_state(out)
    t = datetime.fromtimestamp(cb.t0 + CANDLE_S * 30 + 20, tz=timezone.utc)   # before PUMP's signal candle
    st["products"]["DUST-USD"] = {"base_inc": "0.01", "quote_inc": "0.01", "quote_min": 1.0, "base_min": 0, "price": 1.0}
    cycle(ex, cb, out, st, False, t)
    pos = st["pos"]
    assert pos and pos["pid"] == "FLAT-USD" and pos["signal"] == {"adopted": True} and abs(pos["hw"] - 10.0) < 1e-9, pos
    assert pos["stop"]["order_id"] and abs(pos["stop"]["stop_px"] - 10.0 * (1 - TRAIL - DISASTER_GAP)) < 1e-9, pos["stop"]
    assert abs(st["start_usd"] - 3.45) < 1e-6 and len(ex.open_orders("FLAT-USD")) == 1
    cb.bids["FLAT-USD"] = 10.5
    cycle(ex, cb, out, st, False, t + timedelta(minutes=5))
    assert abs(st["pos"]["stop"]["stop_px"] - 10.5 * 0.90) < 1e-9 and len(ex.open_orders("FLAT-USD")) == 1, st["pos"]["stop"]
    # 2) the bid touches the trail (10.08): first tick is a blip, second confirms -> maker sell posted at the ask, stop cancelled
    cb.bids["FLAT-USD"] = 10.05
    assert not quick(ex, cb, out, st, False) and st["pos"]["trail_hits"] == 1 and not st["pos"].get("exit")
    assert quick(ex, cb, out, st, False)
    x = st["pos"]["exit"]
    assert x and x["reason"] == "trail" and abs(x["px"] - 10.06) < 1e-9 and x["order_id"], x       # max(ask 10.06005->10.06, bid+tick 10.06)
    opens = ex.open_orders("FLAT-USD")
    assert len(opens) == 1 and "limit_limit_gtc" in opens[0]["order_configuration"] and opens[0]["order_configuration"]["limit_limit_gtc"]["post_only"]
    assert st["pos"]["stop"] is None
    ex.tick()                                                                   # bid 10.05 < 10.06: no fill yet
    assert not quick(ex, cb, out, st, False)                                     # ask unchanged: we wait
    # 3) the market drops away from us: chase down to the new ask (still maker), then a buyer lifts us
    cb.bids["FLAT-USD"] = 9.90
    assert quick(ex, cb, out, st, False)
    x = st["pos"]["exit"]
    assert abs(x["px"] - 9.91) < 1e-9 and x["reposts"] == 1 and len(ex.open_orders("FLAT-USD")) == 1, x
    cb.bids["FLAT-USD"] = 9.93
    ex.tick()
    assert quick(ex, cb, out, st, False) and st["pos"] is None and st["hops"] == 1, st
    tr = paper.read_jsonl(out / "live_trades.jsonl")
    assert tr[-1]["ev"] == "sell" and tr[-1]["reason"] == "trail" and tr[-1]["maker"] is True and abs(tr[-1]["px"] - 9.91) < 1e-9, tr[-1]
    usd = ex.bal["USD"]
    assert abs(usd - 0.345 * 9.91 * (1 - MAKER_FEE)) < 1e-9 and sum(ex.hold.values()) < 1e-12, (usd, ex.hold)
    assert ex.rejects == 0
    # 4) PUMP signals: a post-only buy rests at the bid for the whole bankroll (fee headroom kept); no fill while the ask is above it
    t2 = datetime.fromtimestamp(cb.t0 + CANDLE_S * 41 + 20, tz=timezone.utc)   # PUMP's signal candle has closed
    cycle(ex, cb, out, st, False, t2)
    e = st["entry"]
    assert e and e["pid"] == "PUMP-USD" and abs(e["px"] - 1.10) < 1e-9 and st["pos"] is None, e
    assert abs(e["qty"] - float(floor_to(usd / (1.10 * (1 + FEE_BUFFER)), "0.00000001"))) < 1e-9, (e["qty"], usd)
    assert abs(e["cap_px"] - 1.10 * (1 + ENTRY_CHASE)) < 1e-9
    assert len(ex.open_orders("PUMP-USD")) == 1 and ex.hold["USD"] > 0
    ex.tick()
    assert not quick(ex, cb, out, st, False) and st["entry"]                      # ask 1.1011 > 1.10: resting
    # a second cycle while the buy rests does nothing else (no double entry, no adoption of a partial)
    cycle(ex, cb, out, st, False, t2 + timedelta(minutes=5))
    assert st["entry"] and st["pos"] is None and len(ex.open_orders("PUMP-USD")) == 1
    # 5) the bid runs: re-price up to it, but never above the cap; then a seller hits our bid -> position opened at the limit
    cap_grid = float(floor_to(e["cap_px"], "0.01"))                              # 1.122 -> 1.12 on the fake's 1-cent grid
    cb.bids["PUMP-USD"] = 1.115
    assert quick(ex, cb, out, st, False) and abs(st["entry"]["px"] - 1.11) < 1e-9 and st["entry"]["reposts"] == 1, st["entry"]
    cb.bids["PUMP-USD"] = 1.15
    assert quick(ex, cb, out, st, False) and abs(st["entry"]["px"] - cap_grid) < 1e-9 and st["entry"]["reposts"] == 2, st["entry"]
    cb.bids["PUMP-USD"] = 1.16
    assert not quick(ex, cb, out, st, False) and st["entry"]["reposts"] == 2    # at the cap: we wait for the pullback
    cb.bids["PUMP-USD"] = 1.115                                                  # ask 1.116 <= 1.12: a seller hits our bid
    ex.tick()
    assert quick(ex, cb, out, st, False) and st["entry"] is None
    pos = st["pos"]
    assert pos and pos["pid"] == "PUMP-USD" and abs(pos["entry_px"] - cap_grid) < 1e-9 and pos["stop"] is None, pos
    buy = [x for x in paper.read_jsonl(out / "live_trades.jsonl") if x["ev"] == "buy"][-1]
    assert buy["maker"] is True and abs(buy["fee"] - pos["qty"] * pos["entry_px"] * MAKER_FEE) < 1e-9, buy
    assert ex.bal["USD"] < usd * 0.02 and ex.hold.get("USD", 0) < 1e-12, (ex.bal["USD"], ex.hold)   # nearly all in; nothing held
    cycle(ex, cb, out, st, False, t2 + timedelta(minutes=10))
    assert st["pos"]["stop"]["order_id"] and abs(st["pos"]["stop"]["stop_px"] - pos["hw"] * 0.90) < 1e-9       # disaster stop parked
    # 6) crash: trail hit hard (one tick is enough), maker sell posted, then the bid falls through the panic line -> taker sell
    cb.bids["PUMP-USD"] = 1.30
    cycle(ex, cb, out, st, False, t2 + timedelta(minutes=15))
    assert abs(st["pos"]["hw"] - 1.30) < 1e-9
    cb.bids["PUMP-USD"] = 1.22                                                   # trail 1.248, hard line 1.2355: exit at once
    assert quick(ex, cb, out, st, False) and st["pos"]["exit"] and abs(st["pos"]["exit"]["px"] - 1.23) < 1e-9, st["pos"]["exit"]
    cb.bids["PUMP-USD"] = 1.20                                                   # panic line 1.30*(1-0.04-0.03)=1.209
    st["pos"]["exit"]["t_posted"] = iso(now() - timedelta(seconds=FAST_S + 1))
    assert quick(ex, cb, out, st, False) and st["pos"] is None and st["hops"] == 2
    tr = paper.read_jsonl(out / "live_trades.jsonl")
    assert tr[-1]["reason"] == "trail+panic" and tr[-1]["maker"] is False and abs(tr[-1]["px"] - 1.20) < 1e-9, tr[-1]
    assert not ex.open_orders("PUMP-USD") and sum(ex.hold.values()) < 1e-12
    # --- caps: daily hop cap blocks the next entry; floor halts when flat and tiny
    MAX_HOPS_DAY = 2
    cycle(ex, cb, out, st, False, t2 + timedelta(minutes=20))
    assert st["entry"] is None and st["last"].get("note") == "daily hop cap", st["last"]
    MAX_HOPS_DAY = 6
    ex.bal["USD"] = 0.90
    cycle(ex, cb, out, st, False, t2 + timedelta(minutes=25))
    assert st["halted"] and st["halted"].startswith("floor"), st["halted"]
    # --- entry TTL: a buy nobody sells into is cancelled, the USD comes back, nothing is held
    out2 = Path(tempfile.mkdtemp()) / "mrh"
    cb2 = paper.FakeCB()
    ex2 = FakeEx(cb2, usd=4.0)
    st2 = load_state(out2)
    cycle(ex2, cb2, out2, st2, False, t2)
    assert st2["entry"] and ex2.hold["USD"] > 0
    st2["entry"]["t"] = iso(now() - timedelta(minutes=ENTRY_TTL_MIN + 1))
    assert quick(ex2, cb2, out2, st2, False) and st2["entry"] is None and st2["pos"] is None
    assert abs(ex2.bal["USD"] - 4.0) < 1e-12 and ex2.hold["USD"] < 1e-12 and not ex2.open_orders("PUMP-USD")
    assert any(e["ev"] == "entry_ended" and e["why"] == "expired" for e in paper.read_jsonl(out2 / "live_events.jsonl"))
    # --- swap: an adopted coin plus idle USD gives way to a fresh signal: maker sell first, then the buy with the whole stack
    out3 = Path(tempfile.mkdtemp()) / "mrh"
    cb3 = paper.FakeCB()
    cb3.bids["FLAT-USD"] = 10.0
    ex3 = FakeEx(cb3, usd=10.0, coins={"FLAT": 0.345})
    st3 = load_state(out3)
    cycle(ex3, cb3, out3, st3, False, t2)                                       # PUMP signal candle has closed
    x = st3["pos"]["exit"]
    assert st3["pos"]["pid"] == "FLAT-USD" and x and x["reason"] == "swap" and x["sig"]["pid"] == "PUMP-USD" and abs(x["px"] - 10.01) < 1e-9, x
    cb3.bids["FLAT-USD"] = 10.02
    ex3.tick()                                                                  # a buyer lifts our ask
    assert quick(ex3, cb3, out3, st3, False) and st3["pos"] is None and st3["hops"] == 1
    e3 = st3["entry"]
    assert e3 and e3["pid"] == "PUMP-USD" and st3.get("pending_sig") is None, (e3, st3.get("pending_sig"))
    stack = 10.0 + 0.345 * 10.01 * (1 - MAKER_FEE)
    assert abs(e3["budget"] - stack) < 1e-9, (e3["budget"], stack)
    tr3 = paper.read_jsonl(out3 / "live_trades.jsonl")
    assert [x["ev"] for x in tr3] == ["sell"] and tr3[0]["reason"] == "swap" and tr3[0]["maker"] is True
    # a signalled coin is NOT swappable while it keeps making highs, and IS once it has gone stale
    cb3.bids["PUMP-USD"] = 1.09
    ex3.tick()
    quick(ex3, cb3, out3, st3, False)
    pos3 = st3["pos"]
    assert pos3 and pos3["pid"] == "PUMP-USD" and not swap_due(pos3)
    pos3["hw_t"] = iso(now() - timedelta(hours=3))
    assert swap_due(pos3)
    # --- deposits are flows, not profit
    out4 = Path(tempfile.mkdtemp()) / "mrh"
    cb4 = paper.FakeCB()
    ex4 = FakeEx(cb4, usd=4.0)
    st4 = load_state(out4)
    cycle(ex4, cb4, out4, st4, False, t)                                        # flat, no signal yet
    ex4.bal["USD"] += 5.0
    cycle(ex4, cb4, out4, st4, False, t + timedelta(minutes=5))
    assert abs(st4["flows"] - 5.0) < 1e-9 and abs(st4["last"]["total"] - 9.0) < 1e-9, st4
    rep = report(out4)
    assert "| $9.00 | $4.00 | $+5.00 | $+0.00" in rep, rep
    # --- dry mode sends nothing
    ex5 = FakeEx(cb, usd=4.0)
    st5 = load_state(Path(tempfile.mkdtemp()) / "mrh")
    cb.bids["PUMP-USD"] = 1.10
    cycle(ex5, cb, Path(tempfile.mkdtemp()), st5, True, t2)
    assert st5["pos"] is None and not ex5.orders and abs(ex5.bal["USD"] - 4.0) < 1e-12 and st5["entry"]
    txt = report(out)
    assert "LIVE" in txt and "HALTED" in txt and "PUMP" in txt and "maker" in txt
    print("selftest ok:", {"hops": st["hops"], "wins": st["wins"], "fees": round(st["fees"], 4), "post_only_rejects": ex.rejects})


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--out", default="data/mrh-live"); r.add_argument("--minutes", type=float, default=335)
    r.add_argument("--dry", action="store_true", help="everything but sending orders")
    p = sub.add_parser("report"); p.add_argument("--out", default="data/mrh-live")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        run(Path(a.out), a.minutes, a.dry)
    elif a.cmd == "report":
        print(report(Path(a.out)))
    else:
        selftest()


if __name__ == "__main__":
    main()
