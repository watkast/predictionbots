// PM15 Copilot worker — a Cloudflare Worker (free tier) that does two things:
//
//  1. SERVES THE COCKPIT.  GET /  (or /app)  -> research/pm15_copilot.html from the repo's main branch on GitHub,
//     wrapped with the mobile viewport / home-screen metas, cached at the edge for 60 s. That URL is where the cockpit
//     is opened on a phone: Safari -> Share -> Add to Home Screen. The claude.ai artifact copy cannot reach Coinbase
//     or this relay (the artifact origin blocks outbound connections), so it only shows the layout.
//     ?ref=<branch-or-sha> serves another revision (testing); ?fresh=1 bypasses the edge cache.
//
//  2. RELAYS three read-only Polymarket US gateway endpoints with the CORS header a browser page needs:
//     GET /v1/market/slug/{slug}                 -> market terms (priceToBeat, settlementPrice, feeCoefficient)
//     GET /v1/markets/{slug}/book                -> live order book (Up-side bids/offers)
//     GET /v1/asset-prices/history?assets=crypto:btc&from=<unix s>&to=0&bucket=ASSET_PRICE_BUCKET_1S
//                                                -> the exchange's own 1-second index series: PM's 60-print trailing
//                                                   average, whose value at T-1 is the settlement price (verified on
//                                                   recorded settlements to $0.005). The page uses it for the exact PM
//                                                   line, the exact final price / next target and the live basis.
//
// Deploy: dash.cloudflare.com -> Workers & Pages -> the worker -> Edit code -> paste this file -> Deploy.
// Nothing here places orders; there is no key. Only the paths above are answered, with only the four query parameters
// the history endpoint needs. Budget: the page polls ~0.5–1 request/s in the last three minutes of a round and ~0.2/s
// otherwise — roughly 30–40k requests per day if it runs around the clock (free tier: 100k/day).

const UPSTREAM = 'https://gateway.polymarket.us';
const PAGE_REPO = 'watkast/predictionbots';
const PAGE_PATH = 'research/pm15_copilot.html';
const ALLOWED = [/^\/v1\/market\/slug\/[a-z0-9-]+$/, /^\/v1\/markets\/[a-z0-9-]+\/book$/, /^\/v1\/asset-prices\/history$/];
const HISTORY_PARAMS = { assets: /^crypto:[a-z]{2,10}$/, from: /^\d{1,12}$/, to: /^\d{1,12}$/, bucket: /^ASSET_PRICE_BUCKET_(1S|1M|5M|15M|1H)$/ };
const HEAD = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
  + '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'
  + '<meta name="apple-mobile-web-app-title" content="PM15"><meta name="theme-color" content="#0a0d14"><meta name="robots" content="noindex">'
  + '<style>html{background:#0a0d14}</style></head><body>';

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
    if (request.method !== 'GET') return new Response('not found', { status: 404, headers: cors });

    // ---- 1. the cockpit page
    if (url.pathname === '/' || url.pathname === '/app' || url.pathname === '/index.html') {
      const ref = /^[A-Za-z0-9._\/-]{1,80}$/.test(url.searchParams.get('ref') || '') ? url.searchParams.get('ref') : 'main';
      const src = `https://raw.githubusercontent.com/${PAGE_REPO}/${ref}/${PAGE_PATH}`;
      const fresh = url.searchParams.has('fresh');
      const r = await fetch(src, { cf: fresh ? { cacheTtl: 0 } : { cacheTtl: 60, cacheEverything: true }, headers: { 'User-Agent': 'pm15-copilot worker' } });
      if (!r.ok) return new Response(`cockpit source unavailable (${r.status} from GitHub for ${ref})`, { status: 502, headers: { 'Content-Type': 'text/plain' } });
      const body = await r.text();
      const page = /^\s*<!doctype/i.test(body) ? body : HEAD + body + '</body></html>';
      return new Response(page, { status: 200, headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'X-PM15-Source': `${ref}/${PAGE_PATH}` } });
    }
    if (url.pathname === '/health') return new Response(JSON.stringify({ ok: true, routes: ['/', '/v1/market/slug/{slug}', '/v1/markets/{slug}/book', '/v1/asset-prices/history'] }), { headers: { ...cors, 'Content-Type': 'application/json' } });

    // ---- 2. the relay
    if (!ALLOWED.some(re => re.test(url.pathname))) return new Response('not found', { status: 404, headers: cors });
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
