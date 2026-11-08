# The Floor — build plan (v1)

Two-sided threads (Defend / Deviate) under every benchmark row, research post, Learn page and market page. Read
without an account; post with one tap. UGC lives on our domain and is indexed.

## Stack
- **Auth:** Clerk (free tier to 10,000 MAU): Google, Apple, email magic link. No password, no walkthrough. Clerk's
  hosted components on the page; the session JWT is verified in the Function with Clerk's JWKS.
- **Storage:** Cloudflare D1 (SQLite). Tables: `threads(id, kind, key, title, created)`, `posts(id, thread_id, user_id,
  handle, side CHECK(side IN ('defend','deviate')), body, data_url, created, hidden, vendor_badge)`, `votes(post_id,
  user_id, weight)`, `reports(post_id, user_id, reason, created)`, `users(id, handle, badge, created, banned)`.
- **Functions (Pages):** `GET /api/floor/:kind/:key` (thread + posts, public, cached 30 s), `POST /api/floor/:kind/:key`
  (post; auth; rate limit 5/min/user; body ≤ 2,000 chars; links allowed except venue referral/promo patterns, which are
  rejected with a message), `POST /api/floor/vote`, `POST /api/floor/report`, `GET /floor/:kind/:key` (server-rendered
  HTML for crawlers and no-JS: the same thread as a static page with the two columns).
- **Weights:** a post with an attached data file or a link into our repo/data counts double in the column tally.
- **Badges:** `vendor` (self-declared at sign-up or set by us; required for anyone posting about their own product),
  `staff`, `market maker` (self-declared). Badges render beside the handle.

## House rules (enforced, shown on every thread)
Patterns and public records only; never a private person's name without a court or exchange filing (a filter flags
capitalised two-word names in posts about "insider"/"whale" for review before publish); vendors wear the badge;
no referral links; one tap to report; three reports hide a post pending review; posts are public and indexed.

## Order of work
1. D1 schema + Functions with a stub auth (dev) and the server-rendered thread page.
2. Clerk keys (Noah creates the Clerk app; keys as Pages env vars) → real auth.
3. Thread blocks embedded on: benchmark rows, posts, Learn pages, market pages (the generator emits the block).
4. Moderation page for us (list reports, hide/unhide, badge, ban).
5. Sitemap entries for threads with ≥ 3 posts.
