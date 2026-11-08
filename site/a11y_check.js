// Accessibility check: axe-core (WCAG 2.0/2.1/2.2 A+AA + best practices) on every page, light and dark, plus reduced
// motion on the simulator, plus a keyboard tab-order dump. Run from the repo root after `python3 site/build.py` and
// `python3 -m http.server 8765 -d site/dist &`. Needs `npm i -D playwright axe-core` once (or the preinstalled ones).
//   node site/a11y_check.js [baseUrl]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const base = process.argv[2] || 'http://localhost:8765';
const axePath = require.resolve('axe-core/axe.min.js');
const axe = fs.readFileSync(axePath, 'utf8');
const posts = fs.readdirSync(path.join(__dirname, 'dist', 'posts')).filter(f => f.endsWith('.html')).map(f => '/posts/' + f);
const pages = ['/index.html', '/simulate.html', ...posts];
(async () => {
  const b = await chromium.launch(); let total = 0;
  for (const url of pages) for (const scheme of ['light', 'dark']) {
    const p = await b.newPage({ viewport: { width: 1280, height: 900 }, colorScheme: scheme });
    await p.goto(base + url, { waitUntil: 'domcontentloaded' }); await p.waitForTimeout(1200);
    await p.addScriptTag({ content: axe });
    const r = await p.evaluate(async () => await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] } }));
    total += r.violations.length;
    console.log(`${url} [${scheme}] violations: ${r.violations.length}`);
    for (const v of r.violations) console.log(`  [${v.impact}] ${v.id}: ${v.help} (${v.nodes.length}) e.g. ${v.nodes[0].target.join(' ')}`);
    await p.close();
  }
  const k = await b.newPage({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
  await k.goto(base + '/simulate.html', { waitUntil: 'domcontentloaded' }); await k.waitForTimeout(800);
  console.log('reduced motion:', await k.evaluate(() => document.getElementById('sm-play').textContent));
  const order = [];
  for (let i = 0; i < 18; i++) { await k.keyboard.press('Tab'); order.push(await k.evaluate(() => { const a = document.activeElement; return a.id || a.textContent.trim().slice(0, 16) || a.tagName; })); }
  console.log('tab order:', order.join(' > '));
  await b.close();
  if (total) { console.error(`\n${total} violation(s)`); process.exit(1); }
  console.log('\nno violations');
})();
