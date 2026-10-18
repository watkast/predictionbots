# Bug-bounty venture — operating plan (2026-10-17)

Honest premise. `research/non_trading_ventures.md` ranked a *validated-exploit*
bounty pipeline #2 ("$0 for 3-6 months, then $500-3k lumpy"). The platform facts
checked today make 2026 the worst year on record for automated OSS bounty hunting:

| event | date | source |
|---|---|---|
| curl ends its HackerOne bounty: valid-report rate fell below 5 % in 2025, 87 CVEs / $100k+ over 6 yrs | 2026-01-26 | https://daniel.haxx.se/blog/2026/01/26/the-end-of-the-curl-bug-bounty/ (back on H1 reputation-gated, 2026-04-22: https://daniel.haxx.se/blog/2026/04/22/high-quality-chaos/) |
| Node.js requires HackerOne Signal >= 1.0 after "over 30 reports" in one holiday month | Jan/Feb 2026 | https://nodejs.org/en/blog/announcements/hackerone-signal-requirement |
| Bugcrowd: queues +334 % in three weeks; 10 invalids -> ID check, 10 consecutive -> 30-day suspension, farming -> permanent ban | 2026-03-10 | https://www.bugcrowd.com/blog/bugcrowd-policy-changes-to-address-ai-slop-submissions/ |
| HackerOne pauses the Internet Bug Bounty (IBB, $1.5M paid since 2012); Node.js keeps triaging but stops paying | Apr 2026 | https://www.infoworld.com/article/4154210/internet-bug-bounty-program-hits--on-payouts.html , https://www.privacyguides.org/news/2026/04/17/hackerone-pauses-internet-bug-bounty/ |
| huntr (Palo Alto Networks) stops its OSS vulnerability program; pivots to $15k-pot challenges; only the Model File Format program still takes standard submissions | 2026-06-30 | https://blog.huntr.com/huntr-2-0-faq |
| Google OSS VRP pauses *product* vulnerability rewards ("a significant rise in automated submissions, the vast majority of which are not valid"); supply-chain tier stays | 2026-10-01 | https://thehackernews.com/2026/10/google-pauses-oss-product-bug-bounty.html |
| GitHub Security Lab CodeQL bounty: "no longer active" | — | https://securitylab.github.com/bounties/ |
| Google Chrome VRP cuts standard payouts, drops 2025 bonuses over "an overwhelming influx of AI-generated reports"; still paid a record $17.1M across VRPs in 2025 | 2026-05 | https://securityaffairs.com/191600/security/google-revamps-bug-bounty-programs-android-rewards-rise-chrome-payouts-drop-in-the-age-of-ai.html |

So: the aggregator money for OSS bugs (IBB, Google OSS VRP, huntr, GitHub) is gone
or paused; what remains is **self-run programs by well-funded OSS vendors**
(Kubernetes, GitLab, Nextcloud, Grafana, Mattermost, Mozilla, Microsoft .NET,
WordPress, Chromium) plus the **AI-product programs** (Google AI VRP). Every one of
them now gates on a reproduced PoC and most explicitly sanction automated-tool
output. The venture is still worth a small, capped build because the stack we
already own (Actions runners, an agent that can read code and write PoCs) costs
nothing to point at it. Expected year-1 result: **$0-3,000 total, most likely $0**;
the realistic upside is one or two High findings in a Go/PHP code base at
$1-5k each. Anything in `configs/ventures.yaml` stays `verdict: unproven` until a
payment lands.

## (a) Platforms

