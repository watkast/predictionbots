#!/usr/bin/env node
// Replay the PM15 cockpit against recorded rounds and simulate a human who trades only on its DO NEXT instruction.
//
//   node scripts/pm15_human_sim.js research/pm15_copilot.html btc15_windows.json [--latency 8] [--stake 20] [--warmup 480]
//
// btc15_windows.json comes from mrp/mrp_extract_btc15.py (Mr. P recorder data: 1-Hz CF Benchmarks prints, the Polymarket
// US book top every second it was seen, the exact price to beat and settlement). The page runs unmodified in a DOM stub:
// the prints are fed to it as the spot feed (basis 0 — the prints ARE the settlement series, so this is Coinbase without
// its ~1 s lead: slightly pessimistic for the human), the 60-print average as the index series, the recorded book as the
// live book. Records and the bad-minute ladder are learned walk-forward from the prints already seen (the live page scans
// five days of Coinbase candles instead); the first --warmup minutes are not scored.
//
// Personas (each run with an obedient seller and an EV seller):
//   lock     buys only on SURE THING (BUY fav <= max), holds; sells when told SELL / SELL NOW
//   ef+lock  also buys the Early Favorite instruction (fav at 80–94c at 13:00 / 12:00 left)
//   row      buys whenever flat and the ask is at or under the next-trade price the row shows (GOOD price / max), plus lock buys
// The human reads an instruction the tick it appears, taps after --latency seconds, and fills against the book at that
// second (best level only; partial fills when the level is thin). Taker fee 0.0695·p·(1−p) per contract both ways.
'use strict';
const fs = require('fs'), vm = require('vm');
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? Number(args[i + 1]) : d; };
const LAT = opt('latency', 8), STAKE = opt('stake', 20), WARM = opt('warmup', 480), TICK = opt('tick', 1), SIGK = opt('sigk', 1.3), QUIET = args.includes('--quiet'), EVNOW = args.includes('--evsellnow'), ETAWARN = opt('etawarn', 30), EXITBY = opt('exitby', 45);
// strategy knobs passed straight into the page's settings (S.*), plus sim-side ones
// (only the knobs given on the command line are overridden; the rest are the page's own defaults, so a plain run tests the page as shipped)
const KN = {}; for (const [flag, key, map] of [['entryedge', 'entryEdge'], ['buymin', 'buyMinLeft'], ['buymax', 'buyMaxLeft'], ['dog', 'dogBuy', v => v >= 1], ['selledge', 'sellEdge'], ['sellzone', 'sellZone'], ['sellpersist', 'sellPersist']]) { const v = opt(flag, NaN); if (Number.isFinite(v)) KN[key] = map ? map(v) : v; }
const PERSIST = opt('persist', 0), SIZE = opt('size', 0), STRICT = opt('strict', 20), ONLY = (i => i >= 0 ? args[i + 1] : '')(args.indexOf('--only')), DAYS = (i => i >= 0 ? args[i + 1].split(',') : null)(args.indexOf('--days')), JSONOUT = args.includes('--json');
const pagePath = args[0], dataPath = args[1];
const html = fs.readFileSync(pagePath, 'utf8');
const script = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));
const DATA = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
const W = DATA.windows.filter(w => w.print_cov >= 0.98 && w.settle != null && (!DAYS || DAYS.some(d => w.slug.includes(d)))).sort((a, b) => a.T0 - b.T0);

// ---------------- DOM / platform stubs ----------------
const els = {};
const mkEl = id => ({ id, textContent: '', innerHTML: '', className: '', hidden: false, value: '', title: '', style: {}, dataset: {},
  lastChild: { textContent: '' }, classList: { add() {}, toggle() {}, remove() {} }, onclick: null, parentElement: { clientWidth: 800, clientHeight: 300 },
  getContext: () => new Proxy({}, { get: (t, k) => (k === 'measureText' ? () => ({ width: 10 }) : () => {}) }), width: 0, height: 0 });
