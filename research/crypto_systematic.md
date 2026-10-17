# Crypto automatable-edge survey (2026-10-17) — evidence-graded

Grades: [A] peer-reviewed / large-sample; [B] credible practitioner data; [C] marketing.

## Ranking for a $1k–$20k US operator (edge × capacity × automatability ÷ risk)

1. **BTC/ETH funding carry on CFTC-regulated US perps** (Coinbase nano perps Jul-2025 / Kraken Derivatives US via Bitnomial Jun-2026), threshold entry, idle collateral in T-bills or core Aave USDC. BIS WP1087: carry >10%/yr avg but high carry predicts crashes; BitMEX Q3-25: mean 8h funding ~6–9% ann., 92–96% intervals positive; 6-yr open backtest BTC 9%/yr, maxDD −0.34%. 2026 regime compressed (CME basis ≈ T-bill; Ethena sUSDe ~3.7%). Honest: 3–8% gross, 0–4% over T-bills; spikes add upside. Risks: negative funding stretches, hedge-leg liquidation, API churn (Coinbase INTX perps via Advanced Trade API ended 2026-10-01).
2. **Long-only vol-targeted time-series momentum on BTC/ETH spot** (daily signal, weekly/monthly rebalance). AUT 471-coin study: TSMOM Sharpe 1.51 vs 0.85 post 15bp cost (params ex post); Zenodo 2018–2026 Sharpe 0.8–1.2. Better-shaped beta, DD 30–60%, not market-neutral.
3. **Alt-coin funding-spike harvester** — episodic 20–100% ann. bursts; MDPI 2026 (26 exchanges, 749 symbols): only 8/20 portfolios profitable, reversals in 19/20; needs strict size/exit rules; US limited to 9 Kraken US perps.
4. **Fee-positive concentrated LP on volatile mid-cap pairs** (Fritsch 2024: LDO/LINK/UNI-ETH fees ≈1.5× LVR; majors do not cover LVR). Yield on coins you'd hold anyway; token beta.
5. **Hour-of-day seasonality (long 21–23 UTC)** — research candidate only; Quantpedia 33%/yr gross through 2021, no cost/post-2022 evidence; test on Kraken 1-min with maker fills.

## Rejected (with evidence)
- Cross-exchange / triangular arb: Bamberg FRL 2024 — 97% unprofitable even at VIP fees, $12–18/week net at 4 ms latency.
- MEV / liquidation bots: pro-dominated (top-3 Solana bots ~60%); infra ≥$1.8k/mo; Jito tips −50% QoQ.
- Copy-trading: CHI 2024 — popularity *negatively* correlated with ROI, median leader life 2.9 days.
- Pump-and-dump following: Xu & Livshits 2019, Gandal 2018 — followers are exit liquidity; participation is manipulation. Not buildable.
- Grid/martingale bots (passivbot etc.): no verified results, tail blow-ups.
- Curated stablecoin vaults: Stream xUSD −$93M, Resolv, KelpDAO bad debt 2026.
- Airdrop farming: sybil filters remove 59–60%; −88% 3-month drift.
- Open-source bots (Freqtrade, Hummingbot, Jesse, Nautilus): good plumbing, zero auditable live alpha.

## Data
Binance Vision zips (free; futures funding/bookDepth dirs), Kraken OHLCVT CSVs (free, survivorship-biased), CryptoDataDownload (free 1m/1h), Coinbase Advanced Trade candles + funding endpoints (free), Tardis (paid), DefiLlama yields API.

Sources: BIS https://www.bis.org/publ/work1087.pdf · BitMEX https://blog.bitmex.com/2025q3-derivatives-report · https://github.com/zwmjj/funding-rate-arb · https://www.mdpi.com/2227-7390/14/2/346 · AUT TSMOM https://acfr.aut.ac.nz/__data/assets/pdf_file/0009/918729/Time_Series_and_Cross_Sectional_Momentum_in_the_Cryptocurrency_Market_with_IA.pdf · https://zenodo.org/records/19671502 · Fritsch LVR https://arxiv.org/html/2404.05803v2 · HLP https://www.coingecko.com/learn/hyperliquid-hlp-vault-analysis · Bamberg arb https://fis.uni-bamberg.de/bitstreams/8b9ae900-017a-4bed-94b9-609c16e89945/download · Xu & Livshits https://www.doc.ic.ac.uk/~livshits/papers/tr/pump_and_dump_tr.pdf · Kawai CHI24 https://www.andrew.cmu.edu/user/nicolasc/publications/Kawai-CHI24.pdf · Coinbase US perps https://cryptobriefing.com/us-perpetual-futures-cftc-launch/ · Kraken US perps https://www.coindesk.com/markets/2026/06/15/kraken-debuts-u-s-perpetual-futures-as-crypto-derivatives-move-onshore
