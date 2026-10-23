# Early Favorite auto-buyer v1 (paper)

Paper only. Reads the live Polymarket US book at 13:00 left, else 12:00 left; buys the favorite if its ask is 80-95c with a limit at ask+1c, filled only against size actually resting on the book.
Updated 2026-10-23T10:05:32Z.

Rounds watched: 74. Entries: 8. Settled: 8.

Win rate: 7/8 = 87.5%

| Stake | Full fill rate | Avg fill | Avg price | Net P&L | Per $ staked |
|---|---|---|---|---|---|
| $50 | 100% | 100% | 0.848 | $+13.05 | +3.26% |
| $100 | 100% | 100% | 0.848 | $+26.09 | +3.26% |
| $250 | 100% | 100% | 0.848 | $+64.13 | +3.21% |

Live $100 fill price minus the backtest's display price: -3.00c average over 7 entries (the backtest edge was about +4.2c, so this gap is what it must survive).

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

Book reads: 147, failed: 55, median latency 0.07s.