const document = { getElementById: id => els[id] || (els[id] = mkEl(id)), querySelectorAll: () => [], querySelector: () => mkEl('x'), addEventListener() {}, hidden: false };
const store = {}; const localStorage = { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } };
let fakeNow = 0;
const ctxObj = { document, localStorage, console, Intl, Math, Number, JSON, Map, Set, Array, Object, String,
  Date: Object.assign(function (...a) { return a.length ? new Date(...a) : new Date(fakeNow); }, { now: () => fakeNow, parse: Date.parse, UTC: Date.UTC }),
  setInterval: () => 0, clearTimeout() {}, setTimeout: () => 0, fetch: () => Promise.reject(new TypeError('Failed to fetch')),
  WebSocket: class { constructor() { this.readyState = 1; } send() {} close() {} }, window: { devicePixelRatio: 1, addEventListener() {} }, navigator: {},
  location: { href: 'https://pm15-relay-worker.machwonder.workers.dev/' }, Promise, Error, TypeError, RegExp, parseFloat, isFinite, Infinity, NaN, undefined };
ctxObj.Date.prototype = Date.prototype;
const ctx = vm.createContext(ctxObj);
vm.runInContext(script, ctx, { filename: 'cockpit.js' });
const run = code => vm.runInContext(code, ctx);
const G = name => run(name);

// records and the bad-minute ladder measured over the whole recorded set (Oct 29 – Nov 2): what the live page's 5-day Coinbase
// scan would know on the last day — a mild look-ahead for the earlier rounds (it makes LOCKED stricter there, not looser)
run(`REC.up = [0, 0.00607, 0.00883, 0.01049, 0.01197, 0.01197, 0.01197, 0.01225, 0.01225, 0.01225, 0.01229, 0.01325, 0.0133, 0.01334, 0.01334, 0.01334];
     REC.dn = [0, 0.00746, 0.00985, 0.01242, 0.013, 0.01445, 0.0169, 0.01932, 0.01984, 0.02081, 0.02081, 0.02118, 0.02118, 0.02119, 0.02323, 0.02553];
     REC.sec = { 5: 0.00313, 10: 0.00357, 15: 0.00481, 30: 0.00588 }; REC.ready = true; REC.at = Date.now(); REC.spans = { m1: 4, m5: 4, m15: 4 };
     REC.bad = { n: 3562, at: 0, med: 0.00011, up: [0.000717, 0.001021, 0.002027, 0.002354, 0.00361], dn: [0.000675, 0.00105, 0.002021, 0.002771, 0.004853] };
     R.offset = 0; R.offsetSrc = 'live'; R.offsetSd = 0.0; S.latency = ${LAT}; S.sigK = ${SIGK}; S.etaWarnS = ${ETAWARN}; S.exitBy = ${EXITBY}; Object.assign(S, ${JSON.stringify(KN)});`);

// ---------------- walk-forward bad-minute ladder from the prints ----------------
const excUp = [], excDn = [];
let lastMin = null;
function feedMinute(prints, sec) {   // once a minute: prev minute's last print -> extreme within this minute
  const m = Math.floor(sec / 60); if (m === lastMin) return; lastMin = m;
  const base = prints[(m - 1) * 60 + 59] ?? prints[(m - 1) * 60 + 58]; if (!(base > 0)) return;
  let hi = -Infinity, lo = Infinity, n = 0;
  for (let s = m * 60 - 60; s < m * 60; s++) { const v = prints[s]; if (v > 0) { n++; if (v > hi) hi = v; if (v < lo) lo = v; } }
  if (n < 50) return;
  excUp.push((hi - base) / base); excDn.push((base - lo) / base);
}
const q = (a, p) => { const s = a.slice().sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };
function pushLadder() {
  if (excUp.length < 300) { run('REC.bad = null;'); return; }
  const all = excUp.concat(excDn);
  const lad = { n: excUp.length, at: fakeNow, med: q(all, 0.5), up: [0.9, 0.95, 0.99, 0.995, 0.999].map(p => q(excUp, p)), dn: [0.9, 0.95, 0.99, 0.995, 0.999].map(p => q(excDn, p)) };
  run('REC.bad = ' + JSON.stringify(lad) + ';');
}

// ---------------- personas ----------------
const fee = (p) => 0.0695 * p * (1 - p);
const mkPersona = (name, buys, sellMode) => ({ name, buys, sellMode, cash: 0, pos: null, pending: null, trades: [], rounds: 0, equity: [], sells: { saved: 0, savedUsd: 0, soldWinner: 0, soldWinnerUsd: 0, noBid: 0 }, locks: { held: 0, lost: 0 } });
let personas = [];
for (const sm of ['obey', 'ev']) { personas.push(mkPersona('lock/' + sm, ['sure'], sm), mkPersona('ef+lock/' + sm, ['sure', 'ef'], sm), mkPersona('row/' + sm, ['sure', 'ef', 'row'], sm), mkPersona('edge/' + sm, ['sure', 'edge'], sm)); }
if (ONLY) personas = personas.filter(p => p.name === ONLY);
const centsOf = s => { const m = /(\d+(?:\.\d+)?)¢/.exec(s || ''); return m ? Number(m[1]) / 100 : NaN; };

