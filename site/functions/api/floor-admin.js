// Floor moderation, protected by ADMIN_KEY (the same env var as the waitlist listing).
//   GET  /api/floor-admin?key=…                       -> reported posts (any report), newest first, with counts
//   POST /api/floor-admin?key=…  {action, post_id | user_id, badge?}
//        action: hide | unhide | ban | unban | badge   (badge: "vendor" | "staff" | "market maker" | null)
const json = (obj, status = 200) => new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });

function authorized(request, env) {
  const key = new URL(request.url).searchParams.get("key");
  return env.ADMIN_KEY && key && key === env.ADMIN_KEY;
}

export async function onRequestGet({ request, env }) {
  if (!authorized(request, env)) return json({ error: "Not found." }, 404);
  if (!env.FLOOR) return json({ error: "The Floor is not configured yet." }, 503);
  const { results } = await env.FLOOR.prepare(
    `SELECT p.id AS post_id, p.side, p.body, p.hidden, p.created, u.id AS user_id, u.handle, u.badge, u.banned,
            t.kind, t.key, COUNT(r.id) AS reports, GROUP_CONCAT(r.reason, ' | ') AS reasons
       FROM reports r JOIN posts p ON p.id = r.post_id JOIN users u ON u.id = p.user_id JOIN threads t ON t.id = p.thread_id
      GROUP BY p.id ORDER BY MAX(r.created) DESC LIMIT 200`).all();
  return json({ count: (results || []).length, reported: results || [] });
}

export async function onRequestPost({ request, env }) {
  if (!authorized(request, env)) return json({ error: "Not found." }, 404);
  const db = env.FLOOR;
  if (!db) return json({ error: "The Floor is not configured yet." }, 503);
  const b = await request.json().catch(() => ({}));
  const BADGES = new Set(["vendor", "staff", "market maker"]);
  switch (b.action) {
    case "hide":
    case "unhide":
      if (!Number.isInteger(b.post_id)) return json({ error: "post_id required." }, 400);
      await db.prepare("UPDATE posts SET hidden = ? WHERE id = ?").bind(b.action === "hide" ? 1 : 0, b.post_id).run();
      if (b.action === "unhide") await db.prepare("DELETE FROM reports WHERE post_id = ?").bind(b.post_id).run();
      return json({ ok: true });
    case "ban":
    case "unban":
      if (!b.user_id) return json({ error: "user_id required." }, 400);
      await db.prepare("UPDATE users SET banned = ? WHERE id = ?").bind(b.action === "ban" ? 1 : 0, String(b.user_id)).run();
      return json({ ok: true });
    case "badge":
      if (!b.user_id) return json({ error: "user_id required." }, 400);
      if (b.badge !== null && !BADGES.has(b.badge)) return json({ error: "badge must be vendor, staff, market maker or null." }, 400);
      await db.prepare("UPDATE users SET badge = ? WHERE id = ?").bind(b.badge, String(b.user_id)).run();
      return json({ ok: true });
    default:
      return json({ error: "action must be hide, unhide, ban, unban or badge." }, 400);
  }
}
