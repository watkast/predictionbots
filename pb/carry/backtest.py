"""Realistic funding-rate carry backtest (long spot + short perp).

Model (one step per funding interval):

* **Signal** = trailing ``lookback``-interval mean of the *annualized* funding
  rate. Enter when signal > ``entry_ann``; exit when signal < ``exit_ann`` or
  the latest interval's funding print is negative (after ``min_hold``).
  Signal at interval *i* uses rates up to and including *i*; the trade happens
  at the candle close of *i*; funding is earned from interval *i+1* on.
* **Sizing**: hedged notional ``N = capital * notional_frac`` with
  ``notional_frac`` defaulting to ``1 / (1 + perp_collateral_frac)`` so that
  spot (N) plus perp collateral (N * perp_collateral_frac, default 50 % => 2x on
  the perp side) exactly uses the capital. Everything not deployed earns
  ``tbill_rate``; perp collateral earns ``collateral_yield`` (default 0: USD at
  an FCM earns nothing).
* **Costs**: per leg, per side: ``LegFees.cost`` (bps on notional + per-contract
  USD) plus ``slippage_bps`` for taker legs. Maker legs pay the maker bps and
  no slippage (optimistic: assumes the resting order filled).
* **Basis P&L**: the hedge is in dollar notional, so the position's mark is
  ``N * (spot_t/spot_entry - perp_t/perp_entry)``: perp premium widening
  *against* a short perp is a loss until exit. Realized on exit.
* **Liquidation**: the short perp is liquidated if the perp's intra-interval
  high rises ``liq_distance`` above entry, where
  ``liq_distance = collateral_frac (+ idle_cash/N if topup_from_idle) - maintenance_margin_frac``.
  A breach force-closes both legs at the liquidation price (perp) and the
  interval close (spot), pays the venue liquidation fee and ``liq_penalty_bps``.
* **Outputs**: annualized net (simple and CAGR), max drawdown, funding captured
  vs costs, basis P&L, idle yield, time in market, worst single-interval basis
  shock (in position and overall), liquidation count, per-trade log, equity
  curve. ``walk_forward`` picks thresholds on year *k-1* and evaluates on year *k*.

The historical funding/candles are offshore proxies (Binance) for the young US
perps; see pb/carry/data.py.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from pb.carry.venues import VenueFees, KRAKEN_BTC, annualize

HOURS_PER_YEAR = 8760.0


@dataclass
class CarryParams:
    capital: float = 10_000.0
    entry_ann: float = 0.08
    exit_ann: float = 0.02
    lookback: int = 3
    min_hold: int = 1
    perp_collateral_frac: float = 0.5
    notional_frac: float | None = None
    spot_maker: bool = False
    perp_maker: bool = False
    slippage_bps: float = 2.0
    tbill_rate: float = 0.04
    collateral_yield: float = 0.0
    topup_from_idle: bool = True
    liq_penalty_bps: float = 50.0
    exit_on_negative_print: bool = True

    def notional(self) -> float:
        f = self.notional_frac if self.notional_frac is not None else 1.0 / (1.0 + self.perp_collateral_frac)
        return self.capital * f


@dataclass
class Trade:
    entry_ts: float
    exit_ts: float | None = None
    entry_spot: float = 0.0
    entry_perp: float = 0.0
    exit_spot: float = 0.0
    exit_perp: float = 0.0
    notional: float = 0.0
    intervals: int = 0
    funding: float = 0.0
    basis_pnl: float = 0.0
    fees: float = 0.0
    slippage: float = 0.0
    liq_fee: float = 0.0
    reason: str = ""

    @property
    def net(self) -> float:
        return self.funding + self.basis_pnl - self.fees - self.slippage - self.liq_fee


@dataclass
class CarryResult:
    params: dict
    venue: str
    start_ts: float
    end_ts: float
    hours: float
    intervals: int
    net_pnl: float
    annualized_net: float
    cagr: float
    max_drawdown: float
    max_drawdown_frac: float
    funding_captured: float
    fees: float
    slippage: float
    costs: float
    basis_pnl: float
    idle_yield: float
    liq_fees: float
    time_in_market: float
    n_trades: int
    liquidations: int
    worst_basis_shock_usd: float
    worst_basis_shock_bps: float
    worst_basis_shock_bps_any: float
    liq_distance_frac: float
    mean_ann_funding: float
    frac_intervals_positive: float
    benchmark_tbill_pnl: float
    excess_over_tbill_ann: float
    trades: list[dict] = field(default_factory=list)
    equity: pd.DataFrame | None = None

    def summary(self) -> dict:
        d = {k: v for k, v in asdict(self).items() if k not in ("trades", "equity")}
        d["trades"] = self.trades
        return d


# --------------------------------------------------------------------------- alignment


def align(funding: pd.DataFrame, spot: pd.DataFrame, perp: pd.DataFrame) -> pd.DataFrame:
    """One row per funding interval with the latest candle close at/before the
    interval end and the perp high within the interval (for liquidation checks)."""
    f = funding.sort_values("ts").drop_duplicates("ts").reset_index(drop=True).astype({"ts": float})
    s = spot.sort_values("ts")[["ts", "close"]].rename(columns={"close": "spot_close"}).astype(float)
    p = perp.sort_values("ts")[["ts", "close", "high"]].rename(columns={"close": "perp_close", "high": "perp_high_bar"}).astype(float)
    out = pd.merge_asof(f, s, on="ts", direction="backward")
    out = pd.merge_asof(out, p[["ts", "perp_close"]], on="ts", direction="backward")
    # perp high within (prev_ts, ts]
    highs = np.full(len(out), np.nan)
    pts = p["ts"].to_numpy()
    phigh = p["perp_high_bar"].to_numpy()
    prev = -np.inf
    for i, t in enumerate(out["ts"].to_numpy()):
        lo = np.searchsorted(pts, prev, side="right")
        hi = np.searchsorted(pts, t, side="right")
        if hi > lo:
            highs[i] = np.nanmax(phigh[lo:hi])
        prev = t
    out["perp_high"] = highs
    out["perp_high"] = out["perp_high"].fillna(out["perp_close"])
    out = out.dropna(subset=["spot_close", "perp_close"]).reset_index(drop=True)
    out["ann"] = [annualize(r, h) for r, h in zip(out["rate"], out["interval_hours"])]
    return out


# --------------------------------------------------------------------------- core


def _leg_cost(fees, notional: float, price: float, maker: bool, slippage_bps: float) -> tuple[float, float]:
    fee = fees.cost(notional, price, maker)
    slip = 0.0 if maker else notional * slippage_bps / 1e4
    return fee, slip


def run_backtest(aligned: pd.DataFrame, params: CarryParams, fees: VenueFees = KRAKEN_BTC) -> CarryResult:
    df = aligned.reset_index(drop=True)
    n = len(df)
    if n == 0:
        raise ValueError("empty dataset")
    ts = df["ts"].to_numpy(float)
    rate = df["rate"].to_numpy(float)
    ann = df["ann"].to_numpy(float)
    ih = df["interval_hours"].to_numpy(float)
    spot = df["spot_close"].to_numpy(float)
    perp = df["perp_close"].to_numpy(float)
    phigh = df["perp_high"].to_numpy(float)
    sig = pd.Series(ann).rolling(params.lookback, min_periods=params.lookback).mean().to_numpy()

    N = params.notional()
    collateral = N * params.perp_collateral_frac
    cash = params.capital  # realized equity
    in_pos = False
    tr: Trade | None = None
    trades: list[Trade] = []
    eq = np.zeros(n)
    unreal = 0.0
    tot_funding = tot_fees = tot_slip = tot_idle = tot_liq = tot_basis = 0.0
    in_market = 0
    liqs = 0
    worst_shock_usd = 0.0
    worst_shock_bps = 0.0
    prev_basis = 0.0
    # overall basis-shock stat (premium change per interval, bps), independent of position
    prem = perp / spot - 1.0
    dprem = np.diff(prem, prepend=prem[0])
    worst_any_bps = float(-np.max(dprem) * 1e4) if n > 1 else 0.0  # premium widening hurts the short perp

    idle_cash_flat = params.capital
    static_liq_dist = params.perp_collateral_frac - fees.maintenance_margin_frac
    if params.topup_from_idle:
        idle_in_pos = max(params.capital - N - collateral, 0.0)
        static_liq_dist += idle_in_pos / N if N > 0 else 0.0

    for i in range(n):
        dt_years = ih[i] / HOURS_PER_YEAR
        if in_pos:
            assert tr is not None
            in_market += 1
            tr.intervals += 1
            # funding earned this interval (short perp receives positive funding)
            f = rate[i] * N
            tr.funding += f
            cash += f
            tot_funding += f
            idle = max(cash - N - collateral, 0.0)
            y = idle * params.tbill_rate * dt_years + collateral * params.collateral_yield * dt_years
            cash += y
            tot_idle += y
            # basis mark
            basis = N * (spot[i] / tr.entry_spot - perp[i] / tr.entry_perp)
            shock = basis - prev_basis
            if shock < worst_shock_usd:
                worst_shock_usd = shock
                worst_shock_bps = shock / N * 1e4
            prev_basis = basis
            unreal = basis
            # liquidation check on intra-interval perp high
            liq_dist = params.perp_collateral_frac - fees.maintenance_margin_frac
            if params.topup_from_idle:
                liq_dist += idle / N
            liq_price = tr.entry_perp * (1.0 + liq_dist)
            forced = phigh[i] >= liq_price
            exit_now = False
            reason = ""
            if forced:
                exit_now, reason = True, "liquidation"
            elif tr.intervals >= params.min_hold:
                if not math.isnan(sig[i]) and sig[i] < params.exit_ann:
                    exit_now, reason = True, "signal_below_exit"
                elif params.exit_on_negative_print and rate[i] < 0:
                    exit_now, reason = True, "negative_print"
            if exit_now:
                xp = liq_price if forced else perp[i]
                xs = spot[i]
                tr.exit_ts, tr.exit_spot, tr.exit_perp, tr.reason = ts[i], xs, xp, reason
                tr.basis_pnl = N * (xs / tr.entry_spot - xp / tr.entry_perp)
                fs, ss = _leg_cost(fees.spot, N * xs / tr.entry_spot, xs, params.spot_maker, params.slippage_bps)
                fp, sp = _leg_cost(fees.perp, N * xp / tr.entry_perp, xp, params.perp_maker and not forced, params.slippage_bps)
                tr.fees += fs + fp
                tr.slippage += ss + sp
                if forced:
                    tr.liq_fee = fees.liquidation_fee_usd + N * params.liq_penalty_bps / 1e4
                    liqs += 1
                cash += tr.basis_pnl - fs - fp - ss - sp - tr.liq_fee
                tot_fees += fs + fp
                tot_slip += ss + sp
                tot_liq += tr.liq_fee
                tot_basis += tr.basis_pnl
                trades.append(tr)
                tr, in_pos, unreal, prev_basis = None, False, 0.0, 0.0
        else:
            y = cash * params.tbill_rate * dt_years
            cash += y
            tot_idle += y
            if not math.isnan(sig[i]) and sig[i] > params.entry_ann and i < n - 1:
                tr = Trade(entry_ts=ts[i], entry_spot=spot[i], entry_perp=perp[i], notional=N)
                fs, ss = _leg_cost(fees.spot, N, spot[i], params.spot_maker, params.slippage_bps)
                fp, sp = _leg_cost(fees.perp, N, perp[i], params.perp_maker, params.slippage_bps)
                tr.fees, tr.slippage = fs + fp, ss + sp
                cash -= fs + fp + ss + sp
                tot_fees += fs + fp
                tot_slip += ss + sp
                in_pos = True
        eq[i] = cash + unreal

    # close any open position at the last bar (mark-to-market, pay exit costs)
    if in_pos and tr is not None:
        i = n - 1
        tr.exit_ts, tr.exit_spot, tr.exit_perp, tr.reason = ts[i], spot[i], perp[i], "end_of_data"
        tr.basis_pnl = N * (spot[i] / tr.entry_spot - perp[i] / tr.entry_perp)
        fs, ss = _leg_cost(fees.spot, N, spot[i], params.spot_maker, params.slippage_bps)
        fp, sp = _leg_cost(fees.perp, N, perp[i], params.perp_maker, params.slippage_bps)
        tr.fees += fs + fp
        tr.slippage += ss + sp
        cash += tr.basis_pnl - fs - fp - ss - sp
        tot_fees += fs + fp
        tot_slip += ss + sp
        tot_basis += tr.basis_pnl
        trades.append(tr)
        eq[i] = cash

    hours = float(ts[-1] - ts[0]) / 3600.0 + float(ih[-1])
    years = max(hours / HOURS_PER_YEAR, 1e-9)
    net = cash - params.capital
    peak = np.maximum.accumulate(eq)
    dd = peak - eq
    max_dd = float(dd.max()) if n else 0.0
    bench = params.capital * ((1 + params.tbill_rate) ** years - 1)
    ann_net = net / params.capital / years
    cagr = (cash / params.capital) ** (1 / years) - 1 if cash > 0 else -1.0
    equity = pd.DataFrame({"ts": ts, "equity": eq, "ann_funding": ann, "signal": sig})
    return CarryResult(
        params=asdict(params), venue=fees.name, start_ts=float(ts[0]), end_ts=float(ts[-1]), hours=hours, intervals=n,
        net_pnl=net, annualized_net=ann_net, cagr=cagr, max_drawdown=max_dd, max_drawdown_frac=max_dd / params.capital,
        funding_captured=tot_funding, fees=tot_fees, slippage=tot_slip, costs=tot_fees + tot_slip + tot_liq,
        basis_pnl=tot_basis, idle_yield=tot_idle, liq_fees=tot_liq, time_in_market=in_market / n,
        n_trades=len(trades), liquidations=liqs, worst_basis_shock_usd=worst_shock_usd,
        worst_basis_shock_bps=worst_shock_bps, worst_basis_shock_bps_any=worst_any_bps,
        liq_distance_frac=static_liq_dist, mean_ann_funding=float(np.mean(ann)),
        frac_intervals_positive=float(np.mean(rate > 0)), benchmark_tbill_pnl=bench,
        excess_over_tbill_ann=ann_net - bench / params.capital / years,
        trades=[{**asdict(t), "net": t.net} for t in trades], equity=equity,
    )


# --------------------------------------------------------------------------- walk-forward


def _year(ts: float) -> int:
    return datetime.fromtimestamp(ts, tz=timezone.utc).year


def grid_points(grid: dict[str, list]) -> list[dict]:
    keys = list(grid)
    return [dict(zip(keys, vals)) for vals in itertools.product(*(grid[k] for k in keys))]


def walk_forward(aligned: pd.DataFrame, base: CarryParams, grid: dict[str, list], fees: VenueFees = KRAKEN_BTC,
                 objective: str = "annualized_net", min_train_intervals: int = 100) -> dict:
    """Per calendar year k >= first+1: choose grid point maximizing ``objective``
    on year k-1 (all prior years when ``train_all_prior``), evaluate on year k."""
    years = aligned["ts"].map(_year)
    uniq = sorted(years.unique())
    oos: list[dict] = []
    for k in uniq[1:]:
        train = aligned[years == k - 1]
        test = aligned[years == k]
        if len(train) < min_train_intervals or len(test) < 2:
            continue
        best, best_v, best_p = None, -np.inf, None
        for gp in grid_points(grid):
            p = CarryParams(**{**asdict(base), **gp})
            try:
                r = run_backtest(train, p, fees)
            except ValueError:
                continue
            v = getattr(r, objective)
            if v > best_v:
                best, best_v, best_p = gp, v, p
        if best_p is None:
            continue
        r = run_backtest(test, best_p, fees)
        s = r.summary()
        s.pop("trades", None)
        oos.append({"year": int(k), "train_year": int(k - 1), "chosen": best, "train_objective": best_v, **s})
    if oos:
        tot_hours = sum(o["hours"] for o in oos)
        net = sum(o["net_pnl"] for o in oos)
        agg = {
            "net_pnl": net,
            "annualized_net": net / base.capital / (tot_hours / HOURS_PER_YEAR),
            "max_drawdown_frac": max(o["max_drawdown_frac"] for o in oos),
            "time_in_market": float(np.average([o["time_in_market"] for o in oos], weights=[o["hours"] for o in oos])),
            "liquidations": sum(o["liquidations"] for o in oos),
            "years": [o["year"] for o in oos],
        }
    else:
        agg = {}
    return {"oos": oos, "aggregate": agg}


# --------------------------------------------------------------------------- synthetic (tests / CI)


def synthetic_dataset(n: int = 2000, seed: int = 0, ann_mean: float = 0.10, ann_sd: float = 0.15,
                      interval_hours: float = 8.0, price0: float = 50_000.0, vol_8h: float = 0.02,
                      premium_sd: float = 0.0005, start_ts: float = 1_577_836_800.0,
                      funding: np.ndarray | None = None, shock_at: int | None = None,
                      shock_bps: float = 0.0) -> pd.DataFrame:
    """Random-walk spot, perp = spot * (1 + premium), AR(1) funding. Never for
    evaluation; CI and unit tests only."""
    rng = np.random.default_rng(seed)
    ts = start_ts + np.arange(n) * interval_hours * 3600
    if funding is None:
        per_int = ann_mean / (HOURS_PER_YEAR / interval_hours)
        sd = ann_sd / (HOURS_PER_YEAR / interval_hours)
        f = np.zeros(n)
        f[0] = per_int
        for i in range(1, n):
            f[i] = per_int + 0.8 * (f[i - 1] - per_int) + sd * 0.6 * rng.standard_normal()
    else:
        f = np.asarray(funding, float)
        assert len(f) == n
    rets = rng.standard_normal(n) * vol_8h
    spot = price0 * np.exp(np.cumsum(rets))
    prem = rng.standard_normal(n) * premium_sd
    if shock_at is not None:
        prem[shock_at:] += shock_bps / 1e4
    perp = spot * (1 + prem)
    high = perp * (1 + np.abs(rng.standard_normal(n)) * vol_8h * 0.5)
    df = pd.DataFrame({"ts": ts, "rate": f, "interval_hours": interval_hours, "spot_close": spot,
                       "perp_close": perp, "perp_high": np.maximum(high, perp)})
    df["ann"] = df["rate"] * (HOURS_PER_YEAR / interval_hours)
    return df
