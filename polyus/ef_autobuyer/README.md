# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-11-08T15:47:06Z.

Rounds watched: 1399. Entries: 157. Settled: 157.

Win rate: 127/157 = 80.9%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 99% | 100% | 0.842 | $-411.34 | -5.26% |
| $100 | 97% | 99% | 0.842 | $-820.38 | -5.28% |
| $250 | 89% | 95% | 0.844 | $-2,054.75 | -5.48% |

Live $100 fill price minus the backtest's display price: +0.92c average over 155 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 11-05T06:15 | 12:00 | Up | 0.80 | 74 | 100% @ 0.804 | WIN | +23.00 |
| 11-05T06:45 | 13:00 | Up | 0.82 | 1024 | 100% @ 0.820 | WIN | +20.70 |
| 11-05T07:30 | 13:00 | Down | 0.87 | 1089 | 100% @ 0.870 | WIN | +14.04 |
| 11-05T09:00 | 13:00 | Down | 0.80 | 553 | 100% @ 0.800 | WIN | +23.61 |
| 11-05T13:45 | 12:00 | Up | 0.81 | 643 | 100% @ 0.810 | LOSS | -101.32 |
| 11-05T15:00 | 12:00 | Down | 0.82 | 68 | 100% @ 0.824 | WIN | +20.08 |
| 11-05T15:15 | 13:00 | Up | 0.90 | 1981 | 100% @ 0.900 | LOSS | -100.69 |
| 11-05T19:15 | 12:00 | Up | 0.83 | 133 | 100% @ 0.830 | LOSS | -101.18 |
| 11-05T23:00 | 13:00 | Down | 0.83 | 22 | 100% @ 0.838 | WIN | +18.19 |
| 11-06T05:30 | 12:00 | Down | 0.80 | 308 | 100% @ 0.800 | LOSS | -101.39 |
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

Book reads: 2742, failed: 833, re-tried: 875, median latency 0.04s.
Entries read more than 20 s after their target second: 18 of 157 (avg 31 s late).
