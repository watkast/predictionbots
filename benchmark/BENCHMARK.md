# Bot Benchmark — Polymarket US BTC 15-minute, recorded books

Generated 2026-11-13 16:15 UTC. Windows recorded: 1176; usable (settled, book coverage >= 50%): 1081. Size per trade: 10 contracts or the displayed quantity, whichever is smaller. Fees: Polymarket US taker schedule in effect on the trade date. Paper fills at displayed depth; real fills can be worse.

| Rule | Trades | Win rate | Net per trade | Net per $ staked (95% interval) | Fees paid | Worst losing run | Book coverage | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Retail rule: buy a side at 45¢ or less, sell at 70¢ (hold to settlement otherwise) | 1081 | 48% | $-0.375 | -10.7% (-20% to -7%) | $273.18 | 7 | 85% | loses |
| Turbine reference bot: buy the side the live price favours vs. the strike (10 bps threshold, confidence-priced limits) | 82 | 66% | $+1.359 | +6.0% (-7% to +26%) | $62.14 | 4 | 91% | inconclusive |
| AstroTick, fee-aware favorite (last 120 s) | 8 | 100% | $+2.140 | +27.7% (+7% to +63%) | $0.98 | 0 | 85% | inconclusive |
| Control: buy Up at the open, hold | 474 | 44% | $-0.801 | -16.9% (-26% to -8%) | $90.71 | 10 | 94% | loses |

- **Retail rule: buy a side at 45¢ or less, sell at 70¢ (hold to settlement otherwise)**: A rule circulated in bot tutorials and vendor marketing for BTC 15-minute markets; it is not any one vendor's product (Turbine, where we first saw it quoted, is a bot-builder platform, not a fixed-rule bot). If 70¢ is never bid, the position is held to settlement.
- **Turbine reference bot: buy the side the live price favours vs. the strike (10 bps threshold, confidence-priced limits)**: The 'price action bot' in Turbine's turbine-py-client docs, as documented there: 10 bps threshold, confidence 0.6 to 0.9 scaled with distance from the strike and used as the limit price, buy repeatedly up to a per-market maximum, stop with 60 s left, hold to settlement. Documented on Pyth prices; replayed on the CF Benchmarks prints the market settles on. A reference implementation, not a product the vendor sells as a strategy.
- **AstroTick, fee-aware favorite (last 120 s)**: Rule as summarised on the project README: favoured side by the running settlement average, offered at or below 90¢, margin >= 5 bps, positive fee-adjusted edge.
- **Control: buy Up at the open, hold**: Baseline, not a product.
