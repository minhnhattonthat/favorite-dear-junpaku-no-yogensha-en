"""G3 status tags and G4 skill banners (tools/banners.py): every row fits, and the rebuilt TIM only changes the
tag and banner area (rows 184-255, x < 236), same size and header."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import banners  # noqa: E402
import tim  # noqa: E402

pytestmark = pytest.mark.skipif(not banners.SRC.is_file(), reason="work/lkf/GRPDATA not unpacked")


def test_all_fit():
    assert banners.check()


def test_only_the_text_area_changes():
    old = banners.SRC.read_bytes()
    new = banners.changes()["GRPDATA"][banners.ENTRY]
    assert len(new) == len(old)
    a, b = tim.parse(old), tim.parse(new)
    assert a["cluts"] == b["cluts"] and (a["w"], a["h"]) == (b["w"], b["h"])
    diff = [i for i, (x, y) in enumerate(zip(a["pix"], b["pix"])) if x != y]
    assert diff
    assert all(i // 256 >= 184 and i % 256 < 236 for i in diff)


def test_tim_with_pixels_roundtrip():
    old = banners.SRC.read_bytes()
    assert tim.with_pixels(old, tim.parse(old)["pix"]) == old
