"""ventures/bounty: scope checker, targets, scan planner, metrics, workflow (no network)."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
BOUNTY = ROOT / "ventures" / "bounty"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


scope_mod = _load("bounty_scope", BOUNTY / "scope.py")
metrics_mod = _load("bounty_metrics", BOUNTY / "metrics.py")
scan_mod = _load("bounty_scan", BOUNTY / "pipeline" / "scan.py")


@pytest.fixture
def scope():
    return scope_mod.Scope.load(BOUNTY / "scope_example.yaml")


def test_scope_deny_by_default_and_exclusions(scope):
    ok = scope.in_scope
    assert ok("api.example.com").allowed and ok("https://deep.sub.example.com/path?x=1").allowed
    assert ok("example.com").allowed  # apex listed explicitly
    assert not ok("legacy.example.com").allowed  # excluded wins over *.example.com
    assert not ok("a.corp.example.com").allowed
    assert not ok("example.org").allowed and not ok("notexample.com").allowed
    assert not ok("evilexample.com").allowed  # suffix trick
    assert ok("203.0.113.9").allowed and not ok("203.0.113.250").allowed and not ok("198.51.100.1").allowed
    assert ok("github.com/example/server").allowed and ok("https://github.com/Example/Server.git").allowed
    assert not ok("github.com/example/other").allowed and not ok("gitlab.com/example/server").allowed
    # unclassifiable targets are refused, never allowed
    for t in ("", "*.example.com", "just-a-word", "mailto:x@example.com"):
        d = ok(t)
        assert not d.allowed and d.kind is None, t
    assert scope.forbids("dos") and scope.forbids("social_engineering") and scope.forbids("production_data")


def test_scope_wildcard_never_matches_apex_and_rejects_bad_files(tmp_path):
    s = scope_mod.Scope.from_dict({"program": "p", "in_scope": {"domains": ["*.x.io"]}})
    assert s.in_scope("a.x.io").allowed and not s.in_scope("x.io").allowed
    with pytest.raises(ValueError):
        scope_mod.Scope.from_dict({"in_scope": {"domains": ["a.b"]}})
    with pytest.raises(ValueError):
        scope_mod.Scope.from_dict({"program": "p", "in_scope": {"hosts": ["a.b"]}})
    with pytest.raises(ValueError):
        scope_mod.Scope.from_dict({"program": "p", "in_scope": {"repos": ["not a repo"]}})
    empty = scope_mod.Scope.from_dict({"program": "p"})
    assert not empty.in_scope("github.com/a/b").allowed and not empty.in_scope("1.1.1.1").allowed


def test_scope_cli(capsys):
    rc = scope_mod.main([str(BOUNTY / "scope_example.yaml"), "api.example.com", "nope.org"])
    out = capsys.readouterr().out
    assert rc == 1 and "IN  api.example.com" in out and "OUT nope.org" in out
    assert scope_mod.main([str(BOUNTY / "scope_example.yaml"), "api.example.com"]) == 0


def test_targets_file_is_well_formed_and_scoped():
    targets = scan_mod.load_targets(BOUNTY / "targets.yaml")
    assert len(targets) >= 10 and len({t["id"] for t in targets}) == len(targets)
    for t in targets:
        assert t["program_url"].startswith("https://"), t["id"]
        assert "http" in t["evidence"], f"{t['id']} evidence needs a URL"
        assert t["platform"] in {"hackerone", "bugcrowd", "intigriti", "yeswehack", "huntr", "direct"}
        lo, hi = t["payout_usd"]
        assert 0 < lo <= hi
        sc = scan_mod.target_scope(t)
        for r in t["scope"]["repos"]:
            assert sc.in_scope(r).allowed
        assert not sc.in_scope("github.com/attacker/anything").allowed
    # a few programs that closed/paused in 2026 must not be targets
    ids = {t["id"] for t in targets}
    assert not ids & {"curl", "nodejs", "ibb", "google_oss_vrp"}


def test_scan_plan_and_dry_run_only_lists_targets_repos(tmp_path):
    targets = scan_mod.load_targets(BOUNTY / "targets.yaml")
    jobs = scan_mod.plan(targets)
    listed = {scope_mod.normalize_repo(r) for t in targets for r in t["scope"]["repos"] if t["scan"]["enabled"]}
    assert jobs and {j["repo"] for j in jobs} == listed
    assert all(j["clone_url"].startswith("https://") and j["clone_url"].endswith(".git") for j in jobs)
    assert all("p/security-audit" in j["rulesets"] for j in jobs)
    only = scan_mod.plan(targets, {"nextcloud"})
    assert {j["target"] for j in only} == {"nextcloud"}
    # a tampered target whose repo list disagrees with its scope is refused before any clone
    bad = dict(targets[0], scope={"repos": ["github.com/x/y"], "exclude_repos": ["github.com/x/y"]})
    with pytest.raises(PermissionError):
        scan_mod.plan([bad])
    out = tmp_path / "out"
    rc = scan_mod.main(["--out", str(out), "--dry-run", "--only", "kubernetes", "--work", str(tmp_path / "w")])
    assert rc == 0
    idx = json.loads((out / "index.json").read_text())
    assert len(idx["runs"]) == 1 and idx["runs"][0]["jobs"][0]["dry_run"] is True
    assert not any((tmp_path / "w").iterdir())  # nothing cloned


def test_scan_run_job_handles_missing_semgrep(tmp_path):
    job = {"target": "t", "platform": "x", "program_url": "u", "repo": "github.com/a/b",
           "clone_url": str(tmp_path / "definitely-missing.git"), "paths": ["."], "depth": 1, "rulesets": ["p/x"]}
    rec = scan_mod.run_job(job, tmp_path / "w", tmp_path / "o", "semgrep-not-installed", dry_run=False)
    assert rec["error"] and rec["findings"] is None and not (tmp_path / "w" / "github.com__a__b").exists()
    cmd = scan_mod.semgrep_cmd("semgrep", ["p/a", "p/b"], ["src"], tmp_path / "x.json")
    assert cmd[:2] == ["semgrep", "scan"] and "--metrics=off" in cmd and cmd.count("--config") == 2 and cmd[-1] == "src"


def test_metrics_schema_summary_and_transitions(tmp_path):
    doc = metrics_mod.load(BOUNTY / "metrics.json")
    s = metrics_mod.summary(doc)
    assert s["submitted"] == 0 and s["paid_usd"] == 0 and s["acceptance_rate"] is None
    base = {"program": "kubernetes", "platform": "hackerone", "title": "t", "severity": "high"}
    doc["reports"] = [
        dict(base, id="r1", state="paid", poc_verified_by="owner", submitted_at="2026-11-01T00:00:00Z",
             triaged_at="2026-11-04T00:00:00Z", paid_at="2026-12-01T00:00:00Z", bounty_usd=1500),
        dict(base, id="r2", state="duplicate", poc_verified_by="owner", submitted_at="2026-11-02T00:00:00Z",
             triaged_at="2026-11-03T00:00:00Z"),
        dict(base, id="r3", state="draft"),
    ]
    assert metrics_mod.validate(doc) == []
    s = metrics_mod.summary(doc)
    assert s["submitted"] == 2 and s["triaged"] == 2 and s["duplicates"] == 1 and s["paid_usd"] == 1500
    assert s["acceptance_rate"] == 0.5 and s["median_days_submit_to_triage"] == 2.0 and s["median_days_submit_to_payout"] == 30.0
    assert s["in_pipeline"] == 1
    md = metrics_mod.render_md(s)
    assert "| Paid $ | 1500.00 |" in md and "50%" in md
    # invariants: no submission without a human-verified PoC; paid needs money + date
    doc["reports"].append(dict(base, id="r4", state="submitted", submitted_at="2026-11-05T00:00:00Z"))
    assert any("poc_verified_by" in e for e in metrics_mod.validate(doc))
    doc["reports"][-1] = dict(base, id="r4", state="paid", poc_verified_by="o", submitted_at="2026-11-05T00:00:00Z")
    assert any("bounty_usd" in e for e in metrics_mod.validate(doc))
    doc["reports"][-1] = dict(base, id="r1", state="draft")
    assert any("duplicate id" in e for e in metrics_mod.validate(doc))
    assert metrics_mod.can_transition("draft", "poc_verified") and not metrics_mod.can_transition("draft", "submitted")
    assert not metrics_mod.can_transition("paid", "draft")
    # scan index fold
    idx = tmp_path / "index.json"
    idx.write_text(json.dumps({"runs": [{"at": "2026-10-20T06:19:00+00:00",
                                         "jobs": [{"repo": "github.com/a/b", "findings": 12}, {"repo": "github.com/c/d", "findings": None, "error": "x"}]}]}))
    doc["reports"] = doc["reports"][:3]
    metrics_mod.fold_scan_index(doc, idx)
    s = metrics_mod.summary(doc)
    assert s["scan_runs"] == 1 and s["scan_repos"] == 1 and s["scan_raw_findings"] == 12 and s["raw_findings_per_paid_report"] == 12.0


def test_bounty_workflow_scans_only_targets_and_never_submits():
    wf = yaml.safe_load((ROOT / ".github/workflows/bounty-scan.yml").read_text())
    steps = wf["jobs"]["scan"]["steps"]
    runs = " ".join(s.get("run", "") for s in steps)
    assert "ventures/bounty/pipeline/scan.py" in runs and "--dry-run" in runs and "HEAD:data" in runs
    assert "HEAD:main" not in runs
    for bad in ("hackerone.com", "bugcrowd.com", "api.hackerone", "report_intents", "curl ", "POST"):
        assert bad not in runs, bad
    assert "git clone" not in runs  # only scan.py clones, and only targets.yaml repos
    assert all(not s.get("env", {}).get("HACKERONE_TOKEN") for s in steps)
    assert "secrets." not in (ROOT / ".github/workflows/bounty-scan.yml").read_text()


def test_bounty_docs_and_registry():
    plan = (BOUNTY / "PLAN.md").read_text()
    for must in ("Hacker API", "Bugcrowd", "Intigriti", "YesWeHack", "Immunefi", "huntr", "W-9", "acceptance rate",
                 "no denial of service", "safe harbor", "2026-10-01", "2026-06-30"):
        assert must.lower() in plan.lower(), must
    assert "https://" in plan
    assert "no submission code" in (BOUNTY / "pipeline" / "submit.md").read_text().lower()
    tri = (BOUNTY / "pipeline" / "TRIAGE.md").read_text()
    assert "--network none" in tri and "poc_verified_by" in tri and "CWE" in tri
    v = yaml.safe_load((ROOT / "configs/ventures.yaml").read_text())["ventures"]
    b = [x for x in v if x["id"] == "bug_bounty_pipeline"]
    assert b and b[0]["verdict"] == "unproven" and b[0]["capital_usd"] == 0
    assert "bounty" in (ROOT / "research/README.md").read_text()
    # no scope-free network constants anywhere in the pipeline code
    for py in (BOUNTY / "scope.py", BOUNTY / "metrics.py", BOUNTY / "pipeline" / "scan.py"):
        src = py.read_text()
        assert "httpx" not in src and "import requests" not in src and "api.hackerone.com" not in src
