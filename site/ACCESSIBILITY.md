# Accessibility — standing check (WCAG 2.2 AA)

Measured, not eyeballed: `node site/a11y_check.js` runs axe-core (WCAG 2.0/2.1/2.2 A + AA and best-practice rules) on
every built page in light and dark mode, checks the simulator under `prefers-reduced-motion`, and dumps the keyboard
tab order. Last full run: 8 Nov 2026, **0 violations** on the home page, the simulator and both posts, both themes.

## What the pass changed (8 Nov 2026)
- Contrast: the "win" green darkened (`#1f8a5b` → `#17744a`) to clear 4.5:1 on the table surface; everything else passed.
- Links inside text are underlined (color alone is not enough); nav, brand and buttons stay unstyled.
- Landmarks: `<main id="main">` on every page, a "Skip to content" link first in the tab order, `<header>`/`<footer>`.
- Tables carry `<caption>`s (visually hidden); the benchmark and data tables wrap instead of forcing horizontal scroll.
- Live regions: the True Cost results and the simulator headline/narration announce updates politely.
- The simulator chart has a role, a text alternative, and a "Show as a table" view (trade, time, typical career, median,
  10th/90th percentile) so nothing is hover-only; the narration is plain text under the chart.
- Reduced motion: the 9-second playback is skipped and the final state rendered; the Play button says so. The ledger
  row animation is already disabled under reduced motion. Nothing flashes.
- Target size: nav links padded to a 24px-tall target; buttons and inputs exceed 24×24.
- Forms: every input has a visible `<label>`; the email field's error and success messages are text.

## What stays true for anything we add
- Color never carries meaning alone: a sign, a word or an icon travels with it (the ledger shows `+`/`−`, the chart has a
  legend and a table).
- Every chart gets a text alternative and a table; every animation respects reduced motion and is user-started.
- One `<h1>`, headings in order, landmarks on every page, the skip link first.
- Text contrast ≥ 4.5:1 in both themes (validate dark mode separately; it is its own palette, not an inversion).
- No zoom lock (`maximum-scale` is never set); layouts hold at 320px and at 200% zoom.
- No cognitive tests at sign-in: one tap (Google, Apple, email link), no CAPTCHA puzzles.
- Run `node site/a11y_check.js` before a deploy; a violation is a build failure, not a backlog item.
