# Early Favorite v1 - forward test

Rule (frozen): at minute 2, else 3, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-22T08:30:00Z. Updated 2026-10-22T18:31:40Z.

**Too early to judge: 10 of the ~150 rounds (about a week) needed.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 10 | 371 |
| Win rate | 90.0% | 88.9% |
| Break-even win rate at prices paid | 85.9% | - |
| Average ask | 0.850 | 0.842 |
| Net at $100/round | $+56.63 | $+1,649 |
| Per round | +5.66% | +4.44% |
| Max drawdown | $-100.76 | $-498 |
| Longest losing streak | 1 | 2 |

Rounds where the rule did not trigger: 21. Pending (not settled or not fetched yet): 2.

## By day (UTC)

| Day | Net |
|---|---|
| 2026-10-22 | $+56.63 |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Result | P&L | Running |
|---|---|---|---|---|---|---|
| 10-22 08:30 | 3 | Down | 0.80 | won | $+23.61 | $+23.61 |
| 10-22 08:45 | 2 | Down | 0.80 | won | $+23.61 | $+47.22 |
| 10-22 09:45 | 3 | Up | 0.87 | won | $+14.04 | $+61.26 |
| 10-22 13:15 | 2 | Up | 0.88 | won | $+12.80 | $+74.06 |
| 10-22 13:45 | 2 | Down | 0.89 | LOST | $-100.76 | $-26.70 |
| 10-22 16:30 | 2 | Down | 0.87 | won | $+14.04 | $-12.66 |
| 10-22 16:45 | 2 | Down | 0.93 | won | $+7.04 | $-5.62 |
| 10-22 17:15 | 2 | Up | 0.82 | won | $+20.70 | $+15.08 |
| 10-22 17:30 | 2 | Down | 0.80 | won | $+23.61 | $+38.69 |
| 10-22 18:00 | 2 | Down | 0.84 | won | $+17.94 | $+56.63 |
