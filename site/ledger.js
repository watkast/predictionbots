// The ledger: every real-money round trip our bots made, newest first.
// Source: /data/bot_trades.json, built by scripts/ledger_build.py from the bots' own log and state files on the repo's
// public data branches (the record closed on 8 Nov 2026, so the file is built once and committed; the script and its
// --check flag let anyone rebuild it and compare). Nothing here is typed in by hand.
(function () {
  var FIRST = 14, all = false, data = null;
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function money(x) { return (x > 0 ? '+' : x < 0 ? '−' : '') + '$' + Math.abs(x).toFixed(2); }
  function fmtPx(x, unit) {
    if (x == null || isNaN(x)) return '—';
    if (unit === 'c') return (Math.round(x * 1000) / 10).toLocaleString(undefined, { maximumFractionDigits: 1 }) + '¢';
    return x >= 1 ? x.toLocaleString(undefined, { maximumFractionDigits: 2 }) : x.toPrecision(3);
  }
  function fmtT(iso) { var d = new Date(iso); if (isNaN(d)) return iso; return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }); }
  function cls(x) { return x > 0 ? 'win' : x < 0 ? 'loss' : ''; }
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function days(b) {   // "2 to 4 Nov" (UTC dates of the first and last close), written out so no locale reorders it
    if (!b.first) return '';
    var f = b.first.split('-'), l = b.last.split('-'), end = +l[2] + ' ' + MON[+l[1] - 1];
    return b.first === b.last ? end : (f[1] === l[1] ? +f[2] : +f[2] + ' ' + MON[+f[1] - 1]) + ' to ' + end;
  }
  function row(r) {
    var pct = r.cost ? r.n / r.cost : 0, bot = data.bots[r.b].bot;
    return '<tr><td>' + esc(fmtT(r.t)) + '</td><td>' + esc(bot) + '</td><td>' + esc(r.m) + '</td><td>' + esc(r.s) + '</td><td class="num">' + fmtPx(r.i, r.u) +
           '</td><td class="num">' + fmtPx(r.o, r.u) + '</td><td class="num ' + cls(r.n) + '">' + (pct > 0 ? '+' : pct < 0 ? '−' : '') + Math.abs(pct * 100).toFixed(1) + '% (' + money(r.n) + ')</td><td>' +
           esc(r.w) + (r.f ? ' <span title="' + esc(r.e) + '">†</span>' : '') + '</td></tr>';
  }
  function renderRows() {
    var rows = all ? data.rows : data.rows.slice(0, FIRST), more = $('ledger-more');
    $('ledger-body').innerHTML = rows.map(row).join('') || '<tr><td colspan="8">No trades on record.</td></tr>';
    if (!more) return;
    more.hidden = data.rows.length <= FIRST;
    more.textContent = all ? 'Show the newest ' + FIRST + ' only' : 'Show all ' + data.rows.length + ' round trips';
    more.setAttribute('aria-expanded', all ? 'true' : 'false');
  }
  function render(d) {
    data = d;
    var t = d.total, per = t.staked ? Math.abs(t.net) / t.staked * 100 : 0;
    $('ledger-sum').innerHTML = '<span><b>' + t.trips + '</b> round trips</span><span><b>' + t.won + '</b> won</span><span><b>' + t.lost + '</b> lost</span>' +
      (t.flat ? '<span><b>' + t.flat + '</b> flat</span>' : '') + '<span>net <b>' + money(t.net) + '</b> on $' + t.staked.toFixed(2) + ' staked</span>' +
      (t.net < 0 ? '<span><b>' + per.toFixed(1) + '¢</b> lost per dollar staked</span>' : '');
    var bots = $('ledger-bots');
    if (bots) bots.innerHTML = d.bots.map(function (b) {
      var none = !b.trips;
      return '<tr><th scope="row">' + esc(b.bot) + '</th><td class="num">' + b.trips + '</td><td class="num">' + (none ? '—' : b.won) + '</td><td class="num ' + cls(b.net) + '">' + money(b.net) +
             '</td><td>' + esc(b.where) + (b.first ? '<br>' + esc(days(b)) : '') + '</td><td>' + esc(b.idea) + (b.note ? ' ' + esc(b.note) : '') + '</td></tr>';
    }).join('') + '<tr><th scope="row">All bots</th><td class="num">' + t.trips + '</td><td class="num">' + t.won + '</td><td class="num ' + cls(t.net) + '">' + money(t.net) + '</td><td>2 to 8 Nov 2026</td><td></td></tr>';
    var ev = $('ledger-unlogged');
    if (ev) ev.innerHTML = d.rows.filter(function (r) { return r.f; }).map(function (r) {
      return '<li>' + esc(fmtT(r.t)) + ', ' + esc(d.bots[r.b].bot) + ', ' + esc(r.s) + ' at ' + fmtPx(r.i, r.u) + ': ' + esc(r.w) + ', ' + money(r.n) + '. ' + esc(r.e) + '</li>';
    }).join('');
    var gaps = $('ledger-gaps');
    if (gaps && d.gaps) gaps.innerHTML = d.gaps.windows.map(function (g) {
      return '<li>' + esc(g.market) + ', round starting ' + esc(g.round.slice(11, 16)) + ' UTC on ' + +g.round.slice(8, 10) + ' ' + MON[+g.round.slice(5, 7) - 1] + ': twelve one-share buys rested at ' +
             esc(g.rested) + '; what was left was cancelled at ' + esc(g.cleared) + '. ' + esc(g.seen) + ' The round settled ' + esc(g.settled) + '.</li>';
    }).join('');
    var more = $('ledger-more');
    if (more) more.addEventListener('click', function () { all = !all; renderRows(); });
    renderRows();
  }
  fetch('/data/bot_trades.json', { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }).then(render).catch(function () {
    var msg = 'Could not load the record just now. The file is /data/bot_trades.json; the logs behind it are at github.com/watkast/predictionbots, data branches.';
    $('ledger-body').innerHTML = '<tr><td colspan="8">' + msg + '</td></tr>';
    if ($('ledger-bots')) $('ledger-bots').innerHTML = '<tr><td colspan="6">' + msg + '</td></tr>';
  });
})();
