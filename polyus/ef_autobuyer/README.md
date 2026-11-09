# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-11-09T22:34:23Z.

Rounds watched: 1496. Entries: 167. Settled: 166.

Win rate: 135/166 = 81.3%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 99% | 100% | 0.842 | $-394.12 | -4.77% |
| $100 | 98% | 99% | 0.842 | $-786.67 | -4.79% |
| $250 | 90% | 96% | 0.844 | $-1,974.47 | -4.97% |

Live $100 fill price minus the backtest's display price: +0.91c average over 163 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 11-06T12:30 | 12:00 | Down | 0.83 | 1465 | 100% @ 0.830 | WIN | +19.30 |
| 11-06T15:30 | 13:00 | Down | 0.80 | 81 | 100% @ 0.803 | LOSS | -101.37 |
| 11-06T22:00 | 12:00 | Up | 0.86 | 84 | 100% @ 0.863 | WIN | +14.60 |
| 11-06T22:45 | 12:00 | Down | 0.84 | 1 | 86% @ 0.850 | WIN | +14.04 |
| 11-07T09:30 | 12:00 | Down | 0.81 | 178 | 100% @ 0.810 | WIN | +21.65 |
| 11-07T16:45 | 12:00 | Down | 0.80 | 63 | 100% @ 0.805 | WIN | +22.38 |
| 11-07T22:30 | 13:00 | Up | 0.80 | 275 | 100% @ 0.800 | WIN | +23.10 |
| 11-08T03:00 | 12:00 | Up | 0.80 | 181 | 100% @ 0.800 | WIN | +23.10 |
| 11-08T04:45 | 12:00 | Down | 0.83 | 168 | 100% @ 0.830 | WIN | +18.87 |
| 11-08T10:30 | 13:00 | Down | 0.80 | 61 | 100% @ 0.805 | LOSS | -101.85 |
| 11-08T22:00 | 13:00 | Up | 0.83 | 44 | 100% @ 0.836 | WIN | +18.02 |
| 11-09T00:00 | 12:00 | Down | 0.80 | 1196 | 100% @ 0.800 | WIN | +23.10 |
| 11-09T00:15 | 13:00 | Up | 0.90 | 307 | 100% @ 0.900 | WIN | +10.16 |
| 11-09T05:00 | 12:00 | Down | 0.86 | 95 | 100% @ 0.862 | WIN | +14.72 |
| 11-09T07:00 | 12:00 | Down | 0.88 | 114 | 100% @ 0.880 | WIN | +12.50 |
| 11-09T09:00 | 12:00 | Up | 0.82 | 21 | 100% @ 0.828 | LOSS | -101.64 |
| 11-09T10:30 | 12:00 | Down | 0.80 | 1495 | 100% @ 0.800 | WIN | +23.10 |
| 11-09T14:00 | 12:00 | Down | 0.84 | 719 | 100% @ 0.840 | WIN | +17.53 |
| 11-09T20:30 | 12:00 | Down | 0.85 | 836 | 100% @ 0.850 | WIN | +16.22 |
| 11-09T22:30 | 12:00 | Up | 0.80 | 100 | 100% @ 0.802 | - | +0.00 |

Book reads: 2934, failed: 898, re-tried: 955, median latency 0.04s.
Entries read more than 20 s after their target second: 19 of 167 (avg 32 s late).
