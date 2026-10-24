# Trend / momentum backtest (monthly ETF, overnight holds only)

generated 2026-10-24T09:09:10.750727+00:00  synthetic=False

Daily closes 1993-01-29 .. 2026-10-23 (8492 days); cash sleeve earns fred. Costs: 1 bp spread + 2 bp slippage per trade, zero commission; signal at month-end close, executed next close.

| symbol | first date | source | dividend-adjusted |
|---|---|---|---|
| SPY | 1993-01-29 | yfinance | True |
| QQQ | 1999-03-10 | yfinance | True |
| IWM | 2000-05-26 | yfinance | True |
| EFA | 2001-08-27 | yfinance | True |
| EEM | 2003-04-14 | yfinance | True |
| TLT | 2002-07-30 | yfinance | True |
| IEF | 2002-07-30 | yfinance | True |
| GLD | 2004-11-18 | yfinance | True |
| DBC | 2006-02-06 | yfinance | True |
| VNQ | 2004-09-29 | yfinance | True |

| name | cagr | ann_vol | sharpe | max_drawdown | worst_year | worst_year_ret | annual_turnover | cost_drag_ann | avg_cash_weight | start | end |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tsmom | 0.0798 | 0.1157 | 0.5008 | -0.3249 | 2000 | -0.2463 | 1.3600 | 0.0004 | 0.3449 | 1993-02-01 | 2026-10-23 |
| sma | 0.0765 | 0.1085 | 0.4982 | -0.2933 | 2000 | -0.1359 | 1.9086 | 0.0006 | 0.3170 | 1993-02-01 | 2026-10-23 |
| gem | 0.1002 | 0.1513 | 0.5381 | -0.3372 | 2022 | -0.1660 | 2.5199 | 0.0008 | 0.1275 | 1993-02-01 | 2026-10-23 |
| ensemble | 0.0753 | 0.0897 | 0.5689 | -0.1926 | 2022 | -0.0853 | 1.8409 | 0.0006 | 0.3584 | 1993-02-01 | 2026-10-23 |
| spy_bh | 0.1076 | 0.1852 | 0.5065 | -0.5519 | 2008 | -0.3680 | 0.0296 | 0.0000 | 0.0000 | 1993-02-01 | 2026-10-23 |
| sixty_forty | 0.0830 | 0.1058 | 0.5643 | -0.3218 | 2008 | -0.1770 | 0.2228 | 0.0001 | 0.1127 | 1993-02-01 | 2026-10-23 |

## Walk-forward (ensemble; 27 grid points, chosen on the prior train window by Sharpe)

