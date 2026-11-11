# Bot Benchmark — Polymarket US BTC 15-minute, recorded books

Generated 2026-11-11 17:39 UTC. Windows recorded: 1015; usable (settled, book coverage >= 50%): 934. Size per trade: 10 contracts or the displayed quantity, whichever is smaller. Fees: Polymarket US taker schedule in effect on the trade date. Paper fills at displayed depth; real fills can be worse.

| Rule | Trades | Win rate | Net per trade | Net per $ staked (95% interval) | Fees paid | Worst losing run | Book coverage | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Retail rule: buy a side at 45¢ or less, sell at 70¢ (hold to settlement otherwise) | 934 | 47% | $-0.379 | -10.8% (-21% to -7%) | $229.30 | 7 | 84% | loses |
| Turbine reference bot: buy the side the live price favours vs. the strike (10 bps threshold, confidence-priced limits) | 61 | 69% | $+1.711 | +7.6% (-5% to +33%) | $43.46 | 2 | 90% | inconclusive |
| AstroTick, fee-aware favorite (last 120 s) | 6 | 100% | $+2.533 | +34.5% (+8% to +79%) | $0.80 | 0 | 82% | inconclusive |
| Control: buy Up at the open, hold | 383 | 44% | $-0.837 | -17.5% (-27% to -6%) | $71.42 | 10 | 94% | loses |

- **Retail rule: buy a side at 45¢ or less, sell at 70¢ (hold to settlement otherwise)**: A rule circulated in bot tutorials and vendor marketing for BTC 15-minute markets; it is not any one vendor's product (Turbine, where we first saw it quoted, is a bot-builder platform, not a fixed-rule bot). If 70¢ is never bid, the position is held to settlement.
- **Turbine reference bot: buy the side the live price favours vs. the strike (10 bps threshold, confidence-priced limits)**: The 'price action bot' in Turbine's turbine-py-client docs, as documented there: 10 bps threshold, confidence 0.6 to 0.9 scaled with distance from the strike and used as the limit price, buy repeatedly up to a per-market maximum, stop with 60 s left, hold to settlement. Documented on Pyth prices; replayed on the CF Benchmarks prints the market settles on. A reference implementation, not a product the vendor sells as a strategy.
- **AstroTick, fee-aware favorite (last 120 s)**: Rule as summarised on the project README: favoured side by the running settlement average, offered at or below 90¢, margin >= 5 bps, positive fee-adjusted edge.
- **Control: buy Up at the open, hold**: Baseline, not a product.
