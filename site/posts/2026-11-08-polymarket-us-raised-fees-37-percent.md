---
title: "Polymarket US raised the small trader's fee 37% on 6 November. The welcome rate hides it for a week."
date: 2026-11-08
author: PredictionBots
summary: "Effective 1:00 PM ET on 6 November 2026, Polymarket US tiers its taker fee by 30-day volume: 9.5% × price × (1 − price) for anyone under $10,000, down to 6.95% above $250,000. Everyone paid 6.95% before. New accounts get the old rate for seven days. What it costs, in dollars, at the sizes people actually trade."
tags: [news, polymarket, fees]
---

Polymarket US's fee page now reads differently from the one most of its users signed up under. From the schedule itself, effective 1:00 PM ET on 6 November 2026:

| Your 30-day taker volume | Taker coefficient Θ | Before 6 Nov |
| --- | --- | --- |
| New account, days 1 to 7 | 6.95% | 6.95% |
| Under $10,000 | **9.5%** | 6.95% |
| $10,000 to $50,000 | 8.5% | 6.95% |
| $50,000 to $250,000 | 7.5% | 6.95% |
| $250,000 and up | 6.95% | 6.95% |

The fee is Θ × shares × price × (1 − price), charged on orders that take liquidity. For an account trading less than $10,000 a month, which is almost everyone, Θ went from 6.95% to 9.5%: a 37% increase. The largest accounts keep the old rate.

## What it costs

| Trade | Fee before | Fee now (under $10k) | Extra |
| --- | --- | --- | --- |
| 100 shares at 50¢ ($50) | $1.74 | $2.38 | $0.64 |
| 100 shares at 30¢ ($30) | $1.46 | $2.00 | $0.54 |
| 20 trades a week at $50, 50¢ (a month) | $151 | $207 | $56 |
| Break-even win rate at 50¢, held to settlement | 51.7% | 52.4% | +0.7 points |

The seven-day welcome rate means a new account's first week of fees looks like the old schedule. From day eight, tier placement uses the higher of projected or trailing volume, and the ordinary account lands at 9.5%.

## What did not change

Resting (maker) orders still pay nothing. Maker rebates still begin at $10 million of monthly maker volume and taker rebates at $250,000 of monthly taker volume. Fees still round to the nearest cent, half to even. Combo orders keep their separate, higher formula.

## What it means for you

If you take the displayed price, your cost of playing just rose by more than a third, and the only lever you control is the one the schedule leaves fee-free: post a resting order and wait, accepting that it may not fill. Everything else is arithmetic: [the full schedule, worked at every price](/learn/polymarket-us-fees.html); [your own numbers](/#truecost); [what a month of this looks like](/simulate.html?venue=pmus).

*Source: docs.polymarket.us/fees, read 8 November 2026. We take no money from any venue for saying this; if that changes, [this page changes first](/#honest).*
