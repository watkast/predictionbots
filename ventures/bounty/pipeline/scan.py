"""Stage 1: static-analysis runner for the repos listed in ventures/bounty/targets.yaml.

What it does
  * reads targets.yaml, builds a Scope per target and REFUSES any repo that the
    target's own scope block does not list (deny-by-default, see ../scope.py);
  * shallow-clones each enabled repo into a scratch dir;
  * runs Semgrep with security rulesets on the listed paths (or the whole repo);
  * writes one JSON file per repo plus an index to --out (data branch, bounty/).

What it never does: contact a bounty platform, open an issue, or send anything.
Findings are raw scanner output; TRIAGE.md says what has to happen before any of
them can become a report (a human-run, reproduced PoC in an isolated container).

Usage
  python ventures/bounty/pipeline/scan.py --out data/bounty [--targets ventures/bounty/targets.yaml]
         [--only kubernetes,nextcloud] [--dry-run] [--semgrep semgrep]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

HERE = Path(__file__).resolve().parent
BOUNTY_DIR = HERE.parent

# Semgrep registry rulesets; all security-oriented, none "best practice".
DEFAULT_RULESETS = ["p/security-audit", "p/secrets", "p/owasp-top-ten", "p/command-injection", "p/sql-injection", "p/xss"]
LANG_RULESETS = {
    "go": ["p/golang"], "python": ["p/python"], "javascript": ["p/javascript", "p/nodejs"],
    "typescript": ["p/typescript"], "php": ["p/php"], "ruby": ["p/ruby"], "csharp": ["p/csharp"],
    "cpp": ["p/c"], "java": ["p/java"],
}


def _load_scope_module():
    spec = importlib.util.spec_from_file_location("bounty_scope", BOUNTY_DIR / "scope.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bounty_scope"] = mod  # dataclasses need the module registered
    spec.loader.exec_module(mod)
    return mod


scope_mod = _load_scope_module()


def load_targets(path: Path) -> list[dict[str, Any]]:
    doc = yaml.safe_load(path.read_text()) or {}
    targets = doc.get("targets") or []
    for t in targets:
        for k in ("id", "project", "platform", "program_url", "evidence", "scope", "scan"):
            if k not in t:
                raise ValueError(f"target {t.get('id', '?')} missing '{k}'")
        if not (t["scope"].get("repos") or []):
            raise ValueError(f"target {t['id']} lists no repos")
    return targets


def target_scope(t: dict[str, Any]):
    return scope_mod.Scope.from_dict({
        "program": t["id"], "platform": t["platform"], "url": t["program_url"],
        "in_scope": {"repos": list(t["scope"].get("repos") or [])},
        "out_of_scope": {"repos": list(t["scope"].get("exclude_repos") or [])},
        "rules": {"no_dos": True, "no_social_engineering": True, "no_production_data": True,
                  "allowed_methods": ["static_analysis", "local_reproduction"]},
    })


def plan(targets: list[dict[str, Any]], only: set[str] | None = None) -> list[dict[str, Any]]:
    """Return the clone/scan jobs; every repo passes the target's own scope check."""
    jobs = []
    for t in targets:
        if only and t["id"] not in only:
            continue
        if not t["scan"].get("enabled", False):
            continue
        sc = target_scope(t)
        for repo in t["scope"]["repos"]:
            d = sc.in_scope(repo)
            if not d.allowed:  # cannot happen for a well-formed file, but never trust input
                raise PermissionError(f"refusing {repo}: {d.reason}")
            rulesets = list(DEFAULT_RULESETS)
            for lang in t["scan"].get("languages") or []:
                rulesets += LANG_RULESETS.get(lang, [])
            jobs.append({
                "target": t["id"], "platform": t["platform"], "program_url": t["program_url"],
                "repo": scope_mod.normalize_repo(repo),
                "clone_url": f"https://{scope_mod.normalize_repo(repo)}.git",
                "paths": list(t["scan"].get("paths") or ["."]),
                "depth": int(t["scan"].get("depth", 1)),
                "rulesets": rulesets,
            })
    return jobs


def semgrep_cmd(semgrep: str, rulesets: list[str], paths: list[str], out_json: Path) -> list[str]:
    cmd = [semgrep, "scan", "--metrics=off", "--json", "--output", str(out_json), "--timeout", "120",
           "--max-target-bytes", "2000000", "--severity", "WARNING", "--severity", "ERROR"]
    for r in rulesets:
        cmd += ["--config", r]
    return cmd + paths


