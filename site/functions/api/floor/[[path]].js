// The Floor API.
//   GET  /api/floor/:kind/:key            -> { thread, posts, tally }           (public, cached 30 s)
//   POST /api/floor/:kind/:key            -> { post }   body {side, body, data_url?, title?}   (auth)
//   POST /api/floor/vote                  -> { votes }  body {post_id}                           (auth)
//   POST /api/floor/report                -> { ok }     body {post_id, reason?}                  (auth)
import { json, validKey, checkBody, userFromRequest, ensureUser, getThread, loadPosts, tally } from "../../../floor_lib.js";

const SCHEMA = [
  "CREATE TABLE IF NOT EXISTS threads (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, key TEXT NOT NULL, title TEXT NOT NULL, created TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')), UNIQUE(kind, key))",
  "CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, handle TEXT NOT NULL UNIQUE, badge TEXT, banned INTEGER NOT NULL DEFAULT 0, created TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')))",
  "CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, thread_id INTEGER NOT NULL REFERENCES threads(id), user_id TEXT NOT NULL REFERENCES users(id), side TEXT NOT NULL CHECK (side IN ('defend','deviate')), body TEXT NOT NULL CHECK (length(body) BETWEEN 1 AND 2000), data_url TEXT, hidden INTEGER NOT NULL DEFAULT 0, created TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')))",
  "CREATE INDEX IF NOT EXISTS posts_thread ON posts(thread_id, created)",
  "CREATE TABLE IF NOT EXISTS votes (post_id INTEGER NOT NULL REFERENCES posts(id), user_id TEXT NOT NULL REFERENCES users(id), created TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')), PRIMARY KEY (post_id, user_id))",
  "CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, post_id INTEGER NOT NULL REFERENCES posts(id), user_id TEXT NOT NULL REFERENCES users(id), reason TEXT, created TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')), UNIQUE(post_id, user_id))",
];
const RATE = new Map(); // per-isolate soft rate limit: user -> [timestamps]
function limited(uid) {
  const now = Date.now(), arr = (RATE.get(uid) || []).filter((t) => now - t < 60_000);
  arr.push(now); RATE.set(uid, arr);
  return arr.length > 5;
}

export async function onRequest({ request, env, params }) {
  const db = env.FLOOR;
  if (!db) return json({ error: "The Floor is not configured yet." }, 503);
  const path = (params.path || []);
  const method = request.method.toUpperCase();

  // development only: create the tables in the local D1 (DEV_AUTH must be "1"; never set in production)
  if (path[0] === "__init" && env.DEV_AUTH === "1") {
    for (const stmt of SCHEMA) await db.prepare(stmt).run();
    return json({ ok: true, tables: ["threads", "users", "posts", "votes", "reports"] });
  }

  if (method === "POST" && path[0] === "vote") {
    const u = await userFromRequest(request, env); if (!u) return json({ error: "Sign in to vote." }, 401);
    const user = await ensureUser(db, u); if (user.banned) return json({ error: "This account cannot vote." }, 403);
    const { post_id } = await request.json().catch(() => ({}));
    if (!Number.isInteger(post_id)) return json({ error: "post_id required." }, 400);
    await db.prepare("INSERT OR IGNORE INTO votes (post_id, user_id) VALUES (?, ?)").bind(post_id, user.id).run();
    const row = await db.prepare("SELECT COUNT(*) AS n FROM votes WHERE post_id = ?").bind(post_id).first();
    return json({ votes: row.n });
  }
  if (method === "POST" && path[0] === "report") {
    const u = await userFromRequest(request, env); if (!u) return json({ error: "Sign in to report." }, 401);
    const user = await ensureUser(db, u);
    const { post_id, reason } = await request.json().catch(() => ({}));
    if (!Number.isInteger(post_id)) return json({ error: "post_id required." }, 400);
    await db.prepare("INSERT OR IGNORE INTO reports (post_id, user_id, reason) VALUES (?, ?, ?)").bind(post_id, user.id, String(reason || "").slice(0, 200)).run();
    return json({ ok: true, message: "Thanks. Three reports hide a post until we review it." });
  }

  const [kind, ...rest] = path; const key = rest.join("/");
  if (!validKey(kind, key)) return json({ error: "Unknown thread." }, 404);

  if (method === "GET") {
    const thread = await getThread(db, kind, key, null);
    if (!thread) return json({ thread: null, posts: [], tally: { defend: 0, deviate: 0 } }, 200, { "Cache-Control": "public, max-age=30" });
    const posts = await loadPosts(db, thread.id);
    return json({ thread, posts, tally: tally(posts) }, 200, { "Cache-Control": "public, max-age=30" });
  }
  if (method === "POST") {
    const u = await userFromRequest(request, env); if (!u) return json({ error: "Sign in with one tap to post." }, 401);
    const user = await ensureUser(db, u); if (user.banned) return json({ error: "This account cannot post." }, 403);
    if (limited(user.id)) return json({ error: "Slow down: five posts a minute." }, 429);
    const b = await request.json().catch(() => ({}));
    const side = b.side === "defend" ? "defend" : b.side === "deviate" ? "deviate" : null;
    if (!side) return json({ error: "Pick Defend or Deviate." }, 400);
    const problem = checkBody(b.body); if (problem) return json({ error: problem }, 400);
    let data_url = String(b.data_url || "").trim().slice(0, 300);
    if (data_url && !/^https?:\/\//i.test(data_url)) return json({ error: "The data link must be a URL." }, 400);
    const thread = await getThread(db, kind, key, String(b.title || key).slice(0, 200));
    const r = await db.prepare("INSERT INTO posts (thread_id, user_id, side, body, data_url) VALUES (?, ?, ?, ?, ?)").bind(thread.id, user.id, side, String(b.body).trim(), data_url || null).run();
    return json({ post: { id: r.meta.last_row_id, side, body: String(b.body).trim(), data_url: data_url || null, handle: user.handle, badge: user.badge, votes: 0, created: new Date().toISOString() } }, 201);
  }
  return json({ error: "Method not allowed." }, 405);
}