// ---------------- accuracy ledgers (persona-independent) ----------------
const led = { favCal: new Map(), lockCalls: [], holdClaims: [], sellCalls: [], flipAtLeft: new Map(), firstLock: [], dontBuy: [], winnerAsk: [] };
const bucket = p => Math.min(0.99, Math.floor(p * 20) / 20);

// ---------------- the replay ----------------
let scored = 0, warmSecs = 0;
const t0All = W[0].T0 - 130;
let lastKeyFlat = '', lastHead = '';
const started = Date.now();
for (let wi = 0; wi < W.length; wi++) {
  const w = W[wi];
  const prints = {}; for (const k in w.prints) prints[Number(k)] = w.prints[k];
  const book = {}; for (const k in w.book) book[Number(k)] = w.book[k];
  const nearestBook = (sec, tol) => { const T = tol == null ? 20 : tol; for (let d = 0; d <= T; d++) { if (book[sec - d]) return book[sec - d]; if (d && book[sec + d]) return book[sec + d]; } return null; };
  // feed the pre-open minute so the first pmA / basis exist
  for (let s = w.T0 - 130; s < w.T0; s++) if (prints[s] > 0) run(`secs.set(${s}, ${prints[s]}); if (${s} < firstSec) firstSec = ${s};`);
  const avg60 = s => { let n = 0, sum = 0; for (let t = s - 59; t <= s; t++) { const v = prints[t]; if (v > 0) { n++; sum += v; } } return n >= 55 ? sum / n : NaN; };
  for (let s = w.T0 - 70; s < w.T0; s++) { const a = avg60(s); if (a > 0) run(`pmA.set(${s}, ${a});`); }
  const outcome = w.settle >= w.ptb ? 'UP' : 'DOWN';
  const scoring = (w.T0 - t0All) / 60 >= WARM;
  const roundStats = { firstLock: null, sideCush: {} };
  for (const P of personas) { P.pos = null; P.pending = null; P.boughtThisRound = false; P.lastSellLogged = false; }
  let lockAskSeen = null;   // the cheapest ask seen for the locked side after the first lock
  for (let sec = w.T0; sec <= w.T + 1; sec += 1) {
    const v = prints[sec]; if (v > 0) run(`secs.set(${sec}, ${v}); spotNow = ${v}; lastTickMs = ${sec * 1000 + 400};`);
    const a = avg60(sec); if (a > 0) run(`pmA.set(${sec}, ${a}); IDX.ok = true; IDX.at = ${sec * 1000}; IDX.latest = ${sec};`);
    feedMinute(prints, sec);
    const bk = nearestBook(sec);
    if (bk) run(`R.book = { upAsk: ${bk[0] == null ? 'NaN' : bk[0]}, upBid: ${bk[2] == null ? 'NaN' : bk[2]}, upAskQty: ${bk[1] || 0}, upBidQty: ${bk[3] || 0} }; R.bookAt = ${sec * 1000 + 500};`); else run('R.book = null;');
    for (let sub = 0; sub < TICK; sub++) {
      fakeNow = sec * 1000 + 450 + sub * Math.floor(1000 / TICK);
      if (sec === w.T0) { run('evaluate();'); run(`R.target = ${w.ptb}; R.targetSrc = 'api'; R.offset = 0; R.offsetSrc = 'live'; R.offsetSd = 0;`); }
      run('liveRecordCheck(' + sec + ');');
      // ---- each persona sees its own page state (its own position); evaluate once per persona with myPos set
      for (const P of personas) {
        run('myPos = ' + (P.pos ? JSON.stringify({ T0: w.T0, side: P.pos.side, price: P.pos.price, spent: P.pos.spent, shares: P.pos.shares }) : 'null') + '; verdict = ' + JSON.stringify(P.verdict || { key: '', since: 0, pend: '', pendSince: 0 }) + ';');
        const E = run('evaluate()'); run('dictate(lastEval)');
        P.verdict = run('verdict');
        const key = run('verdict.key'), head = els['do-head'].textContent, ntL = els['nt-left'].textContent, ntR = els['nt-right'].textContent;
        const r = E.r;
        // persona-independent ledgers: take them from the first persona (flat view) when it is flat
        if (P === personas[0] && !P.pos && scoring && r > 0) {
          const fav = E.favInfo; if (Number.isFinite(E.pFavAdj)) { const b = bucket(E.pFavAdj), c = led.favCal.get(b) || [0, 0]; c[0]++; if (E.fav === outcome) c[1]++; led.favCal.set(b, c); }
          if (fav.locked) { const askL = bk ? (E.fav === 'UP' ? bk[0] : (bk[2] != null ? 1 - bk[2] : null)) : null; if (!roundStats.firstLock) roundStats.firstLock = { left: r, side: E.fav, ask: askL, cush: fav.cush, rec: fav.rec, bestAsk: null, bestAskLeft: null }; if (askL != null && r > LAT + 2 && (roundStats.firstLock.bestAsk == null || askL < roundStats.firstLock.bestAsk)) { roundStats.firstLock.bestAsk = askL; roundStats.firstLock.bestAskLeft = r; } }
          if (key === 'wait' || key === 'chop') { const m = /for (\d+):(\d+)|for (\d+) s/.exec(head); if (m) led.dontBuy.push({ w: wi, at: r, secs: m[3] ? Number(m[3]) : Number(m[1]) * 60 + Number(m[2]) }); }
          // "HOLD >= N s" claims for the favorite, as if held: verified later against the cushion path
          const hc = fav.holdConf; if (Number.isFinite(hc) && hc > 0 && hc < r && !fav.locked && sec % 5 === 0) led.holdClaims.push({ w: wi, side: E.fav, at: sec, N: hc, cush: fav.cush, left: r });
          roundStats.sideCush[sec] = [E.cushUp, E.cushDn];
          // what the eventual winner cost at each moment, and what the page thought of it then
          if (bk && sec % 5 === 0) { const askW = outcome === 'UP' ? bk[0] : (bk[2] != null ? 1 - bk[2] : null); if (askW != null) { const xi = E.sideInfo(outcome); led.winnerAsk.push({ w: wi, left: r, ask: askW, p: xi.pAdj, favIsWinner: E.fav === outcome, cush: xi.cush }); } }
        }
        if (!scoring || r <= 0) continue;
        // ---- act on pending orders at their fill time
        if (P.pending && sec >= P.pending.at) {
          const o = P.pending; P.pending = null; const b = nearestBook(sec, STRICT);   // the fill needs a quote this fresh
          if (o.kind === 'buy' && b) {
            const ask = o.side === 'UP' ? b[0] : (b[2] != null ? 1 - b[2] : null), qty = o.side === 'UP' ? b[1] : b[3];
            if (ask != null && ask <= o.limit + 1e-9 && qty >= 1) { const sh = Math.min((o.stake || STAKE) / ask, qty); const spent = sh * ask; P.cash -= spent + fee(ask) * sh; P.pos = { side: o.side, price: ask, spent, shares: sh, at: r, key: o.key }; P.boughtThisRound = true; P.trades.push({ w: wi, kind: 'buy', side: o.side, px: ask, sh, left: r, key: o.key }); }
            else P.trades.push({ w: wi, kind: 'nofill', side: o.side, left: r, key: o.key, ask });
          } else if (o.kind === 'sell' && P.pos && b) {
            const bid = P.pos.side === 'UP' ? b[2] : (b[0] != null ? 1 - b[0] : null), qty = P.pos.side === 'UP' ? b[3] : b[1];
            if (bid != null && bid > 0 && qty >= 1) { const sh = Math.min(P.pos.shares, qty); const proceeds = sh * bid - fee(bid) * sh; P.cash += proceeds;
              const wouldWin = P.pos.side === outcome; const holdValue = wouldWin ? sh : 0;
              if (wouldWin) { P.sells.soldWinner++; P.sells.soldWinnerUsd += holdValue - proceeds; } else { P.sells.saved++; P.sells.savedUsd += proceeds; }
              P.trades.push({ w: wi, kind: 'sell', side: P.pos.side, px: bid, sh, left: r, key: o.key, wouldWin });
              P.pos.shares -= sh; if (P.pos.shares < 0.5) P.pos = null; }
            else { P.sells.noBid++; P.trades.push({ w: wi, kind: 'nobid', side: P.pos.side, left: r, key: o.key }); }
          }
        }
        // ---- read the instruction, decide, queue after latency
        if (P.pending) continue;
        if (P.pos && key !== 'sellnow' && key !== 'sell') P.sellRun = 0;
        if (P.pos) {
          if (key === 'sellnow' || key === 'sell') {
            P.sellRun = (P.sellRun || 0) + 1; if (P.sellRun < PERSIST + 1 && key !== 'sellnow') continue;
            const x = run("lastEval.exitCheck('" + P.pos.side + "')");
            const bidNow = Number.isFinite(x.bid) ? x.bid : NaN;
            const go = P.sellMode === 'obey' || (key === 'sellnow' && !EVNOW) || (Number.isFinite(bidNow) && bidNow >= x.sellAbove);
            if (go) P.pending = { kind: 'sell', at: sec + LAT, key };
            if (scoring && !P.lastSellLogged) { led.sellCalls.push({ w: wi, persona: P.name, side: P.pos.side, key, left: r, wouldWin: P.pos.side === outcome, entryKey: P.pos.key, reason: key === 'sellnow' ? 'projected loss' : (x.reason || '').split(/[(:—]/)[0].trim().slice(0, 28) }); P.lastSellLogged = true; }
          }
        } else if (r > LAT + 2 && !P.boughtThisRound) {
          const fav = E.fav;
          if (P.buys.includes('edge') && E.entry && E.entry.qty >= 1) P.pending = { kind: 'buy', side: E.entry.side, limit: E.entry.lim, at: sec + LAT, key: 'edge', stake: SIZE ? Math.min(STAKE * 2, STAKE * Math.max(0.5, E.entry.edge / 0.04)) : STAKE };
          else if (key === 'sure' && P.buys.includes('sure')) P.pending = { kind: 'buy', side: fav, limit: Math.max(centsOf(ntR) || 0, 0.97), at: sec + LAT, key };
          else if (key === 'ef' && P.buys.includes('ef')) P.pending = { kind: 'buy', side: fav, limit: 0.94, at: sec + LAT, key };
          else if (P.buys.includes('row') && (key === 'wait' || key === 'chop' || key === 'ready' || key === 'efcheck')) {
            const lim = centsOf(ntR); const b = nearestBook(sec); const ask = b ? (fav === 'UP' ? b[0] : (b[2] != null ? 1 - b[2] : null)) : null;
            if (Number.isFinite(lim) && ask != null && ask <= lim) P.pending = { kind: 'buy', side: fav, limit: lim, at: sec + LAT, key: 'row' };
          }
        }
      }
    }
  }
  // ---- the bell: settle open positions, judge the ledgers for this round
  for (const P of personas) {
    if (P.pos) { const won = P.pos.side === outcome; P.cash += won ? P.pos.shares : 0; P.trades.push({ w: wi, kind: 'settle', side: P.pos.side, won, sh: P.pos.shares, key: P.pos.key }); if (P.pos.locked) {} P.pos = null; }
    if (scoring) { P.rounds++; P.equity.push(P.cash); }
  }
  if (scoring) {
    scored++;
    if (roundStats.firstLock) { led.firstLock.push({ ...roundStats.firstLock, w: wi, ok: roundStats.firstLock.side === outcome }); }
    const rs = run('lockStats'); // the page's own lock record
    // verify the hold claims of this round against the cushion path
    for (const c of led.holdClaims) if (c.w === wi && c.ok === undefined) { const t2 = c.at + Math.ceil(c.N); const cu = roundStats.sideCush[t2]; c.ok = cu ? (c.side === 'UP' ? cu[0] > 0 : cu[1] > 0) : null; c.won = c.side === outcome; }
    for (const d of led.dontBuy) if (d.w === wi && d.ok === undefined) { d.ok = true; }
  }
  if (!QUIET && wi % 20 === 0) process.stderr.write(`round ${wi + 1}/${W.length} ${w.slug.slice(-22)} ${scoring ? 'scored' : 'warm-up'} ${(Date.now() - started) / 1000 | 0}s\n`);
}

// ---------------- report ----------------
const pct = x => (100 * x).toFixed(1) + '%';
const usd = x => (x >= 0 ? '+$' : '−$') + Math.abs(x).toFixed(2);
if (JSONOUT) { const out = {}; for (const P of personas) { let worst = 0, prev = 0; for (const e of P.equity) { worst = Math.min(worst, e - prev); prev = e; } const buys = P.trades.filter(t => t.kind === 'buy').length, losses = P.trades.filter(t => t.kind === 'settle' && !t.won).length; out[P.name] = { rounds: P.rounds, buys, losses, pnl: +P.cash.toFixed(2), worst: +worst.toFixed(2), saved: +P.sells.savedUsd.toFixed(0), gaveUp: +(-P.sells.soldWinnerUsd).toFixed(0) }; } console.log(JSON.stringify(out)); process.exit(0); }
console.log(`\nPM15 cockpit — human replay   rounds scored ${scored} of ${W.length} (warm-up ${WARM} min)   latency ${LAT} s   stake $${STAKE}   ${W[0].slug.slice(20, 30)} → ${W[W.length - 1].slug.slice(20, 30)}`);
console.log('page lock record (its own ledger):', JSON.stringify(G('lockStats')));
console.log('\n== Personas (trade only on DO NEXT; obey = sell at any bid on SELL, ev = sell only when the bid beats holding) ==');
console.log('persona        rounds buys  nofill wins losses sells saved(loss avoided) soldWinner(cost)  noBid   P&L      per round  worst round');
for (const P of personas) {
  const buys = P.trades.filter(t => t.kind === 'buy').length, nofill = P.trades.filter(t => t.kind === 'nofill').length;
  const wins = P.trades.filter(t => t.kind === 'settle' && t.won).length, losses = P.trades.filter(t => t.kind === 'settle' && !t.won).length;
  const sells = P.trades.filter(t => t.kind === 'sell').length;
  let worst = 0, prev = 0; for (const e of P.equity) { worst = Math.min(worst, e - prev); prev = e; }
  console.log(`${P.name.padEnd(14)} ${String(P.rounds).padStart(6)} ${String(buys).padStart(5)} ${String(nofill).padStart(6)} ${String(wins).padStart(5)} ${String(losses).padStart(6)} ${String(sells).padStart(5)} ${String(P.sells.saved).padStart(6)} ${usd(P.sells.savedUsd).padStart(12)} ${String(P.sells.soldWinner).padStart(10)} ${usd(-P.sells.soldWinnerUsd).padStart(9)} ${String(P.sells.noBid).padStart(5)}  ${usd(P.cash).padStart(9)}  ${usd(P.cash / Math.max(1, P.rounds)).padStart(9)}  ${usd(worst).padStart(9)}`);
}
// P&L by day per persona (rounds in order; equity is cumulative cash after each scored round)
const scoredW = W.filter((w, i) => (w.T0 - t0All) / 60 >= WARM);
console.log('\nP&L by UTC day (rounds):');
const days = [...new Set(scoredW.map(w => w.slug.slice(20, 30)))];
console.log('persona        ' + days.map(d => d.padStart(12)).join(''));
for (const P of personas) { let prev = 0; const byDay = {}; P.equity.forEach((e, i) => { const d = scoredW[i].slug.slice(20, 30); byDay[d] = (byDay[d] || 0) + (e - prev); prev = e; });
  console.log(P.name.padEnd(14) + days.map(d => (usd(byDay[d] || 0) + ' (' + scoredW.filter(w => w.slug.slice(20, 30) === d).length + ')').padStart(12)).join('')); }
console.log('\n== Forecast accuracy ==');
const fl = led.firstLock; const flOk = fl.filter(x => x.ok).length;
console.log(`LOCKED appeared in ${fl.length} of ${scored} rounds; held ${flOk}, lost ${fl.length - flOk}. First lock: median ${fl.length ? median(fl.map(x => x.left)).toFixed(0) : '-'} s left (p25 ${fl.length ? q(fl.map(x => x.left), 0.25).toFixed(0) : '-'}, p75 ${fl.length ? q(fl.map(x => x.left), 0.75).toFixed(0) : '-'}).`);
console.log(`  Buyable locks (an ask existed with more than ${LAT + 2} s left): ${fl.filter(x => x.bestAsk != null).length}; cheapest ask: median ${fmtAsk(fl.map(x => x.bestAsk).filter(a => a != null))}; locks with an ask <= 97c: ${fl.filter(x => x.bestAsk != null && x.bestAsk <= 0.97).length}, <= 99c: ${fl.filter(x => x.bestAsk != null && x.bestAsk <= 0.99).length}`);
console.log(`  Rounds with no lock at all: ${scored - fl.length} (${pct((scored - fl.length) / Math.max(1, scored))})`);
const hc = led.holdClaims.filter(c => c.ok !== null && c.ok !== undefined);
console.log(`HOLD >= N s claims (favorite as if held, sampled every 5 s): ${hc.length}; cushion still positive after N s: ${pct(hc.filter(c => c.ok).length / Math.max(1, hc.length))} (claimed ${G('S.holdConf')}%); the side still won the round: ${pct(hc.filter(c => c.won).length / Math.max(1, hc.length))}`);
for (const [lab, f] of [['N <= 15 s', c => c.N <= 15], ['15 < N <= 60 s', c => c.N > 15 && c.N <= 60], ['N > 60 s', c => c.N > 60], ['final 2 min', c => c.left <= 120], ['earlier', c => c.left > 120]]) { const g = hc.filter(f); if (g.length) console.log(`   ${lab.padEnd(16)} n=${String(g.length).padStart(6)}  held N s: ${pct(g.filter(c => c.ok).length / g.length)}  won: ${pct(g.filter(c => c.won).length / g.length)}`); }
const sc = led.sellCalls; const byKey = {};
for (const s of sc) { const k = s.persona + ' ' + s.key; byKey[k] = byKey[k] || { n: 0, flip: 0 }; byKey[k].n++; if (!s.wouldWin) byKey[k].flip++; }
const byReason = {}; for (const s2 of sc) { const k = s2.persona.split('/')[0] + ' · ' + s2.reason; byReason[k] = byReason[k] || { n: 0, flip: 0 }; byReason[k].n++; if (!s2.wouldWin) byReason[k].flip++; }
console.log('First SELL call per held position, by reason → real flips:'); for (const [k, v] of Object.entries(byReason).sort()) console.log(`   ${k.padEnd(52)} ${String(v.n).padStart(4)} calls, ${String(v.flip).padStart(3)} flips (${pct(v.flip / Math.max(1, v.n))})`);
console.log('First SELL call per held position → was the side really going to lose?');
for (const [k, v] of Object.entries(byKey).sort()) console.log(`   ${k.padEnd(24)} ${String(v.n).padStart(4)} calls, ${String(v.flip).padStart(3)} real flips (${pct(v.flip / Math.max(1, v.n))})`);
console.log('Favorite calibration (fat-tail-adjusted win chance → realized, flat view, one sample per second):');
for (const [b, c] of [...led.favCal.entries()].sort((a, b) => a[0] - b[0])) console.log(`  ${(b * 100).toFixed(0).padStart(3)}–${(b * 100 + 5).toFixed(0).padStart(3)}%  n=${String(c[0]).padStart(6)}  realized ${pct(c[1] / c[0])}`);
// the late-buy question: what did the eventual winner cost, by time left, and how often was the page's favorite the winner then
console.log('\nThe eventual winner\'s ask by time left (every 5 s a book existed), with the page\'s win chance for it then:');
for (const [lo, hi] of [[600, 900], [300, 600], [180, 300], [120, 180], [90, 120], [60, 90], [45, 60], [30, 45], [20, 30], [10, 20], [0, 10]]) {
  const g = led.winnerAsk.filter(x => x.left > lo && x.left <= hi); if (!g.length) continue;
  const asks = g.map(x => x.ask); const cheap = g.filter(x => x.ask <= 0.97).length, cheap99 = g.filter(x => x.ask <= 0.99).length;
  console.log(`   ${String(lo).padStart(3)}–${String(hi).padStart(3)} s left  n=${String(g.length).padStart(5)}  winner ask median ${(median(asks) * 100).toFixed(0)}c  p25 ${(q(asks, 0.25) * 100).toFixed(0)}c  ≤97c ${pct(cheap / g.length)}  ≤99c ${pct(cheap99 / g.length)}  page's chance for the winner: median ${pct(median(g.map(x => x.p)))}  favorite was the winner ${pct(g.filter(x => x.favIsWinner).length / g.length)}`);
}
function median(a) { return q(a, 0.5); }
function fmtAsk(a) { return a.length ? (median(a) * 100).toFixed(0) + 'c' : '-'; }
