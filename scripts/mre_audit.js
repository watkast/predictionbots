#!/usr/bin/env node
// Read-only account audit for Mr. E: balances, positions, a few activity endpoints, and every order id Mr. E logged in a time
// window re-read from the exchange — its real fills, prices and fees — to reconcile the bots' logged P&L with the cash.
// Places and cancels nothing. Env: POLYMARKET_KEY_ID / POLYMARKET_SECRET_KEY, AUDIT_FROM / AUDIT_TO (ISO), AUDIT_LOGS (comma list).
'use strict';
const fs = require('fs'), crypto = require('crypto');
const KEY_ID = process.env.POLYMARKET_KEY_ID || '', SECRET = process.env.POLYMARKET_SECRET_KEY || '', API = 'https://api.polymarket.us';
function authHeaders(method, p) { const ts = String(Date.now()); let seed = Buffer.from(SECRET, 'base64'); if (seed.length === 64) seed = seed.subarray(0, 32);
  const key = crypto.createPrivateKey({ key: Buffer.concat([Buffer.from('302e020100300506032b657004220420', 'hex'), seed]), format: 'der', type: 'pkcs8' });
  return { 'X-PM-Access-Key': KEY_ID, 'X-PM-Timestamp': ts, 'X-PM-Signature': crypto.sign(null, Buffer.from(ts + method + p), key).toString('base64') }; }
async function get(p, q) { const url = API + p + (q ? '?' + new URLSearchParams(q) : ''); const r = await fetch(url, { headers: { 'Content-Type': 'application/json', 'User-Agent': 'pm15-live/1.0', ...authHeaders('GET', p) } }); const t = await r.text(); return { status: r.status, body: t }; }
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const from = Date.parse(process.env.AUDIT_FROM || '2026-11-03T08:22:00Z'), to = Date.parse(process.env.AUDIT_TO || new Date().toISOString());
  for (const [p, q] of [['/v1/account/balances'], ['/v1/portfolio/positions'], ['/v1/orders/open'], ['/v1/orders', { limit: 5 }], ['/v1/portfolio/activities', { limit: 5 }], ['/v1/portfolio/activity', { limit: 5 }], ['/v1/fills', { limit: 5 }], ['/v1/portfolio/fills', { limit: 5 }], ['/v1/trades', { limit: 5 }], ['/v1/account/transactions', { limit: 5 }]]) {
    const r = await get(p, q); console.log('== GET', p, r.status, r.body.slice(0, 1500).replace(/\s+/g, ' ')); }
  const ids = new Map();
  for (const f of (process.env.AUDIT_LOGS || '').split(',').filter(Boolean)) { if (!fs.existsSync(f)) continue;
    for (const l of fs.readFileSync(f, 'utf8').split('\n')) { if (!l) continue; let r; try { r = JSON.parse(l); } catch (e) { continue; } if (r.t < from - 20 * 60e3 || r.t > to) continue; const d = r.d || {};
      if (d.id) ids.set(d.id, { slug: d.slug, kind: d.sellAt ? 'sell' : 'buy', side: d.side, t: r.t, bot: f });
      if (r.k === 'ladder') for (const id of d.ids || []) ids.set(id, { slug: d.slug, kind: 'buy', t: r.t, bot: f }); } }
  console.log('== order ids from the logs:', ids.size);
  // the account's own trade history: any trade with no order id from the bots' logs was placed by someone else (the app, by hand)
  const acts = []; let cursor = null;
  for (let page = 0; page < 20; page++) { const q = { limit: 200 }; if (cursor) q.cursor = cursor; const r = await get('/v1/portfolio/activities', q); if (r.status !== 200) { console.log('== activities page', page, r.status); break; }
    let j; try { j = JSON.parse(r.body); } catch (e) { break; } const a = j.activities || []; acts.push(...a); cursor = j.nextCursor || j.cursor || (j.pagination && j.pagination.nextCursor); if (page === 0) console.log('== activities keys', Object.keys(j).join(','), 'first', JSON.stringify(a[0] || {}).slice(0, 1200));
    if (!cursor || !a.length) break; await sleep(800); }
  console.log('== activities', acts.length);
  const idsIn = x => { const out = []; const walk = v => { if (v && typeof v === 'object') { for (const [k, w] of Object.entries(v)) { if (k === 'id' && typeof w === 'string') out.push(w); walk(w); } } }; walk(x); return out; };
  const ts = x => { const m = JSON.stringify(x).match(/"(?:createTime|transactTime|updateTime|time|createdAt)":"([^"]+)"/); return m ? Date.parse(m[1]) : NaN; };
  let foreign = 0, foreignCash = 0; const kinds = {};
  for (const a of acts) { kinds[a.type] = (kinds[a.type] || 0) + 1; const t = ts(a); if (Number.isFinite(t) && (t < from || t > to)) continue;
    if (a.type !== 'ACTIVITY_TYPE_TRADE') { console.log('== other activity', a.type, JSON.stringify(a).slice(0, 400)); continue; }
    const mine = idsIn(a).some(id => ids.has(id)); if (mine) continue; foreign++;
    if (foreign <= 40) console.log('== NOT A BOT ORDER', new Date(t).toISOString(), JSON.stringify(a).replace(/"marketMetadata":\{[^}]*\{[^}]*\}[^}]*\},?/g, '').slice(0, 700)); }
  console.log('== activity types', JSON.stringify(kinds), '· trades in the window not placed by either bot:', foreign);
  if (process.env.AUDIT_SKIP_ORDERS) return;
  let printed = 0, cashOut = 0, cashIn = 0, fees = 0, n = 0; const byState = {};
  for (const [id, meta] of ids) {
    const r = await get('/v1/order/' + id); n++; await sleep(250);
    if (r.status !== 200) { byState['HTTP ' + r.status] = (byState['HTTP ' + r.status] || 0) + 1; continue; }
    let j; try { j = JSON.parse(r.body); } catch (e) { continue; } const o = j.order || j;
    if (printed < 3 && Number(o.cumQuantity || 0) > 0) { console.log('== sample filled order', r.body.slice(0, 2500)); printed++; }
    byState[o.state] = (byState[o.state] || 0) + 1;
    const q = Number(o.cumQuantity || 0); if (!(q > 0)) continue;
    const px = Number(o.avgPx && o.avgPx.value != null ? o.avgPx.value : o.avgPx); const intent = o.intent || '';
    const isShort = /SHORT/.test(intent), isBuy = /BUY/.test(intent);
    const ownPx = isShort ? 1 - px : px;   // shorts are quoted in Up terms
    const fee = ['fees', 'fee', 'commission', 'commissions', 'totalFees'].map(k => o[k]).find(v => v != null);
    const feeV = fee == null ? 0 : Number(fee.value != null ? fee.value : fee); fees += Number.isFinite(feeV) ? feeV : 0;
    if (isBuy) cashOut += q * ownPx; else cashIn += q * ownPx;
  }
  console.log('== order states', JSON.stringify(byState));
  console.log('== from fills: bought $' + cashOut.toFixed(2) + ', sold $' + cashIn.toFixed(2) + ', fees reported $' + fees.toFixed(2) + ', net before settlement $' + (cashIn - cashOut - fees).toFixed(2));
})().catch(e => { console.error(e); process.exit(1); });
