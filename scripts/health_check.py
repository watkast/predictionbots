"""Health watchdog: catches jobs that are stale or that run "successfully" while producing nothing.

Saturday 2026-10-25: ef-autobuyer crashed on its first check every run for 30 h and every run showed green,
because the wrapper swallowed the exit code and nothing looked at the output. This looks at the output.

13 Nov 2026: it now watches what the business runs on (the site deploy, the live site, the recorder, the benchmark).
Until then it watched only the trading-era bots, most of them retired, so the board was red with stale alarms while
nothing looked at the site at all.

Checks (each with an owner job, a fingerprint and a max age):
  freshness   last commit that touched a watched path (GitHub API, no deep clone needed)
  content     the live site: the build time printed on predictmenot.com/markets/ (so a deploy that never reached
              the domain, or a domain that stopped answering, shows up here and not only in a green workflow run)
  errors      new records in any errors.jsonl written by pb.errlog since the last health run

Outputs <state>/status.json (what the board shows) and, with --open-tickets, an Error ticket per failing check
through scripts/tracker.py (deduped by fingerprint; repeats become comments). A check that passes again gets its
open ticket labelled `recovered` with a comment, so the fixer bot can close it after Live Test.

Usage:  python scripts/health_check.py --data ../datawt --state ../datawt/health [--open-tickets]
Exit code 0 whenever the checks ran (findings become tickets, not a red health run); non-zero only if the
watchdog itself crashes, which error-watch then turns into its own ticket.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pb import errlog  # noqa: E402

REPO = os.environ.get("TRACKER_REPO", "watkast/predictionbots")
TRACKER = Path(__file__).resolve().parent / "tracker.py"

SITE = os.environ.get("SITE_URL", "https://predictmenot.com")

# (check id, job, branch, path, max age in hours, what it means)
# Limits are loose on purpose: GitHub runs this repo's "hourly" schedules every 6 to 9 h (measured 10-13 Nov).
WATCH = [
    ("site-deploy", "site-deploy", "mrp-data", "site-preview/sitemap.xml", 14,
     "site build and deploy (the preview is published only after a deploy succeeds)"),
    ("recorder", "mrp-record", "mrp-data", "mrp/data", 3, "order-book recorder (publishes about every 20 min; the data is the product)"),
    ("benchmark", "benchmark", "mrp-data", "benchmark/benchmark.json", 40, "daily bot-benchmark replay"),
    ("trend-report", "trend", "main", "reports/trend_paper.json", 80, "weekday trend paper tick (22:23 UTC)"),
]
ERROR_LOGS = ["polyus/*/errors.jsonl", "*/errors.jsonl", "errors.jsonl"]     # under the data worktree


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(d: datetime) -> str:
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def gh_json(path: str):
    r = subprocess.run(["gh", "api", f"repos/{REPO}/{path}"], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def last_commit_time(branch: str, path: str) -> datetime | None:
    j = gh_json(f"commits?sha={branch}&path={path}&per_page=1")
    if not j:
        return None
    return parse_iso(j[0]["commit"]["committer"]["date"])


def hours_since(d: datetime | None) -> float | None:
    return None if d is None else (now() - d).total_seconds() / 3600


# ---------- content checks ----------

def site_built(_data: Path | None = None, fetch=None, base: str | None = None) -> datetime | None:
    """When the live site says its market pages were built ("rebuilt 13 Nov 2026 08:04 UTC" on /markets/).
    None if the domain does not answer, answers with something else, or the stamp is missing: all are failures."""
    base = base or SITE
    try:
        if fetch is None:
            req = urllib.request.Request(f"{base}/markets/", headers={"User-Agent": "predictmenot-health/1.0 (+https://predictmenot.com)"})
            with urllib.request.urlopen(req, timeout=30) as r:
                html = r.read(400_000).decode("utf-8", "replace")
        else:
            html = fetch(f"{base}/markets/")
    except Exception:  # noqa: BLE001
        return None
    m = re.search(r"rebuilt (\d{1,2} [A-Z][a-z]{2} \d{4} \d{2}:\d{2}) UTC", html or "")
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%d %b %Y %H:%M").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


WWW = os.environ.get("SITE_WWW_URL", "https://www.predictmenot.com")
CONTENT = [
    ("site-live", "site-deploy", site_built, 14, "build time shown on the live site (predictmenot.com/markets/)"),
    # people type www; on 13 Nov 2026 the owner's phone could not reach it (a Cloudflare blip, it answered minutes later)
    ("site-live-www", "site-deploy", lambda d: site_built(d, base=WWW), 14, "the same build time, reached at www.predictmenot.com"),
]


# ---------- run ----------

def run_checks(data: Path) -> list[dict]:
    out = []
    for cid, bot, branch, path, max_h, meaning in WATCH:
        t = last_commit_time(branch, path)
        age = hours_since(t)
        ok = age is not None and age <= max_h
        out.append(dict(id=cid, bot=bot, kind="freshness", ok=ok, age_h=None if age is None else round(age, 1), max_h=max_h,
                        last=None if t is None else iso(t), what=f"{branch}:{path}", meaning=meaning))
    for cid, bot, fn, max_h, meaning in CONTENT:
        try:
            t = fn(data)
            err = None
        except Exception as e:  # noqa: BLE001
            t, err = None, f"{type(e).__name__}: {e}"
        age = hours_since(t)
        ok = age is not None and age <= max_h
        out.append(dict(id=cid, bot=bot, kind="content", ok=ok, age_h=None if age is None else round(age, 1), max_h=max_h,
                        last=None if t is None else iso(t), what=meaning, meaning=meaning, error=err))
    return out


def new_error_records(data: Path, since: str | None) -> list[dict]:
    recs = []
    for pat in ERROR_LOGS:
        for f in glob.glob(str(data / pat)):
            for r in errlog.read(Path(f).parent, since):
                r["file"] = os.path.relpath(f, data)
                recs.append(r)
    return recs


def tracker(*args) -> str:
    r = subprocess.run([sys.executable, str(TRACKER), *args], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"tracker {args[0]} failed: {r.stderr.strip()[:300]}", file=sys.stderr)
    return r.stdout.strip()


def open_error_for(check: dict):
    body = (f"Health check **{check['id']}** failed at {iso(now())}.\n\n"
            f"- what: {check['meaning']}\n- watched: `{check['what']}`\n"
            f"- last seen: {check.get('last') or 'never'} ({check['age_h']} h ago; limit {check['max_h']} h)\n"
            + (f"- error: `{check['error']}`\n" if check.get("error") else "")
            + "\nA stale output usually means the bot is crashing before it produces anything, or its workflow is not "
              "running. Reproduce by looking at the newest run of that workflow and the newest commit of the watched path.")
    return tracker("error", f"{check['bot']}: {check['id']} stale ({check['age_h']} h, limit {check['max_h']} h)",
                   "--bot", check["bot"], "--fingerprint", f"health:{check['id']}", "--body", body)


def mark_recovered(check: dict):
    """If an open Error ticket exists for this check and is not yet labelled `recovered`, label and comment it."""
    fp = f"fp:health-{check['id']}".replace("--", "-")
    j = gh_json(f"issues?state=open&per_page=20&labels=type:error,{fp}")
    for t in j or []:
        if any(l["name"] == "recovered" for l in t["labels"]):
            continue
        subprocess.run(["gh", "api", f"repos/{REPO}/issues/{t['number']}/labels", "-X", "POST", "--input", "-"],
                       input=json.dumps({"labels": ["recovered"]}), capture_output=True, text=True)
        tracker("comment", str(t["number"]),
                f"Recovered at {iso(now())}: `{check['id']}` is fresh again ({check['age_h']} h old, limit {check['max_h']} h). "
                "Confirm the cause is fixed, finish Live Test, then close.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="checkout of the data branch")
    ap.add_argument("--state", required=True, help="where status.json lives (committed to the data branch under health/)")
    ap.add_argument("--open-tickets", action="store_true")
    a = ap.parse_args()
    data, state = Path(a.data), Path(a.state)
    state.mkdir(parents=True, exist_ok=True)
    prev = json.loads((state / "status.json").read_text()) if (state / "status.json").exists() else {}
    since = prev.get("generated")

    checks = run_checks(data)
    errors = new_error_records(data, since)
    failing = [c for c in checks if not c["ok"]]
    status = {"generated": iso(now()), "ok": not failing and not errors, "checks": checks,
              "new_error_records": len(errors), "failing": [c["id"] for c in failing]}
    (state / "status.json").write_text(json.dumps(status, indent=1))

    for c in checks:
        flag = "ok  " if c["ok"] else "FAIL"
        print(f"{flag} {c['id']:22} {c['bot']:12} age {c['age_h']}h / {c['max_h']}h  {c['what']}")
    print(f"new error records since {since}: {len(errors)}")

    if a.open_tickets:
        for c in failing:
            print(open_error_for(c))
        for c in checks:
            if c["ok"]:
                mark_recovered(c)
        by_key: dict[tuple, list] = {}
        for r in errors:
            by_key.setdefault((r.get("bot", "unknown"), r.get("kind", "error")), []).append(r)
        for (bot, kind), recs in by_key.items():
            last = recs[-1]
            body = (f"{len(recs)} new `{kind}` record(s) from `{bot}` in `{last['file']}` since {since}.\n\n"
                    f"Latest at {last['t']}:\n```\n{last.get('message', '')[:800]}\n```\n"
                    + (f"```\n{last['traceback'][-1500:]}\n```\n" if last.get("traceback") else "")
                    + (f"Run: {last['run_url']}\n" if last.get("run_url") else ""))
            print(tracker("error", f"{bot}: {kind}", "--bot", bot, "--fingerprint", f"err:{bot}:{kind}", "--body", body))
    return 0


if __name__ == "__main__":
    with errlog.guard("health"):
        sys.exit(main())
