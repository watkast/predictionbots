"""Downloaders and loaders for funding-rate history and 1h candles.

Runs on GitHub Actions (internet); the sandbox has no network. Everything is
written as parquet under ``data/carry/`` with a uniform schema:

* funding:  ``ts`` (epoch s, interval end), ``rate`` (fraction per interval),
            ``interval_hours``, ``source``, ``asset``
* candles:  ``ts`` (epoch s, bar open), ``open, high, low, close, volume``

Sources (URLs verified 2026-10-17; see pb/carry/venues.py for the full list):

* Binance Vision monthly zips (funding since 2019-09, 8 h; USD-M perp and spot
  1h klines) https://github.com/binance/binance-public-data
  ``https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2024-01.zip``
* Binance live ``GET https://fapi.binance.com/fapi/v1/fundingRate`` (<=1000 rows)
* Bybit ``GET https://api.bybit.com/v5/market/funding/history`` (<=200 rows, page by endTime)
  https://bybit-exchange.github.io/docs/v5/market/history-fund-rate
* OKX ``GET https://www.okx.com/api/v5/public/funding-rate-history`` (<=100 rows, page by ``after``)
* Bitnomial (Kraken Derivatives US perps) ``GET https://bitnomial.com/exchange/api/v1/funding-rates/``
  https://bitnomial.com/exchange/docs/api/rest/funding-rates
* Coinbase public candles ``GET https://api.coinbase.com/api/v3/brokerage/market/products/{id}/candles``
  (unix-second ``start``/``end``, ``granularity=ONE_HOUR``, max 350)
  https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/public/get-public-product-candles
* Coinbase public product (live funding of US perp-style futures)
  ``GET https://api.coinbase.com/api/v3/brokerage/market/products/BIP-20DEC30-CDE``

The historical backtest uses Binance as the *proxy* for US-perp funding: the
US products (Coinbase Jul-2025, Kraken/Bitnomial Jun-2026) have months of
history, not years. The paper tick logs the US venues' live rates so the proxy
error can be measured over time (``reports/carry_backtest.md`` prints it when
``data/carry/funding-live.jsonl`` has enough rows).
"""
from __future__ import annotations

import io
import json
import logging
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pandas as pd

log = logging.getLogger("pb.carry.data")

BINANCE_VISION = "https://data.binance.vision/data"
FUNDING_COLS = ["ts", "rate", "interval_hours", "source", "asset"]
CANDLE_COLS = ["ts", "open", "high", "low", "close", "volume"]

ASSET_SYMBOLS = {
    "binance": {"BTC": "BTCUSDT", "ETH": "ETHUSDT"},
    "bybit": {"BTC": "BTCUSDT", "ETH": "ETHUSDT"},
    "okx": {"BTC": "BTC-USDT-SWAP", "ETH": "ETH-USDT-SWAP"},
    "coinbase_spot": {"BTC": "BTC-USD", "ETH": "ETH-USD"},
    "coinbase_perp": {"BTC": "BIP-20DEC30-CDE", "ETH": None},
    "bitnomial": {"BTC": "BTCUC", "ETH": "ETHUI"},
}


def _client(timeout: float = 60.0) -> httpx.Client:
    return httpx.Client(timeout=timeout, headers={"User-Agent": "predictionbots-carry/0.1"}, follow_redirects=True)


def _norm_epoch_s(v) -> float:
    """Binance timestamps: ms historically, microseconds for spot from 2025-01."""
    v = float(v)
    if v > 1e14:
        return v / 1e6
    if v > 1e11:
        return v / 1e3
    return v


def months_between(start: str, end: str | None = None) -> list[str]:
    """['2023-01', ..., end] inclusive; end defaults to the previous full month."""
    y, m = (int(x) for x in start.split("-"))
    if end is None:
        now = datetime.now(timezone.utc)
        ey, em = now.year, now.month - 1
        if em == 0:
            ey, em = ey - 1, 12
    else:
        ey, em = (int(x) for x in end.split("-"))
    out = []
    while (y, m) <= (ey, em):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


