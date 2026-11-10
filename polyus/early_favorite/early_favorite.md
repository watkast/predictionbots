# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-11-10T09:44:18Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 294 | 272 |
| Win rate | 83.7% | 89.3% |
| Break-even win rate at prices paid | 84.8% | - |
| Average ask | 0.839 | 0.838 |
| Net at $100/round | $-432.84 | $+1,486 |
| Per round | -1.47% | +5.46% |
| Max drawdown | $-947.43 | $-403 |
| Longest losing streak | 5 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 1446. Pending (not settled or not fetched yet): 19.

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
| 2026-11-10 | $+64.73 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 226 | 85.0% | $-79.13 |
| with the favorite 1/3 | 55 | 81.8% | $-127.82 |
| against the favorite | 13 | 69.2% | $-225.89 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 294 | same |
| Positions cut | - | 28 (23 would have lost, 5 would have won) |
| Net at $100/round | $-432.84 | $-391.88 (+40.96) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
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
| 11-10 01:30 | 2 | Down | 0.81 | +3 | won | $+22.14 | $-445.71 |
| 11-10 02:45 | 3 | Up | 0.81 | +1 | won | $+22.14 | $-423.57 |
| 11-10 03:45 | 2 | Up | 0.85 | -1 | won | $+16.60 | $-406.97 |
| 11-10 06:00 | 2 | Down | 0.84 | +3 | won | $+17.94 | $-389.03 |
| 11-10 07:00 | 3 | Up | 0.85 | +3 | won | $+16.60 | $-372.43 |
| 11-10 07:45 | 2 | Up | 0.81 | +3 | LOST | $-101.32 | $-473.75 |
| 11-10 08:15 | 3 | Down | 0.81 | +3 | won | $+22.14 | $-451.61 |
| 11-10 08:30 | 2 | Down | 0.88 | +3 | won | $+12.80 | $-438.81 |
| 11-10 09:00 | 3 | Down | 0.94 | +3 | won | $+5.97 | $-432.84 |
