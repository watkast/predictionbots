"""Daily ETF closes and the 3-month T-bill yield for the trend venture.

Runs on GitHub Actions (internet); the sandbox has no network. Everything is
written as parquet under ``data/trend/``:

* ``prices-<SYM>.parquet``: ``date`` (YYYY-MM-DD string), ``close`` (float),
  ``source`` (``stooq`` | ``yfinance``), ``adjusted`` (bool: dividend-adjusted).
* ``fred-DGS3MO.parquet``: ``date``, ``rate`` (annual fraction, e.g. 0.0425).

Sources
-------
* Stooq daily CSV ``https://stooq.com/q/d/l/?s=spy.us&i=d`` (columns
  ``Date,Open,High,Low,Close,Volume``). **Stooq US ETF closes are split-adjusted
  but NOT dividend-adjusted**: for SPY (~1.3 %/yr yield), TLT/IEF (~2-4 %/yr) and
  VNQ (~4 %/yr) that understates total return and, more importantly, biases the
  12-month momentum ranking against high-yield assets. Treated as a fallback.
* yfinance ``Ticker.history(auto_adjust=False)["Adj Close"]`` (Yahoo total-return
  adjusted close) is preferred whenever the package imports (installed in the
  workflow, not a repo dependency). ``adjusted=True`` is recorded per file and
  the backtest report prints which source each symbol came from.
* FRED ``https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS3MO`` (percent,
  ``.`` for holidays) -> cash yield applied to the idle/cash sleeve.

Parsers are pure functions over the CSV text so tests need no network.
"""
from __future__ import annotations

import io
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pandas as pd

log = logging.getLogger("pb.trend.data")

UNIVERSE = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "IEF", "GLD", "DBC", "VNQ"]
CASH_SYMBOLS = ["SHY", "BIL"]
PRICE_COLS = ["date", "close", "source", "adjusted"]
STOOQ_URL = "https://stooq.com/q/d/l/"
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"


def _client(timeout: float = 60.0) -> httpx.Client:
    return httpx.Client(timeout=timeout, headers={"User-Agent": "predictionbots-trend/0.1"}, follow_redirects=True)


# --------------------------------------------------------------------------- parsers (pure)


def parse_stooq_csv(text: str, source: str = "stooq", adjusted: bool = False) -> pd.DataFrame:
    """``Date,Open,High,Low,Close,Volume`` -> price frame. Stooq answers
    ``No data`` (or an HTML page) for unknown symbols; both give an empty frame."""
    if not text or not text.lstrip().startswith("Date"):
        return pd.DataFrame(columns=PRICE_COLS)
    df = pd.read_csv(io.StringIO(text))
    df.columns = [c.strip() for c in df.columns]
    if "Close" not in df.columns or df.empty:
        return pd.DataFrame(columns=PRICE_COLS)
    out = pd.DataFrame({
        "date": pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%Y-%m-%d"),
        "close": pd.to_numeric(df["Close"], errors="coerce"),
    }).dropna()
    out["source"] = source
    out["adjusted"] = adjusted
    return out.sort_values("date").drop_duplicates("date").reset_index(drop=True)[PRICE_COLS]


def parse_fred_csv(text: str) -> pd.DataFrame:
    """``observation_date,DGS3MO`` (older exports: ``DATE``) in percent; ``.`` = missing."""
    if not text or "," not in text:
        return pd.DataFrame(columns=["date", "rate"])
    df = pd.read_csv(io.StringIO(text))
    df.columns = [c.strip() for c in df.columns]
    date_col = "observation_date" if "observation_date" in df.columns else df.columns[0]
    val_col = [c for c in df.columns if c != date_col][0]
    out = pd.DataFrame({
        "date": pd.to_datetime(df[date_col], errors="coerce").dt.strftime("%Y-%m-%d"),
        "rate": pd.to_numeric(df[val_col], errors="coerce") / 100.0,
    }).dropna()
    return out.sort_values("date").drop_duplicates("date").reset_index(drop=True)


# --------------------------------------------------------------------------- downloaders


def stooq_daily(symbol: str, client: httpx.Client | None = None) -> pd.DataFrame:
    own = client is None
    client = client or _client()
    try:
        r = client.get(STOOQ_URL, params={"s": f"{symbol.lower()}.us", "i": "d"})
        r.raise_for_status()
        return parse_stooq_csv(r.text)
    finally:
        if own:
            client.close()


def yfinance_daily(symbol: str) -> pd.DataFrame:
    """Dividend-adjusted closes via yfinance; empty frame if the package is missing."""
    try:
        import yfinance as yf  # type: ignore
    except ImportError:
        return pd.DataFrame(columns=PRICE_COLS)
    hist = yf.Ticker(symbol).history(period="max", auto_adjust=False)
    if hist is None or hist.empty:
        return pd.DataFrame(columns=PRICE_COLS)
    col = "Adj Close" if "Adj Close" in hist.columns else "Close"
    out = pd.DataFrame({
        "date": pd.to_datetime(hist.index).tz_localize(None).strftime("%Y-%m-%d"),
        "close": pd.to_numeric(hist[col].to_numpy(), errors="coerce"),
    }).dropna()
    out["source"] = "yfinance"
    out["adjusted"] = col == "Adj Close"
    return out.sort_values("date").drop_duplicates("date").reset_index(drop=True)[PRICE_COLS]


