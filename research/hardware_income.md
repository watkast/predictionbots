# Idle hardware → income: Mac mini M4 Pro 48 GB, Dell T3600 + RTX 3070, two iPhones (2026-10-17)

Owner: solo US operator, Colorado, already runs the bots on GitHub Actions (public repo → Actions minutes are free; `paper.yml` runs 11 matrix entries for 20,000 s every 6 h, i.e. ~93 % wall-clock coverage with a ~25-min gap per cycle). Question: what does each idle device add, automated first, manual second, net of power, depreciation and ban risk.

Grades: [A] official / large-sample, [B] credible practitioner data, [C] vendor blog / calculator, [D] anecdote. Every number has a URL. Electricity: **Colorado residential ≈ 16 c/kWh** (EnergySage, bills through Oct-2026, Xcel residential general service 15–17 c) [B] https://www.energysage.com/local-data/electricity-cost/co/ — the tables below use **15 c/kWh**; at 16 c add ~7 %.

## 0. Verdict (one line per device)

| Device | Recommendation | Why |
|---|---|---|
| **Mac mini M4 Pro 48 GB** | **Use** — always-on home node: 24/7 paper/live bot host on a residential Colorado IP, local-LLM worker for cheap agent sub-tasks (triage, classification, embeddings, scraping), Xcode build box for an iOS lane. ~$1–7/mo in power. | Renting it out is not possible (no marketplace takes a home Mac), DePIN on Apple silicon pays ~$0, but as *cost-avoidance* it is worth $20–200/mo and it unlocks live-venue requirements (residential IP, Novig/Kalshi apps need a phone, not the Mac). |
| **Dell T3600 + RTX 3070 8 GB** | **Sell** (both, now): ~$240–285 for the 3070 (eBay asks), ~$150–300 for the T3600 shell. | Every automated use nets **$0–40/mo** before token-liquidity and ban risk, while the box burns ~$10/mo at idle (97 W). Best case pays back the resale value in 1–2 years; the GPU loses value faster than that. The Mac mini already covers Whisper/SD/embeddings. |
| **iPhone 17 Pro 512 GB** | **Keep** as daily driver + Kalshi app + Novig app (device geolocation for production keys). | $1,036 avg Swappa sale; nothing earns more than its depreciation. |
| **iPhone 16 512 GB** | **Sell** (~$699 Swappa avg sale, $756 avg ask) **unless** you travel out of state: then keep it plugged in at home as the stationary Novig geolocation / 2FA device (worth more than any earn-app). | Every iPhone "earn" app we could verify pays $0–15/mo [C/D]; the phone depreciates ~$15–20/mo. |

**Automated income from this hardware is ≈ $0–50/mo total.** The real value is (a) avoided cloud spend and (b) removing the two blockers that keep the sports/prediction ventures in paper mode (residential IP, phone-app geolocation). Nothing here beats the T-bill hurdle in `yield_vehicles.md` on the hardware's resale value ($2.5–3k in phones + PC ≈ $110/yr at 4.3 %).

## 1. Energy math (15 c/kWh; 730 h/mo)

| Device | State | Watts | kWh/mo | $/mo | Source |
|---|---|---|---|---|---|
| Mac mini M4 Pro | idle | 5 | 3.7 | $0.55 | Apple spec (64 GB/8 TB config) [A] https://support.apple.com/103253 |
| Mac mini M4 Pro | sustained LLM inference | ~65 | 47 | $7.1 | owner measurement [D] https://www.heyuan110.com/posts/ai/2026-04-14-mac-apple-silicon-ai-workstation/ |
| Mac mini M4 Pro | max | 140 | 102 | $15.3 | Apple spec [A] |
| T3600 (Xeon E5, 64 GB) | idle, no GPU load | 97 | 71 | **$10.6** | AnandTech review config [B] https://at-web1.www.anandtech.com/show/5769/dell-precision-t3600-review-dells-new-enterprise/5 |
| T3600 + 3070 | GPU mining/Salad (GPU 115–170 W + base) | ~220–270 | 160–197 | $24–30 | GPU W from hashrate.no / miningboard [C]; owner's 220 W system figure |
| T3600 + 3070 | full load | ~350 | 256 | $38 | AnandTech load 262 W with a 142 W Quadro; 3070 TGP 220 W |
| iPhone (plugged, screen off, mapping app) | | 2–5 | 1.5–3.7 | $0.2–0.6 | — |

