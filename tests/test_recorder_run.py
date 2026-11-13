"""mrp/gha_record.sh end to end against a local git remote, a stub recorder and a stub GitHub API.

What it pins down (each one was a hole in the recorded data until 13 Nov 2026):
- the recorder starts before the branch is set up;
- the branch is checked out sparse: old runs and other jobs' folders are never materialised, and never deleted;
- the run asks for its successor before the closing publish, once, and not at all if one is already waiting or the run
  was short;
- the closing publish carries the recorder's last lines, also while another job is pushing to the same branch.
"""
from __future__ import annotations

import gzip
import json
import os
import shutil
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "mrp" / "gha_record.sh"

RECORDER = r'''
import datetime as dt, os, signal, time
d = os.environ["MRP_DATA_DIR"]
stop = []
signal.signal(signal.SIGTERM, lambda *a: stop.append(1))
signal.signal(signal.SIGINT, lambda *a: stop.append(1))
def put(line):
    now = dt.datetime.now(dt.timezone.utc)
    p = os.path.join(d, now.strftime("%Y-%m-%d"))
    os.makedirs(p, exist_ok=True)
    with open(os.path.join(p, now.strftime("%H") + ".jsonl"), "a") as f:
        f.write(line + "\n")
n = 0
while not stop:
    put('{"n": %d}' % n)
    n += 1
    time.sleep(0.2)
put('{"bye": true}')
'''

ANALYZER = r'''
import glob, os, sys
data = sys.argv[1]
runs = sorted({p.split(os.sep)[-3] for p in glob.glob(os.path.join(data, "*", "*", "*.jsonl.gz"))})
print("runs seen: " + " ".join(runs))
open(sys.argv[sys.argv.index("--csv") + 1], "w").write("slug\n")
'''


def git(*args, cwd=None, check=True):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=check)


class Api:
    """The two GitHub calls the handoff makes: list this workflow's runs, dispatch the next one."""

    def __init__(self, runs):
        api = self
        self.calls = []

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                api.calls.append(("GET", self.path, time.time(), self.headers.get("Authorization"), None))
                body = json.dumps({"workflow_runs": runs}).encode()
                self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers()
                self.wfile.write(body)

            def do_POST(self):
                raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                api.calls.append(("POST", self.path, time.time(), self.headers.get("Authorization"), raw.decode()))
                self.send_response(204); self.end_headers()

        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.url = f"http://127.0.0.1:{self.srv.server_address[1]}"
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def close(self):
        self.srv.shutdown()


def make_world(base: Path):
    """A bare 'GitHub' with main and a small mrp-data branch, plus a checkout the way actions/checkout leaves one."""
    origin, seed, ws, kit = base / "origin.git", base / "seed", base / "ws", base / "kit"
    git("init", "-q", "--bare", "-b", "main", str(origin))
    git("config", "uploadpack.allowFilter", "true", cwd=origin)
    git("config", "uploadpack.allowAnySHA1InWant", "true", cwd=origin)
    git("init", "-q", "-b", "main", str(seed))
    git("config", "user.name", "t", cwd=seed); git("config", "user.email", "t@example.invalid", cwd=seed)
    (seed / "mrp").mkdir(); (seed / "mrp" / "README.md").write_text("kit\n")
    git("add", "-A", cwd=seed); git("commit", "-qm", "main", cwd=seed)
    git("push", "-q", str(origin), "main", cwd=seed)
    git("checkout", "-q", "--orphan", "mrp-data", cwd=seed); git("rm", "-rqf", ".", cwd=seed)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    files = {
        f"mrp/data/run-PREV/{today}/09.jsonl.gz": gzip.compress(b'{"prev": 1}\n'),
        "mrp/data/run-OLD/2020-01-01/00.jsonl.gz": gzip.compress(b'{"old": 1}\n'),
        "mrp/radar/big.bin": b"x" * 4096,
        "mrp/REPORT.md": b"old report\n",
        "mrp/windows.csv": b"slug\n",
        "mre/state.json": b"{}\n",
        "site-preview/sitemap.xml": b"<urlset/>\n",
    }
    for rel, data in files.items():
        p = seed / rel
        p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
    git("add", "-A", cwd=seed); git("commit", "-qm", "data", cwd=seed)
    git("push", "-q", str(origin), "mrp-data", cwd=seed)

    git("init", "-q", "-b", "main", str(ws))
    git("remote", "add", "origin", origin.as_uri(), cwd=ws)
    git("fetch", "-q", "--depth", "1", "origin", "+refs/heads/main:refs/remotes/origin/main", cwd=ws)
    git("checkout", "-q", "-B", "main", "refs/remotes/origin/main", cwd=ws)
    kit.mkdir()
    (kit / "mrp_recorder.py").write_text(RECORDER)
    (kit / "mrp_analyze.py").write_text(ANALYZER)
    return origin, ws, kit, sorted(files)


