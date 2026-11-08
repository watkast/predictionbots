# Launch day, in order

Everything below is ready on `main`. The site deploys itself the moment the two Cloudflare secrets exist.

## Noah (about 40 minutes, any order within each block)
1. **Domain:** PredictMeNot.com (your pick; fallbacks PredictNothing, LuckTax, PriceOfLuck). Grab the .io/.org as
   redirects if cheap. Tell Claude the final name → one-pass rename (`scripts/rename_brand.py`).
2. **Cloudflare:** custom API token (Pages: Edit, D1: Edit, Workers KV Storage: Edit, Account Settings: Read) +
   Account ID → GitHub repo secrets `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. The next run creates the Pages
   project, the waitlist store and the Floor database, and publishes the site. Then add the custom domain in the Pages
   project (ops/CLOUDFLARE.md).
3. **Handles:** X @predictmenot (or the chosen name); Substack. Create a **Clerk** app (free) with Google, Apple and
   email link enabled; paste the publishable key, frontend API host and JWKS URL to Claude → the Floor opens for posting.
4. **Google Search Console:** add the property, submit `/sitemap.xml` (about 13,200 URLs).

## Claude (same day, automatic or on your word)
- Rename pass; final proofread of every page on the live domain; `node site/a11y_check.js` against the live site.
- Partner applications (marketing/partners.md) sent from the live domain's email once it exists.
- Benchmark and market pages keep regenerating (hourly / daily).

## Posting order (Noah posts, Claude drafted; one a day keeps each one alive)
1. Day 1: **Post 3** thread (the 45/70 rule on 689 markets) — `marketing/thread-04-the-45-70-rule.md`. Strongest hook.
2. Day 2: **Fee increase** thread — `marketing/thread-03-polymarket-fee-increase.md`. News hook; tag no one.
3. Day 3: **Post 2** thread (free money that wasn't) — `marketing/thread-02-free-money.md`.
4. Day 4: **Post 1** thread (the pump candle) — `marketing/thread-01-pump-candle.md`.
5. Reddit: r/algotrading gets the data-first version of post 3 the same day as the X thread; r/Polymarket and r/Kalshi
   get the fee post (read each subreddit's self-promotion rule first; answer every comment with numbers).
6. The simulator link goes in every reply where someone says "but I'm up this week."

## Rules for the first week
- No referral links anywhere until a partner program approves us; the deal cards say so.
- No venue tagged, no vendor tagged, no quote-tweeting critics. Numbers only; let people argue on the Floor.
- Every claim links to the data. If someone finds an error, fix it publicly the same day and thank them by handle.
