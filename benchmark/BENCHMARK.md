# Bot Benchmark — Polymarket US BTC 15-minute, recorded books

Generated 2026-11-08 09:13 UTC. Windows recorded: 747; usable (settled, book coverage >= 50%): 691. Size per trade: 10 contracts or the displayed quantity, whichever is smaller. Fees: Polymarket US taker schedule in effect on the trade date. Paper fills at displayed depth; real fills can be worse.

| Rule | Trades | Win rate | Net per trade | Net per $ staked | Fees paid | Worst losing run | Book coverage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Retail rule: buy a side at 45¢ or less, sell at 70¢ (hold to settlement otherwise) | 691 | 48% | $-0.315 | -9.0% | $160.16 | 7 | 84% |
| Turbine reference bot: buy the side the live price favours vs. the strike (10 bps threshold, confidence-priced limits) | 51 | 71% | $+4.658 | +26.1% | $26.67 | 2 | 90% |
| AstroTick, fee-aware favorite (last 120 s) | 4 | 100% | $+2.683 | +37.3% | $0.47 | 0 | 84% |
| Control: buy Up at the open, hold | 250 | 42% | $-1.028 | -20.9% | $43.43 | 10 | 94% |

- **Retail rule: buy a side at 45¢ or less, sell at 70¢ (hold to settlement otherwise)**: A rule circulated in bot tutorials and vendor marketing for BTC 15-minute markets; it is not any one vendor's product (Turbine, where we first saw it quoted, is a bot-builder platform, not a fixed-rule bot). If 70¢ is never bid, the position is held to settlement.
- **Turbine reference bot: buy the side the live price favours vs. the strike (10 bps threshold, confidence-priced limits)**: The 'price action bot' in Turbine's turbine-py-client docs, as documented there: 10 bps threshold, confidence 0.6 to 0.9 scaled with distance from the strike and used as the limit price, buy repeatedly up to a per-market maximum, stop with 60 s left, hold to settlement. Documented on Pyth prices; replayed on the CF Benchmarks prints the market settles on. A reference implementation, not a product the vendor sells as a strategy.
- **AstroTick, fee-aware favorite (last 120 s)**: Rule as summarised on the project README: favoured side by the running settlement average, offered at or below 90¢, margin >= 5 bps, positive fee-adjusted edge.
- **Control: buy Up at the open, hold**: Baseline, not a product.
