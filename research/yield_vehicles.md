# Yield vehicles for a $1k–$50k US individual: ranked by risk-adjusted after-tax yield (2026-10-17)

Purpose: decide where idle bot capital and the "safe base" should sit, with honest current numbers. Every number has a URL; official sources (Fed H.15, FRED, IRS, SEC, fund pages) preferred. Grades as in README: [A] official/large-sample, [B] credible practitioner data, [C] marketing.

**Macro backdrop (sets every yield below).** Fed funds target 3.75–4.00% after a 25 bp *hike* on 2026-09-16 (first since 2023); effective 3.88%; futures ~48% for another hike 2026-10-28; Sept SEP median 4.1% end-2026. CPI 3.7% y/y headline, core 2.6%; PCE 3.4%/3.0%. Curve is steep: 3-mo 4.10, 1-yr 4.27, 2-yr 4.77, 5-yr 4.91, 10-yr 5.10, 30-yr 5.43; TIPS real 5-yr 2.58, 10-yr 2.78 (H.15, 2026-10-15). Sources: https://www.federalreserve.gov/releases/h15/ [A], https://www.yxinsights.com/p/fomc-october-2026 [B].

**Tax convention used for "after-tax" columns:** mid-bracket single filer, 22% federal ordinary, 15% federal qualified-dividend/LTCG, 5% flat state (adjust for your state; TX/FL/WA etc. → state column is zero and HYSA/CDs/corporates close most of the gap). Treasuries, I/EE bonds, TIPS and Treasury-only MMFs/ETFs are state-tax-exempt; HYSA/CD/corporate/CLO/BDC/stablecoin income is fully taxable ordinary; muni interest is federal-exempt.

---

## 0. The ranking (after-tax, risk-adjusted, for a passive holder)

| Rank | Vehicle | Gross today | After-tax (22/5) | Risk | Bot-manageable? |
|---|---|---|---|---|---|
| 1 | I-bond (buy ≤ Oct 31 to lock 4.26% for 6 mo; $10k/yr cap) | 4.26% composite, tax-deferred | ≈3.32% at redemption, 0% until then | zero credit; 12-mo lock; 3-mo penalty <5 yr | No (TreasuryDirect only, no API) |
| 2 | 26/52-wk T-bill ladder, auto-roll at Fidelity/Schwab | 4.21–4.44% | 3.28–3.46% | zero credit; reinvestment | Set-and-forget auto-roll; IBKR API for ≥$10k lots |
| 3 | 5-yr TIPS (real 2.58% + CPI) | ~6.3% nominal at 3.7% CPI | ~4.9% if CPI holds; real 2.0% after tax | zero credit; 5-yr duration; phantom income | Broker, no auto-roll |
| 4 | Treasury FRN ETF (USFR) / SGOV as sweep | 3.97% / 3.74% SEC | 3.10% / 2.92% | zero credit; 0.15/0.09 ER drag | Yes — any broker incl. Alpaca API |
| 5 | Brokered non-callable CD 1-yr 4.50% / 5-yr 5.15% | 4.50 / 5.15% | 3.29 / 3.76% | FDIC; illiquid (secondary only) | Broker, no auto-roll |
| 6 | HYSA (best base rate, Raisin partners 4.30%) | 4.30% | 3.14% | FDIC; rate float | Own account; some APIs via Raisin |
| 7 | JAAA (AAA CLO, floating) | 4.77% SEC (6/30) | 3.48% | AAA tranche; 2020-style 5% drawdown; liquidity | Yes (ETF) |
| 8 | A-rated corporates 5-yr 5.02% / iBonds-IBDV ~4.8% YTM | 5.02% | 3.66% | IG credit, 4-yr duration | Yes (ETF); ladders need human |
| 9 | PFF preferreds | 6.76% SEC (QDI-heavy) | ~5.4% | bank-subordinated, long duration, −30% in 2020/2023 | Yes (ETF) |
| 10 | HYG high yield | 7.29% SEC; OAS 323 bp | ~5.3% minus ~1.5–2% expected loss ≈ 3.5% | US spec default 5.3% vs spread 3.2% — not paid | Yes (ETF) |

