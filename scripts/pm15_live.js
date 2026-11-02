#!/usr/bin/env node
// PM15 live trader ("Mr. P live"): runs the cockpit page UNMODIFIED in Node — the same brain the phone shows — and executes
// only its STRICT ACTION commands on Polymarket US: one BUY of the discounted favorite per round, one SELL per position.
//
//   node scripts/pm15_live.js research/pm15_copilot.html                # live (needs POLYMARKET_KEY_ID / POLYMARKET_SECRET_KEY)
//   node scripts/pm15_live.js research/pm15_copilot.html --dry          # live feeds and decisions, no orders
//   node scripts/pm15_live.js research/pm15_copilot.html --replay btc15_windows.json [--days 2026-11-01]   # offline, mock exchange
//
// Env: MRP_LIVE_CAPITAL (default 20 — the most that can ever be at risk), MRP_LIVE_DIR (logs + LIVE.md, default ./mrplive),
//      MRP_LIVE_MINUTES (stop after N minutes; default run until SIGTERM). Every decision, order, fill and settlement is logged
//      as JSONL and summarised in LIVE.md; the page's own guards (feeds fresh, target exact, book fresh) gate every order.
'use strict';
const fs = require('fs'), vm = require('vm'), path = require('path'), crypto = require('crypto');
const args = process.argv.slice(2);
const PAGE = args.find(a => a.endsWith('.html')) || 'research/pm15_copilot.html';
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const DRY = args.includes('--dry'), REPLAY = opt('replay', null), DAYS = opt('days', null) ? opt('days').split(',') : null;
const CAP = Math.max(1, Number(process.env.MRP_LIVE_CAPITAL || 20));
const DIR = process.env.MRP_LIVE_DIR || 'mrplive';
const MINUTES = Number(process.env.MRP_LIVE_MINUTES || opt('minutes', 0)) || 0;
const KEY_ID = process.env.POLYMARKET_KEY_ID || '', SECRET = process.env.POLYMARKET_SECRET_KEY || '';
const API = 'https://api.polymarket.us', GATEWAY = 'https://gateway.polymarket.us';
const FEE = 0.0695, fee = p => FEE * p * (1 - p);
fs.mkdirSync(DIR, { recursive: true });

// ---------------------------------------------------------------- log + state
const logPath = path.join(DIR, 'live.jsonl'), statePath = path.join(DIR, 'state.json');
let state = { startedAt: Date.now(), capital: CAP, mode: REPLAY ? 'replay' : DRY ? 'dry' : 'live', trades: [], cmds: 0, skips: {}, errors: 0, balanceStart: null, balanceNow: null, pos: null, order: null, shortConv: null };
try { if (!REPLAY) { const prev = JSON.parse(fs.readFileSync(statePath, 'utf8')); if (prev.mode === state.mode) Object.assign(state, prev); } } catch (e) {}   // a dry run's counters never carry into a live run
const tail = []; let tailDirty = false, tailAt = 0;
const tailPush = rec => { tail.push(rec); if (tail.length > 150) tail.shift(); tailDirty = true; };
const flushTail = () => { if (!tailDirty || Date.now() - tailAt < 2000) return; tailDirty = false; tailAt = Date.now(); try { const tmp = path.join(DIR, 'tail.tmp'); fs.writeFileSync(tmp, tail.map(r => JSON.stringify(r)).join('\n') + '\n'); fs.renameSync(tmp, path.join(DIR, 'tail.jsonl')); } catch (e) {} };
const log = (k, d) => { const rec = { t: now(), k, d }; fs.appendFileSync(logPath, JSON.stringify(rec) + '\n'); if (k !== 'tick') console.log(new Date(rec.t).toISOString(), k, JSON.stringify(d).slice(0, 300)); tailPush(rec); };
const saveState = () => { try { fs.writeFileSync(statePath, JSON.stringify(state, null, 1)); } catch (e) {} };
const skip = why => { state.skips[why] = (state.skips[why] || 0) + 1; log('skip', { why }); };

// ---------------------------------------------------------------- clock (real, or the replay's)
let fakeNow = 0; const now = () => REPLAY ? fakeNow : Date.now();

