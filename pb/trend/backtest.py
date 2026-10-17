"""Monthly ETF trend / momentum backtest with daily-marked accounting.

Signals (all computed on month-end closes, data through month *t* only):

* **TSMOM** ``lookback``-month return skipping the last ``skip`` months
  (12-1 by default), in excess of the T-bill return over the same window.
  Positive -> long that ETF with weight ``1/N_valid``; else its share sits in cash.
* **SMA** close above its ``sma_months``-month simple moving average -> long,
  same equal weighting.
* **GEM** (Antonacci dual momentum): if the ``gem_lookback``-month return of the
  best of ``gem_equity`` (SPY, EFA) beats T-bills, 100 % in that ETF; else 100 %
  in ``gem_bond`` (IEF); before the bond ETF exists, cash.
* **Ensemble**: equal average of the three weight vectors, then scaled so the
  trailing ``vol_lookback_days`` realized portfolio vol equals ``target_vol``,
  never above ``max_gross`` (1.0: a cash account cannot lever). Vol targeting
  therefore only de-risks.

Execution: targets decided at the month-end close are traded at the close
``exec_lag_days`` trading days later (default 1: the signal is computed after
the close, the order goes in next day). Between rebalances holdings drift with
daily prices; the cash sleeve accrues the FRED 3-month T-bill yield (act/365).

Costs per trade (each side, on traded notional): ``spread_bps`` + ``slippage_bps``
(1 + 2 bps default) plus ``commission_usd`` per filled line (0 at every major US
broker). Cash moves are free.

Metrics from the daily equity curve: CAGR, annualized vol, Sharpe (daily excess
over the cash yield, sqrt(252)), max drawdown, calendar-year returns and the
worst one, one-way annual turnover (sum |trade| / NAV per year), cost drag.

Walk-forward: each grid point is run once over the full history (weights are a
function of prices only, so a year's returns do not depend on where the run
started except for the first rebalance); for every year *k* with
``train_years`` of history before it the grid point with the best ``objective``
on years ``[k-train_years, k)`` is chosen and its year-*k* returns are the
out-of-sample record. The OOS years are chained into one equity curve.

Reality: published trend / momentum Sharpe decays ~50 % after publication
(McLean & Pontiff 2016; https://arxiv.org/pdf/2105.01380); the report prints a
haircut row. ETF begin dates (SPY 1993, QQQ 1999, EFA 2001, IEF/TLT 2002, EEM 2003,
GLD/VNQ 2004, DBC 2006) mean the full universe only exists from 2006 and the
10-year-train walk-forward only starts in 2016 on real data.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field, asdict, fields

import numpy as np
import pandas as pd

TRADING_DAYS = 252.0
STRATEGIES = ("tsmom", "sma", "gem", "ensemble")
BENCHMARKS = ("spy_bh", "sixty_forty")


@dataclass
class TrendParams:
    capital: float = 10_000.0
    tsmom_lookback: int = 12
    tsmom_skip: int = 1
    sma_months: int = 10
    gem_lookback: int = 12
    gem_equity: tuple = ("SPY", "EFA")
    gem_bond: str = "IEF"
    target_vol: float = 0.10
    vol_lookback_days: int = 63
    max_gross: float = 1.0
    spread_bps: float = 1.0
    slippage_bps: float = 2.0
    commission_usd: float = 0.0
    exec_lag_days: int = 1
    min_trade_usd: float = 1.0   # ignore sub-$1 dust trades (brokers reject them anyway)
    bench_bond: str = "IEF"

    def __post_init__(self):
        self.gem_equity = tuple(self.gem_equity)

    @classmethod
    def from_dict(cls, d: dict) -> "TrendParams":
        names = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in names})

    def cost_bps(self) -> float:
        return self.spread_bps + self.slippage_bps


@dataclass
class TrendResult:
    name: str
    params: dict
    start: str
    end: str
    years: float
    cagr: float
    ann_vol: float
    sharpe: float
    max_drawdown: float
    worst_year: int | None
    worst_year_ret: float | None
    annual_turnover: float
    costs_usd: float
    cost_drag_ann: float
    n_rebalances: int
    final_equity: float
    avg_cash_weight: float
    yearly: dict = field(default_factory=dict)
    equity: pd.Series | None = None
    excess: pd.Series | None = None     # daily returns in excess of cash
    returns: pd.Series | None = None    # daily returns
    weights: pd.DataFrame | None = None

    def summary(self) -> dict:
        return {k: v for k, v in asdict(self).items() if k not in ("equity", "excess", "returns", "weights")}


# --------------------------------------------------------------------------- helpers


def month_ends(prices: pd.DataFrame) -> pd.DataFrame:
    """Last available close of each calendar month (index = that trading day)."""
    return prices.groupby([prices.index.year, prices.index.month]).tail(1)


def cash_index(rate: pd.Series | float | None, index: pd.DatetimeIndex) -> tuple[pd.Series, pd.Series]:
    """(daily cash rate aligned to ``index``, cumulative cash index starting at 1).
    ``rate`` is an annual fraction series (FRED DGS3MO / 100), a constant, or None (0)."""
    if rate is None:
        r = pd.Series(0.0, index=index)
    elif isinstance(rate, (int, float)):
        r = pd.Series(float(rate), index=index)
    else:
        r = rate.reindex(index.union(rate.index)).sort_index().ffill().reindex(index).fillna(0.0)
    days = np.diff(index.values.astype("datetime64[D]").astype(np.int64), prepend=index.values[0].astype("datetime64[D]").astype(np.int64))
    daily = r.shift(1).fillna(0.0).to_numpy() * days / 365.0   # yesterday's rate accrues over the gap
    ci = pd.Series(np.cumprod(1.0 + daily), index=index)
    return r, ci


def _equal_weight(sig: pd.DataFrame, valid: pd.DataFrame) -> pd.DataFrame:
    n_valid = valid.sum(axis=1).replace(0, np.nan)
    return sig.astype(float).where(valid, 0.0).div(n_valid, axis=0).fillna(0.0)


# --------------------------------------------------------------------------- signals (month-end frames)


def tsmom_weights(M: pd.DataFrame, Cm: pd.Series, lookback: int = 12, skip: int = 1) -> pd.DataFrame:
    ret = M.shift(skip) / M.shift(lookback + skip) - 1.0
    cret = Cm.shift(skip) / Cm.shift(lookback + skip) - 1.0
    valid = ret.notna()
    sig = ret.sub(cret, axis=0) > 0
    return _equal_weight(sig, valid)


def sma_weights(M: pd.DataFrame, months: int = 10) -> pd.DataFrame:
    sma = M.rolling(months, min_periods=months).mean()
    valid = sma.notna() & M.notna()
    sig = M > sma
    return _equal_weight(sig, valid)


def gem_weights(M: pd.DataFrame, Cm: pd.Series, lookback: int = 12, equity=("SPY", "EFA"), bond: str = "IEF") -> pd.DataFrame:
    ret = M / M.shift(lookback) - 1.0
    cret = Cm / Cm.shift(lookback) - 1.0
    w = pd.DataFrame(0.0, index=M.index, columns=M.columns)
    eq_cols = [c for c in equity if c in M.columns]
    for i, t in enumerate(M.index):
        r = ret.loc[t, eq_cols].dropna() if eq_cols else pd.Series(dtype=float)
        if r.empty:
            continue
        best = r.idxmax()
        if r[best] > cret.iloc[i]:
            w.loc[t, best] = 1.0
        elif bond in M.columns and not math.isnan(ret.loc[t, bond]):
            w.loc[t, bond] = 1.0
    return w


def vol_target(w: pd.DataFrame, prices: pd.DataFrame, target_vol: float, lookback_days: int = 63,
               max_gross: float = 1.0) -> tuple[pd.DataFrame, pd.Series]:
    """Scale each month's weight vector so trailing realized portfolio vol hits
    ``target_vol`` (never scaling up past ``max_gross``). Returns (weights, scale)."""
    rets = prices.pct_change()
    out = w.copy()
    scale = pd.Series(1.0, index=w.index)
    for t in w.index:
        wt = w.loc[t].fillna(0.0)
        gross = float(wt.abs().sum())
        if gross <= 0:
            continue
        s = min(1.0, max_gross / gross)
        window = rets.loc[:t].tail(lookback_days)
        cols = wt.index[wt != 0]
        sub = window[cols].dropna(how="any")
        if len(sub) >= max(20, lookback_days // 3):
            cov = sub.cov().to_numpy() * TRADING_DAYS
            v = float(np.sqrt(max(wt[cols].to_numpy() @ cov @ wt[cols].to_numpy(), 0.0)))
            if v > 1e-9:
                s = min(s, target_vol / v)
        scale[t] = s
        out.loc[t] = wt * s
    return out, scale


def strategy_weights(prices: pd.DataFrame, cash_rate, params: TrendParams, strategy: str = "ensemble") -> pd.DataFrame:
    """Month-end target weights (columns = ETF symbols; cash = 1 - row sum)."""
    _, ci = cash_index(cash_rate, prices.index)
    M = month_ends(prices)
    Cm = ci.reindex(M.index)
    if strategy == "tsmom":
        return tsmom_weights(M, Cm, params.tsmom_lookback, params.tsmom_skip)
    if strategy == "sma":
        return sma_weights(M, params.sma_months)
    if strategy == "gem":
        return gem_weights(M, Cm, params.gem_lookback, params.gem_equity, params.gem_bond)
    if strategy == "ensemble":
        w = (tsmom_weights(M, Cm, params.tsmom_lookback, params.tsmom_skip)
             + sma_weights(M, params.sma_months)
             + gem_weights(M, Cm, params.gem_lookback, params.gem_equity, params.gem_bond)) / 3.0
        w, _ = vol_target(w, prices, params.target_vol, params.vol_lookback_days, params.max_gross)
        return w
    if strategy == "spy_bh":
        w = pd.DataFrame(0.0, index=M.index, columns=M.columns)
        w.loc[M["SPY"].notna(), "SPY"] = 1.0
        return w
    if strategy == "sixty_forty":
        w = pd.DataFrame(0.0, index=M.index, columns=M.columns)
        w.loc[M["SPY"].notna(), "SPY"] = 0.6
        if params.bench_bond in M.columns:
            w.loc[M[params.bench_bond].notna(), params.bench_bond] = 0.4
        return w
    raise ValueError(f"unknown strategy {strategy}")


# --------------------------------------------------------------------------- accounting


def simulate(prices: pd.DataFrame, weights: pd.DataFrame, cash_rate, params: TrendParams, name: str = "strategy",
             start: pd.Timestamp | None = None) -> TrendResult:
    """Daily-marked paper account: trade to ``weights`` at the close ``exec_lag_days``
    after each signal date, drift in between, cash earns the T-bill yield."""
    P = prices.sort_index()
    idx = P.index
    px = P.to_numpy(float)
    k = px.shape[1]
    rate, _ = cash_index(cash_rate, idx)
    rate = rate.to_numpy(float)
    days = np.diff(idx.values.astype("datetime64[D]").astype(np.int64))
    pos = {t: i for i, t in enumerate(idx)}
    exec_at: dict[int, pd.Timestamp] = {}
    for t in weights.index:
        if t in pos and pos[t] + params.exec_lag_days < len(idx):
            exec_at[pos[t] + params.exec_lag_days] = t
    if not exec_at:
        raise ValueError("no executable rebalance dates")
    first = min(exec_at)
    if start is not None:
        first = max(first, int(np.searchsorted(idx.values, np.datetime64(start))))
    h = np.zeros(k)
    C = float(params.capital)
    eq = np.full(len(idx), np.nan)
    turn_frac: list[float] = []
    costs = 0.0
    cost_frac = 0.0
    n_reb = 0
    held_w: list[np.ndarray] = []
    cash_w: list[float] = []
    wlog: dict[pd.Timestamp, np.ndarray] = {}
    cbps = params.cost_bps() / 1e4
    for i in range(first, len(idx)):
        if i > first:
            ratio = px[i] / px[i - 1]
            ratio = np.where(np.isfinite(ratio), ratio, 1.0)
            h = h * ratio
            C *= 1.0 + rate[i - 1] * days[i - 1] / 365.0
        if i in exec_at:
            w = weights.loc[exec_at[i]].reindex(P.columns).fillna(0.0).to_numpy(float)
            w = np.where(np.isfinite(px[i]), w, 0.0)
            V = h.sum() + C
            # reserve the (estimated) cost so a fully invested book never goes cash-negative
            est = float(np.abs(w * V - h).sum()) * cbps + params.commission_usd * int((np.abs(w * V - h) >= params.min_trade_usd).sum())
            target = w * max(V - est, 0.0)
            trade = target - h
            trade = np.where(np.abs(trade) >= params.min_trade_usd, trade, 0.0)
            target = h + trade
            turnover = float(np.abs(trade).sum())
            cost = turnover * cbps + params.commission_usd * int((np.abs(trade) > 0).sum())
            h = target
            C = V - target.sum() - cost
            costs += cost
            if V > 0:
                turn_frac.append(turnover / V)
                cost_frac += cost / V
            n_reb += 1
            wlog[idx[i]] = w.copy()
        V = h.sum() + C
        eq[i] = V
        if V > 0:
            held_w.append(h / V)
            cash_w.append(C / V)
    equity = pd.Series(eq, index=idx).iloc[first:]
    rets = equity.pct_change().fillna(0.0)
    cash_daily = pd.Series(np.concatenate([[0.0], rate[first:-1] * days[first:] / 365.0]), index=equity.index)
    excess = rets - cash_daily
    years = max((equity.index[-1] - equity.index[0]).days / 365.25, 1e-9)
    final = float(equity.iloc[-1])
    cagr = (final / params.capital) ** (1 / years) - 1 if final > 0 else -1.0
    vol = float(rets.iloc[1:].std() * math.sqrt(TRADING_DAYS)) if len(rets) > 2 else 0.0
    sd = float(excess.iloc[1:].std())
    sharpe = float(excess.iloc[1:].mean() / sd * math.sqrt(TRADING_DAYS)) if sd > 0 else 0.0
    dd = float((equity / equity.cummax() - 1.0).min())
    yearly: dict[int, float] = {}
    prev_val = float(equity.iloc[0])
    for y, g in equity.groupby(equity.index.year):
        yearly[int(y)] = float(g.iloc[-1] / prev_val - 1.0)
        prev_val = float(g.iloc[-1])
    wy = min(yearly, key=yearly.get) if yearly else None
    wdf = pd.DataFrame(wlog, index=P.columns).T if wlog else None
    return TrendResult(
        name=name, params=asdict(params), start=str(equity.index[0].date()), end=str(equity.index[-1].date()),
        years=years, cagr=float(cagr), ann_vol=vol, sharpe=sharpe, max_drawdown=dd, worst_year=wy,
        worst_year_ret=yearly.get(wy) if wy is not None else None,
        annual_turnover=float(sum(turn_frac) / years), costs_usd=float(costs), cost_drag_ann=float(cost_frac / years),
        n_rebalances=n_reb, final_equity=final, avg_cash_weight=float(np.mean(cash_w)) if cash_w else 1.0,
        yearly=yearly, equity=equity, excess=excess, returns=rets, weights=wdf,
    )


def run_strategy(prices: pd.DataFrame, cash_rate, params: TrendParams, strategy: str = "ensemble",
                 start: pd.Timestamp | None = None) -> TrendResult:
    w = strategy_weights(prices, cash_rate, params, strategy)
    return simulate(prices, w, cash_rate, params, name=strategy, start=start)


# --------------------------------------------------------------------------- walk-forward


def grid_points(grid: dict[str, list]) -> list[dict]:
    keys = list(grid)
    return [dict(zip(keys, vals)) for vals in itertools.product(*(grid[k] for k in keys))]


def _metrics_from_returns(rets: pd.Series, excess: pd.Series) -> dict:
    if len(rets) < 2:
        return {"ret": 0.0, "sharpe": 0.0, "max_drawdown": 0.0, "ann_vol": 0.0, "cagr": 0.0}
    eq = (1.0 + rets).cumprod()
    years = max((rets.index[-1] - rets.index[0]).days / 365.25, 1e-9)
    sd = float(excess.std())
    return {
        "ret": float(eq.iloc[-1] - 1.0),
        "cagr": float(eq.iloc[-1] ** (1 / years) - 1.0),
        "ann_vol": float(rets.std() * math.sqrt(TRADING_DAYS)),
        "sharpe": float(excess.mean() / sd * math.sqrt(TRADING_DAYS)) if sd > 0 else 0.0,
        "max_drawdown": float((eq / eq.cummax() - 1.0).min()),
    }


def walk_forward(prices: pd.DataFrame, cash_rate, base: TrendParams, grid: dict[str, list], strategy: str = "ensemble",
                 train_years: int = 10, objective: str = "sharpe", min_train_days: int = 500) -> dict:
    """Choose the grid point with the best ``objective`` on the ``train_years``
    before year k, score year k. Returns {oos: [...], aggregate: {...}, grid_runs: n}."""
    runs: list[tuple[dict, TrendResult]] = []
    for gp in grid_points(grid):
        p = TrendParams(**{**asdict(base), **gp})
        try:
            runs.append((gp, run_strategy(prices, cash_rate, p, strategy)))
        except ValueError:
            continue
    if not runs:
        return {"oos": [], "aggregate": {}, "grid_runs": 0}
    ref = runs[0][1]
    years_idx = ref.returns.index.year
    uniq = sorted(set(int(y) for y in years_idx))
    oos: list[dict] = []
    chained_r: list[pd.Series] = []
    chained_x: list[pd.Series] = []
    for k in uniq:
        if k - train_years < uniq[0]:
            continue
        best, best_v, best_r = None, -np.inf, None
        for gp, r in runs:
            yi = r.returns.index.year
            tr = (yi >= k - train_years) & (yi < k)
            if tr.sum() < min_train_days:
                continue
            m = _metrics_from_returns(r.returns[tr], r.excess[tr])
            v = m[objective]
            if v > best_v:
                best, best_v, best_r = gp, v, r
        if best_r is None:
            continue
        yi = best_r.returns.index.year
        te = yi == k
        if te.sum() < 2:
            continue
        m = _metrics_from_returns(best_r.returns[te], best_r.excess[te])
        oos.append({"year": k, "train_years": [k - train_years, k - 1], "chosen": best,
                    "train_objective": float(best_v), **m})
        chained_r.append(best_r.returns[te])
        chained_x.append(best_r.excess[te])
    agg: dict = {}
    if oos:
        r = pd.concat(chained_r)
        x = pd.concat(chained_x)
        agg = {**_metrics_from_returns(r, x), "years": [o["year"] for o in oos],
               "worst_year": min(oos, key=lambda o: o["ret"])["year"],
               "worst_year_ret": min(o["ret"] for o in oos),
               "mean_year_ret": float(np.mean([o["ret"] for o in oos])),
               "frac_years_positive": float(np.mean([o["ret"] > 0 for o in oos]))}
    return {"oos": oos, "aggregate": agg, "grid_runs": len(runs)}


# --------------------------------------------------------------------------- synthetic (tests / CI)


def synthetic_prices(years: int = 30, seed: int = 0, symbols: list[str] | None = None,
                     start: str = "1994-01-03", stagger: dict[str, int] | None = None) -> tuple[pd.DataFrame, pd.Series]:
    """Regime-switching GBM per symbol on business days, staggered start dates
    to mimic ETF inception, constant 3 % cash yield. Never for evaluation."""
    from pb.trend.data import UNIVERSE
    symbols = symbols or [*UNIVERSE, "SHY"]
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start, periods=int(years * 252))
    n = len(idx)
    stagger = stagger if stagger is not None else {
        "QQQ": 5, "EFA": 7, "IEF": 8, "TLT": 8, "EEM": 9, "GLD": 10, "VNQ": 10, "DBC": 12}
    cols = {}
    for s in symbols:
        if s == "SHY":
            cols[s] = pd.Series(100.0 * np.cumprod(1.0 + np.full(n, 0.03 / 252)), index=idx)
            continue
        daily_vol = {"TLT": 0.14, "IEF": 0.06, "GLD": 0.15, "DBC": 0.18, "EEM": 0.22, "QQQ": 0.22}.get(s, 0.17) / math.sqrt(252)
        drift = np.zeros(n)
        i = 0
        while i < n:
            L = int(rng.integers(120, 400))
            mu = rng.choice([-0.15, 0.0, 0.12, 0.20]) / 252
            drift[i:i + L] = mu
            i += L
        r = drift + daily_vol * rng.standard_normal(n)
        p = 50.0 * np.exp(np.cumsum(r))
        s0 = int(stagger.get(s, 0) * 252)
        p[:s0] = np.nan
        cols[s] = pd.Series(p, index=idx)
    prices = pd.DataFrame(cols)
    cash = pd.Series(0.03, index=idx)
    return prices, cash
