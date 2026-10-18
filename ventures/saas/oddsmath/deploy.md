# Deploying oddsmath to Cloudflare Workers (free plan)

Host choice and limits: Workers Free = 100,000 requests/day, 10 ms CPU per request, no
charge beyond that (requests error instead of billing); Python Workers are GA (2026-09-21)
with a 64 MiB uncompressed bundle limit on free and paid plans; the Paid plan is $5/mo
minimum. Sources: https://developers.cloudflare.com/workers/platform/pricing/ ,
https://byteiota.com/cloudflare-python-workers-ga/ (third-party write-up; the official
Python Workers page could not be fetched from this sandbox — re-read
https://developers.cloudflare.com/workers/languages/python/ before the first deploy and
adjust `worker.py` if the entrypoint signature differs).

The API has no dependencies, so the bundle is ~30 KB.

## 0. One-time (owner, see ../PLAN.md §g)

* Cloudflare account (no card) → API token from template "Edit Cloudflare Workers" →
  GitHub secret `CLOUDFLARE_API_TOKEN`; Account ID → `CLOUDFLARE_ACCOUNT_ID`.
* Node 18+ wherever wrangler runs (GitHub Actions `ubuntu-latest` has it).

## 1. Local check (any machine with Python 3.11+, no network)

```bash
cd ventures/saas
python -m pytest -q                      # 24 oddsmath tests + metrics tests
cd oddsmath && python -m oddsmath.server # http://127.0.0.1:8787/v1/health
```

## 2. Deploy from a laptop or CI (needs internet)

```bash
cd ventures/saas/oddsmath
npx wrangler@latest whoami                       # uses CLOUDFLARE_API_TOKEN / CLOUDFLARE_ACCOUNT_ID env
npx wrangler@latest deploy                       # reads wrangler.toml -> https://oddsmath.<account>.workers.dev
curl -s https://oddsmath.<account>.workers.dev/v1/health
curl -s https://oddsmath.<account>.workers.dev/v1/devig -d '{"odds":[-110,-110]}'
```

`wrangler dev` runs the Worker locally in workerd (also exercises `worker.py`, which the
pytest suite does not).

## 3. Secrets (only when a paid channel exists)

```bash
npx wrangler secret put PROXY_SECRET   # paste RapidAPI "Proxy Secret" (provider dashboard -> Settings)
npx wrangler secret put API_KEYS       # comma-separated keys for Stripe customers; rotate by re-putting
```

With neither secret the API is open (free tier). `GET /v1/health` and `/openapi.yaml`
are always open.

## 4. Free-tier rate limit (dashboard, once)

Workers & Pages → oddsmath → Settings → Triggers/Rate limiting (or Security → WAF rate
limiting on a custom domain): 100 requests / day / IP on path `/v1/*` unless header
`X-RapidAPI-Proxy-Secret` or `X-API-Key` is present. Until that rule exists the only cap is
the plan's 100k/day.

## 5. GitHub Actions (proposed; workflow files live outside `ventures/saas/`)

```yaml
name: saas-deploy
on: { push: { branches: [main], paths: ["ventures/saas/oddsmath/**"] } }
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install pytest pyyaml && python -m pytest -q ventures/saas
      - uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          workingDirectory: ventures/saas/oddsmath
          command: deploy
      - run: curl -fsS https://oddsmath.${{ vars.CF_SUBDOMAIN }}.workers.dev/v1/health
```

## 6. Listing (agent, after the owner's §g steps)

* **RapidAPI**: provider dashboard → Add API → upload `openapi.yaml`, base URL = the
  workers.dev URL; plans Basic free 100/day, Pro $9/mo 20k, Ultra $29/mo 200k; copy the
  Proxy Secret into step 3. Updates via the OpenAPI provisioning API
  (https://docs.rapidapi.com/docs/automating-api-provisioning).
* **Stripe**: `POST /v1/products` + `POST /v1/prices` (recurring, usd 900 / 2900) +
  `POST /v1/payment_links` (https://docs.stripe.com/payments/payment-links/api); put the
  links in this README and the landing page.
* **MCP registry**: `pip`-publish the `oddsmath` package, add `mcpName:
  io.github.watkast/oddsmath` metadata, `mcp-publisher login github && mcp-publisher
  publish` (https://modelcontextprotocol.io/registry/quickstart).

## 7. Sunset (one commit)

Archive the Stripe prices, delete the RapidAPI listing, `npx wrangler delete`, set
`status: sunset` in `../portfolio.yaml` and `../metrics.json`.

## Fallback host

If Python Workers misbehave: Fly.io shared-cpu-1x/256 MB ≈ $2.19/mo
(https://temps.sh/blog/fly-io-pricing-2026, third-party) running
`python -m oddsmath.server --host 0.0.0.0 --port 8080` behind Fly's TLS. Vercel Hobby and
GitHub Pages are not options (commercial use prohibited; see ../PLAN.md §d).