# --------------------------------------------------------------------------- Binance Vision


def _vision_zip_csv(client: httpx.Client, url: str) -> pd.DataFrame | None:
    r = client.get(url)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        name = z.namelist()[0]
        with z.open(name) as f:
            head = f.read(64)
        with z.open(name) as f:
            # klines have no header; fundingRate does
            has_header = not head[:1].isdigit()
            return pd.read_csv(f, header=0 if has_header else None)


def binance_vision_funding(symbol: str, months: list[str], asset: str = "BTC",
                           client: httpx.Client | None = None) -> pd.DataFrame:
    """Monthly ``fundingRate`` zips -> funding frame. Columns in the CSV are
    ``calc_time,funding_interval_hours,last_funding_rate``."""
    own = client is None
    client = client or _client()
    frames = []
    try:
        for ym in months:
            url = f"{BINANCE_VISION}/futures/um/monthly/fundingRate/{symbol}/{symbol}-fundingRate-{ym}.zip"
            df = _vision_zip_csv(client, url)
            if df is None:
                log.info("no funding zip %s", url)
                continue
            df.columns = [c.strip() for c in df.columns]
            frames.append(pd.DataFrame({
                "ts": df["calc_time"].map(_norm_epoch_s),
                "rate": df["last_funding_rate"].astype(float),
                "interval_hours": df.get("funding_interval_hours", 8).astype(float),
            }))
    finally:
        if own:
            client.close()
    if not frames:
        return pd.DataFrame(columns=FUNDING_COLS)
    out = pd.concat(frames, ignore_index=True)
    out["source"] = "binance"
    out["asset"] = asset
    return out.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)[FUNDING_COLS]


def binance_vision_klines(symbol: str, months: list[str], kind: str = "spot", interval: str = "1h",
                          client: httpx.Client | None = None) -> pd.DataFrame:
    """``kind`` is ``spot`` or ``um`` (USD-M perpetual)."""
    own = client is None
    client = client or _client()
    base = f"{BINANCE_VISION}/spot/monthly/klines" if kind == "spot" else f"{BINANCE_VISION}/futures/um/monthly/klines"
    frames = []
    try:
        for ym in months:
            url = f"{base}/{symbol}/{interval}/{symbol}-{interval}-{ym}.zip"
            df = _vision_zip_csv(client, url)
            if df is None:
                log.info("no kline zip %s", url)
                continue
            df = df.iloc[:, :6]
            df.columns = CANDLE_COLS
            df["ts"] = df["ts"].map(_norm_epoch_s)
            frames.append(df.astype(float))
    finally:
        if own:
            client.close()
    if not frames:
        return pd.DataFrame(columns=CANDLE_COLS)
    return pd.concat(frames, ignore_index=True).sort_values("ts").drop_duplicates("ts").reset_index(drop=True)


def binance_live_funding(symbol: str, asset: str = "BTC", limit: int = 1000,
                         client: httpx.Client | None = None) -> pd.DataFrame:
    own = client is None
    client = client or _client()
    try:
        r = client.get("https://fapi.binance.com/fapi/v1/fundingRate", params={"symbol": symbol, "limit": limit})
        r.raise_for_status()
        rows = r.json()
    finally:
        if own:
            client.close()
    return pd.DataFrame({
        "ts": [_norm_epoch_s(x["fundingTime"]) for x in rows],
        "rate": [float(x["fundingRate"]) for x in rows],
        "interval_hours": 8.0, "source": "binance", "asset": asset,
    })[FUNDING_COLS] if rows else pd.DataFrame(columns=FUNDING_COLS)


# --------------------------------------------------------------------------- Bybit / OKX