Anything below row 8 only "wins" on headline yield; after expected losses and taxes it sits at or below the T-bill with far worse tails. **Rows 1–4 are the safe base; rows 5–7 are marginal gains worth taking only when state tax is zero or the money is in an IRA.**

---

## 1. Government tier

| Instrument | Yield today | Source | After-tax 22/5 | Liquidity / lock | Min | Risks | Automation | Where held |
|---|---|---|---|---|---|---|---|---|
| T-bill 4-wk | 4.00% (H.15 10/15); 4.02% CE (10/16) | https://www.federalreserve.gov/releases/h15/ · https://treasuryratewatch.com/daily/treasury-bill-rates | 3.12% | Weekly auctions; secondary sale same day | $100 TD / $1,000 broker | None credit; reinvestment risk if Fed cuts | TD "schedule reinvestment" up to 2 yrs; Fidelity/Schwab auto-roll (auction only; Schwab excludes 52-wk) https://www.nerdwallet.com/investing/best/best-brokers-for-treasury-bills-bonds-notes | Fidelity, Schwab, Vanguard, IBKR (0.2 bp, **$5 min → 0.5% on a $1k lot; use ≥$10k lots**) https://www.interactivebrokers.com/en/pricing/commissions-bonds.php ; Alpaca only via Broker API partners, $1k min, no auto-roll https://docs.alpaca.markets/us/docs/fixed-income |
| T-bill 8-wk | 4.10% CE (10/16) | treasuryratewatch | 3.20% | same | same | same | same | same |
| T-bill 13-wk | 4.10% (H.15) / 4.18% CE | H.15 / treasuryratewatch | 3.20–3.26% | same | same | same | same | same |
| T-bill 26-wk | 4.21% (H.15) / 4.35% CE | same | 3.28–3.39% | same | same | same | same | same |
| T-bill 52-wk | 4.27% (H.15) / 4.44% CE | same | 3.33–3.46% | monthly auction | same | same | TD yes; Schwab no | same |
| 2-yr note | 4.77% | H.15 | 3.72% | monthly auction; liquid secondary | $100/$1,000 | ~1.9 duration | TD reinvest; no broker auto-roll for notes | any broker |
| 5-yr note | 4.91% | H.15 | 3.83% | | | 4.5 duration | | |
| 10-yr note | 5.10% | H.15 | 3.98% | | | 8 duration | | |
| TIPS 5-yr real | 2.58% real (10/15); RJ 2.65% (10/13) | H.15 · https://www.raymondjames.com/-/media/rj/dotcom/files/wealth-management/market-commentary-and-insights/bond-market-commentary/weekly_rate_monitor.pdf | real ≈2.0% after fed tax; inflation accrual taxed annually (phantom income) → hold in IRA | Apr/Oct auctions + reopenings; liquid | $100/$1,000 | duration; deflation floor only at maturity | TD reinvest | any broker; best inside IRA |
| TIPS 10-yr real | 2.78% | H.15 | | | | | | |
| I-bond | **4.26% composite** (0.90% fixed + 3.34% annualised inflation), May–Oct 2026 purchases; Nov reset projected ~3.8% at 0.90% fixed, 4.1–4.2% if fixed rises | https://tipswatch.com/2026/04/30/treasury-holds-i-bond-fixed-rate-at-0-90-composite-rate-rises-to-4-26/ · https://finbarrow.com/savings/i-bond-rate-november-2026-tracker/ | state-exempt, fed-deferred until redemption; ≈3.32% at 22% | **12-mo hard lock; forfeit last 3 months' interest if redeemed <5 yr** | $25; **$10k/person/yr electronic; paper-via-refund ended 2025-01-01** https://tipswatch.com/2024/09/01/treasury-is-ending-paper-i-bonds-as-a-tax-refund/ | none; fixed rate 0.90% is the only part that persists | **None — TreasuryDirect only, no API; gifting trick stores extra years** | Own TD account |
| EE bond | 2.40% fixed (May–Oct 2026); **guaranteed doubling at 20 yr = 3.53%/yr** | tipswatch 2026-04-30 | state-exempt, deferred | 12-mo lock, 3-mo penalty <5 yr; doubling only if held exactly 20 yr | $25; $10k/yr | opportunity cost vs 20-yr Treasury (~5.3%) | none | TD only |
| Treasury FRN (2-yr, indexed 13-wk bill + spread) | via USFR: 3.97% SEC, 3.76% distribution (10/15), ER 0.15% | https://www.wisdomtree.com/investments/etfs/fixed-income/usfr | 3.10% (state-exempt) | daily | 1 share | none credit; zero duration; ETF ER | yes — ETF | any broker incl. Alpaca |
| AAA munis (for a 22% filer) | 1-yr 3.28%, 5-yr 3.50%, 10-yr 3.96%, 30-yr 5.14% (RJ 10/13) | RJ weekly rate monitor | TEY at 22%: 4.21 / 4.49 / 5.08 / 6.59% → **loses to Treasuries ≤10 yr, wins only at 30 yr**; RJ's 37%-bracket TEY 5.20/5.56/6.29/8.16 | secondary; retail spreads wide | $5k lots; VTEB ETF | credit, call, duration | ETF yes | broker |

