#!/usr/bin/env node
// Phone layout, measured in the engines phones run: WebKit with an iPhone profile (what Safari is) and Chromium with
// an Android one. A desktop browser squeezed narrow is not a phone, and a local build is not what visitors are served:
// on 13 Nov 2026 the owner's iPhone showed a header we believed fixed.
//
//   node site/phone_check.js https://predictmenot.com shots            (after a deploy; needs playwright + webkit)
//   python3 -m http.server 8765 -d site/dist &
//   node site/phone_check.js http://localhost:8765 shots --engines=chromium     (a local build, one engine)
//
// Fails (exit 1) when a page is wider than the screen, the header is taller than two rows, the header's links take
// more than one row, a header control is too small to tap, or the page text is smaller than 15px. Prints the
// cache headers the browser was given for the page and its stylesheet, and saves a screenshot per page and device.
let pw;
try { pw = require('playwright'); } catch (e) { pw = require('playwright-core'); }
const fs = require('fs');
const path = require('path');

const base = (process.argv[2] || 'https://predictmenot.com').replace(/\/$/, '');
const out = process.argv[3] || 'shots';
const only = ((process.argv.find(a => a.startsWith('--engines=')) || '').split('=')[1] || '').split(',').filter(Boolean);
const DEVICES = [
  { name: 'iphone', engine: 'webkit', profile: 'iPhone 15' },
  { name: 'iphone-se', engine: 'webkit', profile: 'iPhone SE' },
  { name: 'android', engine: 'chromium', profile: 'Pixel 7' },
  { name: 'android-small', engine: 'chromium', profile: 'Galaxy S8' },
];
const PAGES = ['/', '/simulate.html', '/reality.html', '/markets/'];
const MAX_HEADER = 124;       // brand row + one row of links

