# PredictionBots — the business (living document)

Started 7 Nov 2026. Owner: Noah Watson. PM: Claude. This file is the plan of record; it changes as we learn. Decisions
are appended at the bottom with the date and the reason, so the reasoning survives.

## What we sell

Research and execution tooling for prediction-market traders and bot builders (Polymarket US, Kalshi), from a team that
publishes every one of its own trades. The thesis: the only edges that survive small capital are **mechanical** — moments
where the rules have already decided the outcome and the order book has not caught up. Those moments are small (tens to
hundreds of contracts), which is why big money ignores them and why they persist. We find them, publish the record, and
sell the finding tools.

1. **The terminal** — $49/month (first fifty: $29 for life). Live scanners (decided games, final-second candidates,
   cross-venue locks), alerts (Telegram/email), the cockpit for working a market by hand, the research archive.
2. **The data API** — per call over x402 (USDC on Base, no account): final-second candidates, decided markets, lock
   history. $0.002–$0.01 a call. Agents pay programmatically; zero marginal cost.
3. Later: managed bot hosting; market making as a capital business once 1 and 2 fund it.

## Why this and not trading

Our own 30-day replay killed the retail-momentum idea (1,172 signals, −1.86%/trade, no edge). Mechanical edges exist but
their capacity is tiny; software sold into a boom is the only shape with a fat right tail. The prediction-market tooling
niche is 6–12 months old, full of thin vendors and hype content, and our research is the differentiator: we publish
losses, code and data. Organizers of pumps own distribution and manufacture events; we own distribution by being the
honest source, and the "event" we manufacture is the research itself.

## Numbers that matter

- Overhead: ~$100/month (AI subscription) + domain. Break-even: 2–4 terminal subscribers or ~50k API calls/month.
- First dollar target: within 14 days of 7 Nov. First 10 paying subscribers: 45 days.
- Base rates we respect: most indie products make $0–2k/month; most x402 endpoints have ≤2 payers; the tail belongs to
  whoever becomes the standard tool in a hot niche during its immature window.

## Stack

GitHub (code, bots as Actions, data branches as the public ledger) · Cloudflare Pages (site, waitlist function + KV) ·
Cloudflare Workers (x402 API) · the Dell T3600 at home (always-on recorder + sniper, deploys; behind T-Mobile CGNAT, so
outbound only) · Stripe (subscriptions, when there is something to charge for) · X + Substack (distribution).

## Launch sequence

1. Post #1 "We bought the pump candle 1,172 times" → site live → waitlist open. (built 7 Nov; publish when the domain is up)
2. Post #2 "The last three seconds" with the live Mr T record (fills or not — either is a post) → early-bird terminal.
3. Weekly build-in-public: every bot's ledger, what changed, what we killed.
4. Channels: X (prediction-market trader community), Polymarket + Kalshi Discords, r/Polymarket, r/Kalshi, Substack,
   dev.to for the x402 angle. Noah owns the accounts and posts; Claude drafts everything.

## Open risks

- The final-second asks may not be hittable (stale feeds / already-taken). Then post #2 is "we tested it, here is why
  it is not real" — still the honest-research brand, but the terminal loses its headline scanner; decided games and locks
  carry it.
- Polymarket US / Kalshi API terms on redistribution of market data (check before the API sells anything derived from
  the venues' books; our own derived signals and settlement arithmetic are ours).
- Venue rule changes (e.g., trading halts in the final seconds) would close the terminal-seconds edge overnight.
- Capital: we have ~$12 in the markets. The business does not depend on it; the research credibility does depend on the
  bots trading real money, however little.

## Decisions log

- 2026-11-07 — Name: PredictionBots.io. Stack as above. Hotfixes go straight to main; strategy/cap/switch changes via PR.
- 2026-11-07 — Mr H (Coinbase hopper) demoted to a lottery ticket (≥5% impulse, 8% trail, maker-only, 4 hops/day) after
  the replay; not a strategy, a published experiment.
- 2026-11-07 — Mr T (terminal sniper) is the headline hypothesis; dry run first, live only on Noah's word.
- 2026-11-08 — Index feed lags the clock by ~10 s; gate recalibrated (44 prints, 10-bps margin). Lesson for the terminal:
  every scanner must state its data latency.
- 2026-11-08 — Monetization order (Noah's suggestion, adopted with one carve-out): sticky first, paid second. No programmatic
  ads (audience blocks them, gambling classification restricts inventory, and the ads that would run are the bot vendors
  we benchmark). Classy alternatives: venue referral programs (verify Kalshi / Polymarket US terms and payouts) and, later,
  one labeled sponsor slot with a published no-bot-vendor rule. Carve-out: the x402 data API stays live from day one as
  the zero-user revenue probe.
- 2026-11-08 — Product rule: nothing requires a signup walkthrough. Anonymous gets the ledger, research, benchmark and a
  delayed scanner preview; one tap (Google, Apple or magic link — Clerk free tier) saves alerts and watchlists; a card
  only on upgrade to real-time alerts + cockpit. The data API never needs an account.
- 2026-11-08 — Bot Benchmark promoted to a first-class free product (the market research found 115 bots and zero
  independent tests; every review site is vendor-run). Vendors get an unedited reply under their row; we take no
  referral fees from any bot vendor.
- 2026-11-08 — Visuals: D3 v7 for the signature animated explainers built from recorded reality (1-s index prints and books);
  TradingView lightweight-charts for time series in the terminal; chart text as indexable SVG. First three: "Watch the
  settlement lock" (real 5-minute window replay), "After you buy the spike" (1,172 signal paths), "A lock appears and
  closes" (two venues, one contract, fee band).
- 2026-11-08 — SEO is an architecture, not adjectives: /benchmark/<bot> pages (the "is it legit" query, 115 of them),
  /learn/ settlement and fee explainers carrying the visualizations, research posts with Article/FAQ/Dataset structured
  data and OG images. Titles from personas' pain points (bot shopper, builder, active trader). Skeleton before launch.
- 2026-11-08 — Mr. T falsified. Six-hour dry run plus a confirmation run with raw books: in the final seconds the winning
  side is bid at 0.99 (tens of thousands of contracts) and never offered; the loser is offered at 0.01 and never bid.
  The recorder's 168 "cheap winners" were stale book snapshots. Retired as a trade; the sniper code stays as the
  final-seconds measurement feed and the post-2 story. Consequence: Mr. P's cross-venue "locks" are unproven until
  rebuilt on a live book with age checks. Validated scanner list for the terminal is now: decided games (Mr. S).
- 2026-11-08 — Pivot (Noah): we are not trading any more. PredictionBots becomes the sane resource for people the markets
  lead into near-certain losses: what not to buy (Bot Benchmark), what the hoop really is (True Cost tools), research
  that tests claims live (post 2: the "free money" that wasn't), the historical ledger as proof we played and lost like
  everyone else, later a Reality Check browser extension. All live trading switched off (mrh/LIVE_ON removed; Mr. S and
  Mr. T off). The recorder keeps running: the data is the product. Decided-games scanner shelved (helps a few take
  money from slower players; not the mission). Revenue model: venue referrals with the truth above the button (Noah
  to decide on the ethical stance), aligned sponsors, premium research, data licensing, API probes.
