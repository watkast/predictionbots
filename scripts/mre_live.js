#!/usr/bin/env node
// Mr. E — a deliberately simple bot on the Polymarket US 15-minute ETH Up/Down market, completely separate from Mr. P:
//   each round, rest a limit BUY at 25¢ for 1 share on BOTH sides (Up, and Down = a short of Up at 75¢);
//   the first one to fill wins — the other is cancelled — and a limit SELL at 30¢ for that share is rested at once;
//   the resting buys are pulled with 7:00 left (no entries after that); the 30¢ sell stays until the window closes, and
//   whatever is still held settles (a 25¢ share pays $1 or $0).
//   Nothing else: no model, no exits, no sizing. Max at risk per round: 25¢.
//
//   node scripts/mre_live.js            # live (POLYMARKET_KEY_ID / POLYMARKET_SECRET_KEY)
//   node scripts/mre_live.js --dry      # logs what it would do, places nothing
// Env: MRE_DIR (log + MRE.md, default ./mre), MRE_MINUTES (stop after N minutes), MRE_BUY (default 0.25), MRE_SELL (0.30), MRE_QTY (1), MRE_NOBUY_LEFT (420 s),
//      MRE_SLUG_PREFIX (default cpceth-eth-updown-15m- : the ETH 15-minute market; cpc-btc-updown-15m- would be BTC)
'use strict';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const DRY = process.argv.includes('--dry');
const DIR = process.env.MRE_DIR || 'mre'; fs.mkdirSync(DIR, { recursive: true });
const BUY = Number(process.env.MRE_BUY || 0.25), SELL = Number(process.env.MRE_SELL || 0.30), QTY = Number(process.env.MRE_QTY || 1);
const MINUTES = Number(process.env.MRE_MINUTES || 0) || 0, NOBUY_LEFT = Number(process.env.MRE_NOBUY_LEFT || 420);
const KEY_ID = process.env.POLYMARKET_KEY_ID || '', SECRET = process.env.POLYMARKET_SECRET_KEY || '';
const API = 'https://api.polymarket.us', GATEWAY = 'https://gateway.polymarket.us', ROUND = 900;
const PREFIX = process.env.MRE_SLUG_PREFIX || 'cpceth-eth-updown-15m-';
const SLUG = T0 => { const d = new Date(T0 * 1000); const p = n => String(n).padStart(2, '0'); return `${PREFIX}${d.getUTCFullYear()}-${p(d.getUTCMonth() + 1)}-${p(d.getUTCDate())}-${p(d.getUTCHours())}${p(d.getUTCMinutes())}z`; };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const money = v => ({ value: (Math.round(v * 100) / 100).toFixed(2), currency: 'USD' });
const amt = v => v && typeof v === 'object' ? Number(v.value) : Number(v);

