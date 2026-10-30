# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-10-30T07:04:46Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 120 | 272 |
| Win rate | 83.3% | 89.3% |
| Break-even win rate at prices paid | 85.4% | - |
| Average ask | 0.845 | 0.838 |
| Net at $100/round | $-327.89 | $+1,486 |
| Per round | -2.73% | +5.46% |
| Max drawdown | $-627.87 | $-403 |
| Longest losing streak | 3 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 572. Pending (not settled or not fetched yet): 9.

## By day (UTC)

| Day | Net |
|---|---|
| 2026-10-23 | $-138.09 |
| 2026-10-24 | $-72.04 |
| 2026-10-25 | $+158.51 |
| 2026-10-26 | $-288.77 |
| 2026-10-27 | $-135.61 |
| 2026-10-28 | $-114.87 |
| 2026-10-29 | $+265.34 |
| 2026-10-30 | $-2.36 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 91 | 85.7% | $-67.73 |
| with the favorite 1/3 | 26 | 76.9% | $-205.99 |
| against the favorite | 3 | 66.7% | $-54.17 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 120 | same |
| Positions cut | - | 12 (10 would have lost, 2 would have won) |
| Net at $100/round | $-327.89 | $-288.13 (+39.76) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 10-29 13:30 | 2 | Down | 0.82 | +1 | won | $+20.70 | $-510.15 |
| 10-29 14:30 | 3 | Up | 0.94 | +3 | won | $+5.97 | $-504.18 |
| 10-29 15:00 | 3 | Up | 0.81 | +3 | won | $+22.14 | $-482.04 |
| 10-29 15:30 | 3 | Up | 0.88 | +3 | won | $+12.80 | $-469.24 |
| 10-29 16:15 | 3 | Down | 0.82 | +3 | won | $+20.70 | $-448.54 |
| 10-29 17:45 | 3 | Down | 0.82 | +3 | won | $+20.70 | $-427.84 |
| 10-29 18:30 | 2 | Down | 0.87 | +3 | won | $+14.04 | $-413.80 |
| 10-29 19:30 | 3 | Up | 0.88 | +3 | won | $+12.80 | $-401.00 |
| 10-29 20:00 | 2 | Down | 0.91 | +3 | won | $+9.26 | $-391.74 |
| 10-29 20:45 | 3 | Down | 0.87 | +3 | won | $+14.04 | $-377.70 |
| 10-29 21:15 | 3 | Up | 0.83 | +3 | won | $+19.30 | $-358.40 |
| 10-29 21:45 | 3 | Down | 0.80 | +3 | won | $+23.61 | $-334.79 |
| 10-29 23:45 | 2 | Down | 0.91 | +3 | won | $+9.26 | $-325.53 |
| 10-30 01:45 | 3 | Down | 0.88 | +3 | won | $+12.80 | $-312.73 |
| 10-30 03:00 | 3 | Up | 0.82 | +3 | won | $+20.70 | $-292.03 |
| 10-30 03:30 | 3 | Up | 0.86 | +3 | won | $+15.31 | $-276.72 |
| 10-30 04:00 | 2 | Down | 0.87 | +1 | won | $+14.04 | $-262.68 |
| 10-30 04:15 | 3 | Up | 0.83 | +3 | won | $+19.30 | $-243.38 |
| 10-30 05:00 | 3 | Up | 0.85 | +1 | won | $+16.60 | $-226.78 |
| 10-30 06:45 | 3 | Down | 0.84 | +3 | LOST | $-101.11 | $-327.89 |