def other_writer(origin: Path, base: Path, stop: threading.Event, pushed: list):
    """Another job publishing to the same branch all the while (site-deploy and the benchmark do)."""
    w = base / "writer"
    git("init", "-q", str(w)); git("remote", "add", "origin", origin.as_uri(), cwd=w)
    git("config", "user.name", "w", cwd=w); git("config", "user.email", "w@example.invalid", cwd=w)
    i = 0
    while not stop.is_set():
        i += 1
        if git("fetch", "-q", "origin", "mrp-data", cwd=w, check=False).returncode == 0:
            git("reset", "-q", "--hard", "FETCH_HEAD", cwd=w)
            (w / "site-preview").mkdir(exist_ok=True); (w / "site-preview" / f"tick-{i}.txt").write_text(str(i))
            git("add", "-A", cwd=w); git("commit", "-qm", f"site-preview {i}", cwd=w)
            if git("push", "-q", "origin", "HEAD:mrp-data", cwd=w, check=False).returncode == 0:
                pushed.append(f"site-preview/tick-{i}.txt")
        stop.wait(1.0)


def run_recorder(base: Path, *, runs, env_extra=None, race=False):
    base.mkdir(parents=True)
    origin, ws, kit, seeded = make_world(base)
    api = Api(runs)
    home = base / "home"; home.mkdir()
    env = dict(os.environ, HOME=str(home), GITHUB_WORKSPACE=str(ws), KIT=str(kit), GITHUB_ACTIONS="true",
               GITHUB_API_URL=api.url, GITHUB_REPOSITORY="o/r", GITHUB_RUN_ID="777", GH_TOKEN="tok",
               MRP_RUN_SECONDS="34", MRP_PUBLISH_SECONDS="6", MRP_LAST_FULL_SECONDS="8", MRP_POLL_SECONDS="1",
               MRP_CHAIN_MIN_SECONDS="20", MRP_CHAIN_RETRY_SECONDS="1")
    env.pop("MRP_DATA_DIR", None); env.pop("GIT_DIR", None)
    env.update(env_extra or {})
    stop, pushed = threading.Event(), []
    t = threading.Thread(target=other_writer, args=(origin, base, stop, pushed), daemon=True) if race else None
    if t:
        t.start()
    try:
        r = subprocess.run(["bash", str(SCRIPT)], cwd=ws, env=env, capture_output=True, text=True, timeout=240)
    finally:
        stop.set()
        if t:
            t.join(timeout=30)
        api.close()
    tree = git("ls-tree", "-r", "--name-only", "mrp-data", cwd=origin).stdout.split()
    return dict(rc=r.returncode, out=r.stdout + r.stderr, calls=api.calls, origin=origin, wt=base / "datawt", tree=tree,
                seeded=seeded, pushed=pushed)


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    if not shutil.which("git") or not shutil.which("bash") or not shutil.which("curl"):
        pytest.skip("needs git, bash and curl")
    base = tmp_path_factory.mktemp("recorder")
    me = {"id": 777, "status": "in_progress"}
    jobs = {
        "chain": dict(runs=[me, {"id": 5, "status": "completed"}], race=True),
        "waiting": dict(runs=[me, {"id": 999, "status": "pending"}]),
        "short": dict(runs=[me], env_extra={"MRP_CHAIN_MIN_SECONDS": "100000"}),
    }
    with ThreadPoolExecutor(len(jobs)) as ex:
        futs = {k: ex.submit(run_recorder, base / k, **kw) for k, kw in jobs.items()}
        return {k: f.result() for k, f in futs.items()}


