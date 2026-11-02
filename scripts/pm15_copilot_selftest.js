// Self-test for research/pm15_copilot.html: stub the DOM/network, load the page script, feed random-walk Coinbase seconds
// and index-series points across four rounds (a flash drop, a feed gap, positions on both sides), run the whole per-frame
// pipeline and fail on any exception.   Run:  node scripts/pm15_copilot_selftest.js research/pm15_copilot.html
'use strict';
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const script = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));
const els = {};
const mkEl = id => ({ id, textContent: '', innerHTML: '', className: '', hidden: false, value: '', style: {}, dataset: {},
  lastChild: { textContent: '' }, classList: { add() {}, toggle() {}, remove() {} }, onclick: null, parentElement: { clientWidth: 800, clientHeight: 450 },
  getContext: () => new Proxy({}, { get: (t, k) => (k === 'measureText' ? () => ({ width: 10 }) : () => {}) }), width: 0, height: 0 });
const document = { getElementById: id => els[id] || (els[id] = mkEl(id)), querySelectorAll: () => [], querySelector: () => mkEl('x'), addEventListener() {}, hidden: false };
const store = {}; const localStorage = { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } };
let fakeNow = 0; const timers = [];
const ctxObj = { document, localStorage, console, Intl, Math, Number, JSON, Map, Set, Array, Object, String,
  Date: Object.assign(function (...a) { return a.length ? new Date(...a) : new Date(fakeNow); }, { now: () => fakeNow, parse: Date.parse, UTC: Date.UTC }),
  setInterval: (fn, ms) => { timers.push({ fn, ms }); return timers.length; }, clearTimeout() {}, setTimeout: () => 0,
  fetch: () => Promise.reject(new TypeError('Failed to fetch')), WebSocket: class { constructor() { this.readyState = 1; } send() {} close() {} },
  window: { devicePixelRatio: 1, addEventListener() {} }, navigator: {}, Promise, Error, TypeError, RegExp, parseFloat, isFinite, Infinity, NaN, undefined };
ctxObj.Date.prototype = Date.prototype;
const ctx = vm.createContext(ctxObj);
vm.runInContext(script, ctx, { filename: 'cockpit.js' });
const run = code => vm.runInContext(code, ctx);

let seed = 12345; const rnd = () => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; };
const gauss = () => { let u = 0, v = 0; while (!u) u = rnd(); while (!v) v = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
const T0 = Math.floor(1793400000 / 900) * 900;
let px = 80000, t = T0 - 300;
const push = (sec, v) => run(`secs.set(${sec}, ${v}); if (${sec} < firstSec) firstSec = ${sec};`);
for (; t < T0; t++) { px += 8 * gauss(); push(t, px); }
run(`REC.up = [0, .0025, .0035, .0042, .0048, .0053, .0058, .0062, .0066, .007, .0074, .0077, .008, .0083, .0086, .009]; REC.dn = REC.up.map(x => x * 1.05);`);
let frames = 0, errors = 0, verdicts = {};
const stages = ['evaluate()', 'liveRecordCheck(lastEval.sec)', 'paperStep(lastEval)', 'dictate(lastEval)', 'renderHeader(lastEval)', 'renderPosLine(lastEval)', 'renderNumbers(lastEval)', 'renderWarn(lastEval)', 'drawChart(lastEval)', 'settleFromSeries()', 'renderPast()'];
for (let round = 0; round < 4; round++) {
  const Ts = T0 + round * 900;
  if (round === 1) run('REC.ready = true; REC.at = Date.now(); REC.bad = { n: 7000, at: 0, med: .0004, up: [.0008, .0011, .0018, .0022, .003], dn: [.00085, .0012, .0019, .0023, .0032] };');
  for (let s = 0; s < 900; s++) {
    t = Ts + s;
    // a flash drop in round 2 at 0:40, a gap (no prints) in round 3 between 2:00 and 1:30
    if (round === 2 && s >= 860 && s < 872) px -= 14; else if (!(round === 3 && s >= 780 && s < 810)) px += 8 * gauss();
    if (!(round === 3 && s >= 780 && s < 810)) push(t, px);
    if (round >= 1 && s % 2 === 0) run(`pmA.set(${t - 1}, avgRange(${t - 60}, ${t}) + 2.0 + ${0.3 * gauss()}); IDX.ok = true; IDX.at = Date.now(); IDX.latest = ${t - 1};`);
    if (s === 100) run(`myPos = { T0: R.T0, side: '${rnd() < 0.5 ? 'UP' : 'DOWN'}', price: 0.85, spent: 20, shares: 23.5 };`);
    if (s === 840) run('myPos = null;');
    if (s === 5) run(`R.target = ${round === 0 ? 'NaN' : 'R.target'}; if (!Number.isFinite(R.target)) { R.target = ${px.toFixed(2)}; R.targetSrc = 'api'; }`);
    if (s % 1 === 0) {
      fakeNow = t * 1000 + 300 + Math.floor(rnd() * 600);
      run(`lastTickMs = ${fakeNow}; spotNow = ${px};`);
      for (const st of stages) { try { run(st); } catch (e) { errors++; if (errors <= 8) console.log('ERR at round', round, 's', s, st, '->', e.message); } }
      frames++;
      const v = els['do-head'].textContent.split(' ')[0] + '|' + els['do-label'].textContent; verdicts[v] = (verdicts[v] || 0) + 1;
    }
  }
  console.log('round', round, 'done; history', run('history.length'), 'lockStats', JSON.stringify(run('lockStats')), 'paper', JSON.stringify(run('({side: paper.side, total: +paper.totalPnl.toFixed(2), note: paper.note})')));
}
console.log("frames", frames, "errors", errors); if (errors) process.exitCode = 1;
console.log('verdict mix:', JSON.stringify(verdicts));
console.log('last history:', JSON.stringify(run('history.slice(-2)')));
console.log('warn:', els['warn'].textContent);
