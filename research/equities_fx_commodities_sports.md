# Equities / options / FX / metals / sports — automatable retail edge survey (2026-10-17)

Legend: [P] peer-reviewed; [I] index/regulator data; [Pr] practitioner backtest; [M] marketing.

## Ranking ($1k–$20k US operator, edge × capacity × automatability ÷ risk)
1. **Sportsbook promo + early +EV harvest** (scan automated, bets hand-placed — bot placement violates book ToS). Realized ROI 1.9–3.5% on 6.8k–23k bets vs Pinnacle close [Pr]; $1–3k one-time sign-up EV; books limit winners within months (MGC data). Highest $/bankroll, but human time, finite lifetime.
2. **Maker on CFTC sports exchanges** — Novig (DCM Jun-2026, API Oct-2026: Ed25519 REST + WS, **zero maker fees**), Kalshi, ProphetX (no public API). Only venue where retail can be the house; no published track record → funded experiment priced off Pinnacle/Circa with hard inventory caps.
3. **Monthly ETF trend + cross-sectional momentum** (SPY/TLT/GLD/DBC, GEM-style). SG Trend CAGR 5.3% MDD 20.6% since 2000 [I]; post-publication decay ~50% [P]. Expect Sharpe 0.3–0.5, −20–30% DD, flat years. Free to run, unlimited capacity, PDT-exempt.
4. **SPAC trust arb** — buy below trust, redeem; T-bill +1–3% with free deal option [Pr/AQR]; illiquidity caps size; screen + limit orders at IBKR.
5. **SPY overnight-only via MOC/MOO** — gross effect intact (5-yr overnight Sharpe 0.5 vs intraday 0.3 [Pr]); net untested at modern ~1%/yr cost; paper test only.

## Rejected with evidence
- 0DTE/weekly option selling: variance premium "small and hard to capture after frictions" [P, Vilkov]; retail loses ~$358k/day [Verdad]; Cboe: customer option P&L ≈ 0; one −10% day ends a $20k account.
- BXM/PUT index premium: Sharpe 0.54 vs S&P 0.56 — beta, not alpha [I].
- VIX carry: all roll; −96% days (XIV 2018); one VX margin > $10k account.
- Leveraged-ETF decay: naive short pair −$3.5k 2015–26; borrow double-digit [Pr].
- FX carry/momentum: no significant combos 2010–25 [P]; 34% of OANDA accounts profitable [I]; spread ≈5%/yr at daily turnover.
- Gold/silver ratio, GLD/GDX pairs: not stationary / no support [Pr]; PAXG/XAUT vs spot: deviation sd ~0.9% < fees.
- PEAD (dead ex-microcaps 2006+), index-addition effect (<1% since 2010s), short-term reversal (costs subsume), closing-auction imbalance (HFT horizon, paid ITCH feed), retail ML predictors (OOS R² negative; Alpha Streams no audited Sharpe).

## Broker/data notes
Alpaca = margin only → PDT <$25k; IBKR cash account PDT-exempt; Robinhood API crypto-only; Schwab Trader API exists. Free data: Alpaca IEX, Polygon EOD, Databento $125 credits, Dukascopy tick FX, Stooq/FRED, Tradier sandbox for delayed options.

Sources: TTU trend report https://www.toptradersunplugged.com/trend-following-performance-report-december-2025/ · Man https://www.man.com/insights/is-this-time-different · decay https://arxiv.org/pdf/2105.01380 · overnight https://elmwealth.com/night-shift/ , https://alphaarchitect.com/trading-costs-wipe-out-the-overnight-return-anomaly/ · PEAD https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again/ · SPAC https://www.aqr.com/-/media/AQR/Documents/Insights/White-Papers/Are-SPACs-Still-Alive.pdf · BXM https://prefblog.com/wp-content/uploads/2026/02/CboeGlobalIndices_BXM-Index_Factsheet_251231.pdf · 0DTE https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4641356 , https://verdadcap.com/archive/zero-day-options , https://cdn.cboe.com/resources/education/research_publications/Retail_Profitability.pdf · VIX https://statoasis.com/overfit/research/master-volatility-futures-vix-trading-strategies · LETF https://www.alphanume-research.com/p/shorting-leveraged-etfs-is-still · FX https://www.bis.org/publ/bisbull90.pdf , https://aaltodoc.aalto.fi/items/0db57fa9-e5c6-4b7d-9dd8-1ae15a8940c6 · metals https://www.mdpi.com/2674-1032/5/1/19 · sports https://networked.substack.com/p/a-view-from-the-pinnacle , https://vegas-odds.com/news/us-sportsbooks-limiting-winning-bettors-proof/ , https://docs.novig.com/ , https://bettorsinsider.com/news/2026/06/18/novig-wins-cftc-approval-to-operate-as-first-sports-focused-federally-regulated-prediction-market/ · ML https://www.nber.org/system/files/working_papers/w31502/w31502.pdf
