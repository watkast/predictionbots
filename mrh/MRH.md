# Mr. H — Coinbase hopper, PAPER

Updated 2026-11-07T23:30:29Z · scans 224 · universe 111 coins (USD pairs with ≥ $100k 24-h volume) · fees 0.9% taker each way · start $4.00

## Books (one position at a time, all-in every hop)

| profile | bankroll | vs start | peak | hops | win % | avg net/hop | fees paid | open |
|---|---|---|---|---|---|---|---|---|
| aggressive | $3.05 | -23.8% | $4.00 | 7 | 29% | -3.74% | $0.442 | — |
| standard | $3.48 | -12.9% | $4.00 | 5 | 20% | -2.33% | $0.365 | CRO-USD @ 0.04914 |
| aggressive_swap | $3.70 | -7.5% | $4.02 | 3 | 33% | -2.53% | $0.211 | — |

## Signal forward returns (every signal, whether or not a book took it)

| profile | signals | scored | median +15m | median +1h | median +4h | % beat 1.8% at +1h | median 4%-trail hop net | max run-up (med) | max drawdown (med) |
|---|---|---|---|---|---|---|---|---|---|
| aggressive | 27 | 15 | -0.37% | -1.87% | -0.69% | 20% | -5.87% | +4.33% | -6.89% |
| standard | 23 | 15 | -0.21% | -1.38% | -0.47% | 20% | -5.13% | +5.66% | -4.92% |

## Aggressive signals by BTC regime (BTC's own move in the hour before the signal)

| BTC 1h | signals | median +1h | median 4%-trail hop net | % beat 1.8% at +1h |
|---|---|---|---|---|
| ≤ −0.5% (downdraft) | 0 | — | — | — |
| −0.5% … +0.5% (flat) | 3 | -5.25% | -6.02% | 0% |
| ≥ +0.5% (bid under the market) | 0 | — | — | — |

## Verdict

**Not yet.** Needs 40 scored aggressive signals (15 so far) and 30 closed aggressive hops (7 so far) before this says anything. Until then every number above is noise.

## Last 20 hops

| time (UTC) | book | coin | in | out | held | net | reason | bankroll |
|---|---|---|---|---|---|---|---|---|
| 11-07T06:45 | aggressive | GROVE | 0.00907 | 0.00868 | 20 m | -6.01% | trail | $3.76 |
| 11-07T07:25 | standard | ICNT | 0.303 | 0.2926 | 200 m | -5.16% | trail | $3.79 |
| 11-07T11:25 | standard | ALIGN | 0.00449 | 0.00433 | 65 m | -5.29% | trail | $3.59 |
| 11-07T11:45 | aggressive | ICNT | 0.3087 | 0.32 | 25 m | +1.80% | trail | $3.83 |
| 11-07T11:45 | standard | ICNT | 0.3173 | 0.32 | 20 m | -0.96% | trail | $3.56 |
| 11-07T14:10 | standard | CAP | 0.09713 | 0.1032 | 60 m | +4.35% | trail | $3.71 |
| 11-07T15:15 | aggressive | ALIGN | 0.0043 | 0.00412 | 115 m | -5.90% | trail | $3.60 |
| 11-07T16:26 | aggressive | RITUAL | 0.02644 | 0.02463 | 51 m | -8.51% | trail | $3.29 |
| 11-07T16:45 | standard | APR | 0.0424 | 0.0412 | 130 m | -4.57% | trail | $3.54 |
| 11-07T19:50 | aggressive | RITUAL | 0.02404 | 0.0246 | 125 m | +0.50% | trail | $3.31 |
| 11-07T19:50 | aggressive_swap | RITUAL | 0.02404 | 0.0246 | 125 m | +0.50% | trail | $4.02 |
| 11-07T21:50 | aggressive | MEZO | 0.004897 | 0.00468 | 30 m | -6.14% | trail | $3.11 |
| 11-07T21:50 | aggressive_swap | MEZO | 0.004897 | 0.00468 | 30 m | -6.14% | trail | $3.77 |
| 11-07T22:20 | aggressive | A8 | 0.004262 | 0.004255 | 30 m | -1.95% | trail | $3.05 |
| 11-07T22:20 | aggressive_swap | A8 | 0.004262 | 0.004255 | 30 m | -1.95% | trail | $3.70 |

## Last 15 signals

| time (UTC) | profile | coin | impulse | vol× | >2h high | spread | taken | +1h | +4h |
|---|---|---|---|---|---|---|---|---|---|
| 11-07T19:05 | aggressive | RITUAL | +3.7% | 3.3 | y | 0.04% | in_position | -5.2% | -5.2% |
| 11-07T19:05 | standard | RITUAL | +3.7% | 3.3 | y | 0.04% | in_position | -5.2% | -5.2% |
| 11-07T19:10 | standard | RITUAL | +1.1% | 9.9 | y | 1.05% | spread | -4.4% | -6.1% |
| 11-07T19:25 | standard | PROMPT | +2.0% | 4.7 | y | 0.05% | in_position | … | … |
| 11-07T19:55 | aggressive | DEGEN | +5.5% | 32.6 | n | 0.62% | spread | … | … |
| 11-07T21:20 | aggressive | MEZO | +3.8% | 18.0 | n | 0.55% | y | … | … |
| 11-07T21:25 | aggressive | MEZO | +2.4% | 10.4 | y | 0.42% | in_position | … | … |
| 11-07T21:25 | standard | MEZO | +2.4% | 10.4 | y | 0.42% | in_position | … | … |
| 11-07T21:35 | aggressive | RITUAL | +2.4% | 16.3 | y | 0.04% | in_position | … | … |
| 11-07T21:35 | standard | RITUAL | +2.4% | 16.3 | y | 0.04% | in_position | … | … |
| 11-07T21:50 | aggressive | A8 | +3.3% | 7.7 | n | 0.05% | y | … | … |
| 11-07T21:55 | aggressive | MEZO | +3.4% | 4.1 | n | 1.03% | spread | … | … |
| 11-07T21:55 | aggressive | A8 | +2.1% | 8.9 | n | 2.13% | spread | … | … |
| 11-07T22:00 | aggressive | A8 | +3.0% | 7.7 | n | 0.45% | in_position | … | … |
| 11-07T22:20 | standard | MET | +1.3% | 4.4 | y | 0.12% | in_position | … | … |