// ---------------------------------------------------------------- exchange: Ed25519 auth, REST
function authHeaders(method, p) {
  const ts = String(Date.now()); let seed = Buffer.from(SECRET, 'base64'); if (seed.length === 64) seed = seed.subarray(0, 32);
  const key = crypto.createPrivateKey({ key: Buffer.concat([Buffer.from('302e020100300506032b657004220420', 'hex'), seed]), format: 'der', type: 'pkcs8' });
  return { 'X-PM-Access-Key': KEY_ID, 'X-PM-Timestamp': ts, 'X-PM-Signature': crypto.sign(null, Buffer.from(ts + method + p), key).toString('base64') };
}
async function api(method, p, body, query) {
  const url = API + p + (query ? '?' + new URLSearchParams(query) : '');
  const r = await fetch(url, { method, headers: { 'Content-Type': 'application/json', 'User-Agent': 'pm15-live/1.0', ...authHeaders(method, p) }, body: body ? JSON.stringify(body) : undefined });
  const txt = await r.text(); let j; try { j = JSON.parse(txt); } catch (e) { j = { raw: txt }; }
  if (!r.ok) { const err = new Error(method + ' ' + p + ' -> HTTP ' + r.status + ' ' + txt.slice(0, 400)); err.status = r.status; err.body = j; throw err; }
  return j;
}
const amt = v => v && typeof v === 'object' ? Number(v.value) : Number(v);
const money = v => ({ value: (Math.round(v * 100) / 100).toFixed(2), currency: 'USD' });

// the live exchange (or the replay's mock, below)
const live = {
  async balances() { const j = await api('GET', '/v1/account/balances'); const b = (j.balances && j.balances[0]) || j; return { cash: Number(b.buyingPower ?? b.currentBalance ?? NaN), total: Number(b.currentBalance ?? NaN), raw: b }; },
  async position(slug) { const j = await api('GET', '/v1/portfolio/positions', null, { market: slug }); const p = j.positions && (j.positions[slug] || Object.values(j.positions)[0]); return p ? { net: Number(p.netPositionDecimal ?? p.netPosition ?? 0), avail: Number(p.qtyAvailableDecimal ?? p.qtyAvailable ?? 0), avgPx: amt(p.avgPx), expired: !!p.expired, realized: amt(p.realized), raw: p } : null; },
  async place(o) { return api('POST', '/v1/orders', o); },
  async order(id) { for (let i = 0; i < 4; i++) { try { const j = await api('GET', '/v1/order/' + id); return j.order || j; } catch (e) { if (!(e.status === 404 && i < 3)) throw e; await sleep(350); } } },
  async cancel(id, slug) { try { await api('POST', '/v1/order/' + id + '/cancel', { marketSlug: slug }); } catch (e) { if (!/HTTP 4/.test(e.message)) throw e; } },
  async cancelAll() { try { return await api('POST', '/v1/orders/open/cancel', {}); } catch (e) { log('warn', { cancelAll: e.message }); } },
  async preview(o) { return api('POST', '/v1/order/preview', { request: o }); }
};

// ---------------------------------------------------------------- the page, running in Node
const els = {};
const mkEl = id => ({ id, textContent: '', innerHTML: '', className: '', hidden: false, value: '', title: '', style: {}, dataset: {}, options: [], selectedIndex: 0,
  lastChild: { textContent: '' }, classList: { add() {}, toggle() {}, remove() {} }, onclick: null, parentElement: { clientWidth: 800, clientHeight: 300 },
  getContext: () => new Proxy({}, { get: (t, k) => (k === 'measureText' ? () => ({ width: 10 }) : () => {}) }), width: 0, height: 0, insertAdjacentHTML() {}, addEventListener() {} });
