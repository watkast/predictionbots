# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-11-01T05:55:31Z.

Rounds watched: 783. Entries: 99. Settled: 98.

Win rate: 82/98 = 83.7%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.844 | $-89.78 | -1.83% |
| $100 | 100% | 100% | 0.844 | $-182.02 | -1.86% |
| $250 | 96% | 99% | 0.845 | $-511.01 | -2.11% |

Live $100 fill price minus the backtest's display price: +1.06c average over 92 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 10-30T14:00 | 12:00 | Down | 0.81 | 1001 | 100% @ 0.810 | WIN | +22.14 |
| 10-30T15:15 | 12:00 | Up | 0.87 | 662 | 100% @ 0.870 | LOSS | -100.90 |
| 10-30T15:45 | 12:00 | Down | 0.90 | 1795 | 100% @ 0.900 | LOSS | -100.69 |
| 10-30T18:15 | 12:00 | Down | 0.82 | 705 | 100% @ 0.820 | WIN | +20.70 |
| 10-30T20:00 | 12:00 | Up | 0.80 | 185 | 100% @ 0.800 | WIN | +23.61 |
| 10-30T22:00 | 12:00 | Up | 0.87 | 226 | 100% @ 0.870 | WIN | +14.04 |
| 10-31T04:00 | 13:00 | Up | 0.83 | 354 | 100% @ 0.830 | WIN | +19.30 |
| 10-31T06:00 | 12:00 | Up | 0.86 | 508 | 100% @ 0.860 | WIN | +15.31 |
| 10-31T06:45 | 12:00 | Up | 0.89 | 5 | 100% @ 0.899 | WIN | +10.47 |
| 10-31T10:00 | 12:00 | Down | 0.81 | 354 | 100% @ 0.810 | LOSS | -101.32 |
| 10-31T11:15 | 13:00 | Up | 0.80 | 323 | 100% @ 0.800 | WIN | +23.61 |
| 10-31T19:15 | 12:00 | Down | 0.80 | 304 | 100% @ 0.800 | WIN | +23.61 |
| 10-31T19:45 | 13:00 | Down | 0.83 | 418 | 100% @ 0.830 | WIN | +19.30 |
| 10-31T20:00 | 12:00 | Up | 0.85 | 138 | 100% @ 0.850 | WIN | +16.60 |
| 11-01T00:00 | 13:00 | Down | 0.81 | 294 | 100% @ 0.810 | WIN | +22.14 |
| 11-01T02:45 | 12:00 | Up | 0.86 | 243 | 100% @ 0.860 | WIN | +15.31 |
| 11-01T04:00 | 12:00 | Down | 0.82 | 2121 | 100% @ 0.820 | WIN | +20.70 |
| 11-01T05:00 | 12:00 | Up | 0.80 | 788 | 100% @ 0.800 | WIN | +23.61 |
| 11-01T05:30 | 12:00 | Up | 0.87 | 157 | 100% @ 0.870 | LOSS | -100.90 |
| 11-01T05:45 | 13:00 | Up | 0.84 | 60 | 50% @ 0.840 | - | +0.00 |

Book reads: 1534, failed: 459, re-tried: 401, median latency 0.04s.
Entries read more than 20 s after their target second: 12 of 99 (avg 29 s late).
