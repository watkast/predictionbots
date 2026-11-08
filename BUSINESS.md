# PredictionBots — the business (living document)

Started 7 Nov 2026. Owner: Noah Watson. PM: Claude. This file is the plan of record; it changes as we learn. Decisions
are appended at the bottom with the date and the reason, so the reasoning survives.

## What we are

The sane resource for people the prediction markets (Polymarket US, Kalshi) lead into near-certain losses. We do not
trade; we did, at tiny size, lost like everyone else, and published it. We measure: what the fees really cost, which
bots actually work, how markets settle, what the real-world odds are, and who is paid to tell you to bet. The model is
Wirecutter for prediction markets: a public service, funded by the commerce it informs, with the truth above every
button.

## What we ship (in order)

1. **True Cost tools** — fee per trade from the venue's own formula, fees per month, expected loss with no edge,
   break-even win rate, streak odds, time-to-ruin; shareable result cards. Free.
2. **Bot Benchmark** — every bot sold for these venues, its published rule run on paper against our recorded books for
   30 days, with sample size, coverage % and the data file; a vendor reply under each row; one page per bot. Free.
3. **Market pages** — one page per market on both venues, generated from the venues' APIs: the premise in plain
   language, market price vs real-world odds (50/50 by construction for crypto minutes; sportsbook consensus for sports;
   NWS for weather; the score for in-play), the fee at that price, and a "luck needed" meter. The 😈 voice mocks the
   game, never the player, never a venue by name. This is the SEO engine: thousands of pages, each with numbers nobody
   else publishes.
