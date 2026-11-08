/* True Cost calculator — fee formulas from the venues' published schedules.
   Kalshi: fee = 0.07 × contracts × P × (1 − P), rounded up to the cent (taker; most markets).
   Polymarket US: taker fee per share = 0.0695 × P × (1 − P); resting (maker) orders pay 0.
   "No edge" means the win probability equals the price: expected gross is zero, expected net is minus the fees. */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var venue = $('tc-venue'), price = $('tc-price'), size = $('tc-size'), perWeek = $('tc-week'), bank = $('tc-bank'), hold = $('tc-hold');
  if (!venue) return;

  function feePerShare(v, p) { return (v === 'kalshi' ? 0.07 : 0.0695) * p * (1 - p); }
  function feePerTrade(v, p, dollars) {
    var shares = dollars / p;
    var raw = shares * feePerShare(v, p);
    return v === 'kalshi' ? Math.ceil(raw * 100 - 1e-9) / 100 : raw;
  }
  // P(at least one run of k losses in n independent trials with loss probability q): exact DP on run length.
  function streakProb(n, k, q) {
    var state = new Array(k).fill(0); state[0] = 1; var hit = 0;
    for (var i = 0; i < n; i++) {
      var next = new Array(k).fill(0);
      for (var r = 0; r < k; r++) {
        var m = state[r]; if (!m) continue;
        next[0] += m * (1 - q);
        if (r + 1 >= k) hit += m * q; else next[r + 1] += m * q;
      }
      state = next;
    }
    return hit;
  }
  function money(x) { return (x < 0 ? '−' : '') + '$' + Math.abs(x).toLocaleString(undefined, { maximumFractionDigits: Math.abs(x) < 10 ? 2 : 0 }); }
  function pct(x) { return (x * 100).toFixed(1) + '%'; }

  function update() {
    var v = venue.value;
    var p = Math.min(0.99, Math.max(0.01, (parseFloat(price.value) || 50) / 100));
    var dollars = Math.max(1, parseFloat(size.value) || 50);
    var tpw = Math.max(0, parseFloat(perWeek.value) || 0);
    var bankroll = Math.max(1, parseFloat(bank.value) || 500);
    var legs = hold.checked ? 1 : 2;
    var fee = feePerTrade(v, p, dollars);
    var tpm = tpw * 52 / 12;
    var feesMonth = fee * legs * tpm;
    var f = feePerShare(v, p);
    var beHold = p + f, beOut = p + 2 * f;
    var months = feesMonth > 0 ? bankroll / feesMonth : Infinity;
    var n = Math.round(tpm);
    var s5 = n ? streakProb(n, 5, 1 - p) : 0, s7 = n ? streakProb(n, 7, 1 - p) : 0;

    $('tc-fee').textContent = money(fee);
    $('tc-fee-sub').textContent = pct(fee / dollars) + ' of your ' + money(dollars) + ', from ' + (v === 'kalshi' ? "Kalshi's 7%" : "Polymarket US's 6.95%") + ' × price × (1 − price)' + (legs === 2 ? ', charged on entry and exit' : '');
    $('tc-month').textContent = money(-feesMonth);
    $('tc-month-sub').textContent = n.toLocaleString() + ' trades × ' + money(fee * legs) + '; ' + pct(feesMonth / bankroll) + ' of your bankroll, every month';
    $('tc-ruin').textContent = isFinite(months) ? (months < 1 ? 'under a month' : 'about ' + months.toFixed(1) + ' months') : 'never (no trades)';
    $('tc-ruin-sub').textContent = 'With no edge, the fees alone drain ' + money(bankroll) + ' in that time';
    $('tc-streak').textContent = n ? pct(s5) : '—';
    $('tc-streak-sub').textContent = n ? ('Chance of 5 losses in a row inside a month; 7 in a row: ' + pct(s7)) : 'Add trades per week';
    $('tc-be').textContent = pct(beHold) + ' holding to settlement, ' + pct(beOut) + ' if you trade out early';
    var share = $('tc-share'); if (share) share.dataset.text =
      'True Cost (' + (v === 'kalshi' ? 'Kalshi' : 'Polymarket US') + '): ' + money(dollars) + ' at ' + Math.round(p * 100) + '¢ costs ' + money(fee) + ' in fees per trade. ' +
      n + ' trades a month = ' + money(feesMonth) + ' in fees, ' + pct(feesMonth / bankroll) + ' of a ' + money(bankroll) + ' bankroll. Break-even win rate ' + pct(beHold) + '. predictionbots.io/#truecost';
  }
  [venue, price, size, perWeek, bank, hold].forEach(function (el) { el.addEventListener('input', update); el.addEventListener('change', update); });
  var share = $('tc-share');
  if (share) share.addEventListener('click', function () {
    var t = share.dataset.text || '';
    (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(function () { share.textContent = 'Copied'; setTimeout(function () { share.textContent = 'Copy this result'; }, 1600); }, function () { prompt('Copy:', t); });
  });
  update();
})();
