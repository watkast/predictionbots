-- The Floor: Defend / Deviate threads. Cloudflare D1 (SQLite). Apply with:
--   wrangler d1 execute floor --remote --file=site/schema.sql   (prod)
--   wrangler pages dev ... --d1=FLOOR=floor  then  wrangler d1 execute floor --local --file=site/schema.sql
CREATE TABLE IF NOT EXISTS threads (
  id INTEGER PRIMARY KEY,
  kind TEXT NOT NULL,            -- benchmark | post | learn | market | rule
  key TEXT NOT NULL,             -- e.g. turbine_standard, 2026-11-08-free-money-that-wasnt, pmus/btc-updown-5m
  title TEXT NOT NULL,
  created TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE(kind, key)
);
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,           -- Clerk user id (or dev:<name> in development)
  handle TEXT NOT NULL UNIQUE,
  badge TEXT,                    -- vendor | staff | market maker | NULL
  banned INTEGER NOT NULL DEFAULT 0,
  created TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY,
  thread_id INTEGER NOT NULL REFERENCES threads(id),
  user_id TEXT NOT NULL REFERENCES users(id),
  side TEXT NOT NULL CHECK (side IN ('defend','deviate')),
  body TEXT NOT NULL CHECK (length(body) BETWEEN 1 AND 2000),
  data_url TEXT,                 -- a link to a data file; counts double in the tally
  hidden INTEGER NOT NULL DEFAULT 0,
  created TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS posts_thread ON posts(thread_id, created);
CREATE TABLE IF NOT EXISTS votes (
  post_id INTEGER NOT NULL REFERENCES posts(id),
  user_id TEXT NOT NULL REFERENCES users(id),
  created TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  PRIMARY KEY (post_id, user_id)
);
CREATE TABLE IF NOT EXISTS reports (
  id INTEGER PRIMARY KEY,
  post_id INTEGER NOT NULL REFERENCES posts(id),
  user_id TEXT NOT NULL REFERENCES users(id),
  reason TEXT,
  created TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE(post_id, user_id)
);
