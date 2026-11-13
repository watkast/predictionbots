// PredictMeNot paid data API — x402 per-call endpoints on Cloudflare Workers (Hono).
//
//   GET /                                 what this is, prices, how to pay (free)
//   GET /v1/preview                        last 3 final-second moments, 10+ minutes delayed (free)
//   GET /v1/final-seconds/recent           the last 200 qualifying moments with every gate reading (paid)
//   GET /v1/final-seconds/stats            per coin / horizon / hour: how often the decided side is still cheap (paid)
//   GET /v1/final-seconds/live             candidates seen in the last 15 s by the always-on sniper (paid, needs ingest)
//   POST /ingest                           the sniper pushes gate readings here (header x-ingest-key)
//
// Payment: x402 v2, "exact" scheme, USDC on Base. A client without a payment header gets 402 + the terms; a client
// library (@x402/fetch, Coinbase's agent tools) pays and retries. We never see a key or a wallet; the facilitator
// verifies and settles. Data: the bots' logs on GitHub (mrp-data branch, mrt/), pulled every 5 min by the cron.
import { Hono } from "hono";
import { cors } from "hono/cors";
import { paymentMiddleware, x402ResourceServer } from "@x402/hono";
import { ExactEvmScheme } from "@x402/evm/exact/server";
import { HTTPFacilitatorClient } from "@x402/core/server";
import { bazaarResourceServerExtension, declareDiscoveryExtension } from "@x402/extensions/bazaar";

const app = new Hono();
app.use("*", cors({ origin: "*" }));

let server = null;
function resourceServer(env) {
  if (server) return server;
  const facilitator = new HTTPFacilitatorClient({ url: env.FACILITATOR_URL || "https://x402.org/facilitator" });
  server = new x402ResourceServer(facilitator).register(env.NETWORK || "eip155:8453", new ExactEvmScheme());
  try { server.registerExtension(bazaarResourceServerExtension); } catch (e) { /* discovery is optional */ }
  return server;
}

function discovery(example) {
  try { return declareDiscoveryExtension({ input: {}, output: { example } }); } catch (e) { return undefined; }
}

const EXAMPLE_MOMENT = { t: "2026-11-07T23:59:57.1Z", market: "cpc-btc-updown-5m-2026-11-08-0000z", coin: "btc", horizon_min: 5, seconds_left: 2.9,
  prints_in: 57, leader: "UP", margin_bps: 12.3, leader_ask: 0.85, offered: 40 };

function routes(env) {
  const pay = (price) => [{ scheme: "exact", price, network: env.NETWORK || "eip155:8453", payTo: env.PAY_TO }];
  return {
    "GET /v1/final-seconds/recent": { accepts: pay(env.PRICE_RECENT || "$0.002"),
      description: "Polymarket US crypto Up/Down markets: the last 200 final-second moments where the already-decided side was still offered below $1 (gate readings from PredictMeNot's sniper).",
      mimeType: "application/json", extensions: discovery({ count: 1, moments: [EXAMPLE_MOMENT] }) },
    "GET /v1/final-seconds/stats": { accepts: pay(env.PRICE_STATS || "$0.002"),
      description: "How often the decided side of Polymarket US crypto markets is still cheap in the final seconds, by coin, horizon and UTC hour, with median ask and size.",
      mimeType: "application/json", extensions: discovery({ window_days: 4, by_coin: { btc: { moments: 56, median_ask: 0.78 } } }) },
    "GET /v1/final-seconds/live": { accepts: pay(env.PRICE_LIVE || "$0.01"),
      description: "Final-second candidates seen in the last 15 seconds by PredictMeNot's always-on sniper (Polymarket US BTC/ETH/SOL/XRP 5m and 15m).",
      mimeType: "application/json", extensions: discovery({ as_of: "2026-11-08T00:04:57Z", candidates: [EXAMPLE_MOMENT] }) },
  };
}

// ---- payment middleware (built once per isolate, after env is known)
let paywall = null;
app.use("/v1/final-seconds/*", async (c, next) => {
  if (!c.env.PAY_TO || c.env.PAY_TO.startsWith("0xREPLACE")) return c.json({ error: "PAY_TO is not configured on this deployment." }, 503);
  if (!paywall) paywall = paymentMiddleware(routes(c.env), resourceServer(c.env));
  return paywall(c, next);
});

// ---- data helpers
async function kv(env, key, fallback) { try { const v = await env.DATA.get(key, "json"); return v ?? fallback; } catch (e) { return fallback; } }