function measure() {
  const de = document.documentElement, vw = de.clientWidth;
  const h = document.querySelector('header.top');
  const links = h ? [...h.querySelectorAll('nav a')] : [];
  const scrolls = e => e.closest('nav, [role=region], pre, .ledger-wrap, .table-wrap');
  const wide = [...document.querySelectorAll('body *')].filter(e => {
    const r = e.getBoundingClientRect();
    return r.width > 0 && r.right > vw + 1 && !scrolls(e);
  }).slice(0, 3).map(e => e.tagName.toLowerCase() + (e.id ? '#' + e.id : e.className ? '.' + String(e.className).split(' ')[0] : ''));
  const small = h ? [...h.querySelectorAll('a, label, button')].filter(e => {
    const r = e.getBoundingClientRect();
    return r.width > 0 && (r.height < 24 || r.width < 24);
  }).map(e => (e.textContent || '').trim().slice(0, 16)) : [];
  const theme = document.querySelector('.theme');
  return {
    vw, scrollW: de.scrollWidth, headerH: h ? Math.round(h.getBoundingClientRect().height) : null,
    navRows: new Set(links.map(a => Math.round(a.getBoundingClientRect().top))).size, navLinks: links.length,
    themeRight: theme ? Math.round(theme.getBoundingClientRect().right) : null,
    wide, small, bodyFont: parseFloat(getComputedStyle(document.body).fontSize),
  };
}

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const rows = [], fails = [], headers = {};
  for (const d of DEVICES) {
    const engine = only.length ? only[0] : d.engine;
    if (only.length && !only.includes(engine)) continue;
    const browser = await pw[engine].launch();
    const { defaultBrowserType, ...profile } = pw.devices[d.profile];
    const ctx = await browser.newContext({ ...profile, deviceScaleFactor: 2 });
    const page = await ctx.newPage();
    page.on('response', r => {
      const u = r.url();
      if (u.startsWith(base) && /\/(styles\.css|theme\.js)(\?|$)/.test(u)) {
        const hd = r.headers();
        headers[u.replace(base, '')] = `${r.status()} cache-control: ${hd['cache-control'] || '(none)'}; age: ${hd['age'] || '-'}; cf-cache-status: ${hd['cf-cache-status'] || '-'}`;
      }
    });
    // one page of each kind: the fixed ones, then a post, a guide and a market page found by following the site's own links
    const pages = [...PAGES];
    try {
      const home = await page.goto(base + '/', { waitUntil: 'load', timeout: 45000 });
      const hd = home.headers();
      headers['/'] = `${home.status()} cache-control: ${hd['cache-control'] || '(none)'}; age: ${hd['age'] || '-'}; cf-cache-status: ${hd['cf-cache-status'] || '-'}`;
      const found = await page.evaluate(() => [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')));
      for (const re of [/^\/posts\/[^#?]+\.html$/, /^\/learn\/[^#?]+\.html$/]) { const m = found.find(x => re.test(x)); if (m) pages.push(m); }
      await page.goto(base + '/markets/', { waitUntil: 'load', timeout: 45000 });
      const mk = await page.evaluate(() => [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')));
      const inMarkets = mk.filter(x => /^\/markets\/(kalshi|pmus)\/[^/]+\/$/.test(x));
      const category = inMarkets.find(x => /\/c-[^/]+\/$/.test(x)), series = inMarkets.find(x => !/\/c-[^/]+\/$/.test(x));
      if (category) pages.push(category);
      if (series) pages.push(series);
    } catch (e) { fails.push(`${d.name}: could not walk the site from ${base}/ (${String(e.message).split('\n')[0]})`); }

    for (const p of pages) {
      const slug = p === '/' ? 'home' : p.replace(/^\/|\/$|\.html$/g, '').replace(/[^a-z0-9]+/gi, '-').slice(0, 40);
      try {
        const resp = await page.goto(base + p, { waitUntil: 'load', timeout: 45000 });
        await page.waitForTimeout(600);
        const m = await page.evaluate(measure);
        const bad = [];
        if (!resp || resp.status() !== 200) bad.push(`answered ${resp ? resp.status() : 'nothing'}`);
        if (m.headerH === null) bad.push('no site header on the page');
        if (m.scrollW > m.vw + 1) bad.push(`page is ${m.scrollW}px wide on a ${m.vw}px screen (${m.wide.join(', ') || 'no single element found'})`);
        if (m.headerH !== null && m.headerH > MAX_HEADER) bad.push(`header is ${m.headerH}px tall (limit ${MAX_HEADER})`);
        if (m.navRows > 1) bad.push(`header links take ${m.navRows} rows`);
        if (m.themeRight !== null && m.themeRight > m.vw + 1) bad.push(`theme switch ends at ${m.themeRight}px, off a ${m.vw}px screen`);
        if (m.small.length) bad.push(`too small to tap: ${m.small.join(', ')}`);
        if (m.bodyFont < 15) bad.push(`body text is ${m.bodyFont}px`);
        rows.push({ device: d.name, engine, page: p, vw: m.vw, headerH: m.headerH, navRows: m.navRows, ok: !bad.length, bad });
        for (const b of bad) fails.push(`${d.name} (${engine}) ${p}: ${b}`);
        await page.screenshot({ path: path.join(out, `${d.name}-${slug}.png`) });      // the first screen; the home page is too long for one image
      } catch (e) {
        fails.push(`${d.name} (${engine}) ${p}: ${String(e.message).split('\n')[0]}`);
      }
    }
    await browser.close();
  }
  console.log(`### Phone check: ${base}\n`);
  console.log('| Device | Engine | Page | Screen | Header | Link rows | Result |\n| --- | --- | --- | --- | --- | --- | --- |');
  for (const r of rows) console.log(`| ${r.device} | ${r.engine} | \`${r.page}\` | ${r.vw}px | ${r.headerH}px | ${r.navRows} | ${r.ok ? 'ok' : 'FAIL: ' + r.bad.join('; ')} |`);
  console.log('\nCache headers the browser was given:\n');
  for (const [u, v] of Object.entries(headers)) console.log(`- \`${u}\` ${v}`);
  if (!rows.length) fails.push('no page was measured');
  if (fails.length) { console.log(`\n**${fails.length} problem(s)**\n`); for (const f of fails) console.log(`- ${f}`); process.exit(1); }
  console.log(`\nAll ${rows.length} page renders fit their screens.`);
})().catch(e => { console.error(e); process.exit(1); });
