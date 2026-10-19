"""Polymarket US (gateway.polymarket.us) public-data fetcher for the 15-minute BTC up/down
markets: market list (window, priceToBeat, settlement), 1-minute Yes/No display-price history
per market, and the BRTI reference index (1-minute candles, plus 1-second candles for the
most recent hour). Public endpoints only — no API key. Output is JSON under --out, one file
per kind, merged with what is already there so repeated runs accumulate history.

Docs (read 2026-10-19): docs.polymarket.us/api-reference/markets/get-markets,
.../price-history/get-price-history, .../asset-prices/get-a-bucketed-ohlc-price-series...
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

BASE = "https://gateway.polymarket.us"


DEADLINE = [float("inf")]


def get(client: httpx.Client, path: str, params=None, tries: int = 3):
    for i in range(tries):
        if time.time() > DEADLINE[0]:
            return None
        try:
            r = client.get(BASE + path, params=params, timeout=30)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (404, 400):
                print(f"  {path} {params} -> {r.status_code} {r.text[:200]}", file=sys.stderr)
                return None
            print(f"  {path} -> {r.status_code} {r.text[:120]}, retry", file=sys.stderr)
        except Exception as e:  # network blip
            print(f"  {path} -> {e!r}, retry", file=sys.stderr)
        time.sleep(1.5 * (i + 1))
    return None


def is_btc_15m(m: dict) -> bool:
    t = m.get("assetPriceTerms") or {}
    if t.get("marketType") != "ASSET_PRICE_MARKET_TYPE_UP_DOWN":
        return False
    sym = str(((t.get("asset") or {}).get("symbol")) or "").lower()
    hz = str(t.get("horizon") or "").lower()
    slug = str(m.get("slug") or "").lower()
    return (sym == "btc" or "btc" in slug) and (hz in ("15m", "horizon_15m", "asset_price_horizon_15m") or "15m" in slug)


def slug_for(ts: int) -> str:
    from datetime import datetime, timezone
    d = datetime.fromtimestamp(ts, timezone.utc)
    return f"cpc-btc-updown-15m-{d:%Y-%m-%d-%H%M}z"


def fetch_markets(client: httpx.Client, days: float, known: dict) -> list[dict]:
    """Walk the deterministic slugs (window start, UTC) back `days`; 404 = never listed."""
    now = int(time.time())
    t = now - (now % 900)
    out = []
    misses = 0
    while t > now - days * 86400 and time.time() < DEADLINE[0]:
        slug = slug_for(t)
        t -= 900
        if slug in known and (known[slug].get("assetPriceTerms") or {}).get("settlementPrice"):
            continue  # resolved and stored
        j = get(client, f"/v1/market/slug/{slug}")
        m = (j or {}).get("market") or j
        if not m or not isinstance(m, dict) or not m.get("slug"):
            misses += 1
            if misses > 12:
                print(f"  12 consecutive unlisted windows before {slug}; stopping", file=sys.stderr)
                break
            continue
        misses = 0
        out.append(m)
        time.sleep(0.1)
    print(f"  slug walk: {len(out)} markets fetched", file=sys.stderr)
    return out


def window(m: dict) -> tuple[float | None, float | None]:
    t = m.get("assetPriceTerms") or {}
    from datetime import datetime

    def p(v):
        if not v:
            return None
        try:
            return datetime.fromisoformat(str(v).replace("Z", "+00:00")).timestamp()
        except ValueError:
            return None
    return p(t.get("windowStart")), p(t.get("windowEnd"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/polyus")
    ap.add_argument("--days", type=float, default=14.0, help="BRTI 1-minute history to backfill (<= 60 h per call)")
    ap.add_argument("--max-history", type=int, default=3000, help="max markets to pull price history for per run")
    ap.add_argument("--budget-min", type=float, default=35.0, help="stop issuing requests after this many minutes")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    client = httpx.Client(headers={"User-Agent": "predictionbots/0.1 (paper research)"})
    DEADLINE[0] = time.time() + a.budget_min * 60

    # 1. markets
    mk_path = out / "markets.json"
    markets = {m["slug"]: m for m in json.loads(mk_path.read_text())} if mk_path.exists() else {}
    fresh = fetch_markets(client, a.days, markets)
    for m in fresh:
        markets[str(m.get("slug") or m.get("id"))] = m
    mk_path.write_text(json.dumps(list(markets.values())))
    print(f"markets: {len(fresh)} fetched, {len(markets)} total")

    # 2. price history (1-minute Yes/No display prices) per market; skip ones already complete
    ph_dir = out / "price_history"
    ph_dir.mkdir(exist_ok=True)
    now = time.time()
    n = 0
    for slug, m in sorted(markets.items(), key=lambda kv: (window(kv[1])[0] or 0), reverse=True):
        ws, we = window(m)
        if ws is None or we is None:
            continue
        f = ph_dir / f"{slug}.json"
        if f.exists() and we < now - 120:
            continue  # closed and already stored
        if n >= a.max_history or time.time() > DEADLINE[0]:
            break
        if n and n % 50 == 0:
            print(f"  price history: {n} so far", file=sys.stderr)
        j = get(client, "/v1/price-history", {"symbol": slug, "timestamp.startTimestamp": int(ws) - 120,
                                              "timestamp.endTimestamp": int(min(we + 60, now)), "fidelity": 1})
        if j is not None:
            f.write_text(json.dumps({"slug": slug, "windowStart": ws, "windowEnd": we,
                                     "priceToBeat": (m.get("assetPriceTerms") or {}).get("priceToBeat"),
                                     "settlementPrice": (m.get("assetPriceTerms") or {}).get("settlementPrice"),
                                     "feeCoefficient": m.get("feeCoefficient"), "history": j.get("history") or []}))
            n += 1
        time.sleep(0.15)
    print(f"price history: {n} markets fetched")

    # 3. BRTI candles: 1-minute, backfilled in <= 60 h chunks; 1-second for the last hour
    br_path = out / "brti_1m.json"
    cand = {c["timestamp"]: c for c in json.loads(br_path.read_text())} if br_path.exists() else {}
    start = int(now - a.days * 86400)
    if cand:
        start = max(start, max(cand) - 3600)
    t0 = start
    while t0 < int(now) - 60 and time.time() < DEADLINE[0]:
        t1 = min(int(now), t0 + 3600 * 60)
        if t1 <= t0:
            break
        j = get(client, "/v1/asset-prices/history", [("assets", "crypto:btc"), ("from", t0), ("to", t1),
                                                     ("bucket", "ASSET_PRICE_BUCKET_1M")])
        for s in (j or {}).get("series") or []:
            for c in s.get("candles") or []:
                if c.get("tickCount", 1) != 0:
                    cand[int(c["timestamp"])] = c
        t0 = max(t1, t0 + 60)
        time.sleep(0.2)
    br_path.write_text(json.dumps([cand[k] for k in sorted(cand)]))
    print(f"BRTI 1m candles: {len(cand)}")
    j = get(client, "/v1/asset-prices/history", [("assets", "crypto:btc"), ("from", int(now - 3600)),
                                                 ("bucket", "ASSET_PRICE_BUCKET_1S")])
    sec_dir = out / "brti_1s"
    sec_dir.mkdir(exist_ok=True)
    for s in (j or {}).get("series") or []:
        cs = [c for c in s.get("candles") or [] if c.get("tickCount", 1) != 0]
        if cs:
            (sec_dir / f"{int(cs[0]['timestamp'])}.json").write_text(json.dumps(cs))
            print(f"BRTI 1s candles: {len(cs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
