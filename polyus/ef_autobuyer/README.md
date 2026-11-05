# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-11-05T07:19:01Z.

Rounds watched: 1116. Entries: 139. Settled: 139.

Win rate: 115/139 = 82.7%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 99% | 100% | 0.844 | $-225.95 | -3.27% |
| $100 | 98% | 99% | 0.844 | $-445.54 | -3.24% |
| $250 | 91% | 96% | 0.846 | $-1,009.54 | -3.01% |

Live $100 fill price minus the backtest's display price: +1.18c average over 136 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 11-02T23:00 | 13:00 | Down | 0.91 | 87 | 100% @ 0.912 | WIN | +9.03 |
| 11-03T00:15 | 13:00 | Up | 0.82 | 119 | 100% @ 0.820 | WIN | +20.67 |
| 11-03T03:45 | 12:00 | Up | 0.93 | 1351 | 100% @ 0.930 | WIN | +7.04 |
| 11-03T04:30 | 12:00 | Down | 0.82 | 9 | 100% @ 0.829 | WIN | +19.40 |
| 11-03T06:15 | 12:00 | Up | 0.86 | 207 | 100% @ 0.860 | WIN | +15.31 |
| 11-03T06:45 | 12:00 | Down | 0.83 | 582 | 100% @ 0.830 | WIN | +19.30 |
| 11-03T12:00 | 13:00 | Down | 0.84 | 638 | 100% @ 0.840 | LOSS | -101.11 |
| 11-03T13:30 | 13:00 | Up | 0.82 | 5 | 16% @ 0.827 | WIN | +3.09 |
| 11-03T14:00 | 12:00 | Down | 0.82 | 1388 | 100% @ 0.820 | WIN | +20.70 |
| 11-03T21:45 | 12:00 | Down | 0.82 | 1475 | 100% @ 0.820 | WIN | +20.70 |
| 11-04T03:00 | 12:00 | Down | 0.92 | 1092 | 100% @ 0.920 | WIN | +8.14 |
| 11-04T07:30 | 13:00 | Down | 0.81 | 1525 | 100% @ 0.810 | WIN | +22.14 |
| 11-04T09:30 | 12:00 | Up | 0.88 | 1050 | 100% @ 0.880 | WIN | +12.80 |
| 11-04T09:45 | 12:00 | Up | 0.80 | 15 | 78% @ 0.808 | LOSS | -78.66 |
| 11-04T18:00 | 13:00 | Up | 0.89 | 222 | 100% @ 0.890 | WIN | +11.60 |
| 11-04T19:00 | 12:00 | Down | 0.86 | 209 | 100% @ 0.860 | WIN | +15.31 |
| 11-04T23:00 | 13:00 | Down | 0.90 | 40 | 100% @ 0.906 | WIN | +9.68 |
| 11-05T03:45 | 12:00 | Down | 0.87 | 331 | 100% @ 0.870 | WIN | +14.04 |
| 11-05T06:15 | 12:00 | Up | 0.80 | 74 | 100% @ 0.804 | WIN | +23.00 |
| 11-05T06:45 | 13:00 | Up | 0.82 | 1024 | 100% @ 0.820 | WIN | +20.70 |

Book reads: 2183, failed: 651, re-tried: 655, median latency 0.04s.
Entries read more than 20 s after their target second: 18 of 139 (avg 31 s late).