| platform | program discovery / submission API | payouts by severity (public examples) | triage time | on AI / automation |
|---|---|---|---|---|
| **HackerOne** https://hackerone.com | Hacker API https://api.hackerone.com/hacker-resources/ (Basic auth `username:token`): `GET /v1/hackers/programs`, `/programs/{handle}/structured_scopes`, `/scope_exclusions`, `/weaknesses`, `GET /hackers/me/reports`, `/payments/{balance,earnings,payouts}`; `POST /hackers/reports` and Report Intents exist — **we do not call them** (submit.md). Customer-API limits: 600 reads/min, 25 writes/20 s (https://api.hackerone.com/getting-started); hacker limits undocumented. | Kubernetes $100-10,000 (CVSS); GitLab $100-35,000+; WordPress $150-1,337+; Neon $150/$500/$1,500/$3,000 L/M/H/C (https://codenote.net/en/posts/oss-bug-bounty-program-cases/). $300M+ paid platform-wide. | program-set SLAs, typically first response in 1-5 business days, bounty on triage or on fix; months to payout on OSS programs | Code of Conduct https://www.hackerone.com/policies/code-of-conduct : AI "permitted and encouraged" but members are "fully responsible"; forbidden: "large volumes of low-signal or non-actionable reports", claims "without a proof of concept", "invented endpoints or unsupported impact claims"; "Hackbots must not operate in a fully autonomous manner"; must respect program "limits on automation, request volume, and rate limiting". Sanctions: final warning -> 12-month ban -> permanent; one account per person; ban evasion = permanent. Node.js additionally requires Signal >= 1.0. |
| **Bugcrowd** https://bugcrowd.com/engagements | Programs listed on the web; the Bugcrowd API is customer-facing (https://docs.bugcrowd.com/api/), researchers submit via the web form. | Mattermost: amount decided after validation, ack in 2 business days, decision in 5 (https://mattermost.com/security-vulnerability-report/); PostHog VDP pays swag only. | days to weeks; Bugcrowd triages before the customer sees it | 2026-03-10 policy: 10 invalid reports -> identity verification; 10 consecutive invalids attributable to AI/automation -> 30-day suspension; "submission farming" -> permanent ban; automation that squats common finding types at launch -> enforcement. |
| **Intigriti** https://app.intigriti.com | Web only for researchers (platform API is customer-side). Grafana OSS program: https://app.intigriti.com/company/programs/grafanalabs/grafanaossbbp/detail | Grafana: CVSS-tiered, no NDA (https://grafana.com/blog/2024/07/24/grafana-labs-bug-bounty-what-you-need-to-know-about-our-new-partnership-with-intigriti) | Intigriti triage first (hours-days), then the customer | "requires human verification of all findings, working proof of concepts"; AI use must be disclosed under the Community Code of Conduct; AI Triage Assist flags likely-invalid reports (https://www.intigriti.com/blog/business-insights/the-ai-impact-a-triagers-perspective) |
| **YesWeHack** https://yeswehack.com/programs | Web only. Nextcloud program: https://yeswehack.com/programs/nextcloud | Nextcloud EUR 500 / 1,500 / 5,000 / 10,000 (L/M/H/C), average paid EUR 700 | Nextcloud: average reward EUR 700 suggests mostly Low/Medium; weeks | Nextcloud rules: "submission from automated tools won't be considered and may lead to sanctions (code analysis tools, AI, ...)"; LLM use must be disclosed and only locally run LLMs; DoS forbidden; "Targeting other users' instances is forbidden, only test against your own." |
| **Immunefi** https://immunefi.com | Web only; crypto protocols. | $134M cumulative paid by Mar-2026; 230 programs; Q1-2026 average $7,131/report ($4,406 ex one $3M payout) (https://www.kucoin.com/blog/en-immunefi-ecosystem-2026-q1-update) | weeks; payout in stablecoins/tokens, many programs require KYC | PoC on a forked chain is mandatory; **out of our initial scope** — needs Solidity/EVM tooling and the biggest bounties go to full-time auditors. |
| **huntr** https://huntr.com | Web. OSS program closed 2026-06-30 (locked 2026-07-31); challenges with $15k pots ranked by leaderboard; Model File Format program still takes standard submissions (https://blog.huntr.com/huntr-2-0-faq , https://huntr.com/guidelines) | historical base $1,500 (ML frameworks/inference), $900-1,500 (data science), up to 10x for model/training-data access | historical: weeks-months | challenges replace written reports with live exploitation; no per-report AI rule published |
| **Google** https://bughunters.google.com | Web form (Bug Hunters). OSS VRP rules https://bughunters.google.com/about/rules/6521337925468160/google-open-source-software-vulnerability-reward-program-rules ; AI VRP rules https://bughunters.google.com/about/rules/5222232590712832/ai-vulnerability-reward-program-rules | OSS VRP (paused for product bugs since 2026-10-01): flagship $500-7,500, important $101-3,133.7; still open: supply-chain compromise $3,133.7-31,337 flagship, leaked write-capable credentials $500-1,000, Patch Rewards $100-15,000. AI VRP (2025-10-06): rogue actions $20k flagship / $15k / $10k, up to $30k with quality multipliers; direct prompt injection, jailbreaks and alignment issues are **out of scope** (https://www.theregister.com/2025/10/07/google_ai_bug_bounty/). Chrome: memory-safety base $500 + multipliers, full chain up to $250k. | weeks; panel decides reward after fix | OSS VRP paused precisely because of automated submissions; Chrome wants "concise reports that include a reproducer"; stronger proof required for some tiers since 2026-03 |
| **Microsoft MSRC** https://www.microsoft.com/en-us/msrc/bounty | MSRC Researcher Portal (web). | .NET / ASP.NET Core up to $40,000 (https://www.microsoft.com/en-us/msrc/blog/2025/07/net-bounty-program-now-offers-up-to-40000-in-awards); other programs to $100k+ | 1-2 weeks to case assignment, payment after fix (often 1-3 months) | requires a working PoC and current supported release; no public AI clause found (not verified) |
| **Meta** https://bugbounty.meta.com | Web. | public minimum $500, large payouts for account takeover / RCE (amounts not re-verified today) | days-weeks | not re-verified today; treat as "PoC required" like the others |
| **GitHub Security Lab** https://securitylab.github.com/bounties/ | — | — | — | CodeQL bounty closed; GitHub's own product bounty https://bounty.github.com/ remains (not an OSS program) |

