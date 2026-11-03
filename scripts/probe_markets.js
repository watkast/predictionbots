// read-only: which 15-minute Up/Down markets exist on Polymarket US, and how deep/active their books are (10-s samples)
'use strict';
const G = 'https://gateway.polymarket.us';
const assets = (process.env.PROBE_PREFIXES || 'cpc-btc,cpceth-eth,cpcsol-sol,cpc-sol,cpcxrp-xrp,cpc-xrp,cpcxlm-xlm,cpc-xlm,cpcdoge-doge').split(',');
const MIN = Number(process.env.PROBE_MINUTES || 12);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const slugAt = (p, T0) => { const d = new Date(T0 * 1000).toISOString(); return `${p}-updown-15m-${d.slice(0, 10)}-${d.slice(11, 13)}${d.slice(14, 16)}z`; };
const lv = a => (a || []).map(e => [Number(e.px && e.px.value != null ? e.px.value : e.px), Number(e.qty)]).filter(x => Number.isFinite(x[0]) && x[1] > 0);
(async () => {
  const T0 = Math.floor(Date.now() / 1000 / 900) * 900; const live = [];
  for (const p of assets) { const s = slugAt(p, T0); try { const r = await fetch(G + '/v1/market/slug/' + s); const t = await r.text(); console.log(JSON.stringify({ k: 'market', p, s, http: r.status, body: t.slice(0, 200) })); if (r.ok && t.length > 20) live.push(p); } catch (e) { console.log(JSON.stringify({ k: 'market', p, err: e.message })); } }
  const end = Date.now() + MIN * 60e3;
  while (Date.now() < end) {
    const T = Math.floor(Date.now() / 1000 / 900) * 900;
    for (const p of live) { const s = slugAt(p, T); try { const j = await (await fetch(G + '/v1/markets/' + s + '/book')).json(); const md = j.marketData || j; const o = lv(md.offers).sort((a, b) => a[0] - b[0]), b = lv(md.bids).sort((a, b) => b[0] - a[0]);
      console.log(JSON.stringify({ k: 'book', t: Date.now(), p, s, ask: o[0] || null, bid: b[0] || null, askDepth5: o.slice(0, 5).reduce((a, x) => a + x[1], 0), bidDepth5: b.slice(0, 5).reduce((a, x) => a + x[1], 0), levels: [o.length, b.length] })); } catch (e) { console.log(JSON.stringify({ k: 'book', p, err: e.message })); } }
    await sleep(10000);
  }
})();
