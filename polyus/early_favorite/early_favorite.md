# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-10-29T14:16:10Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 101 | 272 |
| Win rate | 81.2% | 89.3% |
| Break-even win rate at prices paid | 85.2% | - |
| Average ask | 0.843 | 0.838 |
| Net at $100/round | $-510.15 | $+1,486 |
| Per round | -5.05% | +5.46% |
| Max drawdown | $-627.87 | $-403 |
| Longest losing streak | 3 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 523. Pending (not settled or not fetched yet): 10.

## By day (UTC)

| Day | Net |
|---|---|
| 2026-10-23 | $-138.09 |
| 2026-10-24 | $-72.04 |
| 2026-10-25 | $+158.51 |
| 2026-10-26 | $-288.77 |
| 2026-10-27 | $-135.61 |
| 2026-10-28 | $-114.87 |
| 2026-10-29 | $+80.72 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 74 | 83.8% | $-219.35 |
| with the favorite 1/3 | 24 | 75.0% | $-236.63 |
| against the favorite | 3 | 66.7% | $-54.17 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 101 | same |
| Positions cut | - | 11 (10 would have lost, 1 would have won) |
| Net at $100/round | $-510.15 | $-389.37 (+120.78) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 10-28 08:45 | 2 | Down | 0.80 | -1 | won | $+23.61 | $-376.35 |
| 10-28 12:00 | 3 | Down | 0.81 | +3 | won | $+22.14 | $-354.21 |
| 10-28 13:45 | 2 | Down | 0.82 | +3 | won | $+20.70 | $-333.51 |
| 10-28 14:15 | 2 | Down | 0.80 | +3 | won | $+23.61 | $-309.90 |
| 10-28 15:00 | 3 | Up | 0.81 | +3 | won | $+22.14 | $-287.76 |
| 10-28 15:30 | 2 | Down | 0.90 | +3 | won | $+10.42 | $-277.34 |
| 10-28 17:00 | 3 | Down | 0.82 | +1 | won | $+20.70 | $-256.64 |
| 10-28 18:00 | 3 | Up | 0.85 | +3 | LOST | $-101.04 | $-357.68 |
| 10-28 18:45 | 2 | Down | 0.80 | -1 | won | $+23.61 | $-334.07 |
| 10-28 20:00 | 2 | Up | 0.82 | +3 | LOST | $-101.25 | $-435.32 |
| 10-28 20:30 | 2 | Up | 0.80 | -3 | LOST | $-101.39 | $-536.71 |
| 10-28 21:45 | 2 | Up | 0.81 | +1 | won | $+22.14 | $-514.57 |
| 10-28 22:00 | 3 | Down | 0.92 | +3 | won | $+8.14 | $-506.43 |
| 10-28 22:30 | 2 | Up | 0.85 | +3 | won | $+16.60 | $-489.83 |
| 10-28 23:00 | 2 | Down | 0.85 | +3 | LOST | $-101.04 | $-590.87 |
| 10-29 01:30 | 2 | Down | 0.85 | +3 | won | $+16.60 | $-574.27 |
| 10-29 04:45 | 2 | Up | 0.88 | +3 | won | $+12.80 | $-561.47 |
| 10-29 13:00 | 2 | Up | 0.86 | +3 | won | $+15.31 | $-546.16 |
| 10-29 13:15 | 2 | Up | 0.86 | +3 | won | $+15.31 | $-530.85 |
| 10-29 13:30 | 2 | Down | 0.82 | +1 | won | $+20.70 | $-510.15 |
