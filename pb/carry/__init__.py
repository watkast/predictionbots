"""Venture #2: BTC/ETH funding-rate carry (long spot + short perpetual, collect funding).

US-legal path first: CFTC-regulated perpetual-style futures at Coinbase Financial
Markets (Coinbase Derivatives Exchange, ``*-CDE`` products) and Kraken Derivatives US
(Bitnomial-listed ``P*`` perps), with the spot leg on the same operator's spot venue.

Modules
-------
venues    verified venue/API facts and fee schedules (every number cites its URL)
data      downloaders (run on GitHub Actions, which has internet) -> data/carry/*.parquet
backtest  realistic carry backtest + walk-forward
paper     paper-signal ledger (no orders) used by scripts/carry_paper.py

Nothing here places orders.
"""
