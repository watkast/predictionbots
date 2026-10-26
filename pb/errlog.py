"""Error log for the bots. Wrap a bot's work in `guard(...)`: any crash is written as a JSON record the tracker can
read, printed as a GitHub Actions error annotation, and re-raised so the step FAILS (never swallowed).

    from pb.errlog import guard
    with guard("ef-autobuyer", out="data/polyus/ef_autobuyer"):
        run(...)

Records go to <out>/errors.jsonl (one JSON object per line: time, bot, kind, message, traceback, context).
`record(...)` logs a non-fatal failure the same way without raising (e.g. a producer that fell back to stale data).
The health watchdog (scripts/health_check.py) reads these files and opens Error tickets for anything new.
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

FILE = "errors.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record(bot: str, kind: str, message: str, out: str | os.PathLike | None = None, fatal: bool = False, **context) -> dict:
    rec = {"t": _now(), "bot": bot, "kind": kind, "fatal": fatal, "message": message[:2000], "context": context,
           "run_url": _run_url()}
    if fatal:
        rec["traceback"] = traceback.format_exc()[-4000:]
    if out is not None:
        p = Path(out) / FILE
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
    # GitHub Actions annotation (harmless elsewhere)
    print(f"::{'error' if fatal else 'warning'} title={bot} {kind}::{message[:500]}", file=sys.stderr, flush=True)
    return rec


def _run_url() -> str | None:
    srv, repo, run = os.environ.get("GITHUB_SERVER_URL"), os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_RUN_ID")
    return f"{srv}/{repo}/actions/runs/{run}" if srv and repo and run else None


@contextmanager
def guard(bot: str, out: str | os.PathLike | None = None, **context):
    """Log and re-raise anything the block throws. KeyboardInterrupt and SystemExit(0) pass through untouched."""
    try:
        yield
    except SystemExit as e:
        if e.code not in (None, 0):
            record(bot, "exit", f"exit code {e.code}", out, fatal=True, **context)
        raise
    except KeyboardInterrupt:
        raise
    except BaseException as e:  # noqa: BLE001 - this is the catch-all by design
        record(bot, type(e).__name__, str(e) or repr(e), out, fatal=True, **context)
        raise


def read(out: str | os.PathLike, since: str | None = None) -> list[dict]:
    """Records in <out>/errors.jsonl, optionally only those after ISO time `since`."""
    p = Path(out) / FILE
    if not p.exists():
        return []
    recs = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if since is None or r.get("t", "") > since:
            recs.append(r)
    return recs