Take-aways: (a) at a 22% bracket munis are not worth it short of 30-yr paper; (b) the I-bond is the single best risk-free after-tax rate in the table **only because of the 0.90% fixed + state exemption + deferral** — the projected Nov rate (~3.8%) drops it below a 52-wk bill, so buy the 2026 allotment before Oct 31; (c) TIPS real 2.6–2.8% is the highest since 2008-era levels and is the only instrument here that is a real hedge against the 3.7% CPI the Fed is hiking into.

## 2. Cash-like tier

| Instrument | Yield today | Source | After-tax 22/5 | Liquidity | Min | Risk | Automation | Where |
|---|---|---|---|---|---|---|---|---|
| HYSA — Raisin partners (Northpointe/Western Alliance) | 4.30% | https://www.fool.com/money/banks/articles/top-savings-account-rates-today-oct-17-2026/ | 3.14% | 1–3 day ACH | $1 | FDIC via partner; teaser locks 60–90 days | Raisin: one login, no public API | own account |
| HYSA — promos (Axos ONE 5.00% 6 mo; Go2bank 4.50% ≤$5k) | 4.5–5.0% | same | 3.3–3.65% | | | conditions; capped balances | none | own |
| HYSA — E*TRADE Premium 4.25% (6-mo guarantee), SoFi 4.20% with DD | 4.20–4.25% | same | 3.1% | | | | none | own |
| National avg savings | 0.37% | same | — | | | | | |
| VMFXX (Vanguard Federal MMF) | 3.68% (dividend yield 10/1) | https://stockanalysis.com/quote/mutf/VMFXX/dividend/ | ~2.9% (partly state-exempt, repo-heavy) | T+0/T+1 | $3,000 | none | sweep | Vanguard only |
| SWVXX / SNSXX (Schwab prime / Treasury MMF) | 3.71% / 3.60% 7-day (10/16) | https://www.schwabassetmanagement.com/products/money-fund-yields | 2.71% / 2.81% | T+1 | $0 | prime fund gates possible | Schwab API (thinkorswim) | Schwab |
| SGOV (0–3 mo T-bill ETF) | 3.74% SEC, ER 0.09%, $116B (10/15) | https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf | 2.92% (state-exempt) | intraday | 1 share | none; ETF spread 1 bp | yes — any API broker | Alpaca/IBKR/Schwab/Fidelity |
| BIL (1–3 mo T-bill ETF) | 3.72% SEC, ER 0.1353% | https://www.ssga.com/us/en/intermediary/etfs/spdr-bloomberg-1-3-month-t-bill-etf-bil | 2.90% | intraday | | | yes | same |
| USFR (Treasury FRN ETF) | **3.97% SEC** | wisdomtree (above) | 3.10% | intraday | | | yes | same |
| Bank CD 1-yr best (E*TRADE 4.75%, Barclays/BTG/Popular 4.50%) | 4.75% | https://www.bankrate.com/banking/cds/best-1-year-cd-rates/ | 3.47% | early-withdrawal penalty | $0–10k | FDIC | none | own |
| Bank CD 5-yr best (Popular Direct 5.00%) | 5.00% | bankrate | 3.65% | penalty | $10k | FDIC | none | own |
| Brokered CD non-callable (10/02–10/07): 3-mo 4.20, 6-mo 4.25, 1-yr 4.50, 2-yr 4.90, 3-yr 5.00, **5-yr 5.15** (Morgan Stanley/Capital One/UBS) | 4.20–5.15% | https://www.depositaccounts.com/community/promos/63559-highest-brokered-cd-rates-10022026.html | 1-yr 3.29%; 5-yr 3.76% | secondary market only (bid-ask) | $1,000 | FDIC per issuer; no auto-roll | Fidelity/Schwab/Vanguard new-issue, commission-free | broker, no API ladder |
| Bank-bonus churning (ties to non_trading_ventures.md row 7) | $150–600/bonus; documented $2.8k–$21.6k/yr | https://travelwithgrant.boardingarea.com/?p=30372 | ordinary income; on a $10k float cycled 3×/yr ≈ 6–15% effective | 60–90 day holds | $500–15k DD/deposit requirements | ChexSystems/identity cap; KYC needs a human every time | none | own accounts |