The T3600's **idle draw alone ($10.6/mo, $127/yr) exceeds every DePIN/rental net figure below.** Its 2012 Sandy Bridge-E CPU (no AVX2) is also rejected or deprioritised by most modern compute marketplaces and cannot run current Windows 11 officially.

## 2. Compute rental / DePIN / mining — RTX 3070 8 GB (in the T3600) and M4 Pro

### 2a. GPU marketplaces

| Platform | 3070 8 GB accepted? | Gross (listed) | Realistic utilisation | Net/mo after power* | Payout evidence | Grade |
|---|---|---|---|---|---|---|
| **Salad** (Windows only, no macOS) | yes (RTX 3060+ "best"; 8 GB limits job eligibility) | Salad's own July-2025 post: 20/30-series jobs "up to $2.14/day"; measured Sept-2026 **4090** mean $0.17/chop-hour ($4.2/day); a 4090 owner nets $2.87/day over 9,058 h; GTX 1060 ≈ $0.005/h | job-fill is the binding constraint; 8 GB cards get the leftovers | **−$10 to +$15** (3070 ≈ $0.5–1.5/day gross vs $0.85–1.0/day power at 240–270 W system) | PayPal/gift cards, 5-day redemption; real 4090 numbers only | B (4090) / C (3070) https://x.com/Salad_Chefs/status/1940872611409330612 · https://www.bestcloudmining.net/providers/salad/ · https://salad.com/download/ |
| **Vast.ai** (Ubuntu host) | yes, 8 offers listed | $0.109/h list; host keeps ~85 % → $0.093/h; **3090 hosts keep $0.10–0.17/h** | 20–50 % for hobby hosts (4090 steady-state 65–85 %) | **$0–10** (at 30 %: $0.67/day gross − $0.35/day idle power) | USD payout via Stripe/PayPal; 3090 "≈ $0–25/mo after amortisation, marginal at best" | B https://ownyourmind.ai/use/gpu-provider-income/ · C https://miningboard.com/rigs/nvidia-rtx-3070/ai-rental · https://vast.ai/article/how-much-money-can-you-earn-renting-out-your-gpu-on-vast-ai |
| **Clore.ai** | yes, 12 offers | $0.167/h list, 23 % rented now, 15 % fee | 23 % | **$0–12** ($0.78/day gross at 23 %) | paid in CLORE token (thin) | C https://miningboard.com/rigs/nvidia-rtx-3070/ai-rental |
| **Nosana** (NVIDIA only, Solana) | 2 offers at $0.064/h | $1.53/day at 100 % | low; 8 GB too small for most LLM jobs | **≤ $5** | NOS token | C same |
| **RunPod Community Cloud** | effectively **no** for a single home card: Secure Cloud is T3/T4 DCs with SOC2 partners; community hosting is multi-GPU, vetted, reliability-scored | — | — | — | — | A https://docs.runpod.io/hosting/partner-requirements |
| **io.net** | NVIDIA + Apple M-series workers accepted; earnings are "block rewards" paid on uptime (≥ 5 h/day) and need an IO stake per device; job payments go to high-end cards | no $ figure published for consumer cards or Macs | idle rewards only | **≈ $0–5, paid in IO, minus stake lock-up** | token | C https://io.net/docs/guides/block-rewards/block-rewards · https://ownyourmind.ai/use/gpu-provider-income/ |
| **Akash** | GPU providers are datacenter operators (Kubernetes, public IP); 33.7 % network GPU utilisation (84 of 334 GPUs, Q1-26); no consumer-card income data | — | — | not viable solo | — | B same |
| **Render** | OctaneBench nodes; "$300–800/mo per high-end GPU" is for 4090/pro-class render nodes, 7–10-day release; macOS Octane X exists but no Mac-node earnings data | — | — | 3070 8 GB: tiny OctaneBench score → tens of $ at best | RENDER token | C same |
| **Apple silicon (M4 Pro) on any of the above** | Vast/Salad/Clore/Nosana/RunPod: **no**. io.net: yes (idle rewards). Morpheus has a Mac consumer-node guide (network-wide ~255 MOR/day ≈ $510/day split across *all* providers) | — | — | **≈ $0** | — | C https://ownyourmind.ai/use/gpu-provider-income/ |

