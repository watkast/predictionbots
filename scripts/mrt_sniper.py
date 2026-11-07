#!/usr/bin/env python3
"""Mr. T — the terminal sniper. Polymarket US crypto Up/Down markets, the final seconds. REAL MONEY, tiny, hard-capped.

The idea (from Mr. P's recorder, mrp/windows.csv, Nov 4–7): these markets settle on the simple average of the 60 one-second
CF Benchmarks index prints before the close, so with a few seconds left the outcome is all but decided — yet the winning side
is still offered below $1 in ~4% of windows (median ask 86¢, 10–1,200 contracts), because the crowd quotes off spot while
the running average has already locked. Every one of the 7 historical flips needed the remaining prints to move the index
by < 1.5 bps; with a 5-bps margin there were 170 qualifying moments in 3.9 days, zero flips, +25% per trade. Whether those
asks are *hittable* is the question only a live order can answer. This bot asks it, 5–10 contracts at a time.

Rule, every 100 ms for each live market in its last MRT_SNIPE_T seconds:
  prints  k of the 60 settlement seconds are known (k >= MRT_MIN_PRINTS); sum_done, last print
  leader  UP if (sum_done + last * (60 - k)) / 60 >= price-to-beat else DOWN (ties go UP, per the rules)
  margin  the remaining prints would have to AVERAGE |need_rem_avg - last| >= MRT_MIN_MOVE_BPS of the index to flip it
          (the 1-second move's p99.9 is 4–6 bps on every coin recorded)
  price   the leader is offered at <= MRT_MAX_ASK with >= MRT_MIN_QTY contracts on the live WebSocket book
  fire    ONE immediate-or-cancel limit buy at that ask for min(MRT_MAX_QTY, cash / ask, offered) contracts; one retry if
          nothing filled and it still qualifies with > 0.8 s left. Fees here are the exchange's 0.0695·p·(1−p): ~0.3% at 95¢.
Settlement is read back from the exchange; every attempt, fill, miss and result is logged. Halts after MRT_HALT_LOSSES
losses in a row (a flip at these margins means the index or the leader logic is wrong, not bad luck) and at
MRT_MAX_TRADES_DAY trades per UTC day.

    python scripts/mrt_sniper.py run --out data/mrt --minutes 335 [--dry]     # --dry: feeds, gate and "would fire" only
    python scripts/mrt_sniper.py report --out data/mrt                        # -> data/mrt/MRT.md
    python scripts/mrt_sniper.py selftest                                     # no network, no key

Env: POLYMARKET_KEY_ID / POLYMARKET_SECRET_KEY (orders + market-data WebSocket), KALSHI_KEY_ID / KALSHI_PRIVATE_KEY_PEM
(the index prints: Kalshi pushes every CF Benchmarks index every second). Switch: mrt/LIVE_ON on main (checked each minute).
Files in --out: state.json, live.jsonl (events), trades.jsonl, MRT.md.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

BOT = "mrt"
REPO = os.environ.get("GITHUB_REPOSITORY", "watkast/predictionbots")
COINS = [c.strip().lower() for c in os.environ.get("MRT_COINS", "btc,eth,sol,xrp").split(",") if c.strip()]
HORIZONS = {"5m": 300, "15m": 900}
RTI_TO_SYM = {"BRTI": "btc"} | {f"{c.upper()}USD_RTI": c for c in ("eth", "sol", "xrp", "doge", "bnb", "hype", "near", "zec", "ltc", "link", "ada", "sui")}

SNIPE_T = float(os.environ.get("MRT_SNIPE_T", "5.0"))             # start looking this many seconds before the close
MIN_PRINTS = int(os.environ.get("MRT_MIN_PRINTS", "52"))           # of the 60 settlement prints must be in hand
MIN_MOVE_BPS = float(os.environ.get("MRT_MIN_MOVE_BPS", "6"))      # remaining prints must average this far from the last one to flip it
MAX_ASK = float(os.environ.get("MRT_MAX_ASK", "0.90"))             # never pay more than this for the leader
MIN_QTY = float(os.environ.get("MRT_MIN_QTY", "5"))                # offered contracts at that ask
MAX_QTY = float(os.environ.get("MRT_MAX_QTY", "10"))               # per trade
MAX_TRADES_DAY = int(os.environ.get("MRT_MAX_TRADES_DAY", "60"))
HALT_LOSSES = int(os.environ.get("MRT_HALT_LOSSES", "2"))          # consecutive losses -> halt (the logic is wrong, not unlucky)
FEE = lambda p: 0.0695 * p * (1 - p)                               # Polymarket US taker fee per contract


def now() -> float:
    return time.time()


def iso(t: float | None = None) -> str:
    return datetime.fromtimestamp(t if t is not None else now(), timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def slug_for(sym: str, label: str, start: int) -> str:
    prefix = "cpc" if sym == "btc" else f"cpc{sym}"
    d = datetime.fromtimestamp(start, tz=timezone.utc)
    return f"{prefix}-{sym}-updown-{label}-{d:%Y-%m-%d-%H%M}z"


def amount(v) -> float | None:
    if v is None:
        return None
    if isinstance(v, dict):
        v = v.get("value")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse_ts(v) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v) / 1000.0 if v > 1e11 else float(v)
    if isinstance(v, dict):
        s = v.get("seconds") or v.get("unixSeconds")
        return float(s) if s is not None else None
    s = str(v).strip()
    if s.isdigit():
        return parse_ts(int(s))
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s).timestamp()
    except ValueError:
        return None


# ----------------------------------------------------------------------------------------------- pure logic

def gate(prints: dict[int, float], end: int, ptb: float, book: dict | None, t: float) -> dict:
    """Everything the decision needs, from the prints in hand, the price to beat and the live book."""
    pts = [prints[s] for s in range(end - 60, end) if s in prints]
    k = len(pts)
    last_sec = max((s for s in prints if s < end), default=None)
    last = prints[last_sec] if last_sec is not None else None
    out = {"rem": round(end - t, 3), "k": k, "last": last, "ptb": ptb, "ok": False, "why": ""}
    if k < MIN_PRINTS or last is None or last <= 0 or ptb is None:
        out["why"] = "prints"
        return out
    tot = sum(pts)
    proj = (tot + last * (60 - k)) / 60 if k < 60 else tot / 60
    leader = "UP" if round(proj, 2) >= ptb else "DOWN"
    if k < 60:
        need_rem_avg = (60 * ptb - tot) / (60 - k)
        margin_bps = abs(need_rem_avg - last) / last * 1e4
    else:
        margin_bps = float("inf")                 # all prints in: the close is known
    out.update(leader=leader, proj=round(proj, 4), margin_bps=round(margin_bps, 2))
    if margin_bps < MIN_MOVE_BPS:
        out["why"] = "margin"
        return out
    if not book or t - book.get("at", 0) > 3.0:
        out["why"] = "no book"
        return out
    if leader == "UP":
        ask, qty = book.get("up_ask"), book.get("up_ask_q", 0)
    else:
        ask = (1 - book["up_bid"]) if book.get("up_bid") else None
        qty = book.get("up_bid_q", 0)
    out.update(ask=ask, offered=qty)
    if ask is None or ask <= 0:
        out["why"] = "no ask"
        return out
    if ask > MAX_ASK:
        out["why"] = "price"
        return out
    if qty < MIN_QTY:
        out["why"] = "size"
        return out
    out["ok"] = True
    return out


def order_for(slug: str, leader: str, ask: float, qty: float) -> dict:
    """Buy the leader at `ask` (a leader-side price). A Down share at d is a BUY_SHORT of Up at 1 − d on this exchange."""
    px = ask if leader == "UP" else round(1 - ask, 2)
    return {"marketSlug": slug, "intent": "ORDER_INTENT_BUY_LONG" if leader == "UP" else "ORDER_INTENT_BUY_SHORT",
            "type": "ORDER_TYPE_LIMIT", "price": {"value": f"{px:.2f}", "currency": "USD"}, "quantity": int(qty),
            "tif": "TIME_IN_FORCE_IMMEDIATE_OR_CANCEL", "synchronousExecution": True, "maxBlockTime": "2s"}


def fill_of(order: dict, leader: str) -> dict:
    """Filled contracts, leader-side average price, fee from an order record."""
    q = float(order.get("cumQuantity") or 0)
    px = amount(order.get("avgPx"))
    if px is not None and leader == "DOWN":
        px = round(1 - px, 4)                     # avgPx is in Up terms
    fee = amount(order.get("commissionNotionalTotalCollected")) or (q * FEE(px) if (q and px) else 0.0)
    return {"qty": q, "px": px, "fee": round(fee, 4), "state": order.get("state")}


def pnl(trade: dict, outcome: str) -> float:
    win = outcome == trade["leader"]
    return round(trade["qty"] * (1.0 if win else 0.0) - trade["qty"] * trade["px"] - trade["fee"], 4)


# ----------------------------------------------------------------------------------------------- state & io

def load_state(out: Path) -> dict:
    f = out / "state.json"
    st = json.loads(f.read_text()) if f.exists() else {}
    st.setdefault("started", iso())
    st.setdefault("attempts", 0)
    st.setdefault("fills", 0)
    st.setdefault("trades", 0)
    st.setdefault("wins", 0)
    st.setdefault("losses", 0)
    st.setdefault("pnl", 0.0)
    st.setdefault("fees", 0.0)
    st.setdefault("streak_losses", 0)
    st.setdefault("trades_by_day", {})
    st.setdefault("halted", None)
    st.setdefault("open", {})           # slug -> trade awaiting settlement
    st.setdefault("fired", [])          # slugs already attempted (one shot per market)
    st.setdefault("qualified", 0)       # gate-ok moments seen (dry or live)
    st.setdefault("last", {})
    return st


def save_state(out: Path, st: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "state.json.tmp"
    tmp.write_text(json.dumps(st, indent=1))
    tmp.replace(out / "state.json")


def event(out: Path, kind: str, **kw) -> None:
    rec = {"t": iso(), "ev": kind, **kw}
    out.mkdir(parents=True, exist_ok=True)
    with (out / "live.jsonl").open("a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
    print(f"{rec['t']} {kind} {json.dumps(kw, default=str)[:300]}", flush=True)


def read_jsonl(f: Path) -> list[dict]:
    if not f.exists():
        return []
    return [json.loads(l) for l in f.read_text().splitlines() if l.strip()]


def switch_on(out: Path) -> bool | None:
    import requests
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    try:
        if tok:
            r = requests.get(f"https://api.github.com/repos/{REPO}/contents/mrt/LIVE_ON", params={"ref": "main"},
                             headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"}, timeout=10)
            if r.status_code in (200, 404):
                return r.status_code == 200
        r = requests.get(f"https://raw.githubusercontent.com/{REPO}/main/mrt/LIVE_ON", timeout=10)
        if r.status_code in (200, 404):
            return r.status_code == 200
    except Exception as e:  # noqa
        event(out, "switch_check_error", err=str(e)[:200])
    return None


def kalshi_signer():
    """Kalshi request signer (same scheme as mrp/mrp_recorder.py): RSA-PSS or Ed25519 over timestamp + METHOD + path."""
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa
    key_id = os.environ.get("KALSHI_KEY_ID", "")
    pem = os.environ.get("KALSHI_PRIVATE_KEY_PEM", "")
    path = os.environ.get("KALSHI_PRIVATE_KEY_PATH", "")
    if path:
        pem_b = Path(path).read_bytes()
    elif pem:
        pem_b = pem.replace("\\n", "\n").encode()
    else:
        pem_b = base64.b64decode(os.environ.get("KALSHI_PRIVATE_KEY_B64", "") or "")
    if not key_id or not pem_b:
        raise SystemExit("no KALSHI_KEY_ID / KALSHI_PRIVATE_KEY_PEM — the index feed needs them")
    key = serialization.load_pem_private_key(pem_b, password=None)

    def headers(method: str, path: str) -> dict:
        ts = str(int(now() * 1000))
        msg = (ts + method.upper() + path).encode()
        if isinstance(key, rsa.RSAPrivateKey):
            sig = key.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
        elif isinstance(key, ed25519.Ed25519PrivateKey):
            sig = key.sign(msg)
        else:
            raise RuntimeError("unsupported Kalshi key type")
        return {"KALSHI-ACCESS-KEY": key_id, "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(), "KALSHI-ACCESS-TIMESTAMP": ts}
    return headers


# ----------------------------------------------------------------------------------------------- the bot

class Sniper:
    def __init__(self, out: Path, dry: bool):
        self.out, self.dry = out, dry
        self.st = load_state(out)
        self.prints: dict[str, dict[int, float]] = {}       # sym -> {sec: value}
        self.markets: dict[str, dict] = {}                  # slug -> {sym, hz, start, end, ptb}
        self.books: dict[str, dict] = {}                    # slug -> {up_ask, up_ask_q, up_bid, up_bid_q, at}
        self.cash = None
        self.client = None
        self.stop = asyncio.Event()
        self.attempted: dict[str, int] = {}                 # slug -> attempts this market
        self.log_gate_at: dict[str, float] = {}

    # ---- exchange
    def connect(self):
        from polymarket_us import PolymarketUS
        key, sec = os.environ.get("POLYMARKET_KEY_ID", ""), os.environ.get("POLYMARKET_SECRET_KEY", "")
        if not key or not sec:
            raise SystemExit("no POLYMARKET_KEY_ID / POLYMARKET_SECRET_KEY — nothing to do")
        self.client = PolymarketUS(key_id=key, secret_key=sec)
        self.refresh_cash()

    def refresh_cash(self):
        try:
            j = self.client.account.balances()
            b = (j.get("balances") or [{}])[0]
            self.cash = amount(b.get("buyingPower"))
            self.st["last"]["cash"] = self.cash
        except Exception as e:  # noqa
            event(self.out, "balance_error", err=str(e)[:200])

    # ---- discovery: the 5- and 15-minute markets of each coin around now, with their price to beat once it exists
    async def discovery_loop(self):
        while not self.stop.is_set():
            t = now()
            want = []
            for sym in COINS:
                for label, hz in HORIZONS.items():
                    base = int(t // hz) * hz
                    for k in (0, 1):
                        want.append((sym, hz, base + k * hz, slug_for(sym, label, base + k * hz)))
            for sym, hz, start, slug in want:
                m = self.markets.get(slug)
                if m and m.get("ptb") is not None:
                    continue
                if t < start - 5:                                  # the price to beat exists only once the window has started
                    self.markets.setdefault(slug, {"sym": sym, "hz": hz, "start": start, "end": start + hz, "ptb": None})
                    continue
                try:
                    j = await asyncio.to_thread(self.client.markets.retrieve_by_slug, slug)
                    mk = j.get("market", j)
                    apt = mk.get("assetPriceTerms") or {}
                    end = int(parse_ts(apt.get("windowEnd")) or (start + hz))
                    self.markets[slug] = {"sym": sym, "hz": hz, "start": int(parse_ts(apt.get("windowStart")) or start), "end": end,
                                          "ptb": amount(apt.get("priceToBeat")), "state": mk.get("state") or mk.get("status")}
                except Exception as e:  # noqa
                    if "404" not in str(e):
                        event(self.out, "market_error", slug=slug, err=str(e)[:200])
                    self.markets.setdefault(slug, {"sym": sym, "hz": hz, "start": start, "end": start + hz, "ptb": None})
                await asyncio.sleep(0.2)
            for slug in [s for s, m in self.markets.items() if m["end"] < t - 1200]:
                self.markets.pop(slug, None)
                self.books.pop(slug, None)
            await asyncio.sleep(10)

    # ---- the index: Kalshi pushes every CF Benchmarks print, once a second
    async def index_loop(self):
        import websockets
        sign = kalshi_signer()
        path = "/trade-api/ws/v2"
        url = os.environ.get("KALSHI_WS_URL", "wss://external-api-ws.kalshi.com/trade-api/ws/v2")
        while not self.stop.is_set():
            try:
                async with websockets.connect(url, additional_headers=sign("GET", path), ping_interval=None, max_size=2 ** 23) as ws:
                    event(self.out, "index_ws", state="connected")
                    await ws.send(json.dumps({"id": 1, "cmd": "subscribe", "params": {"channels": ["cfbenchmarks_value"], "index_ids": ["all"]}}))
                    while not self.stop.is_set():
                        raw = await asyncio.wait_for(ws.recv(), timeout=30)
                        msg = json.loads(raw)
                        if msg.get("type") != "cfbenchmarks_value":
                            continue
                        m = msg.get("msg") or {}
                        d = json.loads(m.get("data") or "{}")
                        idx_id = m.get("index_id") or d.get("id")
                        sym = RTI_TO_SYM.get(idx_id, str(idx_id).lower())
                        if sym not in COINS:
                            continue
                        sec = int(int(d.get("time", 0)) // 1000)
                        v = float(d.get("value"))
                        self.prints.setdefault(sym, {})[sec] = v
                        self.st["last"][f"idx_{sym}"] = [sec, v]
            except Exception as e:  # noqa
                event(self.out, "index_ws_error", err=str(e)[:200])
                await asyncio.sleep(3)
            cut = int(now()) - 3600
            for d in self.prints.values():
                for k in [k for k in d if k < cut]:
                    d.pop(k, None)

    # ---- the book: the exchange's market-data WebSocket for markets closing soon (the gateway caps subscriptions)
    async def book_loop(self):
        while not self.stop.is_set():
            try:
                ws = self.client.ws.markets()

                def on_md(msg):
                    md = msg.get("marketData") or msg.get("marketDataLite") or {}
                    slug = md.get("marketSlug")
                    if not slug:
                        return
                    lv = lambda a: sorted([(amount(e.get("px")), float(e.get("qty") or 0)) for e in (a or []) if amount(e.get("px")) and float(e.get("qty") or 0) > 0])
                    offers, bids = lv(md.get("offers")), lv(md.get("bids"))
                    b = self.books.setdefault(slug, {})
                    b.update(up_ask=offers[0][0] if offers else None, up_ask_q=offers[0][1] if offers else 0,
                             up_bid=bids[-1][0] if bids else None, up_bid_q=bids[-1][1] if bids else 0, at=now())
                ws.on("market_data", on_md)
                ws.on("market_data_lite", on_md)
                ws.on("error", lambda e: event(self.out, "book_ws_error", err=str(e)[:200]))
                await ws.connect()
                event(self.out, "book_ws", state="connected")
                subs: dict[str, str] = {}
                n = 0
                while not self.stop.is_set() and ws.is_connected:
                    t = now()
                    want = sorted([s for s, m in self.markets.items() if m["start"] - 30 <= t < m["end"] and m["end"] - t <= 150],
                                  key=lambda s: self.markets[s]["end"])[:8]
                    for slug in [s for s in subs if s not in want]:
                        rid = subs.pop(slug)
                        try:
                            await ws.unsubscribe(rid)
                        except Exception:
                            pass
                    for slug in [s for s in want if s not in subs]:
                        n += 1
                        rid = f"md-{n}"
                        await ws.subscribe_market_data(rid, [slug])
                        subs[slug] = rid
                    await asyncio.sleep(1.0)
                try:
                    await ws.close()
                except Exception:
                    pass
            except Exception as e:  # noqa
                event(self.out, "book_ws_error", err=str(e)[:200])
                await asyncio.sleep(3)

    # ---- the trigger
    async def gate_loop(self):
        while not self.stop.is_set():
            t = now()
            day = iso(t)[:10]
            for slug, m in list(self.markets.items()):
                rem = m["end"] - t
                if rem <= 0.25 or rem > SNIPE_T or m.get("ptb") is None:
                    continue
                g = gate(self.prints.get(m["sym"], {}), m["end"], m["ptb"], self.books.get(slug), t)
                if t - self.log_gate_at.get(slug, 0) >= 1.0:          # a readable trace of every final second, fired or not
                    self.log_gate_at[slug] = t
                    event(self.out, "gate", slug=slug, **{k: v for k, v in g.items() if k != "ok"}, ok=g["ok"])
                if not g["ok"]:
                    continue
                self.st["qualified"] += 1
                tries = self.attempted.get(slug, 0)
                if self.st["halted"] or slug in self.st["open"] or tries >= 2 or (tries == 1 and rem < 0.8):
                    continue
                if tries == 0 and slug in self.st["fired"]:            # attempted by an earlier run: one shot per market
                    continue
                if self.st["trades_by_day"].get(day, 0) >= MAX_TRADES_DAY:
                    self.st["last"]["note"] = "daily cap"
                    continue
                qty = min(MAX_QTY, g["offered"], int((self.cash or 0) / g["ask"]) if self.cash else MAX_QTY)
                if qty < 1:
                    event(self.out, "skip", slug=slug, reason="no cash", cash=self.cash)
                    continue
                self.attempted[slug] = self.attempted.get(slug, 0) + 1
                if slug not in self.st["fired"]:
                    self.st["fired"].append(slug)
                await self.fire(slug, m, g, int(qty))
                save_state(self.out, self.st)
            await asyncio.sleep(0.1)

    async def fire(self, slug: str, m: dict, g: dict, qty: int):
        o = order_for(slug, g["leader"], g["ask"], qty)
        self.st["attempts"] += 1
        t0 = now()
        if self.dry:
            event(self.out, "would_fire", slug=slug, leader=g["leader"], ask=g["ask"], qty=qty, margin_bps=g["margin_bps"], rem=g["rem"], order=o)
            return
        event(self.out, "fire", slug=slug, leader=g["leader"], ask=g["ask"], qty=qty, margin_bps=g["margin_bps"], rem=g["rem"], k=g["k"])
        try:
            r = await asyncio.to_thread(self.client.orders.create, o)
        except Exception as e:  # noqa
            event(self.out, "order_error", slug=slug, err=str(e)[:400], ms=round((now() - t0) * 1000))
            return
        execs = r.get("executions") or []
        order = (execs[-1].get("order") if execs and isinstance(execs[-1], dict) else None) or r.get("order") or {}
        oid = r.get("id") or order.get("id")
        if not order.get("cumQuantity") and oid:
            for _ in range(3):                                   # the synchronous reply may omit fills: read the order back
                try:
                    order = (await asyncio.to_thread(self.client.orders.retrieve, oid)).get("order") or {}
                    if order.get("state") in ("ORDER_STATE_FILLED", "ORDER_STATE_CANCELED", "ORDER_STATE_REJECTED", "ORDER_STATE_EXPIRED", "ORDER_STATE_PARTIALLY_FILLED"):
                        break
                except Exception as e:  # noqa
                    event(self.out, "order_read_error", slug=slug, err=str(e)[:200])
                await asyncio.sleep(0.4)
        f = fill_of(order, g["leader"])
        event(self.out, "order_result", slug=slug, order_id=oid, ms=round((now() - t0) * 1000), **f, raw=json.dumps(r, default=str)[:600])
        if f["qty"] <= 0:
            event(self.out, "miss", slug=slug, ask=g["ask"], state=f["state"], note="IOC filled nothing: the ask was not there for us")
            return
        self.st["fills"] += 1
        trade = {"t": iso(), "slug": slug, "sym": m["sym"], "hz": m["hz"], "leader": g["leader"], "ask": g["ask"], "qty": f["qty"], "px": f["px"] or g["ask"],
                 "fee": f["fee"], "margin_bps": g["margin_bps"], "rem": g["rem"], "k": g["k"], "order_id": oid, "ptb": m["ptb"], "end": m["end"]}
        self.st["open"][slug] = trade
        self.refresh_cash()
        event(self.out, "filled", slug=slug, qty=f["qty"], px=f["px"], fee=f["fee"], cash=self.cash)

    # ---- settlements
    async def settle_loop(self):
        while not self.stop.is_set():
            t = now()
            for slug, tr in list(self.st["open"].items()):
                if t < tr["end"] + 3:
                    continue
                outcome = None
                try:
                    j = await asyncio.to_thread(self.client.markets.retrieve_by_slug, slug)
                    mk = j.get("market", j)
                    sp = amount((mk.get("assetPriceTerms") or {}).get("settlementPrice"))
                    if sp is not None and tr.get("ptb") is not None:
                        outcome = "UP" if sp >= tr["ptb"] else "DOWN"
                        tr["settlement"] = sp
                except Exception as e:  # noqa
                    event(self.out, "settle_error", slug=slug, err=str(e)[:200])
                if outcome is None and t > tr["end"] + 90:           # fall back to our own prints
                    pts = [self.prints.get(tr["sym"], {}).get(s) for s in range(tr["end"] - 60, tr["end"])]
                    pts = [p for p in pts if p is not None]
                    if len(pts) >= 55:
                        outcome = "UP" if round(sum(pts) / len(pts), 2) >= tr["ptb"] else "DOWN"
                        tr["settlement"] = round(sum(pts) / len(pts), 2)
                        tr["settlement_src"] = "own prints"
                if outcome is None:
                    if t > tr["end"] + 1800:
                        event(self.out, "settle_unknown", slug=slug)
                        self.st["open"].pop(slug, None)
                    continue
                p = pnl(tr, outcome)
                tr.update(outcome=outcome, pnl=p, settled=iso())
                self.st["open"].pop(slug, None)
                self.st["trades"] += 1
                self.st["pnl"] = round(self.st["pnl"] + p, 4)
                self.st["fees"] = round(self.st["fees"] + tr["fee"], 4)
                day = iso(t)[:10]
                self.st["trades_by_day"][day] = self.st["trades_by_day"].get(day, 0) + 1
                if p > 0:
                    self.st["wins"] += 1
                    self.st["streak_losses"] = 0
                else:
                    self.st["losses"] += 1
                    self.st["streak_losses"] += 1
                    if self.st["streak_losses"] >= HALT_LOSSES:
                        self.st["halted"] = f"{self.st['streak_losses']} losses in a row at {iso()} — the leader logic or the index is wrong; investigate"
                        event(self.out, "halted", reason=self.st["halted"])
                with (self.out / "trades.jsonl").open("a") as fh:
                    fh.write(json.dumps(tr) + "\n")
                event(self.out, "settled", slug=slug, outcome=outcome, leader=tr["leader"], pnl=p, pnl_total=self.st["pnl"])
                save_state(self.out, self.st)
            await asyncio.sleep(5)

    async def housekeeping(self, minutes: float):
        t_end = now() + minutes * 60
        last_switch = 0.0
        while not self.stop.is_set():
            t = now()
            if t > t_end and not self.st["open"]:
                event(self.out, "run_end", minutes=minutes)
                self.stop.set()
                break
            if t - last_switch >= 60 and not self.dry:                 # a dry run needs no switch: it sends nothing
                last_switch = t
                on = switch_on(self.out)
                if on is False:
                    event(self.out, "switch_off", note="mrt/LIVE_ON missing on main — stopping")
                    self.stop.set()
                    break
            self.st["last"].update(t=iso(), markets=len(self.markets), books=len(self.books),
                                   prints={s: len(d) for s, d in self.prints.items()}, cash=self.cash)
            save_state(self.out, self.st)
            report(self.out)
            await asyncio.sleep(10)

    async def main(self, minutes: float):
        self.connect()
        event(self.out, "start", mode="dry" if self.dry else "live", cash=self.cash, snipe_t=SNIPE_T, min_move_bps=MIN_MOVE_BPS, max_ask=MAX_ASK,
              max_qty=MAX_QTY, min_prints=MIN_PRINTS, coins=COINS)
        tasks = [asyncio.create_task(c) for c in (self.discovery_loop(), self.index_loop(), self.book_loop(), self.gate_loop(),
                                                   self.settle_loop(), self.housekeeping(minutes))]
        await self.stop.wait()
        for task in tasks:
            task.cancel()
        save_state(self.out, self.st)
        report(self.out)


# ----------------------------------------------------------------------------------------------- report

def report(out: Path) -> str:
    st = load_state(out)
    trades = read_jsonl(out / "trades.jsonl")
    events = read_jsonl(out / "live.jsonl")
    L = ["# Mr. T — terminal sniper, LIVE (Polymarket US, real money, tiny)\n",
         f"Updated {iso()} · started {st['started']} · gate: last {SNIPE_T:g} s, ≥{MIN_PRINTS} of 60 prints, flip needs ≥{MIN_MOVE_BPS:g} bps/s, "
         f"leader ask ≤ {MAX_ASK:.2f}, ≥{MIN_QTY:g} offered, {MAX_QTY:g} contracts max · coins {','.join(COINS)} · 5m + 15m\n"]
    if st.get("halted"):
        L.append(f"**HALTED: {st['halted']}**\n")
    L.append("## Scoreboard\n")
    L.append("| qualifying moments | attempts | fills | fill rate | settled | wins | losses | P&L | fees | cash |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    fr = f"{st['fills']/st['attempts']*100:.0f}%" if st["attempts"] else "—"
    L.append(f"| {st['qualified']} | {st['attempts']} | {st['fills']} | {fr} | {st['trades']} | {st['wins']} | {st['losses']} | ${st['pnl']:+.2f} | ${st['fees']:.3f} | "
             f"{'$%.2f' % st['last']['cash'] if st.get('last', {}).get('cash') is not None else '—'} |")
    L.append("")
    L.append("**Read it like this:** fill rate is the whole experiment — the data said the asks exist; only fills say they were real. "
             "A loss at these margins is a logic error, not variance.\n")
    L.append("## Trades\n")
    L.append("| time (UTC) | market | side | ask | filled | px | fee | margin bps | s left | outcome | P&L |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for x in trades[-40:]:
        L.append(f"| {x['t'][5:19]} | {x['slug'].split('-updown-')[0].replace('cpc','').strip('-') or 'btc'} {x['hz']//60}m {x['slug'][-6:]} | {x['leader']} | {x['ask']:.2f} | "
                 f"{x['qty']:g} | {x['px']:.3f} | ${x['fee']:.3f} | {x['margin_bps']:.1f} | {x['rem']:.1f} | {x.get('outcome','?')} | ${x.get('pnl', 0):+.2f} |")
    for slug, x in st.get("open", {}).items():
        L.append(f"| {x['t'][5:19]} | {slug[-20:]} | {x['leader']} | {x['ask']:.2f} | {x['qty']:g} | {x['px']:.3f} | ${x['fee']:.3f} | {x['margin_bps']:.1f} | {x['rem']:.1f} | (settling) | |")
    L.append("")
    fires = [e for e in events if e["ev"] in ("fire", "would_fire", "miss", "filled", "order_error", "order_result")][-30:]
    L.append("## Last 30 attempts / results\n")
    for e in fires:
        L.append(f"- `{e['t'][5:23]}` **{e['ev']}** " + ", ".join(f"{k}={json.dumps(v, default=str)[:70]}" for k, v in e.items() if k not in ("t", "ev", "raw", "order")))
    L.append("")
    gates = [e for e in events if e["ev"] == "gate"][-40:]
    L.append("## Last 40 gate readings (one per second per market in its final seconds)\n")
    L.append("| time | market | s left | prints | leader | margin bps | ask | offered | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for e in gates:
        L.append(f"| {e['t'][11:23]} | {e['slug'][-24:]} | {e.get('rem')} | {e.get('k')} | {e.get('leader','')} | {e.get('margin_bps','')} | {e.get('ask','')} | {e.get('offered','')} | "
                 f"{'FIRE' if e.get('ok') else e.get('why')} |")
    L.append("")
    L.append("Where this came from: Mr. P's recorder, `mrp/windows.csv` and `mrp/REPORT.md` on this branch.\n")
    txt = "\n".join(L) + "\n"
    (out / "MRT.md").write_text(txt)
    return txt


# ----------------------------------------------------------------------------------------------- selftest

def selftest() -> None:
    import tempfile
    end = 1_800_000_600
    ptb = 100.00
    # 57 prints in, all at 100.20: the average is locked above the price to beat; the remaining 3 would have to average far below
    prints = {s: 100.20 for s in range(end - 60, end - 3)}
    book = {"up_ask": 0.85, "up_ask_q": 40, "up_bid": 0.80, "up_bid_q": 10, "at": end - 3.0}
    g = gate(prints, end, ptb, book, end - 3.0)
    need = (60 * ptb - 57 * 100.20) / 3                      # what the 3 remaining prints must average to tie
    assert g["leader"] == "UP" and g["ok"] and g["ask"] == 0.85 and g["offered"] == 40, g
    assert abs(g["margin_bps"] - abs(need - 100.20) / 100.20 * 1e4) < 0.01 and g["margin_bps"] > 300, g
    # the same tape but the leader is DOWN: the ask is 1 − up bid, the order is a BUY_SHORT at the up bid
    prints_d = {s: 99.80 for s in range(end - 60, end - 3)}
    g2 = gate(prints_d, end, ptb, book, end - 3.0)
    assert g2["leader"] == "DOWN" and g2["ok"] and abs(g2["ask"] - 0.20) < 1e-9 and g2["offered"] == 10, g2
    o = order_for("cpc-btc-updown-5m-x", "DOWN", g2["ask"], 10)
    assert o["intent"] == "ORDER_INTENT_BUY_SHORT" and o["price"]["value"] == "0.80" and o["tif"] == "TIME_IN_FORCE_IMMEDIATE_OR_CANCEL" and o["quantity"] == 10
    o2 = order_for("cpc-btc-updown-5m-x", "UP", 0.85, 7)
    assert o2["intent"] == "ORDER_INTENT_BUY_LONG" and o2["price"]["value"] == "0.85" and o2["quantity"] == 7
    # too close to call: 57 prints at 100.004, remaining need ~99.92 — 8 bps/s away — passes at 6, fails at 10
    global MIN_MOVE_BPS
    prints_c = {s: 100.004 for s in range(end - 60, end - 3)}
    g3 = gate(prints_c, end, ptb, book, end - 3.0)
    assert g3["leader"] == "UP" and 7 < g3["margin_bps"] < 9, g3
    assert g3["ok"]
    MIN_MOVE_BPS = 10
    assert not gate(prints_c, end, ptb, book, end - 3.0)["ok"] and gate(prints_c, end, ptb, book, end - 3.0)["why"] == "margin"
    MIN_MOVE_BPS = 6
    # gate refusals: too few prints, stale book, price, size
    assert gate({s: 100.2 for s in range(end - 60, end - 20)}, end, ptb, book, end - 3.0)["why"] == "prints"
    assert gate(prints, end, ptb, {**book, "at": end - 10}, end - 3.0)["why"] == "no book"
    assert gate(prints, end, ptb, {**book, "up_ask": 0.95}, end - 3.0)["why"] == "price"
    assert gate(prints, end, ptb, {**book, "up_ask_q": 2}, end - 3.0)["why"] == "size"
    # all 60 prints in: the close is known, margin infinite
    assert gate({s: 100.2 for s in range(end - 60, end)}, end, ptb, book, end - 0.5)["ok"]
    # fills and P&L: an Up buy at 0.85 ×10 that wins nets 10 − 8.5 − fee; a Down fill reports avgPx in Up terms
    f = fill_of({"cumQuantity": "10", "avgPx": {"value": "0.85"}, "state": "ORDER_STATE_FILLED"}, "UP")
    assert f["qty"] == 10 and f["px"] == 0.85 and abs(f["fee"] - round(10 * FEE(0.85), 4)) < 1e-9, f
    tr = {"leader": "UP", "qty": 10, "px": 0.85, "fee": f["fee"]}
    assert abs(pnl(tr, "UP") - (10 - 8.5 - f["fee"])) < 1e-4 and abs(pnl(tr, "DOWN") - (-8.5 - f["fee"])) < 1e-4
    fd = fill_of({"cumQuantity": "5", "avgPx": {"value": "0.80"}, "commissionNotionalTotalCollected": {"value": "0.0556"}}, "DOWN")
    assert fd["px"] == 0.20 and fd["fee"] == 0.0556, fd
    # report renders from a scratch dir
    out = Path(tempfile.mkdtemp()) / "mrt"
    st = load_state(out)
    st.update(attempts=3, fills=2, trades=2, wins=2, pnl=2.1, qualified=5)
    save_state(out, st)
    (out / "trades.jsonl").write_text(json.dumps({"t": iso(), "slug": "cpc-btc-updown-5m-2026-11-08-0100z", "sym": "btc", "hz": 300, "leader": "UP", "ask": 0.85,
                                                   "qty": 10, "px": 0.85, "fee": 0.09, "margin_bps": 12.3, "rem": 2.9, "k": 57, "outcome": "UP", "pnl": 1.41}) + "\n")
    event(out, "gate", slug="cpc-btc-updown-5m-2026-11-08-0100z", rem=2.9, k=57, leader="UP", margin_bps=12.3, ask=0.85, offered=40, ok=True)
    txt = report(out)
    assert "fill rate" in txt and "| 5 | 3 | 2 | 67% |" in txt and "FIRE" in txt, txt
    print("selftest ok")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--out", default="data/mrt"); r.add_argument("--minutes", type=float, default=335)
    r.add_argument("--dry", action="store_true", help="feeds and gate only; logs would_fire instead of sending orders")
    p = sub.add_parser("report"); p.add_argument("--out", default="data/mrt")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        from pb.errlog import guard
        with guard(BOT, out=Path(a.out)):
            asyncio.run(Sniper(Path(a.out), a.dry).main(a.minutes))
    elif a.cmd == "report":
        print(report(Path(a.out)))
    else:
        selftest()


if __name__ == "__main__":
    main()
