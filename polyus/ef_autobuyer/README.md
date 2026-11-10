# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-11-10T14:46:23Z.

Rounds watched: 1545. Entries: 175. Settled: 175.

Win rate: 141/175 = 80.6%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 99% | 99% | 0.842 | $-499.37 | -5.76% |
| $100 | 97% | 98% | 0.842 | $-998.25 | -5.79% |
| $250 | 90% | 95% | 0.843 | $-2,508.26 | -6.01% |

Live $100 fill price minus the backtest's display price: +0.89c average over 168 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
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
| 11-09T22:30 | 12:00 | Up | 0.80 | 100 | 100% @ 0.802 | WIN | +22.81 |
| 11-09T23:15 | 12:00 | Up | 0.83 | 5 | 4% @ 0.830 | WIN | +0.78 |
| 11-10T03:45 | 12:00 | Up | 0.85 | 1436 | 100% @ 0.850 | WIN | +16.22 |
| 11-10T07:45 | 13:00 | Up | 0.80 | 1532 | 100% @ 0.800 | LOSS | -101.90 |
| 11-10T11:30 | 12:00 | Down | 0.86 | 1073 | 100% @ 0.860 | LOSS | -101.33 |
| 11-10T13:00 | 12:00 | Down | 0.88 | 863 | 100% @ 0.880 | LOSS | -101.14 |
| 11-10T13:15 | 13:00 | Down | 0.88 | 1522 | 100% @ 0.880 | WIN | +12.50 |
| 11-10T13:30 | 13:00 | Down | 0.82 | 367 | 100% @ 0.820 | WIN | +20.24 |
| 11-10T14:15 | 12:00 | Down | 0.82 | 134 | 100% @ 0.820 | WIN | +20.24 |

Book reads: 3029, failed: 918, re-tried: 979, median latency 0.04s.
Entries read more than 20 s after their target second: 20 of 175 (avg 32 s late).
