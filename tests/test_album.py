"""G10 album profile atlas (tools/album.py): every row fits its rect, and the rebuilt TIM changes only pixels inside
the listed rects (height/weight rects untouched)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import album  # noqa: E402
import tim  # noqa: E402

pytestmark = pytest.mark.skipif(not album.SRC.is_file(), reason="work/lkf/GRPDATA not unpacked")


def test_all_fit():
    assert album.check()


def test_only_listed_rects_change():
    old = album.SRC.read_bytes()
    new = album.changes()["GRPDATA"][album.ENTRY]
    assert len(new) == len(old)
    a, b = tim.parse(old), tim.parse(new)
    assert a["cluts"] == b["cluts"]
    inside = set()
    for r in album.rows():
        inside |= {(r["v"] + y) * 256 + r["u"] + x for y in range(r["h"]) for x in range(r["w"])}
    diff = {i for i, (x, y) in enumerate(zip(a["pix"], b["pix"])) if x != y}
    assert diff and diff <= inside
    assert not any(216 <= i % 256 for i in diff)
