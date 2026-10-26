"""Tracker: Project and Error tickets as GitHub Issues on this repo. Simpler than Jira: two ticket types, fixed stages.

  Project ticket  stages: Research > Design > Build > Test > Integration > QA > Launch > Live Test
  Error ticket    stages: Reproduce > Cause & Effect > Fix > QA > Deploy > Live Test   (priority P0: worked before anything else)

Every ticket carries labels: `type:project` or `type:error`, exactly one `stage:<name>`, `bot:<assignee>`, and `P0` on errors.
An Error ticket also carries a fingerprint (`fp:<key>`) so the same failure is never opened twice: a repeat lands as a
comment on the open ticket. Closing a ticket means its Live Test passed (or it was dropped: say so in the comment).

Usage (needs `gh` logged in, or GITHUB_TOKEN in Actions):
  python scripts/tracker.py ensure-labels
  python scripts/tracker.py new project "Early Favorite forward test" --bot ef-tracker --stage "Live Test" --body "..."
  python scripts/tracker.py error "ef-autobuyer run failed" --fingerprint wf:ef-autobuyer --bot ef-autobuyer --body "..."
  python scripts/tracker.py move 12 "Cause & Effect" --note "404s come from the gateway, not the slug"
  python scripts/tracker.py comment 12 "still failing at 2026-10-26T10:00Z"
  python scripts/tracker.py close 12 --note "Live Test passed: 24 h of clean runs"
  python scripts/tracker.py list [--type error|project] [--all]
  python scripts/tracker.py board            # JSON for the board page / the bot
  python scripts/tracker.py board-docs OUT   # OUT/board_doc.json + OUT/health_doc.json, the two documents the board artifact reads
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = os.environ.get("TRACKER_REPO", "watkast/predictionbots")

STAGES = {
    "project": ["Research", "Design", "Build", "Test", "Integration", "QA", "Launch", "Live Test"],
    "error": ["Reproduce", "Cause & Effect", "Fix", "QA", "Deploy", "Live Test"],
}
PRIORITY = {"error": "P0", "project": "P2"}
COLORS = {"type:error": "B60205", "type:project": "0E8A16", "P0": "B60205", "P2": "C5DEF5", "recovered": "FBCA04",
          "stage": "1D76DB", "bot": "5319E7", "fp": "EDEDED"}
BOTS_HINT = ["ef-autobuyer", "ef-tracker", "polyus", "carry", "trend", "paper", "record", "backtest", "bounty-scan", "ci",
             "health", "claude"]


# ---------- gh plumbing ----------

def gh(*args, input_: str | None = None) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True, input=input_)
    if r.returncode != 0:
        raise SystemExit(f"gh {' '.join(args[:3])}... failed: {r.stderr.strip()[:400]}")
    return r.stdout


def api(path: str, method: str = "GET", **fields) -> object:
    args = ["api", f"repos/{REPO}/{path}", "-X", method]
    if fields:
        args += ["--input", "-"]
        out = gh(*args, input_=json.dumps(fields))
    else:
        out = gh(*args)
    return json.loads(out) if out.strip() else None


def paged(path: str) -> list:
    out = gh("api", "--paginate", "--slurp", f"repos/{REPO}/{path}")
    pages = json.loads(out) if out.strip() else []
    return [item for page in pages for item in (page if isinstance(page, list) else [page])]


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def stage_label(stage: str) -> str:
    return f"stage:{stage}"


# ---------- labels ----------

def ensure_labels() -> list[str]:
    have = {l["name"] for l in paged("labels?per_page=100")}
    want = {"type:error": COLORS["type:error"], "type:project": COLORS["type:project"], "P0": COLORS["P0"],
            "P2": COLORS["P2"], "recovered": COLORS["recovered"]}
    for t, stages in STAGES.items():
        for s in stages:
            want[stage_label(s)] = COLORS["stage"]
    for b in BOTS_HINT:
        want[f"bot:{b}"] = COLORS["bot"]
    made = []
    for name, color in want.items():
        if name not in have:
            api("labels", "POST", name=name, color=color)
            made.append(name)
    return made


def ensure_label(name: str, color: str):
    try:
        api(f"labels/{name.replace('/', '%2F')}")
    except SystemExit:
        api("labels", "POST", name=name, color=color)


# ---------- tickets ----------

def ticket_type(issue: dict) -> str | None:
    names = {l["name"] for l in issue.get("labels", [])}
    return "error" if "type:error" in names else "project" if "type:project" in names else None


def ticket_stage(issue: dict) -> str | None:
    for l in issue.get("labels", []):
        if l["name"].startswith("stage:"):
            return l["name"][6:]
    return None


def ticket_bot(issue: dict) -> str | None:
    for l in issue.get("labels", []):
        if l["name"].startswith("bot:"):
            return l["name"][4:]
    return None


def ticket_fp(issue: dict) -> str | None:
    for l in issue.get("labels", []):
        if l["name"].startswith("fp:"):
            return l["name"][3:]
    return None


def open_tickets(kind: str | None = None, state: str = "open") -> list[dict]:
    items = [i for i in paged(f"issues?state={state}&per_page=100") if "pull_request" not in i and ticket_type(i)]
    if kind:
        items = [i for i in items if ticket_type(i) == kind]
    # errors first, then by number
    return sorted(items, key=lambda i: (ticket_type(i) != "error", i["number"]))


def new_ticket(kind: str, title: str, bot: str, body: str = "", stage: str | None = None, fingerprint: str | None = None) -> dict:
    stages = STAGES[kind]
    stage = stage or stages[0]
    if stage not in stages:
        raise SystemExit(f"{kind} tickets have stages {stages}, not {stage!r}")
    labels = [f"type:{kind}", stage_label(stage), f"bot:{bot}", PRIORITY[kind]]
    ensure_label(f"bot:{bot}", COLORS["bot"])
    if kind == "error":
        fingerprint = slug(fingerprint or title)[:40]
        fp_label = f"fp:{fingerprint}"
        dupes = []
        for attempt in range(2):          # the issues index lags creation by a few seconds; look twice
            dupes = [t for t in paged(f"issues?state=open&per_page=50&labels=type:error,{fp_label}") if "pull_request" not in t]
            if dupes or attempt:
                break
            time.sleep(4)
        if dupes:
            t = sorted(dupes, key=lambda i: i["number"])[0]
            api(f"issues/{t['number']}/comments", "POST", body=f"Seen again.\n\n{body}".strip())
            print(f"#{t['number']} already open for fp:{fingerprint}; commented")
            return t
        ensure_label(fp_label, COLORS["fp"])
        labels.append(fp_label)
        title = title if title.startswith("[ERROR]") else f"[ERROR] {title}"
    checklist = "\n".join(f"- [{'x' if s == stage else ' '}] {s}" for s in stages)
    full = f"{body.strip()}\n\n**Type:** {kind} · **Assigned bot:** `{bot}` · **Priority:** {PRIORITY[kind]}\n\n**Stages**\n{checklist}\n"
    issue = api("issues", "POST", title=title, body=full, labels=labels)
    print(f"#{issue['number']} {issue['title']}  [{stage}]  {issue['html_url']}")
    return issue


def move(number: int, stage: str, note: str = "") -> dict:
    issue = api(f"issues/{number}")
    kind = ticket_type(issue)
    if not kind:
        raise SystemExit(f"#{number} is not a tracker ticket")
    if stage not in STAGES[kind]:
        raise SystemExit(f"{kind} tickets have stages {STAGES[kind]}, not {stage!r}")
    names = [l["name"] for l in issue["labels"] if not l["name"].startswith("stage:")] + [stage_label(stage)]
    # tick the checklist in the body up to and including this stage
    body = issue.get("body") or ""
    for s in STAGES[kind]:
        mark = "x" if STAGES[kind].index(s) <= STAGES[kind].index(stage) else " "
        body = re.sub(rf"- \[[ x]\] {re.escape(s)}\n", f"- [{mark}] {s}\n", body)
    issue = api(f"issues/{number}", "PATCH", labels=names, body=body)
    api(f"issues/{number}/comments", "POST", body=f"**→ {stage}**" + (f"\n\n{note}" if note else ""))
    print(f"#{number} → {stage}")
    return issue


def comment(number: int, text: str):
    api(f"issues/{number}/comments", "POST", body=text)
    print(f"#{number} commented")


def close(number: int, note: str = ""):
    if note:
        api(f"issues/{number}/comments", "POST", body=note)
    api(f"issues/{number}", "PATCH", state="closed")
    print(f"#{number} closed")


def board() -> dict:
    out = {"repo": REPO, "stages": STAGES, "tickets": []}
    for state in ("open", "closed"):
        for i in open_tickets(None, state):
            out["tickets"].append({"number": i["number"], "title": i["title"], "type": ticket_type(i), "stage": ticket_stage(i),
                                   "bot": ticket_bot(i), "state": i["state"], "url": i["html_url"],
                                   "updated": i["updated_at"], "created": i["created_at"],
                                   "recovered": any(l["name"] == "recovered" for l in i["labels"])})
            if state == "closed" and len([t for t in out["tickets"] if t["state"] == "closed"]) >= 30:
                break
    return out


def board_docs(out: Path) -> list[Path]:
    """The two documents behind the board artifact (collection `board`, docs `tickets` and `health`)."""
    from datetime import datetime, timezone
    out.mkdir(parents=True, exist_ok=True)
    b = board()
    b["generated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (out / "board_doc.json").write_text(json.dumps(b))
    r = subprocess.run(["gh", "api", "-H", "Accept: application/vnd.github.raw",
                        f"repos/{REPO}/contents/health/status.json?ref=data"], capture_output=True, text=True)
    health = json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else {"generated": None, "ok": None, "checks": [],
                                                                                 "note": "health/status.json not found on the data branch"}
    (out / "health_doc.json").write_text(json.dumps(health))
    return [out / "board_doc.json", out / "health_doc.json"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ensure-labels")
    p = sub.add_parser("new"); p.add_argument("kind", choices=["project", "error"]); p.add_argument("title")
    p.add_argument("--bot", required=True); p.add_argument("--body", default=""); p.add_argument("--stage"); p.add_argument("--fingerprint")
    p = sub.add_parser("error"); p.add_argument("title"); p.add_argument("--bot", required=True); p.add_argument("--body", default="")
    p.add_argument("--fingerprint"); p.add_argument("--stage")
    p = sub.add_parser("move"); p.add_argument("number", type=int); p.add_argument("stage"); p.add_argument("--note", default="")
    p = sub.add_parser("comment"); p.add_argument("number", type=int); p.add_argument("text")
    p = sub.add_parser("close"); p.add_argument("number", type=int); p.add_argument("--note", default="")
    p = sub.add_parser("list"); p.add_argument("--type", choices=["project", "error"]); p.add_argument("--all", action="store_true")
    sub.add_parser("board")
    p = sub.add_parser("board-docs"); p.add_argument("out")
    a = ap.parse_args()
    if a.cmd == "ensure-labels":
        made = ensure_labels()
        print(f"labels ok ({len(made)} created)")
    elif a.cmd == "new":
        new_ticket(a.kind, a.title, a.bot, a.body, a.stage, a.fingerprint)
    elif a.cmd == "error":
        new_ticket("error", a.title, a.bot, a.body, a.stage, a.fingerprint)
    elif a.cmd == "move":
        move(a.number, a.stage, a.note)
    elif a.cmd == "comment":
        comment(a.number, a.text)
    elif a.cmd == "close":
        close(a.number, a.note)
    elif a.cmd == "list":
        for i in open_tickets(a.type, "all" if a.all else "open"):
            print(f"#{i['number']:<4} {ticket_type(i):7} {ticket_stage(i) or '-':15} {ticket_bot(i) or '-':14} {i['state']:6} {i['title']}")
    elif a.cmd == "board":
        print(json.dumps(board(), indent=1))
    elif a.cmd == "board-docs":
        for f in board_docs(Path(a.out)):
            print(f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
