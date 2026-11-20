"""Name entry (asm/pro.asm + asm/name.asm): the Python model of name_commit, and no branch in pro.bin landing
inside the default-name blocks pro.asm rewrites."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import font_en  # noqa: E402

LKF = ROOT / "work" / "disc" / "tree" / "FD2BN.LKF"
PRO_BASE = 0x8009B4B0
# the words pro.asm rewrites inside a block (a branch target on a block's first word is fine)
BLOCKS = [(0x8009BF80, 14), (0x8009D7F4, 14)]


def fw(s):
    return s.encode("cp932")


def test_default_name_pairs():
    assert font_en.name_to_pairs(fw("Ｒａｖｉｅｌ")) == font_en.pair_code("R", "a") + font_en.pair_code(
        "v", "i") + font_en.pair_code("e", "l") + b"\0" * 6


def test_odd_and_mixed():
    out = font_en.name_to_pairs(fw("Ｒａｙ") + b"\0" * 6)
    assert out == font_en.pair_code("R", "a") + font_en.pair_code("y", " ") + b"\0" * 8
    out = font_en.name_to_pairs(fw("ＡラＢ１"))
    assert out == font_en.pair_code("A", " ") + fw("ラ") + font_en.pair_code("B", "1") + b"\0" * 6
    assert font_en.name_to_pairs(fw("ラビエル") + b"\0" * 4) == fw("ラビエル") + b"\0" * 4
    assert len(font_en.name_to_pairs(fw("ＡＢＣＤＥＦ"))) == 12


def test_no_branch_into_default_name_blocks():
    if not LKF.exists():
        pytest.skip("no unpacked disc")
    sys.path.insert(0, str(ROOT / "tools"))
    import lkf
    data = LKF.read_bytes()
    e = next(e for e in lkf.parse(data)["entries"] if e["name"] == "pro.bin")
    pro = data[e["off"]:e["off"] + e["size"]]
    inside = {a for lo, n in BLOCKS for a in range(lo + 4, lo + 4 * n, 4)}
    for off in range(0, len(pro) - 3, 4):
        w = struct.unpack_from("<I", pro, off)[0]
        pc = PRO_BASE + off
        op = w >> 26
        if op in (4, 5, 6, 7) or (op == 1 and ((w >> 16) & 0x1F) in (0, 1, 16, 17)):
            tgt = pc + 4 + (((w & 0xFFFF) ^ 0x8000) - 0x8000) * 4
        elif op in (2, 3):
            tgt = (pc & 0xF0000000) | ((w & 0x3FFFFFF) << 2)
        else:
            continue
        assert tgt not in inside, f"branch at {pc:#x} lands inside a rewritten block ({tgt:#x})"
