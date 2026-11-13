"""The CI smoke log is public three times over (the Actions log, the smoke-live-log artifact, logs/ on the data branch),
so it may say that the signed balance call answered and with which fields, and never an amount."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _smoke():
    spec = importlib.util.spec_from_file_location("smoke_live", ROOT / "scripts" / "smoke_live.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_balance_note_names_fields_and_no_amounts():
    answer = {"balance": 1234567, "balance_dollars": "12345.6700", "portfolio_value": 7654321, "updated_ts": 1794284860,
              "balance_breakdown": [{"balance": "98.7600", "exchange_index": 2}]}
    note = _smoke().balance_note(answer)
    assert "balance_dollars" in note and "portfolio_value" in note
    for amount in ("1234567", "12345.67", "7654321", "98.76", "1794284860"):
        assert amount not in note


def test_balance_note_survives_an_odd_answer():
    assert "fields: )" in _smoke().balance_note({})
    assert "7" not in _smoke().balance_note({"balance": 7})


def test_smoke_script_never_formats_the_balance_answer_into_a_message():
    src = (ROOT / "scripts" / "smoke_live.py").read_text()
    assert "{bal}" not in src
    assert "balance_note(bal)" in src