\*Net uses 15 c/kWh and the T3600's ~97 W base + GPU draw; a modern low-idle host would change the picture by ~$8/mo but you do not own one.

**Conclusion:** the 3070 is the wrong card (8 GB VRAM is below the 12–24 GB floor most paid jobs want), in the wrong chassis (97 W idle, no AVX2). Expected net across all platforms: **$0–15/mo**, with downside of negative months and token-denominated payouts.

### 2b. Mining (today's calculators, GPU-only power, $0.10/kWh in the source)

| Source | Best coin | GPU W | Rev/day | Profit/day @10 c | **Profit/day @15 c incl. 97 W base** | Grade |
|---|---|---|---|---|---|---|
| WhatToMine | Pearl (PRL) 68 TH/s | 150 | $2.15 | $1.79 | $2.15 − 0.89 = **$1.26** | C https://whattomine.com/gpus/48-nvidia-geforce-rtx-3070 |
| hashrate.no | Pearl 72 TH/s | 116 | $2.39 | $2.11 | **$1.62** | C https://hashrate.no/gpus/3070 |
| miningboard | PearlHash 51 TH/s | 170 | $1.61 | $1.20 | **$0.65** | C https://miningboard.com/rigs/nvidia-rtx-3070/mining |
| Kryptex (365-day avg, BTC-paid) | — | 125 | ~$1.00 | $216/yr | **≈ $0.20** | C https://www.kryptex.com/hardware/nvidia-rtx-3070 |

So $6–50/mo *if* you can sell PRL/Quantus/Keryx — all launched-this-year coins with thin order books; the 365-day BTC-equivalent average is ~$1/day gross. NiceHash pays BTC but routes to the same algos at a 2–5 % cut. Monero (RandomX) is CPU-only and a 2012 Xeon makes cents/day. **Mining: $5–30/mo expected, high variance, not worth the fan noise.**

### 2c. Bandwidth sharing (any device; one residential IP)

| App | $/mo single US IP | Payout min | Risks | Grade |
|---|---|---|---|---|
| Honeygain | $5–15 | $20 PayPal | resells your IP to scrapers; ISP ToS (Xcel-area ISPs: Xfinity/CenturyLink AUPs prohibit reselling bandwidth, rarely enforced) | C https://1dollaperday.com/blog/honeygain-vs-pawns-vs-earnapp-vs-packetstream |
| Pawns.app | $1–3 | $5 | same | C same |
| EarnApp (Bright Data) | $0.5–3 | $2.50 | same + Bright Data is the proxy vendor whose traffic others block | C same |
| PacketStream | $1–3 | $5 | same | C same |
| Grass | Season-2 pool ≈ $3M USDC for Oct-2024→Jun-2026 across "thousands" of nodes; network revenue ~$33M/yr with **zero** currently flowing to node tokens | points/airdrop only | token-price risk; 20 months for one claim | B/C https://www.hokanews.com/2026/07/grass-airdrop-season-2-3m-usdc-claims.html · https://www.kucoin.com/news/flash/grass-generates-33m-annually-from-ai-customers-governance-vote-on-revenue-capture-set-for-july-7 |
| Mysterium | lifetime $568k paid to 31,547 IPs ≈ **$18 per IP ever** | MYST | you are an exit node for strangers' scraping/VPN traffic | C https://paylinedata.com/blog/mystnodes-review/ |
| Tor exit | $0 and abuse complaints | — | no | — |

Stacking the four paid apps ≈ **$8–25/mo**, each one a scraper-proxy on the same IP the trading bots would use. **Do not run these on the IP that trades on Kalshi/Novig** (datacenter/proxy IP reputation is exactly what geofenced venues score).

### 2d. Storage / radio / phone DePIN