const document = { getElementById: id => els[id] || (els[id] = mkEl(id)), querySelectorAll: () => [], querySelector: () => mkEl('x'), addEventListener() {}, hidden: false, title: '', activeElement: null };
const store = {}; const localStorage = { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } };
const ctxObj = {
  document, localStorage, console, Intl, Math, Number, JSON, Map, Set, Array, Object, String, Promise, Error, TypeError, RegExp, parseFloat, parseInt, isFinite, isNaN, Infinity, NaN, undefined,
  URL, URLSearchParams, AbortController, TextDecoder, TextEncoder, encodeURIComponent, decodeURIComponent,
  window: { devicePixelRatio: 1, addEventListener() {}, __noBotLog: true }, navigator: {}, location: { href: 'https://pm15-relay-worker.machwonder.workers.dev/' },
  performance: { now: () => Number(process.hrtime.bigint() / 1000000n) }
};
if (REPLAY) {   // frozen clock, no feeds, no timers: the harness drives every second
  ctxObj.Date = Object.assign(function (...a) { return a.length ? new Date(...a) : new Date(fakeNow); }, { now: () => fakeNow, parse: Date.parse, UTC: Date.UTC }); ctxObj.Date.prototype = Date.prototype;
  Object.assign(ctxObj, { setInterval: () => 0, setTimeout: () => 0, clearTimeout() {}, clearInterval() {}, fetch: () => Promise.reject(new TypeError('Failed to fetch')), WebSocket: class { constructor() { this.readyState = 1; } send() {} close() {} } });
} else {        // real clock, real Coinbase WebSocket, real gateway fetches (direct, no relay)
  Object.assign(ctxObj, { Date, setInterval, setTimeout, clearTimeout, clearInterval, fetch, WebSocket });
}
const ctx = vm.createContext(ctxObj);
const html = fs.readFileSync(PAGE, 'utf8');
vm.runInContext(html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>')), ctx, { filename: 'pm15_copilot.js' });
const run = code => vm.runInContext(code, ctx);
// settings for the bot: direct gateway, no sound, the stake is the capital (the 8c+ edge doubles the base, so base = half)
run(`S.relay = 'direct'; S.sound = false; S.voice = false; S.stake = ${(CAP / 2).toFixed(2)}; S.paperOn = 'edge';`);
run('pmFetchBook = async function () {};');                      // the book comes from the exchange WebSocket (or the replay)
run('__setBook = b => { R.book = b; R.bookAt = Date.now(); R.apiOk = true; };');
run('__setPos = p => { myPos = p; R.traded = !!p || R.traded; };');
run('__setTraded = v => { R.traded = v; };');
const setBook = run('__setBook'), setPos = run('__setPos'), setTraded = run('__setTraded');

// ---------------------------------------------------------------- the exchange book: WebSocket on the live market
let ws = null, wsSlug = '';
function connectBookWS(slug) {
  if (REPLAY || !KEY_ID) return;
  if (ws && wsSlug === slug) return;
  try { if (ws) ws.close(); } catch (e) {}
  wsSlug = slug;
  const WSImpl = require('ws'); const p = '/v1/ws/markets';
  ws = new WSImpl('wss://api.polymarket.us' + p, { headers: authHeaders('GET', p) });
  ws.on('open', () => { ws.send(JSON.stringify({ subscribe: { requestId: 'md-' + Date.now(), subscriptionType: 'SUBSCRIPTION_TYPE_MARKET_DATA', marketSlugs: [slug] } })); log('ws', { open: slug }); });
  ws.on('message', m => { try { const j = JSON.parse(m.toString()); const md = j.marketData || j.marketDataLite; if (md && md.marketSlug === slug) setBook(topOf(md)); } catch (e) {} });
  ws.on('close', () => { log('ws', { close: slug }); if (wsSlug === slug) setTimeout(() => { if (wsSlug === slug) { ws = null; connectBookWS(slug); } }, 2000); });
  ws.on('error', e => log('ws', { error: String(e).slice(0, 200) }));
}
function topOf(md) {
  const lv = a => (a || []).map(e => [Number(e.px && e.px.value != null ? e.px.value : e.px), Number(e.qty)]).filter(x => Number.isFinite(x[0]) && x[1] > 0);
  const offers = lv(md.offers).sort((a, b) => a[0] - b[0]), bids = lv(md.bids).sort((a, b) => b[0] - a[0]);
  return { upAsk: offers.length ? offers[0][0] : NaN, upBid: bids.length ? bids[0][0] : NaN, upAskQty: offers.length ? offers[0][1] : 0, upBidQty: bids.length ? bids[0][1] : 0 };
}
// REST top of book as a fallback for the WebSocket (public gateway)
async function restBook(slug) { try { const r = await fetch(GATEWAY + '/v1/markets/' + slug + '/book'); const j = await r.json(); return topOf(j.marketData || j); } catch (e) { return null; } }

// ---------------------------------------------------------------- order semantics
// The market's instrument is "Up". BUY UP = BUY_LONG at the Up ask. DOWN = the short side; whether the exchange quotes a short
// at its own price (1 - Up bid) or at the Up price is checked once with a preview before any DOWN order (state.shortConv).
const intentFor = (side, kind) => side === 'UP' ? (kind === 'buy' ? 'ORDER_INTENT_BUY_LONG' : 'ORDER_INTENT_SELL_LONG') : (kind === 'buy' ? 'ORDER_INTENT_BUY_SHORT' : 'ORDER_INTENT_SELL_SHORT');
const pxFor = (side, px) => side === 'UP' ? px : (state.shortConv === 'up' ? 1 - px : px);     // px is always the side's own price (Down = 1 - Up bid)
async function detectShortConvention(slug, book) {
  if (state.shortConv || DRY || REPLAY) return state.shortConv || 'own';
  const askDown = Number.isFinite(book.upBid) ? Math.round((1 - book.upBid) * 100) / 100 : 0.5;
  try {
    const j = await live.preview({ marketSlug: slug, intent: 'ORDER_INTENT_BUY_SHORT', type: 'ORDER_TYPE_LIMIT', price: money(askDown), quantity: 1, tif: 'TIME_IN_FORCE_GOOD_TILL_CANCEL' });
    const o = j.order || j, cash = amt(o.cashOrderQty), px = amt(o.price);
    let conv = null;
    if (Number.isFinite(cash) && cash > 0) conv = Math.abs(cash - askDown) <= Math.abs(cash - (1 - askDown)) ? 'own' : 'up';
    log('preview', { askDown, px, cash, conv, raw: JSON.stringify(o).slice(0, 400) });
    state.shortConv = conv; saveState(); return conv;
  } catch (e) { log('preview', { error: e.message.slice(0, 300) }); return null; }
}

// ---------------------------------------------------------------- the replay's mock exchange
const mock = { cash: CAP, pos: null, orders: {}, n: 0, book: null,
  async balances() { return { cash: this.cash, total: this.cash + (this.pos ? this.pos.qty * this.pos.px : 0) }; },
  async position() { return this.pos ? { net: this.pos.qty, avail: this.pos.qty, avgPx: this.pos.px } : null; },
  async place(o) { const id = 'm' + (++this.n); const px = amt(o.price), q = Number(o.quantity), b = this.book || {};
    const side = o.intent.includes('LONG') ? 'UP' : 'DOWN', buy = o.intent.includes('BUY');
    const ask = side === 'UP' ? b.upAsk : 1 - b.upBid, bid = side === 'UP' ? b.upBid : 1 - b.upAsk, qty = buy ? (side === 'UP' ? b.upAskQty : b.upBidQty) : (side === 'UP' ? b.upBidQty : b.upAskQty);
    const fillPx = buy ? (Number.isFinite(ask) && ask <= px + 1e-9 ? ask : NaN) : (Number.isFinite(bid) && bid >= px - 1e-9 ? bid : NaN);
    const filled = Number.isFinite(fillPx) ? Math.min(q, Math.floor(qty)) : 0;
    const ord = { id, state: filled >= q ? 'ORDER_STATE_FILLED' : filled > 0 ? 'ORDER_STATE_PARTIALLY_FILLED' : (o.tif === 'TIME_IN_FORCE_IMMEDIATE_OR_CANCEL' ? 'ORDER_STATE_CANCELED' : 'ORDER_STATE_NEW'), cumQuantity: filled, avgPx: money(filled ? fillPx : 0), quantity: q };
    if (filled) { if (buy) { this.cash -= filled * (fillPx + fee(fillPx)); this.pos = { side, qty: filled, px: fillPx }; } else { this.cash += filled * (fillPx - fee(fillPx)); this.pos = this.pos && this.pos.qty > filled ? { ...this.pos, qty: this.pos.qty - filled } : null; } }
    this.orders[id] = ord; return { id, executions: [] }; },
  async order(id) { return this.orders[id]; }, async cancel(id) { const o = this.orders[id]; if (o && o.state === 'ORDER_STATE_NEW') o.state = 'ORDER_STATE_CANCELED'; }, async cancelAll() {}, async preview() { return {}; },
  settle(result) { if (!this.pos) return 0; const won = this.pos.side === result; const pnl = (won ? this.pos.qty : 0) - this.pos.qty * this.pos.px; this.cash += won ? this.pos.qty : 0; this.pos = null; return pnl; }
};
const ex = REPLAY ? mock : live;

// ---------------------------------------------------------------- execution of a STRICT ACTION command
let busy = false, lastCmdSince = 0;
function guards(E) {
  if (!(E && E.r > 0)) return 'round over';
  if (!E.fresh) return 'coinbase stale';
  if (!(run('IDX.ok') === true) || !(E.pmAge <= 12)) return 'index series stale';
  const src = run('R.targetSrc'); if (src !== 'api' && src !== 'series') return 'target not exact';
  const age = (now() - run('R.bookAt')) / 1000; if (!run('R.book') || age > 3) return 'book stale';
  return null;
}
async function onBuy(cmd, E) {
  const slug = run('R.slug'), T0 = run('R.T0');
  if (state.pos) return skip('already in a position');
  const bal = await ex.balances(); state.balanceNow = bal.total;
  const avail = Math.min(CAP, Number.isFinite(bal.cash) ? bal.cash : 0);
  const px = cmd.px, qty = Math.floor(avail / (px + fee(px)));   // sized at the LTE price so the cap holds even if the fill walks up to it
  if (qty < 1) return skip('no cash (' + avail.toFixed(2) + ')');
  if (cmd.side === 'DOWN' && !REPLAY && !DRY) { const conv = await detectShortConvention(slug, run('R.book')); if (!conv) return skip('DOWN convention unknown — UP only'); }
  const payUpTo = Number.isFinite(cmd.ask) ? Math.min(px, cmd.ask + 0.01) : px;   // the ask plus a cent, never above the LTE price: no chasing a market that is running away
  const o = { marketSlug: slug, intent: intentFor(cmd.side, 'buy'), type: 'ORDER_TYPE_LIMIT', price: money(pxFor(cmd.side, payUpTo)), quantity: qty, tif: 'TIME_IN_FORCE_GOOD_TILL_CANCEL' };
  log('order', { kind: 'buy', side: cmd.side, lim: px, ask: cmd.ask, qty, usd: +(qty * px).toFixed(2), edge: cmd.edge, p: cmd.p, left: Math.round(E.r), dry: DRY, o });
  if (DRY) return;
  let res; try { res = await ex.place(o); } catch (e) { state.errors++; return log('error', { place: e.message.slice(0, 400) }); }
  const id = res.id || (res.order && res.order.id); state.order = { id, slug, kind: 'buy', side: cmd.side, px, qty, at: now() }; saveState();
  // watch the order for the action window, then cancel what is left
  const windowMs = (run('S.actWindow') || 15) * 1000; let filled = 0, avg = NaN;
  for (let i = 0; i < 60; i++) {
    let ord; try { ord = await ex.order(id); } catch (e) { log('warn', { order: e.message.slice(0, 200) }); }
    if (ord) { filled = Number(ord.cumQuantity || 0); avg = amt(ord.avgPx); if (/FILLED$|CANCELED|REJECTED|EXPIRED/.test(ord.state || '') && ord.state !== 'ORDER_STATE_PARTIALLY_FILLED') break; }
    if (now() - state.order.at > windowMs) { await ex.cancel(id, slug); log('order', { cancel: id, filled }); break; }
    if (REPLAY) break; await sleep(1000);
  }
  state.order = null;
  if (filled > 0) {
    const price = Number.isFinite(avg) && avg > 0 ? (cmd.side === 'UP' ? avg : (state.shortConv === 'up' ? 1 - avg : avg)) : px;
    state.pos = { slug, T0, side: cmd.side, qty: filled, px: price, spent: +(filled * price).toFixed(2), at: now(), left: Math.round(E.r) };
    setPos({ T0, side: cmd.side, price, spent: state.pos.spent, shares: filled });
    state.trades.push({ T0, slug, side: cmd.side, buyPx: price, qty: filled, spent: state.pos.spent, buyLeft: Math.round(E.r), p: cmd.p, edge: cmd.edge });
    log('fill', { kind: 'buy', side: cmd.side, px: price, qty: filled, usd: state.pos.spent });
  } else { setTraded(false); log('order', { unfilled: id }); }
  saveState();
}
async function onSell(cmd, E) {
  if (!state.pos) return skip('no position to sell');
  const slug = state.pos.slug, side = state.pos.side;
  const windowMs = (run('S.actWindow') || 15) * 1000, t0 = now(); let filled = 0, avg = NaN, tries = 0;
  while (now() - t0 <= windowMs && filled < state.pos.qty && tries < 20) {
    tries++; const b = run('R.book') || {}; const bid = side === 'UP' ? b.upBid : 1 - b.upAsk;
    if (!Number.isFinite(bid)) { if (REPLAY) break; await sleep(1000); continue; }
    const px = cmd.now ? Math.max(0.01, bid - 0.02 * Math.min(3, tries - 1)) : cmd.px;      // SELL NOW chases the bid down a little; a harvest sells only at or above its line
    if (!cmd.now && bid < px - 1e-9) { if (REPLAY) break; await sleep(1000); continue; }
    let qty = state.pos.qty - filled;
    if (!REPLAY) { const ep = await ex.position(slug).catch(() => null); if (ep) { const held = side === 'UP' ? ep.avail : -ep.avail; if (!(held > 0)) { log('order', { nothingHeld: ep.raw ? { net: ep.net, avail: ep.avail } : null }); filled = state.pos.qty; break; } qty = Math.min(qty, held); } }
    const o = { marketSlug: slug, intent: intentFor(side, 'sell'), type: 'ORDER_TYPE_LIMIT', price: money(pxFor(side, px)), quantity: qty, tif: 'TIME_IN_FORCE_IMMEDIATE_OR_CANCEL' };
    log('order', { kind: 'sell', side, px, bid, qty: o.quantity, now: cmd.now, left: Math.round(E.r), dry: DRY, o });
    if (DRY) return;
    let res; try { res = await ex.place(o); } catch (e) { state.errors++; log('error', { place: e.message.slice(0, 400) }); if (REPLAY) break; await sleep(1000); continue; }
    const id = res.id || (res.order && res.order.id); await sleep(REPLAY ? 0 : 400);
    let ord; try { ord = await ex.order(id); } catch (e) {}
    if (ord) { const f = Number(ord.cumQuantity || 0); if (f > 0) { avg = Number.isFinite(avg) ? (avg * filled + amt(ord.avgPx) * f) / (filled + f) : amt(ord.avgPx); filled += f; } }
    if (REPLAY) break;
  }
  if (filled > 0) {
    const price = Number.isFinite(avg) && avg > 0 ? (side === 'UP' ? avg : (state.shortConv === 'up' ? 1 - avg : avg)) : NaN;
    const t = state.trades[state.trades.length - 1]; const proceeds = filled * (price - fee(price));
    if (t && t.T0 === state.pos.T0) {   // sells accumulate (thin books fill in pieces); P&L = proceeds so far minus the cost of what was sold
      const sq = (t.sellQty || 0) + filled; t.sellPx = ((t.sellPx || 0) * (t.sellQty || 0) + price * filled) / sq; t.sellQty = sq; t.proceeds = +((t.proceeds || 0) + proceeds).toFixed(2); t.sellLeft = Math.round(E.r);
      t.pnl = +(t.proceeds - t.spent * (sq / t.qty)).toFixed(2); t.exit = (t.exit && t.exit !== 'harvest' && t.exit !== 'SELL NOW' ? t.exit + ' + ' : '') + (cmd.now ? 'SELL NOW' : 'harvest') + (sq < t.qty ? ' (part)' : ''); }
    log('fill', { kind: 'sell', side, px: price, qty: filled, proceeds: +proceeds.toFixed(2) });
    if (!REPLAY) { const ep = await ex.position(slug).catch(() => null); log('position', ep ? { net: ep.net, avail: ep.avail, avgPx: ep.avgPx } : { none: true }); }
    if (filled >= state.pos.qty - 1e-9) { state.pos = null; setPos(null); } else { state.pos.qty -= filled; setPos({ T0: state.pos.T0, side, price: state.pos.px, spent: state.pos.qty * state.pos.px, shares: state.pos.qty }); }
  } else log('order', { unfilledSell: true });
  saveState();
}
async function onCommand(cmd, E) {
  if (busy) return; busy = true;
  try {
    state.cmds++; log('cmd', { kind: cmd.kind, text: cmd.text, side: cmd.side, px: cmd.px, sh: cmd.sh, left: Math.round(E.r) });
    const g = guards(E); if (g) return skip(g);
    if (cmd.kind === 'buy') await onBuy(cmd, E); else if (cmd.kind === 'sell') await onSell(cmd, E);
  } catch (e) { state.errors++; log('error', { cmd: e.message.slice(0, 400) }); }
  finally { busy = false; saveState(); }
}
// settle a held position at the bell (the page knows the result from the index series ~1 s after)
let settledT0 = 0;
async function settleIfDone() {
  if (!state.pos || state.pos.T0 === settledT0) return;
  const h = run('history.slice(-3)').find(x => x.T0 === state.pos.T0 && x.result);
  if (!h) return;
  settledT0 = state.pos.T0;
  const won = h.result === state.pos.side; const pnl = (won ? state.pos.qty : 0) - state.pos.spent;   // state.pos holds what is still open
  const t = state.trades[state.trades.length - 1]; if (t && t.T0 === state.pos.T0) { t.settle = h.result; t.pnl = +((t.proceeds || 0) + (won ? state.pos.qty : 0) - t.spent).toFixed(2); t.exit = (t.sellQty ? t.exit.replace(' (part)', '') + ' + ' : '') + (won ? 'won at the bell' : 'lost at the bell'); }
  if (REPLAY) mock.settle(h.result);
  log('settle', { T0: state.pos.T0, side: state.pos.side, result: h.result, settle: h.settle, pnl: +pnl.toFixed(2), src: h.settleSrc });
  state.pos = null; setPos(null); saveState();
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

// ---------------------------------------------------------------- the report
function etTime(ms) { return new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }).format(new Date(ms)); }
function report() {
  const tr = state.trades, done = tr.filter(t => t.pnl != null), pnl = done.reduce((s, t) => s + t.pnl, 0), wins = done.filter(t => t.pnl > 0).length;
  const lines = ['# Mr. P — live progress', '', `Mode **${state.mode}** · capital cap **$${CAP}** · started ${etTime(state.startedAt)} ET · updated ${etTime(now())} ET`,
    state.balanceStart != null ? `Account balance: $${Number(state.balanceStart).toFixed(2)} at start → $${Number(state.balanceNow ?? state.balanceStart).toFixed(2)} now · buying power $${Number(state.cashNow ?? state.cashStart ?? 0).toFixed(2)} (the difference is cash held by open orders or positions, the bot's or yours)` : '',
    '', `**Trades ${done.length} closed (${tr.length} opened) · wins ${wins} · P&L from fills ${pnl >= 0 ? '+' : '−'}$${Math.abs(pnl).toFixed(2)}** · strict commands seen ${state.cmds} · skips ${JSON.stringify(state.skips)} · errors ${state.errors}`,
    state.pos ? `Open: ${state.pos.side} ${state.pos.qty} sh @ ${Math.round(state.pos.px * 100)}¢ ($${state.pos.spent}) bought with ${state.pos.left} s left` : 'Open: none', '',
    '| round (ET) | side | buy | qty | $ | exit | sell / settle | P&L |', '|---|---|---|---|---|---|---|---|'];
  for (const t of tr.slice(-60).reverse()) lines.push(`| ${etTime(t.T0 * 1000)} | ${t.side} | ${Math.round(t.buyPx * 100)}¢ @ ${Math.floor(t.buyLeft / 60)}:${String(t.buyLeft % 60).padStart(2, '0')} | ${t.qty} | $${t.spent} | ${t.exit || 'holding'} | ${t.sellPx ? Math.round(t.sellPx * 100) + '¢' : t.settle || '—'} | ${t.pnl != null ? (t.pnl >= 0 ? '+' : '−') + '$' + Math.abs(t.pnl).toFixed(2) : '—'} |`);
  lines.push('', 'Every decision, order, fill and settlement: `live.jsonl` beside this file. The brain is `research/pm15_copilot.html` unmodified; only its STRICT ACTION commands are executed.');
  fs.writeFileSync(path.join(DIR, 'LIVE.md'), lines.join('\n') + '\n');
}