| year | train | chosen | train Sharpe | OOS return | OOS Sharpe | OOS max DD |
|---|---|---|---|---|---|---|
| 2003 | 1993-2002 | {'tsmom_lookback': 9, 'sma_months': 12, 'target_vol': 0.08} | 0.58 | 0.1264 | 1.86 | -0.0331 |
| 2004 | 1994-2003 | {'tsmom_lookback': 9, 'sma_months': 12, 'target_vol': 0.08} | 0.71 | 0.1292 | 1.39 | -0.0574 |
| 2005 | 1995-2004 | {'tsmom_lookback': 9, 'sma_months': 12, 'target_vol': 0.08} | 0.95 | 0.0819 | 0.60 | -0.0551 |
| 2006 | 1996-2005 | {'tsmom_lookback': 9, 'sma_months': 12, 'target_vol': 0.1} | 0.71 | 0.1869 | 1.27 | -0.1149 |
| 2007 | 1997-2006 | {'tsmom_lookback': 9, 'sma_months': 12, 'target_vol': 0.1} | 0.72 | 0.1013 | 0.51 | -0.0802 |
| 2008 | 1998-2007 | {'tsmom_lookback': 9, 'sma_months': 12, 'target_vol': 0.1} | 0.62 | 0.0005 | -0.21 | -0.0513 |
| 2009 | 1999-2008 | {'tsmom_lookback': 9, 'sma_months': 12, 'target_vol': 0.1} | 0.57 | 0.0439 | 0.63 | -0.0543 |
| 2010 | 2000-2009 | {'tsmom_lookback': 9, 'sma_months': 12, 'target_vol': 0.1} | 0.56 | 0.0659 | 0.65 | -0.0938 |
| 2011 | 2001-2010 | {'tsmom_lookback': 12, 'sma_months': 12, 'target_vol': 0.1} | 0.72 | 0.0181 | 0.20 | -0.1154 |
| 2012 | 2002-2011 | {'tsmom_lookback': 12, 'sma_months': 12, 'target_vol': 0.1} | 0.70 | 0.0586 | 0.87 | -0.0531 |
| 2013 | 2003-2012 | {'tsmom_lookback': 12, 'sma_months': 12, 'target_vol': 0.1} | 0.78 | 0.1157 | 1.34 | -0.0741 |
| 2014 | 2004-2013 | {'tsmom_lookback': 12, 'sma_months': 12, 'target_vol': 0.1} | 0.73 | 0.0736 | 0.99 | -0.0502 |
| 2015 | 2005-2014 | {'tsmom_lookback': 12, 'sma_months': 12, 'target_vol': 0.1} | 0.69 | -0.0510 | -0.58 | -0.0874 |
| 2016 | 2006-2015 | {'tsmom_lookback': 12, 'sma_months': 12, 'target_vol': 0.1} | 0.56 | 0.0260 | 0.37 | -0.0441 |
| 2017 | 2007-2016 | {'tsmom_lookback': 12, 'sma_months': 10, 'target_vol': 0.1} | 0.47 | 0.1564 | 2.70 | -0.0175 |
| 2018 | 2008-2017 | {'tsmom_lookback': 12, 'sma_months': 10, 'target_vol': 0.08} | 0.62 | -0.0443 | -0.65 | -0.1140 |
| 2019 | 2009-2018 | {'tsmom_lookback': 9, 'sma_months': 10, 'target_vol': 0.1} | 0.53 | 0.1338 | 1.75 | -0.0314 |
| 2020 | 2010-2019 | {'tsmom_lookback': 9, 'sma_months': 10, 'target_vol': 0.08} | 0.60 | -0.0126 | -0.04 | -0.1926 |
| 2021 | 2011-2020 | {'tsmom_lookback': 9, 'sma_months': 8, 'target_vol': 0.12} | 0.50 | 0.1826 | 1.74 | -0.0386 |
| 2022 | 2012-2021 | {'tsmom_lookback': 9, 'sma_months': 10, 'target_vol': 0.12} | 0.71 | -0.0903 | -1.50 | -0.1035 |
| 2023 | 2013-2022 | {'tsmom_lookback': 9, 'sma_months': 8, 'target_vol': 0.12} | 0.53 | 0.0313 | -0.31 | -0.0730 |
| 2024 | 2014-2023 | {'tsmom_lookback': 9, 'sma_months': 8, 'target_vol': 0.12} | 0.39 | 0.1421 | 0.91 | -0.0598 |
| 2025 | 2015-2024 | {'tsmom_lookback': 9, 'sma_months': 8, 'target_vol': 0.12} | 0.40 | 0.1448 | 0.90 | -0.1155 |
| 2026 | 2016-2025 | {'tsmom_lookback': 9, 'sma_months': 8, 'target_vol': 0.12} | 0.56 | 0.0870 | 0.63 | -0.0758 |

OOS chained: CAGR 0.0691, vol 0.0895, Sharpe 0.59, max DD -0.1926, worst year 2022 (-0.0903), 83% of years positive, years 2003-2026

## Reality

* Post-publication decay: published trend/momentum Sharpe roughly halves out of sample (McLean & Pontiff; arxiv 2105.01380). OOS Sharpe 0.59 -> expect ~0.30; OOS CAGR 0.0691 vs mean cash yield 0.0383 -> haircut excess ~0.0154/yr.
* On a $10k account that excess is tens to a few hundred dollars a year; the drawdowns are not haircut.

## Reading this

* `oos<year>` rows and the chained OOS line are the only numbers that count; full-period rows use fixed params.
* Compare the ensemble against `spy_bh` and `sixty_forty` on Sharpe and max DD, not CAGR: trend is a drawdown-control trade.
* Stooq closes are split- but not dividend-adjusted (`dividend-adjusted=False`): total returns and the momentum ranking of TLT/IEF/VNQ/SPY are biased down; yfinance rows are total-return.
* The full ETF universe exists only from 2006 (DBC); earlier years run on whatever ETFs existed, so the 10-year-train walk-forward starts in 2016 on real data.
* Turnover is one-way per year as a fraction of NAV; cost drag is what 3 bps per trade costs at that turnover.
