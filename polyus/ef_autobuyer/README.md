# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-11-12T06:13:31Z.

Rounds watched: 1673. Entries: 192. Settled: 191.

Win rate: 155/191 = 81.2%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 99% | 99% | 0.841 | $-466.57 | -4.93% |
| $100 | 97% | 99% | 0.841 | $-934.40 | -4.96% |
| $250 | 91% | 96% | 0.842 | $-2,355.81 | -5.15% |

Live $100 fill price minus the backtest's display price: +0.72c average over 187 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

## Last 20 entries

| Window (UTC) | Left | Side | Ask | Depth at ask | $100 fill | Result | P&L $100 |
|---|---|---|---|---|---|---|---|
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
| 11-12T04:30 | 12:00 | Down | 0.81 | 701 | 100% @ 0.810 | WIN | +21.65 |
| 11-12T05:00 | 13:00 | Down | 0.81 | 705 | 100% @ 0.810 | WIN | +21.65 |
| 11-12T06:00 | 12:00 | Up | 0.86 | 934 | 100% @ 0.860 | - | +0.00 |

Book reads: 3279, failed: 958, re-tried: 1039, median latency 0.04s.
Entries read more than 20 s after their target second: 22 of 192 (avg 32 s late).