Observation: the SGOV/USFR ETF route costs 25–50 bp vs rolling bills yourself (ER + ETF holds slightly shorter paper), but it is the only cash sleeve a bot can move in and out of the same day at Alpaca/IBKR without a human. **Brokered 5-yr CD 5.15% vs 5-yr Treasury 4.91%: after state tax the Treasury wins (3.83% vs 3.76%) and is liquid — CDs only beat Treasuries in zero-income-tax states.**

## 3. Credit tier

| Instrument | Yield today | Source | After-tax 22/5 | Liquidity | Min | Credit / duration / platform risk | Auto | Where |
|---|---|---|---|---|---|---|---|---|
| A-rated corporate index YTW: 1-yr 4.47, 2-yr 4.80, 5-yr 5.02, 10-yr 5.24 (10/13) | 5.02% (5-yr) | RJ weekly rate monitor | 3.66% | liquid via ETF; single bonds wide | $1k bonds / 1 share ETF | ~20–40 bp historical IG annual loss; 4-yr dur | iBonds/BulletShares defined-maturity ETFs (IBDV Dec-2030: ~4.8% YTM, ER 0.10%, May data) https://www.ishares.com/us/products/314496/ ; Alpaca Broker API trades IG bonds | any broker |
| Agency MBS — MBB | 4.46% SEC, dur 5.75, ER 0.04% (10/15) | https://www.ishares.com/us/products/239465/ishares-mbs-etf | 3.26% (state-taxable) | intraday | 1 sh | negative convexity; −12% in 2022 | ETF | any |
| Preferreds — PFF | 6.76% SEC, 5.56% trailing, ER 0.45% (9/30) | https://www.ishares.com/us/products/239826/ishares-us-preferred-stock-etf | ~5.4% (largely QDI at 15%) | intraday | 1 sh | bank-sub capital; −30% drawdowns 2020/2023; perpetual duration | ETF | any |
| High yield — HYG | 7.29% SEC, 7.95% YTM, dur 3.2, ER 0.49% (10/15); **OAS 323 bp (FRED 10/15)** | https://www.ishares.com/us/products/239565/ishares-iboxx-high-yield-corporate-bond-etf · https://fred.stlouisfed.org/series/BAMLH0A0HYM2 | 5.32% before losses | intraday | 1 sh | **US spec-grade default 5.3% (Aug-26, Moody's; Dec-26 f'cast 4.3%; global 4.5% vs 4.2% avg)** https://www.ftportfolios.com/Blogs/InvestBlog/2026/9/17/factoid---thursday,-september-17,-2026 — at ~40% recovery that is ~2.5–3% annual loss vs 3.2% spread: spread barely covers default; long-run median OAS ~450–500 bp → tight | ETF | any |
| CLO AAA — JAAA | 4.77% SEC, ER 0.20%, $28.4B, dur 0.06 (6/30) | https://cdn.janushenderson.com/webdocs/FactSheet_JAAA_ETF_2026_06_exp_2026_10.pdf | 3.48% | intraday; Mar-2020 −5% NAV gap | 1 sh | AAA tranche never impaired historically; liquidity/price gaps; SOFR float | ETF | any |
| CLO BBB/BB — JBBB | 5.76% SEC, ER 0.47%, $1.52B (9/30) | https://www.janushenderson.com/en-us/advisor/product/jbbb-b-bbb-clo-etf/ | 4.20% | intraday | 1 sh | mezz tranche: −20% in a 2020-type shock; loan default sensitivity | ETF | any |
| Public BDCs (ARCC ~10.7%, HTGC 12.7% as of Mar-26; sector cash yield ~8.3%) | 8–13% | https://www.kiplinger.com/investing/where-to-find-the-top-yields-for-the-rest-of-2026 · https://angelinvestorsnetwork.com/market-analysis/bdc-non-accrual-rates-q2-2026-data | ~6–9% (non-qualified) | intraday equity | 1 sh | **non-accruals rising: top-10 BDCs 3.95% at cost (Q2-26, +20 bp q/q), adjusted 5.95%; FSK 7.1%**; leverage ~1.2×; equity-like drawdowns (−50% 2020) | ETF (PBDC) / stock | any |
| Private-credit non-traded BDCs / interval funds (BCRED, OCIC, OTIC, Apollo ADS, Ares ASIF) | 8–11% distribution | https://angelinvestorsnetwork.com/alternative-investments/bdc-redemption-crisis-2026-private-credit-liquidity-gates | — | **GATED: 10 of 16 Fitch-tracked breached 5%/qtr caps in Q2-26; $15.6B requested; avg request 10.3% of shares, OTIC 38.1%** | $2.5k–25k | you cannot exit when you want; NAV marks lag | none | own / advisor |
| P2P — Prosper notes | hist. net ~5.5% (June-24) ; ~11% coupon − 4% losses − 1% servicing | https://investormint.com/entrepreneurship/best-p2p-lending-platforms-2026-prosper-lendingclub-upstart | ~4% | 3–5 yr amortising; thin secondary | $25/note | unsecured consumer; state eligibility | Prosper has an investor API (auto-invest) | own |
| P2P — LendingClub retail notes | **closed to retail** | same | — | — | — | — | — | — |
| Worthy Property Bonds 2 | 6.5% (cut from 7% Jan-26) | https://www.sec.gov/Archives/edgar/data/0001971864/000149315226033334/partii.htm | 4.7% | demand (5-day notice) but **"substantial doubt… going concern"**; FY-26 net loss $1.75M; shareholder deficit $4.05M; $37–55M bonds vs $12.7M loans | $10 | unsecured, uninsured; **avoid** | — | own |
| Yieldstreet → Willow Wealth | targets 7–8% | https://angelinvestorsnetwork.com/alternative-investments/yieldstreet-review-2026-returns-fees-accredited-investors | — | per-deal lockups | $10k | **>$208M documented losses; RE default rate ~30%; −2%/yr RE 2015–25; SEC $1.9M (2023); $9M class settlement (2025); 3.3–6.7%/yr all-in fees** | — | **avoid** |

