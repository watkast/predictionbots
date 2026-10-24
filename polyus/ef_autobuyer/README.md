# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-10-24T20:19:00Z.

Rounds watched: 208. Entries: 19. Settled: 19.

Win rate: 16/19 = 84.2%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.841 | $-4.03 | -0.42% |
| $100 | 100% | 100% | 0.841 | $-8.31 | -0.44% |
| $250 | 100% | 100% | 0.842 | $-22.13 | -0.47% |

Live $100 fill price minus the backtest's display price: -1.22c average over 18 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 10-22T16:30 | 12:00 | Down | 0.81 | 1466 | 100% @ 0.810 | WIN | +22.14 |
| 10-22T16:45 | 12:00 | Down | 0.91 | 2029 | 100% @ 0.910 | WIN | +9.26 |
| 10-22T17:15 | 12:00 | Up | 0.83 | 1478 | 100% @ 0.830 | WIN | +19.30 |
| 10-22T21:15 | 12:00 | Up | 0.84 | 200 | 100% @ 0.840 | WIN | +17.94 |
| 10-23T01:45 | 12:00 | Up | 0.90 | 1711 | 100% @ 0.900 | LOSS | -100.69 |
| 10-23T03:15 | 12:00 | Down | 0.84 | 4032 | 100% @ 0.840 | WIN | +17.94 |
| 10-23T07:00 | 12:00 | Down | 0.80 | 683 | 100% @ 0.800 | WIN | +23.61 |
| 10-23T08:15 | 12:00 | Up | 0.85 | 1021 | 100% @ 0.850 | WIN | +16.60 |
| 10-23T11:00 | 12:00 | Down | 0.82 | 1853 | 100% @ 0.820 | WIN | +20.70 |
| 10-23T16:30 | 13:00 | Up | 0.80 | 3653 | 100% @ 0.800 | WIN | +23.61 |
| 10-23T18:45 | 12:00 | Down | 0.80 | 6585 | 100% @ 0.800 | WIN | +23.61 |
| 10-23T22:30 | 13:00 | Down | 0.87 | 1442 | 100% @ 0.870 | WIN | +14.04 |
| 10-23T23:45 | 12:00 | Up | 0.83 | 1416 | 100% @ 0.830 | WIN | +19.30 |
| 10-24T03:00 | 12:00 | Up | 0.85 | 20 | 100% @ 0.858 | LOSS | -100.99 |
| 10-24T04:00 | 12:00 | Up | 0.81 | 100 | 100% @ 0.812 | LOSS | -101.31 |
| 10-24T12:15 | 12:00 | Up | 0.82 | 4245 | 100% @ 0.820 | WIN | +20.70 |
| 10-24T13:30 | 12:00 | Down | 0.82 | 821 | 100% @ 0.820 | WIN | +20.70 |
| 10-24T14:15 | 13:00 | Down | 0.93 | 3565 | 100% @ 0.930 | WIN | +7.04 |
| 10-24T20:00 | 12:00 | Up | 0.83 | 23 | 100% @ 0.838 | WIN | +18.19 |

Book reads: 412, failed: 146, median latency 0.04s.
