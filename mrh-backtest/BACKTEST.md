# Mr. H — Coinbase hopper, BACKTEST (30 days)

Generated 2026-11-07T22:33:44Z · window 2026-10-08 22:25 → 2026-11-07 22:25 UTC · universe 112 coins · 5150 signals, 5119 scored · fees 0.9% taker each way (the ≤0.6% live spread comes on top) · fills and stops on 5-min closes · 3249 API calls in 393s

## Signal forward returns (every signal)

| profile | signals | fresh | median +15m | median +1h | median +4h | % beat 1.8% at +1h | mean trail-4% net | median trail-4% net | max run-up (med) | max drawdown (med) |
|---|---|---|---|---|---|---|---|---|---|---|
| aggressive | 1982 | 1185 | -0.43% | -1.19% | -2.27% | 24% | -2.07% | -4.04% | +4.52% | -5.56% |
| standard | 3168 | 2092 | -0.14% | -0.47% | -1.13% | 21% | -1.89% | -2.94% | +2.87% | -3.23% |

## Verdict (fresh aggressive signals — one per spike)

- The live rule (4% trail) nets a **negative** mean of **-1.86%** per hop over 1172 fresh signals, 24% of them winners; compounding all-in that is **-2.04%** per hop.
- Best trail width by compounded net: **8%** at **-1.96%** per hop (live uses 4%).
- Continuation entry (wait one candle, enter only if it held): 532/1172 (45%) held; those net **-2.02%** mean / **-2.20%** compounded per hop on the 4% trail vs -1.86% / -2.04% entering on the spike.
- The candle right after the impulse closes a median **-0.21%** from the signal close (43% of the time above it) — the size of the immediate give-back.
- 23% of signals beat the 1.8% round-trip fee at +1 h.

## Trail width — fresh aggressive signals, entered at the signal close

| trail | hops | win % | mean net/hop | median net/hop | geo mean/hop (compounding) | worst | best |
|---|---|---|---|---|---|---|---|
| 3% | 1172 | 22% | -2.00% | -3.64% | -2.14% | -13.58% | +93.62% |
| 4% | 1172 | 24% | -1.86% | -3.55% | -2.04% | -15.23% | +93.62% |
| 6% | 1172 | 27% | -1.72% | -3.39% | -1.98% | -15.23% | +93.62% |
| 8% | 1172 | 28% | -1.54% | -3.24% | -1.96% | -15.23% | +211.78% |
| 12% | 1172 | 27% | -1.76% | -3.24% | -2.19% | -32.60% | +211.78% |
| hold 4 h, no stop | 1172 | 27% | -1.62% | -3.31% | -2.28% | -60.86% | +369.29% |

## Continuation entry — wait one candle, enter only if it held (532 of 1172 held)

| trail | hops | win % | mean net/hop | median net/hop | geo mean/hop (compounding) | worst | best |
|---|---|---|---|---|---|---|---|
| 3% | 532 | 21% | -2.13% | -3.75% | -2.26% | -15.14% | +64.58% |
| 4% | 532 | 23% | -2.02% | -3.53% | -2.20% | -15.14% | +64.58% |
| 6% | 532 | 25% | -2.00% | -3.40% | -2.26% | -15.14% | +65.90% |
| 8% | 532 | 24% | -1.64% | -3.42% | -2.11% | -15.14% | +189.68% |
| 12% | 532 | 24% | -1.85% | -3.41% | -2.35% | -17.73% | +189.68% |

## Where the edge is (or isn't) — fresh aggressive signals, 4% trail

| BTC 2-h regime at signal | signals | median +1h | median +4h | mean trail-4% net | win % (4% trail) | mean trail-8% net |
|---|---|---|---|---|---|---|
| BTC down >1% | 63 | -1.48% | -3.10% | -3.25% | 19% | -3.19% |
| BTC flat | 1051 | -0.83% | -1.50% | -1.75% | 24% | -1.41% |
| BTC up >1% | 58 | -0.74% | -1.38% | -2.32% | 21% | -2.08% |

| impulse size | signals | median +1h | median +4h | mean trail-4% net | win % (4% trail) | mean trail-8% net |
|---|---|---|---|---|---|---|
| 2–3% | 684 | -0.68% | -1.34% | -1.92% | 24% | -1.99% |
| 3–5% | 354 | -1.12% | -1.90% | -1.88% | 22% | -1.58% |
| 5–10% | 110 | -1.31% | -3.34% | -1.60% | 27% | +0.29% |
| 10%+ | 24 | -3.02% | -5.12% | -1.08% | 29% | +3.59% |

| volume multiple | signals | median +1h | median +4h | mean trail-4% net | win % (4% trail) | mean trail-8% net |
|---|---|---|---|---|---|---|
| 3–5× | 288 | -0.46% | -1.00% | -1.25% | 32% | -0.71% |
| 5–10× | 347 | -1.31% | -1.97% | -2.57% | 18% | -1.99% |
| 10–30× | 305 | -0.33% | -0.91% | -1.39% | 26% | -1.30% |
| 30×+ | 232 | -1.00% | -1.63% | -2.17% | 19% | -2.19% |

| closed above prior 2-h high | signals | median +1h | median +4h | mean trail-4% net | win % (4% trail) | mean trail-8% net |
|---|---|---|---|---|---|---|
| yes | 673 | -0.78% | -1.53% | -1.77% | 25% | -1.57% |
| no | 499 | -0.98% | -1.55% | -1.99% | 22% | -1.49% |

| hour (UTC) | signals | median +1h | median +4h | mean trail-4% net | win % (4% trail) | mean trail-8% net |
|---|---|---|---|---|---|---|
| 00–05 | 329 | -0.74% | -1.26% | -1.53% | 27% | -1.75% |
| 06–11 | 254 | -0.83% | -1.92% | -1.97% | 24% | -2.17% |
| 12–17 | 345 | -0.66% | -1.55% | -1.57% | 23% | -0.56% |
| 18–23 | 244 | -1.36% | -1.09% | -2.60% | 21% | -1.98% |

## Noisiest coins (fresh aggressive signals)

| coin | signals | mean trail-4% net | win % | median +4h |
|---|---|---|---|---|
| FORT | 73 | -2.14% | 23% | -1.75% |
| MEZO | 65 | -2.11% | 22% | -2.78% |
| APR | 56 | -0.89% | 21% | -0.39% |
| ICNT | 55 | -0.45% | 38% | +0.37% |
| GROVE | 55 | -2.48% | 16% | -1.63% |
| PROMPT | 50 | -2.57% | 16% | -2.10% |
| LCX | 49 | -2.80% | 14% | -1.74% |
| GTC | 48 | -2.36% | 27% | -2.00% |
| RITUAL | 44 | -1.44% | 36% | -2.56% |
| ALEO | 40 | -2.30% | 18% | -0.74% |
| AMP | 39 | -3.07% | 18% | -3.59% |
| IRYS | 38 | +0.48% | 37% | -0.28% |
| UP | 35 | -1.39% | 29% | -1.08% |
| BIRB | 33 | +2.65% | 39% | -2.37% |
| CAP | 33 | -1.33% | 24% | -0.04% |

Same signal code as paper and live (`scripts/mrh_paper.py`: evaluate / forward_score / trail_pnl). Spread is not modelled; subtract up to 0.6% per hop. Paper twin and live book: `mrh/MRH.md`, `mrh-live/LIVE.md`.
