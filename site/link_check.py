"""Check every internal link in site/dist resolves to a file. Run after build.py.

  python site/link_check.py [site/dist]
Exits 1 and lists the broken links if any. External links are not fetched (the shell has no general web access).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

DIST = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "dist")
HREF = re.compile(r'\s(?:href|src)="([^"]+)"')


def target(page: Path, link: str) -> Path | None:
    u = urlparse(link)
    if u.scheme or link.startswith(("#", "mailto:", "tel:", "javascript:", "data:")) or "{" in link:
        return None
    path = unquote(u.path)
    if not path or (path.startswith("/markets") and not (DIST / "markets").exists()):  # market pages are built in CI only
        return None
    p = (DIST / path.lstrip("/")) if path.startswith("/") else (page.parent / path)
    if p.is_dir() or path.endswith("/"):
        p = p / "index.html"
    return p


def main() -> None:
    bad = []
    pages = list(DIST.rglob("*.html"))
    for page in pages:
        for link in HREF.findall(page.read_text(errors="ignore")):
            p = target(page, link)
            if p is not None and not p.exists() and not p.with_suffix(".html").exists():
                bad.append(f"{page.relative_to(DIST)} -> {link}")
    print(f"{len(pages)} pages checked, {len(bad)} broken links")
    for b in sorted(set(bad))[:200]:
        print("  ", b)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
