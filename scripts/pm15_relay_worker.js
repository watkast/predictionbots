// PM15 Copilot relay — a Cloudflare Worker (free tier) that forwards three read-only Polymarket US
// gateway endpoints and adds the CORS header a browser page needs.
//
//   GET /v1/market/slug/{slug}                 -> market terms (priceToBeat, settlementPrice, feeCoefficient)
//   GET /v1/markets/{slug}/book                -> live order book (Up-side bids/offers)
//   GET /v1/asset-prices/history?assets=crypto:btc&from=<unix s>&to=0&bucket=ASSET_PRICE_BUCKET_1S
//                                              -> the exchange's own 1-second index series: PM's 60-print trailing
//                                                 average, whose value at T-1 is the settlement price (verified on
//                                                 recorded settlements to $0.005). The page uses it for the exact PM
//                                                 line, the exact final price / next target and the live basis.
//
// Deploy: dash.cloudflare.com -> Workers & Pages -> Create -> paste this file -> Deploy.
// Then put the worker URL (https://<name>.<account>.workers.dev) in the page's Settings -> "PM API relay URL".
// Nothing here places orders; there is no key. Only the three paths above are forwarded, with only the four
// query parameters the history endpoint needs. Budget: the page polls ~0.5–1 request/s in the last three minutes
// of a round and ~0.2/s otherwise — roughly 30–40k requests per day if it runs around the clock (free tier: 100k/day).

const UPSTREAM = 'https://gateway.polymarket.us';
const ALLOWED = [/^\/v1\/market\/slug\/[a-z0-9-]+$/, /^\/v1\/markets\/[a-z0-9-]+\/book$/, /^\/v1\/asset-prices\/history$/];
const HISTORY_PARAMS = { assets: /^crypto:[a-z]{2,10}$/, from: /^\d{1,12}$/, to: /^\d{1,12}$/, bucket: /^ASSET_PRICE_BUCKET_(1S|1M|5M|15M|1H)$/ };

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const cors = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Accept, Content-Type',
      'Access-Control-Max-Age': '86400',
    };
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    if (request.method !== 'GET' || !ALLOWED.some(re => re.test(url.pathname))) {
      return new Response('not found', { status: 404, headers: cors });
    }
    let target = UPSTREAM + url.pathname;
    if (url.pathname === '/v1/asset-prices/history') {
      const q = new URLSearchParams();
      for (const [k, re] of Object.entries(HISTORY_PARAMS)) { const v = url.searchParams.get(k); if (v != null && re.test(v)) q.set(k, v); }
      if (!q.has('assets') || !q.has('from')) return new Response('bad query', { status: 400, headers: cors });
      target += '?' + q.toString();
    }
    const upstream = await fetch(target, {
      headers: { 'Accept': 'application/json', 'User-Agent': 'pm15-copilot relay (read-only)' },
      cf: { cacheTtl: 1, cacheEverything: false },
    });
    const body = await upstream.text();
    return new Response(body, {
      status: upstream.status,
      headers: { ...cors, 'Content-Type': upstream.headers.get('Content-Type') || 'application/json', 'Cache-Control': 'no-store' },
    });
  },
};
