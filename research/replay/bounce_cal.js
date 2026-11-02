// where a real quote exists, how does the market price the trailing side versus the model proxy, by proxy band and time left?
'use strict';
const fs = require('fs'); const file = process.argv[2];
const D = JSON.parse(fs.readFileSync(file, 'utf8')); const W = D.windows.filter(w => w.print_cov >= 0.95 && w.settle != null);
const Phi = z => { const t = 1 / (1 + 0.2316419 * Math.abs(z)), d = 0.3989423 * Math.exp(-z * z / 2); let p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274)))); return z > 0 ? 1 - p : p; };
const acc = {};
for (const w of W) {
  const pr = {}; for (const k in w.prints) pr[Number(k)] = w.prints[k]; const bk = {}; for (const k in w.book) bk[Number(k)] = w.book[k];
  const secs = Object.keys(pr).map(Number).sort((a, b) => a - b); const ret = []; for (let i = 5; i < secs.length; i++) if (secs[i] - secs[i - 5] === 5) ret.push(Math.log(pr[secs[i]] / pr[secs[i - 5]]));
  const s0 = [...ret].sort((a, b) => a - b), med = s0[Math.floor(s0.length / 2)], dev = ret.map(x => Math.abs(x - med)).sort((a, b) => a - b), sigRel = 1.4826 * dev[Math.floor(dev.length / 2)] / Math.sqrt(5);
  for (const s of Object.keys(bk).map(Number)) { const b = bk[s]; const spot = pr[s]; if (!(spot > 0) || b[0] == null || b[2] == null) continue; const r = w.T - s; if (r < 60 || r > 870) continue;
    const sig = sigRel * spot * 1.3, sd = sig * Math.sqrt(Math.max(0, r - 60) + 20); const pUp = Phi((spot - w.ptb) / sd);
    const loser = spot >= w.ptb ? 'DOWN' : 'UP'; const model = loser === 'UP' ? pUp : 1 - pUp; const ask = loser === 'UP' ? b[0] : 1 - b[2];
    const band = model < 0.2 ? '<20' : model < 0.3 ? '20-30' : model < 0.4 ? '30-40' : model < 0.5 ? '40-50' : '50+'; const tl = r > 600 ? '10-14.5m' : r > 300 ? '5-10m' : r > 120 ? '2-5m' : '1-2m';
    const k = tl + ' ' + band; acc[k] = acc[k] || { n: 0, d: 0, won: 0 }; acc[k].n++; acc[k].d += ask - model; acc[k].won += (w.settle >= w.ptb ? 'UP' : 'DOWN') === loser ? 1 : 0; }
}
console.log('time left · model band → n, market ask − model (avg ¢), realized win rate of that trailing side');
for (const k of Object.keys(acc).sort()) { const a = acc[k]; console.log(k.padEnd(16), String(a.n).padStart(6), (100 * a.d / a.n).toFixed(1).padStart(7) + '¢', (100 * a.won / a.n).toFixed(0).padStart(5) + '%'); }
