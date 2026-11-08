# Cloudflare: what has to exist once (Noah), and what runs itself (Actions)

## Noah, once
1. **Domain:** register predictionbots.io on Cloudflare Registrar (fallback .dev or .app). It lands in your Cloudflare
   account with DNS already here.
2. **API token:** Cloudflare dashboard → My Profile → API Tokens → Create Token → Custom token with these account
   permissions: **Cloudflare Pages · Edit**, **D1 · Edit**, **Workers KV Storage · Edit**, **Account Settings · Read**;
   resources: your account. Copy the token once.
3. **Account ID:** dashboard → any zone or Workers & Pages → right sidebar → Account ID.
4. **GitHub secrets:** repo → Settings → Secrets and variables → Actions → New repository secret:
   `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`.
5. After the first deploy (it creates the Pages project `predictionbots`): Workers & Pages → predictionbots →
   **Custom domains** → add `predictionbots.io` and `www.predictionbots.io` (Cloudflare writes the DNS records).
6. **Stores:** nothing to click. The deploy script creates the KV namespace `WAITLIST` and the D1 database `floor`
   (the Floor), binds both, and applies the schema. Optional: in predictionbots → Settings → Variables add `ADMIN_KEY`
   (a long random string; lets `GET /api/waitlist?key=…` list signups) and, when the Clerk app exists,
   `CLERK_JWKS_URL` and `CLERK_ISSUER` for one-tap sign-in on the Floor.

## What then runs itself
- `site-deploy.yml`: on every push to `site/**` and hourly: reference rates, posts, Learn pages, the ledger page,
  13k market pages, sitemap → `wrangler pages deploy site/dist --project-name=predictionbots`.
- `benchmark.yml`: daily replay of vendor rules against the recorder; results published to `mrp-data/benchmark`, read
  by the home page.
- `mrp-record.yml`: the recorder backstop on Actions; the Dell takes over the primary role when linked (ops/dell).

## Checks after the first deploy
- `https://predictionbots.pages.dev/` renders; `/markets/` lists both venues; `/simulate.html` plays; `/sitemap.xml` has ~13k URLs.
- `curl -X POST https://predictionbots.pages.dev/api/waitlist -d '{"email":"test@example.com"}' -H 'content-type: application/json'` → `{"message": …}` once KV is bound.
- Google Search Console: add the property, submit `/sitemap.xml`.
