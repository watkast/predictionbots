#!/usr/bin/env python3
"""Build the site: copy static files to site/dist and render site/posts/*.md into dist/posts/*.html.
    python site/build.py          # -> site/dist (deploy that folder with Cloudflare Pages; functions/ ships alongside)
Front matter: title, date, summary, images (list). Markdown via the `markdown` package (pip install markdown)."""
import re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — PredictionBots</title><meta name="description" content="{summary}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{summary}">{og_image}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css"></head>
<body><div class="wrap">
<header class="top"><a class="brand" href="/">PredictionBots</a><nav><a href="/#ledger">Live ledger</a><a href="/#terminal">Terminal</a><a href="/#research">Research</a><a href="https://github.com/watkast/predictionbots">GitHub</a></nav></header>
<article class="post"><h1>{title}</h1><div class="meta">{date_h} · PredictionBots research</div><div class="body">{body}</div></article>
<section id="waitlist"><h2>Get the next one</h2><p class="sub">One email when the terminal opens, and the research posts as they publish. Nothing else.</p>
<form class="wait" id="wait-form" action="/api/waitlist" method="post"><input type="email" id="email" name="email" placeholder="you@example.com" required autocomplete="email" aria-label="Email"><button type="submit">Join the waitlist</button></form><div class="wait-msg" id="wait-msg"></div></section>
<footer><p>PredictionBots builds research tools and publishes its own trading records. Nothing on this site is investment advice; prediction markets and crypto involve risk of loss, and most participants lose money.</p><p>Code and data: <a href="https://github.com/watkast/predictionbots">github.com/watkast/predictionbots</a></p></footer>
</div>
<script>(function(){{var f=document.getElementById('wait-form'),m=document.getElementById('wait-msg');if(!f)return;f.addEventListener('submit',async function(e){{e.preventDefault();var b=f.querySelector('button');b.disabled=true;m.className='wait-msg';m.textContent='Adding you…';try{{var r=await fetch('/api/waitlist',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:f.email.value.trim(),source:location.pathname}})}});var j=await r.json().catch(function(){{return{{}}}});if(r.ok){{m.className='wait-msg ok';m.textContent=j.message||'You are on the list.';f.reset();}}else{{m.className='wait-msg err';m.textContent=j.error||'That did not go through.';}}}}catch(err){{m.className='wait-msg err';m.textContent='No connection. Try again in a moment.';}}b.disabled=false;}});}})();</script>
</body></html>"""


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
    for f in ("index.html", "styles.css", "ledger.js", "truecost.js"):
        shutil.copy(ROOT / f, DIST / f)
    shutil.copytree(ROOT / "functions", DIST / "functions")
    (DIST / "posts").mkdir()
    if (ROOT / "posts" / "img").exists():
        shutil.copytree(ROOT / "posts" / "img", DIST / "posts" / "img")
    for md in sorted((ROOT / "posts").glob("*.md")):
        meta, body = front_matter(md.read_text())
        html = markdown.markdown(body, extensions=["extra", "smarty"])
        imgs = meta.get("images") or []
        og = f'<meta property="og:image" content="/posts/{imgs[0]}">' if imgs else ""
        out = TEMPLATE.format(title=meta.get("title", md.stem), summary=meta.get("summary", ""), og_image=og,
                              date_h=human_date(meta.get("date", "")), body=html)
        (DIST / "posts" / (md.stem + ".html")).write_text(out)
        print("built", md.stem)
    print("site ->", DIST)


if __name__ == "__main__":
    build()
