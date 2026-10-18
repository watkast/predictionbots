"""Make `ventures/saas/*` products importable when running `pytest ventures/saas`."""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for p in (_HERE, _HERE / "oddsmath"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