// ---- log, state, report
const logPath = path.join(DIR, 'live.jsonl'), statePath = path.join(DIR, 'state.json');
let state = { startedAt: Date.now(), mode: DRY ? 'dry' : 'live', rounds: [], balanceStart: null, balanceNow: null, errors: 0 };
try { const prev = JSON.parse(fs.readFileSync(statePath, 'utf8')); if (prev.mode === state.mode) state = prev; } catch (e) {}
const tail = []; let tailDirty = false, tailAt = 0;
const tailPush = rec => { tail.push(rec); if (tail.length > 150) tail.shift(); tailDirty = true; };
const flushTail = () => { if (!tailDirty || Date.now() - tailAt < 2000) return; tailDirty = false; tailAt = Date.now(); try { const tmp = path.join(DIR, 'tail.tmp'); fs.writeFileSync(tmp, tail.map(r => JSON.stringify(r)).join('\n') + '\n'); fs.renameSync(tmp, path.join(DIR, 'tail.jsonl')); } catch (e) {} };
const log = (k, d) => { const rec = { t: Date.now(), k, d }; fs.appendFileSync(logPath, JSON.stringify(rec) + '\n'); console.log(new Date(rec.t).toISOString(), k, JSON.stringify(d).slice(0, 300)); tailPush(rec); flushTail(); };
const live = { slug: '', T: 0, resting: [], held: null };   // what the snapshot shows
const save = () => { try { fs.writeFileSync(statePath, JSON.stringify(state, null, 1)); } catch (e) {} };
const et = ms => new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }).format(new Date(ms));
function report() {
  const R = state.rounds, closed = R.filter(r => r.pnl != null), pnl = closed.reduce((s, r) => s + r.pnl, 0);
  const sold = closed.filter(r => r.exit === 'sold at ' + Math.round(SELL * 100) + '¢').length, won = closed.filter(r => r.exit === 'won at the bell').length, lost = closed.filter(r => r.exit === 'lost at the bell').length, none = R.filter(r => r.exit === 'no fill').length;
  const lines = ['# Mr. E — live progress', '', `Market **${PREFIX.replace(/-$/, '')}** · mode **${state.mode}** · rests ${QTY} share at ${Math.round(BUY * 100)}¢ on both sides each round, sells the first fill at ${Math.round(SELL * 100)}¢ · started ${et(state.startedAt)} ET · updated ${et(Date.now())} ET`,
    state.balanceStart != null ? `Account balance $${Number(state.balanceStart).toFixed(2)} at start → $${Number(state.balanceNow ?? state.balanceStart).toFixed(2)} now (shared with Mr. P)` : '', '',
    `**Rounds ${R.length} · fills ${R.length - none} · sold at ${Math.round(SELL * 100)}¢ ${sold} · held and won ${won} · held and lost ${lost} · no fill ${none} · P&L ${pnl >= 0 ? '+' : '−'}$${Math.abs(pnl).toFixed(2)}** · errors ${state.errors}`, '',
    '| round (ET) | side | bought | exit | P&L |', '|---|---|---|---|---|'];
  for (const r of R.slice(-60).reverse()) lines.push(`| ${et(r.T0 * 1000)} | ${r.side || '—'} | ${r.buyPx != null ? Math.round(r.buyPx * 100) + '¢ at ' + Math.floor(r.buyLeft / 60) + ':' + String(r.buyLeft % 60).padStart(2, '0') : '—'} | ${r.exit || 'open'} | ${r.pnl != null ? (r.pnl >= 0 ? '+' : '−') + '$' + Math.abs(r.pnl).toFixed(2) : '—'} |`);
  lines.push('', 'Every order, fill and settlement: `live.jsonl` beside this file. Source: `scripts/mre_live.js`.');
  fs.writeFileSync(path.join(DIR, 'MRE.md'), lines.join('\n') + '\n');
}

// ---- exchange
function authHeaders(method, p) {
  const ts = String(Date.now()); let seed = Buffer.from(SECRET, 'base64'); if (seed.length === 64) seed = seed.subarray(0, 32);
  const key = crypto.createPrivateKey({ key: Buffer.concat([Buffer.from('302e020100300506032b657004220420', 'hex'), seed]), format: 'der', type: 'pkcs8' });
  return { 'X-PM-Access-Key': KEY_ID, 'X-PM-Timestamp': ts, 'X-PM-Signature': crypto.sign(null, Buffer.from(ts + method + p), key).toString('base64') };
}
async function api(method, p, body, query) {
  const r = await fetch(API + p + (query ? '?' + new URLSearchParams(query) : ''), { method, headers: { 'Content-Type': 'application/json', 'User-Agent': 'mre-live/1.0', ...authHeaders(method, p) }, body: body ? JSON.stringify(body) : undefined });
  const txt = await r.text(); let j; try { j = JSON.parse(txt); } catch (e) { j = { raw: txt }; }
  if (!r.ok) { const err = new Error(method + ' ' + p + ' -> HTTP ' + r.status + ' ' + txt.slice(0, 300)); err.status = r.status; throw err; }
  return j;
}
const ex = {
  async balance() { const j = await api('GET', '/v1/account/balances'); const b = (j.balances && j.balances[0]) || {}; return { cash: Number(b.buyingPower ?? NaN), total: Number(b.currentBalance ?? NaN) }; },
  async place(o) { if (DRY) { log('dry', o); return { id: 'dry-' + Date.now() }; } return api('POST', '/v1/orders', o); },
  async order(id) { for (let i = 0; i < 4; i++) { try { const j = await api('GET', '/v1/order/' + id); return j.order || j; } catch (e) { if (!(e.status === 404 && i < 3)) throw e; await sleep(400); } } },
  async cancel(id, slug) { if (DRY || !id || id.startsWith('dry-')) return; try { await api('POST', '/v1/order/' + id + '/cancel', { marketSlug: slug }); } catch (e) { if (!/HTTP 4/.test(e.message)) throw e; } },
  async market(slug) { try { const r = await fetch(GATEWAY + '/v1/market/slug/' + slug); return await r.json(); } catch (e) { return null; } },
  async book(slug) { try { const r = await fetch(GATEWAY + '/v1/markets/' + slug + '/book'); const j = await r.json(); const md = j.marketData || j; const lv = a => (a || []).map(e => [Number(e.px && e.px.value != null ? e.px.value : e.px), Number(e.qty)]).filter(x => Number.isFinite(x[0]) && x[1] > 0); const o = lv(md.offers).sort((a, b) => a[0] - b[0]), b = lv(md.bids).sort((a, b) => b[0] - a[0]); return { upAsk: o.length ? o[0][0] : NaN, upBid: b.length ? b[0][0] : NaN }; } catch (e) { return null; } }
};
// a Down share at price d is a short of the Up contract quoted at 1 − d (the exchange shows a BUY_SHORT as a SELL of Up at the price sent)
const buyOrder = (slug, side) => ({ marketSlug: slug, intent: side === 'UP' ? 'ORDER_INTENT_BUY_LONG' : 'ORDER_INTENT_BUY_SHORT', type: 'ORDER_TYPE_LIMIT', price: money(side === 'UP' ? BUY : 1 - BUY), quantity: QTY, tif: 'TIME_IN_FORCE_GOOD_TILL_CANCEL' });
const sellOrder = (slug, side) => ({ marketSlug: slug, intent: side === 'UP' ? 'ORDER_INTENT_SELL_LONG' : 'ORDER_INTENT_SELL_SHORT', type: 'ORDER_TYPE_LIMIT', price: money(side === 'UP' ? SELL : 1 - SELL), quantity: QTY, tif: 'TIME_IN_FORCE_GOOD_TILL_CANCEL' });
const filledOf = async id => { const o = await ex.order(id); if (!o) return { qty: 0 }; const q = Number(o.cumQuantity || 0); const px = amt(o.avgPx); return { qty: q, px: Number.isFinite(px) ? px : NaN, state: o.state || '' }; };

