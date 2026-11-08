"""Market pages: one static page per market series on Kalshi and Polymarket US.

Each page says, in plain words, what the market is, what the market price implies, the fee at that price from the
venue's published formula, the win rate needed to break even, and a "luck needed" meter: the share of outcomes the
market itself cannot call, 2 * min(p, 1 - p). Crypto minute markets read 100% by construction (50/50 at the open,
unforecastable at that horizon). Nothing here is advice; every number links to its source.

Public endpoints only, no keys:
  Kalshi      GET https://external-api.kalshi.com/trade-api/v2/markets?status=open&limit=1000&cursor=...
              GET .../trade-api/v2/series/{ticker}            (title, category, fee_type, settlement sources)
  Polymarket  GET https://gateway.polymarket.us/v1/markets?limit=...   (tolerant pager; shapes logged)

Usage:
  python scripts/market_pages.py build --out site/dist/markets [--max-series N] [--venue kalshi|pmus|both]
  python scripts/market_pages.py selftest
"""
from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    import httpx
except Exception:  # selftest without httpx
    httpx = None

KALSHI = "https://external-api.kalshi.com/trade-api/v2"
PMUS = "https://gateway.polymarket.us"
SITE = "https://predictionbots.io"
KALSHI_TAKER, PMUS_TAKER = 0.07, 0.095   # Polymarket US: Θ for accounts under $10k of 30-day taker volume (schedule of 6 Nov 2026)
LOG = lambda *a: print(*a, file=sys.stderr)


# ----------------------------------------------------------------------------- arithmetic
def fee_per_contract(venue: str, p: float) -> float:
    return (KALSHI_TAKER if venue == "kalshi" else PMUS_TAKER) * p * (1 - p)


def fee_on(venue: str, p: float, dollars: float) -> float:
    return (dollars / p) * fee_per_contract(venue, p)


def breakeven(venue: str, p: float) -> float:
    return p + fee_per_contract(venue, p)


def luck(p: float) -> float:
    return 2 * min(p, 1 - p)


def luck_words(l: float, crypto_minutes: bool) -> tuple[str, str]:
    if crypto_minutes:
        return "100%", "A coin flip with a cover charge. Skill contributes nothing at this horizon; the fee always does."
    pct = f"{round(l * 100)}%"
    if l >= 0.8:
        return pct, "Mostly luck. The market itself expects the favorite to lose this often; the fee is the only certainty."
    if l >= 0.4:
        return pct, "Half luck. The favorite is clear, the fee is not small, and the payout on the favorite is thin."
    if l >= 0.1:
        return pct, "Mostly decided. You are paying a fee to collect a few cents the market already agrees on."
    return pct, "Decided. The remaining cents are someone's rent for carrying the one-in-a-thousand flip."


def pct(x: float) -> str:
    return f"{round(x * 100)}%"


def cents(p: float) -> str:
    return f"{round(p * 100)}¢"


# ----------------------------------------------------------------------------- fetch
class Http:
    def __init__(self, pace: float = 0.25):
        self.c = httpx.Client(timeout=30, headers={"User-Agent": "predictionbots-market-pages/1.0 (+https://predictionbots.io)"})
        self.pace = pace
        self.last = 0.0

    def get(self, url: str, params=None, tries: int = 3):
        for i in range(tries):
            dt = time.time() - self.last
            if dt < self.pace:
                time.sleep(self.pace - dt)
            self.last = time.time()
            try:
                r = self.c.get(url, params=params)
                if r.status_code == 200:
                    return r.json()
                if r.status_code in (400, 404):
                    LOG(f"  {url} {params} -> {r.status_code} {r.text[:160]}")
                    return None
                LOG(f"  {url} -> {r.status_code}; retry")
                time.sleep(1.5 * (i + 1) + (float(r.headers.get("Retry-After", 0)) if r.status_code == 429 else 0))
            except Exception as e:
                LOG(f"  {url} -> {e!r}; retry")
                time.sleep(1.5 * (i + 1))
        return None


