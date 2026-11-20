"""G8 battle name plates (tools/plates.py): every plate has English that fits 64 px, and encodes to 384 bytes."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import plates  # noqa: E402


def test_all_fit():
    assert plates.check()


@pytest.mark.skipif(not plates.SRC.is_dir(), reason="work/lkf/GRPDATA not unpacked")
def test_changes_are_plates():
    ch = plates.changes()["GRPDATA"]
    assert len(ch) == 88
    assert all(len(b) == 384 for b in ch.values())
    assert all(any(b) for b in ch.values())
