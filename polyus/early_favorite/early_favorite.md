# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-11-05T06:39:36Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 209 | 272 |
| Win rate | 83.7% | 89.3% |
| Break-even win rate at prices paid | 84.9% | - |
| Average ask | 0.840 | 0.838 |
| Net at $100/round | $-314.64 | $+1,486 |
| Per round | -1.51% | +5.46% |
| Max drawdown | $-843.92 | $-403 |
| Longest losing streak | 5 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 1048. Pending (not settled or not fetched yet): 18.

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
| 2026-10-31 | $+42.86 |
| 2026-11-01 | $+118.14 |
| 2026-11-02 | $-313.40 |
| 2026-11-03 | $+1.61 |
| 2026-11-04 | $+170.62 |
| 2026-11-05 | $+127.27 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 157 | 85.4% | $-25.02 |
| with the favorite 1/3 | 44 | 79.5% | $-215.71 |
| against the favorite | 8 | 75.0% | $-73.91 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 209 | same |
| Positions cut | - | 20 (16 would have lost, 4 would have won) |
| Net at $100/round | $-314.64 | $-302.50 (+12.14) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 11-04 04:45 | 3 | Up | 0.85 | +3 | won | $+16.60 | $-555.93 |
| 11-04 07:30 | 2 | Down | 0.81 | -1 | won | $+22.14 | $-533.79 |
| 11-04 08:45 | 3 | Up | 0.81 | +3 | won | $+22.14 | $-511.65 |
| 11-04 09:00 | 3 | Down | 0.83 | +3 | won | $+19.30 | $-492.35 |
| 11-04 09:30 | 2 | Up | 0.82 | +1 | won | $+20.70 | $-471.65 |
| 11-04 12:00 | 3 | Down | 0.90 | +3 | won | $+10.42 | $-461.23 |
| 11-04 13:00 | 2 | Up | 0.84 | +3 | won | $+17.94 | $-443.29 |
| 11-04 13:30 | 3 | Down | 0.80 | +1 | won | $+23.61 | $-419.68 |
| 11-04 14:00 | 3 | Down | 0.84 | +3 | won | $+17.94 | $-401.74 |
| 11-04 14:30 | 2 | Up | 0.86 | +3 | won | $+15.31 | $-386.43 |
| 11-04 18:00 | 2 | Up | 0.89 | +3 | won | $+11.60 | $-374.83 |
| 11-04 19:00 | 2 | Down | 0.80 | +3 | won | $+23.61 | $-351.22 |
| 11-04 20:30 | 3 | Up | 0.84 | +3 | LOST | $-101.11 | $-452.33 |
| 11-04 23:00 | 2 | Down | 0.90 | +3 | won | $+10.42 | $-441.91 |
| 11-05 01:15 | 2 | Down | 0.80 | +3 | won | $+23.61 | $-418.30 |
| 11-05 01:30 | 3 | Up | 0.83 | +3 | won | $+19.30 | $-399.00 |
| 11-05 03:15 | 3 | Up | 0.81 | +3 | won | $+22.14 | $-376.86 |
| 11-05 03:45 | 2 | Down | 0.81 | +3 | won | $+22.14 | $-354.72 |
| 11-05 04:00 | 3 | Down | 0.81 | +3 | won | $+22.14 | $-332.58 |
| 11-05 06:15 | 2 | Up | 0.84 | +3 | won | $+17.94 | $-314.64 |
