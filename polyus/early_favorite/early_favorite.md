# Early Favorite v1 - forward test

Rule (frozen): at minute 2, else 3, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-22T08:30:00Z. Updated 2026-10-22T13:47:57Z.

**Too early to judge: 4 of the ~150 rounds (about a week) needed.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 4 | 371 |
| Win rate | 100.0% | 88.9% |
| Break-even win rate at prices paid | 84.7% | - |
| Average ask | 0.838 | 0.842 |
| Net at $100/round | $+74.06 | $+1,649 |
| Per round | +18.52% | +4.44% |
| Max drawdown | $0.00 | $-498 |
| Longest losing streak | 0 | 2 |

Rounds where the rule did not trigger: 8. Pending (not settled or not fetched yet): 2.

## By day (UTC)

| Day | Net |
|---|---|
| 2026-10-22 | $+74.06 |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Result | P&L | Running |
|---|---|---|---|---|---|---|
| 10-22 08:30 | 3 | Down | 0.80 | won | $+23.61 | $+23.61 |
| 10-22 08:45 | 2 | Down | 0.80 | won | $+23.61 | $+47.22 |
| 10-22 09:45 | 3 | Up | 0.87 | won | $+14.04 | $+61.26 |
| 10-22 13:15 | 2 | Up | 0.88 | won | $+12.80 | $+74.06 |
