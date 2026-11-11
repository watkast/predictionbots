# Early Favorite v2 - forward test

Rule (frozen): at 2:00 elapsed (13:00 left), else 3:00, buy the leading side if its ask is 0.80-0.95; $100 per round; hold to settlement; taker fee 0.0695*p*(1-p). Paper only.
Forward test started 2026-10-23T00:00:00Z. Updated 2026-11-11T14:10:38Z.

**Losing: forward win rate is below break-even at the prices paid.**

| | Forward | Backtest (Oct 6-22) |
|---|---|---|
| Rounds | 317 | 272 |
| Win rate | 83.0% | 89.3% |
| Break-even win rate at prices paid | 84.8% | - |
| Average ask | 0.839 | 0.838 |
| Net at $100/round | $-755.69 | $+1,486 |
| Per round | -2.38% | +5.46% |
| Max drawdown | $-947.43 | $-403 |
| Longest losing streak | 5 | 2 |
| Entry timing | 13:00 / 12:00 left | same |

Rounds where the rule did not trigger: 1537. Pending (not settled or not fetched yet): 19.

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
| 2026-11-10 | $-266.21 |
| 2026-11-11 | $+8.09 |

## Chart pull at the check (parallel column - not part of the rule)

Pull = EMA 9/21 and Supertrend on BRTI 1-minute candles, as drawn by research/market_pull.pine, read against the favorite. Oct 16-24 (143 rounds): 3/3 with the favorite won 92%, 1/3 won 84%, against won 78%. Small sample; this column is the forward test of that.

| Pull at the check | Rounds | Win rate | Net |
|---|---|---|---|
| with the favorite 3/3 | 245 | 84.5% | $-227.97 |
| with the favorite 1/3 | 58 | 81.0% | $-200.44 |
| against the favorite | 14 | 64.3% | $-327.28 |

## Cut at 5:00 left (parallel column - not part of the rule)

What if the position were sold at 5:00 left whenever the favorite's bid is under 45c (sold 2c under the bid, taker fee)? Backtest Oct 6-22: about +$150-220 over holding on 272 trades, under 1% of the money staked and found in-sample. This is its forward test; the traded rule stays hold-to-settlement.

| | Hold (the rule) | Cut under 45c at 5:00 left |
|---|---|---|
| Rounds with a 5:00-left price | 317 | same |
| Positions cut | - | 29 (24 would have lost, 5 would have won) |
| Net at $100/round | $-755.69 | $-678.00 (+77.69) |

## Last 20 rounds

| Window (UTC) | Min | Side | Ask | Pull | Result | P&L | Running |
|---|---|---|---|---|---|---|---|
| 11-10 12:30 | 3 | Down | 0.87 | +3 | won | $+14.04 | $-476.65 |
| 11-10 13:00 | 2 | Down | 0.83 | +1 | LOST | $-101.18 | $-577.83 |
| 11-10 13:15 | 2 | Down | 0.91 | +1 | won | $+9.26 | $-568.57 |
| 11-10 13:30 | 2 | Down | 0.91 | +3 | won | $+9.26 | $-559.31 |
| 11-10 14:15 | 3 | Down | 0.83 | +3 | won | $+19.30 | $-540.01 |
| 11-10 14:45 | 3 | Down | 0.80 | -3 | LOST | $-101.39 | $-641.40 |
| 11-10 15:00 | 2 | Up | 0.92 | +3 | won | $+8.14 | $-633.26 |
| 11-10 18:30 | 3 | Up | 0.86 | +3 | won | $+15.31 | $-617.95 |
| 11-10 19:45 | 3 | Up | 0.85 | +3 | won | $+16.60 | $-601.35 |
| 11-10 20:00 | 2 | Down | 0.81 | +3 | LOST | $-101.32 | $-702.67 |
| 11-10 20:15 | 3 | Up | 0.80 | +3 | won | $+23.61 | $-679.06 |
| 11-10 21:00 | 2 | Up | 0.85 | +3 | won | $+16.60 | $-662.46 |
| 11-10 23:15 | 2 | Up | 0.81 | +3 | LOST | $-101.32 | $-763.78 |
| 11-11 01:00 | 3 | Down | 0.81 | +3 | won | $+22.14 | $-741.64 |
| 11-11 01:30 | 3 | Up | 0.84 | +3 | won | $+17.94 | $-723.70 |
| 11-11 04:15 | 2 | Down | 0.82 | +3 | won | $+20.70 | $-703.00 |
| 11-11 07:15 | 2 | Up | 0.88 | +3 | won | $+12.80 | $-690.20 |
| 11-11 08:15 | 3 | Down | 0.83 | +1 | won | $+19.30 | $-670.90 |
| 11-11 12:15 | 3 | Up | 0.85 | +3 | won | $+16.60 | $-654.30 |
| 11-11 13:00 | 2 | Down | 0.80 | +3 | LOST | $-101.39 | $-755.69 |