def bybit_funding_history(symbol: str, asset: str = "BTC", start_ts: float | None = None,
                          client: httpx.Client | None = None, max_pages: int = 200) -> pd.DataFrame:
    own = client is None
    client = client or _client()
    rows: list[dict] = []
    end_ms: int | None = None
    try:
        for _ in range(max_pages):
            params = {"category": "linear", "symbol": symbol, "limit": 200}
            if end_ms:
                params["endTime"] = end_ms
            r = client.get("https://api.bybit.com/v5/market/funding/history", params=params)
            r.raise_for_status()
            lst = r.json().get("result", {}).get("list", [])
            if not lst:
                break
            rows.extend(lst)
            oldest = min(int(x["fundingRateTimestamp"]) for x in lst)
            if start_ts is not None and oldest / 1000 <= start_ts:
                break
            if len(lst) < 200:
                break
            end_ms = oldest - 1
    finally:
        if own:
            client.close()
    if not rows:
        return pd.DataFrame(columns=FUNDING_COLS)
    out = pd.DataFrame({
        "ts": [int(x["fundingRateTimestamp"]) / 1000 for x in rows],
        "rate": [float(x["fundingRate"]) for x in rows],
        "interval_hours": 8.0, "source": "bybit", "asset": asset,
    })
    if start_ts is not None:
        out = out[out.ts >= start_ts]
    return out.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)[FUNDING_COLS]


def okx_funding_history(inst_id: str, asset: str = "BTC", start_ts: float | None = None,
                        client: httpx.Client | None = None, max_pages: int = 300) -> pd.DataFrame:
    own = client is None
    client = client or _client()
    rows: list[dict] = []
    after: str | None = None
    try:
        for _ in range(max_pages):
            params = {"instId": inst_id, "limit": 100}
            if after:
                params["after"] = after
            r = client.get("https://www.okx.com/api/v5/public/funding-rate-history", params=params)
            r.raise_for_status()
            lst = r.json().get("data", [])
            if not lst:
                break
            rows.extend(lst)
            oldest = min(int(x["fundingTime"]) for x in lst)
            if start_ts is not None and oldest / 1000 <= start_ts:
                break
            if len(lst) < 100:
                break
            after = str(oldest)
    finally:
        if own:
            client.close()
    if not rows:
        return pd.DataFrame(columns=FUNDING_COLS)
    out = pd.DataFrame({
        "ts": [int(x["fundingTime"]) / 1000 for x in rows],
        "rate": [float(x["realizedRate"] if x.get("realizedRate") not in (None, "") else x["fundingRate"]) for x in rows],
        "interval_hours": 8.0, "source": "okx", "asset": asset,
    })
    if start_ts is not None:
        out = out[out.ts >= start_ts]
    return out.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)[FUNDING_COLS]


# --------------------------------------------------------------------------- Bitnomial / Coinbase


def bitnomial_funding(base_symbol: str, asset: str = "BTC", begin_iso: str | None = None,
                      client: httpx.Client | None = None, max_pages: int = 100) -> pd.DataFrame:
    """Kraken Derivatives US perps are Bitnomial-listed; funding API is public."""
    own = client is None
    client = client or _client()
    rows: list[dict] = []
    cursor: str | None = None
    try:
        for _ in range(max_pages):
            params = {"base_symbol": base_symbol, "limit": 500, "order": "asc"}
            if begin_iso:
                params["begin_time"] = begin_iso
            if cursor:
                params["cursor"] = cursor
            r = client.get("https://bitnomial.com/exchange/api/v1/funding-rates/", params=params)
            r.raise_for_status()
            body = r.json()
            data = body.get("funding_rates", body.get("data", body)) if isinstance(body, dict) else body
            if not data:
                break
            rows.extend(data)
            cursor = body.get("cursor") if isinstance(body, dict) else None
            if not cursor:
                break
    finally:
        if own:
            client.close()
    if not rows:
        return pd.DataFrame(columns=FUNDING_COLS)
    out = pd.DataFrame({
        "ts": [datetime.fromisoformat(str(x["interval_end"]).replace("Z", "+00:00")).timestamp() for x in rows],
        "rate": [float(x["funding_rate"]) for x in rows],
        "interval_hours": 8.0, "source": "bitnomial", "asset": asset,
    })
    return out.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)[FUNDING_COLS]


