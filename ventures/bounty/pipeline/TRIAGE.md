# Stage 2 — triage: no PoC, no report

A Semgrep/CodeQL hit is not a vulnerability. In 2026 every platform that matters
says the same thing in different words: HackerOne bans "claims without a proof of
concept" and hackbots that "operate in a fully autonomous manner"; Bugcrowd suspends
accounts after 10 invalid reports; Nextcloud/YesWeHack say "submission from automated
tools won't be considered and may lead to sanctions (code analysis tools, AI)";
Google's Chrome VRP wants "concise reports that include a reproducer". The pipeline
therefore treats a finding as **non-existent** until a human has watched it reproduce
in an isolated container. Everything below is mandatory and in order.

## 2.1 Intake (agent, offline)

1. Read `data` branch `bounty/<target>/<repo>-<stamp>.json`. Drop every result whose
   rule has `confidence: LOW` or no CWE, every result in tests/, docs/, examples/,
   vendor/, third_party/, and every fingerprint already present in `triage/seen.jsonl`.
2. For each survivor write `triage/<target>/<fingerprint>.md` with: file:line, rule,
   CWE, the exact code, and **one paragraph on why it is probably a false positive**.
   If the agent cannot argue it is a false positive, that is the signal to go on.
3. Fetch (read-only, GitHub only) the project's `SECURITY.md`, its advisory list and
   the last 90 days of security-labelled issues/PRs. If the sink or the file already
   appears in a published advisory or an open security PR, mark `duplicate_suspect`
   and stop. Duplicates are the most common outcome on every platform.
4. Budget: at most **20 survivors per repo per week**, chosen by (CWE severity ×
   reachability from an unauthenticated or low-privilege entry point). The rest wait.

## 2.2 Reachability (agent, offline)

For each survivor trace the data flow from a concrete entry point (HTTP handler, CLI
flag, file parser, RPC method) to the sink. Produce a numbered path with file:line at
every hop. If any hop requires a privilege the program's threat model excludes (admin
on the same box, a malicious maintainer, physical access), mark `out_of_threat_model`
and stop. If the path cannot be completed with evidence, mark `unreachable_so_far`
and stop. Never guess a hop; "likely" is not a hop.

## 2.3 Reproduction (human-run, isolated container)

Only the owner (or a human they delegate) runs this. The agent prepares, the human
executes and watches.

* Environment: a throwaway container or VM with **no credentials, no network
  except to pull the project's own release artifacts, and no production data**.
  `docker run --rm --network none` after the build step is the default. The
  vulnerable commit is pinned (`poc_commit`); the build uses the project's own
  documented build/run instructions.
* The PoC is a script (`poc/<id>/run.sh` + whatever it needs) that: starts the
  target, sends the malicious input, and **asserts** the impact in a way a triager
  can see in one screen: a file created outside the sandbox dir, a shell command's
  output echoed back, a row read that the test user must not see, a crash with an
  ASan/UBSan report. "The debugger shows the tainted value" is not impact.
* Impact must be against *your own* instance and *your own* test accounts. No PoC
  ever touches a program's production hosts, other users' data, or a third party.
* No denial of service PoCs on anything you do not run yourself; for crash bugs the
  evidence is the sanitizer trace from a local build, nothing else.
* Record: exact commands, container image digest, the vulnerable commit, the output,
  and a 30-90 s screen recording or asciinema cast. Then try it on the latest
  release *and* on `main`. If `main` already fixed it, the report is dead
  (platforms pay for unknown bugs, not for "not yet released" ones, unless the
  program says otherwise).
* Severity: compute CVSS 3.1 **and** 4.0 vectors honestly. Inflating severity is a
  HackerOne Code-of-Conduct violation on its own.

A finding becomes `poc_verified` in `metrics.json` only when the human who ran it
puts their name in `poc_verified_by`. The agent may not set that field.

## 2.4 Report draft (agent, then human-rewritten)

The human rewrites the draft in their own words before approval; both YesWeHack and
Intigriti require disclosing LLM use, and HackerOne holds the member "fully
responsible" for anything AI-assisted. Keep it short: triagers now prefer concise
reports with a reproducer over long AI prose.

Fields below match HackerOne's report form (title, severity/CVSS, weakness/CWE,
asset, description, steps, impact, attachments) and huntr's / YesWeHack's
(vulnerability type, affected version, PoC, impact, remediation). Fill every line
or delete the report.

```
Title:            <one line: <vuln class> in <component> allows <impact> via <input>>
Asset / scope:    <exact structured-scope entry from the program page, copied verbatim>
Affected version: <tag or commit sha>; fixed in: <none | sha>
Weakness (CWE):   CWE-<n> <name>
Severity:         <program's scale> — CVSS 3.1 <vector> (<score>); CVSS 4.0 <vector>
Summary:          <2-3 sentences: what, where, who can trigger it, what they get>
Steps to reproduce:
  1. <exact command / request>
  2. ...
  N. Observe: <the assertion the PoC makes>
Proof of concept:  attached poc.tar.gz (run.sh, Dockerfile, expected_output.txt) + <recording>
Impact:           <concrete: which data/accounts/hosts, which precondition, realistic attacker>
Root cause:       <file:line, the missing check>
Suggested fix:    <one paragraph or a diff; several OSS programs add a bonus for a patch>
Disclosure:       <we follow the program's policy; no public disclosure before fix + program consent>
AI assistance:    <"Static analysis and initial draft were AI-assisted; reproduction and
                   this text are by <name>." — required by YesWeHack/Intigriti, honest everywhere>
```

## 2.5 Gate to stage 3

Move to `approved` only when all of these are true, checked by the human:

- [ ] target is `in_scope` per `ventures/bounty/scope.py` against a scope file copied
      from the program page **today** (scopes change; cite `copied_on`)
- [ ] `poc_verified_by` is a human name and the recording exists
- [ ] the PoC never touched a production host, real user data, or a third party
- [ ] no DoS, no social engineering, no credential use beyond a single read-only
      liveness check (secrets niche), no automated traffic to the program's hosts
- [ ] not already fixed on `main`; no matching advisory or open security PR
- [ ] severity is what the PoC shows, not what the rule says
- [ ] the report text is human-rewritten and discloses AI assistance
- [ ] this program has received fewer than **2 reports from us in the last 30 days**
      (hard cap while acceptance rate < 50 %; see submit.md)

Anything that fails goes back to `draft` or `withdrawn`, with the reason in `notes`,
so the acceptance-rate metric stays honest.
