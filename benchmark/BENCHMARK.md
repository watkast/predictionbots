# Bot Benchmark — Polymarket US BTC 15-minute, recorded books

Generated 2026-11-08 08:37 UTC. Windows recorded: 745; usable (settled, book coverage >= 50%): 689. Size per trade: 10 contracts or the displayed quantity, whichever is smaller. Fees: Polymarket US taker schedule in effect on the trade date. Paper fills at displayed depth; real fills can be worse.

| Rule | Trades | Win rate | Net per trade | Net per $ staked | Fees paid | Worst losing run | Book coverage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Turbine, standard rule (buy 45¢, sell 70¢) | 689 | 48% | $-0.317 | -9.0% | $159.66 | 7 | 84% |
| AstroTick, fee-aware favorite (last 120 s) | 4 | 100% | $+2.683 | +37.3% | $0.47 | 0 | 84% |
| Control: buy Up at the open, hold | 248 | 42% | $-1.032 | -21.0% | $42.95 | 10 | 94% |

- **Turbine, standard rule (buy 45¢, sell 70¢)**: If 70¢ is never bid, the position is held to settlement (the vendor's page does not say).
- **AstroTick, fee-aware favorite (last 120 s)**: Rule as summarised on the project README: favoured side by the running settlement average, offered at or below 90¢, margin >= 5 bps, positive fee-adjusted edge.
- **Control: buy Up at the open, hold**: Baseline, not a product.
