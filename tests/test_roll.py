"""ENDING.STR staff roll (tools/roll.py, gfx/roll.tsv): every Japanese line has English (or is already Latin), the
lines are in scroll order and do not overlap, every English line fits the 320 px frame (english_strip asserts it),
and the strip offset is exactly 1.5 px/frame until the roll stops."""
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import roll  # noqa: E402

JP = re.compile(r"[぀-ヿ㐀-鿿＀-￯]")


def test_table():
    rows = roll.rows()
    assert len(rows) == 143
    for a, b in zip(rows, rows[1:]):
        assert a["y1"] < b["y0"], (a["jp"], b["jp"])
    for r in rows:
        assert r["style"] in roll.STYLES or r["style"] == "keep", r
        assert r["y0"] < r["y1"] and 0 <= r["x0"] < r["x1"] < roll.W, r
        if r["style"] == "keep":
            assert not r["en"] and not JP.search(r["jp"]), r
        else:
            assert r["en"] and not JP.search(r["en"]), r
            assert ("|" in r["en"]) == (r["style"] == "name2"), r


def test_strip_fits():
    col, a = roll.english_strip(roll.rows())   # asserts every line fits the frame
    assert a.shape[1] == 2 * roll.W and a.max() > 0.9 and np.isfinite(col).all()


def test_offset():
    assert roll.offset(roll.N0) == 0
    assert roll.offset(roll.N0 + 2) == 3
    assert roll.offset(roll.LAST) == roll.offset(roll.STOP)
