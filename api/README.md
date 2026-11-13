# PredictMeNot data API (Cloudflare Worker, x402)

Paid per call in USDC on Base via the x402 protocol — no accounts, no API keys. A client without a payment header gets
`402` with the terms; x402 clients (`@x402/fetch`, Coinbase's agent tools) pay and retry. The facilitator verifies and
settles; the worker never holds keys. Prices: `/v1/final-seconds/recent` and `/stats` $0.002, `/live` $0.01; `/v1/preview` free.

Data comes from the bots' public logs on GitHub (`mrp-data` branch, `mrt/live.jsonl`), pulled every 5 minutes by the
cron, and — for `/live` — from the always-on sniper POSTing to `/ingest`.

## Deploy (from the always-on box)
    cd api && npm install
    npx wrangler login
    npx wrangler kv namespace create DATA        # paste the id into wrangler.toml
    # set PAY_TO in wrangler.toml to the Base address that should receive USDC
    npx wrangler secret put INGEST_KEY            # any long random string; the sniper uses the same
    npx wrangler deploy
    curl https://predictionbots-api.<account>.workers.dev/v1/final-seconds/recent   # -> 402 with payment terms

Test on Base Sepolia first: NETWORK = "eip155:84532", test USDC from Circle's faucet, facilitator unchanged.
Custom domain: route `api.predictmenot.com/*` to the worker in the Cloudflare dashboard.