Verdict on credit for a $1k–$50k passive holder: only **JAAA** (AAA, floating, +15 bp after-tax vs T-bill) and a **defined-maturity IG ladder inside an IRA** earn their risk. HY at 323 bp OAS against a 5.3% default rate is the worst risk/reward in the memo; private credit is uninvestable while gates are active.

## 4. Equity income / alternatives

| Vehicle | Headline yield | Total return evidence (nominal, div reinvested, 2022-05-04 → 2026-10-16) | Source | Tax | Verdict |
|---|---|---|---|---|---|
| JEPI | 7.18% fwd / 8.00% TTM, ER 0.35% | **7.99%/yr vs SPY 15.36%**; 5-yr price −7.6% | https://totalrealreturns.com/n/SPY,JEPI,JEPQ,SCHD,VNQ,AMLP · https://www.dividendvision.com/compare/jepi-vs-xyld · https://finance.yahoo.com/markets/options/articles/jepq-just-paid-biggest-distribution-200044822.html | ELN income = ordinary (not QDI) | headline yield ≠ return; half of SPY with 70% of the drawdown (−13.3% vs −18.8%) |
| JEPQ | ~9–10% fwd | 15.37%/yr ≈ SPY; DD −20.1% | same | ordinary | matched SPY in a tech bull; no evidence it adds vs QQQ |
| XYLD | 8.61% fwd / 10.35% TTM, ER 0.60% | 8.10%/yr; DD −17.2% | same | mostly ROC | NAV erodes; return of your own capital |
| QYLD | ~11–12% | 10.91%/yr; DD −19.9% | totalrealreturns | ROC | same |
| SCHD | ~3.3% | 10.19%/yr | same | QDI | fine as equity, not "yield" |
| NOBL aristocrats | 2.17% | — | https://walnutinvest.com/etf/nobl/dividend | QDI | not a yield vehicle |
| VNQ REITs | 3.4% | **1.26%/yr**, DD −27% | same | ordinary (199A 20% deduction) | rate-sensitive; lost to T-bills 4 yrs running |
| AGNC mREIT | 13.5–16.5% | dividend "long periods of decline"; price tracks dividend; BV $8.58, price $8.72 (10/16) | https://www.fool.com/investing/2026/08/05/agnc-investment-trades-28-above-its-858-book-value/ | ordinary | levered MBS carry; yield is compensation for BV erosion |
| AMLP midstream | ~7% (ET 6.9%, EPD 5.8%) | 14.90%/yr; DD −20.9% | same | ROC-deferred (AMLP is C-corp: no K-1) | best realised among "income" sleeves but it is an energy-equity bet |
| CEFs at discount | taxable-FI CEF avg discount **−9.98%** (9/30/26) vs 10-yr avg −4.16%; all CEFs −8.40% vs −5.36% | https://www.ftportfolios.com/Commentary/Insights/2026/10/6/third-quarter-2026 | varies | Discount mean-reversion is real but slow (Pontiff 1995; discounts last this wide Dec-2023 then closed ~4 pts in 12 mo ≈ +4% one-off); 1–1.5% ER + leverage; harvesting needs a screener + patience, bot-able at IBKR | [B] modest, episodic edge; not passive income |
| Buy-write on own holdings | SPX 30-delta monthly ≈ 1–1.5%/mo premium | CBOE BXM long-run: ~SPX return with ~2/3 vol; underperforms in bull runs | (see equities memo options-selling section) | short-term gains | only in an IRA, only on positions you'd sell anyway |

