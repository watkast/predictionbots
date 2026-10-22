# Early Favorite v1 - forward test

Rule (frozen): at minute 2, else 3, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-22T08:30:00Z. Updated 2026-10-22T22:17:56Z.

**Too early to judge: 14 of the ~150 rounds (about a week) needed.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 14 | 371 |
| Win rate | 92.9% | 88.9% |
| Break-even win rate at prices paid | 85.3% | - |
| Average ask | 0.844 | 0.842 |
| Net at $100/round | $+135.37 | $+1,649 |
| Per round | +9.67% | +4.44% |
| Max drawdown | $-100.76 | $-498 |
| Longest losing streak | 1 | 2 |

Rounds where the rule did not trigger: 32. Pending (not settled or not fetched yet): 2.

## By day (UTC)

| Day | Net |
|---|---|
| 2026-10-22 | $+135.37 |

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
| 10-22 20:15 | 2 | Down | 0.81 | won | $+22.14 | $+78.77 |
| 10-22 20:30 | 3 | Down | 0.83 | won | $+19.30 | $+98.07 |
| 10-22 21:15 | 2 | Up | 0.85 | won | $+16.60 | $+114.67 |
| 10-22 22:00 | 3 | Up | 0.82 | won | $+20.70 | $+135.37 |
