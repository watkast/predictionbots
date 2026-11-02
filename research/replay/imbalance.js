// Does the order book's imbalance predict the next 30 s? Per second with a full book: imb = (bid depth − ask depth) / (sum) within
// 5¢ of the top (Up contract). Tested against (a) the index's move over the next 30 s, (b) the Up mid's move over the next 30 s,
// and (c) the outcome of the strategy's own entries (fresh-quote replay moments: the first second a side is offered under its
// limit for 2 s running) — does imbalance separate the entries that went on to be sold at a profit from the ones that lost?
'use strict';
const fs = require('fs');
const D = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const W = D.windows.filter(w => w.print_cov >= 0.95 && w.settle != null).sort((a, b) => a.T0 - b.T0);
const rows = [];
for (const w of W) {
  const pr = {}; for (const k in w.prints) pr[Number(k)] = w.prints[k];
  const bk = {}; for (const k in w.book) bk[Number(k)] = w.book[k];
  const secs = Object.keys(bk).map(Number).sort((a, b) => a - b);
  for (const s of secs) {
    const b = bk[s]; if (b.length < 7 || b[0] == null || b[2] == null) continue;
    const bd = b[5], ad = b[6]; if (!(bd + ad > 0)) continue;
    const imb = (bd - ad) / (bd + ad), mid = (b[0] + b[2]) / 2;
    const b30 = bk[s + 30] || bk[s + 29] || bk[s + 31]; const p0 = pr[s], p30 = pr[s + 30];
    if (!b30 || b30[0] == null || b30[2] == null || !(p0 > 0) || !(p30 > 0)) continue;
    const r = w.T - s; if (r < 40) continue;
    rows.push({ r, imb, dIdx: p30 - p0, dMid: (b30[0] + b30[2]) / 2 - mid, mid, up: w.settle >= w.ptb, lead: p0 >= w.ptb ? 'UP' : 'DOWN' });
  }
}
console.log('seconds with a full book and a 30-s follow-up:', rows.length, 'over', W.length, 'rounds');
const q = (arr, p) => { const s = [...arr].sort((a, b) => a - b); return s[Math.floor(p * (s.length - 1))]; };
const imbs = rows.map(x => x.imb); const cuts = [q(imbs, 0.2), q(imbs, 0.4), q(imbs, 0.6), q(imbs, 0.8)];
const bucket = v => v <= cuts[0] ? 'ask-heavy (bottom 20%)' : v <= cuts[1] ? '20–40%' : v <= cuts[2] ? '40–60%' : v <= cuts[3] ? '60–80%' : 'bid-heavy (top 20%)';
const agg = {}; for (const x of rows) { const k = bucket(x.imb); const a = agg[k] = agg[k] || { n: 0, dIdx: 0, dMid: 0, upMid: 0, idxUp: 0 }; a.n++; a.dIdx += x.dIdx; a.dMid += x.dMid; a.upMid += x.dMid > 0 ? 1 : 0; a.idxUp += x.dIdx > 0 ? 1 : 0; }
console.log('\nimbalance bucket (Up book) → n, avg index move next 30 s ($), avg Up-mid move next 30 s (¢), share of up moves (index / mid)');
for (const k of ['ask-heavy (bottom 20%)', '20–40%', '40–60%', '60–80%', 'bid-heavy (top 20%)']) { const a = agg[k]; if (!a) continue; console.log(k.padEnd(24), String(a.n).padStart(7), (a.dIdx / a.n).toFixed(2).padStart(8), (100 * a.dMid / a.n).toFixed(2).padStart(8) + '¢', (100 * a.idxUp / a.n).toFixed(1).padStart(6) + '% /', (100 * a.upMid / a.n).toFixed(1) + '%'); }
// correlation
const mean = a => a.reduce((s, v) => s + v, 0) / a.length;
const corr = (xs, ys) => { const mx = mean(xs), my = mean(ys); let sxy = 0, sxx = 0, syy = 0; for (let i = 0; i < xs.length; i++) { sxy += (xs[i] - mx) * (ys[i] - my); sxx += (xs[i] - mx) ** 2; syy += (ys[i] - my) ** 2; } return sxy / Math.sqrt(sxx * syy); };
console.log('\ncorrelation imbalance ↔ next-30-s index move:', corr(imbs, rows.map(x => x.dIdx)).toFixed(3), ' ↔ next-30-s Up-mid move:', corr(imbs, rows.map(x => x.dMid)).toFixed(3));
// by time left
for (const [lo, hi, name] of [[600, 900, '10–15 min left'], [300, 600, '5–10 min'], [120, 300, '2–5 min'], [40, 120, '<2 min']]) { const sub = rows.filter(x => x.r > lo && x.r <= hi); if (sub.length > 200) console.log(name.padEnd(16), 'n', String(sub.length).padStart(7), 'corr idx', corr(sub.map(x => x.imb), sub.map(x => x.dIdx)).toFixed(3), 'corr mid', corr(sub.map(x => x.imb), sub.map(x => x.dMid)).toFixed(3)); }
// does the imbalance say anything about the entries the strategy takes? entry = leader offered under (model chance − 8¢): approximate
// with: lead side's ask ≤ 0.90 and the book exists; outcome = the lead side's mid 60 s later vs now (did the discount pay?)
const ent = []; for (const w of W) { const pr = {}; for (const k in w.prints) pr[Number(k)] = w.prints[k]; const bk = {}; for (const k in w.book) bk[Number(k)] = w.book[k];
  for (const s of Object.keys(bk).map(Number)) { const b = bk[s]; if (b.length < 7 || b[0] == null || b[2] == null) continue; const r = w.T - s; if (r < 300 || r > 840) continue; const p0 = pr[s]; if (!(p0 > 0)) continue;
    const lead = p0 >= w.ptb ? 'UP' : 'DOWN'; const b60 = bk[s + 60]; if (!b60 || b60[0] == null || b60[2] == null) continue;
    const imbLead = lead === 'UP' ? (b[5] - b[6]) / (b[5] + b[6] || 1) : (b[6] - b[5]) / (b[5] + b[6] || 1);   // imbalance in favour of the leader
    const midNow = lead === 'UP' ? (b[0] + b[2]) / 2 : 1 - (b[0] + b[2]) / 2, mid60 = lead === 'UP' ? (b60[0] + b60[2]) / 2 : 1 - (b60[0] + b60[2]) / 2;
    ent.push({ imbLead, d60: mid60 - midNow, won: (w.settle >= w.ptb ? 'UP' : 'DOWN') === lead }); } }
const g = (f, name) => { const sub = ent.filter(f); if (!sub.length) return; console.log(name.padEnd(34), 'n', String(sub.length).padStart(7), 'leader mid +60 s avg', (100 * mean(sub.map(x => x.d60))).toFixed(2).padStart(6) + '¢', ' leader won', (100 * mean(sub.map(x => x.won ? 1 : 0))).toFixed(1) + '%'); };
console.log('\nleader at 5:00–14:00 left, by book imbalance in the leader\'s favour:');
g(x => x.imbLead < -0.3, 'book against the leader (< −0.3)'); g(x => x.imbLead >= -0.3 && x.imbLead < 0, 'mildly against (−0.3..0)'); g(x => x.imbLead >= 0 && x.imbLead < 0.3, 'mildly for (0..0.3)'); g(x => x.imbLead >= 0.3, 'book for the leader (> 0.3)');
