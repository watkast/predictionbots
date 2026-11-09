# Mr. H — Coinbase hopper, PAPER

Updated 2026-11-09T05:30:31Z · scans 583 · universe 111 coins (USD pairs with ≥ $100k 24-h volume) · fees 0.9% taker each way · start $4.00

## Books (one position at a time, all-in every hop)

| profile | bankroll | vs start | peak | hops | win % | avg net/hop | fees paid | open |
|---|---|---|---|---|---|---|---|---|
| aggressive | $2.85 | -28.8% | $4.00 | 8 | 25% | -4.00% | $0.521 | IRYS-USD @ 0.01717 |
| standard | $3.09 | -22.7% | $4.00 | 9 | 11% | -2.67% | $0.604 | INJ-USD @ 8.15 |
| aggressive_swap | $3.33 | -16.8% | $4.02 | 15 | 33% | -1.03% | $0.969 | — |

## Signal forward returns (every signal, whether or not a book took it)

| profile | signals | scored | median +15m | median +1h | median +4h | % beat 1.8% at +1h | median 4%-trail hop net | max run-up (med) | max drawdown (med) |
|---|---|---|---|---|---|---|---|---|---|
| aggressive | 86 | 67 | -0.36% | -1.87% | -3.33% | 27% | -3.63% | +7.45% | -9.51% |
| standard | 66 | 54 | -0.20% | -1.32% | -3.31% | 22% | -3.20% | +5.56% | -6.68% |

## Aggressive signals by BTC regime (BTC's own move in the hour before the signal)

| BTC 1h | signals | median +1h | median 4%-trail hop net | % beat 1.8% at +1h |
|---|---|---|---|---|
| ≤ −0.5% (downdraft) | 2 | +5.00% | +4.79% | 50% |
| −0.5% … +0.5% (flat) | 49 | -2.42% | -4.70% | 22% |
| ≥ +0.5% (bid under the market) | 4 | +3.00% | +0.55% | 75% |

## Verdict

**Not yet.** Needs 40 scored aggressive signals (67 so far) and 30 closed aggressive hops (8 so far) before this says anything. Until then every number above is noise.

## Last 20 hops

| time (UTC) | book | coin | in | out | held | net | reason | bankroll |
|---|---|---|---|---|---|---|---|---|
| 11-07T21:50 | aggressive_swap | MEZO | 0.004897 | 0.00468 | 30 m | -6.14% | trail | $3.77 |
| 11-07T22:20 | aggressive | A8 | 0.004262 | 0.004255 | 30 m | -1.95% | trail | $3.05 |
| 11-07T22:20 | aggressive_swap | A8 | 0.004262 | 0.004255 | 30 m | -1.95% | trail | $3.70 |
| 11-08T04:50 | aggressive_swap | DRV | 0.32104 | 0.3189 | 280 m | -2.45% | swap | $3.61 |
| 11-08T05:50 | aggressive_swap | MEZO | 0.00406 | 0.004075 | 60 m | -1.43% | trail | $3.56 |
| 11-08T06:35 | aggressive_swap | RITUAL | 0.03362 | 0.03225 | 5 m | -5.79% | trail | $3.35 |
| 11-08T08:05 | aggressive_swap | ICNT | 0.3317 | 0.3606 | 50 m | +6.76% | trail | $3.58 |
| 11-08T09:25 | aggressive_swap | ICNT | 0.3888 | 0.3624 | 10 m | -8.46% | trail | $3.27 |
| 11-08T10:30 | standard | CRO | 0.04914 | 0.04833 | 1010 m | -3.41% | delisted | $3.42 |
| 11-08T13:05 | aggressive_swap | MEZO | 0.00408 | 0.004839 | 40 m | +16.48% | trail | $3.81 |
| 11-08T13:55 | standard | VVV | 20.767 | 20.6601 | 160 m | -2.30% | trail | $3.34 |
| 11-08T16:10 | standard | CAP | 0.10564 | 0.106 | 55 m | -1.46% | trail | $3.30 |
| 11-08T16:20 | aggressive_swap | CAP | 0.10564 | 0.10301 | 65 m | -4.24% | trail | $3.65 |
| 11-08T17:20 | aggressive_swap | BOBBOB | 0.00406 | 0.00389 | 15 m | -5.90% | trail | $3.44 |
| 11-08T19:35 | aggressive_swap | FORTH | 0.158 | 0.1675 | 50 m | +4.11% | trail | $3.58 |
| 11-08T19:55 | aggressive_swap | FORTH | 0.174 | 0.167 | 15 m | -5.74% | trail | $3.37 |
| 11-08T20:47 | standard | RSR | 0.001783 | 0.001721 | 32 m | -5.21% | trail | $3.12 |
| 11-08T22:00 | aggressive | DRV | 0.32104 | 0.30804 | 1310 m | -5.77% | trail | $2.87 |
| 11-08T22:55 | aggressive_swap | ICNT | 0.3688 | 0.3552 | 165 m | -5.41% | trail | $3.19 |
| 11-09T00:40 | aggressive_swap | RITUAL | 0.04055 | 0.04305 | 65 m | +4.26% | trail | $3.33 |

## Last 15 signals

| time (UTC) | profile | coin | impulse | vol× | >2h high | spread | taken | +1h | +4h |
|---|---|---|---|---|---|---|---|---|---|
| 11-08T23:35 | aggressive | RITUAL | +4.8% | 9.0 | n | 0.07% | in_position | +8.9% | +11.0% |
| 11-08T23:35 | aggressive | MEZO | +2.3% | 8.4 | n | 0.56% | in_position | +3.5% | +0.2% |
| 11-09T00:25 | aggressive | RITUAL | +5.2% | 3.6 | y | 1.57% | spread | +10.6% | -4.4% |
| 11-09T00:25 | standard | RITUAL | +5.2% | 3.6 | y | 1.57% | spread | +10.6% | -4.4% |
| 11-09T00:30 | aggressive | RITUAL | +4.9% | 7.4 | y | 0.79% | spread | +11.9% | -5.3% |
| 11-09T00:30 | standard | RITUAL | +4.9% | 7.4 | y | 0.79% | spread | +11.9% | -5.3% |
| 11-09T00:50 | aggressive | RITUAL | +6.8% | 7.7 | y | 1.86% | spread | +2.2% | -4.6% |
| 11-09T00:50 | standard | RITUAL | +6.8% | 7.7 | y | 1.86% | spread | +2.2% | -4.6% |
| 11-09T00:55 | aggressive | RITUAL | +3.3% | 6.7 | y | 1.64% | spread | -3.2% | -9.9% |
| 11-09T00:55 | standard | RITUAL | +3.3% | 6.7 | y | 1.64% | spread | -3.2% | -9.9% |
| 11-09T01:10 | aggressive | MEZO | +4.8% | 23.1 | n | 1.11% | spread | +2.5% | -1.6% |
| 11-09T01:30 | aggressive | RITUAL | +5.0% | 4.8 | n | 0.80% | spread | … | … |
| 11-09T01:55 | aggressive | MEZO | +2.1% | 3.9 | n | 0.67% | spread | … | … |
| 11-09T04:50 | aggressive | MEZO | +3.5% | 15.5 | n | 0.94% | spread | … | … |
| 11-09T04:50 | aggressive | RITUAL | +3.4% | 3.3 | n | 1.62% | spread | … | … |
