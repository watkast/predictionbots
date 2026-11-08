// Cloudflare Pages Function: POST /api/waitlist {email, source} -> stored in the WAITLIST KV namespace (binding "WAITLIST").
// One key per email (lower-cased), value = JSON {email, source, ua, t}. GET /api/waitlist?key=ADMIN_KEY lists them (ADMIN_KEY env).
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const json = (obj, status = 200) => new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });

export async function onRequestPost({ request, env }) {
  let body = {};
  try { body = await request.json(); } catch (e) { return json({ error: "Send JSON with an email." }, 400); }
  const email = String(body.email || "").trim().toLowerCase();
  if (!EMAIL.test(email) || email.length > 200) return json({ error: "That does not look like an email address." }, 400);
  if (!env.WAITLIST) return json({ error: "The waitlist store is not configured yet." }, 503);
  const existing = await env.WAITLIST.get(email);
  if (existing) return json({ message: "You are already on the list." });
  await env.WAITLIST.put(email, JSON.stringify({ email, source: String(body.source || "").slice(0, 120), ua: (request.headers.get("User-Agent") || "").slice(0, 160),
                                               country: request.cf && request.cf.country, t: new Date().toISOString() }));
  return json({ message: "You are on the list. Research posts and new benchmark rows as they publish; nothing else." });
}

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  if (!env.ADMIN_KEY || url.searchParams.get("key") !== env.ADMIN_KEY) return json({ error: "Not found." }, 404);
  const out = [];
  let cursor;
  do {
    const page = await env.WAITLIST.list({ cursor, limit: 1000 });
    for (const k of page.keys) out.push(JSON.parse((await env.WAITLIST.get(k.name)) || "{}"));
    cursor = page.list_complete ? undefined : page.cursor;
  } while (cursor);
  out.sort((a, b) => (a.t < b.t ? 1 : -1));
  return json({ count: out.length, signups: out });
}
