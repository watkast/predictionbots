#!/usr/bin/env bash
# Deploy the site to Cloudflare Pages from CI. Needs CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID in the env (token:
# Pages Edit, D1 Edit, Workers KV Storage Edit, Account Settings Read). Creates the D1 database `floor` and the KV
# namespace `WAITLIST` if they do not exist, writes wrangler.toml with their ids so the bindings travel with the deploy,
# applies the Floor schema, deploys `dist`. Run from site/.
set -euo pipefail
PROJECT="${PAGES_PROJECT:-predictionbots}"
W="npx --yes wrangler@4"

d1_id() { $W d1 list --json 2>/dev/null | python3 -c 'import json,sys; rows=json.load(sys.stdin); print(next((r.get("uuid") for r in rows if r.get("name")=="floor"), ""))'; }
kv_id() { $W kv namespace list 2>/dev/null | python3 -c 'import json,sys; rows=json.load(sys.stdin); print(next((r.get("id") for r in rows if r.get("title","").endswith("WAITLIST")), ""))'; }

D1=$(d1_id || true)
if [ -z "$D1" ]; then echo "creating D1 floor"; $W d1 create floor >/dev/null 2>&1 || true; D1=$(d1_id || true); fi
KV=$(kv_id || true)
if [ -z "$KV" ]; then echo "creating KV WAITLIST"; $W kv namespace create WAITLIST >/dev/null 2>&1 || true; KV=$(kv_id || true); fi
echo "D1 floor: ${D1:-missing}   KV WAITLIST: ${KV:-missing}"

{
  echo "name = \"$PROJECT\""
  echo 'pages_build_output_dir = "dist"'
  echo 'compatibility_date = "2026-01-01"'
  if [ -n "$D1" ]; then printf '[[d1_databases]]\nbinding = "FLOOR"\ndatabase_name = "floor"\ndatabase_id = "%s"\n' "$D1"; fi
  if [ -n "$KV" ]; then printf '[[kv_namespaces]]\nbinding = "WAITLIST"\nid = "%s"\n' "$KV"; fi
} > wrangler.toml
cat wrangler.toml

if [ -n "$D1" ]; then $W d1 execute floor --remote --file=schema.sql >/dev/null && echo "schema applied"; fi
# the project must exist before the first deploy; create is a no-op error if it does
$W pages project create "$PROJECT" --production-branch main >/dev/null 2>&1 || true
# Cloudflare's API answers 5xx now and then (13 Nov 2026: a 503 on the project lookup failed a whole deploy, and the
# next one was hours away): three tries before the run goes red.
for try in 1 2 3; do
  if $W pages deploy dist --project-name="$PROJECT" --commit-dirty=true --branch main; then exit 0; fi
  echo "deploy try $try failed"; [ "$try" = 3 ] || sleep $((30 * try))
done
echo "the deploy failed three times"; exit 1