Triage-time note: no platform publishes a researcher-facing SLA for OSS programs;
the HackerOne Hacker API `/hackers/me/reports` timestamps are the only way to
measure ours, which is why metrics.json records every timestamp.

## (b) Scope rules the pipeline enforces

`ventures/bounty/scope.py` is deny-by-default: a target (repo, domain, IP) is in
scope only if it matches an `in_scope` entry of a scope file copied from the
program page (with `copied_on`) and no `out_of_scope` entry; wildcards never match
the apex; unknown target kinds are refused. `pipeline/scan.py` runs that check on
every repo in `targets.yaml` before cloning, and `targets.yaml` is the only source
of clone URLs. Beyond asset lists, these rules are enforced by the stage documents
and the human gate (TRIAGE.md 2.5, submit.md):

1. **In-scope assets only**, verbatim strings from the program's structured scope.
2. **No denial of service** of anything we do not run ourselves; crash bugs are
   evidenced by sanitizer traces from a local build.
3. **No social engineering, phishing, or physical** anything (every program excludes it).
4. **No testing against production hosts or other users' data**: reproduction
   happens on our own instance in a network-isolated container (`--network none`).
5. **Rate limits**: no automated traffic to program hosts at all in stage 1-2; the
   only network calls are `git clone` of public repos and read-only GitHub reads.
   `max_requests_per_second` in the scope file caps any future dynamic stage.
6. **Secrets**: a leaked credential gets at most one read-only liveness call
   (e.g. `sts get-caller-identity`), never a second action; then it is reported
   or dropped, never stored outside the report.
7. **Safe harbor**: we only act inside programs whose policy contains safe-harbor
   language (HackerOne's and Bugcrowd's standard disclosure terms, Google's and
   Mozilla's rules do; direct-to-vendor emails without a published policy do not
   count). The scope file's `url` must point at that policy.
8. **Self-imposed volume caps** (submit.md): 2 reports/program/30 days, 6/platform,
   freeze on two consecutive N/A verdicts, full halt on any "spam" verdict.
9. **Disclosure**: coordinated only; we never publish before the program allows.

## (c) Niches, ranked

Grades as in the research memos: [A] platform/regulator disclosure, [B] detailed
case data, [C] vendor blog, [D] anecdote. "$/mo" is the honest expected value for
this operator in months 6-12, not the first quarter (which is $0 everywhere).