// ---------------------------------------------------------------- main loops
async function liveMain() {
  log('start', { mode: state.mode, cap: CAP, page: PAGE, node: process.version });
  if (!DRY) { try { await live.cancelAll(); } catch (e) {} }
  try { const b = await live.balances(); if (state.balanceStart == null) { state.balanceStart = b.total; state.cashStart = b.cash; } state.balanceNow = b.total; state.cashNow = b.cash; log('balance', { cash: b.cash, total: b.total }); } catch (e) { log('error', { balances: e.message.slice(0, 300) }); if (!DRY) { console.error('cannot read the account — stopping'); process.exit(2); } }
  const deadline = MINUTES ? Date.now() + MINUTES * 60000 : Infinity;
  let lastReport = 0, lastRest = 0, lastSnap = 0;
  setInterval(() => { try { if (run('R.slug')) run('pmFetchSeries()'); } catch (e) {} }, 2000);   // the exact PM line every 2 s (direct gateway; the page's own 10-s cadence was built for the relay budget)
  const stop = async () => { log('stop', {}); try { if (!DRY) await live.cancelAll(); } catch (e) {} report(); saveState(); process.exit(0); };
  process.on('SIGTERM', stop); process.on('SIGINT', stop);
  setInterval(async () => {
    try {
      const E = run('lastEval'); if (!E) return;
      const slug = run('R.slug'); if (slug && slug !== wsSlug) connectBookWS(slug);
      if (Date.now() - lastRest > 5000 && slug && (!run('R.book') || Date.now() - run('R.bookAt') > 3000)) { lastRest = Date.now(); const b = await restBook(slug); if (b) setBook(b); }
      // adopt a position the exchange already holds for this round (restart safety)
      if (!state.pos && !busy && E.r > 0 && E.r % 30 < 0.3 && !DRY) { const p = await live.position(slug).catch(() => null); if (p && p.net > 0 && Number.isFinite(p.avgPx)) { state.pos = { slug, T0: run('R.T0'), side: 'UP', qty: p.net, px: p.avgPx, spent: +(p.net * p.avgPx).toFixed(2), at: Date.now(), left: Math.round(E.r) }; setPos({ T0: run('R.T0'), side: 'UP', price: p.avgPx, spent: state.pos.spent, shares: p.net }); log('adopt', state.pos); } }
      const st = run('strict'); if (st.cmd && st.since !== lastCmdSince) { lastCmdSince = st.since; onCommand(st.cmd, E); }
      await settleIfDone();
      if (Date.now() - lastSnap > 10000) { lastSnap = Date.now(); const b = run('R.book') || {}; const fav = E.fav, favAsk = fav === 'UP' ? b.upAsk : (Number.isFinite(b.upBid) ? 1 - b.upBid : NaN);
        tailPush({ t: Date.now(), k: 'snap', d: { slug, r: Math.round(E.r), key: run('verdict.key'), fav, p: E.pFavAdj, ask: favAsk, lim: E.buyIn ? E.buyIn.lim : NaN, bid: Number.isFinite(b.upBid) ? (fav === 'UP' ? b.upBid : 1 - b.upAsk) : NaN, pos: state.pos ? state.pos.side + ' ' + state.pos.qty + '@' + Math.round(state.pos.px * 100) : null, bookAge: +((Date.now() - run('R.bookAt')) / 1000).toFixed(1), pmAge: E.pmAge, cash: state.cashNow, sig: +Number(E.sig).toFixed(3), sigLive: +Number(E.sigLive).toFixed(3), sigFloor: +Number(E.sigFloor).toFixed(3), off: +Number(E.off).toFixed(2), spot: E.spot, target: E.target } }); }
      flushTail();
      if (Date.now() - lastReport > 60000) { lastReport = Date.now(); if (!DRY) { try { const b = await live.balances(); state.balanceNow = b.total; state.cashNow = b.cash; } catch (e) {} } report(); saveState(); log('tick', { r: Math.round(E.r), key: run('verdict.key'), fav: E.fav, p: E.pFavAdj, book: run('R.book'), pos: state.pos && state.pos.side }); }
      if (Date.now() > deadline) stop();
    } catch (e) { state.errors++; log('error', { loop: e.message.slice(0, 300) }); }
  }, 250);
}
async function replayMain() {
  const D = JSON.parse(fs.readFileSync(REPLAY, 'utf8'));
  const W = D.windows.filter(w => w.print_cov >= 0.98 && w.settle != null && (!DAYS || DAYS.some(d => w.slug.includes(d)))).sort((a, b) => a.T0 - b.T0);
  run(`REC.up = [0, 0.00607, 0.00883, 0.01049, 0.01197, 0.01197, 0.01197, 0.01225, 0.01225, 0.01225, 0.01229, 0.01325, 0.0133, 0.01334, 0.01334, 0.01334];
       REC.dn = [0, 0.00746, 0.00985, 0.01242, 0.013, 0.01445, 0.0169, 0.01932, 0.01984, 0.02081, 0.02081, 0.02118, 0.02118, 0.02119, 0.02323, 0.02553];
       REC.sec = { 5: 0.00313, 10: 0.00357, 15: 0.00481, 30: 0.00588 }; REC.ready = true; REC.at = Date.now(); REC.spans = { m1: 4, m5: 4, m15: 4 };
       REC.bad = { n: 3562, at: 0, med: 0.00011, up: [0.000717, 0.001021, 0.002027, 0.002354, 0.00361], dn: [0.000675, 0.00105, 0.002021, 0.002771, 0.004853] };
       R.offset = 0; R.offsetSrc = 'live'; R.offsetSd = 0;`);
  log('start', { mode: 'replay', rounds: W.length, cap: CAP });
  for (let wi = 0; wi < W.length; wi++) {
    const w = W[wi]; const prints = {}; for (const k in w.prints) prints[Number(k)] = w.prints[k];
    const avg60 = s => { let n = 0, sum = 0; for (let t = s - 59; t <= s; t++) { const v = prints[t]; if (v > 0) { n++; sum += v; } } return n >= 55 ? sum / n : NaN; };
    const book = {}; for (const k in w.book) book[Number(k)] = w.book[k];
    const nearestBook = (sec, tol = 20) => { for (let d = 0; d <= tol; d++) { if (book[sec - d]) return book[sec - d]; if (d && book[sec + d]) return book[sec + d]; } return null; };
    for (let s = w.T0 - 130; s < w.T0; s++) if (prints[s] > 0) run(`secs.set(${s}, ${prints[s]}); if (${s} < firstSec) firstSec = ${s};`);   // the pre-open minute: first PM line and basis
    for (let s = w.T0 - 70; s < w.T0; s++) { const a = avg60(s); if (a > 0) run(`pmA.set(${s}, ${a});`); }
    for (let sec = w.T0; sec <= w.T + 1; sec++) {
      fakeNow = sec * 1000 + 450;
      const v = prints[sec]; if (v > 0) run(`secs.set(${sec}, ${v}); spotNow = ${v}; lastTickMs = ${sec * 1000 + 400};`);
      const a = avg60(sec); if (a > 0) run(`pmA.set(${sec}, ${a}); IDX.ok = true; IDX.at = ${sec * 1000}; IDX.latest = ${sec};`);
      const bk = nearestBook(sec); if (bk) { const b = { upAsk: bk[0] == null ? NaN : bk[0], upBid: bk[2] == null ? NaN : bk[2], upAskQty: bk[1] || 0, upBidQty: bk[3] || 0 }; setBook(b); mock.book = b; } else { run('R.book = null;'); mock.book = null; }
      if (sec === w.T0) { run('evaluate();'); run(`R.target = ${w.ptb}; R.targetSrc = 'api'; R.offset = 0; R.offsetSrc = 'live'; R.offsetSd = 0;`); }
      run('liveRecordCheck(' + sec + ');'); const E = run('evaluate()'); run('dictate(lastEval)');
      const st = run('strict'); if (st.cmd && st.since !== lastCmdSince) { lastCmdSince = st.since; await onCommand(st.cmd, E); }
      await settleIfDone();
    }
    run('finishRound(); settleFromSeries();'); await settleIfDone();
    if (wi % 20 === 0) report();
  }
  report(); const done = state.trades.filter(t => t.pnl != null);
  console.log(JSON.stringify({ rounds: W.length, trades: state.trades.length, closed: done.length, pnl: +done.reduce((s, t) => s + t.pnl, 0).toFixed(2), cashEnd: +mock.cash.toFixed(2), losses: done.filter(t => t.settle && t.pnl < 0).length, skips: state.skips }));
}
(REPLAY ? replayMain() : liveMain()).catch(e => { console.error(e); process.exit(1); });
