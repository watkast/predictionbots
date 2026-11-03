#!/usr/bin/env node
// Mr. E — a deliberately simple bot on the Polymarket US 15-minute ETH Up/Down market, completely separate from Mr. P:
//   each round, rest a limit BUY at 30¢ for 1 share on BOTH sides (Up, and Down = a short of Up at 70¢);
//   the first one to fill wins — the other is cancelled — and a limit SELL at 55¢ for that share is rested at once;
//   the resting buys are pulled with 7:00 left (no entries after that); the 55¢ sell stays until the window closes, and
//   whatever is still held settles (a 30¢ share pays $1 or $0). Prices: MRE_BUY / MRE_SELL (Nov 2: 25¢ / 30¢ at 6:45 AM MT, 35¢ / 55¢ from 7:36 AM, 30¢ / 55¢ from 3:50 PM).
//   Nothing else: no model, no exits, no sizing. Max at risk per round: the buy price.
//
//   node scripts/mre_live.js            # live (POLYMARKET_KEY_ID / POLYMARKET_SECRET_KEY)
//   node scripts/mre_live.js --dry      # logs what it would do, places nothing
// Env: MRE_DIR (log + MRE.md, default ./mre), MRE_MINUTES (stop after N minutes), MRE_LADDER (default 0.20:0.30, 1¢ rungs), MRE_SELL (0.45), MRE_QTY (shares per rung, 1), MRE_NOBUY_LEFT (540 s),
//      MRE_SLUG_PREFIX (default cpceth-eth-updown-15m- : the ETH 15-minute market; cpc-btc-updown-15m- would be BTC)
'use strict';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const DRY = process.argv.includes('--dry');
const DIR = process.env.MRE_DIR || 'mre'; fs.mkdirSync(DIR, { recursive: true });
const SELL = Number(process.env.MRE_SELL || 0.45), QTY = Number(process.env.MRE_QTY || 1);          // QTY = shares per rung
// the buy ladder: one QTY-share limit at every cent from LO to HI on both sides (MRE_LADDER "lo:hi", default 20¢–30¢; "0.25:0.25" = one price)
const [LO, HI] = String(process.env.MRE_LADDER || '0.20:0.30').split(':').map(Number);
const RUNGS = []; for (let c = Math.round(HI * 100); c >= Math.round(LO * 100); c--) RUNGS.push(c / 100);   // highest first: the price falls into them in this order
const BUY = HI;
const MINUTES = Number(process.env.MRE_MINUTES || 0) || 0, NOBUY_LEFT = Number(process.env.MRE_NOBUY_LEFT || 540);
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
const live = { slug: '', T: 0, resting: [], held: null, ids: null };   // what the snapshot shows; ids = this round's resting buy order ids (cancelled on stop)
const save = () => { try { fs.writeFileSync(statePath, JSON.stringify(state, null, 1)); } catch (e) {} };
const et = ms => new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }).format(new Date(ms));
function report() {
  const R = state.rounds, closed = R.filter(r => r.pnl != null), pnl = closed.reduce((s, r) => s + r.pnl, 0);
  const sold = closed.filter(r => r.exit === 'sold at ' + Math.round(SELL * 100) + '¢').length, won = closed.filter(r => / won at the bell$/.test(r.exit) || r.exit === 'won at the bell').length, lost = closed.filter(r => / lost at the bell$/.test(r.exit) || r.exit === 'lost at the bell').length, none = R.filter(r => r.exit === 'no fill').length;
  const lines = ['# Mr. E — live progress', '', `Market **${PREFIX.replace(/-$/, '')}** · mode **${state.mode}** · rests ${QTY} share at every cent from ${Math.round(LO * 100)}¢ to ${Math.round(HI * 100)}¢ on both sides until ${Math.round(NOBUY_LEFT / 60)}:00 left, sells the first fill at ${Math.round(SELL * 100)}¢ · started ${et(state.startedAt)} ET · updated ${et(Date.now())} ET`,
    state.balanceStart != null ? `Account balance $${Number(state.balanceStart).toFixed(2)} at start → $${Number(state.balanceNow ?? state.balanceStart).toFixed(2)} now (shared with Mr. P)` : '', '',
    `**Rounds ${R.length} · fills ${R.filter(r => r.buyPx != null).length} · sold at ${Math.round(SELL * 100)}¢ ${sold} · held and won ${won} · held and lost ${lost} · no fill ${none} · P&L ${pnl >= 0 ? '+' : '−'}$${Math.abs(pnl).toFixed(2)}** · errors ${state.errors}`, '',
    '| round (ET) | side | bought | exit | P&L |', '|---|---|---|---|---|'];
  for (const r of R.slice(-60).reverse()) lines.push(`| ${et(r.T0 * 1000)} | ${r.side || '—'}${r.qty > 1 ? ' ×' + r.qty : ''} | ${r.buyPx != null ? Math.round(r.buyPx * 100) + '¢ at ' + Math.floor(r.buyLeft / 60) + ':' + String(r.buyLeft % 60).padStart(2, '0') : '—'} | ${r.exit || 'open'} | ${r.pnl != null ? (r.pnl >= 0 ? '+' : '−') + '$' + Math.abs(r.pnl).toFixed(2) : '—'} |`);
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
const buyOrder = (slug, side, px = BUY) => ({ marketSlug: slug, intent: side === 'UP' ? 'ORDER_INTENT_BUY_LONG' : 'ORDER_INTENT_BUY_SHORT', type: 'ORDER_TYPE_LIMIT', price: money(side === 'UP' ? px : 1 - px), quantity: QTY, tif: 'TIME_IN_FORCE_GOOD_TILL_CANCEL' });
const sellOrder = (slug, side) => ({ marketSlug: slug, intent: side === 'UP' ? 'ORDER_INTENT_SELL_LONG' : 'ORDER_INTENT_SELL_SHORT', type: 'ORDER_TYPE_LIMIT', price: money(side === 'UP' ? SELL : 1 - SELL), quantity: QTY, tif: 'TIME_IN_FORCE_GOOD_TILL_CANCEL' });
const filledOf = async id => { const o = await ex.order(id); if (!o) return { qty: 0 }; const q = Number(o.cumQuantity || 0); const px = amt(o.avgPx); return { qty: q, px: Number.isFinite(px) ? px : NaN, state: o.state || '' }; };

// ---- one round
// A ladder of resting buys on both sides (QTY shares at every cent from HI down to LO). The first side to fill at all is the
// side; the other ladder is cancelled; this side's rungs keep resting until the no-buy cutoff, so a deeper dip buys cheaper. The
// sell always covers exactly what is held and unsold (re-placed when more is bought); whatever is still held at the bell settles.
// Fills come top-down (the price falls into 30¢ before 29¢), so each tick polls the highest unfilled rung per side, walking down
// while they fill, plus a sweep of every rung every 10 s for anything the walk missed.
async function playRound(T0) {
  const slug = SLUG(T0), T = T0 + ROUND; const rec = { T0, slug, side: null, buyPx: null, buyLeft: null, qty: 0, sold: 0, exit: null, pnl: null }; state.rounds.push(rec); save();
  const lad = { UP: [], DOWN: [] }; live.slug = slug; live.T = T; live.resting = ['UP', 'DOWN']; live.held = null; live.ids = lad;
  for (const sd of ['UP', 'DOWN']) for (const px of RUNGS) { try { const res = await ex.place({ ...buyOrder(slug, sd, px), quantity: QTY }); lad[sd].push({ id: res.id || (res.order && res.order.id), px, cum: 0, done: false }); } catch (e) { state.errors++; log('error', { place: sd + ' ' + px, msg: e.message.slice(0, 300) }); } }
  log('ladder', { slug, ids: lad.UP.map(r => r.id).concat(lad.DOWN.map(r => r.id)) }); log('rest', { slug, side: 'BOTH', at: HI, ladder: Math.round(LO * 100) + '–' + Math.round(HI * 100) + '¢', rungs: RUNGS.length, qty: QTY });
  const own = (side, px) => side === 'UP' ? px : 1 - px;   // order prices come back in Up terms
  let side = null, sold = 0, proceeds = 0, sell = null, buysPulled = false, lastSweep = 0;
  const bought = () => side ? lad[side].reduce((a, r) => a + r.cum, 0) : 0, cost = () => side ? lad[side].reduce((a, r) => a + r.cum * r.px, 0) : 0;
  const check = async (sd, r) => { let f; try { f = await filledOf(r.id); } catch (e) { return 0; } const add = f.qty - r.cum; if (add > 0) { r.cum = f.qty; if (Number.isFinite(f.px) && f.px > 0) r.px = own(sd, f.px); } if (r.cum >= QTY - 1e-9 || /CANCEL|REJECT|EXPIRE/.test(f.state || '')) r.done = true; return add > 0 ? add : 0; };
  const readSell = async () => { if (!sell) return; let f; try { f = await filledOf(sell.id); } catch (e) { return; } const newQ = f.qty - (sold - sell.base); if (newQ > 0) { proceeds += newQ * own(side, f.px); sold += newQ; rec.sold = sold; log('fill', { slug, side, sold: own(side, f.px), qty: newQ, soldTotal: +sold.toFixed(2), of: +bought().toFixed(2) }); } };
  const placeSell = async () => { const q = +(bought() - sold).toFixed(4); if (q <= 0) return; try { const res = await ex.place({ ...sellOrder(slug, side), quantity: q }); sell = { id: res.id || (res.order && res.order.id), qty: q, base: sold }; rec.sellId = sell.id; log('rest', { slug, side, sellAt: SELL, qty: q, id: sell.id }); } catch (e) { state.errors++; log('error', { placeSell: e.message.slice(0, 300) }); } };
  const cancelLadder = async sd => { for (const r of lad[sd]) if (!r.done) { await ex.cancel(r.id, slug); await check(sd, r); r.done = true; } };
  const scan = async () => {   // new fills on the ladder(s): walk each side top-down while rungs are full; every 10 s check every rung
    const sweep = Date.now() - lastSweep > 10000; if (sweep) lastSweep = Date.now();
    for (const sd of (side ? [side] : ['UP', 'DOWN'])) {
      for (const r of lad[sd]) { if (r.done) continue; const add = await check(sd, r); if (add > 0 && !side) side = sd; if (sweep || r.done) continue; break; }
      if (side) break; } };
  while (Date.now() / 1000 < T - 2) {
    await sleep(2000);
    if (DRY) continue;
    const before = bought(); const hadSide = side;
    await scan();
    if (side && !hadSide) { const other = side === 'UP' ? 'DOWN' : 'UP'; await cancelLadder(other); rec.side = side; rec.buyLeft = Math.round(T - Date.now() / 1000); live.resting = [side]; }
    if (!buysPulled && T - Date.now() / 1000 <= NOBUY_LEFT) {   // no more buys inside the cutoff
      for (const sd of ['UP', 'DOWN']) await cancelLadder(sd);
      buysPulled = true; live.resting = []; log('round', { slug, buysPulled: 'no entry inside the last ' + Math.round(NOBUY_LEFT / 60) + ' min', held: +bought().toFixed(2) });
      if (!side) break;
    }
    if (!side) continue;
    const b = bought();
    if (b > before + 1e-9) { rec.qty = +b.toFixed(4); rec.buyPx = cost() / b; log('fill', { slug, side, px: +rec.buyPx.toFixed(3), qty: +(b - before).toFixed(2), heldTotal: +b.toFixed(2), of: RUNGS.length * QTY }); live.held = side + ' ' + +b.toFixed(2) + ' @ ' + Math.round(rec.buyPx * 100) + '¢';
      if (sell) { await ex.cancel(sell.id, slug); await readSell(); sell = null; }   // re-size the sell to everything held
      await placeSell(); save(); }
    await readSell();
    const ladderOpen = lad[side].some(r => !r.done);
    if (b > 0 && sold >= b - 1e-9 && !ladderOpen) { rec.exit = 'sold at ' + Math.round(SELL * 100) + '¢'; rec.sellPx = proceeds / sold; rec.pnl = +(proceeds - cost()).toFixed(2); live.held = null; live.resting = []; log('round', { slug, exit: rec.exit, qty: +sold.toFixed(2), pnl: rec.pnl }); save(); return; }
  }
  for (const sd of ['UP', 'DOWN']) await cancelLadder(sd);
  const b = bought();
  if (!side || b === 0) { rec.exit = 'no fill'; live.held = null; log('round', { slug, exit: 'no fill' }); save(); return; }
  await readSell(); rec.qty = +b.toFixed(4); rec.buyPx = cost() / b;
  if (sold >= b - 1e-9) { rec.exit = 'sold at ' + Math.round(SELL * 100) + '¢'; rec.sellPx = proceeds / sold; rec.pnl = +(proceeds - cost()).toFixed(2); live.held = null; save(); return; }
  rec.exit = 'held to the bell'; rec._sold = sold; rec._proceeds = proceeds; rec._cost = cost(); rec._sell = sell; save(); log('round', { slug, held: side, qty: +(b - sold).toFixed(2), of: +b.toFixed(2), px: +rec.buyPx.toFixed(3) });
  settleLater(rec);
}
// the result lands on the gateway 20 s to several minutes after the bell
async function settleLater(rec) {
  const own = px => rec.side === 'UP' ? px : 1 - px;
  for (let i = 0; i < 40; i++) {
    await sleep(30000);
    if (rec._sell && !DRY) { try { const f = await filledOf(rec._sell.id); const newQ = f.qty - (rec._sold - rec._sell.base); if (newQ > 0) { rec._proceeds += newQ * own(f.px); rec._sold += newQ; rec.sold = rec._sold; log('fill', { slug: rec.slug, side: rec.side, sold: own(f.px), qty: newQ, late: true }); } } catch (e) {} }   // the sell may have filled in the last seconds
    if (rec._sold >= rec.qty) { rec.exit = 'sold at ' + Math.round(SELL * 100) + '¢'; rec.sellPx = rec._proceeds / rec._sold; rec.pnl = +(rec._proceeds - rec._cost).toFixed(2); log('round', { slug: rec.slug, exit: rec.exit, pnl: rec.pnl, late: true }); save(); report(); return; }
    const m = await ex.market(rec.slug); const apt = (m && (m.assetPriceTerms || (m.market && m.market.assetPriceTerms))) || {};
    const sp = amt(apt.settlementPrice), ptb = amt(apt.priceToBeat);
    if (Number.isFinite(sp) && Number.isFinite(ptb)) { const result = sp >= ptb ? 'UP' : 'DOWN'; const won = result === rec.side; const left = rec.qty - rec._sold;
      rec.exit = (rec._sold ? rec._sold + ' sold at ' + Math.round(SELL * 100) + '¢ + ' : '') + left + (won ? ' won at the bell' : ' lost at the bell'); rec.pnl = +(rec._proceeds + (won ? left : 0) - rec._cost).toFixed(2); rec.result = result;
      log('settle', { slug: rec.slug, result, side: rec.side, qty: left, pnl: rec.pnl }); save(); report(); return; }
  }
  log('warn', { slug: rec.slug, settlement: 'not seen in 20 min' });
}

// ---- main
(async () => {
  log('start', { mode: state.mode, market: PREFIX, buy: BUY, ladder: [LO, HI], sell: SELL, qty: QTY, noBuyLeft: NOBUY_LEFT, node: process.version });
  if (!DRY) { try { const b = await ex.balance(); if (state.balanceStart == null) state.balanceStart = b.total; state.balanceNow = b.total; log('balance', b); } catch (e) { console.error('cannot read the account — stopping', e.message); process.exit(2); } }
  if (!DRY) { try {   // a previous run's resting buys (it logs every one) must not outlive it: cancel any rested in the last 16 minutes
    const lines = fs.readFileSync(logPath, 'utf8').trim().split('\n').slice(-400); const cut = Date.now() - 16 * 60000;
    for (const l of lines) { let r; try { r = JSON.parse(l); } catch (e) { continue; } if (r.k === 'rest' && r.d && r.d.at != null && r.t > cut && r.d.id && !String(r.d.id).startsWith('dry-')) { try { await ex.cancel(r.d.id, r.d.slug); log('cancel', { side: r.d.side, id: r.d.id, why: 'left by the previous run' }); } catch (e) {} }
      if (r.k === 'ladder' && r.t > cut) { for (const id of r.d.ids || []) { try { await ex.cancel(id, r.d.slug); } catch (e) {} } log('cancel', { ladder: (r.d.ids || []).length, why: 'left by the previous run' }); } }
  } catch (e) {} }
  const deadline = MINUTES ? Date.now() + MINUTES * 60000 : Infinity;
  const stop = async () => { log('stop', {}); if (!DRY && live.ids) for (const side of ['UP', 'DOWN']) for (const r of (live.ids[side] || [])) if (!r.done) { try { await ex.cancel(r.id, live.slug); } catch (e) {} }   // resting buys die with the run; a resting sell stays with the exchange
    report(); save(); process.exit(0); };
  process.on('SIGTERM', stop); process.on('SIGINT', stop);
  setInterval(async () => { if (!DRY) { try { const b = await ex.balance(); state.balanceNow = b.total; } catch (e) {} } report(); save(); }, 60000);
  setInterval(async () => { if (!live.slug) return; const b = await ex.book(live.slug); tailPush({ t: Date.now(), k: 'snap', d: { bot: 'E', slug: live.slug, r: Math.max(0, Math.round(live.T - Date.now() / 1000)), upAsk: b ? b.upAsk : NaN, dnAsk: b && Number.isFinite(b.upBid) ? +(1 - b.upBid).toFixed(2) : NaN, resting: live.resting, held: live.held } }); flushTail(); }, 10000);
  let first = true;
  while (Date.now() < deadline) {
    const now = Date.now() / 1000, T0 = Math.floor(now / ROUND) * ROUND;
    if (now - T0 < 3) await sleep(3000);
    if (now > T0 + ROUND - 30 || (first && now - T0 > 60)) {           // too late in this round — or a fresh run joining one mid-way, where a bid at BUY would cross a lopsided book: wait for the next open
      if (first) { log('round', { slug: SLUG(T0), skipped: 'joined mid-round — waiting for the next open' }); first = false; }
      const nextOpen = T0 + ROUND; await sleep(Math.max(1000, (nextOpen - Date.now() / 1000 + 2) * 1000)); continue; }
    first = false;
    await playRound(T0);
    const next = T0 + ROUND;                                              // the round after the one just played (never computed from the clock: the wrap-up can cross the boundary and would skip a round)
    const wait = (next - Date.now() / 1000 + 2) * 1000; if (wait > 0) await sleep(wait);
  }
  stop();
})().catch(e => { console.error(e); process.exit(1); });
