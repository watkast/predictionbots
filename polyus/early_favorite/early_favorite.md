# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-10-29T00:56:02Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 96 | 272 |
| Win rate | 80.2% | 89.3% |
| Break-even win rate at prices paid | 85.1% | - |
| Average ask | 0.842 | 0.838 |
| Net at $100/round | $-590.87 | $+1,486 |
| Per round | -6.15% | +5.46% |
| Max drawdown | $-627.87 | $-403 |
| Longest losing streak | 3 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 483. Pending (not settled or not fetched yet): 1.

## By day (UTC)

| Day | Net |
|---|---|
| 2026-10-23 | $-138.09 |
| 2026-10-24 | $-72.04 |
| 2026-10-25 | $+158.51 |
| 2026-10-26 | $-288.77 |
| 2026-10-27 | $-135.61 |
| 2026-10-28 | $-114.87 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 70 | 82.9% | $-279.37 |
| with the favorite 1/3 | 23 | 73.9% | $-257.33 |
| against the favorite | 3 | 66.7% | $-54.17 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 96 | same |
| Positions cut | - | 11 (10 would have lost, 1 would have won) |
| Net at $100/round | $-590.87 | $-470.09 (+120.78) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 10-27 22:15 | 3 | Up | 0.81 | +3 | won | $+22.14 | $-476.00 |
| 10-28 03:30 | 3 | Up | 0.85 | +3 | won | $+16.60 | $-459.40 |
| 10-28 04:30 | 2 | Up | 0.81 | +1 | won | $+22.14 | $-437.26 |
| 10-28 07:45 | 2 | Up | 0.85 | +3 | won | $+16.60 | $-420.66 |
| 10-28 08:00 | 2 | Up | 0.82 | +3 | won | $+20.70 | $-399.96 |
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
