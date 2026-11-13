#!/usr/bin/env python3
"""Merge two extracted-windows files (mrp/mrp_extract_btc15.py, mrp/mrp_extract_kalshi15.py) into one.

Why: the benchmark used to re-extract every window from every raw book in git, every day. Raw books older than a
week now live in release assets (scripts/archive_release.py), so a fresh extraction only sees the last week. The
windows the benchmark already published are the memory: each run merges them with what it just extracted.

  python scripts/windows_merge.py PUBLISHED.json[.gz] FRESH.json OUT.json

A window is keyed by its slug. When both files have it, the fuller record wins: settled beats unsettled, then more
index prints, then more book seconds; a tie goes to the fresh extraction. A missing or unreadable PUBLISHED file is
an empty one (the first run, or a branch without a benchmark yet) and is said out loud.
"""
from __future__ import annotations

import gzip
import json
import sys


def load(path: str) -> dict:
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def fullness(w: dict) -> tuple:
    return (w.get("settle") is not None, len(w.get("prints") or {}), int(w.get("book_secs") or 0))


def merge(published: dict, fresh: dict) -> dict:
    by_slug = {w["slug"]: w for w in published.get("windows", [])}
    kept_old = 0
    for w in fresh.get("windows", []):
        old = by_slug.get(w["slug"])
        if old is None or fullness(w) >= fullness(old):
            by_slug[w["slug"]] = w
        else:
            kept_old += 1
    out = {k: v for k, v in fresh.items() if k != "windows"}
    out["windows"] = [by_slug[s] for s in sorted(by_slug)]
    out["merged"] = {"published": len(published.get("windows", [])), "fresh": len(fresh.get("windows", [])),
                     "total": len(by_slug), "fuller_published_kept": kept_old}
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__)
        return 2
    try:
        published = load(argv[1])
    except (OSError, ValueError) as e:
        print(f"no published windows to merge ({type(e).__name__}: {e}); using the fresh extraction alone")
        published = {"windows": []}
    fresh = load(argv[2])
    out = merge(published, fresh)
    with open(argv[3], "w", encoding="utf-8") as fh:
        json.dump(out, fh, separators=(",", ":"))
    m = out["merged"]
    only_old = m["total"] - m["fresh"]
    print(f"windows: published {m['published']}, fresh {m['fresh']}, merged {m['total']} "
          f"({only_old} only in the published file, {m['fuller_published_kept']} fuller there)")
    if m["total"] < m["published"]:
        print("FAIL: the merge lost windows")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