app.get("/", (c) => c.json({
  name: "PredictMeNot data API", docs: "https://predictmenot.com/#data", protocol: "x402 v2 (exact, USDC on Base)",
  endpoints: {
    "GET /v1/preview": "free — last 3 final-second moments, delayed",
    "GET /v1/final-seconds/recent": `${c.env.PRICE_RECENT || "$0.002"} per call`,
    "GET /v1/final-seconds/stats": `${c.env.PRICE_STATS || "$0.002"} per call`,
    "GET /v1/final-seconds/live": `${c.env.PRICE_LIVE || "$0.01"} per call`,
  },
  how_to_pay: "Request a paid route; the 402 response carries the payment terms. Use @x402/fetch or any x402 client to pay and retry.",
  source: "https://github.com/watkast/predictionbots",
}));

app.get("/v1/preview", async (c) => {
  const recent = await kv(c.env, "recent", { moments: [], updated: null });
  const cutoff = Date.now() - 10 * 60 * 1000;
  const old = recent.moments.filter((m) => Date.parse(m.t) < cutoff).slice(-3);
  return c.json({ updated: recent.updated, delayed_minutes: 10, moments: old, paid: "/v1/final-seconds/recent for the last 200, undelayed" });
});

app.get("/v1/final-seconds/recent", async (c) => c.json(await kv(c.env, "recent", { moments: [], updated: null })));
app.get("/v1/final-seconds/stats", async (c) => c.json(await kv(c.env, "stats", { updated: null, note: "no data yet" })));
app.get("/v1/final-seconds/live", async (c) => {
  const live = await kv(c.env, "live", { as_of: null, candidates: [] });
  const fresh = live.as_of && Date.now() - Date.parse(live.as_of) < 15000;
  return c.json({ as_of: live.as_of, fresh, candidates: fresh ? live.candidates : [], note: fresh ? undefined : "no candidate in the last 15 s" });
});

app.post("/ingest", async (c) => {
  if (!c.env.INGEST_KEY || c.req.header("x-ingest-key") !== c.env.INGEST_KEY) return c.json({ error: "forbidden" }, 403);
  const body = await c.req.json().catch(() => null);
  if (!body || !Array.isArray(body.candidates)) return c.json({ error: "send {candidates: [...]}" }, 400);
  await c.env.DATA.put("live", JSON.stringify({ as_of: new Date().toISOString(), candidates: body.candidates.slice(0, 50) }), { expirationTtl: 120 });
  return c.json({ ok: true, n: body.candidates.length });
});

// ---- cron: pull the sniper's gate readings from GitHub, keep the qualifying moments and the stats
function toMoment(e) {
  const slug = e.slug || "";
  const coin = (slug.split("-updown-")[0] || "").replace(/^cpc/, "").replace(/^-/, "") || "btc";
  const hz = /-15m-/.test(slug) ? 15 : /-5m-/.test(slug) ? 5 : /-1h-/.test(slug) ? 60 : null;
  return { t: e.t, market: slug, coin, horizon_min: hz, seconds_left: e.rem, prints_in: e.k, leader: e.leader, margin_bps: e.margin_bps, leader_ask: e.ask, offered: e.offered };
}

async function refresh(env) {
  const r = await fetch(`${env.GITHUB_RAW}/mrp-data/mrt/live.jsonl`, { cf: { cacheTtl: 0 } });
  if (!r.ok) return;
  const lines = (await r.text()).split("\n").filter(Boolean);
  const gates = [];
  for (const l of lines) { try { const e = JSON.parse(l); if (e.ev === "gate" && e.ok) gates.push(toMoment(e)); } catch (err) { /* skip */ } }
  const moments = gates.slice(-200);
  await env.DATA.put("recent", JSON.stringify({ updated: new Date().toISOString(), count: moments.length, moments }));
  const by = (key) => { const m = {}; for (const g of gates) { const k = key(g); if (k == null) continue; (m[k] ||= { moments: 0, asks: [] }); m[k].moments++; if (g.leader_ask != null) m[k].asks.push(g.leader_ask); } 
    for (const k in m) { const a = m[k].asks.sort((x, y) => x - y); m[k].median_ask = a.length ? a[Math.floor(a.length / 2)] : null; delete m[k].asks; } return m; };
  const first = gates[0]?.t, last = gates[gates.length - 1]?.t;
  const days = first && last ? Math.max((Date.parse(last) - Date.parse(first)) / 86400000, 1 / 24) : null;
  await env.DATA.put("stats", JSON.stringify({ updated: new Date().toISOString(), window_start: first, window_end: last, window_days: days && +days.toFixed(2),
    moments: gates.length, per_day: days ? +(gates.length / days).toFixed(1) : null,
    by_coin: by((g) => g.coin), by_horizon: by((g) => g.horizon_min), by_hour_utc: by((g) => new Date(g.t).getUTCHours()),
    gate: { seconds_left_max: 5, min_prints: 52, min_margin_bps: 6, max_ask: 0.9, min_offered: 5 } }));
}

export default {
  fetch: app.fetch,
  scheduled: (event, env, ctx) => ctx.waitUntil(refresh(env)),
};
