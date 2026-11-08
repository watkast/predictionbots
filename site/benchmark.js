/* Bot Benchmark rows: measured results from the replay published by the benchmark workflow
   (mrp-data branch, benchmark/benchmark.json). Rows in the table carry data-rule="<rule key>"; this fills their
   result cell with net per trade, win rate, trades, worst losing run and book coverage, and links the data file. */
(function () {
  var BASE = 'https://raw.githubusercontent.com/watkast/predictionbots/mrp-data/benchmark/';
  var VIEW = 'https://github.com/watkast/predictionbots/blob/mrp-data/benchmark/';
  var rows = document.querySelectorAll('[data-rule]');
  if (!rows.length) return;
  var files = { pmus: 'benchmark.json', kalshi: 'benchmark_kalshi.json' };
  Promise.all(Object.keys(files).map(function (k) { return fetch(BASE + files[k], { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }).then(function (j) { return [k, j]; }); })).then(function (pairs) {
    var data = {}; pairs.forEach(function (p) { data[p[0]] = p[1]; });
    rows.forEach(function (tr) {
      var src = tr.getAttribute('data-src') || 'pmus', j = data[src]; if (!j) return;
      var DATA = VIEW + files[src];
      var r = j.rules && j.rules[tr.getAttribute('data-rule')];
      var cell = tr.querySelector('[data-result]'), status = tr.querySelector('[data-status]');
      if (!r || !cell) return;
      if (!r.trades) { cell.textContent = 'No qualifying trade in ' + j.windows_usable + ' recorded windows'; if (status) status.textContent = 'Measured ' + j.generated.slice(0, 10); return; }
      var net = r.net_per_dollar, cls = net < 0 ? 'loss' : 'win';
      cell.innerHTML = '<span class="' + cls + '">' + (net >= 0 ? '+' : '−') + Math.abs(net * 100).toFixed(1) + '% per $ staked</span>, ' + Math.round(r.win_rate * 100) + '% winners, ' + r.trades + ' trades, worst run ' + r.worst_losing_run + '; coverage ' + Math.round(r.mean_coverage * 100) + '%';
      if (status) status.innerHTML = 'Measured ' + j.generated.slice(0, 10) + ' · <a href="' + DATA + '" rel="noopener">data</a>';
    });
  }).catch(function () {});
})();
