---
title: "Kalshi fees, explained: the 7% formula, the maker fee most people don't know about, and the break-even math"
updated: 2026-11-08
summary: "Kalshi charges a taker fee of 7% × contracts × price × (1 − price), rounded up, on orders that match immediately. On most sports and economics series a resting order also pays 1.75% × contracts × price × (1 − price) when it fills; crypto minute series charge makers nothing. Worked examples and what it does to your break-even."
faq: ["What is the Kalshi trading fee?|A taker fee of 7% × contracts × price × (1 − price), rounded up, on orders that match immediately against resting orders. On a 50¢ contract that is 1.75¢; on 100 contracts at 50¢, $1.75.", "Does Kalshi charge a maker fee?|On series with a non-zero maker multiplier, yes: 1.75% × contracts × price × (1 − price) when a resting order fills. Most sports game lines and economics series (NFL, NBA, MLB, CPI, Fed) carry it; the crypto 5-minute, 15-minute and hourly series and daily weather series do not. Canceling a resting order is free.", "What win rate do I need to break even on Kalshi?|Price plus the fee: at 50¢, about 51.75% holding to settlement, about 53.5% if you trade out early and pay the fee twice.", "Are any Kalshi markets fee-free?|A short list of series carry a zero multiplier (for example the yearly BTC and ETH price series, KXBTCY and KXETHY). Everything else pays the standard taker fee."]
---

Kalshi's fee is a formula, not a flat rate, and it has two parts. From the fee schedule in effect since 7 July 2026:

> **Taker fee = round up(M × 0.07 × C × p × (1 − p))** on orders that match immediately.
> **Maker fee = round up(M_m × 0.0175 × C × p × (1 − p))** when a resting order fills, on series where the maker multiplier is not zero.

C is contracts, p is the price in dollars, M and M_m are per-series multipliers (taker 1 and maker 0 unless the series is listed otherwise). Rounding is up, to the centicent, so the fee is never rounded in your favour.

## What it costs at each price

| Price | Taker fee per contract | On $50 of contracts | Maker fee per contract (where it applies) |
| --- | --- | --- | --- |
| 10¢ | 0.63¢ | $3.15 | 0.16¢ |
| 30¢ | 1.47¢ | $2.45 | 0.37¢ |
| 50¢ | 1.75¢ | $1.75 | 0.44¢ |
| 70¢ | 1.47¢ | $1.05 | 0.37¢ |
| 90¢ | 0.63¢ | $0.35 | 0.16¢ |

Measured against what you put in, cheap longshots carry the heaviest fee: 6.3% of your stake at 10¢, 3.5% at 50¢, 0.7% at 90¢.

## The maker fee most people don't know about

The schedule lists a maker multiplier of 1 for most sports game series (KXNFLGAME, KXNBA, KXMLBGAME and the like) and for economics series (CPI, the Fed, jobs). On those, a resting order that fills pays a quarter of the taker rate. The crypto minute series (5-minute, 15-minute, hourly) and the daily weather series carry a maker multiplier of 0: resting orders there are free, which is why the people quoting both sides of those markets all day can do it.

A short list of series is fee-free in both directions (multipliers 0/0), including the yearly BTC and ETH price series. Combination markets (KXMVE) charge makers double.

## What it does to your break-even

> **Break-even win rate = p + 0.07 × p × (1 − p)** holding to settlement; add the fee again if you trade out early.

At 50¢: 51.75% to settlement, about 53.5% if you exit early. A month of 87 fifty-dollar trades at 50¢ costs about $152 in taker fees before any outcome. [Run your own numbers](/#truecost) or [watch a typical career play out](/simulate.html?venue=kalshi).

## Where the fee hides on screen

Kalshi shows the fee at order entry, but the implied cost does not appear in the price you see on the market page. A contract at 50¢ that you take costs 51.75¢ all-in; a 94¢ contract on a game that is already decided costs 94.4¢ all-in and pays $1, a 6¢ gross margin that becomes 5.6¢ after the fee, which is why those cents are someone's rent, not free money.

*Source: Kalshi fee schedule (kalshi.com/docs/kalshi-fee-schedule.pdf), effective 7 July 2026, read 8 November 2026. Multipliers change by series; check the schedule for the series you trade. Nothing here is investment advice.*
