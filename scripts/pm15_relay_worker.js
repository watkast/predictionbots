// PM15 Copilot relay — a Cloudflare Worker (free tier) that forwards two read-only Polymarket US
// gateway endpoints and adds the CORS header a browser page needs.
//
//   GET /v1/market/slug/{slug}      -> market terms (priceToBeat, settlementPrice, feeCoefficient)
//   GET /v1/markets/{slug}/book     -> live order book (Up-side bids/offers)
//
// Deploy: dash.cloudflare.com -> Workers & Pages -> Create -> paste this file -> Deploy.
// Then put the worker URL (https://<name>.<account>.workers.dev) in the page's Settings -> "PM API relay URL".
// Nothing here places orders; there is no key. Only the two paths above are forwarded.

const UPSTREAM = 'https://gateway.polymarket.us';
const ALLOWED = [/^\/v1\/market\/slug\/[a-z0-9-]+$/, /^\/v1\/markets\/[a-z0-9-]+\/book$/];

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
    const upstream = await fetch(UPSTREAM + url.pathname, {
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
