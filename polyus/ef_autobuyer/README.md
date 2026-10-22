# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-10-22T20:16:52Z.

Rounds watched: 19. Entries: 3. Settled: 3.

Win rate: 3/3 = 100.0%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.850 | $+25.35 | +16.90% |
| $100 | 100% | 100% | 0.850 | $+50.70 | +16.90% |
| $250 | 100% | 100% | 0.850 | $+126.75 | +16.90% |

Live $100 fill price minus the backtest's display price: -2.33c average over 3 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 10-22T16:30 | 12:00 | Down | 0.81 | 1466 | 100% @ 0.810 | WIN | +22.14 |
| 10-22T16:45 | 12:00 | Down | 0.91 | 2029 | 100% @ 0.910 | WIN | +9.26 |
| 10-22T17:15 | 12:00 | Up | 0.83 | 1478 | 100% @ 0.830 | WIN | +19.30 |

Book reads: 37, failed: 4, median latency 0.08s.
