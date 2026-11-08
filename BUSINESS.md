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
