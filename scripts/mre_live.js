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
// Env: MRE_DIR (log + MRE.md, default ./mre), MRE_MINUTES (stop after N minutes), MRE_LADDER (default 0.25:0.30, 1¢ rungs), MRE_SELL (0.60, the resting cap), MRE_EXIT_MIN (0.02), MRE_EXIT_STALL (10 s), MRE_EXIT_DROP (0.02), MRE_QTY (shares per rung, 1), MRE_NOBUY_LEFT (540 s),
//      MRE_SLUG_PREFIX (default cpceth-eth-updown-15m- : the ETH 15-minute market; cpc-btc-updown-15m- would be BTC)
'use strict';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const DRY = process.argv.includes('--dry');
const DIR = process.env.MRE_DIR || 'mre'; fs.mkdirSync(DIR, { recursive: true });
const SELL = Number(process.env.MRE_SELL || 0.60), QTY = Number(process.env.MRE_QTY || 1);          // QTY = shares per rung
// the buy ladder: one QTY-share limit at every cent from LO to HI on both sides (MRE_LADDER "lo:hi", default 20¢–30¢; "0.25:0.25" = one price)
const [LO, HI] = String(process.env.MRE_LADDER || '0.25:0.30').split(':').map(Number);
const RUNGS = []; for (let c = Math.round(HI * 100); c >= Math.round(LO * 100); c--) RUNGS.push(c / 100);   // highest first: the price falls into them in this order
const BUY = HI;
// the dynamic exit: once the bid pays more than the average cost + EXIT_MIN after the taker fee, track its high; the first time it
// stops climbing (no new high for EXIT_STALL s) or slips EXIT_DROP under the high, sell everything at the bid. SELL stays resting
// as a cap for a straight run-up (a maker fill, no fee).
const EXIT_MIN = Number(process.env.MRE_EXIT_MIN || 0.02), EXIT_STALL = Number(process.env.MRE_EXIT_STALL || 10), EXIT_DROP = Number(process.env.MRE_EXIT_DROP || 0.02);
const FEE = p => 0.0695 * p * (1 - p);
const EXIT_SLIP = Number(process.env.MRE_EXIT_SLIP || 0.03);   // the exit's second try sells up to this far under the bid (the first try is EXIT_SLIP1 under)
const EXIT_SLIP1 = Number(process.env.MRE_EXIT_SLIP1 || 0.01);
// Nov 3 PM: once armed, a fade sells even if the bid has slid back toward cost (down to EXIT_FLOOR under it, after the fee) —
// a spike that collapses in seconds used to disarm and ride to zero. Below the floor it holds and waits for the next rise.
const EXIT_FLOOR = Number(process.env.MRE_EXIT_FLOOR || 0.02), EXIT_TICK = Number(process.env.MRE_EXIT_TICK || 250);   // ms between exit checks on the WS book
// the exit decision, pure (st = { peak, peakAt }): 'arm' | 'sell' | 'disarm' | null
function exitDecide(st, bid, avg, now) {
  if (!Number.isFinite(bid) || !Number.isFinite(avg)) return null;
  if (st.peak == null) { if (bid - FEE(bid) >= avg + EXIT_MIN) { st.peak = bid; st.peakAt = now; return 'arm'; } return null; }
  if (bid > st.peak + 1e-9) { st.peak = bid; st.peakAt = now; return null; }
  if (now - st.peakAt >= EXIT_STALL * 1000 || bid <= st.peak - EXIT_DROP + 1e-9) {
    if (bid - FEE(bid) >= avg - EXIT_FLOOR) return 'sell';
    st.peak = null; return 'disarm';
  }
  return null;
}
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
  const sold = closed.filter(r => /^sold at/.test(r.exit || '')).length, won = closed.filter(r => / won at the bell$/.test(r.exit) || r.exit === 'won at the bell').length, lost = closed.filter(r => / lost at the bell$/.test(r.exit) || r.exit === 'lost at the bell').length, none = R.filter(r => r.exit === 'no fill').length;
  const lines = ['# Mr. E' + (PREFIX.includes('btc') ? ' (BTC)' : '') + ' — live progress', '', `Market **${PREFIX.replace(/-$/, '')}** · mode **${state.mode}** · rests ${QTY} share at every cent from ${Math.round(LO * 100)}¢ to ${Math.round(HI * 100)}¢ on both sides until ${Math.round(NOBUY_LEFT / 60)}:00 left, sells the first fill at ${Math.round(SELL * 100)}¢ · started ${et(state.startedAt)} ET · updated ${et(Date.now())} ET`,
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
// ---- the live book: the exchange's authenticated market-data WebSocket for the round's market (REST gateway as a fallback)
const WSB = { slug: '', ws: null, top: null, at: 0 };
function wsBook(slug) {
  if (DRY || !KEY_ID) return; if (WSB.ws && WSB.slug === slug) return;
  try { if (WSB.ws) WSB.ws.close(); } catch (e) {}
  WSB.slug = slug; WSB.top = null; WSB.at = 0;
  let WSImpl; try { WSImpl = require('ws'); } catch (e) { return; }
  const p = '/v1/ws/markets'; const w = new WSImpl('wss://api.polymarket.us' + p, { headers: authHeaders('GET', p) }); WSB.ws = w;
  w.on('open', () => w.send(JSON.stringify({ subscribe: { requestId: 'md-' + Date.now(), subscriptionType: 'SUBSCRIPTION_TYPE_MARKET_DATA', marketSlugs: [slug] } })));
  w.on('message', m => { try { const j = JSON.parse(m.toString()); const md = j.marketData || j.marketDataLite; if (!md || md.marketSlug !== slug) return;
    const lv = a => (a || []).map(e => [Number(e.px && e.px.value != null ? e.px.value : e.px), Number(e.qty)]).filter(x => Number.isFinite(x[0]) && x[1] > 0);
    const o = lv(md.offers).sort((a, b) => a[0] - b[0]), b = lv(md.bids).sort((a, b) => b[0] - a[0]);
    if (o.length || b.length) { WSB.top = { upAsk: o.length ? o[0][0] : NaN, upBid: b.length ? b[0][0] : NaN }; WSB.at = Date.now(); } } catch (e) {} });
  w.on('close', () => { if (WSB.ws === w) { WSB.ws = null; setTimeout(() => { if (WSB.slug === slug && !WSB.ws) wsBook(slug); }, 2000); } });
  w.on('error', () => {});
}
const ex = {
  async balance() { const j = await api('GET', '/v1/account/balances'); const b = (j.balances && j.balances[0]) || {}; return { cash: Number(b.buyingPower ?? NaN), total: Number(b.currentBalance ?? NaN) }; },
  async place(o) { if (DRY) { log('dry', o); return { id: 'dry-' + Date.now() }; } return api('POST', '/v1/orders', o); },
  async order(id) { for (let i = 0; i < 4; i++) { try { const j = await api('GET', '/v1/order/' + id); return j.order || j; } catch (e) { if (!(e.status === 404 && i < 3)) throw e; await sleep(400); } } },
  async cancel(id, slug) { if (DRY || !id || id.startsWith('dry-')) return; try { await api('POST', '/v1/order/' + id + '/cancel', { marketSlug: slug }); } catch (e) { if (!/HTTP 4/.test(e.message)) throw e; } },
  async market(slug) { try { const r = await fetch(GATEWAY + '/v1/market/slug/' + slug); return await r.json(); } catch (e) { return null; } },
  async book(slug) { if (WSB.slug === slug && WSB.top && Date.now() - WSB.at < 3000) return { ...WSB.top, src: 'ws' }; if (WSB.slug === slug && WSB.top && Date.now() - WSB.at < 15000) return { ...WSB.top, src: 'ws-quiet' };   // the WS sends on change: a quiet book is still the book
    try { const r = await fetch(GATEWAY + '/v1/markets/' + slug + '/book'); const j = await r.json(); const md = j.marketData || j; const lv = a => (a || []).map(e => [Number(e.px && e.px.value != null ? e.px.value : e.px), Number(e.qty)]).filter(x => Number.isFinite(x[0]) && x[1] > 0); const o = lv(md.offers).sort((a, b) => a[0] - b[0]), b = lv(md.bids).sort((a, b) => b[0] - a[0]); return { upAsk: o.length ? o[0][0] : NaN, upBid: b.length ? b[0][0] : NaN }; } catch (e) { return null; } }
};
// a Down share at price d is a short of the Up contract quoted at 1 − d (the exchange shows a BUY_SHORT as a SELL of Up at the price sent)
const buyOrder = (slug, side, px = BUY) => ({ marketSlug: slug, intent: side === 'UP' ? 'ORDER_INTENT_BUY_LONG' : 'ORDER_INTENT_BUY_SHORT', type: 'ORDER_TYPE_LIMIT', price: money(side === 'UP' ? px : 1 - px), quantity: QTY, tif: 'TIME_IN_FORCE_GOOD_TILL_CANCEL' });
const sellOrder = (slug, side) => ({ marketSlug: slug, intent: side === 'UP' ? 'ORDER_INTENT_SELL_LONG' : 'ORDER_INTENT_SELL_SHORT', type: 'ORDER_TYPE_LIMIT', price: money(side === 'UP' ? SELL : 1 - SELL), quantity: QTY, tif: 'TIME_IN_FORCE_GOOD_TILL_CANCEL' });
const filledOf = async id => { const o = await ex.order(id); if (!o) return { qty: 0 }; const q = Number(o.cumQuantity || 0); const px = amt(o.avgPx); return { qty: q, px: Number.isFinite(px) ? px : NaN, state: o.state || '' }; };

// Nov 3 PM — the momentum filter: rest the ladder only on the side that won the previous round (a dip on the side that has been
// winning tends to bounce; a dip on the side that just lost tends to keep falling). The previous round's winner is read off the
// last WS book of that market (still subscribed at this round's open): Up mid ≥ 80¢ → UP, ≤ 20¢ → DOWN, otherwise unknown
// (then both sides rest, as before). MRE_MOMENTUM=0 turns it off.
const MOMENTUM = process.env.MRE_MOMENTUM !== '0';
function lastWinner(prevSlug, T0) {
  if (WSB.slug !== prevSlug || !WSB.top || WSB.at < (T0 - 120) * 1000) return null;
  const { upBid, upAsk } = WSB.top; const a = Number.isFinite(upAsk), b = Number.isFinite(upBid);
  const mid = a && b ? (upBid + upAsk) / 2 : a ? (upAsk <= 0.05 ? 0 : NaN) : b ? (upBid >= 0.95 ? 1 : NaN) : NaN;
  return mid >= 0.8 ? 'UP' : mid <= 0.2 ? 'DOWN' : null;
}
// ---- one round
// A ladder of resting buys on both sides (QTY shares at every cent from HI down to LO). The first side to fill at all is the
// side; the other ladder is cancelled; this side's rungs keep resting until the no-buy cutoff, so a deeper dip buys cheaper. The
// sell always covers exactly what is held and unsold (re-placed when more is bought); whatever is still held at the bell settles.
// Fills come top-down (the price falls into 30¢ before 29¢), so each tick polls the highest unfilled rung per side, walking down
// while they fill, plus a sweep of every rung every 10 s for anything the walk missed.
async function playRound(T0) {
  const slug = SLUG(T0), T = T0 + ROUND; const rec = { T0, slug, side: null, buyPx: null, buyLeft: null, qty: 0, sold: 0, exit: null, pnl: null }; state.rounds.push(rec); save();
  const prevWin = MOMENTUM ? lastWinner(SLUG(T0 - ROUND), T0) : null;   // read off the WS book before it switches to this round
  const SIDES = prevWin ? [prevWin] : ['UP', 'DOWN']; rec.momentum = prevWin || 'unknown';
  wsBook(slug); const lad = { UP: [], DOWN: [] }; live.slug = slug; live.T = T; live.resting = SIDES.slice(); live.held = null; live.ids = lad;
  for (const sd of SIDES) for (const px of RUNGS) { try { const res = await ex.place({ ...buyOrder(slug, sd, px), quantity: QTY }); lad[sd].push({ id: res.id || (res.order && res.order.id), px, cum: 0, done: false }); } catch (e) { state.errors++; log('error', { place: sd + ' ' + px, msg: e.message.slice(0, 300) }); } }
  log('ladder', { slug, ids: lad.UP.map(r => r.id).concat(lad.DOWN.map(r => r.id)) }); log('rest', { slug, side: prevWin || 'BOTH', momentum: prevWin ? 'last round closed ' + prevWin : 'last close unclear: both sides', at: HI, ladder: Math.round(LO * 100) + '–' + Math.round(HI * 100) + '¢', rungs: RUNGS.length, qty: QTY });
  const own = (side, px) => side === 'UP' ? px : 1 - px;   // order prices come back in Up terms
  let side = null, sold = 0, proceeds = 0, sell = null, buysPulled = false, lastSweep = 0;
  const bought = () => side ? lad[side].reduce((a, r) => a + r.cum, 0) : 0, cost = () => side ? lad[side].reduce((a, r) => a + r.cum * r.px, 0) : 0;
  const check = async (sd, r) => { let f; try { f = await filledOf(r.id); } catch (e) { return 0; } const add = f.qty - r.cum; if (add > 0) { r.cum = f.qty; if (Number.isFinite(f.px) && f.px > 0) r.px = own(sd, f.px); } if (r.cum >= QTY - 1e-9 || /CANCEL|REJECT|EXPIRE/.test(f.state || '')) r.done = true; return add > 0 ? add : 0; };
  const ext = { peak: null, peakAt: 0 }; let lastTry = 0;
  const wsBid = () => { if (WSB.slug !== slug || !WSB.top || Date.now() - WSB.at > 15000) return NaN; return side === 'UP' ? WSB.top.upBid : (Number.isFinite(WSB.top.upAsk) ? +(1 - WSB.top.upAsk).toFixed(2) : NaN); };
  const exitTick = async () => {   // runs every EXIT_TICK ms on the live WS book — no API call unless it sells
    if (+(bought() - sold).toFixed(4) <= 0) return;
    const avg = cost() / bought(); const bid0 = wsBid(); const d = exitDecide(ext, bid0, avg, Date.now());
    if (d === 'arm') log('exit', { slug, side, armed: bid0, avg: +avg.toFixed(3), src: 'ws' });
    if (d === 'disarm') log('exit', { slug, side, disarmed: bid0, avg: +avg.toFixed(3) });
    if (d !== 'sell' || Date.now() - lastTry < 1000) return; lastTry = Date.now();
    if (sell) { await ex.cancel(sell.id, slug); await readSell(); sell = null; }
    for (const slip of [EXIT_SLIP1, EXIT_SLIP]) {
      const q = +(bought() - sold).toFixed(4); if (q <= 0) break;
      const b = wsBid(); if (!Number.isFinite(b)) break; const px = Math.max(0.01, b - slip);
      try { const res = await ex.place({ ...sellOrder(slug, side), price: money(side === 'UP' ? px : 1 - px), quantity: q, tif: 'TIME_IN_FORCE_IMMEDIATE_OR_CANCEL' });
        const id = res.id || (res.order && res.order.id); await sleep(300); let f = null; try { f = await filledOf(id); } catch (e) {}
        const fq = f ? f.qty : 0; const fpx = f && Number.isFinite(f.px) ? own(side, f.px) : b;
        if (fq > 0) { proceeds += fq * (fpx - FEE(fpx)); sold += fq; rec.sold = sold; }
        log('fill', { slug, side, sold: fpx, qty: fq, soldTotal: +sold.toFixed(2), of: +bought().toFixed(2), exit: 'stall', peak: ext.peak, bid: b, slip });
        if (fq > 0 && +(bought() - sold).toFixed(4) <= 0) break; } catch (e) { state.errors++; log('error', { exitSell: e.message.slice(0, 300) }); }
    }
    if (+(bought() - sold).toFixed(4) > 0) await placeSell(); else ext.peak = null;   // whatever did not fill goes back on the cap; still armed, it retries
    save(); };
  const readSell = async () => { if (!sell) return; let f; try { f = await filledOf(sell.id); } catch (e) { return; } const newQ = f.qty - (sold - sell.base); if (newQ > 0) { proceeds += newQ * own(side, f.px); sold += newQ; rec.sold = sold; log('fill', { slug, side, sold: own(side, f.px), qty: newQ, soldTotal: +sold.toFixed(2), of: +bought().toFixed(2) }); } };
  const placeSell = async () => { const q = +(bought() - sold).toFixed(4); if (q <= 0) return; try { const res = await ex.place({ ...sellOrder(slug, side), quantity: q }); sell = { id: res.id || (res.order && res.order.id), qty: q, base: sold }; rec.sellId = sell.id; log('rest', { slug, side, sellAt: SELL, qty: q, id: sell.id }); } catch (e) { state.errors++; log('error', { placeSell: e.message.slice(0, 300) }); } };
  const cancelLadder = async sd => { for (const r of lad[sd]) if (!r.done) { await ex.cancel(r.id, slug); await check(sd, r); r.done = true; } };
  const scan = async () => {   // new fills on the ladder(s): walk each side top-down while rungs are full; every 10 s check every rung
    const sweep = Date.now() - lastSweep > 10000; if (sweep) lastSweep = Date.now();
    for (const sd of (side ? [side] : ['UP', 'DOWN'])) {
      for (const r of lad[sd]) { if (r.done) continue; const add = await check(sd, r); if (add > 0 && !side) side = sd; if (sweep || r.done) continue; break; }
      if (side) break; } };
  while (Date.now() / 1000 < T - 2) {
    for (let i = 0; i < Math.max(1, Math.round(2000 / EXIT_TICK)); i++) { await sleep(EXIT_TICK); if (side && !DRY) await exitTick(); }
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
    await readSell();   // the dynamic exit runs in exitTick, between scans
    const ladderOpen = lad[side].some(r => !r.done);
    if (b > 0 && sold >= b - 1e-9 && !ladderOpen) { rec.exit = 'sold at ' + Math.round(100 * proceeds / sold) + '¢ avg'; rec.sellPx = proceeds / sold; rec.pnl = +(proceeds - cost()).toFixed(2); live.held = null; live.resting = []; log('round', { slug, exit: rec.exit, qty: +sold.toFixed(2), pnl: rec.pnl }); save(); return; }
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
    // the published log lags up to 10 min; the live tail (published every 15 s, MRE_PREV_TAIL) covers a run cancelled mid-round
    let lines = []; try { lines = fs.readFileSync(logPath, 'utf8').trim().split('\n').slice(-400); } catch (e) {}
    try { if (process.env.MRE_PREV_TAIL) lines = lines.concat(fs.readFileSync(process.env.MRE_PREV_TAIL, 'utf8').trim().split('\n')); } catch (e) {}
    const seen = new Set(); lines = lines.filter(l => !seen.has(l) && seen.add(l)); const cut = Date.now() - 16 * 60000;
    for (const l of lines) { let r; try { r = JSON.parse(l); } catch (e) { continue; } if (r.k === 'rest' && r.d && r.d.at != null && r.t > cut && r.d.id && !String(r.d.id).startsWith('dry-')) { try { await ex.cancel(r.d.id, r.d.slug); log('cancel', { side: r.d.side, id: r.d.id, why: 'left by the previous run' }); } catch (e) {} }
      if (r.k === 'ladder' && r.t > cut) { for (const id of r.d.ids || []) { try { await ex.cancel(id, r.d.slug); } catch (e) {} } log('cancel', { ladder: (r.d.ids || []).length, why: 'left by the previous run' }); } }
  } catch (e) {} }
  if (process.argv.includes('--cleanup')) { flushTail && 0; console.log('cleanup done'); process.exit(0); }
  const deadline = MINUTES ? Date.now() + MINUTES * 60000 : Infinity;
  const stop = async () => { log('stop', {}); if (!DRY && live.ids) for (const side of ['UP', 'DOWN']) for (const r of (live.ids[side] || [])) if (!r.done) { try { await ex.cancel(r.id, live.slug); } catch (e) {} }   // resting buys die with the run; a resting sell stays with the exchange
    report(); save(); process.exit(0); };
  process.on('SIGTERM', stop); process.on('SIGINT', stop);
  setInterval(async () => { if (!DRY) { try { const b = await ex.balance(); state.balanceNow = b.total; } catch (e) {} } report(); save(); }, 60000);
  setInterval(async () => { if (!live.slug) return; const b = await ex.book(live.slug); const snap = { t: Date.now(), k: 'snap', d: { bot: 'E', slug: live.slug, r: Math.max(0, Math.round(live.T - Date.now() / 1000)), upAsk: b ? b.upAsk : NaN, dnAsk: b && Number.isFinite(b.upBid) ? +(1 - b.upBid).toFixed(2) : NaN, resting: live.resting, held: live.held } }; tailPush(snap); flushTail();
    try { if (b) fs.appendFileSync(path.join(DIR, 'snaps.jsonl'), JSON.stringify({ t: snap.t, s: live.slug.slice(-16), r: snap.d.r, u: b.upAsk, d: snap.d.dnAsk }) + '\n'); } catch (e) {}   /* the price history the status page charts */ }, 10000);
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
