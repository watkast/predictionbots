# ORACLE-LAG v4 (15-min BTC "Alpha Engine") — backtest on recorded books

Date: 2026-10-19. Source rule: `15_Min_BTC_Automation.docx` + Pine "Polymarket US Alpha Engine v4".
Code: `scripts/oracle_lag_backtest.py` (window-level replay), `pb/strategies/oracle_lag.py`
(same rule for the paper runner), `configs/oracle_lag.yaml`, paper entries
`oracle_lag_poly_btc15m` / `oracle_lag_kxbtc15m`.

Data: `data` branch recordings 2026-10-16 .. 10-19 — Coinbase BTC-USD trade tape (`btc_index`,
~39 h), Polymarket `btc-updown-15m-*` and Kalshi `KXBTC15M` L2 books + prints. 91 windows had
books; 10 more were dropped (no spot at the open or no book inside minute 10-13:45).

Fills are only what the recorded book could give: the $300 IOC walks the resting asks up to
the 0.85 cap, and the 0.88 exit counts only when a later print at >= 0.88 or a bid at 0.88 is
on the tape. Taker fee 0.07·p·(1-p) on both venues; the exit is a maker (free).

## Result (v4 rule, Pine TWAP, defaults from the doc)

| | windows | signals | ask >= 0.93 (blocked) | entered | hit 0.88 | settled (won) | net |
|---|---|---|---|---|---|---|---|
| Polymarket | 69 | 33 | 23 | 9 | 6 | 3 (0) | **-$123.34** |
| Kalshi | 22 | 11 | 8 | 2 | 1 | 1 (0) | **-$93.78** |

Every entry:

| window (UTC) | venue | call | min | spot-anchor | ask | avg fill | n | outcome | pnl |
|---|---|---|---|---|---|---|---|---|---|
| 10-17 14:30 | polymarket | UP | 10.0 | +29 | 0.75 | 0.800 | 77 | sold 0.88 @ 13.2m | +5.30 |
| 10-17 16:30 | polymarket | DOWN | 10.1 | -42 | 0.84 | 0.845 | 14 | sold 0.88 @ 11.7m | +0.36 |
| 10-17 16:30 | kalshi | DOWN | 10.1 | -42 | 0.85 | 0.850 | 7 | sold 0.88 @ 11.1m | +0.14 |
| 10-17 17:00 | kalshi | DOWN | 11.1 | -11 | 0.56 | 0.655 | 140 | settled LOSS | -93.92 |
| 10-17 17:00 | polymarket | DOWN | 12.1 | -12 | 0.49 | 0.595 | 140 | settled LOSS | -85.59 |
| 10-19 05:45 | polymarket | UP | 10.0 | +42 | 0.84 | 0.845 | 14 | sold 0.88 @ 10.4m | +0.36 |
| 10-19 07:00 | polymarket | UP | 10.0 | +59 | 0.82 | 0.835 | 28 | settled LOSS | -23.65 |
| 10-19 07:15 | polymarket | UP | 11.3 | +34 | 0.60 | 0.695 | 140 | sold 0.88 @ 12.5m | +23.82 |
| 10-19 07:30 | polymarket | UP | 12.1 | +12 | 0.72 | 0.771 | 140 | sold 0.88 @ 14.1m | +13.48 |
| 10-19 08:45 | polymarket | DOWN | 12.3 | -15 | 0.76 | 0.805 | 70 | sold 0.88 @ 12.7m | +4.48 |
| 10-19 10:00 | polymarket | UP | 12.3 | +13 | 0.33 | 0.425 | 140 | settled LOSS | -61.89 |

## Variants (same data)

| variant | signals | entered | hit 0.88 | settled (won) | net |
|---|---|---|---|---|---|
| v4 (veto on), Pine TWAP — default | 44 | 11 | 7 | 4 (0) | -$217 |
| v3 (no reversal veto) | 46 | 12 | 7 | 5 (0) | -$313 |
| doc TWAP (anchored, spot fills the unknown minutes) | 52 | 19 | 15 | 4 (0) | -$213 |
| v4 + chop band widened to $25 | 39 | 7 | 6 | 1 (0) | +$6 |
| v4, no 0.88 exit (hold to settlement) | 44 | 11 | - | 11 (7) | -$162 |

## What the data says

1. **The direction call is fine; the price is not.** Spot-vs-anchor at minute 10 is right
   64-86% of the time. But the book has already moved: in 31 of 44 signals the signalled side
   asks 0.93-1.00, so the doc's own 0.85 cap (and its 0.93 ceasefire) blocks the trade. The
   median ask at signal time is **0.97**.
2. **What gets through at <= 0.85 is the marginal move.** The fills happen when spot is only
   $11-15 from the anchor (the book is at 0.33-0.56 because it is a coin flip) — and all four
   such entries settled against us (-$94, -$86, -$62, -$24). The 0.88 exits exist but are small
   (+$0.14 to +$24) because the resting depth at <= 0.85 was 7-140 contracts, not the 400 the
   $300 size needs.
3. **The $40/round target never happened** in 39 hours. Best single round: +$23.82.
4. **The $0.88 exit does help** (hold-to-settle is -$162 with the same entries) but it caps the
   winners at 3-8c while the losers pay 60-85c.
5. Settlement is the Chainlink/BRTI price at the close vs the open, not a TWAP; the TWAP in
   the rule is a smoother, not the thing being settled.

Widening the chop band to $25 turns the sample green (+$6 on 7 fills) by deleting the four
losers — that is fitting to 11 trades, not evidence.

## Status

Paper-trading on both venues from `configs/paper_matrix.yaml` (every 6 h, GitHub Actions),
`LIVE_TRADING_ENABLED` is structurally false (this repo has no live-money path). Judge after
7 days of ledgers in `reports/README.md`. Bar to clear: positive net on >= 30 fills with the
0.85 cap intact.
