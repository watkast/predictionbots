# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-10-31T05:31:23Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 133 | 272 |
| Win rate | 82.7% | 89.3% |
| Break-even win rate at prices paid | 85.3% | - |
| Average ask | 0.844 | 0.838 |
| Net at $100/round | $-438.13 | $+1,486 |
| Per round | -3.29% | +5.46% |
| Max drawdown | $-627.87 | $-403 |
| Longest losing streak | 3 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 648. Pending (not settled or not fetched yet): 10.

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
| 2026-10-30 | $-136.21 |
| 2026-10-31 | $+23.61 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 99 | 84.9% | $-152.97 |
| with the favorite 1/3 | 30 | 76.7% | $-247.59 |
| against the favorite | 4 | 75.0% | $-37.57 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 133 | same |
| Positions cut | - | 14 (11 would have lost, 3 would have won) |
| Net at $100/round | $-438.13 | $-450.02 (-11.89) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 10-30 01:45 | 3 | Down | 0.88 | +3 | won | $+12.80 | $-312.73 |
| 10-30 03:00 | 3 | Up | 0.82 | +3 | won | $+20.70 | $-292.03 |
| 10-30 03:30 | 3 | Up | 0.86 | +3 | won | $+15.31 | $-276.72 |
| 10-30 04:00 | 2 | Down | 0.87 | +1 | won | $+14.04 | $-262.68 |
| 10-30 04:15 | 3 | Up | 0.83 | +3 | won | $+19.30 | $-243.38 |
| 10-30 05:00 | 3 | Up | 0.85 | +1 | won | $+16.60 | $-226.78 |
| 10-30 06:45 | 3 | Down | 0.84 | +3 | LOST | $-101.11 | $-327.89 |
| 10-30 07:45 | 2 | Up | 0.85 | -1 | won | $+16.60 | $-311.29 |
| 10-30 09:30 | 3 | Down | 0.88 | +3 | won | $+12.80 | $-298.49 |
| 10-30 10:30 | 2 | Up | 0.81 | +1 | won | $+22.14 | $-276.35 |
| 10-30 10:45 | 3 | Down | 0.80 | +1 | LOST | $-101.39 | $-377.74 |
| 10-30 13:30 | 3 | Down | 0.82 | +3 | won | $+20.70 | $-357.04 |
| 10-30 15:00 | 2 | Up | 0.80 | +3 | won | $+23.61 | $-333.43 |
| 10-30 15:15 | 3 | Up | 0.87 | +3 | LOST | $-100.90 | $-434.33 |
| 10-30 15:45 | 3 | Down | 0.85 | +3 | LOST | $-101.04 | $-535.37 |
| 10-30 16:00 | 2 | Down | 0.86 | +3 | won | $+15.31 | $-520.06 |
| 10-30 16:45 | 3 | Down | 0.81 | +3 | won | $+22.14 | $-497.92 |
| 10-30 20:00 | 3 | Up | 0.81 | +3 | won | $+22.14 | $-475.78 |
| 10-30 22:00 | 3 | Up | 0.87 | +1 | won | $+14.04 | $-461.74 |
| 10-31 04:00 | 2 | Up | 0.80 | +1 | won | $+23.61 | $-438.13 |
