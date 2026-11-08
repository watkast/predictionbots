---
title: "Polymarket US fees, explained: what you actually pay per trade (and the 6 November 2026 change)"
updated: 2026-11-08
summary: "Polymarket US charges a taker fee of Θ × price × (1 − price) per share. Since 6 November 2026, Θ is 9.5% for accounts under $10,000 of 30-day volume, 8.5% to $50,000, 7.5% to $250,000 and 6.95% above; a new account pays 6.95% for its first week. Resting orders pay nothing. Worked examples, the break-even math, and what the change costs a small trader."
faq: ["What is the fee on Polymarket US?|A taker fee of Θ × contracts × price × (1 − price), where Θ depends on your 30-day taker volume: 9.5% under $10,000, 8.5% to $50,000, 7.5% to $250,000, 6.95% above. Resting (maker) orders pay no fee. New accounts pay 6.95% for days 1 to 7.", "How much is the Polymarket US fee on a 50¢ contract?|At 50¢ the fee is largest: 2.375¢ per share at 9.5% (most accounts), 1.74¢ at 6.95%. On 100 shares that is $2.38 or $1.74.", "Did Polymarket US raise its fees?|Yes. Effective 1:00 PM ET on 6 November 2026 the taker coefficient became tiered by 30-day volume. Accounts under $10,000 moved from 6.95% to 9.5%, a 37% increase. The 6.95% rate now applies only above $250,000 of 30-day volume and to a new account's first seven days.", "How do I avoid the Polymarket US fee?|Post a resting (limit) order instead of taking the displayed price. Resting orders pay no fee on Polymarket US; the fee is charged only on orders that remove liquidity. The cost is that a resting order may not fill."]
---

Polymarket US charges a fee only on orders that **take** liquidity, and the fee is largest in the middle of the price range. The formula, from the venue's published schedule:

> **Fee = Θ × C × p × (1 − p)**, where C is the number of shares, p is the price in dollars, and Θ is a coefficient set by your trailing 30-day taker volume.

## The coefficient since 6 November 2026

| Your 30-day taker volume | Θ | Fee on a 50¢ share | On 100 shares at 50¢ |
| --- | --- | --- | --- |
| New account, days 1 to 7 | 6.95% | 1.74¢ | $1.74 |
| Under $10,000 (most people) | **9.5%** | **2.38¢** | **$2.38** |
| $10,000 to $50,000 | 8.5% | 2.13¢ | $2.13 |
| $50,000 to $250,000 | 7.5% | 1.88¢ | $1.88 |
| $250,000 and up | 6.95% | 1.74¢ | $1.74 |

Before 6 November everyone paid 6.95%. The change raised the fee for an ordinary account by 37% and left the old rate for the largest accounts and for a new account's first week. Volume is measured in dollars paid or received, not face value: a buy counts C × p, a sell counts C × (1 − p). Tiers reset daily on a rolling 30-day window of completed days.

## Why the middle costs the most

p × (1 − p) peaks at p = 0.5 and falls toward zero at either end:

| Price | p × (1 − p) | Fee per share at 9.5% | Fee as % of what you pay |
| --- | --- | --- | --- |
| 10¢ | 0.09 | 0.86¢ | 8.6% |
| 30¢ | 0.21 | 2.00¢ | 6.7% |
| 50¢ | 0.25 | 2.38¢ | 4.8% |
| 70¢ | 0.21 | 2.00¢ | 2.9% |
| 90¢ | 0.09 | 0.86¢ | 1.0% |

Measured against what you put in, the fee is heaviest on cheap longshots: a 10¢ share costs 8.6% of your stake in fees before the outcome is known.

## What it does to your break-even

A share bought at p pays $1 if it wins and $0 if it loses. With no fee you break even at a win rate equal to the price. With the fee you need:

> **Break-even win rate = p + Θ × p × (1 − p)** (holding to settlement; trading out early pays the fee again)

At 50¢ and 9.5% that is 52.4% rather than 50%. At 9.5% across a month of 87 fifty-dollar trades at 50¢, the fees alone are about $207, whatever the outcomes. [See your own numbers](/#truecost), or [watch a few hundred simulated careers play out](/simulate.html?venue=pmus).

## The one honest way to pay less

Resting orders pay nothing. If you place a limit order below the current offer and wait, the fee is zero when it fills. The cost is uncertainty: the market may move away and the order may never fill, and the people quoting both sides for a living are better at this than you are. Rebates exist for very large makers (from $10 million of monthly maker volume), and taker rebates start at $250,000 of monthly taker volume; neither applies to an ordinary account.

## Rounding and small trades

Fees round to the nearest cent using banker's rounding (half to even), and on small trades they can round to $0.00: 1 share at 50¢ carries a 2.4¢ fee that rounds to 2¢; 1 share at 5¢ carries a 0.45¢ fee that rounds to $0.00. Combo (multi-leg) orders use a separate, higher formula.

*Source: Polymarket US fee schedule, docs.polymarket.us/fees, read 8 November 2026. Fees change; the date on this page is when we last checked. Nothing here is investment advice.*
