"""Tracker: ticket parsing and stage rules (no network)."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("tracker", Path(__file__).parents[1] / "scripts" / "tracker.py")
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)


def _issue(*labels):
    return {"labels": [{"name": n} for n in labels]}


def test_stage_lists_are_the_agreed_ones():
    assert tr.STAGES["project"] == ["Research", "Design", "Build", "Test", "Integration", "QA", "Launch", "Live Test"]
    assert tr.STAGES["error"] == ["Reproduce", "Cause & Effect", "Fix", "QA", "Deploy", "Live Test"]
    assert tr.PRIORITY["error"] == "P0"


def test_label_parsing():
    i = _issue("type:error", "P0", "stage:Cause & Effect", "bot:ef-autobuyer", "fp:wf-ef-autobuyer")
    assert tr.ticket_type(i) == "error" and tr.ticket_stage(i) == "Cause & Effect"
    assert tr.ticket_bot(i) == "ef-autobuyer" and tr.ticket_fp(i) == "wf-ef-autobuyer"
    assert tr.ticket_type(_issue("bug")) is None


def test_slug():
    assert tr.slug("wf:ef-autobuyer / Watch rounds!") == "wf-ef-autobuyer-watch-rounds"