def run_job(job: dict[str, Any], work: Path, out: Path, semgrep: str, dry_run: bool) -> dict[str, Any]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = job["repo"].replace("/", "__")
    out_dir = out / job["target"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / f"{slug}-{stamp}.json"
    rec = {"target": job["target"], "repo": job["repo"], "clone_url": job["clone_url"], "stamp": stamp,
           "rulesets": job["rulesets"], "paths": job["paths"], "findings": None, "error": None, "file": str(out_json)}
    if dry_run:
        rec["dry_run"] = True
        return rec
    repo_dir = work / slug
    t0 = time.time()
    try:
        subprocess.run(["git", "clone", "--depth", str(job["depth"]), "--filter=blob:none", "--quiet",
                        job["clone_url"], str(repo_dir)], check=True, timeout=900)
        rec["commit"] = subprocess.run(["git", "-C", str(repo_dir), "rev-parse", "HEAD"], check=True,
                                       capture_output=True, text=True).stdout.strip()
        paths = [p for p in job["paths"] if (repo_dir / p).exists()] or ["."]
        cmd = semgrep_cmd(semgrep, job["rulesets"], paths, out_json)
        proc = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True, timeout=3600)
        if out_json.exists():
            data = json.loads(out_json.read_text())
            results = data.get("results", [])
            rec["findings"] = len(results)
            rec["by_severity"] = _count(results, lambda r: r.get("extra", {}).get("severity", "?"))
            rec["by_rule"] = dict(sorted(_count(results, lambda r: r.get("check_id", "?")).items(),
                                         key=lambda kv: -kv[1])[:30])
            # strip absolute paths / noise so the data branch stays small and comparable
            slim = [{"check_id": r.get("check_id"), "path": r.get("path"), "start": r.get("start", {}).get("line"),
                     "end": r.get("end", {}).get("line"), "severity": r.get("extra", {}).get("severity"),
                     "message": (r.get("extra", {}).get("message") or "")[:400],
                     "fingerprint": hashlib.sha1(f"{r.get('check_id')}|{r.get('path')}|{r.get('extra', {}).get('lines', '')}".encode()).hexdigest()[:16],
                     "metadata": {k: r.get("extra", {}).get("metadata", {}).get(k) for k in ("cwe", "owasp", "confidence", "likelihood", "impact")}}
                    for r in results]
            out_json.write_text(json.dumps({"meta": rec, "results": slim}, indent=0, sort_keys=True))
        else:
            rec["error"] = f"semgrep rc={proc.returncode}: {proc.stderr[-800:]}"
    except Exception as e:  # noqa: BLE001 - a scan job must never take the run down
        rec["error"] = f"{type(e).__name__}: {e}"[:800]
    finally:
        shutil.rmtree(repo_dir, ignore_errors=True)
    rec["seconds"] = round(time.time() - t0, 1)
    return rec


def _count(items, key) -> dict[str, int]:
    c: dict[str, int] = {}
    for it in items:
        k = str(key(it))
        c[k] = c.get(k, 0) + 1
    return c


def write_index(out: Path, records: list[dict[str, Any]]) -> Path:
    idx = out / "index.json"
    prev = json.loads(idx.read_text()) if idx.exists() else {"runs": []}
    prev["runs"].append({"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "jobs": records})
    prev["runs"] = prev["runs"][-60:]
    idx.write_text(json.dumps(prev, indent=1, sort_keys=True))
    return idx


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--targets", default=str(BOUNTY_DIR / "targets.yaml"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--semgrep", default="semgrep")
    ap.add_argument("--dry-run", action="store_true", help="plan + scope check only; no clone, no scan")
    ap.add_argument("--work", default="", help="scratch dir for clones (default: a temp dir)")
    a = ap.parse_args(argv)

    targets = load_targets(Path(a.targets))
    only = {s.strip() for s in a.only.split(",") if s.strip()} or None
    jobs = plan(targets, only)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(a.work) if a.work else Path(tempfile.mkdtemp(prefix="bounty-scan-"))
    work.mkdir(parents=True, exist_ok=True)
    print(f"{len(jobs)} job(s) from {len(targets)} target(s); out={out} dry_run={a.dry_run}")
    records = []
    for j in jobs:
        print(f"-> {j['target']}: {j['repo']} paths={j['paths']}")
        rec = run_job(j, work, out, a.semgrep, a.dry_run)
        print(f"   findings={rec.get('findings')} error={rec.get('error')}")
        records.append(rec)
    write_index(out, records)
    if not a.work:
        shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