Bottom line: none of these is "yield" in the risk-free sense. JEPI-style funds convert upside into ordinary-taxed income; the honest comparison is total return, where SPY beat every covered-call product since 2022. The one defensible income-alternative idea is **harvesting taxable-FI CEF discounts when >2× the 10-yr average (now)** — episodic, not a base.

## 5. Crypto / stable yield (brief; see crypto_systematic.md)

| Vehicle | Rate | Source | Access / tax | Risk | vs. alternatives |
|---|---|---|---|---|---|
| Coinbase USDC rewards | **3.75% APY, Coinbase One members only ($4.99/mo)**, weekly, "subject to location" | https://www.coinbase.com/usdc | fully taxable ordinary; no state exemption | unsecured exchange claim; rate changed 4× since 2023 (cut ~90% in 2023) https://www.theblock.co/linked/67284/security | **Strictly worse than SGOV 3.74% state-exempt/0.09% ER with SIPC**; the $60/yr membership alone is 0.6% on $10k |
| Tokenised T-bills | BUIDL $5M min, qualified purchasers; OUSG $100k, accredited; USDY non-US only; BENJI (Franklin) retail, $20 | https://eco.com/support/en/articles/15254021-tokenized-treasury-kyc-requirements-2026-buidl-ousg-benji-access-tiers | 3.6–3.9% net of 15–50 bp fees | smart-contract + custody; BENJI is the only retail door and yields ≈ SGOV | no reason for a US retail holder to leave the ETF |
| ETH staking via Coinbase | ~1.7% net (Sept-26) after 25–35% commission | https://wealthvieu.com/banking/coinbase/staking/ | ordinary income at receipt | slashing (Coinbase indemnifies some), unbonding days–weeks, state blocks (NJ/CA etc. have been restricted) | you are long ETH; the 1.7% is noise vs 60% vol |
| SOL staking via Coinbase | ~3.4% net | same | same | same + 2–3 day unbond | same |
| Funding-carry bot (this repo) | backtest always-in ~5%/yr over T-bills, maxDD 4–5%, 5–10 liquidation events at 50% collateral; thresholded ~0 excess since 2022 (reports/carry_backtest.md) | configs/ventures.yaml | short-term gains | hedge-leg liquidation, venue/API churn, spot fees | the only crypto "yield" with positive expected excess over bills, and it is unproven on US venues |