def fred_series(series_id: str = "DGS3MO", client: httpx.Client | None = None) -> pd.DataFrame:
    own = client is None
    client = client or _client()
    try:
        r = client.get(FRED_URL, params={"id": series_id})
        r.raise_for_status()
        return parse_fred_csv(r.text)
    finally:
        if own:
            client.close()


def fetch_prices(symbol: str, client: httpx.Client | None = None, prefer_yfinance: bool = True) -> pd.DataFrame:
    """yfinance (dividend-adjusted) when importable, else Stooq (split-adjusted only)."""
    if prefer_yfinance:
        try:
            df = yfinance_daily(symbol)
            if len(df) > 100:
                return df
        except Exception as e:  # noqa: BLE001
            log.warning("yfinance %s: %s", symbol, e)
    return stooq_daily(symbol, client)


# --------------------------------------------------------------------------- orchestration


def download_all(cfg: dict, out_dir: Path, client: httpx.Client | None = None,
                 fetch=fetch_prices, fetch_fred=fred_series) -> dict[str, Path]:
    """Download everything configs/trend.yaml asks for. Returns {name: parquet path}.
    ``fetch``/``fetch_fred`` are injectable for tests."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dcfg = cfg.get("data", {})
    symbols = list(dict.fromkeys([*cfg.get("universe", UNIVERSE), *dcfg.get("cash_symbols", CASH_SYMBOLS)]))
    own = client is None
    client = client or _client()
    written: dict[str, Path] = {}
    try:
        for sym in symbols:
            try:
                df = fetch(sym, client, prefer_yfinance=dcfg.get("prefer_yfinance", True))
            except Exception as e:  # noqa: BLE001
                log.error("prices %s: %s", sym, e)
                continue
            if df is None or df.empty:
                log.warning("empty prices: %s", sym)
                continue
            p = out_dir / f"prices-{sym}.parquet"
            if p.exists():
                try:
                    old = pd.read_parquet(p)
                    # a dividend-adjusted series replaces an unadjusted one wholesale
                    # (adjustment factors shift the entire history on every ex-date)
                    if bool(df["adjusted"].iloc[-1]) or not bool(old["adjusted"].iloc[-1]):
                        df = pd.concat([old[~old["date"].isin(df["date"])], df], ignore_index=True)
                    else:
                        df = pd.concat([old, df[~df["date"].isin(old["date"])]], ignore_index=True)
                except Exception as e:  # noqa: BLE001
                    log.warning("could not merge %s: %s", p, e)
            df = df.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
            df.to_parquet(p, index=False)
            written[sym] = p
            log.info("wrote %s (%d rows, %s adjusted=%s)", p, len(df), df["source"].iloc[-1], bool(df["adjusted"].iloc[-1]))
        try:
            fr = fetch_fred(dcfg.get("fred_series", "DGS3MO"), client)
            if fr is not None and not fr.empty:
                p = out_dir / f"fred-{dcfg.get('fred_series', 'DGS3MO')}.parquet"
                fr.to_parquet(p, index=False)
                written["fred"] = p
        except Exception as e:  # noqa: BLE001
            log.error("fred: %s", e)
    finally:
        if own:
            client.close()
    (out_dir / "manifest.json").write_text(json.dumps(
        {"updated_at": datetime.now(timezone.utc).isoformat(), "files": {k: str(v) for k, v in written.items()}}, indent=1))
    return written


# --------------------------------------------------------------------------- loaders


def load_prices(data_dir: Path, symbols: list[str]) -> tuple[pd.DataFrame, dict[str, dict]]:
    """Wide daily close frame (DatetimeIndex x symbols; NaN before a symbol's
    first date) plus per-symbol meta {source, adjusted, first, last}."""
    data_dir = Path(data_dir)
    cols: dict[str, pd.Series] = {}
    meta: dict[str, dict] = {}
    for sym in symbols:
        p = data_dir / f"prices-{sym}.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p).sort_values("date").drop_duplicates("date", keep="last")
        s = pd.Series(df["close"].to_numpy(float), index=pd.to_datetime(df["date"]), name=sym)
        cols[sym] = s
        meta[sym] = {"source": str(df["source"].iloc[-1]), "adjusted": bool(df["adjusted"].iloc[-1]),
                     "first": str(df["date"].iloc[0]), "last": str(df["date"].iloc[-1]), "rows": int(len(df))}
    if not cols:
        return pd.DataFrame(), meta
    wide = pd.concat(cols.values(), axis=1).sort_index()
    return wide, meta


def load_cash_yield(data_dir: Path, series_id: str = "DGS3MO") -> pd.Series | None:
    p = Path(data_dir) / f"fred-{series_id}.parquet"
    if not p.exists():
        return None
    df = pd.read_parquet(p)
    return pd.Series(df["rate"].to_numpy(float), index=pd.to_datetime(df["date"])).sort_index()
