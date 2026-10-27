# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-10-27T01:04:27Z.

Rounds watched: 294. Entries: 27. Settled: 27.

Win rate: 22/27 = 81.5%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.841 | $-54.68 | -4.05% |
| $100 | 100% | 100% | 0.841 | $-109.60 | -4.06% |
| $250 | 100% | 100% | 0.842 | $-276.46 | -4.10% |

Live $100 fill price minus the backtest's display price: +1.03c average over 27 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
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
| 10-24T23:30 | 12:00 | Up | 0.88 | 181 | 100% @ 0.880 | WIN | +12.80 |
| 10-25T01:00 | 12:00 | Down | 0.81 | 1886 | 100% @ 0.810 | WIN | +22.14 |
| 10-26T14:30 | 12:00 | Down | 0.80 | 1725 | 100% @ 0.800 | LOSS | -101.39 |
| 10-26T14:45 | 12:00 | Up | 0.81 | 1296 | 100% @ 0.810 | WIN | +22.14 |
| 10-26T20:00 | 13:00 | Down | 0.81 | 3035 | 100% @ 0.810 | WIN | +22.14 |
| 10-26T20:30 | 12:00 | Up | 0.83 | 2465 | 100% @ 0.830 | LOSS | -101.18 |
| 10-26T21:00 | 12:00 | Up | 0.91 | 652 | 100% @ 0.910 | WIN | +9.26 |
| 10-26T23:00 | 12:00 | Down | 0.88 | 1836 | 100% @ 0.880 | WIN | +12.80 |

Book reads: 583, failed: 198, re-tried: 54, median latency 0.04s.
Entries read more than 20 s after their target second: 3 of 27 (avg 32 s late).
