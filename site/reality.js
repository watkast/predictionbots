/* Reality Check: drop your Kalshi or Polymarket US export (CSV or JSON) and get your statement, computed in this
   browser. Nothing is uploaded: the file is read with FileReader and never leaves the page. Column names are matched
   loosely; when a file does not fit, the page says which column it could not find. Mirrors scripts/reality_check.py. */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var drop = $('rc-drop'), input = $('rc-file'), out = $('rc-out'), msg = $('rc-msg');
  if (!drop) return;
  var ALIASES = {
    time: ['time', 'created_time', 'createdtime', 'created', 'timestamp', 'date', 'filled_at', 'ts', 'transacttime', 'executed_at'],
    market: ['ticker', 'market_ticker', 'market', 'marketslug', 'slug', 'market_slug', 'question', 'event'],
    side: ['side', 'outcome', 'yes_no', 'direction', 'intent'],
    action: ['action', 'type', 'buy_sell', 'order_side'],
    count: ['count', 'contracts', 'quantity', 'qty', 'size', 'shares', 'filled_quantity', 'filledquantity'],
    price: ['price', 'yes_price', 'price_dollars', 'avg_price', 'fill_price', 'average_price', 'averageprice', 'price_usd'],
    fee: ['fee', 'fees', 'fee_cost', 'taker_fee', 'commission', 'fee_usd', 'fees_usd'],
    amount: ['amount', 'value', 'usd', 'cash', 'net_amount']
  };
  var norm = function (s) { return String(s).toLowerCase().replace(/[^a-z0-9_]/g, ''); };
  function pick(cols, f) { var m = {}; cols.forEach(function (c) { m[norm(c)] = c; }); for (var i = 0; i < ALIASES[f].length; i++) if (m[norm(ALIASES[f][i])]) return m[norm(ALIASES[f][i])]; return null; }
  function num(x) { var v = parseFloat(String(x == null ? '' : x).replace(/[$,¢%\s]/g, '')); return isNaN(v) ? 0 : v; }
  function when(x) { if (x == null || x === '') return null; if (/^\d{10,13}$/.test(String(x))) { var n = +x; return new Date(n > 1e11 ? n : n * 1000); } var d = new Date(String(x)); return isNaN(d) ? null : d; }
  function csv(text) {
    var rows = [], row = [], cur = '', q = false;
    for (var i = 0; i < text.length; i++) {
      var c = text[i];
      if (q) { if (c === '"' && text[i + 1] === '"') { cur += '"'; i++; } else if (c === '"') q = false; else cur += c; }
      else if (c === '"') q = true; else if (c === ',') { row.push(cur); cur = ''; } else if (c === '\n' || c === '\r') { if (c === '\r' && text[i + 1] === '\n') i++; row.push(cur); rows.push(row); row = []; cur = ''; } else cur += c;
    }
    if (cur || row.length) { row.push(cur); rows.push(row); }
    var head = rows.shift() || [];
    return rows.filter(function (r) { return r.length > 1 || (r[0] || '').trim(); }).map(function (r) { var o = {}; head.forEach(function (h, j) { o[h.replace(/^﻿/, '')] = r[j]; }); return o; });
  }
  function parse(name, text) {
    if (/\.json$/i.test(name) || /^\s*[\[{]/.test(text)) {
      var j = JSON.parse(text);
      if (Array.isArray(j)) return j;
      var k = ['fills', 'orders', 'data', 'results', 'items', 'transactions'].find(function (k) { return Array.isArray(j[k]); });
      return k ? j[k] : [j];
    }
    return csv(text);
  }
  var state = { fills: [], cash: [], files: [] };
  function ingest(name, rows) {
    if (!rows.length) return 'no rows';
    var cols = Object.keys(rows[0]);
    var c = {}; Object.keys(ALIASES).forEach(function (f) { c[f] = pick(cols, f); });
    // a deposits/withdrawals file: has an amount and a time but no price/count
    if (c.amount && c.time && !c.price) {
      rows.forEach(function (r) { var t = when(r[c.time]); if (!t) return; var a = num(r[c.amount]); var kind = String(r[c.action] || r[c.side] || '').toLowerCase(); if (/withdraw/.test(kind) && a > 0) a = -a; state.cash.push({ t: t, amount: a }); });
      return null;
    }
    var missing = ['time', 'price', 'count'].filter(function (f) { return !c[f]; });
    if (missing.length) return 'could not find a column for ' + missing.join(', ') + ' (columns: ' + cols.slice(0, 10).join(', ') + ')';
    var venue = /kalshi|ticker|yes_price/i.test(cols.join(' ')) ? 'Kalshi' : 'Polymarket US';
    rows.forEach(function (r) {
      var t = when(r[c.time]); if (!t) return;
      var p = num(r[c.price]); if (p > 1.5) p = p / 100;
      var n = Math.abs(num(r[c.count])), act = String(r[c.action] || '').toUpperCase(), side = String(r[c.side] || '').toUpperCase();
      var buy = !/SELL/.test(act) && !/SELL/.test(side);
      state.fills.push({ t: t, venue: venue, market: c.market ? String(r[c.market] || '') : '', buy: buy, n: n, p: p, fee: c.fee ? Math.abs(num(r[c.fee])) : 0, cost: n * p });
    });
    return null;
  }
  function money(x) { return (x < 0 ? '−' : '') + '$' + Math.abs(x).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function render() {
    var f = state.fills, cash = state.cash, bal = parseFloat(($('rc-balance') || {}).value);
    if (!f.length && !cash.length) { out.innerHTML = ''; return; }
    f.sort(function (a, b) { return a.t - b.t; });
    var fees = f.reduce(function (s, x) { return s + x.fee; }, 0), staked = f.filter(function (x) { return x.buy; }).reduce(function (s, x) { return s + x.cost; }, 0);
    var dep = cash.filter(function (c) { return c.amount > 0; }).reduce(function (s, c) { return s + c.amount; }, 0), wd = -cash.filter(function (c) { return c.amount < 0; }).reduce(function (s, c) { return s + c.amount; }, 0);
    var days = f.length ? Math.max(1, Math.round((f[f.length - 1].t - f[0].t) / 864e5) + 1) : 0, perWeek = days ? fees / (days / 7) : 0;
    var late = f.length ? f.filter(function (x) { var h = x.t.getHours(); return h >= 23 || h < 5; }).length / f.length : 0;
    var weeks = {}; f.forEach(function (x) { var d = new Date(x.t); d.setHours(0, 0, 0, 0); d.setDate(d.getDate() - ((d.getDay() + 6) % 7)); var k = d.toISOString().slice(0, 10); var w = weeks[k] = weeks[k] || { n: 0, staked: 0, fees: 0 }; w.n++; w.fees += x.fee; if (x.buy) w.staked += x.cost; });
    var net = (!isNaN(bal) && cash.length) ? bal + wd - dep : null;
    var h = '<h2>Your statement</h2><p class="fine">Computed in this browser from your files; nothing was uploaded. It is arithmetic, not a judgment.</p><div class="kpis">';
    h += '<div class="kpi"><div class="k">Fills</div><div class="v">' + f.length.toLocaleString() + '</div><div class="s">' + (days ? days + ' days' : '') + '</div></div>';
    h += '<div class="kpi"><div class="k">Put at risk</div><div class="v">' + money(staked) + '</div><div class="s">sum of every buy</div></div>';
    h += '<div class="kpi"><div class="k">Fees paid</div><div class="v loss">' + money(fees) + '</div><div class="s">' + (staked ? (fees / staked * 100).toFixed(1) + '% of stake; ' : '') + money(perWeek) + ' a week</div></div>';
    if (net !== null) h += '<div class="kpi"><div class="k">Net result</div><div class="v ' + (net < 0 ? 'loss' : 'win') + '">' + (net >= 0 ? '+' : '') + money(net) + '</div><div class="s">balance + withdrawals − deposits' + (net < 0 && fees ? '; fees are ' + Math.min(100, Math.round(fees / -net * 100)) + '% of it' : '') + '</div></div>';
    h += '</div>';
    if (dep || wd) h += '<p>Deposited <b>' + money(dep) + '</b>, withdrew <b>' + money(wd) + '</b>' + (!isNaN(bal) ? ', balance today <b>' + money(bal) + '</b>' : '') + '.</p>';
    var ks = Object.keys(weeks).sort();
    if (ks.length) h += '<div class="ledger-wrap"><table class="ledger cells"><caption>Your fills by week</caption><thead><tr><th scope="col">Week of</th><th scope="col" class="num">Fills</th><th scope="col" class="num">Staked</th><th scope="col" class="num">Fees</th></tr></thead><tbody>' + ks.map(function (k) { var w = weeks[k]; return '<tr><th scope="row">' + k + '</th><td class="num">' + w.n + '</td><td class="num">' + money(w.staked) + '</td><td class="num">' + money(w.fees) + '</td></tr>'; }).join('') + '</tbody></table></div>';
    if (f.length) h += '<p><b>' + Math.round(late * 100) + '%</b> of your fills happened between 11 p.m. and 5 a.m. (your clock). Not a verdict; a pattern worth knowing about yourself.</p>';
    if (perWeek && !isNaN(bal) && bal > 0) h += '<p>At this pace the fees alone take <b>' + money(perWeek) + ' a week</b>; with no edge, a balance of ' + money(bal) + ' lasts about <b>' + Math.round(bal / perWeek) + ' weeks</b> on fees alone. <a href="/simulate.html">See it play out with your numbers →</a></p>';
    h += '<div id="rc-elsewhere" class="elsewhere"></div>';
    out.innerHTML = h;
    if (window.PB && window.PB.elsewhere && (dep || staked)) window.PB.elsewhere('rc-elsewhere', { bank: dep || staked, monthlyLoss: perWeek * 52 / 12 });
  }
  function handle(files) {
    msg.textContent = '';
    Array.prototype.forEach.call(files, function (file) {
      if (file.size > 25e6) { msg.textContent = file.name + ' is over 25 MB; split it by year.'; return; }
      var rd = new FileReader();
      rd.onload = function () {
        try { var err = ingest(file.name, parse(file.name, rd.result)); state.files.push(file.name); msg.textContent = err ? file.name + ': ' + err : 'Read ' + state.files.join(', ') + '.'; render(); }
        catch (e) { msg.textContent = file.name + ': could not read this file (' + e.message + ').'; }
      };
      rd.readAsText(file);
    });
  }
  input.addEventListener('change', function () { handle(input.files); });
  ['dragenter', 'dragover'].forEach(function (e) { drop.addEventListener(e, function (ev) { ev.preventDefault(); drop.classList.add('over'); }); });
  ['dragleave', 'drop'].forEach(function (e) { drop.addEventListener(e, function (ev) { ev.preventDefault(); drop.classList.remove('over'); }); });
  drop.addEventListener('drop', function (ev) { handle(ev.dataTransfer.files); });
  var b = $('rc-balance'); if (b) b.addEventListener('input', render);
  var clear = $('rc-clear'); if (clear) clear.addEventListener('click', function () { state = { fills: [], cash: [], files: [] }; out.innerHTML = ''; msg.textContent = 'Cleared.'; input.value = ''; });
})();
