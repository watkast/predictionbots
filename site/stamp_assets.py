#!/usr/bin/env python3
"""Stamp every page's links to our own CSS and JS with a hash of the file: /styles.css -> /styles.css?v=1a2b3c4d5e.

Why: a page and its stylesheet are fetched and cached separately. Without the stamp, a browser (or a cache in front
of it) can pair today's page with yesterday's stylesheet for as long as it keeps the old copy; on 13 Nov 2026 that
showed a phone header we had already fixed. With the stamp, a changed file has a new address, so the page that
names it can only get that version.

    python site/stamp_assets.py site/dist        (run last, after every page has been written)

Stamps href/src that point at a .css or .js file in the root of the build (not vendor/, which is versioned by name).
Running it twice gives the same result.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path


def stamp(dist: Path) -> tuple[int, dict[str, str]]:
    assets = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:10]
              for p in sorted(dist.iterdir()) if p.is_file() and p.suffix in (".css", ".js")}
    if not assets:
        return 0, {}
    names = "|".join(re.escape(n) for n in assets)
    ref = re.compile(r'((?:href|src)=")/(' + names + r')(?:\?v=[0-9a-f]+)?(")')
    changed = 0
    for page in dist.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        new = ref.sub(lambda m: f"{m.group(1)}/{m.group(2)}?v={assets[m.group(2)]}{m.group(3)}", text)
        if new != text:
            page.write_text(new, encoding="utf-8")
            changed += 1
    return changed, assets


def main(argv: list[str]) -> int:
    dist = Path(argv[1] if len(argv) > 1 else "site/dist")
    if not dist.is_dir():
        print(f"no build at {dist}")
        return 1
    changed, assets = stamp(dist)
    print(f"stamped {changed} pages; " + ", ".join(f"{n}?v={h}" for n, h in assets.items()))
    unstamped = [str(p) for p in dist.rglob("*.html") if re.search(r'(?:href|src)="/(?:' + "|".join(re.escape(n) for n in assets) + r')"', p.read_text(encoding="utf-8"))]
    if unstamped:
        print(f"FAIL: {len(unstamped)} pages still link an unstamped file, e.g. {unstamped[:3]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