4. **Research + Learn** — measured posts with code and data (post 1: the pump candle; post 2: the free money that
   wasn't; post 3: the bot market), D3 explainers built from recorded reality, and evergreen pages for the questions a
   loss or a headline makes people type (fees explained, how settlement works, is Kalshi safe, can I withdraw, how
   insider trading works and gets caught).
5. **Prediction News + the Endorsement Ledger** — what is being reported, linked to its sources, with one measurement of
   ours under each headline, auto-posted to X (account labeled automated). The Ledger: every public promoter of either
   venue, the quote verbatim with source, disclosed pay or "not disclosed", and the True Cost of the market promoted.
   Pro-market voices included; it is a ledger, not a hit list. No decoy or filler content, ever.
6. **The Floor** — a two-sided thread (Defend / Deviate) under every benchmark row, post, market and rule. Read free;
   post with one tap (Clerk: Google, Apple, email link). Data-backed posts count double. House rules: patterns and
   public records, never a private person's name without a court or exchange filing; vendors wear a badge; no
   referral links in posts. UGC on our domain compounds the SEO.
7. **Our ledger (historical)** — every trade our bots made, closed 8 Nov 2026, kept as proof we played and lost.
8. **Data** — the recorder's one-second books, index prints and settlements; per-call x402 API for builders and agents;
   dataset licences for journalists, academics and lawyers. Later: a Reality Check browser extension (your real P&L,
   fees paid and expected loss on the venue's own page).

Shelved: the trading terminal and its scanners (final seconds falsified live; decided games would only move money from
slower players; cross-venue locks unproven until rebuilt on a live book).

## How we make money (and the order)

Sticky first, paid second. Revenue legs, strongest-in-a-crackdown first:
1. **Data licences and the API** — gets stronger with every scandal (journalists, class actions, researchers).
2. **Members** (~$8/month) — data files early, the methods, a monthly measured report. The site stays free.
3. **Venue referrals** — Kalshi (trade $25 → $25 credit) and Polymarket US (deposit $10 + 1 trade → $25 bonus) pay
   publishers per sign-up. We apply once the site is live. The card shows exactly what happens, step by step, with the
   fees and odds above the button and our payment disclosed; venue-supplied creative only; geo-gated; switchable in a
   day. Opportunistic, never structural: it is the first thing a crackdown kills, and partner contracts carry
   non-disparagement clauses, so the data does the talking and the message never depends on the money.
4. **One labeled sponsor slot** — tax, security, education, legal. Never a bot vendor, never a venue we measure.
No ad networks. No money from bot vendors. No personal refer-a-friend codes used as a publisher (breaks venue terms).

Break-even ≈ $115/month (AI subscription ~$100, domain ~$3, Dell power ~$10; Cloudflare free tiers). First dollar =
first referral payout, first member, or first USDC to the API wallet. This is a media business: it earns through
traffic, and search traffic takes months; X threads and Reddit answers pay in days and bridge the gap.

## Why this and not trading

Our own 30-day replay killed the retail-momentum idea (1,172 signals, −1.86%/trade). Our live test killed the
final-seconds idea (the winner is bid at 0.99 by the thousand and never offered). What is left is the truth about the
game, which nobody with venue or vendor money will publish. Regulatory pressure is rising (DOJ/CFTC insider-trading
case, Kalshi candidate suspensions, CFTC surveillance letters, a congressional probe): if it bursts, a truth-telling
resource that is already standing is the best-positioned site on the internet; if it drags on, the benchmark and True
Cost pay the same either way. Nothing in the plan depends on timing.

## Stack

GitHub (code, the recorder on Actions as backstop, data branches as the public record) · Cloudflare Pages (site) ·
Cloudflare Workers + D1/KV (x402 API, the Floor, waitlist) · Clerk (one-tap sign-in, free tier) · the Dell T3600 at
home (always-on recorder, benchmark runner, publisher; outbound only behind T-Mobile CGNAT, Cloudflare Tunnel if it ever
needs to serve) · Stripe or Substack paid (members) · X (automated news account + Noah's) · Substack (long form).

## The clean data point (what makes us as accurate as anyone)

Trading was never the data source; the recorder is, and it needs zero dollars. Four things make it citable: redundant
recording (Dell + Actions backstop), a published coverage % with gaps listed, raw files public with checksums, and a
daily cross-check against the venues' own candle history. Fills in the benchmark are paper fills at displayed depth,
stated on every row. The accounts at both venues stay open for API keys only; balances go to zero.

## Open risks

- Nobody wants to hear it: lead with the questions people already search; the warning rides on the answer.
- Search takes months: the API probe, X threads and Reddit answers run in parallel from day one.
- Referral money contradicts the message: truth above the button, pay disclosed, switchable in a day; if a partner
  contract's non-disparagement terms conflict with the message, we drop the referral, not the message.
- Venues object (cut referrals, rate-limit the recorder, send a letter): public data only, cited; derived numbers and
  settlement arithmetic are ours; verify both venues' data-redistribution terms before the API sells anything
  book-derived.
- Defamation via the Ledger or the Floor: verbatim quotes with sources, no causal claims about anyone's losses,
  Section 230 for user posts, house rules enforced, a lawyer's read before the Ledger goes live.
- Programmatic pages read as spam to Google: every page carries unique live numbers; series pages, not expiring
  instances; launch the categories with real search demand first.
- The home box or the home connection goes down: Actions stays as the backstop runner.
- We mistake luck for signal: every claim ships with its sample size and data file; our own failures are published first.
- The AI subscription lapses: the sequence reaches for the first dollar early; code and docs are readable without it.

## Decisions log

- 2026-11-07 — Name: PredictionBots.io. Stack as above. Hotfixes go straight to main; strategy/cap/switch changes via PR.
- 2026-11-07 — Mr H (Coinbase hopper) demoted to a lottery ticket (≥5% impulse, 8% trail, maker-only, 4 hops/day) after
  the replay; not a strategy, a published experiment.
- 2026-11-07 — Mr T (terminal sniper) is the headline hypothesis; dry run first, live only on Noah's word.
- 2026-11-08 — Index feed lags the clock by ~10 s; gate recalibrated (44 prints, 10-bps margin). Lesson for the terminal:
  every scanner must state its data latency. (Later corrected: the first refusals were the bot connecting 50 s before
  the close, not feed lag; defaults kept because the margin governs.)
- 2026-11-08 — Monetization order (Noah's suggestion, adopted with one carve-out): sticky first, paid second. No programmatic
  ads (audience blocks them, gambling classification restricts inventory, and the ads that would run are the bot vendors
  we benchmark). Classy alternatives: venue referral programs (verify Kalshi / Polymarket US terms and payouts) and, later,
  one labeled sponsor slot with a published no-bot-vendor rule. Carve-out: the x402 data API stays live from day one as
  the zero-user revenue probe.
- 2026-11-08 — Product rule: nothing requires a signup walkthrough. Anonymous gets everything free; one tap (Google, Apple
  or magic link — Clerk free tier) saves alerts and watchlists and lets you post. The data API never needs an account.
- 2026-11-08 — Bot Benchmark promoted to a first-class free product (the market research found 115 bots and zero
  independent tests; every review site is vendor-run). Vendors get an unedited reply under their row; we take no
  referral fees from any bot vendor.
- 2026-11-08 — Visuals: D3 v7 for the signature animated explainers built from recorded reality (1-s index prints and books);
  TradingView lightweight-charts for time series; chart text as indexable SVG. First three: "Watch the settlement lock",
  "After you buy the spike", "A lock appears and closes".
- 2026-11-08 — SEO is an architecture, not adjectives: /benchmark/<bot> pages, /markets/<venue>/<series> pages, /learn/
  explainers, research posts with Article/FAQ/Dataset structured data and OG images. Titles from personas' pain points
  (bot shopper, losing trader, builder/journalist). Skeleton before launch.
- 2026-11-08 — Mr. T falsified. Six-hour dry run plus a confirmation run with raw books: in the final seconds the winning
  side is bid at 0.99 (tens of thousands of contracts) and never offered; the loser is offered at 0.01 and never bid.
  The recorder's 168 "cheap winners" were stale book snapshots. Retired as a trade; the sniper code stays as the
  final-seconds measurement feed and the post-2 story. Consequence: Mr. P's cross-venue "locks" are unproven until
  rebuilt on a live book with age checks.
- 2026-11-08 — Pivot (Noah): we are not trading any more. PredictionBots becomes the sane resource for people the markets
  lead into near-certain losses. All live trading switched off (mrh/LIVE_ON removed; Mr. S and Mr. T off). The recorder
  keeps running: the data is the product. Decided-games scanner shelved.
- 2026-11-08 — Referrals: yes, with the truth above the button (Noah). Verified offers: Kalshi trade $25 → $25 credit (not
  withdrawable, 90 days, 46 states + DC); Polymarket US deposit $10 + 1 trade → $25 bonus (1× playthrough, not NV).
  Publishers (RotoWire, Action Network, Covers) run these via partner codes, so programs exist; we apply once the site is
  live. Venue-supplied creative, "here's the deal" disclosure, our rate published, geo-gated, switchable in a day.
  Opportunistic, never structural. No personal refer-a-friend codes as a publisher.
- 2026-11-08 — The Floor (Noah): accounts exist so a debate forum can exist. "Deviants vs defenders" two-sided threads
  under everything; UGC on our domain is the engagement and SEO engine. House rules as above.
- 2026-11-08 — Macro thesis (Noah, "assuming"): a crackdown is coming. Plan sized to win in both branches: pre-build the
  crisis pages; move data licensing up (it strengthens with scandal); referrals stay opportunistic. Nothing depends on
  timing.
- 2026-11-08 — Market pages + Prediction News (Noah): adopted. Real-world odds and a luck meter on a page per market;
  news told by its sources with our number attached and auto-posted. Rejected: the word "disguise" and any decoy/filler
  content. The numbers are the inflammatory content; honesty is the temperature control. Non-profit structure rejected
  for now (3–12 months to 501(c)(3), no ownership, referral income taxed as UBI anyway); for-profit LLC on the Wirecutter
  model, a nonprofit arm later if grant money appears.
- 2026-11-08 — Endorsement Ledger (Noah): adopted as part of Prediction News, with guardrails: verbatim quotes with
  sources, disclosed pay or "not disclosed", no causal claims about losses, pro-market voices included, lawyer's read
  before launch.
- 2026-11-08 — X policy risk found: X's paid-partnership policy (Feb 2026) bars affiliate accounts from posting gambling
  content; Kalshi removed its X affiliate badges on 23 Feb 2026. The Prediction News X account is editorial only, never
  a badged affiliate, never carries referral codes; referral links live on the site under the disclosure. Category
  economics (iGB Affiliate, Nov 2025): ~$100 CPA or less per new trader, sometimes $5 per $1,000 traded; ask for CPA.
  Drafted both partner applications (marketing/partners.md).
- 2026-11-08 — Fee schedules verified at the source: Polymarket US (effective 6 Nov 2026) tiers the taker coefficient by
  30-day volume: 9.5% under $10k (most people), 8.5%, 7.5%, 6.95% above $250k; new accounts 6.95% for days 1–7. A 37%
  increase for the ordinary account; first Prediction News item (post + thread). Kalshi (7 Jul 2026): taker 7%, maker
  1.75% on most sports/econ series, crypto minute series maker-free, rounding up to the centicent. All calculators,
  the simulator and the market pages use the real ladders with a tier selector.
- 2026-11-08 — "Same money, elsewhere" (Noah's idea, adopted with one line drawn): under True Cost and the simulator, the
  expected trading result next to the same bankroll in 4-week T-bills and I-bonds (official rates fetched at build
  time and dated), then honest fast-cash options (no referral codes), then help (1-800-GAMBLER call/text/chat, NCPG
  state lookup, GA, self-exclusion). No investment affiliate links for now: same conflict as venue referrals plus
  financial-advertising rules; TreasuryDirect first. Revisit only with a clean partner contract and full disclosure.
- 2026-11-08 — Learn pages shipped with sources and check dates: Polymarket US fees, Kalshi fees, how 5-minute crypto
  markets settle, insider trading on prediction markets (2026 cases, pattern-level, names only where a filing exists),
  what the research says (Hollenbeck/Larsen/Proserpio 2024; NCPG prevalence; wallet-loss analyses). "Is Kalshi safe"
  and "Can I withdraw" wait for primary sources; no page is better than a wrong one.
- 2026-11-08 — Deploy path: GitHub Actions builds and publishes to Cloudflare Pages hourly and on push once Noah adds the
  CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID secrets; the Dell is the recorder only (ops/dell runbook ready).
  Accessibility is a standing check (site/a11y_check.js, 0 axe violations); theme switch System/Dark/Light everywhere.
