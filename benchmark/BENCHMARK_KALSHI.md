# Bot Benchmark — Kalshi BTC 15-minute, recorded books

Generated 2026-11-27 19:19 UTC. Windows recorded: 2429; usable (settled, book coverage >= 50%): 2406. Size per trade: 10 contracts or the displayed quantity, whichever is smaller. Fees: Kalshi taker schedule (7%, rounded up). Paper fills at displayed depth; real fills can be worse.

| Rule | Trades | Win rate | Net per trade | Net per $ staked (95% interval) | Fees paid | Worst losing run | Book coverage | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Retail rule: buy a side at 45¢ or less, sell at 70¢ (hold to settlement otherwise) | 2406 | 52% | $-0.312 | -8.2% (-12% to -5%) | $579.73 | 14 | 94% | loses |
| Turbine reference bot: buy the side the live price favours vs. the strike (10 bps threshold, confidence-priced limits) | 479 | 58% | $+0.550 | +2.4% (-3% to +12%) | $336.61 | 9 | 95% | inconclusive |
| AstroTick, fee-aware favorite (last 120 s) | 11 | 100% | $+1.236 | +15.9% (-1% to +22%) | $0.91 | 0 | 92% | inconclusive |
| Control: buy Up at the open, hold | 1317 | 46% | $-0.605 | -12.0% (-19% to -8%) | $224.67 | 9 | 96% | loses |

- **Retail rule: buy a side at 45¢ or less, sell at 70¢ (hold to settlement otherwise)**: A rule circulated in bot tutorials and vendor marketing for BTC 15-minute markets; it is not any one vendor's product (Turbine, where we first saw it quoted, is a bot-builder platform, not a fixed-rule bot). If 70¢ is never bid, the position is held to settlement.
- **Turbine reference bot: buy the side the live price favours vs. the strike (10 bps threshold, confidence-priced limits)**: The 'price action bot' in Turbine's turbine-py-client docs, as documented there: 10 bps threshold, confidence 0.6 to 0.9 scaled with distance from the strike and used as the limit price, buy repeatedly up to a per-market maximum, stop with 60 s left, hold to settlement. Documented on Pyth prices; replayed on the CF Benchmarks prints the market settles on. A reference implementation, not a product the vendor sells as a strategy.
- **AstroTick, fee-aware favorite (last 120 s)**: Rule as summarised on the project README: favoured side by the running settlement average, offered at or below 90¢, margin >= 5 bps, positive fee-adjusted edge.
- **Control: buy Up at the open, hold**: Baseline, not a product.
