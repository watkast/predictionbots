"""scripts/archive_release.py against a local git remote and a directory standing in for GitHub releases.

The property under test: a file leaves a branch only when a copy of it, proven byte for byte, sits in a release.
"""
from __future__ import annotations

import gzip
import importlib.util
import io
import json
import shutil
import subprocess
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


AR = load("archive_release")
WM = load("windows_merge")


def git(*args, cwd, check=True):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=check).stdout


def gz(text: str) -> bytes:
    return gzip.compress(text.encode(), mtime=0)


BOOKS = {
    "mrp/data/run-A/2026-11-01/10.jsonl.gz": gz("a-10\n" * 400),
    "mrp/data/run-A/2026-11-01/11.jsonl.gz": gz("a-11\n" * 400),
    "mrp/data/run-A/2026-11-02/00.jsonl.gz": gz("a-00\n" * 400),
    "mrp/data/run-B/2026-11-02/01.jsonl.gz": gz("b-01\n" * 400),
    "mrp/data/run-B/2026-11-06/23.jsonl.gz": gz("b-23\n" * 400),
    "mrp/data/run-C/2026-11-07/00.jsonl.gz": gz("c-00\n" * 400),
    "mrp/data/run-C/2026-11-12/05.jsonl.gz": gz("c-05\n" * 400),
}
MRP = {
    **BOOKS,
    "mrp/radar/run-X/2026-10-29/15.jsonl.gz": gz("radar\n" * 3000),
    "mrp/radar/run-X/2026-10-29/16.jsonl.gz": gz("radar2\n" * 3000),
    "mrp/radar/paper_state.json": b'{"open": []}\n',
    "mrp/research/nfl/cache/a.json": json.dumps({"k": list(range(2000))}).encode(),
    "mrp/REPORT.md": b"report\n",
    "benchmark/benchmark.json": b"{}\n",
    "mre/state.json": b"{}\n",
}
DATA = {
    "ledger/log-a.txt": ("line of a paper bot log\n" * 20000).encode(),
    "ledger/log-b.txt": ("another line\n" * 20000).encode(),
    "ledger/fills.jsonl": b'{"fill": 1}\n' * 500,
    "recorded/kalshi/a.jsonl.gz": gz("kalshi\n" * 100),
    "health/status.json": b"{}\n",
}


@pytest.fixture()
def world(tmp_path, monkeypatch):
    if not shutil.which("git") or not shutil.which("tar"):
        pytest.skip("needs git and tar")
    origin, seed = tmp_path / "origin.git", tmp_path / "seed"
    git("init", "-q", "--bare", "-b", "main", str(origin), cwd=tmp_path)
    git("config", "uploadpack.allowFilter", "true", cwd=origin)
    git("config", "uploadpack.allowAnySHA1InWant", "true", cwd=origin)
    git("init", "-q", "-b", "main", str(seed), cwd=tmp_path)
    git("config", "user.name", "t", cwd=seed); git("config", "user.email", "t@example.invalid", cwd=seed)
    (seed / "README.md").write_text("main\n")
    git("add", "-A", cwd=seed); git("commit", "-qm", "main", cwd=seed); git("push", "-q", str(origin), "main", cwd=seed)
    for branch, files in (("mrp-data", MRP), ("data", DATA)):
        git("checkout", "-q", "--orphan", branch, cwd=seed); git("rm", "-rqf", ".", cwd=seed)
        for rel, blob in files.items():
            p = seed / rel
            p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(blob)
        git("add", "-A", cwd=seed); git("commit", "-qm", f"{branch} 1", cwd=seed)
        (seed / "touch.txt").write_text("a second commit, so there is history to drop\n")
        git("add", "-A", cwd=seed); git("commit", "-qm", f"{branch} 2", cwd=seed)
        git("push", "-q", str(origin), branch, cwd=seed)
    home = tmp_path / "home"; home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("ARCHIVE_REMOTE", origin.as_uri())
    monkeypatch.setenv("ARCHIVE_RELEASES_DIR", str(tmp_path / "releases"))
    monkeypatch.delenv("GIT_DIR", raising=False)
    return dict(origin=origin, seed=seed, rel=tmp_path / "releases", work=tmp_path / "work", tmp=tmp_path)


