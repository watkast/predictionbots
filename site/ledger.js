// The live ledger: every settled trade from the bots' public logs on GitHub, newest first.
// Sources are the raw files the bots publish every 5 minutes; nothing on this page is typed in by hand.
(function () {
  var RAW = 'https://raw.githubusercontent.com/watkast/predictionbots/';
  var SOURCES = [
    { bot: 'Mr H', venue: 'Coinbase', url: RAW + 'data/mrh-live/live_trades.jsonl', parse: parseMrH },
    { bot: 'Mr T', venue: 'Polymarket US', url: RAW + 'mrp-data/mrt/trades.jsonl', parse: parseMrT }
  ];
  function lines(txt) { return txt.split('\n').filter(function (l) { return l.trim(); }).map(function (l) { try { return JSON.parse(l); } catch (e) { return null; } }).filter(Boolean); }
  function parseMrH(txt) {
    return lines(txt).filter(function (r) { return r.ev === 'sell'; }).map(function (r) {
      return { t: r.t, bot: 'Mr H', market: r.pid.replace('-USD', '') + ' · Coinbase', side: 'long', inPx: r.entry_px, outPx: r.px, netPct: r.net_pct, netUsd: r.net, why: r.reason };
    });
  }
  function parseMrT(txt) {
    return lines(txt).filter(function (r) { return r.outcome; }).map(function (r) {
      var coin = (r.slug.split('-updown-')[0] || '').replace(/^cpc/, '').replace(/^-/, '') || 'btc';
      var cost = r.qty * r.px + r.fee;
      return { t: r.settled || r.t, bot: 'Mr T', market: coin.toUpperCase().replace(/-.*/, '') + ' ' + (r.hz / 60) + 'm · Polymarket US', side: r.leader,
               inPx: r.px, outPx: r.outcome === r.leader ? 1 : 0, netPct: cost ? r.pnl / cost : 0, netUsd: r.pnl, why: 'settled ' + r.outcome.toLowerCase() };
    });
  }
  function fmtPx(x) { if (x == null || isNaN(x)) return '—'; return x >= 1 ? x.toLocaleString(undefined, { maximumFractionDigits: 2 }) : x.toPrecision(3); }
  function fmtT(iso) { var d = new Date(iso); if (isNaN(d)) return iso; return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }); }
  function render(rows) {
    var body = document.getElementById('ledger-body'), sum = document.getElementById('ledger-sum');
    rows.sort(function (a, b) { return a.t < b.t ? 1 : -1; });
    var wins = rows.filter(function (r) { return r.netUsd > 0; }).length, net = rows.reduce(function (s, r) { return s + (r.netUsd || 0); }, 0);
    sum.innerHTML = '<span><b>' + rows.length + '</b> settled trades</span><span><b>' + wins + '</b> won</span><span>net <b>' + (net >= 0 ? '+' : '−') + '$' + Math.abs(net).toFixed(2) + '</b></span>';
    body.innerHTML = rows.slice(0, 14).map(function (r) {
      var cls = r.netUsd > 0 ? 'win' : 'loss';
      return '<tr><td>' + fmtT(r.t) + '</td><td>' + r.bot + '</td><td>' + r.market + '</td><td>' + r.side + '</td><td class="num">' + fmtPx(r.inPx) + '</td><td class="num">' + fmtPx(r.outPx) +
             '</td><td class="num ' + cls + '">' + (r.netPct >= 0 ? '+' : '−') + Math.abs(r.netPct * 100).toFixed(2) + '% (' + (r.netUsd >= 0 ? '+' : '−') + '$' + Math.abs(r.netUsd).toFixed(2) + ')</td><td>' + r.why + '</td></tr>';
    }).join('') || '<tr><td colspan="8">No settled trades yet.</td></tr>';
  }
  Promise.all(SOURCES.map(function (s) {
    return fetch(s.url, { cache: 'no-store' }).then(function (r) { return r.ok ? r.text() : ''; }).then(s.parse).catch(function () { return []; });
  })).then(function (parts) { render([].concat.apply([], parts)); }).catch(function () {
    document.getElementById('ledger-body').innerHTML = '<tr><td colspan="8">Could not reach the logs on GitHub right now. They are at github.com/watkast/predictionbots, data branches.</td></tr>';
  });
})();
