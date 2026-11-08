"""Rename the brand across the site and docs in one pass, leaving repository paths alone.

  python scripts/rename_brand.py --brand PredictMeNot --domain predictmenot.com [--apply]

Replaces the brand word "PredictionBots" and the domain "predictionbots.io" (and e-mail addresses on it) in site/,
scripts/market_pages.py, marketing/, ops/, BUSINESS.md and README.md. Never touches "watkast/predictionbots",
raw.githubusercontent.com URLs, the Pages project name or anything under .git. Dry run by default: prints a count per
file; --apply writes.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ["site", "scripts/market_pages.py", "marketing", "ops", "BUSINESS.md", "README.md", "mrt/README.md"]
SKIP_DIRS = {"dist", "vendor", "node_modules", ".wrangler", "img"}
TEXT_EXT = {".html", ".md", ".js", ".py", ".css", ".json", ".toml", ".yml", ".yaml", ".txt", ".sql", ".sh", ".service", ".example"}
PROTECT = re.compile(r"(watkast/predictionbots|raw\.githubusercontent\.com/[^\s\"')]*|project-name=predictionbots|predictionbots\.pages\.dev|predictionbots-(?:mrh|mrp|site|benchmark|dell|recorder|market-pages|rates)|/opt/predictionbots|/etc/predictionbots|/var/lib/predictionbots|predictionbots-recorder)")


def rename_text(text: str, brand: str, domain: str) -> str:
    keep: list[str] = []
    def stash(m):
        keep.append(m.group(0)); return f"\x00{len(keep) - 1}\x00"
    t = PROTECT.sub(stash, text)
    t = t.replace("predictionbots.io", domain)
    t = t.replace("PredictionBots", brand)
    t = t.replace("Predictionbots", brand)
    t = re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], t)
    return t


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True)
    ap.add_argument("--domain", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    files: list[Path] = []
    for t in TARGETS:
        p = ROOT / t
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix in TEXT_EXT and not (set(f.parts) & SKIP_DIRS):
                    files.append(f)
    total = 0
    for f in files:
        try:
            s = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        n = rename_text(s, a.brand, a.domain)
        if n != s:
            c = s.count("PredictionBots") + s.count("predictionbots.io")
            total += c
            print(f"{c:4d}  {f.relative_to(ROOT)}")
            if a.apply:
                f.write_text(n, encoding="utf-8")
    print(f"{'applied' if a.apply else 'would change'} {total} occurrences in {len([1 for _ in files])} files scanned")


if __name__ == "__main__":
    main()