| rank | niche | evidence | expected $/mo (6-12 mo) | ban risk | verdict |
|---|---|---|---|---|---|
| 1 | **OSS code bugs via Semgrep/CodeQL + targeted fuzzing, reported to self-run vendor programs** (Kubernetes, GitLab, Nextcloud, Grafana, Mattermost, .NET, WordPress; Firefox/Chromium only with a self-hosted fuzz box) | [A] program pages in targets.yaml; [B] ZeroPath-assisted review found 100+ real curl bugs when a human drove it (https://daniel.haxx.se/blog/2025/10/10/a-new-breed-of-analyzers/); [A] but the aggregators that paid for exactly this (IBB, Google OSS VRP, huntr, GitHub) all paused or closed in 2026 | $0-800 lumpy (one Medium/High every 1-3 months at $500-5k if the PoC discipline holds) | low **if** every report ships with a reproducer and volume stays under the caps; medium otherwise (Nextcloud sanctions tool output outright) | build; the only niche where our existing stack adds value |
| 2 | **AI-product bugs: indirect prompt injection -> data exfiltration / rogue actions** in Google AI VRP (and equivalent Microsoft/Meta/OpenAI programs) | [A] Google AI VRP pays $10-30k for rogue actions / exfil, excludes direct injection and jailbreaks; [C] breachloom/industry: most LLM-app reports are rejected as "model behavior" not vulnerabilities | $0-500 (one payable finding a year would be a win) | low-medium: testing is against production SaaS with your own accounts only; a wrong move (other users' data) is a ban and possibly a CFAA problem | second, manual-first: the agent drafts payload families, the human runs them in own accounts |
| 3 | **Secrets leaked in public repos / CI logs** | [A] Google OSS VRP still pays $500-1,000 for write-capable leaked credentials; [A] GitHub secret scanning auto-revokes most partner tokens at push (https://docs.github.com/en/code-security/secret-scanning/secret-scanning-partner-program), so what survives is mostly dead or third-party; most programs treat third-party creds as out of scope | $0-200 | medium-high: every "verification" beyond one read-only call is unauthorized access; many programs class this as low or informative | verify-once-only side channel on repos already in targets.yaml; never a crawler |
| 4 | **Subdomain takeover & misconfig scanning** on programs with wildcard web scope | [D] write-ups put typical payouts at $100-2,000 (https://thehackerslog.substack.com/p/the-secret-life-of-subdomains-from); [B] it is the most automated niche on earth (thousands of hunters run the same can-i-take-over-xyz lists), so duplicate rates are extreme | $0-100 | high: continuous DNS/HTTP probing of program assets is exactly the "request volume" clause HackerOne sanctions; no OSS program in targets.yaml has web scope | do not build |

Why not Immunefi despite the biggest payouts ($7k average, $134M paid): the
work is EVM/Solidity auditing with forked-chain PoCs, a different stack, and the
payers are protocols that routinely dispute severity; revisit only if the trading
side of this repo ever builds EVM tooling.

## (d) One-time human steps (owner, ~2 hours, phone-friendly)

(Identity-check and payout-rail details below are from the platforms' help
centres as remembered, not re-fetched today; confirm each in the settings page.)

1. **HackerOne**: create the single account (https://hackerone.com/users/sign_up),
   enable 2FA, fill the profile, complete the (free) Hacker101 CTF levels to earn
   invite eligibility; **ID verification** is required for private programs and
   some public ones (HackerOne Clear / government-ID check in Settings).
   Generate a Hacker API token (Settings -> API token) and keep it in the
   password manager only; it is read-only by policy here.
2. **Bugcrowd**: account at https://bugcrowd.com, 2FA, ID verification (Bugcrowd
   asks for it after 10 invalid reports anyway; doing it first avoids a freeze).
3. **Intigriti** (https://app.intigriti.com) and **YesWeHack** (https://yeswehack.com):
   accounts + ID verification (both require it before payout).
4. **Direct programs**: Google Bug Hunters profile (https://bughunters.google.com),
   MSRC Researcher Portal (https://msrc.microsoft.com/report), Mozilla Bugzilla account.
5. **Tax**: all platforms collect a **W-9** from US persons before the first payout
   and issue a 1099 above the IRS threshold; bounties are self-employment income
   (set aside ~30 %). Keep the W-9 details identical across platforms.
6. **Payout rails**: HackerOne pays via PayPal, Payoneer, bank transfer or crypto;
   Bugcrowd via PayPal/Payoneer/bank; Intigriti and YesWeHack via bank transfer
   (Intigriti also PayPal); Google via Bugcrowd-style payment partner or wire.
   Set these up before the first report so a payment does not stall for a month.
7. **Decide the AI-disclosure sentence** you will put in every report (TRIAGE.md 2.4)
   and keep it true.

## (e) Dashboard metrics (from `metrics.json` via `metrics.py`)

* reports: total, in pipeline (draft/poc_verified/approved), **submitted**,
  **triaged**, **duplicates**, closed-negative (informative / N/A / spam), accepted
* **paid $** (net received) and paid report count; by severity
* **acceptance rate** = accepted / decided (decided = resolved+paid+duplicate+informative+N/A+spam)
* **median days submit -> triage** and **submit -> payout**
* scan volume: runs, repos scanned, raw findings, and raw findings per paid report
  (the honesty ratio: if it is in the thousands, the scanner is noise)
* the two kill-switches from submit.md shown as a status pill: per-platform freeze,
  venture halt

`scripts/dashboard.py` is untouched for now; integration is one tile row fed by
`metrics.summary(metrics.load(...))` once the first report exists.

## Build order

1. `bounty-scan.yml` runs weekly on `targets.yaml` (done; stage 1).
2. Triage one repo by hand end-to-end (Nextcloud or Kubernetes) following TRIAGE.md;
   expect the first 50 findings to be false positives. Record the ratio.
3. Only after one PoC reproduces in a container: owner does (d), submits one report.
4. Re-rank niches when the first decision comes back; update `configs/ventures.yaml`.
