# Bot dispatcher — standing orders

These are the instructions the hourly scheduled Claude task follows. Humans: this is also how tickets move.

The repo is `watkast/predictionbots` (public; paper-trading bots run from GitHub Actions; the `data` branch holds
ledgers, logs and `health/status.json`; `reports/` on `main` holds reports). Work is tracked as GitHub Issues
through `scripts/tracker.py` — read its docstring first.

- **Error tickets**: label `type:error`, priority **P0**, stages `Reproduce > Cause & Effect > Fix > QA > Deploy > Live Test`,
  fingerprint label `fp:<key>` (one open ticket per failure; repeats are comments).
- **Project tickets**: label `type:project`, stages `Research > Design > Build > Test > Integration > QA > Launch > Live Test`.
- `bot:<name>` is the assignee. `recovered` on an Error ticket means the health watchdog saw the output become fresh again.

## Setup (every run)

1. Attach the repo with push access (`add_repo` owner `watkast`, repo `predictionbots`, access `push`). If denied,
   attach read-only and work in **comment-only mode** (below).
2. Clone; `pip install -e . pytest pytest-asyncio respx` quietly.
3. `python scripts/tracker.py list` (`gh` is authenticated once the repo is attached).

## Rule 1 — all hands on deck for Errors

If any open `type:error` ticket exists, work **only** Error tickets this run, oldest first. Record every move:
`python scripts/tracker.py move <n> "<stage>" --note "<what you found or did>"`.

| Stage | What it means |
|---|---|
| Reproduce | Find the failing run (`gh run list` / `gh run view --log`), the watched output on the data branch (`gh api -H "Accept: application/vnd.github.raw" repos/…/contents/<path>?ref=data`), and `errors.jsonl` records written by `pb.errlog`. State exactly what is broken. |
| Cause & Effect | One sentence naming the cause; what it cost (data lost, hours down). |
| Fix | Smallest correct change **with a unit test that would have caught it**. Never change a frozen trading rule (`early_favorite_tracker.RULE/FORWARD_START`, `ef_autobuyer.RULE`) as a "fix". |
| QA | `python -m pytest tests -q` green (`tests/test_scripts.py::test_replay_check_replays_ledger_with_and_without_risk` is a known pre-existing failure). For long-running watchers also a simulated run (fake clock, see the ef-autobuyer history) or a short `--minutes 1` run. |
| Deploy | Commit to `main` (message ends with `Co-Authored-By: Claude <noreply@anthropic.com>`), push; if the broken workflow is schedule-only, `gh workflow run <file> --ref main` once. |
| Live Test | Leave the ticket here with a comment stating the evidence that closes it (e.g. "24 h of rounds with checks and health check X ok"). On a later run, when that evidence exists (data branch, `health/status.json`, the `recovered` label), `python scripts/tracker.py close <n> --note "<evidence>"`. |

A duplicate of a fixed ticket: comment and close with the reason. Cannot reproduce after a real attempt: say so in a
comment and leave it at Reproduce — never invent a fix.

## Rule 2 — Project tickets (only when no Error ticket is open)

Pick the open Project ticket with the most recent activity that is not at Live Test. Advance it **one stage per run**,
doing what that stage means: Research = read code/data, write findings in a comment · Design = concrete plan in a
comment · Build = implement with tests · Test = tests + a simulated or short real run · Integration = wire into
workflows/configs · QA = full suite + review the diff · Launch = push to `main` and dispatch · Live Test = state the
closing evidence. If every Project ticket is at Live Test: check each one's evidence, close those that pass, comment on
the rest, stop. A ticket whose body says it needs the owner's go before Build stops at Design with a comment asking.

## Rule 3 — safety

Paper trading only: never add order placement, API keys or real-money paths. Never force-push, never rewrite the data
branch, never delete data. Do not retune frozen strategy rules. Keep diffs small. If a change is risky or irreversible,
write the plan into the ticket instead of doing it.

## Comment-only mode (push denied)

Do everything except commit/push: put the full patch (unified diff, fenced) and the test output in a ticket comment,
move the ticket to Fix, and say in the summary that push access was denied.

## Board refresh (every run, after the ticket work)

The owner's board is the Claude artifact at https://claude.ai/artifact/Vcn1HBEASz9u5WrXTe4ma3 (collection `board`,
documents `tickets` and `health`). Run `python scripts/tracker.py board-docs /tmp/board` and write the two files with
the ArtifactData tool: `set` collection `board` doc `tickets` from `/tmp/board/board_doc.json`, and `set` collection
`board` doc `health` from `/tmp/board/health_doc.json` (read each document first and pass its `version` as
`if_version`). Skip silently if the ArtifactData tool is not available in the session.

## Finish

Summary for the owner, 2–6 plain lines: which tickets moved to which stage, anything needing the owner's decision,
and one line `Health: ok` or `Health: <failing check ids>` read from `health/status.json` on the data branch.
If nothing changed and health is ok: `Quiet hour. Health ok.` and nothing else.
