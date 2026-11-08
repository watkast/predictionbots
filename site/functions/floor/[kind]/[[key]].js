// Server-rendered thread page: /floor/:kind/:key — the same thread as a static page, for crawlers and no-JS readers.
import { validKey, getThread, loadPosts, renderThreadHTML } from "../../../floor_lib.js";

export async function onRequestGet({ request, env, params }) {
  const kind = params.kind, key = (params.key || []).join("/");
  if (!env.FLOOR || !validKey(kind, key)) return new Response("Not found", { status: 404 });
  const thread = await getThread(env.FLOOR, kind, key, null);
  if (!thread) return new Response("No thread here yet.", { status: 404, headers: { "Content-Type": "text/plain" } });
  const posts = await loadPosts(env.FLOOR, thread.id);
  const base = new URL(request.url).origin;
  return new Response(renderThreadHTML(thread, posts, base), { headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "public, max-age=60" } });
}
