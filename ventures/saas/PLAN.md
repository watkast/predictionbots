# Micro-SaaS / data-API portfolio — operating plan (2026-10-17)

Owner: solo US operator on a phone. Agents build, deploy, bill and support; the owner does
the handful of KYC/account steps in §g once. Goal: 5–10 tiny products, near-zero human
time, each judged by the kill rules in §f. Everything below cites its source; where the
source is a competitor's blog, that is said.

## The honest frame first

* **Base rate is bad.** 67.8 % of Stripe-verified founder businesses on TrustMRR earned under
  $1,000 *lifetime*; the median indie hacker makes under $1k/month and "only ~30 % ever pass
  $1k MRR"; TrustMRR median monthly growth had slowed to 1.6 % by June 2026
  ([mean.ceo stats](https://blog.mean.ceo/indie-hacker-business-statistics/)). A portfolio of
  ten is the right shape precisely because most entries will do ~$0.
* **Marketplaces are saturated with clones.** Apify Store lists 89,427 Actors
  ([apify.com/challenge](https://apify.com/challenge)); the three "Kalshi + Polymarket odds"
  Actors we found have 6, 13 and 0 monthly active users
  ([lizaraco](https://apify.com/lizaraco/prediction-market-data),
  [scrapesage](https://apify.com/scrapesage/prediction-markets-scraper)); an RSS-to-JSON
  Actor has 23 users / 1 MAU ([xtech](https://apify.com/xtech/feed-extractor)); an email
  checker has 2 users ([swiftkit](https://apify.com/swiftkit/email-check)). Listing is not
  distribution.
* **The money that does exist is real but concentrated.** Apify says it paid developers
  $1.7M "last month", that "many developers earn over $3k", and that the top independent
  creators clear $10k MRR ([Apify help](https://help.apify.com/en/articles/8684010-how-does-actor-monetization-work),
  [Apify blog](https://blog.apify.com/programmer-passive-income-web-scraping/)). Those are
  scrapers of Google Maps / Instagram / TikTok with tens of thousands of users — ToS-grey,
  support-heavy, and outside the selection criteria below.
* **Fees are large.** RapidAPI keeps a flat 25 % and pays by PayPal only, ~2 months after
  the charge ([RapidAPI payouts](https://docs.rapidapi.com/docs/payouts-and-finance)); Apify
  keeps 20 % after deducting platform costs; Gumroad is 10 % + $0.50 plus card fees (30 % on
  Discover) ([checkoutpage.com](https://checkoutpage.com/blog/gumroad-fees), competitor blog);
  Lemon Squeezy MoR is 5 % + $0.50 (+0.5 % on subscriptions, +1.5 % international)
  ([dodopayments review](https://dodopayments.com/blogs/lemonsqueezy-review), competitor
  blog); Stripe Managed Payments MoR is 3.5 % on top of 2.9 % + $0.30
  ([dodopayments](https://dodopayments.com/blogs/stripe-managed-payments-fees-explained),
  competitor blog). On a $9/mo product the all-in take is 30–45 % on marketplaces, ~9 % on a
  Stripe payment link.
* **What is actually different about us:** the repo already has fee models, de-vig code, a
  multi-venue recorder, weather-ensemble calibration and a CI runner with internet. Products
  that reuse those have a defensibility score > 1; everything else is a clone of a $99/mo
  incumbent with a cheaper price tag.

## (a) Selection criteria — what agents can run with zero humans

A candidate must pass **all** of these, else it is not listed:

1. **API-first / file-first.** Request in, JSON (or file) out. No dashboards to support, no
   onboarding flow, no accounts to reset. A payment link + API key is the whole funnel.
2. **No customer-support load by design.** Stateless, deterministic, self-describing
   (OpenAPI + examples + MCP tool schemas). Errors are 400s with a sentence. Refunds are
   automatic via Stripe's customer portal / marketplace rules. Support inbox is an
   auto-responder plus a GitHub issue template that an agent triages.
3. **No content moderation.** No user-generated content stored or published; no scraping of
   social platforms (Raycast rejects "scraping a website without permission"
   ([Raycast guidelines](https://manual.raycast.com/extensions-guidelines.md)); Apify's top
   earners live there and so do the takedowns).
4. **No regulated or sensitive data.** No PII storage, no health/financial account data, no
   payment data (Stripe/LemonSqueezy hold it), no children. Inputs that are PII-adjacent
   (emails, IBANs) are allowed only if never logged and the privacy policy says so.
5. **Builds and tests offline.** Pure functions + fixtures; network only at runtime in the
   host. No secrets needed to pass CI.
6. **Runs on a free or ≤ $5/mo host** (§d), with cost that cannot run away (Workers Free
   hard-stops at 100k req/day rather than billing).
7. **Positive unit economics at $9/mo after a 25–45 % marketplace take**, i.e. hosting cost
   per subscriber ≈ $0.
8. **An agent can publish and update it without a human in the loop** after the one-time
   account setup (§g): CLI or REST publishing exists (wrangler, Stripe API, RapidAPI
   OpenAPI provisioning API, `apify push`, `mcp-publisher`).
9. **Kill-able in one commit.** No long-lived customer data; sunsetting = disable payment
   link, 30-day notice email via Stripe, delete the Worker.

Score = **demand × ease × defensibility ÷ support load**, each 1–5. Demand is scored from
paid competitors' price points and marketplace listing counts (a proxy, not search volume —
no keyword tool is reachable from here; Google Trends is a follow-up for CI).

## (b) Ten candidates, ranked

| # | id | demand | ease | defens. | support | score | one line |
|---|---|---|---|---|---|---|---|
| 1 | `oddsmath` | 2 | 5 | 3 | 1 | **30** | odds conversion, 4-method devig, EV/Kelly, Kalshi/Polymarket/Novig fee models, arb + complete-set checks; REST + MCP |
| 2 | `pm_odds_feed` | 3 | 3 | 4 | 2 | **18** | normalised live + historical Kalshi/Polymarket/Novig books from the repo's recorder |
| 3 | `bizdays` | 4 | 4 | 1 | 1 | **16** | holidays + business-day arithmetic, bundled data |
| 4 | `weatherprob` | 2 | 3 | 4 | 2 | **12** | ensemble P(high ≥ X) at the NWS stations Kalshi settles on |
| 5 | `cronsense` | 2 | 5 | 1 | 1 | **10** | cron explain / next-runs / jitter, REST + MCP |
| 6 | `tzsolar` | 3 | 3 | 1 | 1 | **9** | timezone for coordinates + sunrise/sunset, offline |
| 7 | `idcheck` | 3 | 4 | 1 | 2 | **6** | IBAN/BIC/VAT/EIN checksum validator, no lookups |
| 8 | `mailhygiene` | 4 | 4 | 1 | 3 | **5.3** | email syntax + disposable + typo check |
| 9 | `feedjson` | 3 | 3 | 1 | 2 | **4.5** | RSS/Atom → JSON with filters + webhooks |
| 10 | `linkmeta` | 4 | 3 | 1 | 3 | **4** | OpenGraph / link-preview API |

Evidence per candidate (demand = who already pays, and how much):

1. **oddsmath.** Consumer +EV tools charge $199–999/mo (OddsJam Gold/Platinum,
   [oddspapi blog](https://oddspapi.io/blog/?p=2860), competitor) and the odds-API market
   sits at $25/mo (The Odds API) to $149–499/mo (SportsGameOdds) to $3–5k/mo (Unabated,
   OpticOdds) ([sportsgameodds comparison](https://sportsgameodds.com/comparing-odds-api-providers/),
   vendor page). None of them sell the *math* layer alone; free devig calculators exist as web
   pages (e.g. [matthewmarks](https://production.matthewmarks.com/?p=37438)), so willingness
   to pay for the API is low (demand 2). Defensibility 3 because the Kalshi/Polymarket/Novig
   fee models come from the repo's verified `pb/core/fees.py` and `pb/venues/novig.py` and
   nobody else ships them; an MCP server makes it usable by agent-builders, a channel with
   almost no incumbents. Support 1: pure math, no upstream.
   **Builds with no secrets — this is product #1, scaffolded in `ventures/saas/oddsmath/`.**
2. **pm_odds_feed.** Paid prediction-market data exists but is thin: Apify Actors at
   $1.66–2.10 per 1k snapshots with ≤ 13 users
   ([lizaraco](https://apify.com/lizaraco/prediction-market-data),
   [scrapesage](https://apify.com/scrapesage/prediction-markets-scraper)); simplefunctions.dev
   sells "contracted tiers" over Kalshi+Polymarket normalised books and Brier calibration
   ([simplefunctions](https://simplefunctions.dev/data)); Bot-for-Kalshi charges $99/mo for
   rule automation on the user's own account
   ([botforkalshi](https://www.botforkalshi.com/blog/kalshi-weather-trading-strategy),
   vendor). Our recorder already writes books/trades/settlements per venue per day
   (`README.md`, "Paper matrix"), so the marginal build is an R2 publisher + a Worker that
   serves JSON. Risk: Kalshi/Polymarket ToS on redistribution must be read before launch;
   Novig data is behind a signed WS. Needs a Cloudflare account (R2) to deploy, not to build.
3. **bizdays.** Abstract charges $99/mo and forbids commercial use on the free tier;
   HolidayAPI's "States & Provinces" plan is $399/yr; Calendarific free tier is 500 req/mo
   with attribution; Nager.Date is free and has no business-days endpoint
   ([holidaydb comparison](https://holidaydb.com/blog/holiday-api-comparison-2026),
   competitor blog, prices checked July 2026). Clear demand, zero moat (the Python `holidays`
   package is the data). Wins only on price + the working-day endpoints.
4. **weatherprob.** Kalshi's weather markets are popular enough to have their own help page
   ([Kalshi help](https://help.kalshi.com/markets/popular-markets/weather-markets)) and a $99/mo
   bot vendor whose own article admits the bot "does not convert forecasts into
   probabilities" ([botforkalshi](https://www.botforkalshi.com/blog/kalshi-weather-trading-strategy)).
   The repo's `mm_weather_ladder` already does exactly that from Open-Meteo ensembles
   (no key). Demand 2: the audience is a few hundred traders. Defensibility 4: calibration
   from recorded settlements is the product. Support 2: "why was your 72 % wrong" emails.
5. **cronsense.** crontab.guru is free and dominant; there is no paid incumbent, which means
   demand for *paying* is low (2). Ease 5. Listed because an MCP tool "explain this cron and
   give me the next 5 runs in America/Chicago" is cheap to add to the same Worker as #1.
6. **tzsolar.** TimeZoneDB/Abstract-style APIs exist with free tiers; demand 3 from
   calendar/IoT builders; data (tz boundaries) is open; no moat.
7. **idcheck.** iban.com charges €530/yr for 2,000 lookups and €1,450/yr for 20,000
   ([iban.com pricing](https://www.iban.com/pricing)); Abstract's IBAN API is $99/mo for
   60k ([abstractapi](https://www.abstractapi.com/api/iban-validation)). A checksum-only
   validator at $9/mo undercuts both but is a 200-line library; PII-adjacent, so log nothing.
8. **mailhygiene.** Dozens of listings on Zyla/RapidAPI/Apify
   ([zylalabs](https://zylalabs.com/en/api-marketplace/security+%26+cybersecurity/disposable+mail+validator+api/5677));
   the Apify clone has 2 users. Emails are PII; GDPR deletion requests are support load.
9. **feedjson.** Apify has at least six RSS-to-JSON Actors, best one 23 users
   ([xtech](https://apify.com/xtech/feed-extractor)); FiveFilters sells JSON output "on all
   paid plans" ([fivefilters](https://www.fivefilters.org/?p=3813)). Needs scheduled fetches
   (Workers Cron) and per-customer state → more support.
10. **linkmeta.** microlink Pro is $49/mo for 46k requests, free tier 100/mo
    ([microlink](https://microlink.io/link-preview)); opengraph.io has a free tier
    ([opengraph.io](https://www.opengraph.io/products/preview-metadata)); five+ Apify clones.
    Real demand, but every blocked fetch becomes a ticket (support 3).

Not listed, and why: screenshot APIs (need Browser Rendering, 10 min/day free, support-heavy);
anything scraping Google/Meta/TikTok (ToS, moderation, the Apify money is there but criterion
3 fails); exchange-rate APIs (free incumbents, upstream dependency); Chrome extensions
(payments must go through a third party since Feb 2021 —
[CWS deprecation](https://developer.chrome.com/webstore/cws-payments-deprecation) — and the
largest such processor self-reported $220/mo
[ExtensionPay on IH](https://www.indiehackers.com/product/extensionpay/revenue)); GitHub
Marketplace paid apps (need a verified-publisher org, 100 installs, monthly+annual plans —
[GitHub docs](https://docs.github.com/en/apps/github-marketplace/creating-apps-for-github-marketplace/requirements-for-listing-an-app)).

## (c) Distribution channels that need no human after setup

| channel | take | payout | automated publishing | ToS limits that matter |
|---|---|---|---|---|
| **RapidAPI Hub** | flat 25 % on all Hub payments (processing included since 2025-11-15) | PayPal only; month M charges paid end of M+1 (Jan subs arrive early March) | yes: OpenAPI "Create API / Update API" provisioning endpoints for CI ([docs](https://docs.rapidapi.com/docs/automating-api-provisioning)); Enterprise uses a different Platform API | must link a PayPal email or nothing is paid; W-9 on request ([payouts doc](https://docs.rapidapi.com/docs/payouts-and-finance)) |
| **Stripe payment links** | 2.9 % + $0.30 card; +0.7 % Billing for subscriptions; Stripe Tax 0.5 %/txn (calculates, does not file in most places) ([flexprice](https://flexprice.io/blog/stripe-pricing-breakdown-2026), competitor; verify on stripe.com/pricing) | standard payouts free on Stripe's schedule; 90-day holds possible on risk triggers | yes: `POST /v1/payment_links` with recurring prices and trials ([Stripe docs](https://docs.stripe.com/payments/payment-links/api)); key delivery via webhook → GitHub Action → `wrangler secret put API_KEYS` | account needs human KYC (§e); you are merchant of record for sales tax unless you add Managed Payments (+3.5 %) |
| **Lemon Squeezy (MoR)** | 5 % + $0.50, +0.5 % subs, +1.5 % intl/PayPal | twice-monthly, free to US bank | API + webhooks | Stripe-owned since 2024, "slower support, fewer updates", migration path to Stripe Managed Payments ([dodopayments](https://dodopayments.com/blogs/lemonsqueezy-review), competitor) |
| **Apify Store** | 20 % of profit after platform costs (rental: 20 % of earnings) | monthly | yes: `apify push` from CI | pay-per-event must respect user spend limits; 89k Actors; our criteria exclude the scraping categories that earn ([help](https://help.apify.com/en/articles/8684010-how-does-actor-monetization-work), [PPE docs](https://docs.apify.com/platform/actors/publishing/monetize/pay-per-event)) |
| **Gumroad** | 10 % + $0.50 + card fees (30 % flat on Discover) | weekly Fridays, $10 minimum | product creation is dashboard-first; API is licences/sales | fine for one-off files (datasets, templates), poor for APIs ([checkoutpage](https://checkoutpage.com/blog/gumroad-fees), competitor) |
| **GitHub Marketplace** | n/a for Actions (free listings only); paid *apps* need a verified-publisher org and 100 installs | — | listing is manual | not a channel for us until something has 100 installs ([docs](https://docs.github.com/en/apps/github-marketplace/creating-apps-for-github-marketplace/requirements-for-listing-an-app)) |
| **Chrome Web Store** | $5 one-time dev fee; no in-store payments since 2021-02-01 | via your own processor | review queue, manual | payments → Stripe/ExtensionPay yourself ([CWS](https://developer.chrome.com/webstore/cws-payments-deprecation)) |
| **Raycast Store** | no payments at all | — | PR to the extensions repo, human review ≤ 1 week, stale after 14 days | free distribution only; rejects scrapers ([guidelines](https://manual.raycast.com/extensions-guidelines.md)) |
| **MCP registry + directories** | none (metadata only) | — | yes: `mcp-publisher login github && mcp-publisher publish`, GitHub Actions supported; package must be on npm/PyPI with `mcpName` ([quickstart](https://modelcontextprotocol.io/registry/quickstart)) | registry "in preview, data resets may occur"; monetise through the API key the remote server requires |

Plan: **RapidAPI for discovery, Stripe payment link for margin, MCP registry for the
agent-builder audience.** The same Worker serves all three (proxy secret vs API key, see
`oddsmath/README.md`).

## (d) Hosting that runs free or near-free

| host | free allowance (hard numbers) | what stops you | commercial use |
|---|---|---|---|
| **Cloudflare Workers Free** | 100,000 req/day, 10 ms CPU/request; KV 100k reads + 1k writes/day, 1 GB; D1 5M rows read/100k written per day, 5 GB; R2 10 GB + 1M class-A ops/month; Python Workers GA 2026-09-21, 64 MiB uncompressed bundle on free and paid | over 100k/day the Worker returns errors, it does not bill; Paid is $5/mo minimum | allowed ([pricing](https://developers.cloudflare.com/workers/platform/pricing/), [Python GA](https://byteiota.com/cloudflare-python-workers-ga/) third-party write-up) |
| **Vercel Hobby** | 100 GB bandwidth, 100k function invocations/month, 10 s function timeout | functions stop at the cap | **prohibited** — "Hobby plan explicitly prohibits commercial use" ([deploywise](https://deploywise.dev/blog/vercel-free-tier-limits-2026), competitor; confirm in Vercel ToS) → not usable |
| **Fly.io** | none for new orgs (trial: 2 h of machine time or 7 days); smallest machine shared-1x/256 MB ≈ $2.19/mo | card required after trial | allowed ([temps.sh](https://temps.sh/blog/fly-io-pricing-2026), third-party) — fallback for anything needing a long-lived process |
| **GitHub Pages** | 1 GB site, 100 GB/mo soft bandwidth, 10 builds/h | 429s | **prohibited** for "commercial SaaS" or "sites focused on commercial transactions" ([GitHub docs](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)) → docs/landing only, never checkout |
| **GitHub Actions** | already used by this repo for scheduled jobs with internet | minutes quota on private repos | fine for cron publishers (metrics pull, R2 upload), not for serving |

Decision: Workers Free for every product; Fly $2.19/mo only if a product needs a daemon.
Budget cap for the whole portfolio: **$10/mo** before any product has revenue.

## (e) Legal minimums

* **Entity:** an LLC is optional for a US sole proprietor; Stripe accepts "Sole Proprietor"
  as a legal-entity type and verifies legal name, SSN/ITIN (EIN if registered), and a
  physical business address — no PO boxes
  ([Stripe support](https://support.stripe.com/questions/requirements-for-having-a-us-stripe-account)).
  Form an LLC later if revenue > ~$1k/mo or a product touches anything regulated.
* **Payments / KYC:** Stripe (and RapidAPI's PayPal, Apify's payout profile) need a human to
  complete identity verification once. Agents can never do this; it is §g step 1.
* **Sales tax / VAT:** two options. (1) Stripe Tax at 0.5 %/txn *calculates* but "does not
  file or remit in most jurisdictions" ([flexprice](https://flexprice.io/blog/stripe-pricing-breakdown-2026),
  competitor) — fine while under every state's economic-nexus threshold (typically $100k
  sales, which we will not reach). (2) A merchant of record (Lemon Squeezy 5 % + $0.50 or
  Stripe Managed Payments +3.5 %) takes the liability entirely. Start with Stripe + Stripe
  Tax off; switch to Managed Payments the month MRR passes $500.
* **Privacy policy / ToS:** required by RapidAPI listings, GitHub Marketplace, MCP registry
  good practice and Stripe's checkout. Template (agents fill the blanks):
  > *Service*: {product} is a stateless HTTP API operated by {legal name}, {state}. *Data*:
  > request bodies are processed in memory and not stored; access logs (IP, path, status)
  > are kept ≤ 30 days by Cloudflare for abuse prevention. *Payments*: handled by Stripe /
  > RapidAPI; we never see card numbers. *Refunds*: any charge within 14 days, no questions,
  > via the Stripe customer portal link in your receipt. *Availability*: best effort, no
  > SLA; status at {url}. *Liability*: outputs are mathematical estimates, not financial or
  > betting advice; use at your own risk. *Contact*: {support email}. *Changes*: posted
  > here with the date.
* **Gambling-adjacent disclaimer** for `oddsmath`/`pm_odds_feed`/`weatherprob`: they compute
  numbers; they place no bets, hold no funds and are not a sportsbook — keep that sentence in
  every README and listing.

## (f) Kill criteria and dashboard metrics

Per product, evaluated monthly by `ventures/saas/metrics.py` from `metrics.json`:

| rule | threshold | action |
|---|---|---|
| no traction | MRR < $20 at 60 days after launch | `SUNSET`: disable payment link, 30-day notice, delete Worker, status→sunset |
| support load | > 60 owner-minutes in 30 days | `SUNSET` (the whole point is zero human time) |
| reliability | uptime < 99.0 % for 2 consecutive months | `SUNSET` or move host |
| economics | revenue − cost < 0 for 2 consecutive months | `SUNSET` |
| portfolio | fewer than 3 products live after 6 months, or total MRR < $100 after 9 months | stop adding products; reassess the venture in `research/non_trading_ventures.md` |

Dashboard must show, per product and in total: **MRR, revenue 30d, subscribers, churn 30d
%, support tickets + minutes 30d, uptime 30d %, cost 30d, net 30d, requests 30d, verdict
(OK / WATCH / SUNSET) with reasons.** Schema is in the `metrics.py` docstring; the file is
written by a scheduled GitHub Action (future) that pulls Stripe `subscriptions`, RapidAPI
analytics, Cloudflare GraphQL analytics and UptimeRobot, so the dashboard "cannot say
anything the ledgers do not" (same rule as the trading side).

**Loader hook for `scripts/dashboard.py`** (owned by another agent; not edited here):

```python
# in scripts/dashboard.py build(): after the ventures table
import importlib.util
spec = importlib.util.spec_from_file_location("saas_metrics", ROOT / "ventures/saas/metrics.py")
saas = importlib.util.module_from_spec(spec); spec.loader.exec_module(saas)
saas_summary = saas.dashboard_rows(ROOT / "ventures/saas/metrics.json")
# saas_summary["totals"] -> one KPI row; saas_summary["rows"] -> one table row per product
# (keys: id, name, status, channel, mrr_usd, subscribers, churn_pct_30d, cost_usd_30d,
#  uptime_pct_30d, support_tickets_30d, net_30d_usd, verdict, verdict_reasons)
```

`python ventures/saas/metrics.py` prints the same table; `--json` dumps the dict. Tests:
`python -m pytest ventures/saas` (not yet in `pyproject` `testpaths`; the main-session owner
can add `"ventures/saas"` there — one line, no other change needed).

## (g) One-time human steps (owner, from the phone)

1. **Stripe** (≈15 min): stripe.com → Start now → "Individual / Sole proprietor" → legal
   name, SSN, DOB, home address (not a PO box), bank account for payouts → "Activate".
   Then Developers → API keys → create a **restricted** key with `Payment Links: write`,
   `Products: write`, `Prices: write`, `Customers: read`, `Subscriptions: read`,
   `Webhook Endpoints: write` → paste into GitHub repo secrets as `STRIPE_RESTRICTED_KEY`.
   Agents create products, prices and links from CI; you never touch the dashboard again
   except to approve a payout schedule change.
2. **Cloudflare** (≈5 min): dash.cloudflare.com → sign up (free, no card) → My Profile →
   API Tokens → Create Token → template "Edit Cloudflare Workers" → copy → GitHub secret
   `CLOUDFLARE_API_TOKEN`; also copy the Account ID from the Workers overview page into
   `CLOUDFLARE_ACCOUNT_ID`. First deploy gives `oddsmath.<you>.workers.dev`.
3. **RapidAPI provider** (≈10 min): rapidapi.com → Sign up with GitHub → Provider dashboard
   → "Add API" once by hand (name, category "Sports", upload `oddsmath/openapi.yaml`, base
   URL = the workers.dev URL, pricing: Basic free 100/day, Pro $9/mo 20k, Ultra $29/mo
   200k) → Settings → copy the **Proxy Secret** → GitHub secret `RAPIDAPI_PROXY_SECRET`
   (agents push it to the Worker with `wrangler secret put PROXY_SECRET`). Billing →
   add your PayPal email (without it RapidAPI never pays). Later updates use the
   provisioning API with a RapidAPI key stored as `RAPIDAPI_KEY`.
4. **PyPI + npm + MCP registry** (≈10 min): create a PyPI account and an API token
   (`PYPI_TOKEN`), create an npm account (only if a JS MCP wrapper is wanted). The registry
   itself logs in with GitHub device flow; from CI use the GitHub-Actions auth documented at
   the [registry quickstart](https://modelcontextprotocol.io/registry/quickstart).
5. **Support inbox** (≈5 min): create `support@` on the existing domain or a free Proton
   alias; forward to a GitHub issue via the repo's email-to-issue action (or just let the
   auto-reply point to GitHub Issues). Put the address in every listing and the privacy
   policy.
6. **Uptime monitor** (≈3 min): uptimerobot.com free tier, HTTPS monitor on
   `/v1/health` every 5 min; copy the read-only API key to `UPTIMEROBOT_KEY` for the
   metrics puller.
7. **Optional, later:** Apify account (`APIFY_TOKEN`) if any candidate is published as an
   Actor; Lemon Squeezy / Stripe Managed Payments when MRR > $500 (sales-tax liability).

Everything else — building, tests, deploys, listings, price changes, key issuance, refunds,
sunsets, metrics — is agent work from GitHub Actions with those secrets.

## Next actions (agents)

1. Owner completes §g 1–3 and 6. Until then `oddsmath` stays `building` with MRR 0.
2. Add a `.github/workflows/saas_deploy.yml` (other agent / main session: workflow files are
   outside `ventures/saas/`) running `pytest ventures/saas` then `npx wrangler deploy` from
   `ventures/saas/oddsmath/` on push to main.
3. Publish `oddsmath` to PyPI (`pip install oddsmath` → `python -m oddsmath.mcp_server`) and
   the MCP registry as `io.github.watkast/oddsmath`.
4. Build #2 `pm_odds_feed` only after `oddsmath` has 30 days of uptime and ≥ 1 paying
   subscriber or ≥ 1,000 free requests/day — otherwise build #3 `bizdays` (demand without
   dependence on our own data) and re-rank.
