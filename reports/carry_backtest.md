# Carry backtest (long spot + short perp)

generated 2026-10-17T06:58:22.839921+00:00  synthetic=False

Funding/candles are **Binance proxies** for the US perps (Coinbase `BIP-20DEC30-CDE`, Kraken Derivatives US `PBTCUC`); fees from `pb/carry/venues.py`. `oos<year>` rows pick thresholds on the prior year and score the named year; they are the ones that count.

## BTC
no data under /home/runner/work/predictionbots/predictionbots/data/carry for BTC

## ETH
no data under /home/runner/work/predictionbots/predictionbots/data/carry for ETH

## Reading this

* `annualized_net` is net of fees, slippage, basis drift and liquidation penalties and **includes** T-bill yield on idle cash; `excess_over_tbill_ann` subtracts an all-cash T-bill benchmark — that is the number the venture must beat.
* `always_in` is the no-threshold control; `coinbase_fees` shows what Coinbase Advanced spot tiers do to a small account.
* `worst_basis_shock_bps` is the worst single-interval perp-premium move against the position while held.
* Liquidations > 0 means the 50 % perp collateral (plus idle top-up) was not enough for a rally; raise collateral or cut leverage.