## 6. Tax-advantaged wrappers and "guaranteed returns" (2026 limits)

| Wrapper | 2026 limit | Source | Effect on the ladder above |
|---|---|---|---|
| 401(k)/403(b)/TSP deferral | $24,500; +$8,000 age 50; +$11,250 age 60–63 | https://www.irs.gov/newsroom/401k-limit-increases-to-24500-for-2026-ira-limit-increases-to-7500 | **Employer match is a 50–100% instant return — nothing in this memo competes**; traditional deferral = 22% immediate |
| IRA (Trad/Roth) | $7,500; +$1,100 age 50; Roth phase-out $153–168k single / $242–252k MFJ | same | Roth is where TIPS (phantom income), BDCs, JAAA, IG corporates and covered-call ETFs belong: converts ordinary 22+5% to 0% |
| HSA | $4,400 self / $8,750 family; HDHP min deductible $1,700/$3,400 | https://www.irs.gov/pub/irs-drop/rp-25-19.pdf | triple-exempt: a 4.3% T-bill in an HSA is 4.3% after tax (vs 3.33%) |
| Series I via tax refund | **gone since 2025-01-01**; $10k electronic/person only (gift box for future years) | tipswatch 2024-09-01 | — |
| 529 | state deduction varies ($0–$10k+); federal none | — | only if the money is for education |
| Paying down debt >7% | guaranteed, after-tax, risk-free = coupon | — | any card/auto/private loan above ~4.4% beats the entire safe tier after tax |
| Saver's credit | AGI ≤ $40,250 single / $80,500 MFJ | IRS release above | 10–50% credit on first $2k |

Ordering for new dollars: match → >7% debt → HSA → Roth (hold the credit/TIPS sleeve there) → I-bond cap → taxable T-bill ladder.

---

## 7. Allocation sketch: the bot-managed "safe base"

Design constraints: (1) a bot must be able to move the cash sleeve without a human; (2) IBKR's $5 minimum makes direct bills uneconomic below ~$10k lots (0.05% at $10k, 0.5% at $1k); (3) Fidelity/Schwab auto-roll is free but has no public order API, so it is a set-once human action; (4) Alpaca's fixed-income is Broker-API-partner only, so at Alpaca the bot's cash instrument is SGOV/USFR; (5) I-bonds are TreasuryDirect-only.

