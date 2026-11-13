#!/usr/bin/env python3
"""Move folders of a data branch into GitHub release assets, and let them leave git only once that is proven.

Git is the wrong home for the recorder's books and for old experiment logs: the repository passed 10 GB on
13 Nov 2026 and the books alone add about 8 GB a month. A release asset is as public as the branch was, costs
nothing and has no total size limit (2 GiB a file).

  pack BRANCH NAME TAG PATH...    Tar PATH... from BRANCH's tip, upload it under release TAG, then download it
                                  back and compare every file in it with what git holds. Only after that write
                                  archive/NAME.tsv to BRANCH: one row per file (git blob id, sha256, size, path).
  books [--keep-days 7]           `pack` each finished recorder day older than that: one asset a day
                                  (books-DAY.tar under release books-YYYY-MM).
  prune BRANCH [--apply]          Rebuild BRANCH as one commit without every file that a manifest on it covers
                                  with the same blob id, after checking that the assets are still there with the
                                  recorded size and sha256. What no manifest covers stays. Without --apply it
                                  prints the plan and changes nothing. The branch's history goes: replaying recent
                                  commits was tried (13 Nov 2026) and cannot be pushed from a clone without file
                                  contents, because the old commits reference earlier versions of files that only
                                  the server holds. Nothing may read commit dates on these branches for that
                                  reason; scripts/health_check.py reads each job's own timestamp instead.

What makes `prune` safe: a file leaves git only if (path, blob id) is in a manifest; a manifest is written only
after the upload was downloaded back and every file in it compared; and the assets are checked again before the
branch is rebuilt. `prune` moves the branch with --force-with-lease, so a commit that lands meanwhile is never
lost: the plan is rebuilt on top of it.

Restore a file: download the asset named in archive/NAME.tsv, `tar -xf` it; paths inside are the paths in git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

PART_BYTES = 1900 * 1024 * 1024            # release assets must stay under 2 GiB
COMPRESSED = (".gz", ".zst", ".xz", ".bz2", ".parquet", ".zip", ".png", ".jpg")
BOOKS_BRANCH, BOOKS_ROOT = "mrp-data", "mrp/data"
DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class Stop(Exception):
    """Something did not add up; nothing after this point has been done."""


def redact(text: str) -> str:
    return re.sub(r"x-access-token:[^@\s]+@", "x-access-token:***@", text)


def run(*args, cwd=None, check=True, data=None, env=None) -> subprocess.CompletedProcess:
    r = subprocess.run([str(a) for a in args], cwd=cwd, input=data, capture_output=True, env=env)
    if check and r.returncode != 0:
        raise Stop(redact(f"{' '.join(str(a) for a in args[:4])}... failed ({r.returncode}): {r.stderr.decode('utf-8', 'replace')[-600:]}"))
    return r


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def remote_url() -> str:
    if os.environ.get("ARCHIVE_REMOTE"):
        return os.environ["ARCHIVE_REMOTE"]
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GH_TOKEN")
    if not repo or not token:
        raise Stop("set GITHUB_REPOSITORY and GH_TOKEN (or ARCHIVE_REMOTE)")
    return f"https://x-access-token:{token}@github.com/{repo}.git"


# ---------- git: a blobless, shallow clone; trees are always there, blobs only where a checkout asks for them

class Repo:
    def __init__(self, path: Path):
        self.dir = Path(path)
        if self.dir.exists():
            shutil.rmtree(self.dir)
        self.dir.mkdir(parents=True)
        self.git("init", "-q")
        self.git("remote", "add", "origin", remote_url())
        self.git("config", "user.name", os.environ.get("ARCHIVE_GIT_NAME", "predictionbots-archive"))
        self.git("config", "user.email", os.environ.get("ARCHIVE_GIT_EMAIL", "bots@users.noreply.github.com"))

    def git(self, *args, check=True, data=None, env=None) -> str | None:
        """stdout of a git command; with check=False, None when it failed."""
        e = dict(os.environ, **(env or {}))
        r = run("git", *args, cwd=self.dir, check=check, data=data, env=e)
        if r.returncode != 0:
            return None
        return r.stdout.decode("utf-8", "replace")

    def fetch(self, branch: str) -> str:
        """The branch tip, blobless and one commit deep: trees only, none of the files."""
        self.git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", f"+refs/heads/{branch}:refs/remotes/origin/{branch}")
        return self.git("rev-parse", f"refs/remotes/origin/{branch}").strip()

    def ls(self, treeish: str, paths: list[str] | None = None) -> dict[str, tuple[str, str]]:
        """path -> (mode, blob id) for every file under paths (the whole tree without them). Needs trees only."""
        out = self.git("ls-tree", "-r", "-z", "--full-tree", treeish, "--", *(paths or []))
        res = {}
        for rec in out.split("\0"):
            if not rec:
                continue
            meta, path = rec.split("\t", 1)
            mode, kind, sha = meta.split()
            if kind != "blob" or mode not in ("100644", "100755"):
                raise Stop(f"{path}: a {kind} with mode {mode}; this tool moves plain files only")
            res[path] = (mode, sha)
        return res

    def show(self, treeish: str, path: str) -> bytes:
        return run("git", "show", f"{treeish}:{path}", cwd=self.dir).stdout

    def checkout(self, commit: str, dirs: list[str]) -> None:
        patterns = "".join(f"/{d.strip('/')}/\n" for d in dirs)
        self.git("sparse-checkout", "set", "--no-cone", "--stdin", data=patterns.encode())
        self.git("checkout", "-q", commit)


# ---------- releases: GitHub through `gh`, or a plain directory (tests, dry runs)

class GhReleases:
    def __init__(self):
        self.repo = os.environ.get("GITHUB_REPOSITORY") or ""
        if not self.repo:
            raise Stop("GITHUB_REPOSITORY is not set")

    def _gh(self, *args, check=True):
        return run("gh", *args, check=check)

    def ensure(self, tag: str, title: str, notes: str) -> None:
        if self._gh("release", "view", tag, "-R", self.repo, check=False).returncode == 0:
            return
        self._gh("release", "create", tag, "-R", self.repo, "--title", title, "--notes", notes, "--latest=false",
                 "--target", os.environ.get("ARCHIVE_TARGET", "main"))

    def upload(self, tag: str, files: list[Path]) -> None:
        for f in files:                       # one at a time: a failed upload names its file
            for attempt in (1, 2, 3):
                if self._gh("release", "upload", tag, str(f), "-R", self.repo, "--clobber", check=False).returncode == 0:
                    break
                time.sleep(10 * attempt)
            else:
                raise Stop(f"upload of {f.name} to release {tag} failed three times")

    def assets(self, tag: str) -> dict[str, dict]:
        r = self._gh("api", f"repos/{self.repo}/releases/tags/{tag}", check=False)
        if r.returncode != 0:
            return {}
        rid = json.loads(r.stdout)["id"]
        out, page = {}, 1
        while True:
            chunk = json.loads(self._gh("api", f"repos/{self.repo}/releases/{rid}/assets?per_page=100&page={page}").stdout)
            for a in chunk:
                digest = (a.get("digest") or "")
                out[a["name"]] = {"size": a["size"], "sha256": digest.split(":", 1)[1] if digest.startswith("sha256:") else None,
                                  "state": a.get("state")}
            if len(chunk) < 100:
                return out
            page += 1

    def download(self, tag: str, name: str, dest: Path) -> Path:
        dest.mkdir(parents=True, exist_ok=True)
        self._gh("release", "download", tag, "-R", self.repo, "-p", name, "-D", str(dest), "--clobber")
        return dest / name


class DirReleases:
    """Release assets as files under ROOT/TAG/. Same contract as GhReleases."""

    def __init__(self, root: str):
        self.root = Path(root)

    def ensure(self, tag, title, notes):
        (self.root / tag).mkdir(parents=True, exist_ok=True)
        (self.root / tag / ".notes").write_text(f"{title}\n\n{notes}\n")

    def upload(self, tag, files):
        for f in files:
            shutil.copyfile(f, self.root / tag / f.name)

    def assets(self, tag):
        d = self.root / tag
        if not d.is_dir():
            return {}
        return {p.name: {"size": p.stat().st_size, "sha256": sha256_file(p), "state": "uploaded"}
                for p in d.iterdir() if p.is_file() and not p.name.startswith(".")}

    def download(self, tag, name, dest):
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(self.root / tag / name, dest / name)
        return dest / name


def releases():
    return DirReleases(os.environ["ARCHIVE_RELEASES_DIR"]) if os.environ.get("ARCHIVE_RELEASES_DIR") else GhReleases()


# ---------- hashing and tar

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_git_file(path: Path) -> tuple[int, str, str]:
    """(size, git blob id, sha256) of a file, in one pass."""
    size = path.stat().st_size
    blob, sha = hashlib.sha1(b"blob %d\0" % size), hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            blob.update(chunk)
            sha.update(chunk)
    return size, blob.hexdigest(), sha.hexdigest()


def tar_members(archive: Path) -> dict[str, tuple[str, int]]:
    """path -> (sha256, size) for every file in the archive, read as a stream (nothing is unpacked to disk)."""
    out = {}
    with tarfile.open(archive, "r|gz" if archive.name.endswith(".gz") else "r|") as tf:
        for m in tf:
            if not m.isfile():
                raise Stop(f"{archive.name}: {m.name} is not a plain file")
            h, fh = hashlib.sha256(), tf.extractfile(m)
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
            if m.name in out:
                raise Stop(f"{archive.name}: {m.name} is in the archive twice")
            out[m.name] = (h.hexdigest(), m.size)
    return out


def make_tar(src: Path, paths: list[str], archive: Path) -> None:
    listing = archive.with_name(archive.name + ".list")
    listing.write_bytes(b"".join(p.encode() + b"\0" for p in paths))
    base = ["tar", "--sort=name", "--owner=0", "--group=0", "--numeric-owner", "--mtime=2026-01-01 00:00:00Z", "--no-recursion",
            "-C", str(src), "--null", "-T", str(listing)]
    if archive.name.endswith(".gz"):
        cmd = " ".join(f"'{a}'" for a in base) + f" -cf - | gzip -n -6 > '{archive}'"
        run("bash", "-c", "set -euo pipefail; " + cmd)
    else:
        run(*base, "-cf", str(archive))
    listing.unlink()


def split_parts(archive: Path) -> list[Path]:
    if archive.stat().st_size <= PART_BYTES:
        return [archive]
    run("split", "-b", str(PART_BYTES), "-d", "-a", "2", str(archive), str(archive) + ".part")
    archive.unlink()
    return sorted(archive.parent.glob(archive.name + ".part*"))


# ---------- manifests

def manifest_text(head: dict, assets: list[dict], rows: list[tuple[str, str, int, str]]) -> str:
    lines = [f"# {k}: {v}" for k, v in head.items()]
    lines += [f"# asset: {a['name']}\tsize={a['size']}\tsha256={a['sha256']}" for a in assets]
    lines.append("# columns: git blob id, sha256, bytes, path")
    lines += [f"{blob}\t{sha}\t{size}\t{path}" for blob, sha, size, path in rows]
    return "\n".join(lines) + "\n"


def parse_manifest(text: str) -> dict:
    head, assets, rows = {}, [], {}
    for line in text.splitlines():
        if line.startswith("# asset: "):
            name, size, sha = line[len("# asset: "):].split("\t")
            assets.append({"name": name, "size": int(size.split("=")[1]), "sha256": sha.split("=")[1]})
        elif line.startswith("# "):
            k, _, v = line[2:].partition(": ")
            head[k] = v
        elif line.strip():
            blob, sha, size, path = line.split("\t", 3)
            rows[path] = (blob, sha, int(size))
    return {"head": head, "assets": assets, "rows": rows}


def index_md(manifests: dict[str, dict]) -> str:
    out = ["# Data that moved out of this branch", "",
           "Each row is one archive: files that used to live on a branch of this repository and now live in a release asset.",
           "The `.tsv` next to this file lists every file in it with its git blob id and sha256. To get a file back,",
           "download the asset from the release and `tar -xf` it; the paths inside are the paths the files had here.", "",
           "| Archive | From | Release | Files | Bytes | Moved |", "| --- | --- | --- | --- | --- | --- |"]
    for name in sorted(manifests):
        h = manifests[name]["head"]
        out.append(f"| [{name}]({name}.tsv) | `{h.get('branch', '?')}` | `{h.get('release', '?')}` | {h.get('files', '?')} | {h.get('bytes', '?')} | {h.get('verified', '?')[:10]} |")
    return "\n".join(out) + "\n"


def publish_manifest(branch: str, name: str, text: str, work: Path) -> None:
    """Commit archive/NAME.tsv and the index to BRANCH (an ordinary commit on top of whatever is there)."""
    for attempt in range(1, 7):
        repo = Repo(work / "pub")
        tip = repo.fetch(branch)
        repo.checkout(tip, ["archive"])
        d = repo.dir / "archive"
        d.mkdir(exist_ok=True)
        (d / f"{name}.tsv").write_text(text)
        manifests = {p.stem: parse_manifest(p.read_text()) for p in d.glob("*.tsv")}
        (d / "README.md").write_text(index_md(manifests))
        repo.git("add", "-A", "--", "archive")
        if repo.git("status", "--porcelain", "--", "archive").strip() == "":
            return
        repo.git("commit", "-qm", f"archive: {name} moved to release assets (manifest)")
        if run("git", "push", "-q", "origin", f"HEAD:refs/heads/{branch}", cwd=repo.dir, check=False).returncode == 0:
            return
        time.sleep(min(30, 3 * attempt))
    raise Stop(f"could not push the manifest for {name} to {branch}")


# ---------- pack

def pack(branch: str, name: str, tag: str, paths: list[str], title: str, notes: str, work: Path) -> dict | None:
    rel = releases()
    work.mkdir(parents=True, exist_ok=True)
    repo = Repo(work / "src")
    tip = repo.fetch(branch)
    entries = repo.ls(tip, paths)
    if not entries:
        print(f"[pack] {name}: nothing under {paths} on {branch}")
        return None
    for p in entries:
        if "\n" in p or "\t" in p:
            raise Stop(f"a path with a tab or a newline cannot go in a manifest: {p!r}")
    repo.checkout(tip, paths)
    rows = []
    for path in sorted(entries):
        size, blob, sha = hash_git_file(repo.dir / path)
        if blob != entries[path][1]:
            raise Stop(f"{path}: the checked-out file hashes to {blob}, git says {entries[path][1]}")
        rows.append((blob, sha, size, path))
    total = sum(r[2] for r in rows)
    loose = sum(r[2] for r in rows if not r[3].endswith(COMPRESSED))
    out = work / "out"
    out.mkdir(exist_ok=True)
    archive = out / (name + (".tar.gz" if loose * 10 > total else ".tar"))     # already-compressed data is only tarred
    make_tar(repo.dir, [r[3] for r in rows], archive)
    shutil.rmtree(repo.dir)                                                    # the runner's disk is small
    whole = (sha256_file(archive), archive.stat().st_size)
    parts = split_parts(archive)
    assets = [{"name": p.name, "size": p.stat().st_size, "sha256": sha256_file(p)} for p in parts]
    print(f"[pack] {name}: {len(rows)} files, {total:,} bytes -> {', '.join(a['name'] for a in assets)} ({sum(a['size'] for a in assets):,} bytes)")

    rel.ensure(tag, title, notes)
    rel.upload(tag, parts)
    for p in parts:
        p.unlink()

    # prove it: what GitHub lists, then every byte back and every file compared
    listed = rel.assets(tag)
    back = work / "back"
    if back.exists():
        shutil.rmtree(back)
    for a in assets:
        got = listed.get(a["name"])
        if not got or got["size"] != a["size"] or (got["sha256"] and got["sha256"] != a["sha256"]):
            raise Stop(f"release {tag} lists {a['name']} as {got}; uploaded {a['size']} bytes sha256 {a['sha256']}")
        f = rel.download(tag, a["name"], back)
        if sha256_file(f) != a["sha256"]:
            raise Stop(f"{a['name']} came back from release {tag} with a different sha256")
    joined = back / archive.name
    if len(assets) > 1:
        with open(joined, "wb") as dst:
            for a in assets:
                with open(back / a["name"], "rb") as src:
                    shutil.copyfileobj(src, dst, 1 << 20)
                (back / a["name"]).unlink()
    if (sha256_file(joined), joined.stat().st_size) != whole:
        raise Stop(f"{archive.name}: the parts do not join back into the archive that was made")
    inside = tar_members(joined)
    want = {path: (sha, size) for _blob, sha, size, path in rows}
    if inside != want:
        missing, extra = sorted(set(want) - set(inside))[:3], sorted(set(inside) - set(want))[:3]
        differ = [p for p in want if p in inside and inside[p] != want[p]][:3]
        raise Stop(f"{archive.name} downloaded from {tag} does not match git: missing {missing}, extra {extra}, different {differ}")
    shutil.rmtree(back)

    head = {"archive": name, "branch": branch, "commit": tip, "release": tag, "files": len(rows), "bytes": total,
            "format": "tar.gz" if archive.name.endswith(".gz") else "tar",
            "restore": ("cat " + " ".join(a["name"] for a in assets) + f" > {archive.name}; " if len(assets) > 1 else "") + f"tar -xf {archive.name}",
            "verified": f"{now_iso()} downloaded back from the release; all {len(rows)} files matched git by sha256"}
    publish_manifest(branch, name, manifest_text(head, assets, rows), work)
    print(f"[pack] {name}: verified ({len(rows)} files matched after download) and archive/{name}.tsv is on {branch}")
    return {"name": name, "files": len(rows), "bytes": total, "assets": assets}


# ---------- books: one asset per finished recorder day

def books(keep_days: int, work: Path, today: str | None = None, limit: int | None = None) -> list[str]:
    scan = Repo(work / "scan")
    tip = scan.fetch(BOOKS_BRANCH)
    by_day: dict[str, dict[str, str]] = {}
    for path, (_mode, blob) in scan.ls(tip, [BOOKS_ROOT]).items():
        parts = path.split("/")                 # mrp/data/<run>/<day>/<file>
        if len(parts) >= 5 and DAY_RE.match(parts[3]):
            by_day.setdefault(parts[3], {})[path] = blob
    covered = set()
    for name in (scan.git("ls-tree", "--name-only", tip, "archive/", check=False) or "").split():
        if name.endswith(".tsv") and Path(name).name.startswith("books-"):
            covered |= {(p, r[0]) for p, r in parse_manifest(scan.show(tip, name).decode()).get("rows", {}).items()}
    d0 = datetime.strptime(today, "%Y-%m-%d").date() if today else datetime.now(timezone.utc).date()
    last = (d0 - timedelta(days=keep_days)).isoformat()        # the newest day that leaves; keep_days days stay, today included
    done = []
    for day in sorted(d for d in by_day if d <= last):
        files = by_day[day]
        if all((p, b) in covered for p, b in files.items()):
            continue
        if limit is not None and len(done) >= limit:
            break
        dirs = sorted({"/".join(p.split("/")[:4]) for p in files})
        month = day[:7]
        r = pack(BOOKS_BRANCH, f"books-{day}", f"books-{month}", dirs,
                 title=f"Recorded books, {month}",
                 notes=(f"Order books, index prints and settlements recorded by the Mr. P recorder in {month} (UTC), one tar per day: "
                        f"`books-DAY.tar` holds `mrp/data/<run>/DAY/*.jsonl.gz` exactly as the files were on the `mrp-data` branch. "
                        f"`archive/books-DAY.tsv` on that branch lists every file with its git blob id and sha256. "
                        f"Unpack with `tar -xf books-DAY.tar`."),
                 work=work / f"day-{day}")
        if r:
            done.append(day)
        shutil.rmtree(work / f"day-{day}", ignore_errors=True)
    print(f"[books] days on the branch: {len(by_day)}; kept in git: after {last}; archived now: {done or 'none'}")
    return done


# ---------- prune: rebuild the branch without what the manifests cover

def plan_prune(repo: Repo, branch: str, rel) -> dict:
    tip = repo.fetch(branch)
    cur = repo.ls(tip)
    names = [n for n in (repo.git("ls-tree", "--name-only", tip, "archive/", check=False) or "").split() if n.endswith(".tsv")]
    removable, report, by_tag = {}, [], {}
    for n in sorted(names):
        m = parse_manifest(repo.show(tip, n).decode())
        tag = m["head"].get("release", "")
        if m["head"].get("branch") != branch or "verified" not in m["head"]:
            report.append((Path(n).stem, "skipped: not a verified manifest for this branch", 0, 0))
            continue
        if tag not in by_tag:
            by_tag[tag] = rel.assets(tag)
        listed = by_tag[tag]
        bad = [a["name"] for a in m["assets"]
               if a["name"] not in listed or listed[a["name"]]["size"] != a["size"]
               or (listed[a["name"]]["sha256"] and listed[a["name"]]["sha256"] != a["sha256"])]
        if bad or not m["assets"]:
            report.append((Path(n).stem, f"skipped: release {tag} no longer has {bad or 'any asset'} as recorded", 0, 0))
            continue
        here = {p: r for p, r in m["rows"].items() if p in cur and cur[p][1] == r[0]}
        changed = sum(1 for p, r in m["rows"].items() if p in cur and cur[p][1] != r[0])
        removable.update(here)
        report.append((Path(n).stem, f"{len(here)} files leave git" + (f"; {changed} changed since and stay" if changed else ""),
                       len(here), sum(r[2] for r in here.values())))
    return {"tip": tip, "cur": cur, "removable": removable, "report": report}


def build_commit(repo: Repo, plan: dict, branch: str, squash: bool) -> str:
    """The new tip: the old tree minus the archived files, as one root commit (squash) or as an ordinary commit on
    top of the old tip. Needs trees only."""
    idx = dict(GIT_INDEX_FILE=str(repo.dir / ".git" / "prune.index"), GIT_NO_LAZY_FETCH="1")
    repo.git("read-tree", plan["tip"], env=idx)
    repo.git("update-index", "--force-remove", "-z", "--stdin", data=b"".join(p.encode() + b"\0" for p in sorted(plan["removable"])), env=idx)
    tree = repo.git("write-tree", "--missing-ok", env=idx).strip()
    want = {p: v for p, v in plan["cur"].items() if p not in plan["removable"]}
    if repo.ls(tree) != want:
        raise Stop("the rebuilt tree is not exactly the old tree minus the archived files; nothing was pushed")
    n, size = len(plan["removable"]), sum(r[2] for r in plan["removable"].values())
    msg = (f"{branch}: {len(want)} files; {n} files ({size:,} bytes) now live in release assets\n\n"
           f"Rebuilt from {plan['tip']} without the files listed in archive/*.tsv. Each of them was downloaded back from\n"
           f"its release and compared with git before it left. See archive/README.md.\n")
    parents = [] if squash else ["-p", plan["tip"]]
    return repo.git("commit-tree", tree, *parents, "-m", msg, env=dict(GIT_NO_LAZY_FETCH="1")).strip()


def prune(branch: str, work: Path, apply: bool = False, squash: bool = True, backup: str | None = None, before_push=None) -> dict:
    rel = releases()
    for attempt in range(1, 6):
        repo = Repo(work / "prune")
        plan = plan_prune(repo, branch, rel)
        for name, what, _n, _b in plan["report"]:
            print(f"[prune] {branch}: {name}: {what}")
        n, size = len(plan["removable"]), sum(r[2] for r in plan["removable"].values())
        print(f"[prune] {branch}: {len(plan['cur'])} files at {plan['tip'][:9]}; {n} files, {size:,} bytes would leave; {len(plan['cur']) - n} stay")
        if not n:
            return {"removed": 0, "tip": plan["tip"]}
        commit = build_commit(repo, plan, branch, squash)
        if not apply:
            print(f"[prune] {branch}: plan only (run with --apply to move the branch to {commit[:9]})")
            return {"removed": n, "bytes": size, "tip": plan["tip"], "commit": commit, "applied": False}
        if backup:
            r = run("git", "push", "-q", "origin", f"{plan['tip']}:refs/heads/{backup}", cwd=repo.dir, check=False)
            if r.returncode != 0:
                have = (repo.git("ls-remote", "origin", f"refs/heads/{backup}") or "").split()
                if not have:
                    raise Stop(redact(f"could not create the backup branch {backup}: {r.stderr.decode()[-300:]}"))
                print(f"[prune] {branch}: backup branch {backup} already exists at {have[0][:9]}; left as it is")
            else:
                print(f"[prune] {branch}: old tip kept as {backup}")
        if before_push:
            before_push()
        r = run("git", "push", "-q", f"--force-with-lease=refs/heads/{branch}:{plan['tip']}", "origin", f"{commit}:refs/heads/{branch}",
                cwd=repo.dir, check=False, env=dict(os.environ, GIT_NO_LAZY_FETCH="1"))
        if r.returncode == 0:
            print(f"[prune] {branch}: now {commit[:9]}: {len(plan['cur']) - n} files" + (", one commit" if squash else ""))
            return {"removed": n, "bytes": size, "tip": plan["tip"], "commit": commit, "applied": True}
        err = redact(r.stderr.decode("utf-8", "replace"))
        if not re.search(r"stale info|fetch first|non-fast-forward|cannot lock ref", err):
            raise Stop(f"the push of the rebuilt {branch} failed and the branch was not moved: {err.strip()[-500:]}")
        print(f"[prune] {branch}: the branch moved while the plan was built (try {attempt}); planning again on the new tip")
        time.sleep(2 * attempt)
    raise Stop(f"{branch} kept moving; it was not rebuilt")


# ---------- command line

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--work", default=os.environ.get("ARCHIVE_WORK"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pack")
    p.add_argument("branch"); p.add_argument("name"); p.add_argument("tag"); p.add_argument("paths", nargs="+")
    p.add_argument("--title", default=None); p.add_argument("--notes", default=None)
    b = sub.add_parser("books")
    b.add_argument("--keep-days", type=int, default=7); b.add_argument("--limit", type=int, default=None)
    q = sub.add_parser("prune")
    q.add_argument("branch"); q.add_argument("--apply", action="store_true"); q.add_argument("--keep-history", action="store_true")
    q.add_argument("--backup", default=None, help="keep the old tip as this branch before moving the branch")
    a = ap.parse_args(argv)
    work = Path(a.work) if a.work else Path(tempfile.mkdtemp(prefix="archive-"))
    try:
        if a.cmd == "pack":
            pack(a.branch, a.name, a.tag, [x.strip("/") for x in a.paths], a.title or f"Archive: {a.name}",
                 a.notes or f"Files moved out of the `{a.branch}` branch. `archive/{a.name}.tsv` on that branch lists every file with its git blob id and sha256.", work)
        elif a.cmd == "books":
            if a.keep_days < 5:
                raise Stop("the recorder's report reads the last four days from git: keep at least 5")
            books(a.keep_days, work, limit=a.limit)
        else:
            prune(a.branch, work, apply=a.apply, squash=not a.keep_history, backup=a.backup)
    except Stop as e:
        print(f"STOPPED: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
