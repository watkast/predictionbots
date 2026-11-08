/* "Same money, elsewhere": the one card that puts the expected result of trading next to what the same money does in
   a government-guaranteed instrument, then the honest alternatives when the real problem is needing cash, then help.
   Rates come from site/data/rates.json (official sources, fetched at build time, dated). No affiliate links here. */
(function () {
  var rates = null;
  function fmt(x) { return '$' + Math.abs(x).toLocaleString(undefined, { maximumFractionDigits: Math.abs(x) < 10 ? 2 : 0 }); }
  function pct(x) { return (x * 100).toFixed(2).replace(/\.?0+$/, '') + '%'; }
  function render(host, a) {
    var months = a.months || 12;
    var loss = a.monthlyLoss || 0, bank = a.bank || 0;
    var tb = rates && rates.tbill_4w, ib = rates && rates.ibond;
    var tbRow = tb != null ? '<tr><th scope="row">The same ' + fmt(bank) + ' in 4-week Treasury bills, rolled</th><td class="num win">+' + fmt(bank * tb / 12) + ' a month</td><td>' + pct(tb) + ' a year, backed by the U.S. government; <a href="https://www.treasurydirect.gov/marketable-securities/treasury-bills/" rel="noopener">TreasuryDirect</a>, no minimum beyond $100, no fee. Rate as of ' + rates.tbill_4w_date + '.</td></tr>' :
      '<tr><th scope="row">The same ' + fmt(bank) + ' in 4-week Treasury bills</th><td class="num">—</td><td>Current rate at <a href="https://www.treasurydirect.gov/marketable-securities/treasury-bills/" rel="noopener">TreasuryDirect</a>; backed by the U.S. government, no fee.</td></tr>';
    var ibRow = ib != null ? '<tr><th scope="row">The same ' + fmt(bank) + ' in Series I savings bonds</th><td class="num win">+' + fmt(bank * ib / 12) + ' a month</td><td>' + pct(ib) + ' composite rate (' + rates.ibond_period + '), inflation-linked, cannot be sold for 12 months, which is the point; <a href="https://www.treasurydirect.gov/savings-bonds/i-bonds/" rel="noopener">TreasuryDirect</a>.</td></tr>' :
      '<tr><th scope="row">The same ' + fmt(bank) + ' in Series I savings bonds</th><td class="num">—</td><td>Current composite rate at <a href="https://www.treasurydirect.gov/savings-bonds/i-bonds/" rel="noopener">TreasuryDirect</a>; inflation-linked, locked for 12 months.</td></tr>';
    host.innerHTML =
      '<h3>Same money, elsewhere</h3>' +
      '<div class="ledger-wrap"><table class="ledger cells"><caption>Expected monthly result of trading at these settings next to the same money in government-guaranteed instruments</caption>' +
      '<thead><tr><th scope="col">Where the money is</th><th scope="col" class="num">Expected result</th><th scope="col">What that is</th></tr></thead><tbody>' +
      '<tr><th scope="row">' + fmt(bank) + ' trading this market at your pace</th><td class="num loss">−' + fmt(loss) + ' a month</td><td>The fee drag with no edge; wins and losses average out, the fee does not. ' + (loss > 0 ? 'Gone in about ' + (bank / loss).toFixed(1) + ' months.' : '') + '</td></tr>' +
      tbRow + ibRow + '</tbody></table></div>' +
      '<p class="fine">Not investment advice; an example of what a guaranteed instrument pays, from official rates dated above. We are not paid by anyone for these links.</p>' +
      '<h3>Need money this week, not in four?</h3>' +
      '<p>A prediction market is the worst place to turn $50 into $100 fast: the expected result is minus the fee. Things that pay real money quickly, with the honest hourly range people report after costs:</p>' +
      '<ul><li><b>Driving or delivery</b> (Uber, Lyft, DoorDash, Instacart): instant or same-day cashout; roughly $12 to $25 an hour after fuel and wear, depending on city and hours. The car pays for part of it.</li>' +
      '<li><b>Selling what you already own</b> (Facebook Marketplace, eBay, Craigslist): the fastest real money most people have; nothing to learn.</li>' +
      '<li><b>Task and labor apps</b> (TaskRabbit, Thumbtack): $20 to $50 an hour for moving, assembly and cleaning, paid within days.</li>' +
      '<li><b>Research studies and user tests</b> (Prolific, UserTesting): $8 to $20 an hour, paid weekly; small, but a real number rather than a negative one.</li>' +
      '<li><b>Skip:</b> survey sites paying under $3 an hour, "get paid to trade" bots, and any offer that needs a deposit first.</li></ul>' +
      '<p class="fine">No referral links; nobody pays us for this list.</p>' +
      '<h3>If this isn\'t about the money anymore</h3>' +
      '<p>If you keep coming back to the app when you said you wouldn\'t, if the amounts have grown, or if you\'ve hidden it from someone, you are describing something millions of people in the U.S. are living with right now, and there is nothing weak about saying so. The people on the line below have heard it all and will not judge you.</p>' +
      '<ul><li><b>1-800-GAMBLER</b> (1-800-426-2537): call or text, free, confidential, 24/7, anywhere in the U.S. Chat at <a href="https://www.1800gambler.net" rel="noopener">1800gambler.net</a>.</li>' +
      '<li><a href="https://www.ncpgambling.org/help-treatment/help-by-state/" rel="noopener">Help in your state</a> (National Council on Problem Gambling): local counselors, often free.</li>' +
      '<li><a href="https://www.gamblersanonymous.org/ga/locations" rel="noopener">Gamblers Anonymous meetings</a>, in person and online, today.</li>' +
      '<li>Both venues offer self-exclusion and deposit limits in account settings; setting one tonight costs nothing.</li></ul>' +
      '<p class="fine">Nothing on this site is medical or financial advice. If you are in immediate danger, call or text 988. <a href="/learn/what-the-research-says.html">What the research says about losing money here →</a></p>';
  }
  function go(host, a) { if (rates !== null) return render(host, a); fetch('/data/rates.json', { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; }).then(function (j) { rates = j || {}; render(host, a); }); }
  window.PB = window.PB || {};
  window.PB.elsewhere = function (id, a) { var h = document.getElementById(id); if (h) go(h, a); };
})();