def coinbase_candles(product_id: str, start_ts: float, end_ts: float, granularity: str = "ONE_HOUR",
                     client: httpx.Client | None = None, sleep: float = 0.2) -> pd.DataFrame:
    """Public candles, paged 350 at a time (hourly => ~14.5 days per call)."""
    own = client is None
    client = client or _client()
    step = {"ONE_HOUR": 3600, "ONE_DAY": 86400, "FIFTEEN_MINUTE": 900}[granularity] * 350
    frames = []
    try:
        t = int(start_ts)
        while t < end_ts:
            r = client.get(f"https://api.coinbase.com/api/v3/brokerage/market/products/{product_id}/candles",
                           params={"start": str(t), "end": str(min(int(end_ts), t + step)), "granularity": granularity})
            r.raise_for_status()
            c = r.json().get("candles", [])
            if c:
                frames.append(pd.DataFrame([{k: float(x[k]) for k in ("start", "open", "high", "low", "close", "volume")} for x in c])
                              .rename(columns={"start": "ts"}))
            t += step
            time.sleep(sleep)
    finally:
        if own:
            client.close()
    if not frames:
        return pd.DataFrame(columns=CANDLE_COLS)
    return pd.concat(frames, ignore_index=True).sort_values("ts").drop_duplicates("ts").reset_index(drop=True)[CANDLE_COLS]


def coinbase_public_product(product_id: str, client: httpx.Client | None = None) -> dict:
    own = client is None
    client = client or _client()
    try:
        r = client.get(f"https://api.coinbase.com/api/v3/brokerage/market/products/{product_id}")
        r.raise_for_status()
        return r.json()
    finally:
        if own:
            client.close()


def coinbase_find_perp_products(client: httpx.Client | None = None) -> dict[str, str]:
    """Discover US perp-style product ids (``*-CDE`` with a funding_rate) -> {'BTC': id, 'ETH': id}."""
    own = client is None
    client = client or _client()
    try:
        r = client.get("https://api.coinbase.com/api/v3/brokerage/market/products", params={"product_type": "FUTURE"})
        r.raise_for_status()
        prods = r.json().get("products", [])
    finally:
        if own:
            client.close()
    return parse_coinbase_perp_products(prods)


def parse_coinbase_perp_products(prods: list[dict]) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in prods:
        pid = p.get("product_id", "")
        fpd = p.get("future_product_details") or {}
        name = (p.get("display_name") or "") + " " + (fpd.get("contract_display_name") or "")
        is_perp = fpd.get("contract_expiry_type") == "PERPETUAL" or bool(fpd.get("funding_rate")) or "perp" in name.lower()
        if not (pid.endswith("-CDE") and is_perp):
            continue
        base = (p.get("base_currency_id") or p.get("base_display_symbol") or "").upper()
        if pid.startswith("BIP-") or base == "BTC" or "bitcoin" in name.lower():
            out.setdefault("BTC", pid)
        elif pid.startswith("ETP-") or base == "ETH" or "ether" in name.lower():
            out.setdefault("ETH", pid)
    return out


# --------------------------------------------------------------------------- orchestration


