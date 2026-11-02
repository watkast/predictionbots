// "Loser bounce" study: buy the side priced low after an early run, sell at the first flip (or a fixed gain), one trade a round.
// Price proxy per second = a Brownian settlement model on the 1-s index prints (sigma from the trailing window, x1.3 as
// calibrated on BTC); actual book quotes override the proxy whenever one is within 5 s. Fees: taker both ways.
'use strict';
const fs = require('fs');
const file = process.argv[2], L = Number(process.argv[3] || 900), label = process.argv[4] || file;
const D = JSON.parse(fs.readFileSync(file, 'utf8'));
const W = D.windows.filter(w => w.print_cov >= 0.95 && w.settle != null).sort((a, b) => a.T0 - b.T0);
const FEE = 0.0695, fee = p => FEE * p * (1 - p);
const Phi = z => { const t = 1 / (1 + 0.2316419 * Math.abs(z)), d = 0.3989423 * Math.exp(-z * z / 2); let p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274)))); return z > 0 ? 1 - p : p; };
function series(w) {
  const pr = {}; for (const k in w.prints) pr[Number(k)] = w.prints[k];
  const bk = {}; for (const k in w.book) bk[Number(k)] = w.book[k];
  // per-second sigma (relative) from 5-s log returns over the 15 minutes before each second, floored
  const secs = []; for (let s = w.T0 - 130; s <= w.T + 2; s++) if (pr[s] > 0) secs.push(s);
  const ret = []; for (let i = 5; i < secs.length; i++) { const a = pr[secs[i - 5]], b = pr[secs[i]]; if (a > 0 && b > 0 && secs[i] - secs[i - 5] === 5) ret.push(Math.log(b / a)); }
  const mad = arr => { if (arr.length < 20) return NaN; const s = [...arr].sort((x, y) => x - y), m = s[Math.floor(s.length / 2)]; const dev = arr.map(x => Math.abs(x - m)).sort((x, y) => x - y); return 1.4826 * dev[Math.floor(dev.length / 2)]; };
  return { pr, bk, sig5: mad(ret) };
}
// the loser's price at second s: book if within 5 s (ask of that side), else model
function priceOf(S, w, s, side, sigRel) {
  for (let d = 0; d <= 5; d++) { const b = S.bk[s - d] || (d && S.bk[s + d]); if (b) { const ask = side === 'UP' ? b[0] : (b[2] != null ? 1 - b[2] : null); const bid = side === 'UP' ? b[2] : (b[0] != null ? 1 - b[0] : null); if (ask != null && bid != null) return { ask, bid, src: 'book' }; } }
  const spot = S.pr[s]; if (!(spot > 0)) return null;
  const r = w.T - s; if (r <= 0) return null;
  // settlement model: mean of the last 60 prints; known part is fixed, the rest diffuses from the spot
  const known = []; for (let t = w.T - 60; t < s; t++) if (S.pr[t] > 0) known.push(S.pr[t]);
  const kN = Math.max(0, Math.min(60, known.length)), rest = 60 - kN;
  const mean = kN ? (known.reduce((a, b) => a + b, 0) + rest * spot) / 60 : spot;
  const sig = sigRel * spot * 1.3;   // per-sqrt(second), calibrated x1.3
  const sd = kN ? sig * Math.sqrt(rest * rest * rest / 3) / 60 : sig * Math.sqrt(Math.max(0, r - 60) + 60 / 3);
  const pUp = sd > 0 ? Phi((mean - w.ptb) / sd) : (mean >= w.ptb ? 1 : 0);
  const p = side === 'UP' ? pUp : 1 - pUp; const px = Math.min(0.99, Math.max(0.01, Math.round(p * 100) / 100));
  return { ask: px, bid: Math.max(0.01, px - 0.01), src: 'model' };
}
function run(cfg) {
  const out = { n: 0, soldAtTarget: 0, settledWin: 0, settledLoss: 0, pnl: 0, bookFills: 0, worst: 0, byRound: [] };
  for (const w of W) {
    const S = series(w); if (!(S.sig5 > 0)) continue;
    const sigRel = S.sig5 / Math.sqrt(5);
    const result = w.settle >= w.ptb ? 'UP' : 'DOWN';
    let pos = null, done = false;
    for (let s = w.T0 + cfg.minIn; s <= w.T - 1 && !done; s++) {
      if (!pos) {
        if (s > w.T0 + cfg.entryBy) break;
        const spot = S.pr[s]; if (!(spot > 0)) continue;
        const loser = spot >= w.ptb ? 'DOWN' : 'UP';                  // the side currently behind
        const q = priceOf(S, w, s, loser, sigRel); if (!q) continue;
        if (cfg.bookOnly && q.src !== 'book') continue;
        if (q.ask >= cfg.lo && q.ask <= cfg.hi) { pos = { side: loser, px: q.ask, at: s, src: q.src }; if (q.src === 'book') out.bookFills++; }
      } else {
        const q = priceOf(S, w, s, pos.side, sigRel); if (!q) continue;
        if (cfg.bookOnly && q.src !== 'book') continue;
        const target = cfg.flip ? 0.50 : pos.px * (1 + cfg.gain);
        if (q.bid >= target) { const pnl = (q.bid - fee(q.bid)) - (pos.px + fee(pos.px)); out.pnl += pnl; out.soldAtTarget++; out.n++; out.worst = Math.min(out.worst, pnl); out.byRound.push(pnl); done = true; }
      }
    }
    if (pos && !done) { const won = pos.side === result; const pnl = (won ? 1 : 0) - (pos.px + fee(pos.px)); out.pnl += pnl; out.n++; if (won) out.settledWin++; else out.settledLoss++; out.worst = Math.min(out.worst, pnl); out.byRound.push(pnl); }
  }
  return out;
}
// how often does the early leader flip at all?
let flips = 0, rounds = 0, leadAt2 = 0, flipAfter2 = 0;
for (const w of W) { const S = series(w); const sp = s => S.pr[s]; rounds++;
  let side0 = null, flipped = false; for (let s = w.T0 + 60; s < w.T; s++) { const v = sp(s); if (!(v > 0)) continue; const sd = v >= w.ptb ? 'UP' : 'DOWN'; if (!side0) side0 = sd; else if (sd !== side0) { flipped = true; break; } }
  if (flipped) flips++;
  const v2 = sp(w.T0 + 120); if (v2 > 0) { leadAt2++; const lead = v2 >= w.ptb ? 'UP' : 'DOWN'; for (let s = w.T0 + 121; s < w.T; s++) { const v = sp(s); if (v > 0 && (v >= w.ptb ? 'UP' : 'DOWN') !== lead) { flipAfter2++; break; } } }
}
console.log(`\n=== ${label}: ${W.length} rounds (window ${L}s) ===`);
console.log(`leader after the first minute flips at least once later: ${flips}/${rounds} (${(100 * flips / rounds).toFixed(0)}%); leader at 2:00 in flips later: ${flipAfter2}/${leadAt2} (${(100 * flipAfter2 / leadAt2).toFixed(0)}%)`);
const bands = [[0.20, 0.30], [0.30, 0.40], [0.25, 0.40], [0.35, 0.45], [0.40, 0.48]];
const entries = [[30, Math.round(L / 3)], [30, Math.round(L / 2)], [30, Math.round(L * 2 / 3)]];
const header = 'entry window   buy band   exit        n   sold@target  held:won  held:lost   P&L/trade  worst   total per $20 stake';
for (const bookOnly of [false, true]) {
  console.log(bookOnly ? '\n-- fills and sells only on actual book quotes (within 5 s) --' : '\n-- model price proxy where the book is missing --');
  console.log(header);
  for (const [minIn, entryBy] of entries) for (const [lo, hi] of bands) for (const ex of [{ flip: true, gain: 0 }, { flip: false, gain: 0.2 }, { flip: false, gain: 0.5 }]) {
    const o = run({ minIn, entryBy, lo, hi, flip: ex.flip, gain: ex.gain, bookOnly });
    if (!o.n) continue;
    const per = o.pnl / o.n;
    console.log(`${String(minIn).padStart(3)}s–${String(entryBy).padEnd(4)}s   ${Math.round(lo * 100)}–${Math.round(hi * 100)}¢     ${ex.flip ? 'flip(50¢)' : '+' + Math.round(ex.gain * 100) + '%     '}  ${String(o.n).padStart(4)}   ${String(o.soldAtTarget).padStart(6)}       ${String(o.settledWin).padStart(5)}     ${String(o.settledLoss).padStart(5)}     ${(per * 100).toFixed(1).padStart(6)}¢  ${(o.worst * 100).toFixed(0).padStart(5)}¢   ${(o.pnl / (lo + hi) * 2 * 20 / 1).toFixed(0).padStart(6)}`.replace(/\s+$/, ''));
  }
}
