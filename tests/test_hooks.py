"""No branch or jump in the original EXE lands inside a word the font hooks (asm/font.asm) overwrite: such a
branch would start executing in the middle of the hook (skill §Checks: a code hook doesn't swallow a branch
target). A target on a hook's first word is fine: the hook replaces the code from there."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

EXE = ROOT / "work" / "disc" / "tree" / "SLPS_027.54"
# (first address, words overwritten) for every .org in asm/font.asm except FREE
HOOKS = [(0x8002C500, 4), (0x8002C548, 1), (0x8002C5EC, 2), (0x8002CCD8, 1), (0x8002CCEC, 1), (0x8002CDF0, 1),
         (0x8002CE00, 1), (0x8002BF50, 6), (0x8002C118, 5), (0x8002C358, 5), (0x8002C218, 2)]


def test_hook_list_matches_asm():
    lines = (ROOT / "asm" / "font.asm").read_text().splitlines()
    equ = {f[0]: f[2] for f in (line.split() for line in lines) if len(f) >= 3 and f[1] == "equ"}
    orgs = {int(equ.get(f[1], f[1]), 16) for f in (line.split() for line in lines if line.startswith(".org "))
            if f[1] != "FREE"}
    assert orgs == {a for a, _ in HOOKS}


@pytest.mark.skipif(not EXE.is_file(), reason="unpacked disc not present")
def test_no_branch_into_a_hook():
    d = EXE.read_bytes()
    t_addr, t_size = struct.unpack_from("<II", d, 0x18)
    text = d[0x800:0x800 + t_size]
    inside = {a + 4 * k for a, n in HOOKS for k in range(1, n)}
    bad = []
    for o in range(0, len(text) - 3, 4):
        w = struct.unpack_from("<I", text, o)[0]
        pc = t_addr + o
        op = w >> 26
        if op in (2, 3):                                   # j / jal
            tgt = (pc & 0xF0000000) | ((w & 0x3FFFFFF) << 2)
        elif op in (1, 4, 5, 6, 7, 0x14, 0x15, 0x16, 0x17):  # regimm, beq, bne, blez, bgtz (+ likely)
            imm = w & 0xFFFF
            tgt = pc + 4 + ((imm - 0x10000 if imm & 0x8000 else imm) << 2)
        else:
            continue
        if tgt in inside and not any(a <= pc < a + 4 * n for a, n in HOOKS):
            bad.append(f"{pc:#x} -> {tgt:#x}")
    assert not bad, bad
