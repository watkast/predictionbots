# Carry backtest (long spot + short perp)

generated 2026-10-17T07:03:43.306662+00:00  synthetic=False

Funding/candles are **Binance proxies** for the US perps (Coinbase `BIP-20DEC30-CDE`, Kraken Derivatives US `PBTCUC`); fees from `pb/carry/venues.py`. `oos<year>` rows pick thresholds on the prior year and score the named year; they are the ones that count.

## BTC
7395 funding intervals, 2020-01-01 .. 2026-09-30

| name | annualized_net | excess_over_tbill_ann | cagr | max_drawdown_frac | funding_captured | costs | basis_pnl | idle_yield | time_in_market | n_trades | liquidations | worst_basis_shock_bps | mean_ann_funding | frac_intervals_positive |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | -0.0295 | -0.0744 | -0.0324 | 0.4022 | 5,018 | 8,902 | 845 | 1,046 | 0.6114 | 153 | 5 | -277 | 0.1172 | 0.8599 |
| maker_spot | 0.0340 | -0.0109 | 0.0311 | 0.1246 | 5,020 | 5,067 | 802 | 1,544 | 0.6116 | 151 | 3 | -277 | 0.1172 | 0.8599 |
| coinbase_fees | -0.1848 | -0.2297 | -1.0000 | 1.2888 | 5,007 | 18,031 | 275 | 265 | 0.6112 | 154 | 6 | -277 | 0.1172 | 0.8599 |
| no_tbill | -0.0572 | -0.0572 | -0.0698 | 0.4931 | 5,012 | 9,004 | 128 | 0.0000 | 0.6112 | 154 | 6 | -277 | 0.1172 | 0.8599 |
| always_in | 0.0942 | 0.0493 | 0.0756 | 0.0364 | 5,274 | 725 | 703 | 1,108 | 0.9985 | 7 | 5 | -336 | 0.1172 | 0.8599 |
| oos2021 {'entry_ann': 0.12, 'exit_ann': 0.0} | 0.1465 | 0.1065 | 0.1465 | 0.0420 | 1,931 | 327 | -304 | 165 | 0.6813 | 5 | 1 | -48 | 0.3061 | 0.9269 |
| oos2022 {'entry_ann': 0.2, 'exit_ann': 0.0} | 0.0408 | 0.0008 | 0.0408 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 408 | 0.0000 | 0 | 0 | 0.0000 | 0.0416 | 0.7790 |
| oos2023 {'entry_ann': 0.12, 'exit_ann': 0.0} | 0.0387 | -0.0013 | 0.0387 | 0.0051 | 257 | 176 | 14 | 293 | 0.2831 | 3 | 0 | -18 | 0.0787 | 0.8986 |
| oos2024 {'entry_ann': 0.12, 'exit_ann': 0.02} | 0.0357 | -0.0043 | 0.0357 | 0.0314 | 649 | 283 | -183 | 175 | 0.5783 | 4 | 1 | -20 | 0.1192 | 0.9162 |
| oos2025 {'entry_ann': 0.2, 'exit_ann': 0.05} | 0.0408 | 0.0008 | 0.0408 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 408 | 0.0000 | 0 | 0 | 0.0000 | 0.0513 | 0.8712 |
| oos2026 {'entry_ann': 0.12, 'exit_ann': 0.0} | 0.0406 | 0.0008 | 0.0408 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 304 | 0.0000 | 0 | 0 | 0.0000 | 0.0294 | 0.7399 |

walk-forward aggregate: annualized net 0.0579, max DD 0.0420, time in market 0.27, liquidations 2, years [2021, 2022, 2023, 2024, 2025, 2026]

## ETH
7395 funding intervals, 2020-01-01 .. 2026-09-30

| name | annualized_net | excess_over_tbill_ann | cagr | max_drawdown_frac | funding_captured | costs | basis_pnl | idle_yield | time_in_market | n_trades | liquidations | worst_basis_shock_bps | mean_ann_funding | frac_intervals_positive |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | -0.0224 | -0.0673 | -0.0240 | 0.4666 | 5,948 | 9,495 | 887 | 1,146 | 0.6310 | 158 | 11 | -107 | 0.1384 | 0.8622 |
| maker_spot | 0.0360 | -0.0089 | 0.0328 | 0.1387 | 5,956 | 5,422 | 307 | 1,593 | 0.6314 | 155 | 8 | -107 | 0.1384 | 0.8622 |
| coinbase_fees | -0.2351 | -0.2800 | -1.0000 | 1.6013 | 5,953 | 21,513 | -287 | -30 | 0.6304 | 162 | 15 | -120 | 0.1384 | 0.8622 |
| no_tbill | -0.0390 | -0.0390 | -0.0442 | 0.5607 | 5,941 | 9,494 | 922 | 0.0000 | 0.6310 | 158 | 11 | -108 | 0.1384 | 0.8622 |
| always_in | 0.0948 | 0.0499 | 0.0760 | 0.0499 | 6,208 | 1,373 | 461 | 1,104 | 0.9969 | 14 | 10 | -104 | 0.1384 | 0.8622 |
| oos2021 {'entry_ann': 0.12, 'exit_ann': 0.0} | 0.1735 | 0.1335 | 0.1735 | 0.0535 | 2,309 | 619 | -125 | 170 | 0.6840 | 7 | 4 | -54 | 0.3754 | 0.9589 |
| oos2022 {'entry_ann': 0.12, 'exit_ann': 0.0} | 0.0408 | 0.0008 | 0.0408 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 408 | 0.0000 | 0 | 0 | 0.0000 | 0.0079 | 0.6584 |
| oos2023 {'entry_ann': 0.12, 'exit_ann': 0.0} | 0.0370 | -0.0030 | 0.0370 | 0.0067 | 294 | 222 | 18 | 280 | 0.3105 | 4 | 0 | -10 | 0.0826 | 0.9087 |
| oos2024 {'entry_ann': 0.2, 'exit_ann': 0.0} | 0.0706 | 0.0306 | 0.0706 | 0.0031 | 687 | 270 | 123 | 168 | 0.6220 | 4 | 1 | -13 | 0.1296 | 0.9581 |
| oos2025 {'entry_ann': 0.12, 'exit_ann': 0.02} | 0.0408 | 0.0008 | 0.0408 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 408 | 0.0000 | 0 | 0 | 0.0000 | 0.0493 | 0.8384 |
| oos2026 {'entry_ann': 0.12, 'exit_ann': 0.0} | 0.0406 | 0.0008 | 0.0408 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 304 | 0.0000 | 0 | 0 | 0.0000 | 0.0193 | 0.6972 |

walk-forward aggregate: annualized net 0.0684, max DD 0.0535, time in market 0.28, liquidations 5, years [2021, 2022, 2023, 2024, 2025, 2026]

## Reading this

* `annualized_net` is net of fees, slippage, basis drift and liquidation penalties and **includes** T-bill yield on idle cash; `excess_over_tbill_ann` subtracts an all-cash T-bill benchmark — that is the number the venture must beat.
* `always_in` is the no-threshold control; `coinbase_fees` shows what Coinbase Advanced spot tiers do to a small account.
* `worst_basis_shock_bps` is the worst single-interval perp-premium move against the position while held.
* Liquidations > 0 means the 50 % perp collateral (plus idle top-up) was not enough for a rally; raise collateral or cut leverage.