// ---- one round
async function playRound(T0) {
  const slug = SLUG(T0), T = T0 + ROUND; const rec = { T0, slug, side: null, buyPx: null, buyLeft: null, exit: null, pnl: null }; state.rounds.push(rec); save();
  const ids = {}; let held = null; live.slug = slug; live.T = T; live.resting = ['UP', 'DOWN']; live.held = null;
  for (const side of ['UP', 'DOWN']) { try { const res = await ex.place(buyOrder(slug, side)); ids[side] = res.id || (res.order && res.order.id); log('rest', { slug, side, at: BUY, id: ids[side] }); } catch (e) { state.errors++; log('error', { place: side, msg: e.message.slice(0, 300) }); } }
  let sellId = null, buysPulled = false;
  while (Date.now() / 1000 < T - 2) {
    await sleep(2000);
    if (!held && !buysPulled && T - Date.now() / 1000 <= NOBUY_LEFT) {   // no more buys inside the last 7:00
      for (const side of ['UP', 'DOWN']) if (ids[side]) { await ex.cancel(ids[side], slug); ids[side] = null; }
      buysPulled = true; live.resting = []; log('round', { slug, buysPulled: 'no entry inside the last ' + Math.round(NOBUY_LEFT / 60) + ' min' });
    }
    if (!held) {
      if (buysPulled) break;
      for (const side of ['UP', 'DOWN']) { if (!ids[side] || DRY) continue;
        let f; try { f = await filledOf(ids[side]); } catch (e) { continue; }
        if (f.qty >= QTY) { const px = side === 'UP' ? f.px : 1 - f.px; held = { side, px }; rec.side = side; rec.buyPx = px; rec.buyLeft = Math.round(T - Date.now() / 1000); log('fill', { slug, side, px, qty: f.qty });
          const other = side === 'UP' ? 'DOWN' : 'UP'; await ex.cancel(ids[other], slug); ids[other] = null; live.resting = []; live.held = side + ' @ ' + Math.round(px * 100) + '¢';
          try { const res = await ex.place(sellOrder(slug, side)); sellId = res.id || (res.order && res.order.id); log('rest', { slug, side, sellAt: SELL, id: sellId }); } catch (e) { state.errors++; log('error', { placeSell: e.message.slice(0, 300) }); }
          save(); break; } }
    } else if (sellId) {
      let f; try { f = await filledOf(sellId); } catch (e) { continue; }
      if (f.qty >= QTY) { const px = held.side === 'UP' ? f.px : 1 - f.px; rec.exit = 'sold at ' + Math.round(SELL * 100) + '¢'; rec.sellPx = px; rec.pnl = +((px - rec.buyPx) * QTY).toFixed(2); log('fill', { slug, side: held.side, sold: px, pnl: rec.pnl }); save(); return; }
    }
  }
  for (const id of [ids.UP, ids.DOWN]) if (id) await ex.cancel(id, slug);   // the 30¢ sell stays until the window closes; the exchange closes it with the market
  if (!held) { rec.exit = 'no fill'; log('round', { slug, exit: 'no fill' }); save(); return; }
  rec.exit = 'held to the bell'; rec.sellId = sellId; save(); log('round', { slug, held: held.side, px: held.px });
  settleLater(rec);
}
// the result lands on the gateway 20 s to several minutes after the bell
async function settleLater(rec) {
  for (let i = 0; i < 40; i++) {
    await sleep(30000);
    if (rec.sellId && !DRY) { try { const f = await filledOf(rec.sellId); if (f.qty >= QTY) { const px = rec.side === 'UP' ? f.px : 1 - f.px; rec.exit = 'sold at ' + Math.round(SELL * 100) + '¢'; rec.sellPx = px; rec.pnl = +((px - rec.buyPx) * QTY).toFixed(2); log('fill', { slug: rec.slug, side: rec.side, sold: px, pnl: rec.pnl, late: true }); save(); report(); return; } } catch (e) {} }   // the sell may have filled in the last seconds
    const m = await ex.market(rec.slug); const apt = (m && (m.assetPriceTerms || (m.market && m.market.assetPriceTerms))) || {};
    const sp = amt(apt.settlementPrice), ptb = amt(apt.priceToBeat);
    if (Number.isFinite(sp) && Number.isFinite(ptb)) { const result = sp >= ptb ? 'UP' : 'DOWN'; const won = result === rec.side; rec.exit = won ? 'won at the bell' : 'lost at the bell'; rec.pnl = +(((won ? 1 : 0) - rec.buyPx) * QTY).toFixed(2); rec.result = result; log('settle', { slug: rec.slug, result, side: rec.side, pnl: rec.pnl }); save(); report(); return; }
  }
  log('warn', { slug: rec.slug, settlement: 'not seen in 20 min' });
}

