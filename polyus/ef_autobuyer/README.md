# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-11-12T02:39:09Z.

Rounds watched: 1659. Entries: 189. Settled: 189.

Win rate: 153/189 = 81.0%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 99% | 99% | 0.841 | $-488.22 | -5.21% |
| $100 | 97% | 99% | 0.841 | $-977.71 | -5.25% |
| $250 | 90% | 96% | 0.843 | $-2,464.07 | -5.45% |

Live $100 fill price minus the backtest's display price: +0.66c average over 184 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
| 11-10T07:45 | 13:00 | Up | 0.80 | 1532 | 100% @ 0.800 | LOSS | -101.90 |
| 11-10T11:30 | 12:00 | Down | 0.86 | 1073 | 100% @ 0.860 | LOSS | -101.33 |
| 11-10T13:00 | 12:00 | Down | 0.88 | 863 | 100% @ 0.880 | LOSS | -101.14 |
| 11-10T13:15 | 13:00 | Down | 0.88 | 1522 | 100% @ 0.880 | WIN | +12.50 |
| 11-10T13:30 | 13:00 | Down | 0.82 | 367 | 100% @ 0.820 | WIN | +20.24 |
| 11-10T14:15 | 12:00 | Down | 0.82 | 134 | 100% @ 0.820 | WIN | +20.24 |
| 11-10T15:00 | 13:00 | Up | 0.81 | 20 | 100% @ 0.818 | WIN | +20.47 |
| 11-10T18:30 | 12:00 | Up | 0.81 | 90 | 100% @ 0.813 | WIN | +21.27 |
| 11-10T19:45 | 12:00 | Up | 0.82 | 63 | 100% @ 0.825 | WIN | +19.58 |
| 11-10T20:00 | 12:00 | Down | 0.80 | 862 | 100% @ 0.800 | LOSS | -101.90 |
| 11-10T21:00 | 13:00 | Up | 0.80 | 3460 | 100% @ 0.800 | WIN | +23.10 |
| 11-11T01:00 | 12:00 | Down | 0.83 | 980 | 100% @ 0.830 | WIN | +18.87 |
| 11-11T01:30 | 12:00 | Up | 0.81 | 80 | 100% @ 0.814 | WIN | +21.15 |
| 11-11T05:30 | 12:00 | Up | 0.80 | 180 | 100% @ 0.800 | WIN | +23.10 |
| 11-11T07:15 | 12:00 | Up | 0.85 | 1449 | 100% @ 0.850 | WIN | +16.22 |
| 11-11T08:15 | 12:00 | Down | 0.85 | 745 | 100% @ 0.850 | WIN | +16.22 |
| 11-11T12:15 | 12:00 | Up | 0.87 | 163 | 100% @ 0.870 | WIN | +13.71 |
| 11-11T23:00 | 12:00 | Up | 0.85 | 660 | 100% @ 0.850 | LOSS | -101.42 |
| 11-11T23:15 | 12:00 | Up | 0.89 | 1305 | 100% @ 0.890 | WIN | +11.31 |
| 11-12T00:15 | 12:00 | Up | 0.83 | 809 | 100% @ 0.830 | WIN | +18.87 |

Book reads: 3253, failed: 956, re-tried: 1035, median latency 0.04s.
Entries read more than 20 s after their target second: 22 of 189 (avg 32 s late).
