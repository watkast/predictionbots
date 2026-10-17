"""Venture #3: monthly ETF time-series trend + cross-sectional momentum (GEM-style).

Universe: SPY QQQ IWM EFA EEM TLT IEF GLD DBC VNQ with SHY (BIL fallback) as the
cash proxy. Monthly rebalance, overnight holds only (no pattern-day-trader
exposure), free data (Stooq CSV, yfinance on Actions, FRED DGS3MO).

Modules
-------
data      downloaders (run on GitHub Actions, which has internet) -> data/trend/*.parquet
backtest  monthly signals (TSMOM 12-1, 10-month SMA, GEM dual momentum, vol-targeted
          ensemble), daily-marked rebalance accounting, costs, walk-forward
paper     target weights vs a paper book (data/trend/paper-*.jsonl); no orders

Nothing here places orders.
"""
