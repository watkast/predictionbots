"""Paper book for the trend venture (no orders, ever).

``scripts/trend_paper.py`` (daily on GitHub Actions, after the US close) calls
:func:`tick`:

1. load ``data/trend/prices-*.parquet`` (refreshed by ``--download``) and the FRED
   cash yield;
2. mark the paper book (``data/trend/paper-book.json``: cash + shares per ETF)
   at the latest close, accruing the T-bill yield on cash since the last tick;
3. compute the strategy's target weights from the latest *month-end* close
   (:func:`pb.trend.backtest.strategy_weights`); if that month-end is newer than
   the book's last rebalance, trade the book to the targets at the latest close
   (this is the backtest's ``exec_lag_days=1`` when the tick runs the next
   evening) paying ``spread_bps + slippage_bps`` on traded notional;
4. append a row to ``data/trend/paper-<strategy>.jsonl`` with NAV, weights,
   targets, drift and the trades (if any).

Everything is deterministic given the parquet files, so a tick can be replayed.
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from pb.trend.backtest import TrendParams, strategy_weights
from pb.trend.data import UNIVERSE, load_cash_yield, load_prices

log = logging.getLogger("pb.trend.paper")


def _read_jsonl(p: Path) -> list[dict]:
    if not Path(p).exists():
        return []
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]


def _append(p: Path, row: dict):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a") as f:
        f.write(json.dumps(row, default=float) + "\n")


def new_book(capital: float, now: float) -> dict:
    return {"cash": float(capital), "shares": {}, "capital": float(capital), "created": now,
            "last_mark_date": None, "last_rebalance_month": None, "costs": 0.0, "rebalances": 0}


def load_book(path: Path, capital: float, now: float) -> dict:
    p = Path(path)
    if p.exists():
        return json.loads(p.read_text())
    return new_book(capital, now)


def save_book(path: Path, book: dict):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(book, indent=1, default=float))


def mark(book: dict, prices: pd.DataFrame, cash_rate: pd.Series | None, as_of: pd.Timestamp) -> tuple[float, dict[str, float]]:
    """Accrue cash since ``last_mark_date`` and value the shares at ``as_of``. Returns (nav, {sym: value})."""
    if book.get("last_mark_date"):
        d0 = pd.Timestamp(book["last_mark_date"])
        days = (as_of - d0).days
        if days > 0:
            r = 0.0
            if cash_rate is not None and not cash_rate.empty:
                r = float(cash_rate.loc[:d0].iloc[-1]) if (cash_rate.index <= d0).any() else float(cash_rate.iloc[0])
            book["cash"] = float(book["cash"]) * (1.0 + r * days / 365.0)
    row = prices.loc[as_of]
    values = {}
    for sym, sh in book.get("shares", {}).items():
        px = row.get(sym)
        if px is None or not np.isfinite(px):
            px = float(book.get("last_px", {}).get(sym, 0.0))
        values[sym] = float(sh) * float(px)
    book["last_mark_date"] = str(as_of.date())
    book["last_px"] = {s: float(row[s]) for s in prices.columns if np.isfinite(row[s])}
    return float(book["cash"]) + sum(values.values()), values


def rebalance(book: dict, target_w: dict[str, float], prices_row: pd.Series, nav: float, params: TrendParams,
              signal_date: str, exec_date: str) -> dict:
    """Trade the book to ``target_w`` at ``prices_row`` closes. Returns the trade log row."""
    trades = []
    cost_bps = params.cost_bps() / 1e4
    total_cost = 0.0
    turnover = 0.0
    new_shares: dict[str, float] = {}
    syms = set(book.get("shares", {})) | {s for s, w in target_w.items() if w > 0}
    # reserve the estimated cost so a fully invested book never goes cash-negative
    est = 0.0
    for sym in syms:
        px = prices_row.get(sym)
        if px is None or not np.isfinite(px) or px <= 0:
            continue
        d = float(target_w.get(sym, 0.0)) * nav - float(book.get("shares", {}).get(sym, 0.0)) * float(px)
        if abs(d) >= params.min_trade_usd:
            est += abs(d) * cost_bps + params.commission_usd
    nav_eff = max(nav - est, 0.0)
    for sym in sorted(syms):
        px = prices_row.get(sym)
        if px is None or not np.isfinite(px) or px <= 0:
            if sym in book.get("shares", {}):
                new_shares[sym] = book["shares"][sym]
            continue
        cur = float(book.get("shares", {}).get(sym, 0.0))
        tgt_val = float(target_w.get(sym, 0.0)) * nav_eff
        tgt_sh = tgt_val / float(px)
        d_val = (tgt_sh - cur) * float(px)
        if abs(d_val) < params.min_trade_usd:   # ignore dust
            if cur:
                new_shares[sym] = cur
            continue
        cost = abs(d_val) * cost_bps + params.commission_usd
        total_cost += cost
        turnover += abs(d_val)
        book["cash"] = float(book["cash"]) - d_val - cost
        if tgt_sh > 1e-9:
            new_shares[sym] = tgt_sh
        trades.append({"sym": sym, "side": "buy" if d_val > 0 else "sell", "shares": tgt_sh - cur,
                       "px": float(px), "notional": abs(d_val), "cost": cost})
    book["shares"] = new_shares
    book["costs"] = float(book.get("costs", 0.0)) + total_cost
    book["rebalances"] = int(book.get("rebalances", 0)) + 1
    book["last_rebalance_month"] = signal_date[:7]
    return {"type": "rebalance", "signal_date": signal_date, "exec_date": exec_date, "trades": trades,
            "turnover": turnover, "turnover_frac": turnover / nav if nav else 0.0, "cost": total_cost}


def tick(cfg: dict, data_dir: Path, now: float | None = None, prices: pd.DataFrame | None = None,
         cash_rate: pd.Series | None = None, force_rebalance: bool = False) -> dict:
    """One paper tick. ``prices``/``cash_rate`` are injectable for tests."""
    now = now or time.time()
    data_dir = Path(data_dir)
    pcfg = cfg.get("paper", {})
    strategy = pcfg.get("strategy", "ensemble")
    params = TrendParams.from_dict({**cfg.get("backtest", {}).get("params", {}), **(pcfg.get("params") or {}),
                                    "capital": pcfg.get("capital", 10_000)})
    universe = list(cfg.get("universe", UNIVERSE))
    meta: dict = {}
    if prices is None:
        prices, meta = load_prices(data_dir, universe)
        cash_rate = load_cash_yield(data_dir, cfg.get("data", {}).get("fred_series", "DGS3MO"))
    ledger = data_dir / f"paper-{strategy}.jsonl"
    book_path = data_dir / "paper-book.json"
    book = load_book(book_path, params.capital, now)
    if prices is None or prices.empty or "SPY" not in prices.columns:
        row = {"ts": now, "type": "tick", "error": f"no price data under {data_dir}"}
        _append(ledger, row)
        return row
    prices = prices[[c for c in universe if c in prices.columns]].dropna(how="all")
    as_of = prices.index[-1]
    stale_days = (datetime.fromtimestamp(now, tz=timezone.utc).date() - as_of.date()).days
    nav, values = mark(book, prices, cash_rate, as_of)
    W = strategy_weights(prices, cash_rate, params, strategy)
    # only completed months count: the signal month-end must be strictly before
    # the month of the latest close (= backtest exec_lag_days=1 when the tick runs daily)
    W = W[W.index.to_period("M") < as_of.to_period("M")]
    if W.empty:
        row = {"ts": now, "type": "tick", "error": "no completed month-end in the price history"}
        _append(ledger, row)
        return row
    signal_date = W.index[-1]
    target = {s: float(w) for s, w in W.loc[signal_date].items() if np.isfinite(w) and w > 0}
    cur_w = {s: v / nav for s, v in values.items() if nav} if nav else {}
    drift = sum(abs(target.get(s, 0.0) - cur_w.get(s, 0.0)) for s in set(target) | set(cur_w))
    reb = None
    sig_month = str(signal_date.date())[:7]
    is_new_month = book.get("last_rebalance_month") != sig_month
    if (is_new_month or force_rebalance) and stale_days <= int(pcfg.get("stale_days", 7)):
        reb = rebalance(book, target, prices.loc[as_of], nav, params, str(signal_date.date()), str(as_of.date()))
        nav, values = mark(book, prices, cash_rate, as_of)
        cur_w = {s: v / nav for s, v in values.items()} if nav else {}
        reb.update({"ts": now, "nav_after": nav})
        _append(ledger, reb)
    save_book(book_path, book)
    row = {"ts": now, "type": "tick", "price_date": str(as_of.date()), "stale_days": stale_days, "nav": nav,
           "cash": float(book["cash"]), "cash_w": float(book["cash"]) / nav if nav else 1.0,
           "weights": {s: round(w, 6) for s, w in cur_w.items() if w > 1e-6},
           "target": {s: round(w, 6) for s, w in target.items()}, "signal_date": str(signal_date.date()),
           "drift": drift, "rebalanced": reb is not None, "pnl": nav - params.capital,
           "costs": float(book.get("costs", 0.0)), "sources": {s: m.get("source") for s, m in meta.items()},
           "adjusted": {s: m.get("adjusted") for s, m in meta.items()}}
    _append(ledger, row)
    return row


def summarize(data_dir: Path) -> dict:
    """Roll the paper ledgers up for reports/trend_paper.md."""
    data_dir = Path(data_dir)
    out = {}
    for p in sorted(data_dir.glob("paper-*.jsonl")):
        rows = _read_jsonl(p)
        name = p.stem[len("paper-"):]
        ticks = [r for r in rows if r.get("type") == "tick" and "nav" in r]
        rebs = [r for r in rows if r.get("type") == "rebalance"]
        navs = [t["nav"] for t in ticks]
        peak = -np.inf
        mdd = 0.0
        for v in navs:
            peak = max(peak, v)
            mdd = min(mdd, v / peak - 1.0)
        out[name] = {"ticks": len(ticks), "rebalances": len(rebs), "first": ticks[0]["price_date"] if ticks else None,
                     "last": ticks[-1]["price_date"] if ticks else None, "nav": navs[-1] if navs else None,
                     "pnl": ticks[-1]["pnl"] if ticks else None, "costs": ticks[-1]["costs"] if ticks else 0.0,
                     "max_drawdown": mdd, "last_weights": ticks[-1]["weights"] if ticks else {},
                     "last_target": ticks[-1]["target"] if ticks else {}, "last_drift": ticks[-1]["drift"] if ticks else None,
                     "stale_days": ticks[-1]["stale_days"] if ticks else None,
                     "sources": ticks[-1].get("sources", {}) if ticks else {}}
    return out