def tree(w, branch):
    out = git("ls-tree", "-r", "--full-tree", branch, cwd=w["origin"])
    return {line.split("\t", 1)[1]: line.split()[2] for line in out.splitlines()}


def commits(w, branch):
    return int(git("rev-list", "--count", branch, cwd=w["origin"]).strip())


def asset_files(path: Path) -> dict[str, bytes]:
    with tarfile.open(path) as tf:
        return {m.name: tf.extractfile(m).read() for m in tf if m.isfile()}


def test_pack_copies_and_proves_but_removes_nothing(world):
    before = tree(world, "mrp-data")
    r = AR.pack("mrp-data", "sports-radar", "retired-2026-11", ["mrp/radar"], "t", "n", world["work"])
    assert r["files"] == 3
    asset = world["rel"] / "retired-2026-11" / "sports-radar.tar"            # compressed data is tarred, not compressed again
    assert asset_files(asset) == {p: b for p, b in MRP.items() if p.startswith("mrp/radar/")}
    after = tree(world, "mrp-data")
    assert {p: v for p, v in after.items() if not p.startswith("archive/")} == before     # every file is still in git
    m = AR.parse_manifest(git("show", "mrp-data:archive/sports-radar.tsv", cwd=world["origin"]))
    assert set(m["rows"]) == {p for p in MRP if p.startswith("mrp/radar/")}
    assert all(m["rows"][p][0] == before[p] for p in m["rows"])              # the manifest names git's own blob ids
    assert "downloaded back" in m["head"]["verified"] and m["head"]["release"] == "retired-2026-11"
    assert "sports-radar" in git("show", "mrp-data:archive/README.md", cwd=world["origin"])


def test_prune_plan_changes_nothing_and_apply_removes_exactly_the_proven_files(world):
    AR.pack("mrp-data", "sports-radar", "retired-2026-11", ["mrp/radar"], "t", "n", world["work"])
    old_tip = git("rev-parse", "mrp-data", cwd=world["origin"]).strip()
    before = tree(world, "mrp-data")
    plan = AR.prune("mrp-data", world["work"], apply=False)
    assert plan["removed"] == 3 and git("rev-parse", "mrp-data", cwd=world["origin"]).strip() == old_tip

    done = AR.prune("mrp-data", world["work"], apply=True, backup="backup/mrp-data")
    assert done["applied"] and done["removed"] == 3
    after = tree(world, "mrp-data")
    assert after == {p: v for p, v in before.items() if not p.startswith("mrp/radar/")}       # nothing else moved or changed
    assert commits(world, "mrp-data") == 1                                                     # history is gone with them
    assert git("rev-parse", "backup/mrp-data", cwd=world["origin"]).strip() == old_tip         # and the old tip is kept aside


