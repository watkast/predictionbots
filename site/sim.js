/* "How long until your balance is $0 in this market?"
   A few hundred simulated careers in one market: your win rate is the market's price (no edge) unless you move the
   slider; the venue's fee formula is charged on every trade (Kalshi 7%; Polymarket US by 30-day volume tier, 9.5% for
   most people since 6 Nov 2026); you hold to settlement. The fan is the 10th–90th
   percentile of balances across careers; the narrated path is a real simulated career whose time-to-zero is the median.
   Nothing here is a forecast of any one person's results; it is what the arithmetic of the market does on average. */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var el = { venue: $('sm-venue'), tier: $('sm-tier'), price: $('sm-price'), stake: $('sm-stake'), week: $('sm-week'), bank: $('sm-bank'),
             edge: $('sm-edge'), edgeOut: $('sm-edge-out'), martingale: $('sm-martingale'), chase: $('sm-chase'),
             run: $('sm-run'), play: $('sm-play'), share: $('sm-share'), head: $('sm-head'), sub: $('sm-sub'),
             narr: $('sm-narr'), stats: $('sm-stats'), chart: $('sm-chart'), tip: $('sm-tip') };
  if (!el.chart || typeof d3 === 'undefined') return;

  var N = 300, MAX_T = 4000;
  var PMUS = { week1: 0.0695, t1: 0.095, t2: 0.085, t3: 0.075, t4: 0.0695 };
  function rateFor(v) { return v === 'kalshi' ? 0.07 : (PMUS[el.tier && el.tier.value] || PMUS.t1); }
  function feeFor(v, p, contracts) { return rateFor(v) * contracts * p * (1 - p); }
  function showTier() { var w = $('sm-tier-wrap'); if (w) w.hidden = el.venue.value !== 'pmus'; }
  // mulberry32 so the same inputs give the same picture (shareable, checkable)
  function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; var t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

  function career(cfg, rand) {
    var bal = cfg.bank, stake = cfg.stake, path = [bal], fees = 0, losses = 0, streak5 = -1, peak = bal, peakAt = 0, halfAt = -1, wins = 0;
    for (var t = 1; t <= MAX_T; t++) {
      var s = Math.min(stake, bal);
      if (s < 0.01) break;
      var contracts = s / cfg.p;
      var fee = feeFor(cfg.venue, cfg.p, contracts);
      fees += fee;
      if (rand() < cfg.win) { bal += contracts * (1 - cfg.p) - fee; wins++; losses = 0; stake = cfg.stake; }
      else { bal -= s + fee; losses++; if (losses >= 5 && streak5 < 0) streak5 = t; if (cfg.martingale) stake = Math.min(stake * 2, bal); else if (cfg.chase) stake = stake * 1.5; }
      if (bal <= 0.01) { bal = 0; path.push(0); return { path: path, ruin: t, fees: fees, streak5: streak5, peak: peak, peakAt: peakAt, halfAt: halfAt, wins: wins }; }
      if (bal > peak) { peak = bal; peakAt = t; }
      if (halfAt < 0 && bal <= cfg.bank / 2) halfAt = t;
      path.push(bal);
    }
    return { path: path, ruin: null, fees: fees, streak5: streak5, peak: peak, peakAt: peakAt, halfAt: halfAt, wins: wins };
  }

  function simulate(cfg) {
    var rand = rng(cfg.seed), runs = [];
    for (var i = 0; i < N; i++) runs.push(career(cfg, rand));
    var horizon = Math.max.apply(null, runs.map(function (r) { return r.path.length; }));
    horizon = Math.min(horizon, MAX_T);
    var q10 = [], q50 = [], q90 = [];
    for (var t = 0; t < horizon; t++) {
      var col = runs.map(function (r) { return t < r.path.length ? r.path[t] : 0; }).sort(d3.ascending);
      q10.push(d3.quantileSorted(col, 0.1)); q50.push(d3.quantileSorted(col, 0.5)); q90.push(d3.quantileSorted(col, 0.9));
    }
    var ruins = runs.map(function (r) { return r.ruin == null ? MAX_T + 1 : r.ruin; }).sort(d3.ascending);
    var medRuin = Math.round(d3.quantileSorted(ruins, 0.5));
    var q25Ruin = Math.round(d3.quantileSorted(ruins, 0.25));
    var plotEnd = Math.min(horizon - 1, Math.max(50, Math.round(d3.quantileSorted(ruins, 0.9)) + 5));
    var survivors = runs.filter(function (r) { return r.ruin == null; }).length;
    // the narrated career: a real one whose time-to-zero is closest to the median
    var rep = runs.slice().sort(function (a, b) { return Math.abs((a.ruin || MAX_T + 1) - medRuin) - Math.abs((b.ruin || MAX_T + 1) - medRuin); })[0];
    return { runs: runs, q10: q10, q50: q50, q90: q90, horizon: horizon, plotEnd: plotEnd, medRuin: medRuin, q25Ruin: q25Ruin, survivors: survivors, rep: rep, ruins: ruins };
  }

  function cfgFromInputs() {
    var p = Math.min(0.99, Math.max(0.01, (parseFloat(el.price.value) || 50) / 100));
    var edgePts = parseFloat(el.edge.value) || 0;
    return { venue: el.venue.value, p: p, win: Math.min(0.99, Math.max(0.01, p + edgePts / 100)), stake: Math.max(1, parseFloat(el.stake.value) || 20),
             week: Math.max(1, parseFloat(el.week.value) || 20), bank: Math.max(1, parseFloat(el.bank.value) || 500),
             martingale: el.martingale.checked, chase: el.chase.checked && !el.martingale.checked, seed: 20261108 };
  }
  function weeks(t, perWeek) { var w = t / perWeek; if (w < 1.5) return 'about ' + Math.round(w * 7) + ' days'; if (w < 10) return 'about ' + w.toFixed(1) + ' weeks'; if (w < 70) return 'about ' + Math.round(w / 4.345) + ' months'; return 'about ' + (w / 52).toFixed(1) + ' years'; }
  function money(x) { return '$' + Math.round(x).toLocaleString(); }
  function pct(x) { return Math.round(x * 100) + '%'; }

  var state = null, timer = null;

  function narrate(cfg, res) {
    var r = res.rep, p = cfg.p, c0 = cfg.stake / p, fee0 = feeFor(cfg.venue, p, c0);
    var evs = [];
    evs.push({ t: 1, title: 'Trade 1: the cover charge', text: 'Before anyone wins or loses, $' + fee0.toFixed(2) + ' leaves your account. ' + (fee0 * 100).toFixed(0) + '¢ on a $' + cfg.stake + ' trade is ' + (fee0 / cfg.stake * 100).toFixed(1) + '%. The market pays you ' + pct(p) + ' of the time; it needs to pay you ' + pct(p + fee0 / c0) + ' for this to break even.' });
    if (r.peakAt > 3) evs.push({ t: r.peakAt, title: 'Trade ' + r.peakAt + ': the high-water mark, ' + money(r.peak), text: 'This is where people decide they have figured it out and raise their size. Nothing about the market changed. The next ' + (r.ruin ? r.ruin - r.peakAt : 'many') + ' trades go the other way on average, because the average was always the fee.' });
    if (r.streak5 > 0) evs.push({ t: r.streak5, title: 'Trade ' + r.streak5 + ': five losses in a row', text: 'At a ' + pct(cfg.win) + ' win rate this happens to most people every month. It is where new traders double their size to "get it back." ' + (cfg.martingale ? 'You have that switched on: watch the slope.' : 'Flip "double after a loss" to see what that does.') });
    if (r.halfAt > 0) evs.push({ t: r.halfAt, title: 'Trade ' + r.halfAt + ': half your money is gone', text: 'Fees paid so far: ' + money(r.fees * r.halfAt / (r.ruin || r.path.length)) + '. The rest went to whoever was on the other side of the coin flips, which over time is nobody in particular: it is variance you paid to experience.' });
    if (r.ruin) evs.push({ t: r.ruin, title: 'Trade ' + r.ruin + ': $0 (' + weeks(r.ruin, cfg.week) + ' at your pace)', text: 'Total fees on the way down: ' + money(r.fees) + ' of your ' + money(cfg.bank) + '. In real life people do not ride to zero; they stop, feel better, and deposit again. That is this same curve with pauses in it.' });
    else evs.push({ t: r.path.length - 1, title: 'Still standing after ' + (r.path.length - 1) + ' trades', text: 'With an edge of ' + (cfg.win - p > 0 ? '+' : '') + ((cfg.win - p) * 100).toFixed(1) + ' points you outran the fee in this career. ' + pct(res.survivors / N) + ' of simulated careers did. Ask yourself where the edge comes from; the market is pricing the same information you have.' });
    evs.sort(function (a, b) { return a.t - b.t; });
    return evs;
  }

  function draw(cfg, res, upto) {
    var box = el.chart.getBoundingClientRect(), W = Math.max(320, box.width), H = 360, m = { t: 16, r: 16, b: 40, l: 56 };
    var svg = d3.select(el.chart).html('').append('svg').attr('viewBox', '0 0 ' + W + ' ' + H).attr('width', '100%').attr('height', H).attr('role', 'img')
      .attr('aria-label', 'Simulated account balance over trades, median and 10th to 90th percentile band');
    var T = res.plotEnd;
    var x = d3.scaleLinear().domain([0, T]).range([m.l, W - m.r]);
    var ymax = Math.max(cfg.bank * 1.6, d3.max(res.q90) || 0, d3.max(res.rep.path) || 0);
    var y = d3.scaleLinear().domain([0, ymax]).nice().range([H - m.b, m.t]);
    var ink2 = getComputedStyle(document.documentElement).getPropertyValue('--ink-2').trim() || '#4b5563';
    var rule = getComputedStyle(document.documentElement).getPropertyValue('--rule').trim() || '#cfd5de';
    svg.append('g').attr('transform', 'translate(0,' + (H - m.b) + ')').call(d3.axisBottom(x).ticks(6).tickSize(0).tickPadding(10)).call(function (g) { g.select('.domain').attr('stroke', rule); g.selectAll('text').attr('fill', ink2).attr('font-size', 12); });
    svg.append('g').attr('transform', 'translate(' + m.l + ',0)').call(d3.axisLeft(y).ticks(5).tickFormat(function (d) { return '$' + d3.format('~s')(d); }).tickSize(-(W - m.l - m.r)).tickPadding(8))
      .call(function (g) { g.select('.domain').remove(); g.selectAll('line').attr('stroke', rule); g.selectAll('text').attr('fill', ink2).attr('font-size', 12); });
    svg.append('text').attr('x', W - m.r).attr('y', H - 6).attr('text-anchor', 'end').attr('fill', ink2).attr('font-size', 12).text('trades →');
    var idx = d3.range(0, Math.min(upto, T) + 1);
    var area = d3.area().x(function (i) { return x(i); }).y0(function (i) { return y(res.q10[i]); }).y1(function (i) { return y(res.q90[i]); }).curve(d3.curveMonotoneX);
    svg.append('path').datum(idx).attr('d', area).attr('fill', '#2448c9').attr('fill-opacity', 0.12);
    var line = d3.line().x(function (i) { return x(i); }).y(function (i) { return y(res.q50[i]); }).curve(d3.curveMonotoneX);
    svg.append('path').datum(idx).attr('d', line).attr('fill', 'none').attr('stroke', '#2448c9').attr('stroke-width', 2);
    var rep = res.rep.path, ridx = d3.range(0, Math.min(upto, rep.length - 1) + 1);
    var rl = d3.line().x(function (i) { return x(i); }).y(function (i) { return y(rep[i]); });
    svg.append('path').datum(ridx).attr('d', rl).attr('fill', 'none').attr('stroke', '#c8402f').attr('stroke-width', 2);
    svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(cfg.bank)).attr('y2', y(cfg.bank)).attr('stroke', ink2).attr('stroke-dasharray', '3 4').attr('stroke-opacity', 0.6);
    svg.append('text').attr('x', W - m.r - 6).attr('y', y(cfg.bank) - 6).attr('text-anchor', 'end').attr('fill', ink2).attr('font-size', 12).text('you start with ' + money(cfg.bank));
    // event markers on the narrated path
    (res.events || []).forEach(function (e) { if (e.t <= upto && e.t < rep.length) svg.append('circle').attr('cx', x(e.t)).attr('cy', y(rep[e.t])).attr('r', 5).attr('fill', '#c8402f').attr('stroke', '#fff').attr('stroke-width', 2); });
    // hover
    var tip = el.tip;
    svg.append('rect').attr('x', m.l).attr('y', m.t).attr('width', W - m.l - m.r).attr('height', H - m.t - m.b).attr('fill', 'transparent')
      .on('mousemove', function (ev) {
        var i = Math.round(x.invert(d3.pointer(ev)[0])); i = Math.max(0, Math.min(i, Math.min(upto, T)));
        var cum = res.rep.fees * Math.min(1, i / Math.max(1, (res.rep.ruin || rep.length - 1)));
        tip.hidden = false; tip.style.left = (d3.pointer(ev, el.chart)[0] + 12) + 'px'; tip.style.top = (d3.pointer(ev, el.chart)[1] + 12) + 'px';
        tip.innerHTML = '<b>Trade ' + i + '</b> · ' + weeks(i, cfg.week) + '<br>Typical career: ' + money(i < rep.length ? rep[i] : 0) + '<br>Median of ' + N + ': ' + money(res.q50[i] || 0) + ' · 10–90%: ' + money(res.q10[i] || 0) + '–' + money(res.q90[i] || 0) + '<br>Fees paid so far (typical): ' + money(cum);
      }).on('mouseleave', function () { tip.hidden = true; });
  }

  function render(cfg, res, upto) {
    draw(cfg, res, upto);
    var tw = $('sm-table-wrap'); if (tw && !tw.hidden && upto >= res.plotEnd) tableView(cfg, res);
    var ruinPct = 1 - res.survivors / N, medText = res.medRuin > MAX_T ? 'not within ' + MAX_T.toLocaleString() + ' trades' : res.medRuin + ' trades, ' + weeks(res.medRuin, cfg.week);
    el.head.textContent = res.medRuin > MAX_T ? 'Most careers survive this market at that edge' : 'Median time to $0: ' + medText;
    el.sub.textContent = pct(ruinPct) + ' of ' + N + ' simulated careers hit $0' + (res.medRuin > MAX_T ? '' : '; a quarter were gone by trade ' + res.q25Ruin + ' (' + weeks(res.q25Ruin, cfg.week) + ')') + '. Win rate used: ' + pct(cfg.win) + (Math.abs(cfg.win - cfg.p) < 1e-9 ? ' (the market\'s own price: no edge)' : ' (the price is ' + pct(cfg.p) + ')') + '.';
    el.stats.innerHTML = '<span>Fee per trade <b>' + '$' + feeFor(cfg.venue, cfg.p, cfg.stake / cfg.p).toFixed(2) + '</b></span><span>Typical fees on the way to $0 <b>' + money(res.rep.fees) + '</b></span><span>Win rate to break even <b>' + pct(cfg.p + feeFor(cfg.venue, cfg.p, cfg.stake / cfg.p) / (cfg.stake / cfg.p)) + '</b></span>';
    var shown = (res.events || []).filter(function (e) { return e.t <= upto; });
    el.narr.innerHTML = shown.map(function (e) { return '<div class="ev"><b>' + e.title + '</b><p>' + e.text + '</p></div>'; }).join('') || '<div class="ev"><p>Press play to watch a typical career, or drag over the chart.</p></div>';
    if (upto >= res.plotEnd && window.PB && window.PB.elsewhere) window.PB.elsewhere('sm-elsewhere', { bank: cfg.bank, monthlyLoss: feeFor(cfg.venue, cfg.p, cfg.stake / cfg.p) * cfg.week * 52 / 12 });
    el.share.dataset.text = 'How long until my balance is $0 in this market? ' + (cfg.venue === 'kalshi' ? 'Kalshi' : 'Polymarket US') + ' at ' + Math.round(cfg.p * 100) + '¢, $' + cfg.stake + ' a trade, ' + cfg.week + ' trades a week, starting with ' + money(cfg.bank) + ': median ' + medText + '; ' + pct(ruinPct) + ' of ' + N + ' simulated careers hit $0. predictmenot.com/simulate';
  }

  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function tableView(cfg, res) {
    var wrap = $('sm-table-wrap'); if (!wrap) return;
    var T = res.plotEnd, step = Math.max(1, Math.round(T / 12)), rows = [];
    for (var i = 0; i <= T; i += step) rows.push(i);
    if (rows[rows.length - 1] !== T) rows.push(T);
    var rep = res.rep.path;
    var html = '<table class="ledger cells"><caption>Simulated balance by trade: one typical career, the median of ' + N + ' careers, and the 10th to 90th percentile band</caption>' +
      '<thead><tr><th scope="col">Trade</th><th scope="col">Time at your pace</th><th scope="col" class="num">Typical career</th><th scope="col" class="num">Median of ' + N + '</th><th scope="col" class="num">10th percentile</th><th scope="col" class="num">90th percentile</th></tr></thead><tbody>' +
      rows.map(function (i) { return '<tr><th scope="row">' + i + '</th><td>' + weeks(i, cfg.week) + '</td><td class="num">' + money(i < rep.length ? rep[i] : 0) + '</td><td class="num">' + money(res.q50[i] || 0) + '</td><td class="num">' + money(res.q10[i] || 0) + '</td><td class="num">' + money(res.q90[i] || 0) + '</td></tr>'; }).join('') +
      '</tbody></table>';
    wrap.innerHTML = html;
  }
  var tableBtn = $('sm-table');
  if (tableBtn) tableBtn.addEventListener('click', function () {
    var wrap = $('sm-table-wrap'); var open = wrap.hidden; wrap.hidden = !open; tableBtn.setAttribute('aria-expanded', String(open)); tableBtn.textContent = open ? 'Hide the table' : 'Show as a table';
    if (open && state) tableView(state.cfg, state.res);
  });

  function run(animate) {
    if (timer) { clearInterval(timer); timer = null; }
    if (reduceMotion) animate = false;
    var cfg = cfgFromInputs(); var res = simulate(cfg); res.events = narrate(cfg, res); state = { cfg: cfg, res: res };
    var T = res.plotEnd;
    if (!animate) { render(cfg, res, T); return; }
    var steps = 160, i = 0, start = performance.now(), dur = 9000;
    el.play.textContent = 'Playing…'; el.play.disabled = true;
    timer = setInterval(function () {
      var f = Math.min(1, (performance.now() - start) / dur); var upto = Math.round(Math.pow(f, 1.6) * T);
      render(cfg, res, upto);
      if (f >= 1) { clearInterval(timer); timer = null; el.play.textContent = 'Play it again'; el.play.disabled = false; }
    }, dur / steps);
  }

  function syncEdge() { var p = Math.round((parseFloat(el.price.value) || 50)); var e = parseFloat(el.edge.value) || 0; el.edgeOut.textContent = (p + e) + '% (market says ' + p + '%' + (e ? ', you say you are ' + (e > 0 ? '+' : '') + e + ' points better' : ', no edge') + ')'; }
  ['input', 'change'].forEach(function (evn) { [el.venue, el.tier, el.price, el.stake, el.week, el.bank, el.edge].forEach(function (x) { if (!x) return; x.addEventListener(evn, function () { showTier(); syncEdge(); run(false); }); });
    [el.martingale, el.chase].forEach(function (x) { x.addEventListener(evn, function () { if (x === el.martingale && x.checked) el.chase.checked = false; if (x === el.chase && x.checked) el.martingale.checked = false; run(false); }); }); });
  if (reduceMotion) el.play.textContent = 'Run again (animation off: reduced motion)';
  el.play.addEventListener('click', function () { run(true); });
  el.share.addEventListener('click', function () { var t = el.share.dataset.text || ''; (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(function () { el.share.textContent = 'Copied'; setTimeout(function () { el.share.textContent = 'Copy this result'; }, 1600); }, function () { prompt('Copy:', t); }); });
  window.addEventListener('resize', function () { if (state) render(state.cfg, state.res, state.res.plotEnd); });
  // deep links: /simulate?venue=kalshi&price=52&stake=20&week=20&bank=500
  try { var q = new URLSearchParams(location.search); ['venue', 'price', 'stake', 'week', 'bank'].forEach(function (k) { if (q.get(k) && el[k]) el[k].value = q.get(k); }); } catch (e) {}
  showTier(); syncEdge(); run(true);
})();