def download_all(cfg: dict, out_dir: Path, client: httpx.Client | None = None) -> dict[str, Path]:
    """Download everything configs/carry.yaml asks for. Returns {name: parquet path}."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data_cfg = cfg.get("data", {})
    start = data_cfg.get("start_month", "2020-01")
    assets = [a.upper() for a in cfg.get("assets", ["BTC", "ETH"])]
    months = months_between(start)
    own = client is None
    client = client or _client()
    written: dict[str, Path] = {}

    def _save(name: str, df: pd.DataFrame):
        if df is None or df.empty:
            log.warning("empty: %s", name)
            return
        p = out_dir / f"{name}.parquet"
        if p.exists():
            try:
                old = pd.read_parquet(p)
                df = pd.concat([old, df], ignore_index=True).sort_values("ts").drop_duplicates("ts", keep="last")
            except Exception as e:  # noqa: BLE001
                log.warning("could not merge %s: %s", p, e)
        df.reset_index(drop=True).to_parquet(p, index=False)
        written[name] = p
        log.info("wrote %s (%d rows)", p, len(df))

    try:
        for a in assets:
            sym = ASSET_SYMBOLS["binance"][a]
            frames = []
            try:
                frames.append(binance_vision_funding(sym, months, a, client))
            except Exception as e:  # noqa: BLE001
                log.error("binance vision funding %s: %s", a, e)
            try:
                # fapi.binance.com answers HTTP 451 from US IPs (GitHub runners);
                # the Vision archive still works, so never let the live call
                # discard the history.
                frames.append(binance_live_funding(sym, a, client=client))
            except Exception as e:  # noqa: BLE001
                log.warning("binance live funding %s (expected from US IPs): %s", a, e)
            if frames:
                _save(f"funding-binance-{a}", pd.concat(frames, ignore_index=True)
                      .sort_values("ts").drop_duplicates("ts").reset_index(drop=True))
            for kind in ("spot", "um"):
                try:
                    _save(f"candles-binance-{kind}-{a}", binance_vision_klines(sym, months, kind, "1h", client))
                except Exception as e:  # noqa: BLE001
                    log.error("binance %s klines %s: %s", kind, a, e)
            if data_cfg.get("bybit", True):
                try:
                    _save(f"funding-bybit-{a}", bybit_funding_history(ASSET_SYMBOLS["bybit"][a], a, client=client))
                except Exception as e:  # noqa: BLE001
                    log.error("bybit %s: %s", a, e)
            if data_cfg.get("okx", True):
                try:
                    _save(f"funding-okx-{a}", okx_funding_history(ASSET_SYMBOLS["okx"][a], a, client=client))
                except Exception as e:  # noqa: BLE001
                    log.error("okx %s: %s", a, e)
            if data_cfg.get("bitnomial", True):
                try:
                    _save(f"funding-bitnomial-{a}", bitnomial_funding(ASSET_SYMBOLS["bitnomial"][a], a, client=client))
                except Exception as e:  # noqa: BLE001
                    log.error("bitnomial %s: %s", a, e)
            if data_cfg.get("coinbase_candles", True):
                days = float(data_cfg.get("coinbase_candle_days", 120))
                now = time.time()
                try:
                    _save(f"candles-coinbase-spot-{a}",
                          coinbase_candles(ASSET_SYMBOLS["coinbase_spot"][a], now - days * 86400, now, client=client))
                except Exception as e:  # noqa: BLE001
                    log.error("coinbase spot candles %s: %s", a, e)
                pid = ASSET_SYMBOLS["coinbase_perp"].get(a)
                if pid is None:
                    try:
                        pid = coinbase_find_perp_products(client).get(a)
                    except Exception as e:  # noqa: BLE001
                        log.error("coinbase product discovery: %s", e)
                if pid:
                    try:
                        _save(f"candles-coinbase-perp-{a}", coinbase_candles(pid, now - days * 86400, now, client=client))
                    except Exception as e:  # noqa: BLE001
                        log.error("coinbase perp candles %s: %s", a, e)
    finally:
        if own:
            client.close()
    (out_dir / "manifest.json").write_text(json.dumps(
        {"updated_at": datetime.now(timezone.utc).isoformat(), "files": {k: str(v) for k, v in written.items()}}, indent=1))
    return written


def load_funding(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    return df.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)


def load_candles(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    return df.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
