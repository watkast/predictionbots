# Bot Benchmark — Kalshi BTC 15-minute, recorded books

Generated 2026-11-13 17:35 UTC. Windows recorded: 1104; usable (settled, book coverage >= 50%): 1081. Size per trade: 10 contracts or the displayed quantity, whichever is smaller. Fees: Kalshi taker schedule (7%, rounded up). Paper fills at displayed depth; real fills can be worse.

| Rule | Trades | Win rate | Net per trade | Net per $ staked (95% interval) | Fees paid | Worst losing run | Book coverage | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Retail rule: buy a side at 45¢ or less, sell at 70¢ (hold to settlement otherwise) | 1081 | 51% | $-0.379 | -9.9% (-17% to -5%) | $260.17 | 14 | 94% | loses |
| Turbine reference bot: buy the side the live price favours vs. the strike (10 bps threshold, confidence-priced limits) | 106 | 59% | $+0.392 | +1.9% (-11% to +18%) | $66.80 | 5 | 94% | inconclusive |
| AstroTick, fee-aware favorite (last 120 s) | 2 | 100% | $+1.265 | +14.6% (+11% to +18%) | $0.17 | 0 | 92% | inconclusive |
| Control: buy Up at the open, hold | 533 | 47% | $-0.522 | -10.2% (-21% to -4%) | $91.54 | 7 | 96% | loses |

- **Retail rule: buy a side at 45¢ or less, sell at 70¢ (hold to settlement otherwise)**: A rule circulated in bot tutorials and vendor marketing for BTC 15-minute markets; it is not any one vendor's product (Turbine, where we first saw it quoted, is a bot-builder platform, not a fixed-rule bot). If 70¢ is never bid, the position is held to settlement.
- **Turbine reference bot: buy the side the live price favours vs. the strike (10 bps threshold, confidence-priced limits)**: The 'price action bot' in Turbine's turbine-py-client docs, as documented there: 10 bps threshold, confidence 0.6 to 0.9 scaled with distance from the strike and used as the limit price, buy repeatedly up to a per-market maximum, stop with 60 s left, hold to settlement. Documented on Pyth prices; replayed on the CF Benchmarks prints the market settles on. A reference implementation, not a product the vendor sells as a strategy.
- **AstroTick, fee-aware favorite (last 120 s)**: Rule as summarised on the project README: favoured side by the running settlement average, offered at or below 90¢, margin >= 5 bps, positive fee-adjusted edge.
- **Control: buy Up at the open, hold**: Baseline, not a product.
