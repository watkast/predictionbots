# oddsmath — betting & prediction-market math API + MCP server

Stateless JSON API (and an MCP stdio server with the same functions) for the arithmetic
every betting / prediction-market tool re-implements:

| endpoint | what |
|---|---|
| `POST /v1/convert` | american / decimal / fractional / probability / Kalshi cents, every way |
| `POST /v1/devig` | fair probabilities from a full set of outcome odds: multiplicative, additive, power, Shin, or `all`; returns hold / overround |
| `POST /v1/ev` | edge, EV, ROI and fractional Kelly for a bet or a YES/NO contract, net of venue fees |
| `POST /v1/fees` | Kalshi (taker 0.07·C·p(1−p) rounded up to the cent, maker 0.0175 on flagged series), Polymarket (per-category taker rate, maker 0), Novig (0.06 live-only taker, pregame free) |
| `POST /v1/arb` | best quote per outcome across books, arb margin and the stake split |
| `POST /v1/complete-set` | YES + NO complete-set check net of taker fees on a venue |
| `POST /v1/parlay` | fair parlay odds and EV vs an offered price |
| `GET /v1/health`, `GET /openapi.yaml` | liveness, spec |

`/v1/convert`, `/v1/ev`, `/v1/fees` also accept `GET` with query-string fields
(`?odds=-110,150&fmt=american`). Pure stdlib Python 3.11+, no dependencies, no network, no
storage, no PII. Outputs are mathematical estimates, not betting advice; the service places
no bets and holds no funds.

Fee formulas are the ones verified in this repo on 2026-10-17 (`pb/core/fees.py`,
`pb/venues/novig.py`); venues change fees, so the response carries a `note` and the version.

## Run locally

```bash
cd ventures/saas/oddsmath
python -m oddsmath.server --port 8787
curl -s localhost:8787/v1/devig -d '{"odds":[-110,-110],"fmt":"american","method":"all"}'
curl -s 'localhost:8787/v1/fees?venue=kalshi&price=0.55&contracts=100'
curl -s localhost:8787/v1/ev -d '{"fair_prob":0.60,"offered":55,"fmt":"cents","stake":55,"venue":"kalshi","bankroll":1000}'
```

Tests (offline, < 1 s): `python -m pytest ventures/saas` from the repo root.

## MCP server

```bash
python -m oddsmath.mcp_server            # stdio, newline-delimited JSON-RPC
```

Claude Desktop / Cursor / any MCP client:

```json
{"mcpServers": {"oddsmath": {"command": "python", "args": ["-m", "oddsmath.mcp_server"],
                             "cwd": "<repo>/ventures/saas/oddsmath"}}}
```

Tools: `convert_odds`, `devig`, `expected_value`, `venue_fees`, `arbitrage`, `complete_set`,
`parlay` — same JSON in/out as the HTTP endpoints.

## Auth and billing (how the one Worker serves three channels)

* **Open / free tier**: with no secrets set the API is open; Cloudflare's rate limiting rule
  (100 req/day per IP, set in the dashboard or `wrangler.toml` once Rate Limiting is
  configured) is the free tier.
* **RapidAPI**: the RapidAPI proxy adds `X-RapidAPI-Proxy-Secret`; set the same value with
  `wrangler secret put PROXY_SECRET` and only proxied (billed) calls pass. RapidAPI meters
  and bills; we get 75 % via PayPal ~2 months later.
* **Stripe payment link**: a `checkout.session.completed` webhook (GitHub Action) generates a
  key, appends it to the `API_KEYS` secret and emails it with the receipt; customers send
  `X-API-Key`. Stripe Billing handles renewals, cancellations and the customer portal.

Pricing in `../portfolio.yaml`: free 100 req/day · Basic $9/mo 20k · Pro $29/mo 200k.

## Layout

```
oddsmath/
  core.py        pure math (conversions, devig, fees, EV/Kelly, arb, complete set, parlay)
  app.py         handle(method, path, body, headers, env) -> (status, dict); WSGI adapter; auth gate
  server.py      stdlib dev server
  worker.py      Cloudflare Python Workers entrypoint (not exercised by tests)
  mcp_server.py  MCP stdio server over the same handlers
openapi.yaml     spec (tests assert it matches the routes)
wrangler.toml    Workers config (secrets via `wrangler secret put`)
deploy.md        exact deploy steps
tests/           24 tests, no network
```