// ---- main
(async () => {
  log('start', { mode: state.mode, market: PREFIX, buy: BUY, sell: SELL, qty: QTY, node: process.version });
  if (!DRY) { try { const b = await ex.balance(); if (state.balanceStart == null) state.balanceStart = b.total; state.balanceNow = b.total; log('balance', b); } catch (e) { console.error('cannot read the account — stopping', e.message); process.exit(2); } }
  const deadline = MINUTES ? Date.now() + MINUTES * 60000 : Infinity;
  const stop = async () => { log('stop', {}); report(); save(); process.exit(0); };
  process.on('SIGTERM', stop); process.on('SIGINT', stop);
  setInterval(async () => { if (!DRY) { try { const b = await ex.balance(); state.balanceNow = b.total; } catch (e) {} } report(); save(); }, 60000);
  setInterval(async () => { if (!live.slug) return; const b = await ex.book(live.slug); tailPush({ t: Date.now(), k: 'snap', d: { bot: 'E', slug: live.slug, r: Math.max(0, Math.round(live.T - Date.now() / 1000)), upAsk: b ? b.upAsk : NaN, dnAsk: b && Number.isFinite(b.upBid) ? +(1 - b.upBid).toFixed(2) : NaN, resting: live.resting, held: live.held } }); flushTail(); }, 10000);
  while (Date.now() < deadline) {
    const now = Date.now() / 1000, T0 = Math.floor(now / ROUND) * ROUND;
    if (now - T0 < 3) await sleep(3000);
    if (now > T0 + ROUND - 30) { await sleep(5000); continue; }         // too late in this round: wait for the next
    await playRound(T0);
    const next = (Math.floor(Date.now() / 1000 / ROUND) + 1) * ROUND; await sleep(Math.max(1000, (next - Date.now() / 1000 + 2) * 1000));
  }
  stop();
})().catch(e => { console.error(e); process.exit(1); });