def _num(x, default=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def kalshi_price(m: dict) -> float | None:
    """YES mid in [0,1] from dollar strings or legacy cents; last price as fallback."""
    bid = _num(m.get("yes_bid_dollars"))
    ask = _num(m.get("yes_ask_dollars"))
    if bid is None and m.get("yes_bid") is not None:
        bid = _num(m.get("yes_bid"), 0) / 100
    if ask is None and m.get("yes_ask") is not None:
        ask = _num(m.get("yes_ask"), 0) / 100
    if bid is not None and ask is not None and 0 < ask <= 1 and 0 <= bid < 1 and bid <= ask:
        return (bid + ask) / 2
    last = _num(m.get("last_price_dollars"))
    if last is None and m.get("last_price") is not None:
        last = _num(m.get("last_price"), 0) / 100
    return last if last is not None and 0 < last < 1 else None


def fetch_kalshi(h: Http, max_series: int | None) -> dict[str, dict]:
    markets, cursor, pages = [], None, 0
    while True:
        j = h.get(f"{KALSHI}/markets", {"status": "open", "limit": 1000, "cursor": cursor, "mve_filter": "exclude"})
        if not j:
            break
        got = j.get("markets") or []
        markets.extend(got)
        cursor = j.get("cursor")
        pages += 1
        if not cursor or not got or pages > 400:
            break
    LOG(f"kalshi: {len(markets)} open markets in {pages} pages")
    by_series: dict[str, dict] = defaultdict(lambda: {"venue": "kalshi", "markets": [], "series": {}})
    for m in markets:
        st = m.get("series_ticker") or (m.get("event_ticker") or m.get("ticker") or "").split("-", 1)[0]
        if not st:
            continue
        by_series[st]["markets"].append(m)
    tickers = sorted(by_series, key=lambda t: -sum(_num(x.get("volume_24h_fp", x.get("volume_24h")), 0) or 0 for x in by_series[t]["markets"]))
    if max_series:
        tickers = tickers[:max_series]
    out = {}
    for i, t in enumerate(tickers):
        s = h.get(f"{KALSHI}/series/{t}")
        s = (s or {}).get("series", s) or {}
        rec = by_series[t]
        rec["series"] = s
        rec["ticker"] = t
        out[t] = rec
        if i % 100 == 0:
            LOG(f"  kalshi series {i}/{len(tickers)}")
    return out


def fetch_pmus(h: Http, max_series: int | None) -> dict[str, dict]:
    """Offset pager over /v1/markets (active, not closed); the API returns {"markets": [...]} with no cursor."""
    markets, offset, pages, seen = [], 0, 0, set()
    while True:
        j = h.get(f"{PMUS}/v1/markets", {"limit": 500, "offset": offset, "active": "true", "closed": "false"})
        items = (j or {}).get("markets") or []
        if pages == 0 and items:
            LOG("pmus market keys:", sorted(items[0].keys()))
        new = [m for m in items if m.get("id") not in seen]
        for m in new:
            seen.add(m.get("id"))
        markets.extend(new)
        pages += 1
        if not items or not new or pages > 200:
            break
        offset += len(items)
    LOG(f"pmus: {len(markets)} markets in {pages} pages")
    by_series: dict[str, dict] = defaultdict(lambda: {"venue": "pmus", "markets": [], "series": {}})
    for m in markets:
        if str(m.get("status") or "").upper() not in ("OPEN", "MARKET_STATUS_OPEN", ""):
            continue
        slug = str(m.get("slug") or "")
        terms = m.get("assetPriceTerms") or {}
        if terms:
            sym = str(((terms.get("asset") or {}).get("symbol")) or "").lower() or re.sub(r"^cpc-?", "", slug.split("-updown-")[0])
            hz = str(terms.get("horizon") or "").lower().replace("asset_price_horizon_", "").replace("horizon_", "") or (slug.split("-updown-")[1].split("-")[0] if "-updown-" in slug else "")
            key = f"{sym}-updown-{hz}"
        else:
            key = str(m.get("seriesSlug") or m.get("eventSlug") or (m.get("event") or {}).get("slug") or re.sub(r"-\d{4}-\d{2}-\d{2}.*$", "", slug) or slug)
        if not key:
            continue
        by_series[key]["markets"].append(m)
    keys = sorted(by_series, key=lambda k: -len(by_series[k]["markets"]))
    if max_series:
        keys = keys[:max_series]
    return {k: dict(by_series[k], ticker=k) for k in keys}


# ----------------------------------------------------------------------------- normalise
def norm_kalshi(rec: dict) -> dict:
    s, ms = rec["series"], rec["markets"]
    rows = []
    for m in ms:
        p = kalshi_price(m)
        rows.append({"title": m.get("title") or m.get("ticker"), "sub": m.get("yes_sub_title") or m.get("subtitle") or "",
                     "p": p, "volume": _num(m.get("volume_fp", m.get("volume")), 0) or 0,
                     "close": m.get("close_time") or m.get("expected_expiration_time") or "", "rules": m.get("rules_primary") or ""})
    cat = (s.get("category") or ms[0].get("category") or "").strip()
    title = s.get("title") or (ms[0].get("title") or rec["ticker"])
    fee_type = s.get("fee_type") or ""
    crypto_minutes = bool(re.search(r"(BTC|ETH|SOL|XRP|DOGE)", rec["ticker"], re.I) and re.search(r"(5M|15M|1H|HOUR|MIN)", rec["ticker"] + " " + title, re.I))
    rules = next((r["rules"] for r in rows if r["rules"]), "")
    sources = [x.get("name") or x.get("url") for x in (s.get("settlement_sources") or []) if isinstance(x, dict)]
    return {"venue": "kalshi", "venue_name": "Kalshi", "slug": rec["ticker"].lower(), "title": title, "category": cat,
            "rules": rules, "sources": sources, "fee_note": ("Makers also pay a smaller fee on this series." if "maker" in fee_type else "Resting orders pay no fee on this series."),
            "rows": rows, "crypto_minutes": crypto_minutes, "url": f"https://kalshi.com/markets/{rec['ticker'].lower()}",
            "frequency": s.get("frequency") or ""}


def norm_pmus(rec: dict) -> dict:
    ms = rec["markets"]
    rows = []
    for m in ms:
        p = None
        sides = m.get("marketSides")
        if isinstance(sides, list) and sides:
            p = _num((sides[0] or {}).get("price"))
        if p is None:
            bb, ba = _num(m.get("bestBidQuote")), _num(m.get("bestAskQuote"))
            if bb is not None and ba is not None and 0 < ba <= 1:
                p = (bb + ba) / 2
        for k in ("yesPrice", "lastTradePrice", "price", "midPrice"):
            if p is not None:
                break
            p = _num(m.get(k))
        op = m.get("outcomePrices")
        if isinstance(op, str):
            try:
                op = json.loads(op)
            except Exception:
                op = None
        if p is None and isinstance(op, list) and op:
            p = _num(op[0])
        if p is not None and p > 1:
            p = p / 100
        rows.append({"title": m.get("question") or m.get("title") or m.get("slug"), "sub": "", "p": p if p and 0 < p < 1 else None,
                     "volume": _num(m.get("volume"), 0) or 0, "close": m.get("endDate") or m.get("closeTime") or m.get("windowEnd") or "",
                     "rules": m.get("description") or m.get("rules") or ""})
    key = rec["ticker"]
    crypto_minutes = "-updown-" in key
    if crypto_minutes:
        sym, hz = key.split("-updown-")
        hz_words = {"5m": "5 minutes", "15m": "15 minutes", "1h": "1 hour", "4h": "4 hours", "1d": "1 day"}.get(hz, hz)
        title = f"{sym.upper()} Up or Down, {hz_words}"
        cat = "Crypto"
        rules = (f"A new market every {hz_words}. \"Up\" pays $1 if the CF Benchmarks {sym.upper()} index, averaged over the last 60 seconds of the window, "
                 f"is above the price at the open; \"Down\" pays $1 otherwise.")
    else:
        q = str(ms[0].get("question") or ms[0].get("title") or "").strip()
        # a sports event slug like aec-nfl-hou-ten: title from the question ("Houston vs Tennessee ...")
        title = (ms[0].get("eventTitle") or (q.split("?")[0].strip() if q else "") or key).strip()
        cat = str(ms[0].get("category") or "").strip().capitalize()
        rules = next((r["rules"] for r in rows if r["rules"]), "")
    return {"venue": "pmus", "venue_name": "Polymarket US", "slug": re.sub(r"[^a-z0-9-]+", "-", key.lower()).strip("-"), "title": title,
            "category": cat, "rules": rules, "sources": [], "fee_note": "Resting (maker) orders pay nothing; orders that take liquidity pay the fee.",
            "rows": rows, "crypto_minutes": crypto_minutes, "url": f"https://polymarket.us/", "frequency": ""}


# ----------------------------------------------------------------------------- render
CSS = "/styles.css"
HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><script>try{{var t=localStorage.getItem("pb-theme");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}"><link rel="canonical" href="{canon}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet"><link rel="stylesheet" href="{css}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<script type="application/ld+json">{ld}</script>
<style>.meter{{display:flex;height:10px;border-radius:5px;overflow:hidden;background:var(--rule)}}.meter i{{display:block;background:var(--loss)}}.kpis3{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}}.kpi .big{{font-size:28px;font-weight:600;letter-spacing:-.015em}}.crumbs{{font-size:14px;color:var(--ink-2);margin:18px 0 0}}</style></head>
<body><a class="skip" href="#main">Skip to content</a><div class="wrap">
<header class="top"><a class="brand" href="/">PredictionBots</a><nav><a href="/#truecost">True Cost</a><a href="/simulate.html">Simulator</a><a href="/#benchmark">Bot benchmark</a><a href="/markets/">Markets</a><a href="/#honest">How we're paid</a></nav><fieldset class="theme" id="theme"><legend>Theme</legend><label><input type="radio" name="theme" value="system" checked> System</label><label><input type="radio" name="theme" value="dark"> Dark</label><label><input type="radio" name="theme" value="light"> Light</label></fieldset></header>
<main id="main">"""
FOOT = """</main>
<footer><p>Prices come from the venue's public market data and change constantly; fees follow the venue's published schedule; the arithmetic is ours and you can check it. Nothing on this page is investment advice. Most participants in prediction markets lose money. Problem gambling help: 1-800-GAMBLER.</p>
<p>Code and data: <a href="https://github.com/watkast/predictionbots">github.com/watkast/predictionbots</a> · hello@predictionbots.io</p></footer></div><script src="/theme.js" defer></script></body></html>"""


def esc(x) -> str:
    return html.escape(str(x or ""), quote=True)


def fmt_close(iso: str) -> str:
    try:
        d = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        return d.strftime("%b %d, %H:%M UTC")
    except Exception:
        return str(iso or "")


def render_series(s: dict, built: str) -> str:
    rows = [r for r in s["rows"] if r["p"] is not None]
    rows.sort(key=lambda r: -r["volume"])
    ps = sorted(r["p"] for r in rows)
    if not ps:
        ps = [r["p"] for r in s["rows"] if r["p"] is not None]
    p = ps[len(ps) // 2] if ps else 0.5
    v = s["venue"]
    fee1 = fee_per_contract(v, p)
    fee50 = fee_on(v, p, 50)
    be = breakeven(v, p)
    l = 1.0 if s["crypto_minutes"] else (luck(p) if ps else 1.0)
    lpct, ltext = luck_words(l, s["crypto_minutes"])
    real = "50%" if s["crypto_minutes"] else pct(p)
    real_text = ("Five-minute and fifteen-minute moves have no measurable predictability; our own 30-day test of the most popular entry rule lost on 76% of trades."
                 if s["crypto_minutes"] else "We have no independent base rate for this market yet; the market's own price is the best public forecast, and the fee sits on top of it.")
    title = f"{s['title']} on {s['venue_name']}: the odds, the fee, and how much luck you need"
    desc = f"{s['venue_name']} {s['title']}: market price {pct(p)}, fee {cents(fee1)} a contract at that price, break-even win rate {pct(be)}, luck needed {lpct}. Plain words, no account."
    canon = f"{SITE}/markets/{v}/{s['slug']}/"
    faq = [{"@type": "Question", "name": f"What is the {s['title']} market on {s['venue_name']}?", "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\s+", " ", s["rules"] or f"A {s['venue_name']} market in the {s['category'] or 'general'} category. Contracts pay $1 if the stated outcome happens and nothing otherwise.")[:600]}},
           {"@type": "Question", "name": f"What is the fee on {s['venue_name']} for this market?", "acceptedAnswer": {"@type": "Answer", "text": f"At the current typical price of {cents(p)}, about {cents(fee1)} per contract ({'7% × price × (1 − price), rounded up, on orders that take liquidity' if v == 'kalshi' else '9.5% × price × (1 − price) per share on orders that take liquidity, the rate for accounts under $10,000 of 30-day volume since 6 November 2026; 6.95% in a new account\'s first week'}). On a $50 trade that is about ${fee50:.2f}."}},
           {"@type": "Question", "name": "What win rate do I need to break even?", "acceptedAnswer": {"@type": "Answer", "text": f"About {pct(be)} if you hold to settlement, against a market price of {pct(p)}. The gap is the fee."}}]
    ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq, "dateModified": built}, ensure_ascii=False)
    out = [HEAD.format(title=esc(title), desc=esc(desc), canon=canon, css=CSS, ld=ld)]
    out.append(f'<p class="crumbs"><a href="/markets/">Markets</a> › {esc(s["venue_name"])} › {esc(s["category"] or "Markets")}</p>')
    out.append(f'<div class="hero" style="padding-top:18px"><h1 style="max-width:26ch">{esc(s["title"])} <span style="color:var(--ink-2);font-weight:500">on {esc(s["venue_name"])}</span></h1>')
    out.append(f'<p class="lede">{esc(s["rules"][:700]) if s["rules"] else esc("Contracts pay $1 if the stated outcome happens and nothing otherwise. The price is the market\'s probability; the fee is the venue\'s.")}</p>')
    if s["sources"]:
        out.append(f'<p class="fine">Settles on: {esc(", ".join(map(str, s["sources"])))}.</p>')
    out.append("</div>")
    out.append('<section><div class="kpis3">')
    out.append(f'<div class="kpi"><div class="k">Market says (typical open contract)</div><div class="big">{pct(p)}</div><div class="s">Median YES price across {len(rows)} open contract{"s" if len(rows) != 1 else ""}, {built}.</div></div>')
    out.append(f'<div class="kpi"><div class="k">Real-world odds</div><div class="big">{real}</div><div class="s">{esc(real_text)}</div></div>')
    out.append(f'<div class="kpi" style="background:var(--ink);color:var(--paper)"><div class="k" style="color:#aab2bf">Luck needed meter</div><div class="big">{lpct} 😈</div><div class="meter" aria-hidden="true"><i style="width:{round(l*100)}%"></i></div><div class="s" style="color:#aab2bf">{esc(ltext)}</div></div>')
    out.append("</div></section>")
    out.append('<section><h2>The cover charge</h2>')
    out.append('<div class="ledger-wrap"><table class="ledger cells"><caption>Fee and break-even by purchase price</caption><thead><tr><th scope="col">If you buy at</th><th scope="col" class="num">Fee per contract</th><th scope="col" class="num">On $50</th><th scope="col" class="num">Win rate to break even</th></tr></thead><tbody>')
    for q in sorted({0.3, 0.5, 0.7, 0.9, round(p, 2)}):
        if 0 < q < 1:
            mark = " <b>(now)</b>" if abs(q - round(p, 2)) < 1e-9 else ""
            out.append(f'<tr><th scope="row">{cents(q)}{mark}</th><td class="num">{fee_per_contract(v, q)*100:.1f}¢</td><td class="num">${fee_on(v, q, 50):.2f}</td><td class="num">{breakeven(v, q)*100:.1f}%</td></tr>')
    out.append("</tbody></table></div>")
    out.append(f'<p class="fine">{esc(s["fee_note"])} Formula: {"7% × contracts × price × (1 − price), rounded up, on orders that take liquidity" if v == "kalshi" else "9.5% × price × (1 − price) per share on orders that take liquidity (accounts under $10,000 of 30-day volume; 6.95% in a new account's first week and above $250,000)"}. Break-even assumes you hold to settlement; trading out early pays the fee twice.</p>')
    out.append(f'<p><a class="btn dark" href="/simulate.html?venue={v}&price={round(p*100)}&stake=20&week=20&bank=500">How long until your balance is $0 in this market? →</a></p></section>')
    if rows:
        out.append('<section><h2>Open contracts right now</h2><div class="ledger-wrap"><table class="ledger cells"><caption>Open contracts in this series with price, implied probability, volume and close time</caption><thead><tr><th scope="col">Contract</th><th scope="col" class="num">YES price</th><th scope="col" class="num">Implied</th><th scope="col" class="num">Fee at this price</th><th scope="col" class="num">Luck needed</th><th scope="col" class="num">Volume</th><th scope="col">Closes</th></tr></thead><tbody>')
        for r in rows[:40]:
            q = r["p"]
            lk = "100%" if s["crypto_minutes"] else pct(luck(q))
            out.append(f'<tr><td>{esc(r["title"])}{(" · " + esc(r["sub"])) if r["sub"] else ""}</td><td class="num">{cents(q)}</td><td class="num">{pct(q)}</td><td class="num">{fee_per_contract(v, q)*100:.1f}¢</td><td class="num">{lk}</td><td class="num">{int(r["volume"]):,}</td><td>{esc(fmt_close(r["close"]))}</td></tr>')
        out.append("</tbody></table></div>")
        if len(rows) > 40:
            out.append(f'<p class="fine">Showing the 40 most traded of {len(rows)} open contracts.</p>')
        out.append("</section>")
    out.append('<section><h2>Who actually wins this market</h2><ul><li>Whoever posts the resting orders and collects the spread' + (' without paying a fee' if v == 'pmus' or 'Resting orders pay no fee' in s['fee_note'] else '') + '.</li><li>The venue, on every fee.</li><li>Not, on average, the person clicking buy because the chart is going their way. <a href="/#ledger">That was us.</a></li></ul>')
    out.append('<p>Still want to play? <a href="/#deal">Read the deal first</a>: what the account asks for, what the bonus really is, and whether we are paid. Vendors sell bots for markets like this one; see the <a href="/#benchmark">bot benchmark</a> before you pay for one.</p></section>')
    out.append(FOOT)
    return "".join(out)


def render_index(series: list[dict], built: str) -> str:
    title = "Every market on Kalshi and Polymarket US: the odds, the fee, and how much luck you need"
    desc = "One plain-language page per market series: what the market says, the real-world odds, the fee at that price, and a luck-needed meter."
    ld = json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": desc, "dateModified": built})
    out = [HEAD.format(title=esc(title), desc=esc(desc), canon=f"{SITE}/markets/", css=CSS, ld=ld)]
    out.append(f'<div class="hero"><h1 style="max-width:22ch">Every market, with its odds, its fee and the luck it needs</h1><p class="lede">{esc(desc)} Rebuilt {built}. Crypto minutes read "pure luck"; everything else reads the share of outcomes the market itself cannot call.</p></div>')
    for venue_name in ("Kalshi", "Polymarket US"):
        rows = [s for s in series if s["venue_name"] == venue_name]
        if not rows:
            continue
        out.append(f'<section><h2>{venue_name} <span style="color:var(--ink-2);font-weight:500">· {len(rows)} series</span></h2>')
        bycat = defaultdict(list)
        for s in rows:
            bycat[s["category"] or "Other"].append(s)
        for cat in sorted(bycat):
            out.append(f'<h3>{esc(cat)}</h3><div class="ledger-wrap"><table class="ledger cells"><caption>{esc(venue_name)} {esc(cat)} series</caption><thead><tr><th scope="col">Series</th><th scope="col" class="num">Open</th><th scope="col" class="num">Typical price</th><th scope="col" class="num">Fee</th><th scope="col" class="num">Luck needed</th></tr></thead><tbody>')
            for s in sorted(bycat[cat], key=lambda x: -sum(r["volume"] for r in x["rows"])):
                ps = sorted(r["p"] for r in s["rows"] if r["p"] is not None)
                p = ps[len(ps) // 2] if ps else None
                lk = "100%" if s["crypto_minutes"] else (pct(luck(p)) if p is not None else "—")
                out.append(f'<tr><td><a href="/markets/{s["venue"]}/{s["slug"]}/">{esc(s["title"])}</a></td><td class="num">{len(s["rows"])}</td><td class="num">{cents(p) if p is not None else "—"}</td><td class="num">{(fee_per_contract(s["venue"], p)*100):.1f}¢</td><td class="num">{lk}</td></tr>' if p is not None else
                           f'<tr><td><a href="/markets/{s["venue"]}/{s["slug"]}/">{esc(s["title"])}</a></td><td class="num">{len(s["rows"])}</td><td class="num">—</td><td class="num">—</td><td class="num">—</td></tr>')
            out.append("</tbody></table></div>")
        out.append("</section>")
    out.append(FOOT)
    return "".join(out)


def sitemap(urls: list[str], built_iso: str) -> str:
    body = "".join(f"<url><loc>{esc(u)}</loc><lastmod>{built_iso[:10]}</lastmod></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>'


# ----------------------------------------------------------------------------- main
def build(out: Path, venue: str, max_series: int | None) -> int:
    h = Http()
    series: list[dict] = []
    if venue in ("kalshi", "both"):
        for rec in fetch_kalshi(h, max_series).values():
            try:
                series.append(norm_kalshi(rec))
            except Exception as e:
                LOG("kalshi norm failed", rec.get("ticker"), repr(e))
    if venue in ("pmus", "both"):
        for rec in fetch_pmus(h, max_series).values():
            try:
                series.append(norm_pmus(rec))
            except Exception as e:
                LOG("pmus norm failed", rec.get("ticker"), repr(e))
    return write(out, series)


def write(out: Path, series: list[dict]) -> int:
    now = datetime.now(timezone.utc)
    built = now.strftime("%d %b %Y %H:%M UTC")
    out.mkdir(parents=True, exist_ok=True)
    urls = [f"{SITE}/", f"{SITE}/simulate.html", f"{SITE}/markets/"]
    n = 0
    for s in series:
        if not s["rows"]:
            continue
        d = out / s["venue"] / s["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(render_series(s, built), encoding="utf-8")
        urls.append(f"{SITE}/markets/{s['venue']}/{s['slug']}/")
        n += 1
    (out / "index.html").write_text(render_index([s for s in series if s["rows"]], built), encoding="utf-8")
    (out.parent / "sitemap.xml").write_text(sitemap(urls, now.isoformat()), encoding="utf-8")
    (out / "series.json").write_text(json.dumps([{"venue": s["venue"], "slug": s["slug"], "title": s["title"], "category": s["category"], "open": len(s["rows"])} for s in series], ensure_ascii=False, indent=0), encoding="utf-8")
    LOG(f"wrote {n} series pages + index + sitemap to {out}")
    return n


def selftest() -> None:
    assert abs(fee_per_contract("kalshi", 0.5) - 0.0175) < 1e-12
    assert abs(fee_on("kalshi", 0.5, 50) - 1.75) < 1e-9
    assert abs(fee_on("pmus", 0.3, 50) - 3.325) < 1e-3
    assert abs(breakeven("pmus", 0.5) - 0.52375) < 1e-4
    assert luck(0.5) == 1.0 and abs(luck(0.94) - 0.12) < 1e-9
    fake_k = {"venue": "kalshi", "ticker": "KXBTC5M", "series": {"title": "Bitcoin price, 5 minutes", "category": "Crypto", "fee_type": "quadratic", "settlement_sources": [{"name": "CF Benchmarks BRTI"}]},
              "markets": [{"ticker": "KXBTC5M-26NOV08-1200", "title": "BTC above 75,000 at 12:05?", "yes_bid_dollars": "0.48", "yes_ask_dollars": "0.52", "volume_fp": "1200", "close_time": "2026-11-08T12:05:00Z", "rules_primary": "Resolves YES if the BRTI 60-second average is above the open."}]}
    s = norm_kalshi(fake_k)
    assert s["crypto_minutes"] and s["rows"][0]["p"] == 0.5
    page = render_series(s, "08 Nov 2026 00:00 UTC")
    assert "Luck needed meter" in page and "100% 😈" in page and "FAQPage" in page and '<main id="main">' in page
    fake_p = {"venue": "pmus", "ticker": "eth-updown-15m", "markets": [{"slug": "cpceth-eth-updown-15m-2026-11-08-0100z", "yesPrice": "0.61", "volume": 300, "endDate": "2026-11-08T01:15:00Z", "assetPriceTerms": {"asset": {"symbol": "ETH"}, "horizon": "15m"}}]}
    s2 = norm_pmus(fake_p)
    assert s2["title"] == "ETH Up or Down, 15 minutes" and s2["rows"][0]["p"] == 0.61
    idx = render_index([s, s2], "08 Nov 2026 00:00 UTC")
    assert "Kalshi" in idx and "Polymarket US" in idx
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        n = write(Path(td) / "markets", [s, s2])
        assert n == 2 and (Path(td) / "sitemap.xml").exists()
    print("selftest ok")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--out", default="site/dist/markets")
    b.add_argument("--venue", default="both", choices=["kalshi", "pmus", "both"])
    b.add_argument("--max-series", type=int, default=None)
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        selftest()
    else:
        n = build(Path(a.out), a.venue, a.max_series)
        print(f"{n} series pages")


if __name__ == "__main__":
    main()