| Network | Device | Economics | Verdict | Grade |
|---|---|---|---|---|
| Chia / Filecoin | 1 TB SSD | 1 TB ≈ 0.00005 % of a ~20+ EiB netspace; Filecoin needs sealed sectors + FIL collateral | **no** ($0.0x/mo) | — |
| Helium Mobile Discovery Mapping | iPhone + Helium plan ($15/mo Air) | 30 points/day for 40 hexes/day, pool split equally among all qualifiers; 2023 farmers got 2,000 MOBILE/day → reward rules tightened; MOBILE merged into HNT Jan-2025; one reward per account | **no** unless you'd buy the plan anyway; then low single-digit $/mo | B/C https://support.hellohelium.com/en/articles/7174144-discovery-mapping-faq · https://www.coindesk.com/business/2023/12/18/helium-mobile-cracks-down-on-mobile-token-farmers · https://support.hellohelium.com/en/articles/13370206-changes-to-the-5-beta-and-20-unlimited-plans |
| Hivemapper | Bee dashcam now **$19/mo subscription**; HONEY $0.003–0.008 (ATH $0.376) | 1,800 km/mo driver: $6–14 gross → **negative** after sub; 4,500 km strategic: +$13–41 | **no** | B https://oneshekel.com/how-much-does-a-hivemapper-dashcam-actually-make-per-month-real-data-2026/ |
| NATIX Drive& (iPhone dashcam) | App Store listing now titled **"(discontinued)"** | — | **dead** | A https://apps.apple.com/app/id6446762335 |
| Silencio (noise) | iPhone | in-app coins + raffle tickets; "very little, unpredictably" | **no** ($0–2/mo) | C https://www.aitrainingjobsfinder.com/blog/silencio-review-2026 |
| DIMO Mobile | iPhone + car | weekly DIMO for driving ≥ 1×/week; adapter earns most; no $ figures published | $1–5/mo in token | D https://docs.dimo.org/overview/frequently-asked-questions |
| Geodnet | needs a $several-hundred triple-band RTK base station, not a phone; ~12 GEOD/day ≈ $50/mo gross at $0.14 (Dec-2025) | 6-mo+ payback, only outdoor-roof installs | not a phone play; the one DePIN with real revenue | B https://medium.com/@done_71651/geodnet-geod-in-depth-research-report-the-real-yield-king-of-the-depin-sector-35d3e4a6733f |
| Sweatcoin / StepN | — | step-token economies collapsed 2022–24; no verified cash payouts of note | **dead** | — |

**No iPhone background-earning app with verified payouts above ~$5/mo exists in 2026.**

## 3. Run our own workloads on the Mac mini instead of the cloud

### 3a. What fits in 48 GB and how fast (M4 Pro, 273 GB/s)

| Model (4-bit unless noted) | PP tok/s @16K/64K | TG tok/s @16K/64K | Fits 48 GB? | Source |
|---|---|---|---|---|
| Qwen3.6 35B-A3B (MoE) | 831 / 513 | **71 / 47** | yes (~20 GB) | B https://www.hardware-corner.net/is-mac-mini-m4-pro-good-for-llms/ |
| GPT-OSS 20B | 713 / 463 | 54 / 33 | yes | B same |
| Gemma 4 26B-A4B | 674 / 423 | 48 / 36 | yes | B same |
| Qwen3 Coder Next | 612 / 417 | 51 / 33 | yes | B same |
| Qwen3.6 27B dense, 8-bit | 113 / 71 | 8 / 7 | yes (~29 GB) | B same |
| Qwen3 Coder 30B-A3B | — | 75–80 empty ctx, ~40 real chat | yes | C https://www.popularai.org/p/mac-mini-llm-performance-in-2026 |
| Llama 3.1 8B Q4 (Ollama) | — | 42 | yes | D https://www.heyuan110.com/posts/ai/2026-04-14-mac-apple-silicon-ai-workstation/ |
| Qwen 2.5 14B Q4 | — | 24 | yes | D same |
| 34B dense Q4 | — | 11 | yes | D same |
| Llama 3.3 70B Q4 (~40–44 GB) | — | OOM on 48 GB (3–5 tok/s on 64 GB) | **no** in practice | D same + https://llmcheck.net/models/qwen-3-30b-a3b-on-m4-pro/ |

Rule: MoE models (3–4B active) are the sweet spot — 50–70 tok/s generation and 500–800 tok/s prompt ingestion at ~65 W. Dense ≥ 27B is 7–11 tok/s and only for batch jobs.

### 3b. Local agents vs paid tokens — honest quantification

