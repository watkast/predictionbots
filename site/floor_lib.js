// Shared helpers for the Floor: auth (Clerk JWT in production, a dev header locally), D1 access, rendering, rules.
// Bindings: FLOOR (D1). Env: CLERK_JWKS_URL (e.g. https://<your-clerk-domain>/.well-known/jwks.json),
// CLERK_ISSUER (https://<your-clerk-domain>), DEV_AUTH ("1" allows the x-dev-user header; never set in production).

export const json = (obj, status = 200, extra = {}) =>
  new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store", ...extra } });

export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const KINDS = new Set(["benchmark", "post", "learn", "market", "rule"]);
export function validKey(kind, key) {
  return KINDS.has(kind) && /^[a-z0-9][a-z0-9/_.-]{0,120}$/i.test(key || "");
}

// --- house rules enforced on every post ---------------------------------------------------------------------
const REFERRAL = /(kalshi\.com\/[^ ]*(ref|promo|code)=|polymarket\.us\/[^ ]*(ref|promo|code)=|\b(referral|promo)\s*code\b|\bsign\s*up\s*with\s*(my|code)\b)/i;
export function checkBody(body) {
  const b = String(body || "").trim();
  if (b.length < 1) return "Write something first.";
  if (b.length > 2000) return "Keep it under 2,000 characters.";
  if (REFERRAL.test(b)) return "No referral or promo codes on the Floor.";
  if ((b.match(/https?:\/\//g) || []).length > 5) return "Five links at most.";
  return null;
}

// --- auth ------------------------------------------------------------------------------------------------------
function b64url(s) { return Uint8Array.from(atob(s.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(s.length / 4) * 4, "=")), (c) => c.charCodeAt(0)); }
const jwksCache = { at: 0, keys: null };
async function jwks(env) {
  if (jwksCache.keys && Date.now() - jwksCache.at < 3600_000) return jwksCache.keys;
  const r = await fetch(env.CLERK_JWKS_URL, { cf: { cacheTtl: 3600 } });
  if (!r.ok) throw new Error("jwks");
  const j = await r.json();
  jwksCache.keys = j.keys || []; jwksCache.at = Date.now();
  return jwksCache.keys;
}
export async function userFromRequest(request, env) {
  if (env.DEV_AUTH === "1") {
    const dev = request.headers.get("x-dev-user");
    if (dev && /^[a-z0-9_-]{2,32}$/i.test(dev)) return { id: "dev:" + dev.toLowerCase(), handle: dev };
  }
  const auth = request.headers.get("Authorization") || "";
  const token = auth.startsWith("Bearer ") ? auth.slice(7) : null;
  if (!token || !env.CLERK_JWKS_URL) return null;
  const [h, p, s] = token.split(".");
  if (!h || !p || !s) return null;
  let header, payload;
  try { header = JSON.parse(new TextDecoder().decode(b64url(h))); payload = JSON.parse(new TextDecoder().decode(b64url(p))); } catch { return null; }
  if (header.alg !== "RS256") return null;
  const now = Math.floor(Date.now() / 1000);
  if (!payload.exp || payload.exp < now - 30 || (payload.nbf && payload.nbf > now + 30)) return null;
  if (env.CLERK_ISSUER && payload.iss !== env.CLERK_ISSUER) return null;
  const keys = await jwks(env);
  const jwk = keys.find((k) => k.kid === header.kid) || keys[0];
  if (!jwk) return null;
  const key = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
  const ok = await crypto.subtle.verify("RSASSA-PKCS1-v1_5", key, b64url(s), new TextEncoder().encode(`${h}.${p}`));
  if (!ok) return null;
  const handle = (payload.username || payload.handle || (payload.email ? payload.email.split("@")[0] : null) || ("user_" + payload.sub.slice(-6))).replace(/[^a-z0-9_.-]/gi, "").slice(0, 32) || "user";
  return { id: payload.sub, handle };
}
export async function ensureUser(db, u) {
  const row = await db.prepare("SELECT id, handle, badge, banned FROM users WHERE id = ?").bind(u.id).first();
  if (row) return row;
  // keep handles unique: suffix on collision
  let handle = u.handle, n = 0;
  while (await db.prepare("SELECT 1 FROM users WHERE handle = ?").bind(handle).first()) handle = `${u.handle}${++n}`;
  await db.prepare("INSERT INTO users (id, handle) VALUES (?, ?)").bind(u.id, handle).run();
  return { id: u.id, handle, badge: null, banned: 0 };
}

// --- data ------------------------------------------------------------------------------------------------------
export async function getThread(db, kind, key, title) {
  let t = await db.prepare("SELECT id, kind, key, title, created FROM threads WHERE kind = ? AND key = ?").bind(kind, key).first();
  if (!t && title) {
    await db.prepare("INSERT OR IGNORE INTO threads (kind, key, title) VALUES (?, ?, ?)").bind(kind, key, title.slice(0, 200)).run();
    t = await db.prepare("SELECT id, kind, key, title, created FROM threads WHERE kind = ? AND key = ?").bind(kind, key).first();
  }
  return t;
}
export async function loadPosts(db, threadId) {
  const { results } = await db.prepare(
    `SELECT p.id, p.side, p.body, p.data_url, p.created, u.handle, u.badge,
            (SELECT COUNT(*) FROM votes v WHERE v.post_id = p.id) AS votes,
            (SELECT COUNT(*) FROM reports r WHERE r.post_id = p.id) AS reports
       FROM posts p JOIN users u ON u.id = p.user_id
      WHERE p.thread_id = ? AND p.hidden = 0 AND u.banned = 0
      ORDER BY (votes * (CASE WHEN p.data_url IS NOT NULL AND p.data_url <> '' THEN 2 ELSE 1 END)) DESC, p.created DESC
      LIMIT 200`).bind(threadId).all();
  return (results || []).filter((p) => p.reports < 3);
}
export function tally(posts) {
  const w = (p) => (p.data_url ? 2 : 1) + Number(p.votes || 0);
  return { defend: posts.filter((p) => p.side === "defend").reduce((s, p) => s + w(p), 0), deviate: posts.filter((p) => p.side === "deviate").reduce((s, p) => s + w(p), 0) };
}

// --- rendering (server-side, for crawlers and no-JS) ----------------------------------------------------------
export function renderThreadHTML(thread, posts, base) {
  const t = tally(posts), total = t.defend + t.deviate || 1;
  const col = (side, label, note, color) => `<section class="floor-col"><h2 style="color:${color}">${label} <span class="q-where">${esc(note)}</span></h2>` +
    (posts.filter((p) => p.side === side).map((p) => `<article class="floor-post" style="border-left-color:${color}"><div class="q-where"><b>${esc(p.handle)}</b>${p.badge ? ` <span class="badge">${esc(p.badge)}</span>` : ""} · ${esc(p.created.slice(0, 10))} · ▲ ${p.votes}</div><p>${esc(p.body).replace(/\n/g, "<br>")}</p>${p.data_url ? `<div class="q-where">Data: <a href="${esc(p.data_url)}" rel="noopener nofollow">${esc(p.data_url)}</a> (counts double)</div>` : ""}</article>`).join("") || `<p class="q-where">No posts yet.</p>`) + `</section>`;
  const title = `${thread.title} — The Floor`;
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><script>try{var t=localStorage.getItem("pb-theme");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}catch(e){}</script><meta name="viewport" content="width=device-width, initial-scale=1"><title>${esc(title)}</title><meta name="description" content="${esc("Defend or deviate: " + thread.title + ". " + posts.length + " posts.")}"><link rel="stylesheet" href="/styles.css"><link rel="canonical" href="${esc(base)}/floor/${esc(thread.kind)}/${esc(thread.key)}">
<style>.floor{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}.floor-col h2{font-size:20px}.floor-post{background:var(--paper-2);border:1px solid var(--rule);border-left:3px solid;border-radius:8px;padding:12px 14px;margin:0 0 12px}.floor-post p{margin:6px 0}.badge{background:var(--rule);border-radius:4px;padding:1px 6px;font-size:12px}.bar{display:flex;height:10px;border-radius:5px;overflow:hidden;background:var(--rule)}.bar i{display:block}</style></head>
<body><a class="skip" href="#main">Skip to content</a><div class="wrap"><header class="top"><a class="brand" href="/">PredictionBots</a><nav><a href="/#truecost">True Cost</a><a href="/simulate.html">Simulator</a><a href="/#benchmark">Bot benchmark</a><a href="/markets/">Markets</a><a href="/#honest">How we're paid</a></nav></header>
<main id="main"><div class="hero" style="padding-bottom:12px"><p class="q-where">The Floor › ${esc(thread.kind)}</p><h1 style="max-width:30ch;font-size:clamp(28px,4vw,40px)">${esc(thread.title)}</h1>
<div style="display:flex;align-items:center;gap:14px"><b style="color:var(--win)">Defend ${t.defend}</b><div class="bar" style="flex:1" aria-hidden="true"><i style="width:${Math.round(t.defend / total * 100)}%;background:var(--win)"></i><i style="width:${Math.round(t.deviate / total * 100)}%;background:var(--loss)"></i></div><b style="color:var(--loss)">Deviate ${t.deviate}</b></div>
<p class="fine">Defenders argue the claim holds; deviants argue it doesn't. Posts with a data file count double. Read without an account; post with one tap on the page this thread belongs to. House rules: patterns and public records, never a private person's name without a court or exchange filing; vendors wear a badge; no referral links.</p></div>
<div class="floor">${col("defend", "Defend", "it holds, or close", "var(--win)")}${col("deviate", "Deviate", "it doesn't, and here's why", "var(--loss)")}</div></main>
<footer><p>Posts are written by their authors and are public. Report abuse with the button on the page; three reports hide a post pending review. Nothing here is investment advice.</p></footer></div><script src="/theme.js" defer></script></body></html>`;
}
