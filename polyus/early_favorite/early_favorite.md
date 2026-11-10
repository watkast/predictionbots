# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-11-10T01:30:42Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 285 | 272 |
| Win rate | 83.5% | 89.3% |
| Break-even win rate at prices paid | 84.8% | - |
| Average ask | 0.839 | 0.838 |
| Net at $100/round | $-467.85 | $+1,486 |
| Per round | -1.64% | +5.46% |
| Max drawdown | $-947.43 | $-403 |
| Longest losing streak | 5 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 1422. Pending (not settled or not fetched yet): 20.

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
| 2026-11-05 | $-245.84 |
| 2026-11-06 | $-82.11 |
| 2026-11-07 | $+0.54 |
| 2026-11-08 | $+83.79 |
| 2026-11-09 | $+187.96 |
| 2026-11-10 | $+29.72 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 219 | 84.9% | $-75.40 |
| with the favorite 1/3 | 54 | 81.5% | $-149.96 |
| against the favorite | 12 | 66.7% | $-242.49 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 285 | same |
| Positions cut | - | 28 (23 would have lost, 5 would have won) |
| Net at $100/round | $-467.85 | $-426.89 (+40.96) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 11-08 23:45 | 2 | Down | 0.81 | +3 | won | $+22.14 | $-685.53 |
| 11-09 00:15 | 2 | Up | 0.88 | +3 | won | $+12.80 | $-672.73 |
| 11-09 03:45 | 2 | Down | 0.80 | +1 | won | $+23.61 | $-649.12 |
| 11-09 05:00 | 3 | Down | 0.82 | +3 | won | $+20.70 | $-628.42 |
| 11-09 05:45 | 3 | Up | 0.87 | +1 | won | $+14.04 | $-614.38 |
| 11-09 06:15 | 2 | Down | 0.82 | +3 | won | $+20.70 | $-593.68 |
| 11-09 08:15 | 3 | Up | 0.82 | +3 | won | $+20.70 | $-572.98 |
| 11-09 09:00 | 3 | Up | 0.84 | +3 | LOST | $-101.11 | $-674.09 |
| 11-09 10:30 | 3 | Down | 0.88 | +1 | won | $+12.80 | $-661.29 |
| 11-09 11:15 | 2 | Up | 0.88 | +3 | won | $+12.80 | $-648.49 |
| 11-09 12:30 | 3 | Up | 0.83 | +3 | won | $+19.30 | $-629.19 |
| 11-09 14:00 | 2 | Down | 0.84 | +3 | won | $+17.94 | $-611.25 |
| 11-09 14:30 | 3 | Down | 0.83 | +3 | won | $+19.30 | $-591.95 |
| 11-09 16:30 | 2 | Up | 0.82 | -3 | won | $+20.70 | $-571.25 |
| 11-09 18:15 | 3 | Down | 0.88 | +3 | won | $+12.80 | $-558.45 |
| 11-09 18:30 | 2 | Up | 0.81 | +1 | won | $+22.14 | $-536.31 |
| 11-09 20:30 | 2 | Down | 0.85 | +3 | won | $+16.60 | $-519.71 |
| 11-09 22:30 | 3 | Up | 0.81 | +3 | won | $+22.14 | $-497.57 |
| 11-10 00:15 | 3 | Down | 0.83 | +3 | won | $+19.30 | $-478.27 |
| 11-10 01:00 | 2 | Up | 0.90 | +3 | won | $+10.42 | $-467.85 |