* Quality: a 50-task benchmark (RTX 4070 Ti S, Q4) scored Qwen3-Coder 12.4/15 vs Claude Sonnet 13.2/15; parity on single-file code and unit tests, **−16 % on multi-file refactoring and −9 % on bug diagnosis** [B] https://www.kunalganglani.com/blog/local-llm-vs-claude-coding-benchmark . Claude Code can point at a local Ollama/OpenAI-compatible endpoint [C] https://www.morphllm.com/ollama-claude-code .
* Throughput: at 50 tok/s sustained the Mac emits ~4.3M output tokens/day for **$0.23 of electricity**. The same volume from a frontier API at the $10–15/M-output pricing the benchmark cites would be $43–65/day — but you would not buy 4M frontier tokens/day of *routine* work, so the real saving is bounded by current spend.
* What we would actually move local (all already in the repo's plans): Semgrep/CodeQL finding triage for `ventures/bounty`, odds↔market entity linking (`pb/data/odds_link.py` aliases), news/market-description classification for `mm_inventory` gating, SaaS support/FAQ drafts, embeddings for an `oddsmath` docs search (nomic/bge on MLX = free), Whisper transcription of earnings calls/pressers for sports/macro signals (whisper-large-v3 on MLX runs faster than real time). Frontier models stay for multi-file code and anything that ships.
* **Saving: 50–70 % of routine-task token spend** (the benchmark's hybrid estimate) → if agent API spend is $100–300/mo, **$50–200/mo**; if the agents run on a flat subscription the saving is ~$0 and the value is only privacy and unlimited batch volume.

### 3c. Hosting the bots on the Mac mini instead of GitHub Actions

| Factor | GitHub Actions (now) | Mac mini at home | Evidence |
|---|---|---|---|
| Cost | $0 (public repo) | $0.5–7/mo power | this memo §1 |
| Continuity | 11 parallel 5.5-h jobs every 6 h → ~25-min gaps, no in-process state across cycles, 6-h job cap | true 24/7, state in RAM, no re-warm; launchd restarts; local parquet recorder | `.github/workflows/paper.yml` |
| Latency to Kalshi (AWS us-east-2 Ohio, CloudFront) | Azure East-US runner ≈ 10–25 ms | Colorado residential ≈ 40–60 ms (vendor claims "home 50–200 ms") | A https://latency.glassnode.com/prediction-markets/about · C https://www.quantvps.com/blog/running-kalshi-bots-on-a-vps |
| Latency to Coinbase/Kraken signal feeds | similar | similar | — |
| Polymarket | US is close-only on both frontend *and API*, IP-based geoblock; a home IP changes nothing | same | A https://docs.polymarket.com/developers/CLOB/geoblock |
| IP reputation for *live* trading | datacenter IP (fine for paper; untested for live order flow on geofenced venues) | residential Colorado IP = what the venues expect; Novig AZ/MI/NV exclusions and Kalshi state rules are IP + device based | README Novig section; Kalshi WA-state block is IP-geofenced https://cybernews.com/geo-restrictions/kalshi-blocks-washington-sports-election-bets-2026/ |
| Ops risk | GitHub outages, 6-h cap | home power/ISP outages (no UPS = ~1–3 unplanned restarts/mo); kill-file + RiskManager already cancel on stale data | `pb/live/risk.py` |

**Verdict:** keep paper on Actions (free, slightly *lower* latency), and make the Mac mini the **live-venue host** when any strategy earns a live allocation — residential IP, 24/7 state, local recorder. A $5–30/mo Ohio/Chicago VPS would beat both on latency if a strategy ever becomes latency-sensitive (our maker strategies are not; `order_latency` in the sim already assumes hundreds of ms).

### 3d. Image generation, stock images, POD (RTX 3070 8 GB)

* Capability: SD 1.5/SDXL run on 8 GB; FLUX.1-dev needs ≥ 12–16 GB (fp8/GGUF squeezes onto 8 GB at minutes per image). The M4 Pro runs SDXL/FLUX-schnell via MLX/Draw Things at comparable speed with 48 GB headroom — the 3070 adds nothing you lack.
* Market: Adobe Stock accepts labelled AI images; Shutterstock routes "fully AI" into a lower-payout collection and bans after 3 undisclosed-AI strikes in 12 months; iStock/Getty refuse AI [A/B] https://pixelkeyai.com/blog/ai-generated-stock-submission-rules-2026 . A 45,000-image professional portfolio shows **sales −48 % and real per-image returns −29 % since 2019**, needing +9,600 images/yr just to stay flat; AI-dataset licensing paid him $933 in 2025 [B] https://brutallyhonestmicrostock.com/2026/06/15/microstock-hamster-wheel-more-files-fewer-sales-lower-real-returns-data-analysis-from-2019-2026/ ; Adobe contributors report "drastic decrease in monthly earnings" threads through 2026 [D] https://community.adobe.com/t5/stock-contributors-discussions/drastic-decrease-in-monthly-earnings/m-p/15572728 . **Expected: $0–30/mo after months of uploading. No.**

### 3e. Transcription service, fine-tuning, embeddings

* Whisper API is **$0.006/audio-min** ($0.36/h); gpt-4o-mini-transcribe $0.003/min [B] https://diyai.io/ai-tools/speech-to-text/openai-whisper-api-pricing-2026/ — a home GPU cannot undercut that and no buyer pays for raw ASR. Human-verified niche work still bills $0.20–1.50/min, direct clients $40–120/audio-hour, but it is manual labour [C] https://www.earnifyhub.com/freelancing-gig-work/transcription-income-2026 .
* Fine-tuning small models for the SaaS products: LoRA on ≤ 8B fits the Mac (MLX) or the 3070 (QLoRA 7B barely); worth doing only once a product has paying users. Embeddings for an `oddsmath`/docs search: free on the Mac, and Cloudflare Workers AI/Vectorize free tiers cover the serving side.

## 4. Residential IP / home hosting

* **Own scraping proxy**: legitimate for our own data collection (The Odds API, ESPN, NWS, Open-Meteo, Kalshi/Polymarket public endpoints are all API-ToS-bound, not scrape-blocked); a home IP mostly avoids datacenter-IP blocks on sites like sportsbook odds pages. Value: enables data products in `ventures/saas` that need non-DC egress. Do **not** sell the IP (that is §2c).
* **Home SaaS hosting via Cloudflare Tunnel** (free) vs Workers Free (100k req/day) [B] https://costbench.com/software/cdn-edge/cloudflare/free-plan/ : Workers wins for anything stateless; the Mac mini behind a Tunnel is the right place for stateful/long-running services (recorders, LLM endpoints, batch jobs) that would otherwise need a $5–20/mo VPS. Uptime = home power/ISP; put it behind a UPS.
* **Game servers for money**: a Minecraft server with real revenue is a community business ($600–1,000/mo listings are for established player bases with ranks/cosmetics; Mojang EULA bars pay-to-win) [D] https://builtbybit.com/threads/selling-server-with-10-000-revenue-stable-600-1000-per-month.719622/ ; reselling hosting from home competes with $1–3/GB-month hosts. **No.** Plex/Jellyfin, seedboxes: no (licensing/legal).

## 5. Apple-specific

| Option | Numbers | Verdict | Grade |
|---|---|---|---|
| Apple Developer Program → agent-built iOS apps | $99/yr. RevenueCat SoSA-2026 (115k apps): **17 % reach $1k MRR within 2 yrs** (down from 19 %), 4.6 % reach $10k; avg revenue 1 yr after launch ≈ **$72/mo**; middle 50 % earn $16–429/mo; top-quartile threshold $429/mo; hard paywalls convert 11 % vs 2 % freemium; RLTV/payer $23 median | same base rate as the SaaS lane but with 15–30 % Apple cut; the Mac mini is the only way to build/sign iOS apps, so this is a **new distribution channel for `saas_portfolio`**, not a new venture. Expected $0–100/mo per app, uncapped tail | A https://ppc.land/the-app-middle-class-is-dying-and-revenuecats-data-shows-exactly-how-fast/ |
| Rent out your own Mac (MacStadium/Scaleway/Cirrus style) | providers rent M4 minis at $85–149/mo, Scaleway M4 Pro 64 GB €335/mo; **no marketplace lets an individual list a home Mac** (all are DC-owned fleets; Apple's SLA requires 24-h minimum lease) | **not possible**; the comparison only shows what you *avoid* paying: a hosted M4 Pro is ~$300/mo | A https://scaleway.com/en/pricing/apple-silicon · B https://myremotemac.com/best-mac-cloud-hosting |
| Mac mini as CI runner for others | same — no individual marketplace; GitHub-hosted macOS runners exist | no | — |
| iOS test-device rental | no | no | — |
| Second iPhone as dedicated trading/2FA/geolocation device | Novig production keys require **device geolocation from the Novig app within 3 days** (AZ/MI/NV excluded); Kalshi trading needs the account's KYC + state geofence but the **API does not need the app**. A phone that physically stays in Colorado satisfies Novig's 3-day ping even while you travel, and isolates 2FA/trading apps from the daily phone | the only iPhone use with real option value — but it only matters if (a) you travel out of state often or (b) you want app/2FA isolation. Otherwise the daily 17 Pro does the job and the 16 is $650–700 of idle depreciating glass | A (repo README, Novig docs 2026-10-17) |
| Crowd-testing on iPhone (uTest/Testbirds/UserTesting) | uTest $3–100 per approved bug, $10–50 per UX cycle; Testbirds €1–50/bug; UserTesting $10/20-min test, $30–120 live; realistic $200–800/mo across 3–4 platforms at 10–15 h/wk | manual; ~$15–25/h effective | C https://www.testfi.app/blog/get-paid-to-test-apps-2026 · https://earnifyhub.com/learning-guides/prolific-vs-usertesting-vs-respondent-review-2026 |
| Sell | iPhone 17 Pro 512 GB avg sale **$1,036** (ask $1,157 unlocked, trade-in $676); iPhone 16 512 GB avg sale **$699** (ask $756, trade-in $390); Mac mini M4 Pro 48 GB/512 GB refurb retail $1,618 (used private ≈ $1,200–1,400) | — | A https://swappa.com/prices/apple-iphone-17-pro · https://swappa.com/prices/apple-iphone-16 · https://www.refurb.me/stats/mac-mini/mac-mini-m4-pro-late-2024 |

## 6. Manual options (ranked by $/h, iPhone or Mac in hand)

| Option | Pay evidence | $/h effective | Notes | Grade |
|---|---|---|---|---|
| Respondent / dscout-style research interviews | $75–200/session (30–90 min), 10–25 % qualification | $50–150 while in session; $100–300/mo realistic | lumpy | C https://earnifyhub.com/learning-guides/prolific-vs-usertesting-vs-respondent-review-2026 |
| UserTesting | $10/20-min test, $30–120 live | ~$30 | $100–200/mo | C same |
| uTest / Testbirds | per-bug $3–100 | $10–25 | $200–800/mo across platforms, top testers claim $1k+ | C https://www.testfi.app/blog/get-paid-to-test-apps-2026 |
| Prolific | floor £6/$8 per h, recommended $12/h; $200–350/mo at 60–80 studies | $8–12 | automatable? **no** — bots are banned and the studies are the product | A https://participant-help.prolific.com/en/article/f66985 · C earnifyhub |
| Field Agent / Gigwalk / Observa | $3–15/task, 5–10 tasks/wk in metro; $50–200/mo; worked example $120–160/mo | $10–20 incl. driving | Denver/Boulder suburbs fine | C https://earnifyhub.com/surveys-tasks/field-agent-vs-gigwalk-vs-observa |
| Matterport/Polycam LiDAR tours with iPhone 17 Pro | operators charge $350–500 (<1,000 sq ft), $450–750 (1–2.5k), $750–1,000 (2.5–5k); Matterport Starter $9.99/mo; phone capture is "adequate for basic real estate, not commercial" | $100–300/job after travel/editing, if you can sell it | a local-sales business, not a gig; agents are price-sensitive and Pro cameras win listings | C https://thefuture3d.com/blog/matterport-pricing-guide-2026/ |
| Google Street View "trusted pro" | Google pays nothing; you sell 360 tours to businesses from leads; program pages still live but no 2026 earnings data | unknown | skip | D https://www.adorama.com/alc/?p=38381 |
| Local "AI consulting" with the Mac as demo | no base-rate data; your edge is the bots/SaaS work, not the box | $50–150/h if you land it | manual sales | D |
| Flip the T3600 | refurb dealers list E5-1620/16 GB/512 GB at $334 (out of stock), i.e. a used 64 GB box nets ~$150–300 private; 3070 asks $240–285 (eBay, Oct-2026) | one-off ~$400–550 | **do it** | B https://pcserverandparts.com/dell-precision-t3600-tower-intel-xeon-e5-1620-3-60-ghz-4c-16gb-ddr3-1x-512gb-ssd-generic-gpu-128mb-or-higher-windows-10-professional-refurbished-web/ · https://gpupoet.com/gpu/learn/price/october-2026/nvidia-geforce-rtx-3070 |

## 7. Ranking — expected monthly net × automatability ÷ risk

### Automated
| # | Use | Device | Expected net/mo | Auto | Risk | Score |
|---|---|---|---|---|---|---|
| 1 | Always-on live-venue bot host + recorder on residential IP (replaces a $5–30 VPS; unblocks live Kalshi/Novig) | Mac mini | $5–30 avoided + option value | 95 % | low | **high** |
| 2 | Local LLM worker for routine agent tasks (triage, linking, embeddings, Whisper on filings/pressers) | Mac mini | $0–200 avoided (bounded by current token spend) | 90 % | low | **high** |
| 3 | iOS distribution channel for `saas_portfolio` (Xcode on the Mac + $99 ADP) | Mac mini | $0–100 per app, fat tail | 80 % | low-med (review rejections) | medium |
| 4 | Bandwidth sharing stack (Honeygain/Pawns/EarnApp/PacketStream) | any, **not the trading IP** | $8–25 | 100 % | med (ISP AUP, IP reputation) | low |
| 5 | Salad / Vast / Clore on the 3070 | T3600 | **−10 to +15** | 90 % | med (token payouts, Windows-only Salad) | ~0 |
| 6 | Mining (PRL/Quantus) | T3600 | $5–30 gross of illiquid coins | 100 % | high | ~0 |
| 7 | iPhone DePIN (Helium mapping, Silencio, DIMO) | iPhone 16 | $0–5 | 100 % | low | ~0 |
| — | NATIX Drive&, Hivemapper, Chia/Filecoin, Mysterium/Tor, Render-on-Mac, RunPod, Akash, stock images | — | ≤ $0 | — | — | excluded |

### Manual
| # | Use | $/h | $/mo at 10 h/wk | Note |
|---|---|---|---|---|
| 1 | Research interviews (Respondent/dscout) + UserTesting | 30–150 | $200–500 | qualification-gated |
| 2 | Crowd QA (uTest/Testbirds) | 10–25 | $200–800 | ratings compound |
| 3 | Sell T3600 + 3070 (one-off) | — | ~$400–550 once | also saves $127/yr idle power |
| 4 | Sell iPhone 16 (one-off) | — | ~$650–700 once | unless kept as stationary Novig/2FA device |
| 5 | Field Agent / Gigwalk | 10–20 | $50–200 | metro-only |
| 6 | Prolific | 8–12 | $200–350 | floor pay |
| 7 | LiDAR/Matterport tours | 100–300/job | $0–1,000 | needs local sales effort |

## 8. What goes into the venture registry

* `mac_mini_home_node` (status research): always-on host for live-venue runs + local-LLM worker + iOS build box. Bar check: $0 direct income, but it removes two blockers (residential IP, continuous state) and saves $5–200/mo; cost $1–7/mo. **Clears the bar as infrastructure.**
* Nothing else clears it: every DePIN/rental/mining/phone-earn line is ≤ $25/mo with ban/ISP/token risk and a $10/mo idle-power tax on the T3600; stock images, transcription and game hosting are negative-expectancy or manual.

Sources not already inline: Salad payout/requirements https://www.bestcloudmining.net/providers/salad/ · Vast host economics https://ownyourmind.ai/use/gpu-provider-income/ · GPU-rental fee table https://miningboard.com/guides/rent-gpu-for-ai-earnings · Helium HIP-79 mapper rules https://github.com/helium/HIP/blob/main/0079-mobile-poc-mappers-rewards.md · Kalshi origin region https://latency.glassnode.com/prediction-markets/about · Claude Code + Ollama setup https://www.morphllm.com/ollama-claude-code · Mac hosting price comparison https://myremotemac.com/best-mac-cloud-hosting · Xcel rate bands https://www.energysage.com/local-data/electricity-cost/co/
