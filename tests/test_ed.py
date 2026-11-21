"""asm/ed.asm: the only change to ed.bin is ceed3.end's line count (34 -> 38), and every English .end fits the line
count its ending draws (tools/lint.py end_line_errors; docs/re/text.md §.end files)."""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import lint  # noqa: E402

CEED3 = 0x8009E42C - 0x8009B4B0 + 6 * 32 + 7 * 4


def test_ed_patch_is_one_word():
    ed = build.lkf_entry("FD2BN", "ed.bin")
    out = build.patch_ed(ed)
    assert struct.unpack_from("<I", ed, CEED3)[0] == 34
    assert struct.unpack_from("<I", out, CEED3)[0] == 38
    diff = [i for i in range(len(ed)) if ed[i] != out[i]]
    assert diff == [CEED3]


def test_end_counts_match_patch():
    c = lint.end_counts()
    assert len(c) == 21 and c["ceed3.end"] == 38 and c["feed3.end"] == 35


def test_english_end_files_fit():
    assert lint.end_line_errors() == []
