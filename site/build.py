#!/usr/bin/env python3
"""Build the site: copy static files to site/dist and render site/posts/*.md into dist/posts/*.html.
    python site/build.py          # -> site/dist (deploy that folder with Cloudflare Pages; functions/ ships alongside)
Front matter: title, date, summary, images (list). Markdown via the `markdown` package (pip install markdown)."""
import re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><script>try{{var t=localStorage.getItem("pb-theme");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — PredictMeNot</title><meta name="description" content="{summary}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{summary}">{og_image}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css"></head>
<body><a class="skip" href="#main">Skip to content</a><div class="wrap">
<header class="top"><a class="brand" href="/">PredictMeNot</a><nav><a href="/#truecost">True Cost</a><a href="/simulate.html">Simulator</a><a href="/#benchmark">Bot benchmark</a><a href="/#research">Research</a><a href="/#honest">How we're paid</a></nav><fieldset class="theme" id="theme"><legend>Theme</legend><label><input type="radio" name="theme" value="system" checked> System</label><label><input type="radio" name="theme" value="dark"> Dark</label><label><input type="radio" name="theme" value="light"> Light</label></fieldset></header>
<main id="main"><article class="post"><h1>{title}</h1><div class="meta">{date_h} · PredictMeNot</div><div class="body">{body}</div>{floor}</article>
<section id="waitlist"><h2>Get the next one</h2><p class="sub">Research posts and new benchmark rows as they publish. Nothing else, and you can leave with one click.</p>
<form class="wait" id="wait-form" action="/api/waitlist" method="post"><input type="email" id="email" name="email" placeholder="you@example.com" required autocomplete="email" aria-label="Email"><button type="submit">Send me the posts</button></form><div class="wait-msg" id="wait-msg"></div></section></main>
<script src="/theme.js" defer></script><script src="/floor.js" defer></script><footer><p>PredictMeNot measures prediction markets and publishes its own record. Nothing on this site is investment advice. Prediction markets and crypto involve risk of loss, and most participants lose money. If gambling is a problem for you or someone you know, call 1-800-GAMBLER.</p><p>Code and data: <a href="https://github.com/watkast/predictionbots">github.com/watkast/predictionbots</a></p></footer>
</div>
<script>(function(){{var f=document.getElementById('wait-form'),m=document.getElementById('wait-msg');if(!f)return;f.addEventListener('submit',async function(e){{e.preventDefault();var b=f.querySelector('button');b.disabled=true;m.className='wait-msg';m.textContent='Adding you…';try{{var r=await fetch('/api/waitlist',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:f.email.value.trim(),source:location.pathname}})}});var j=await r.json().catch(function(){{return{{}}}});if(r.ok){{m.className='wait-msg ok';m.textContent=j.message||'You are on the list.';f.reset();}}else{{m.className='wait-msg err';m.textContent=j.error||'That did not go through.';}}}}catch(err){{m.className='wait-msg err';m.textContent='No connection. Try again in a moment.';}}b.disabled=false;}});}})();</script>
</body></html>"""


def wrap_tables(html: str) -> str:
    """Markdown tables get the wrapper the hand-written ones have: a wide table scrolls inside itself on a phone
    instead of widening the page, and the scrolling box can be reached from the keyboard."""
    n = iter(range(1, 1000))        # a page's regions need different names
    html = re.sub("<table>", lambda m: f'<div class="ledger-wrap" tabindex="0" role="region" aria-label="Table {next(n)} (scrolls sideways on a small screen)"><table>', html)
    return html.replace("</table>", "</table></div>")


CANONICAL = "https://predictmenot.com"


def add_canonical(dist: Path) -> int:
    """<link rel="canonical"> on every page the build writes (the market pages carry their own), so a page reached
    at www.predictmenot.com tells search engines its address is predictmenot.com."""
    n = 0
    for page in dist.rglob("*.html"):
        rel = page.relative_to(dist).as_posix()
        if rel.startswith("markets/"):
            continue
        t = page.read_text(encoding="utf-8")
        if 'rel="canonical"' in t or "</head>" not in t:
            continue
        url = CANONICAL + "/" + (rel[: -len("index.html")] if rel.endswith("index.html") else rel)
        page.write_text(t.replace("</head>", f'<link rel="canonical" href="{url}"></head>', 1), encoding="utf-8")
        n += 1
    return n


def front_matter(txt: str):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.S)
    if not m:
        return {}, txt
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip().strip('"')
            if v.startswith("[") and v.endswith("]"):
                v = [x.strip().strip('"') for x in v[1:-1].split(",") if x.strip()]
            meta[k.strip()] = v
    return meta, m.group(2)


def human_date(s: str) -> str:
    from datetime import date
    try:
        d = date.fromisoformat(s)
        return f"{d.day} {d:%B %Y}"
    except Exception:
        return s


def build():
    import markdown
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    for f in ("index.html", "styles.css", "ledger.js", "truecost.js", "simulate.html", "sim.js", "theme.js", "elsewhere.js", "benchmark.js", "floor.js", "reality.html", "reality.js", "robots.txt"):
        shutil.copy(ROOT / f, DIST / f)
    # Prediction News list on the home page, from site/data/news.json
    newsf = ROOT / "data" / "news.json"
    if newsf.exists():
        import json, html as _h
        items = json.loads(newsf.read_text())["items"]
        li = []
        for it in sorted(items, key=lambda x: x["date"], reverse=True):
            li.append(f'<li><div class="when">{human_date(it["date"])} · <a href="{_h.escape(it["source"])}" rel="noopener nofollow">{_h.escape(it["source_name"])}</a></div>'
                      f'<h3>{_h.escape(it["headline"])}</h3><p><b>Our number:</b> {_h.escape(it["number"])} <a href="{_h.escape(it["ours"])}">More →</a></p></li>')
        idx = (DIST / "index.html").read_text().replace("<!--NEWS-->", "".join(li))
        (DIST / "index.html").write_text(idx)
    shutil.copytree(ROOT / "vendor", DIST / "vendor")
    shutil.copytree(ROOT / "data", DIST / "data")
    (DIST / "posts").mkdir()
    if (ROOT / "posts" / "img").exists():
        shutil.copytree(ROOT / "posts" / "img", DIST / "posts" / "img")
    for md in sorted((ROOT / "posts").glob("*.md")):
        meta, body = front_matter(md.read_text())
        html = wrap_tables(markdown.markdown(body, extensions=["extra", "smarty"]))
        imgs = meta.get("images") or []
        og = f'<meta property="og:image" content="/posts/{imgs[0]}"><meta name="twitter:card" content="summary_large_image">' if imgs else ""
        import html as _hh
        floor = f'<div class="wide" data-floor data-kind="post" data-key="{md.stem}" data-title="{_hh.escape(meta.get("title", md.stem))}"></div>'
        out = TEMPLATE.format(title=meta.get("title", md.stem), summary=meta.get("summary", ""), og_image=og,
                              date_h=human_date(meta.get("date", "")), body=html, floor=floor)
        (DIST / "posts" / (md.stem + ".html")).write_text(out)
        print("built", md.stem)
    # /learn/: evergreen explainers, same template, "Updated <date>" instead of a dateline, FAQ structured data if given
    if (ROOT / "learn").exists():
        (DIST / "learn").mkdir()
        for md in sorted((ROOT / "learn").glob("*.md")):
            meta, body = front_matter(md.read_text())
            html = wrap_tables(markdown.markdown(body, extensions=["extra", "smarty", "toc"]))
            faq = ""
            if meta.get("faq"):
                import json
                qa = [q.split("|", 1) for q in meta["faq"] if "|" in q]
                faq = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                    {"@type": "Question", "name": q.strip(), "acceptedAnswer": {"@type": "Answer", "text": a.strip()}} for q, a in qa]}, ensure_ascii=False) + "</script>"
            import html as _hh
            floor = f'<div class="wide" data-floor data-kind="learn" data-key="{md.stem}" data-title="{_hh.escape(meta.get("title", md.stem))}"></div>'
            ogimg = ""
            try:
                import sys as _s; _s.path.insert(0, str(ROOT)); import og as _og
                if _og.card(meta.get("title", md.stem), "Learn", DIST / "og" / f"learn-{md.stem}.png"):
                    ogimg = f'<meta property="og:image" content="/og/learn-{md.stem}.png"><meta name="twitter:card" content="summary_large_image">'
            except Exception as e:
                print("og card skipped:", e)
            out = TEMPLATE.format(title=meta.get("title", md.stem), summary=meta.get("summary", ""), og_image=faq + ogimg,
                                  date_h="Updated " + human_date(meta.get("updated", meta.get("date", ""))), body=html, floor=floor)
            (DIST / "learn" / (md.stem + ".html")).write_text(out)
            print("built learn/" + md.stem)
    # /ledger/: the Endorsement Ledger from site/data/ledger.json (noindex until it is switched on)
    led = ROOT / "data" / "ledger.json"
    if led.exists():
        import json
        L = json.loads(led.read_text())
        def fee_k(p): return 0.07 * p * (1 - p)
        def fee_p(p): return 0.095 * p * (1 - p)
        rows = []
        for e in sorted(L["entries"], key=lambda e: e["date"], reverse=True):
            v = e.get("venue_key", "kalshi"); p = float(e.get("market_price") or 0.5)
            fee = fee_k(p) if v == "kalshi" else fee_p(p)
            tc = f"{fee*100:.1f}¢ a contract at {round(p*100)}¢; break-even {round((p+fee)*100,1)}%"
            quote = f"“{e['quote']}” <span class=\"q-where\">({e['quote_where']})</span>" if e.get("quote") else "<span class=\"q-where\">no public quote found</span>"
            rows.append(f"<tr><th scope=\"row\">{e['figure']}<br><span class=\"q-where\">{e['role']}</span></th><td>{e['venue']}</td><td>{e['deal']}</td><td>{e['date']}</td><td>{quote}</td><td>{e['pay']}</td><td>{e['promoted']}<br><span class=\"q-where\">True Cost: {tc}</span></td><td><a href=\"{e['source']}\" rel=\"noopener nofollow\">{e['source_name']}</a></td></tr>")
        body = ("<p class=\"text\">Who is paid, or partnered, to tell you to bet. Every entry is a publicly announced arrangement with the source it came from; quotes are verbatim from that source; "
                "\"not disclosed\" means no public figure exists and we do not guess. Next to each entry is the True Cost of the kind of market being promoted, from the venue's fee schedule. "
                "This is a record, not an accusation: nothing here says any promotion caused anyone's losses, and promoters who publicly criticise the venues will be listed too. Corrections: inquire@predictmenot.com.</p>"
                "<div class=\"ledger-wrap\"><table class=\"ledger cells\"><caption>Public promoters of Kalshi and Polymarket US, with sources</caption><thead><tr><th scope=\"col\">Who</th><th scope=\"col\">Venue</th><th scope=\"col\">Arrangement</th><th scope=\"col\">Date</th><th scope=\"col\">What they said</th><th scope=\"col\">Pay</th><th scope=\"col\">What is promoted</th><th scope=\"col\">Source</th></tr></thead><tbody>"
                + "".join(rows) + "</tbody></table></div>"
                f"<p class=\"fine\">Updated {human_date(L['updated'])}. Polymarket US had announced no named celebrity partners in the reporting we have found as of that date; its 2025 partnership with X is a platform deal, not a personal endorsement.</p>")
        out = TEMPLATE.format(title="The Endorsement Ledger: who is paid to tell you to bet", summary="Every public promoter of Kalshi and Polymarket US, with the source, the verbatim quote where one exists, disclosed pay or 'not disclosed', and the True Cost of what they promote.",
                              og_image='<meta name="robots" content="noindex">', date_h="Updated " + human_date(L["updated"]), body=body, floor="")
        out = out.replace('<div class="body">', '<div class="body wide-body">', 1)
        (DIST / "ledger").mkdir(exist_ok=True)
        (DIST / "ledger" / "index.html").write_text(out)
        print("built ledger (noindex)")
    try:
        import sys as _s; _s.path.insert(0, str(ROOT)); import og as _og
        for name, title, kicker in (("home", "See the odds before you throw. What prediction markets really cost.", "Free, no account"),
                                    ("simulate", "How long until your balance is $0 in this market?", "Simulator"),
                                    ("reality", "Your prediction-market statement, computed in your browser", "Reality Check")):
            _og.card(title, kicker, DIST / "og" / f"{name}.png")
        for page, name in (("index.html", "home"), ("simulate.html", "simulate"), ("reality.html", "reality")):
            f = DIST / page
            t = f.read_text()
            if 'property="og:image"' not in t:
                t = t.replace('<meta property="og:title"', f'<meta property="og:image" content="/og/{name}.png"><meta name="twitter:card" content="summary_large_image">\n<meta property="og:title"', 1)
            else:
                t = t.replace('<meta property="og:image" content="/posts/img/free-money-snapshot-vs-live.png">', f'<meta property="og:image" content="/og/{name}.png"><meta name="twitter:card" content="summary_large_image">')
            f.write_text(t)
    except Exception as e:
        print("og cards skipped:", e)
    print("canonical links:", add_canonical(DIST))
    print("site ->", DIST)


if __name__ == "__main__":
    build()
