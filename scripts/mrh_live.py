#!/usr/bin/env python3
"""Mr. H LIVE — the Coinbase hopper with a real key. REAL MONEY, hard-capped.

Runs the paper bot's *aggressive* profile (scripts/mrh_paper.py — same universe, same signal, same spread gate)
with real orders on Coinbase Advanced Trade:

  enter   ONE 5-min impulse candle (>= +2% close/open, volume >= 3x the 2-h median), spread <= 0.6%, strongest
          candidate first; market buy with the whole USD bankroll (capped at MRH_LIVE_MAX_USD).
  exit    4% trailing stop from the high-water mark, enforced two ways: a stop-limit sell PARKED ON THE EXCHANGE
          (a dump while the runner sleeps, or in the gap between runs, still gets out) and the bot's own market-sell
          backstop on the live bid every 5 minutes.

Guards: switch file mrh/LIVE_ON on main and no mrh/PAUSED (checked every cycle); one position; at most
MRH_LIVE_MAX_HOPS_DAY sells per UTC day; MRH_LIVE_MAX_USD per entry (a deposit does not become bot money); halts
below MRH_LIVE_FLOOR_USD total (Coinbase's $1 minimum would strand anything smaller); never touches any asset other
than USD and the one coin it holds.

The exchange is the truth: every cycle reconciles balances, open orders and fills. A position bought by hand is
adopted and trailed; a parked stop that filled while the bot slept is booked from its fill.

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
STOP_LIMIT_GAP = 0.015             # stop-limit's limit sits 1.5% under the stop so it fills on a thin book
STOP_REPLACE_MIN = 0.001           # re-park the stop when the high-water mark moved >= 0.1%
DUST_USD = 1.00                    # holdings worth less than this are not "a position"
STABLES = {"USD", "USDC", "USDT", "DAI", "PYUSD", "GUSD", "USDP", "TUSD", "EURC", "USDS", "RLUSD", "PAX", "EUR", "GBP"}

MAX_USD = float(os.environ.get("MRH_LIVE_MAX_USD", "12"))          # per entry
FLOOR_USD = float(os.environ.get("MRH_LIVE_FLOOR_USD", "1.20"))    # halt below this total
MAX_HOPS_DAY = int(os.environ.get("MRH_LIVE_MAX_HOPS_DAY", "6"))
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
    """(available USD, [{pid, qty, available, hold, bid, value}] for every tradable coin worth >= DUST_USD)."""
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
        return None
    if not j.get("success"):
        err = j.get("error_response") or j
        event(out, "order_rejected", label=label, pid=pid, side=side, cfg=cfg, err=err)
        return None
    oid = (j.get("success_response") or {}).get("order_id")
    event(out, "order_sent", label=label, pid=pid, side=side, cfg=cfg, order_id=oid)
    return {"order_id": oid}


def cancel_and_confirm(ex: CDP, out: Path, order_id: str) -> str:
    """Cancel a resting order; return its final status (CANCELLED / FILLED / ...). FILLED means it already exited us."""
    try:
        ex.cancel([order_id])
    except Exception as e:
        event(out, "cancel_error", order_id=order_id, err=str(e)[:200])
    o = wait_done(ex, order_id, timeout_s=8)
    return o.get("status") or "UNKNOWN"


def park_stop(ex: CDP, cb, out: Path, st: dict, dry: bool) -> None:
    """Keep a stop-limit sell resting on the exchange at hw*(1-trail) for the whole position."""
    pos = st["pos"]
    p = st["products"].get(pos["pid"]) or {"base_inc": "0.00000001", "quote_inc": "0.01"}
    stop_px = pos["hw"] * (1 - TRAIL)
    cur = pos.get("stop")
    if cur and cur.get("order_id"):
        status = (ex.order(cur["order_id"]) or {}).get("status") or "UNKNOWN"   # is it really still resting?
        if status == "FILLED":
            pos["stop"]["filled"] = True       # booked by reconcile next cycle
            return
        if status in ("CANCELLED", "EXPIRED", "FAILED"):
            event(out, "stop_missing", order_id=cur["order_id"], status=status, note="re-parking")
            pos["stop"] = None
        elif abs(stop_px / cur["stop_px"] - 1) < STOP_REPLACE_MIN:
            return                             # resting at the right level: nothing to do
        else:
            status = cancel_and_confirm(ex, out, cur["order_id"])
            if status == "FILLED":
                pos["stop"]["filled"] = True
                return
            pos["stop"] = None
    qty = pos["qty"]
    for attempt in range(2):
        cfg = {"stop_limit_stop_limit_gtc": {"base_size": floor_to(qty, p["base_inc"]), "limit_price": floor_to(stop_px * (1 - STOP_LIMIT_GAP), p["quote_inc"]),
                                             "stop_price": floor_to(stop_px, p["quote_inc"]), "stop_direction": "STOP_DIRECTION_STOP_DOWN"}}
        r = place(ex, out, dry, pos["pid"], "SELL", cfg, "park_stop")
        if r or dry:
            pos["stop"] = {"order_id": r["order_id"] if r else None, "stop_px": stop_px, "t": iso(now())}
            return
        time.sleep(2.0)   # funds from a just-cancelled stop may take a moment to release


def market_sell_all(ex: CDP, cb, out: Path, st: dict, dry: bool, reason: str) -> dict | None:
    pos = st["pos"]
    p = st["products"].get(pos["pid"]) or {"base_inc": "0.00000001"}
    if pos.get("stop") and pos["stop"].get("order_id"):
        status = cancel_and_confirm(ex, out, pos["stop"]["order_id"])
        if status == "FILLED":
            pos["stop"]["filled"] = True
            return None          # the exchange already sold it; reconcile books it
        pos["stop"] = None
    r = None
    for attempt in range(3):      # a just-cancelled stop can hold the coins for a moment: retry, don't wait 5 min in a dump
        r = place(ex, out, dry, pos["pid"], "SELL", {"market_market_ioc": {"base_size": floor_to(pos["qty"], p["base_inc"])}}, f"sell:{reason}")
        if r or dry:
            break
        time.sleep(2.0)
    if dry or not r:
        return None
    o = wait_done(ex, r["order_id"])
    f = fill_facts(o)
    if f["qty"] <= 0:
        event(out, "sell_unfilled", **f)
        return None
    return book_sell(out, st, f, reason)


def book_sell(out: Path, st: dict, f: dict, reason: str) -> dict:
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
           "held_min": round(held_min, 1), "reason": reason, "order_id": f["order_id"]}
    paper.append(out, "live_trades.jsonl", rec)
    event(out, "sold", pid=pos["pid"], px=f["px"], net=rec["net"], net_pct=rec["net_pct"], reason=reason)
    st["pos"] = None
    return rec


def buy(ex: CDP, cb, out: Path, st: dict, dry: bool, sig: dict, usd: float) -> dict | None:
    pid = sig["pid"]
    p = st["products"].get(pid) or {"quote_inc": "0.01", "quote_min": 1.0}
    spend = min(usd, MAX_USD)
    if spend < max(p["quote_min"], 1.0):
        event(out, "entry_skipped", reason="below_min", usd=usd, pid=pid)
        return None
    for attempt in range(2):
        cfg = {"market_market_ioc": {"quote_size": floor_to(spend, p["quote_inc"])}}
        r = place(ex, out, dry, pid, "BUY", cfg, "buy")
        if dry:
            return None
        if r:
            break
        spend *= 0.99      # INSUFFICIENT_FUND from fee rounding: try 1% less, once
    else:
        return None
    o = wait_done(ex, r["order_id"])
    f = fill_facts(o)
    if f["qty"] <= 0:
        event(out, "buy_unfilled", **f)
        return None
    cost = (f["value"] if f["value"] else f["qty"] * f["px"]) + f["fee"]
    st["fees"] += f["fee"]
    st["pos"] = {"pid": pid, "qty": f["qty"], "entry_px": f["px"], "cost": cost, "hw": f["px"], "t_in": iso(now()),
                 "signal": {k: sig[k] for k in ("impulse", "vol_mult", "above_2h_high")}, "stop": None, "order_id": f["order_id"]}
    rec = {"t": iso(now()), "ev": "buy", "pid": pid, "px": f["px"], "qty": f["qty"], "cost": round(cost, 4), "fee": f["fee"], "signal": st["pos"]["signal"],
           "order_id": f["order_id"]}
    paper.append(out, "live_trades.jsonl", rec)
    event(out, "bought", pid=pid, px=f["px"], qty=f["qty"], cost=round(cost, 4))
    return rec


# ----------------------------------------------------------------------------------------------- reconcile

def reconcile(ex: CDP, cb, out: Path, st: dict) -> tuple[float, list[dict]]:
    """Make the state agree with the exchange. Returns (usd available, held coins)."""
    usd, held = holdings(ex, cb, st)
    pos = st["pos"]
    on_ex = {h["pid"]: h for h in held}
    if pos and pos["pid"] not in on_ex:
        # we think we hold it, the exchange says no: the parked stop (or a human) sold it while we slept
        f = None
        if pos.get("stop") and pos["stop"].get("order_id"):
            try:
                f = fill_facts(ex.order(pos["stop"]["order_id"]))
            except Exception as e:
                event(out, "reconcile_error", err=str(e)[:200])
        if f and f["qty"] > 0:
            book_sell(out, st, f, "stop")
        else:
            event(out, "position_gone", pid=pos["pid"], note="sold outside the bot; booked at last known bid")
            book_sell(out, st, {"order_id": None, "status": "EXTERNAL", "qty": pos["qty"], "px": pos.get("last_bid", pos["entry_px"]), "fee": 0.0, "value": 0.0}, "external")
        pos = None
    if pos and pos["pid"] in on_ex:
        h = on_ex[pos["pid"]]
        if abs(h["qty"] - pos["qty"]) / max(pos["qty"], 1e-12) > 0.01:
            event(out, "qty_adjusted", pid=pos["pid"], was=pos["qty"], now=h["qty"])
            pos["qty"] = h["qty"]
        pos["last_bid"] = h["bid"]
    if not pos and held:
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
        stop = None
        try:   # adopt a stop we parked in an earlier run whose state was lost
            for o in ex.open_orders(h["pid"]):
                if o.get("side") == "SELL" and str(o.get("client_order_id", "")).startswith(CID_PREFIX):
                    sp = float(((o.get("order_configuration") or {}).get("stop_limit_stop_limit_gtc") or {}).get("stop_price") or 0)
                    stop = {"order_id": o["order_id"], "stop_px": sp, "t": iso(now())}
                    break
        except Exception as e:
            event(out, "open_orders_error", err=str(e)[:200])
        st["pos"] = {"pid": h["pid"], "qty": h["qty"], "entry_px": entry, "cost": cost, "hw": max(entry, h["bid"]), "t_in": iso(now()),
                     "signal": {"adopted": True}, "stop": stop, "last_bid": h["bid"]}
        event(out, "adopted", pid=h["pid"], qty=h["qty"], entry_px=entry, value=round(h["value"], 2), stop=bool(stop))
    total = usd + (st["pos"]["qty"] * st["pos"]["last_bid"] if st["pos"] else 0.0)
    if st["start_usd"] is None:
        st["start_usd"] = round(total, 4)
    st["peak"] = max(st["peak"], total)
    st["last"] = {"t": iso(now()), "usd": round(usd, 4), "total": round(total, 4), "pos": st["pos"]["pid"] if st["pos"] else None}
    return usd, held


# ----------------------------------------------------------------------------------------------- one cycle

def cycle(ex: CDP, cb, out: Path, st: dict, dry: bool, t: datetime | None = None) -> dict:
    t = t or now()
    refresh_universe(cb, st, t)
    usd, held = reconcile(ex, cb, out, st)
    pos = st["pos"]
    total = st["last"]["total"]
    if pos:
        bid = cb.ticker(pos["pid"])["bid"] if pos.get("last_bid") is None else pos["last_bid"]
        pos["hw"] = max(pos["hw"], bid)
        stop_px = pos["hw"] * (1 - TRAIL)
        if bid <= stop_px:
            market_sell_all(ex, cb, out, st, dry, "trail")        # backstop: the parked stop should have done this
        elif pos.get("stop") and pos["stop"].get("filled"):
            pass                                                   # reconcile books it next cycle
        else:
            park_stop(ex, cb, out, st, dry)
    elif st["halted"]:
        pass
    elif total < FLOOR_USD:
        st["halted"] = f"floor: ${total:.2f} < ${FLOOR_USD:.2f}"
        event(out, "halted", reason=st["halted"])
    elif st["hops_by_day"].get(iso(now())[:10], 0) >= MAX_HOPS_DAY:    # same clock as book_sell
        st.setdefault("last", {})["note"] = "daily hop cap"
    else:
        sig = best_signal(cb, out, st, t)
        if sig:
            event(out, "signal", **sig)
            if buy(ex, cb, out, st, dry, sig, usd):
                park_stop(ex, cb, out, st, dry)
    st["cycles"] += 1
    save_state(out, st)
    return st["last"]


# ----------------------------------------------------------------------------------------------- report

def report(out: Path) -> str:
    st = load_state(out)
    trades = paper.read_jsonl(out / "live_trades.jsonl")
    events = paper.read_jsonl(out / "live_events.jsonl")
    last, pos = st.get("last") or {}, st.get("pos")
    start = st.get("start_usd") or 0.0
    total = last.get("total", 0.0)
    L = ["# Mr. H — Coinbase hopper, LIVE (real money)\n",
         f"Updated {iso(now())} · cycles {st['cycles']} · universe {len(st['universe'])} coins · profile aggressive "
         f"(+{PROFILE['impulse']*100:.0f}% impulse, {PROFILE['vol_mult']:.0f}× volume, {TRAIL*100:.0f}% trail) · caps ${MAX_USD:.2f}/entry, "
         f"{MAX_HOPS_DAY} hops/day, floor ${FLOOR_USD:.2f}\n"]
    if st.get("halted"):
        L.append(f"**HALTED: {st['halted']}** — remove mrh/LIVE_ON, fix, delete `halted` in live_state.json on the data branch, restore.\n")
    L.append("## Book\n")
    L.append("| now | start | vs start | peak | USD free | hops | win % | fees paid | position |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    wr = (st["wins"] / st["hops"] * 100) if st["hops"] else 0.0
    pos_s = "—"
    if pos:
        stop = pos.get("stop") or {}
        pos_s = (f"{pos['pid'][:-4]} {pos['qty']:.6g} @ {pos['entry_px']:.6g} · hw {pos['hw']:.6g} · stop "
                 f"{pos['hw']*(1-TRAIL):.6g} ({'parked' if stop.get('order_id') else 'NOT parked'})")
    L.append(f"| ${total:.2f} | ${start:.2f} | {((total/start-1)*100) if start else 0:+.1f}% | ${st['peak']:.2f} | ${last.get('usd', 0):.2f} | "
             f"{st['hops']} | {wr:.0f}% | ${st['fees']:.3f} | {pos_s} |")
    L.append("")
    L.append("## Hops\n")
    L.append("| time (UTC) | coin | in | out | held | net | reason |")
    L.append("|---|---|---|---|---|---|---|")
    for x in [x for x in trades if x["ev"] == "sell"][-25:]:
        L.append(f"| {x['t'][5:16]} | {x['pid'][:-4]} | {x['entry_px']:.6g} | {x['px']:.6g} | {x['held_min']:.0f} m | {x['net_pct']*100:+.2f}% (${x['net']:+.3f}) | {x['reason']} |")
    L.append("")
    L.append("## Last 25 events\n")
    for e in events[-25:]:
        L.append(f"- `{e['t'][5:19]}` **{e['ev']}** " + ", ".join(f"{k}={json.dumps(v, default=str)[:60]}" for k, v in e.items() if k not in ("t", "ev")))
    L.append("")
    L.append("Paper twin and the signal table (the real verdict): mrh/MRH.md on this branch.\n")
    txt = "\n".join(L) + "\n"
    (out / "LIVE.md").write_text(txt)
    return txt


# ----------------------------------------------------------------------------------------------- runner

def run(out: Path, minutes: float, dry: bool) -> None:
    from pb.errlog import guard
    with guard(BOT, out=out):
        key, sec = os.environ.get("COINBASE_API_KEY", ""), os.environ.get("COINBASE_API_SECRET", "")
        if not key or not sec:
            print("no COINBASE_API_KEY / COINBASE_API_SECRET — nothing to do", flush=True)
            return
        ex, cb = CDP(key, sec), paper.Coinbase()
        st = load_state(out)
        event(out, "start", mode="dry" if dry else "live", key=key[-12:], alg=ex.alg, max_usd=MAX_USD, floor=FLOOR_USD, max_hops_day=MAX_HOPS_DAY)
        t_end = time.time() + minutes * 60
        bad = 0
        while True:
            on, why = switch_on(out)
            if not on:
                event(out, "switch_off", why=why, note="no orders; a parked stop stays on the exchange")
                report(out)
                return
            try:
                s = cycle(ex, cb, out, st, dry)
                bad = 0
                print(f"{s.get('t')} usd={s.get('usd')} total={s.get('total')} pos={s.get('pos')} calls={ex.calls}+{cb.calls}", flush=True)
            except Exception as e:   # a transient exchange/network error must not end the run; auth errors must
                msg = str(e)
                if " -> 401" in msg or " -> 403" in msg or bad >= 4:
                    raise
                bad += 1
                from pb.errlog import record
                record(BOT, type(e).__name__, msg, out, cycle=st.get("cycles"), consecutive=bad)
                save_state(out, st)
            report(out)
            if time.time() + CANDLE_S > t_end:
                break
            nxt = (int(time.time()) // CANDLE_S + 1) * CANDLE_S + 15
            time.sleep(max(1.0, nxt - time.time()))


# ----------------------------------------------------------------------------------------------- selftest

class FakeEx:
    """Exchange double: balances, market fills at the fake ticker, resting stops that fill when the bid crosses."""

    def __init__(self, cb, usd: float = 0.0, coins: dict | None = None, fee: float = paper.TAKER_FEE):
        self.cb, self.fee = cb, fee
        self.bal = {"USD": usd, **(coins or {})}
        self.hold: dict[str, float] = {}
        self.orders: dict[str, dict] = {}
        self.fills_: list[dict] = []
        self.alg, self.calls = "fake", 0

    def accounts(self):
        return [{"currency": c, "available": v - self.hold.get(c, 0.0), "hold": self.hold.get(c, 0.0)} for c, v in self.bal.items()]

    def _px(self, pid):
        return self.cb.bids[pid]

    def create_order(self, body):
        oid = "o" + uuid.uuid4().hex[:8]
        pid, side, cfg = body["product_id"], body["side"], body["order_configuration"]
        base = pid[:-4]
        o = {"order_id": oid, "product_id": pid, "side": side, "client_order_id": body["client_order_id"], "order_configuration": cfg,
             "status": "OPEN", "filled_size": "0", "average_filled_price": "0", "total_fees": "0", "filled_value": "0"}
        if "market_market_ioc" in cfg:
            if side == "BUY":
                quote = float(cfg["market_market_ioc"]["quote_size"])
                if quote > self.bal.get("USD", 0) + 1e-9:
                    return {"success": False, "error_response": {"error": "INSUFFICIENT_FUND"}}
                ask = self._px(pid) * 1.001
                fee = quote * self.fee
                qty = (quote - fee) / ask
                self.bal["USD"] -= quote
                self.bal[base] = self.bal.get(base, 0) + qty
                o.update(status="FILLED", filled_size=str(qty), average_filled_price=str(ask), total_fees=str(fee), filled_value=str(quote - fee))
                self.fills_.append({"product_id": pid, "side": "BUY", "price": str(ask), "size": str(qty)})
            else:
                qty = float(cfg["market_market_ioc"]["base_size"])
                if qty > self.bal.get(base, 0) - self.hold.get(base, 0) + 1e-9:
                    return {"success": False, "error_response": {"error": "INSUFFICIENT_FUND"}}
                bid = self._px(pid)
                gross = qty * bid
                fee = gross * self.fee
                self.bal[base] -= qty
                self.bal["USD"] = self.bal.get("USD", 0) + gross - fee
                o.update(status="FILLED", filled_size=str(qty), average_filled_price=str(bid), total_fees=str(fee), filled_value=str(gross))
        else:
            c = cfg["stop_limit_stop_limit_gtc"]
            qty = float(c["base_size"])
            if qty > self.bal.get(base, 0) - self.hold.get(base, 0) + 1e-9:
                return {"success": False, "error_response": {"error": "INSUFFICIENT_FUND"}}
            self.hold[base] = self.hold.get(base, 0) + qty
        self.orders[oid] = o
        return {"success": True, "success_response": {"order_id": oid}}

    def tick(self):
        """Fill resting stops whose stop price the bid has crossed (at the stop price)."""
        for o in self.orders.values():
            if o["status"] != "OPEN" or "stop_limit_stop_limit_gtc" not in o["order_configuration"]:
                continue
            c = o["order_configuration"]["stop_limit_stop_limit_gtc"]
            pid, base = o["product_id"], o["product_id"][:-4]
            if self._px(pid) <= float(c["stop_price"]):
                qty, px = float(c["base_size"]), float(c["stop_price"])
                gross, fee = qty * px, qty * px * self.fee
                self.hold[base] -= qty
                self.bal[base] -= qty
                self.bal["USD"] = self.bal.get("USD", 0) + gross - fee
                o.update(status="FILLED", filled_size=str(qty), average_filled_price=str(px), total_fees=str(fee), filled_value=str(gross))

    def cancel(self, ids):
        res = []
        for i in ids:
            o = self.orders.get(i)
            if o and o["status"] == "OPEN":
                o["status"] = "CANCELLED"
                c = o["order_configuration"].get("stop_limit_stop_limit_gtc")
                if c:
                    self.hold[o["product_id"][:-4]] -= float(c["base_size"])
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
    # --- the book, against the fake exchange: adopt -> trail -> parked stop fills -> signal -> buy -> re-park -> backstop sell
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
    assert pos["stop"]["order_id"] and abs(pos["stop"]["stop_px"] - 9.6) < 1e-9, pos["stop"]
    assert abs(st["start_usd"] - 3.45) < 1e-6, st["start_usd"]
    assert len(ex.open_orders("FLAT-USD")) == 1
    cb.bids["FLAT-USD"] = 10.5                                                  # new high: stop re-parked higher
    cycle(ex, cb, out, st, False, t + timedelta(minutes=5))
    assert abs(st["pos"]["stop"]["stop_px"] - 10.08) < 1e-9 and len(ex.open_orders("FLAT-USD")) == 1, st["pos"]["stop"]
    cb.bids["FLAT-USD"] = 10.0
    ex.tick()                                                                   # the exchange fills the parked stop while we sleep
    cycle(ex, cb, out, st, False, t + timedelta(minutes=10))
    assert st["pos"] is None and st["hops"] == 1, st
    tr = paper.read_jsonl(out / "live_trades.jsonl")
    assert tr[-1]["ev"] == "sell" and tr[-1]["reason"] == "stop" and abs(tr[-1]["px"] - 10.08) < 1e-9, tr[-1]
    usd = ex.bal["USD"]
    assert abs(usd - 0.345 * 10.08 * (1 - paper.TAKER_FEE)) < 1e-9, usd
    t2 = datetime.fromtimestamp(cb.t0 + CANDLE_S * 41 + 20, tz=timezone.utc)   # PUMP's signal candle has closed
    cycle(ex, cb, out, st, False, t2)
    pos = st["pos"]
    spent = float(floor_to(usd, "0.01"))                                        # whole bankroll, floored to the cent
    assert pos and pos["pid"] == "PUMP-USD" and pos["stop"]["order_id"] and abs(pos["cost"] - spent) < 1e-9, pos
    assert ex.bal["USD"] < 0.01 and abs(pos["hw"] - 1.10 * 1.001) < 1e-9, (ex.bal, pos["hw"])
    cb.bids["PUMP-USD"] = 1.30
    cycle(ex, cb, out, st, False, t2 + timedelta(minutes=5))
    assert abs(st["pos"]["stop"]["stop_px"] - 1.30 * 0.96) < 1e-9
    cb.bids["PUMP-USD"] = 1.24                                                  # below the stop but the exchange "missed" it: backstop
    cycle(ex, cb, out, st, False, t2 + timedelta(minutes=10))
    assert st["pos"] is None and st["hops"] == 2 and st["wins"] == 1, st          # FLAT hop: +0.8% gross < 0.9% fee
    tr = paper.read_jsonl(out / "live_trades.jsonl")
    assert tr[-1]["reason"] == "trail" and abs(tr[-1]["px"] - 1.24) < 1e-9, tr[-1]
    assert not ex.open_orders("PUMP-USD") and sum(ex.hold.values()) < 1e-12, (ex.orders, ex.hold)
    # --- caps: daily hop cap blocks the next entry; floor halts when flat and tiny
    MAX_HOPS_DAY = 2
    cycle(ex, cb, out, st, False, t2 + timedelta(minutes=15))
    assert st["pos"] is None and st["last"].get("note") == "daily hop cap", st["last"]
    MAX_HOPS_DAY = 6
    ex.bal["USD"] = 0.90
    cycle(ex, cb, out, st, False, t2 + timedelta(minutes=20))
    assert st["halted"] and st["halted"].startswith("floor"), st["halted"]
    # --- dry mode sends nothing
    ex2 = FakeEx(cb, usd=4.0)
    st2 = load_state(Path(tempfile.mkdtemp()) / "mrh")
    cb.bids["PUMP-USD"] = 1.10
    cycle(ex2, cb, Path(tempfile.mkdtemp()), st2, True, t2)
    assert st2["pos"] is None and not ex2.orders and abs(ex2.bal["USD"] - 4.0) < 1e-12
    txt = report(out)
    assert "LIVE" in txt and "HALTED" in txt and "PUMP" in txt
    print("selftest ok:", {"hops": st["hops"], "wins": st["wins"], "usd": round(ex.bal["USD"], 4), "fees": round(st["fees"], 4)})


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