### $10k
| Sleeve | $ | Instrument | Gross | After-tax 22/5 | Who touches it |
|---|---|---|---|---|---|
| Sweep / dry powder | 2,000 | USFR (or SGOV) at the API broker | 3.97% | 3.10% | bot |
| Ladder | 8,000 | 4 × $2k 26-wk bills at Fidelity auto-roll (rungs 6 wks apart), or 52-wk if you believe the Fed is done | 4.21–4.44% | 3.28–3.46% | human once; auto-roll thereafter |
| **Blend** | 10,000 | | **≈4.3%** | **≈3.3%** ($330/yr) | |
| Optional, separate cash | +10,000 | I-bond before Oct 31 (locks 4.26% to Apr-27) | 4.26% deferred | ≈3.32% | human once at TD |

### $50k
| Sleeve | $ | Instrument | Gross | After-tax 22/5 | Who |
|---|---|---|---|---|---|
| I-bond cap | 10,000 | TreasuryDirect, buy by Oct 31 | 4.26% (deferred, state-exempt) | 3.32% | human once/yr |
| Sweep | 5,000 | USFR/SGOV at IBKR or Alpaca | 3.97% | 3.10% | bot |
| Ladder | 30,000 | 3 × $10k 26-wk bills at IBKR via API ($5/lot = 0.05%), rungs 2 months apart; bot re-buys at auction (IBKR supports auction orders) — or Fidelity auto-roll if you'd rather not code it | 4.21–4.35% | 3.28–3.39% | bot (IBKR) or auto-roll |
| Real-rate hedge | 5,000 | 5-yr TIPS in the Roth IRA (phantom income → tax-free) | 2.58% real (~6.3% nominal at 3.7% CPI) | 2.58% real | human once |
| **Blend** | 50,000 | | **≈4.4% nominal** | **≈3.4% + inflation protection on 10%** (~$1,700/yr) | |

Expected after-tax yield on the safe base: **~3.3–3.4%** at a 22/5 bracket, **~4.3% in a no-income-tax state or inside an HSA/Roth**. Reinvestment risk is symmetric right now (futures split on a hike; SEP says 4.1% end-26) — a 26-wk ladder captures a hike within ~3 months and gives up only ~10 bp vs the 52-wk if cuts come instead.

**Human-once checklist:** TreasuryDirect account (ID.me-style verification, bank link; I-bond + optional EE); Fidelity or Schwab brokerage for auto-roll (or IBKR Pro for API bills — enable bond permissions, fixed-income data); Roth IRA at the same broker for TIPS/credit sleeve; Alpaca live account only if that is where the trading bots already sit (its cash instrument is SGOV/USFR); Coinbase One not worth it for USDC. Everything else — rolling, sweeping, rebalancing between sweep and ladder — is API-able at IBKR/Alpaca.

**What the bot should actually do:** keep ≥X days of margin/collateral in USFR; on each ladder rung maturity, re-bid the auction (IBKR) or let auto-roll (Fidelity) handle it; once a year, on Oct 15–31 and Apr 15–30, flag the human when the projected I-bond reset is below the 52-wk bill (sell rule after the 12-mo lock: redeem when composite < 52-wk bill after-tax for two consecutive resets).

## 8. Shortlist (what gets built / recorded)

1. **safe_yield_base** — USFR sweep + T-bill ladder (auto-roll or IBKR API) + I-bond cap: ~4.3% gross / ~3.3% after-tax, zero credit risk. The hurdle every bot must clear. → ventures.yaml `safe_yield_base`.
2. TIPS 5-yr at 2.58% real inside the Roth — a one-time human action, not a bot.
3. CEF taxable-FI discount harvesting when discount >2× 10-yr avg (now −10% vs −4.2%) — episodic, IBKR-scriptable, revisit in the equities memo.
4. JAAA as the only credit sleeve worth holding in taxable (+15 bp after tax over bills; AAA).
5. Everything else (HY, BDC, private credit, P2P, Worthy, Yieldstreet/Willow, covered-call ETFs, mREITs, USDC rewards, exchange staking) is either underpaid for its risk today or returns your own capital labelled as yield.