def published(res, needle):
    return [p for p in res["tree"] if needle in p]


def test_recorder_starts_before_the_branch_is_set_up(runs):
    out = runs["chain"]["out"]
    assert runs["chain"]["rc"] == 0, out
    assert "[run] run-" in out and "[setup] branch ready" in out, out
    assert out.index("[run] run-") < out.index("[setup] branch ready")


def test_checkout_is_sparse_and_nothing_outside_it_is_lost(runs):
    res = runs["chain"]
    wt = res["wt"]
    assert (wt / "mrp" / "data" / "run-PREV").is_dir()          # the days the report reads are there
    assert not (wt / "mrp" / "data" / "run-OLD").exists()       # an old run is not downloaded
    assert not (wt / "mrp" / "radar").exists() and not (wt / "mre").exists() and not (wt / "site-preview").exists()
    for rel in res["seeded"]:                                   # and none of it was deleted from the branch
        assert rel in res["tree"], rel
    report = git("show", "mrp-data:mrp/REPORT.md", cwd=res["origin"]).stdout
    assert "run-PREV" in report and "-777" in report and "run-OLD" not in report, report


def test_closing_publish_carries_the_last_lines_while_another_job_pushes(runs):
    res = runs["chain"]
    mine = published(res, "-777/")
    assert mine and all(p.endswith(".jsonl.gz") for p in mine), res["out"]
    text = "".join(gzip.decompress(subprocess.run(["git", "show", f"mrp-data:{p}"], cwd=res["origin"], capture_output=True,
                                                  check=True).stdout).decode() for p in mine)
    assert '{"bye": true}' in text, res["out"]                  # written as the recorder stopped: only the closing publish has it
    assert "[publish] fast:" in res["out"] and "[publish] full:" in res["out"], res["out"]
    assert res["pushed"], "the competing writer never got a push in: the race was not exercised"
    for rel in res["pushed"]:                                   # neither side overwrote the other
        assert rel in res["tree"], rel


def test_successor_is_requested_once_and_before_the_closing_publish(runs):
    res = runs["chain"]
    gets = [c for c in res["calls"] if c[0] == "GET"]
    posts = [c for c in res["calls"] if c[0] == "POST"]
    assert len(gets) == 1 and gets[0][1].startswith("/repos/o/r/actions/workflows/mrp-record.yml/runs"), res["calls"]
    assert len(posts) == 1 and posts[0][1] == "/repos/o/r/actions/workflows/mrp-record.yml/dispatches", res["calls"]
    assert json.loads(posts[0][4]) == {"ref": "main"} and posts[0][3] == "Bearer tok"
    last = int(git("log", "-1", "--format=%ct", "--grep=^mrp-record ", "mrp-data", cwd=res["origin"]).stdout)
    assert int(posts[0][2]) <= last, "the closing publish landed before the successor was requested"
    assert "[handoff] next run requested" in res["out"]


def test_no_second_successor_when_one_is_already_waiting(runs):
    res = runs["waiting"]
    assert res["rc"] == 0, res["out"]
    assert [c[0] for c in res["calls"]] == ["GET"], res["calls"]
    assert "already waiting" in res["out"]
    assert published(res, "-777/")                              # the data is published all the same


def test_a_short_run_starts_no_successor(runs):
    res = runs["short"]
    assert res["rc"] == 0, res["out"]
    assert res["calls"] == [], res["calls"]
    assert "starts no successor" in res["out"]
    assert published(res, "-777/")


def test_script_body_runs_inside_a_function():
    """The self-update replaces mrp/ under the running script; bash reads a script as it goes, a function it has already read."""
    src = SCRIPT.read_text()
    assert "\nmain() {" in src and src.rstrip().endswith('main "$@"\nexit $?')
