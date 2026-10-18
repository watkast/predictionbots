"""Loader + summary for ventures/bounty/metrics.json.

Schema (schema_version 1)::

    {
      "schema_version": 1,
      "updated": "<iso8601>",
      "reports": [
        {
          "id": "2026-10-20-kubernetes-001",      # unique, date-prefixed
          "program": "kubernetes",                # id from targets.yaml
          "platform": "hackerone",
          "title": "...",
          "severity": "critical|high|medium|low|informational",
          "cvss": 7.5,                            # optional
          "state": "<one of STATES>",
          "poc_verified_by": "owner",             # human who reproduced it (required before approved)
          "poc_commit": "<sha of the vulnerable commit>",
          "created_at": "<iso>", "approved_at": "<iso>", "submitted_at": "<iso>",
          "triaged_at": "<iso>", "closed_at": "<iso>", "paid_at": "<iso>",
          "bounty_usd": 0.0,                      # received, after platform fees
          "platform_ref": "#1234567",             # report id on the platform
          "notes": ""
        }
      ],
      "scans": {"runs": n, "repos_scanned": n, "raw_findings": n, "last_run": "<iso>"}
    }

States and allowed transitions (STATES / NEXT):
  draft -> poc_verified -> approved -> submitted -> triaged -> {resolved -> paid, duplicate, informative, not_applicable, spam}
  A report may be withdrawn from any state before 'triaged'.

Dashboard integration (NOT wired yet; scripts/dashboard.py is untouched): call
``summary(load(path))`` and render the dict as one tile row: submitted, triaged,
duplicates, paid $, acceptance %, median days submit->triage and submit->payout,
plus the scan totals. The same dict is printed by ``python ventures/bounty/metrics.py``.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DEFAULT_PATH = HERE / "metrics.json"

STATES = ("draft", "poc_verified", "approved", "submitted", "triaged", "resolved", "paid",
          "duplicate", "informative", "not_applicable", "spam", "withdrawn")
TERMINAL_NEGATIVE = {"duplicate", "informative", "not_applicable", "spam"}
NEXT = {
    "draft": {"poc_verified", "withdrawn"},
    "poc_verified": {"approved", "draft", "withdrawn"},
    "approved": {"submitted", "withdrawn"},
    "submitted": {"triaged", "withdrawn", "duplicate", "informative", "not_applicable", "spam"},
    "triaged": {"resolved", "duplicate", "informative", "not_applicable", "spam"},
    "resolved": {"paid"},
    "paid": set(), "duplicate": set(), "informative": set(), "not_applicable": set(), "spam": set(), "withdrawn": set(),
}
SEVERITIES = ("critical", "high", "medium", "low", "informational")
REQUIRED = ("id", "program", "platform", "title", "severity", "state")


def _ts(s: str | None) -> datetime | None:
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def validate(doc: dict[str, Any]) -> list[str]:
    """Return a list of problems; empty means the file is well-formed."""
    errs: list[str] = []
    if doc.get("schema_version") != 1:
        errs.append("schema_version must be 1")
    seen: set[str] = set()
    for i, r in enumerate(doc.get("reports") or []):
        tag = f"reports[{i}]"
        for k in REQUIRED:
            if not r.get(k):
                errs.append(f"{tag}: missing {k}")
        if r.get("id") in seen:
            errs.append(f"{tag}: duplicate id {r.get('id')}")
        seen.add(r.get("id"))
        if r.get("state") not in STATES:
            errs.append(f"{tag}: bad state {r.get('state')}")
        if r.get("severity") not in SEVERITIES:
            errs.append(f"{tag}: bad severity {r.get('severity')}")
        st = r.get("state")
        if st in ("approved", "submitted", "triaged", "resolved", "paid") and not r.get("poc_verified_by"):
            errs.append(f"{tag}: state {st} requires poc_verified_by (a human who reproduced the PoC)")
        if st in ("submitted", "triaged", "resolved", "paid") and not r.get("submitted_at"):
            errs.append(f"{tag}: state {st} requires submitted_at")
        if st == "paid" and not (r.get("paid_at") and float(r.get("bounty_usd") or 0) > 0):
            errs.append(f"{tag}: state paid requires paid_at and bounty_usd > 0")
        for k in ("created_at", "approved_at", "submitted_at", "triaged_at", "closed_at", "paid_at"):
            try:
                _ts(r.get(k))
            except ValueError:
                errs.append(f"{tag}: {k} is not ISO-8601")
    return errs


def can_transition(frm: str, to: str) -> bool:
    return to in NEXT.get(frm, set())


def load(path: str | Path = DEFAULT_PATH) -> dict[str, Any]:
    doc = json.loads(Path(path).read_text())
    errs = validate(doc)
    if errs:
        raise ValueError("; ".join(errs))
    return doc


def summary(doc: dict[str, Any]) -> dict[str, Any]:
    reps = doc.get("reports") or []
    submitted = [r for r in reps if r.get("submitted_at")]
    triaged = [r for r in reps if r.get("triaged_at") or r.get("state") in ("triaged", "resolved", "paid")]
    paid = [r for r in reps if r.get("state") == "paid"]
    dup = [r for r in reps if r.get("state") == "duplicate"]
    closed_neg = [r for r in reps if r.get("state") in TERMINAL_NEGATIVE]
    decided = [r for r in submitted if r.get("state") in TERMINAL_NEGATIVE | {"resolved", "paid"}]
    accepted = [r for r in decided if r["state"] in ("resolved", "paid")]

    def days(a: str, b: str, rows) -> float | None:
        d = []
        for r in rows:
            ta, tb = _ts(r.get(a)), _ts(r.get(b))
            if ta and tb:
                d.append((tb - ta).total_seconds() / 86400)
        return round(statistics.median(d), 1) if d else None

    by_sev = {s: sum(1 for r in reps if r.get("severity") == s) for s in SEVERITIES}
    scans = doc.get("scans") or {}
    return {
        "reports_total": len(reps),
        "in_pipeline": sum(1 for r in reps if r.get("state") in ("draft", "poc_verified", "approved")),
        "submitted": len(submitted),
        "triaged": len(triaged),
        "duplicates": len(dup),
        "closed_negative": len(closed_neg),
        "accepted": len(accepted),
        "paid_reports": len(paid),
        "paid_usd": round(sum(float(r.get("bounty_usd") or 0) for r in paid), 2),
        "acceptance_rate": round(len(accepted) / len(decided), 3) if decided else None,
        "median_days_submit_to_triage": days("submitted_at", "triaged_at", submitted),
        "median_days_submit_to_payout": days("submitted_at", "paid_at", paid),
        "by_severity": by_sev,
        "scan_runs": int(scans.get("runs") or 0),
        "scan_repos": int(scans.get("repos_scanned") or 0),
        "scan_raw_findings": int(scans.get("raw_findings") or 0),
        "scan_last_run": scans.get("last_run"),
        "raw_findings_per_paid_report": (round(int(scans.get("raw_findings") or 0) / len(paid), 1) if paid else None),
    }


def fold_scan_index(doc: dict[str, Any], index_path: str | Path) -> dict[str, Any]:
    """Fill doc['scans'] from the data branch bounty/index.json written by pipeline/scan.py."""
    idx = json.loads(Path(index_path).read_text())
    runs = idx.get("runs") or []
    jobs = [j for r in runs for j in (r.get("jobs") or [])]
    doc["scans"] = {
        "runs": len(runs),
        "repos_scanned": len({j.get("repo") for j in jobs if j.get("findings") is not None}),
        "raw_findings": sum(int(j.get("findings") or 0) for j in jobs),
        "last_run": runs[-1]["at"] if runs else None,
    }
    return doc


def render_md(s: dict[str, Any]) -> str:
    rows = [("Submitted", s["submitted"]), ("Triaged", s["triaged"]), ("Duplicates", s["duplicates"]),
            ("Accepted", s["accepted"]), ("Paid reports", s["paid_reports"]), ("Paid $", f"{s['paid_usd']:.2f}"),
            ("Acceptance rate", "n/a" if s["acceptance_rate"] is None else f"{100 * s['acceptance_rate']:.0f}%"),
            ("Median days submit->triage", s["median_days_submit_to_triage"] or "n/a"),
            ("Median days submit->payout", s["median_days_submit_to_payout"] or "n/a"),
            ("Scan runs / repos / raw findings", f"{s['scan_runs']} / {s['scan_repos']} / {s['scan_raw_findings']}")]
    return "| metric | value |\n|---|---|\n" + "\n".join(f"| {k} | {v} |" for k, v in rows) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="summarize bounty metrics")
    ap.add_argument("--path", default=str(DEFAULT_PATH))
    ap.add_argument("--scans", default="", help="data-branch bounty/index.json to fold in (not written back)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    doc = load(a.path)
    if a.scans:
        fold_scan_index(doc, a.scans)
    s = summary(doc)
    print(json.dumps(s, indent=1) if a.json else render_md(s))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
