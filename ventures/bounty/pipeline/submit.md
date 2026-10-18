# Stage 3 — submission: human-approval gate, no code

There is deliberately **no submission code** in this repo and there will not be
one. HackerOne's Code of Conduct (https://www.hackerone.com/policies/code-of-conduct)
says hackbots "must not operate in a fully autonomous manner" and sanctions
large-scale low-quality submissions with a final warning, a 12-month ban, then a
permanent ban; Bugcrowd (2026-03-10) permanently bans "submission farming" and
suspends after 10 consecutive invalids; Nextcloud/YesWeHack sanction automated-tool
submissions outright. One banned account ends the venture, and the owner may hold
exactly one account per platform. So the last mile is a person, on the platform's
own web form, every time.

## Who may submit

Only the owner, logged in to their own single account, after the TRIAGE.md 2.5
checklist is ticked and the report is in state `approved` in
`ventures/bounty/metrics.json`. Agents prepare files; they never hold platform
credentials. The HackerOne Hacker API token, if one is ever created, is used
**read-only** (`GET /hackers/programs/{handle}/structured_scopes` to refresh scope
files, `GET /hackers/me/reports` and `/hackers/payments/*` to fill metrics) and
lives only in the owner's password manager, never in GitHub secrets.

## Procedure (10 minutes per report)

1. Open the program page and re-read scope, exclusions and the current "AI /
   automated tools" clause. If the clause changed, stop and update `PLAN.md`.
2. Confirm the asset string in the draft equals a structured-scope entry verbatim.
3. Paste the human-rewritten report; attach `poc.tar.gz` and the recording. Choose
   the severity the PoC demonstrates. Tick the AI-assistance disclosure where the
   form has one; otherwise it stays in the report body.
4. Submit. Copy the platform reference into `metrics.json` (`platform_ref`,
   `submitted_at`, state `submitted`). Commit.
5. Reply to triager questions within 24 h, from the same account, in your own
   words. Never argue severity more than once; never resubmit a closed report.
6. When the platform decides, set the terminal state and the timestamps. If paid,
   record the net amount the day it lands (`paid_at`, `bounty_usd`).

## Rate limits we impose on ourselves

* **2 reports per program per 30 days** until that program's acceptance rate over
  the last 6 decided reports is at least 50 %; then 4.
* **6 reports per platform per 30 days** total.
* Two consecutive `not_applicable`/`spam` outcomes on any platform freeze all
  submissions there until the owner has reviewed every open draft.
* Any `spam` verdict anywhere halts the whole venture pending a written post-mortem
  in `ventures/bounty/PLAN.md`.

## Never

* submit from an agent, a script, the Hacker API `POST /hackers/reports`, or
  Report Intents (`POST /hackers/report_intents`) — these exist, we do not use them;
* submit the same bug to two programs or to a program and a CVE CNA at once;
* disclose publicly before the program's policy allows it (HackerOne treats
  uncoordinated disclosure as final-warning-then-permanent-ban);
* test on, or send traffic to, anything outside the scope file;
* use a found credential for anything beyond one read-only liveness check.
