# NFL in-game underdog study (KXNFLGAME)

Updated 2026-10-29 18:06Z. 122 games, 0 team-markets with 1-min candles (skipped: 244 no kickoff time, 0 no candles). Buying at the ask, Kalshi taker fee 0.07·p·(1−p). Phase = minutes since scheduled kickoff (proxy). One entry per team per game per rule.

## A. Calibration — does a team priced X actually win X% of the time?

| phase | ask bucket | n | avg paid | win rate | 95% low | edge/contract (after fee) |
|---|---|---|---|---|---|---|

Edge is real only where the **95% low** win rate is above avg paid + fee. Positive edge with a low bound below the price = not proven yet.

## B/C. Strategies — buy the first time the ask is ≤ P in the phase

| phase | P | n | win% | hold: avg P&L/contract | bounce +10c | +15c | +20c | double | hit% (+15c) | worst-10 sum |
|---|---|---|---|---|---|---|---|---|---|---|

P&L is per $1 contract. A +0.03 average on 25c entries is +12% per trade. Bounce columns sell at the bid the first time it reaches the target and otherwise hold to the final whistle.

## D. Sell limits — place a resting sell right after buying

Each cell: average P&L per contract if the whole position rests one sell at that price (unfilled -> held to the final whistle). The best level is the most profitable single exit; a ladder spreads across levels to smooth results.


