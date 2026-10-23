# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-10-23T13:27:28Z.

**Too early to judge: 14 of the ~150 rounds (about a week) needed.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 14 | 272 |
| Win rate | 71.4% | 89.3% |
| Break-even win rate at prices paid | 85.5% | - |
| Average ask | 0.846 | 0.838 |
| Net at $100/round | $-231.22 | $+1,486 |
| Per round | -16.52% | +5.46% |
| Max drawdown | $-298.14 | $-403 |
| Longest losing streak | 2 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 40. Pending (not settled or not fetched yet): 0.

## By day (UTC)

| Day | Net |
|---|---|
| 2026-10-23 | $-231.22 |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Result | P&L | Running |
|---|---|---|---|---|---|---|
| 10-23 00:00 | 3 | Down | 0.81 | won | $+22.14 | $+22.14 |
| 10-23 00:30 | 3 | Up | 0.88 | won | $+12.80 | $+34.94 |
| 10-23 01:15 | 2 | Down | 0.85 | LOST | $-101.04 | $-66.10 |
| 10-23 01:45 | 2 | Up | 0.89 | LOST | $-100.76 | $-166.86 |
| 10-23 02:30 | 2 | Up | 0.88 | won | $+12.80 | $-154.06 |
| 10-23 03:15 | 2 | Down | 0.82 | won | $+20.70 | $-133.36 |
| 10-23 03:45 | 2 | Up | 0.81 | won | $+22.14 | $-111.22 |
| 10-23 05:00 | 3 | Up | 0.80 | won | $+23.61 | $-87.61 |
| 10-23 05:30 | 3 | Up | 0.87 | won | $+14.04 | $-73.57 |
| 10-23 06:00 | 2 | Down | 0.85 | LOST | $-101.04 | $-174.61 |
| 10-23 07:00 | 3 | Down | 0.88 | won | $+12.80 | $-161.81 |
| 10-23 07:30 | 2 | Up | 0.80 | LOST | $-101.39 | $-263.20 |
| 10-23 08:15 | 2 | Up | 0.87 | won | $+14.04 | $-249.16 |
| 10-23 11:00 | 3 | Down | 0.84 | won | $+17.94 | $-231.22 |
