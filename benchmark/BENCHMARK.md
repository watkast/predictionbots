# Bot Benchmark — Polymarket US BTC 15-minute, recorded books

Generated 2026-11-08 08:50 UTC. Windows recorded: 746; usable (settled, book coverage >= 50%): 690. Size per trade: 10 contracts or the displayed quantity, whichever is smaller. Fees: Polymarket US taker schedule in effect on the trade date. Paper fills at displayed depth; real fills can be worse.

| Rule | Trades | Win rate | Net per trade | Net per $ staked | Fees paid | Worst losing run | Book coverage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Retail rule: buy a side at 45¢ or less, sell at 70¢ (hold to settlement otherwise) | 690 | 48% | $-0.319 | -9.1% | $159.75 | 7 | 84% |
| AstroTick, fee-aware favorite (last 120 s) | 4 | 100% | $+2.683 | +37.3% | $0.47 | 0 | 84% |
| Control: buy Up at the open, hold | 249 | 42% | $-1.050 | -21.4% | $43.19 | 10 | 94% |

- **Retail rule: buy a side at 45¢ or less, sell at 70¢ (hold to settlement otherwise)**: A rule circulated in bot tutorials and vendor marketing for BTC 15-minute markets; it is not any one vendor's product (Turbine, where we first saw it quoted, is a bot-builder platform, not a fixed-rule bot). If 70¢ is never bid, the position is held to settlement.
- **AstroTick, fee-aware favorite (last 120 s)**: Rule as summarised on the project README: favoured side by the running settlement average, offered at or below 90¢, margin >= 5 bps, positive fee-adjusted edge.
- **Control: buy Up at the open, hold**: Baseline, not a product.
