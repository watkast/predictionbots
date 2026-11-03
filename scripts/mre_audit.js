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
async function get(p, q) { const url = API + p + (q ? '?' + new URLSearchParams(q) : ''); const r = await fetch(url, { headers: { 'User-Agent': 'mre-audit/1.0', ...authHeaders('GET', p) } }); const t = await r.text(); return { status: r.status, body: t }; }
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
  let printed = 0, cashOut = 0, cashIn = 0, fees = 0, n = 0; const byState = {};
  for (const [id, meta] of ids) {
    const r = await get('/v1/order/' + id); n++; if (n % 20 === 0) await sleep(500);
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