def test_rebuilding_a_branch_downloads_none_of_its_data(world):
    AR.pack("mrp-data", "sports-radar", "retired-2026-11", ["mrp/radar"], "t", "n", world["work"])
    kept_blob = tree(world, "mrp-data")["mrp/data/run-C/2026-11-12/05.jsonl.gz"]
    AR.prune("mrp-data", world["work"], apply=True)
    r = subprocess.run(["git", "cat-file", "-e", kept_blob], cwd=world["work"] / "prune", capture_output=True,
                       env={"GIT_NO_LAZY_FETCH": "1", "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(world["tmp"] / "home")})
    present = subprocess.run(["git", "rev-list", "--objects", "--missing=print", "--all"], cwd=world["work"] / "prune", capture_output=True, text=True).stdout
    assert f"?{kept_blob}" in present or r.returncode != 0          # the 5 GB of kept data never has to come down to rebuild


def test_text_is_gzipped_and_a_big_archive_is_split_and_joins_back(world, monkeypatch):
    monkeypatch.setattr(AR, "PART_BYTES", 400)
    AR.pack("data", "paper-matrix-logs", "retired-2026-11", ["ledger"], "t", "n", world["work"])
    parts = sorted((world["rel"] / "retired-2026-11").glob("paper-matrix-logs.tar.gz.part*"))
    assert len(parts) > 1
    m = AR.parse_manifest(git("show", "data:archive/paper-matrix-logs.tsv", cwd=world["origin"]))
    assert [a["name"] for a in m["assets"]] == [p.name for p in parts] and m["head"]["restore"].startswith("cat ")
    joined = io.BytesIO(b"".join(p.read_bytes() for p in parts))
    with tarfile.open(fileobj=joined, mode="r:gz") as tf:
        got = {x.name: tf.extractfile(x).read() for x in tf if x.isfile()}
    assert got == {p: b for p, b in DATA.items() if p.startswith("ledger/")}
    AR.prune("data", world["work"], apply=True)
    assert sorted(tree(world, "data")) == ["archive/README.md", "archive/paper-matrix-logs.tsv", "health/status.json",
                                           "recorded/kalshi/a.jsonl.gz", "touch.txt"]


class Corrupting(AR.DirReleases):
    def upload(self, tag, files):
        super().upload(tag, files)
        f = self.root / tag / files[0].name
        raw = bytearray(f.read_bytes()); raw[len(raw) // 2] ^= 0xFF; f.write_bytes(bytes(raw))


def test_a_damaged_upload_writes_no_manifest_so_nothing_can_leave(world, monkeypatch):
    monkeypatch.setattr(AR, "releases", lambda: Corrupting(str(world["rel"])))
    before = tree(world, "mrp-data")
    with pytest.raises(AR.Stop):
        AR.pack("mrp-data", "sports-radar", "retired-2026-11", ["mrp/radar"], "t", "n", world["work"])
    assert tree(world, "mrp-data") == before
    assert AR.prune("mrp-data", world["work"], apply=True)["removed"] == 0
    assert tree(world, "mrp-data") == before


def test_prune_keeps_a_file_that_changed_and_a_file_no_manifest_covers(world):
    AR.pack("mrp-data", "sports-radar", "retired-2026-11", ["mrp/radar"], "t", "n", world["work"])
    seed = world["seed"]
    git("fetch", "-q", str(world["origin"]), "mrp-data", cwd=seed); git("checkout", "-q", "-B", "mrp-data", "FETCH_HEAD", cwd=seed)
    (seed / "mrp/radar/paper_state.json").write_text('{"open": [1]}\n')                 # changed after the archive
    (seed / "mrp/radar/run-X/2026-10-29/17.jsonl.gz").write_bytes(gz("late\n" * 10))    # arrived after the archive
    git("add", "-A", cwd=seed); git("commit", "-qm", "late radar", cwd=seed); git("push", "-q", str(world["origin"]), "mrp-data", cwd=seed)
    assert AR.prune("mrp-data", world["work"], apply=True)["removed"] == 2
    left = sorted(p for p in tree(world, "mrp-data") if p.startswith("mrp/radar/"))
    assert left == ["mrp/radar/paper_state.json", "mrp/radar/run-X/2026-10-29/17.jsonl.gz"]


def test_prune_checks_the_release_again_before_it_removes(world):
    AR.pack("mrp-data", "sports-radar", "retired-2026-11", ["mrp/radar"], "t", "n", world["work"])
    (world["rel"] / "retired-2026-11" / "sports-radar.tar").unlink()                    # someone deleted the asset
    before = tree(world, "mrp-data")
    assert AR.prune("mrp-data", world["work"], apply=True)["removed"] == 0
    assert tree(world, "mrp-data") == before


def test_a_commit_that_lands_while_pruning_is_kept(world):
    AR.pack("mrp-data", "sports-radar", "retired-2026-11", ["mrp/radar"], "t", "n", world["work"])
    seed, calls = world["seed"], []

    def another_job_pushes():
        if calls:
            return
        calls.append(1)
        git("fetch", "-q", str(world["origin"]), "mrp-data", cwd=seed); git("checkout", "-q", "-B", "mrp-data", "FETCH_HEAD", cwd=seed)
        (seed / "site-preview").mkdir(exist_ok=True); (seed / "site-preview/sitemap.xml").write_text("<urlset/>\n")
        git("add", "-A", cwd=seed); git("commit", "-qm", "site-preview", cwd=seed); git("push", "-q", str(world["origin"]), "mrp-data", cwd=seed)

    AR.prune("mrp-data", world["work"], apply=True, before_push=another_job_pushes)
    after = tree(world, "mrp-data")
    assert "site-preview/sitemap.xml" in after and not any(p.startswith("mrp/radar/") for p in after)
    assert commits(world, "mrp-data") == 1


def test_books_moves_finished_days_older_than_the_window_one_asset_a_day(world):
    done = AR.books(7, world["work"], today="2026-11-13")
    assert done == ["2026-11-01", "2026-11-02", "2026-11-06"]                            # 7 Nov to 13 Nov stay
    rel = world["rel"] / "books-2026-11"
    assert sorted(p.name for p in rel.iterdir() if not p.name.startswith(".")) == ["books-2026-11-01.tar", "books-2026-11-02.tar", "books-2026-11-06.tar"]
    assert asset_files(rel / "books-2026-11-02.tar") == {p: b for p, b in BOOKS.items() if "/2026-11-02/" in p}    # a day spans runs
    assert AR.books(7, world["work"], today="2026-11-13") == []                          # a second run has nothing to do
    AR.prune("mrp-data", world["work"], apply=True)
    left = sorted(p for p in tree(world, "mrp-data") if p.startswith("mrp/data/"))
    assert left == ["mrp/data/run-C/2026-11-07/00.jsonl.gz", "mrp/data/run-C/2026-11-12/05.jsonl.gz"]
    assert "mrp/REPORT.md" in tree(world, "mrp-data") and "mrp/radar/paper_state.json" in tree(world, "mrp-data")


def test_books_refuses_a_window_shorter_than_the_report_reads(world, capsys):
    assert AR.main(["--work", str(world["work"]), "books", "--keep-days", "3"]) == 1
    assert "keep at least 5" in capsys.readouterr().out


def test_tokens_never_reach_an_error_message():
    assert "secret" not in AR.redact("fatal: unable to access 'https://x-access-token:secret@github.com/o/r.git/'")


# ---------- windows_merge

def W(slug, settle=1.0, prints=3, book=5):
    return {"slug": slug, "settle": settle, "prints": {str(i): 1.0 for i in range(prints)}, "book_secs": book}


def test_merge_keeps_windows_whose_raw_books_have_left_git():
    out = WM.merge({"windows": [W("a"), W("b")]}, {"windows": [W("b"), W("c")], "n_records": 9})
    assert [w["slug"] for w in out["windows"]] == ["a", "b", "c"] and out["n_records"] == 9
    assert out["merged"] == {"published": 2, "fresh": 2, "total": 3, "fuller_published_kept": 0}


def test_merge_prefers_the_fuller_record_and_the_fresh_one_on_a_tie():
    old_full, new_thin = W("a", prints=900, book=600), W("a", prints=40, book=10)       # half the window's day already left git
    assert WM.merge({"windows": [old_full]}, {"windows": [new_thin]})["windows"][0] is old_full
    unsettled, settled = W("b", settle=None, prints=900), W("b", settle=2.0, prints=10)
    assert WM.merge({"windows": [unsettled]}, {"windows": [settled]})["windows"][0] is settled
    same_old, same_new = W("c"), W("c")
    assert WM.merge({"windows": [same_old]}, {"windows": [same_new]})["windows"][0] is same_new


def test_merge_command_reads_gz_and_survives_a_missing_published_file(tmp_path, capsys):
    pub, fresh, out = tmp_path / "pub.json.gz", tmp_path / "fresh.json", tmp_path / "out.json"
    pub.write_bytes(gzip.compress(json.dumps({"windows": [W("a")]}).encode()))
    fresh.write_text(json.dumps({"windows": [W("b")], "venue": "kalshi"}))
    assert WM.main(["x", str(pub), str(fresh), str(out)]) == 0
    got = json.loads(out.read_text())
    assert [w["slug"] for w in got["windows"]] == ["a", "b"] and got["venue"] == "kalshi"
    assert WM.main(["x", str(tmp_path / "none.json.gz"), str(fresh), str(out)]) == 0
    assert "no published windows" in capsys.readouterr().out
    assert [w["slug"] for w in json.loads(out.read_text())["windows"]] == ["b"]


# ---------- prune: a push the server refuses for another reason stops with that reason

def test_a_refused_push_stops_with_the_servers_reason_and_moves_nothing(world, capsys):
    AR.pack("mrp-data", "sports-radar", "retired-2026-11", ["mrp/radar"], "t", "n", world["work"])
    hook = world["origin"] / "hooks" / "pre-receive"
    hook.write_text("#!/bin/sh\necho 'refusing: repository rule' >&2\nexit 1\n"); hook.chmod(0o755)
    before = tree(world, "mrp-data")
    with pytest.raises(AR.Stop) as e:
        AR.prune("mrp-data", world["work"], apply=True)
    assert "refusing: repository rule" in str(e.value)
    assert capsys.readouterr().out.count("planning again") == 0          # not mistaken for a branch that moved
    assert tree(world, "mrp-data") == before


# ---------- push_data.sh: a job that pushes after the branch was rebuilt

def test_a_late_job_never_puts_archived_files_back(tmp_path):
    if not shutil.which("git") or not shutil.which("bash"):
        pytest.skip("needs git and bash")
    env = {**__import__("os").environ, "HOME": str(tmp_path)}
    sh = lambda *a, cwd: subprocess.run(list(a), cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout
    origin, seed, job = tmp_path / "o.git", tmp_path / "seed", tmp_path / "job"
    sh("git", "init", "-q", "--bare", "-b", "data", str(origin), cwd=tmp_path)
    sh("git", "init", "-q", "-b", "data", str(seed), cwd=tmp_path)
    for d in (seed,):
        sh("git", "config", "user.name", "t", cwd=d); sh("git", "config", "user.email", "t@example.invalid", cwd=d)
    (seed / "big").mkdir(); (seed / "big" / "old.txt").write_text("archived\n"); (seed / "keep.txt").write_text("k\n")
    sh("git", "add", "-A", cwd=seed); sh("git", "commit", "-qm", "a", cwd=seed)
    (seed / "keep.txt").write_text("k2\n"); sh("git", "commit", "-qam", "b", cwd=seed)
    sh("git", "push", "-q", str(origin), "data", cwd=seed)
    # a job checks out the branch and commits its log
    sh("git", "clone", "-q", "-b", "data", str(origin), str(job), cwd=tmp_path)
    sh("git", "config", "user.name", "j", cwd=job); sh("git", "config", "user.email", "j@example.invalid", cwd=job)
    base = sh("git", "rev-parse", "HEAD", cwd=job).strip()
    (job / "logs").mkdir(); (job / "logs" / "run.txt").write_text("log\n")
    sh("git", "add", "-A", cwd=job); sh("git", "commit", "-qm", "job log", cwd=job)
    # meanwhile the branch is rebuilt without big/ and without its history
    sh("git", "rm", "-rq", "big", cwd=seed); sh("git", "commit", "-qm", "drop big", cwd=seed)
    t = sh("git", "rev-parse", "HEAD^{tree}", cwd=seed).strip()
    root = sh("git", "commit-tree", t, "-m", "rebuilt", cwd=seed).strip()
    sh("git", "push", "-q", "--force", str(origin), f"{root}:refs/heads/data", cwd=seed)

    contrast = tmp_path / "contrast"
    shutil.copytree(job, contrast)
    sh("git", "fetch", "-q", "origin", "data", cwd=contrast)
    subprocess.run(["git", "rebase", "origin/data"], cwd=contrast, capture_output=True, env=env)
    assert (contrast / "big" / "old.txt").exists()          # the old way: the archived file is back

    subprocess.run(["bash", str(ROOT / "scripts" / "push_data.sh"), "data", base, "3"], cwd=job, check=True, capture_output=True, env=env)
    files = sh("git", "ls-tree", "-r", "--name-only", "data", cwd=origin).split()
    assert sorted(files) == ["keep.txt", "logs/run.txt"]
    assert sh("git", "rev-list", "--count", "data", cwd=origin).strip() == "2"
    assert sh("git", "log", "--format=%s", "data", cwd=origin).split("\n")[:2] == ["job log", "rebuilt"]
