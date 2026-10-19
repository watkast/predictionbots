# Carry backtest (long spot + short perp)

generated 2026-10-19T08:59:08.366054+00:00  synthetic=False

Funding/candles are **Binance proxies** for the US perps (Coinbase `BIP-20DEC30-CDE`, Kraken Derivatives US `PBTCUC`); fees from `pb/carry/venues.py`. `oos<year>` rows pick thresholds on the prior year and score the named year; they are the ones that count.

## BTC
7395 funding intervals, 2020-01-01 .. 2026-09-30

| name | annualized_net | excess_over_tbill_ann | cagr | max_drawdown_frac | funding_captured | costs | basis_pnl | idle_yield | time_in_market | n_trades | liquidations | worst_basis_shock_bps | mean_ann_funding | frac_intervals_positive |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | -0.0297 | -0.0746 | -0.0326 | 0.3260 | 4,181 | 7,266 | 85 | 992 | 0.6116 | 151 | 3 | -277 | 0.1172 | 0.8599 |
| maker_spot | 0.0233 | -0.0216 | 0.0219 | 0.0982 | 4,190 | 4,163 | 118 | 1,428 | 0.6118 | 150 | 2 | -277 | 0.1172 | 0.8599 |
| coinbase_fees | -0.1439 | -0.1888 | -0.4095 | 1.0053 | 4,182 | 14,669 | 323 | 450 | 0.6116 | 151 | 3 | -277 | 0.1172 | 0.8599 |
| no_tbill | -0.0443 | -0.0443 | -0.0512 | 0.4131 | 4,181 | 7,265 | 95 | 0.0000 | 0.6116 | 151 | 3 | -277 | 0.1172 | 0.8599 |
| always_in | 0.0665 | 0.0216 | 0.0565 | 0.0429 | 4,395 | 523 | -73 | 694 | 0.9986 | 6 | 4 | -283 | 0.1172 | 0.8599 |
| oos2021 {'entry_ann': 0.12, 'exit_ann': 0.0} | 0.1476 | 0.1076 | 0.1476 | 0.0129 | 1,608 | 280 | -19 | 167 | 0.6813 | 5 | 1 | -48 | 0.3061 | 0.9269 |
| oos2022 {'entry_ann': 0.2, 'exit_ann': 0.0} | 0.0408 | 0.0008 | 0.0408 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 408 | 0.0000 | 0 | 0 | 0.0000 | 0.0416 | 0.7790 |
| oos2023 {'entry_ann': 0.12, 'exit_ann': 0.0} | 0.0371 | -0.0029 | 0.0371 | 0.0039 | 214 | 147 | 11 | 293 | 0.2831 | 3 | 0 | -18 | 0.0787 | 0.8986 |
| oos2024 {'entry_ann': 0.12, 'exit_ann': 0.02} | 0.0596 | 0.0196 | 0.0596 | 0.0033 | 545 | 154 | 24 | 183 | 0.5792 | 3 | 0 | -20 | 0.1192 | 0.9162 |
| oos2025 {'entry_ann': 0.2, 'exit_ann': 0.0} | 0.0408 | 0.0008 | 0.0408 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 408 | 0.0000 | 0 | 0 | 0.0000 | 0.0513 | 0.8712 |
| oos2026 {'entry_ann': 0.12, 'exit_ann': 0.0} | 0.0406 | 0.0008 | 0.0408 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 304 | 0.0000 | 0 | 0 | 0.0000 | 0.0294 | 0.7399 |

walk-forward aggregate: annualized net 0.0620, max DD 0.0129, time in market 0.27, liquidations 1, years [2021, 2022, 2023, 2024, 2025, 2026]

## ETH
7395 funding intervals, 2020-01-01 .. 2026-09-30

| name | annualized_net | excess_over_tbill_ann | cagr | max_drawdown_frac | funding_captured | costs | basis_pnl | idle_yield | time_in_market | n_trades | liquidations | worst_basis_shock_bps | mean_ann_funding | frac_intervals_positive |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | -0.0512 | -0.0961 | -0.0609 | 0.4128 | 4,986 | 7,679 | -1,571 | 806 | 0.6314 | 155 | 8 | -98 | 0.1384 | 0.8622 |
| maker_spot | 0.0020 | -0.0429 | 0.0020 | 0.1209 | 4,994 | 4,469 | -1,473 | 1,084 | 0.6315 | 154 | 7 | -98 | 0.1384 | 0.8622 |
| coinbase_fees | -0.1704 | -0.2153 | -1.0000 | 1.1545 | 4,979 | 16,942 | 173 | 283 | 0.6314 | 155 | 8 | -97 | 0.1384 | 0.8622 |
| no_tbill | -0.0567 | -0.0567 | -0.0690 | 0.4524 | 4,983 | 7,591 | -1,221 | 0.0000 | 0.6315 | 154 | 7 | -95 | 0.1384 | 0.8622 |
| always_in | 0.0709 | 0.0260 | 0.0597 | 0.0455 | 5,172 | 926 | -283 | 826 | 0.9973 | 11 | 7 | -147 | 0.1384 | 0.8622 |
| oos2021 {'entry_ann': 0.05, 'exit_ann': 0.0} | 0.0916 | 0.0516 | 0.0916 | 0.0512 | 2,057 | 1,109 | -95 | 63 | 0.9269 | 21 | 2 | -57 | 0.3754 | 0.9589 |
| oos2022 {'entry_ann': 0.12, 'exit_ann': 0.0} | 0.0408 | 0.0008 | 0.0408 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 408 | 0.0000 | 0 | 0 | 0.0000 | 0.0079 | 0.6584 |
| oos2023 {'entry_ann': 0.12, 'exit_ann': 0.0} | 0.0355 | -0.0045 | 0.0355 | 0.0053 | 245 | 185 | 15 | 281 | 0.3105 | 4 | 0 | -10 | 0.0826 | 0.9087 |
| oos2024 {'entry_ann': 0.2, 'exit_ann': 0.0} | 0.0618 | 0.0218 | 0.0618 | 0.0031 | 576 | 141 | 20 | 165 | 0.6230 | 3 | 0 | -21 | 0.1296 | 0.9581 |
| oos2025 {'entry_ann': 0.12, 'exit_ann': 0.02} | 0.0408 | 0.0008 | 0.0408 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 408 | 0.0000 | 0 | 0 | 0.0000 | 0.0493 | 0.8384 |
| oos2026 {'entry_ann': 0.12, 'exit_ann': 0.0} | 0.0406 | 0.0008 | 0.0408 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 304 | 0.0000 | 0 | 0 | 0.0000 | 0.0193 | 0.6972 |

walk-forward aggregate: annualized net 0.0524, max DD 0.0512, time in market 0.32, liquidations 2, years [2021, 2022, 2023, 2024, 2025, 2026]

## Reading this

* `annualized_net` is net of fees, slippage, basis drift and liquidation penalties and **includes** T-bill yield on idle cash; `excess_over_tbill_ann` subtracts an all-cash T-bill benchmark — that is the number the venture must beat.
* `always_in` is the no-threshold control; `coinbase_fees` shows what Coinbase Advanced spot tiers do to a small account.
* `worst_basis_shock_bps` is the worst single-interval perp-premium move against the position while held.
* Liquidations > 0 means the 50 % perp collateral (plus idle top-up) was not enough for a rally; raise collateral or cut leverage.
