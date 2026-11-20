"""Phase 7 EXE/overlay string relocation (tools/codetext.py fit + Heap, insert.repoint_exe_refs): strings longer than
their slot move to the string heap and every reader is re-pointed; the real build's per-file write logs pass
romdiff (no byte changed without a logged write, every logged write found its expected original bytes)."""
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import codetext  # noqa: E402

B = codetext.OVL_BASE
JP = "あいう".encode("cp932")       # 6 bytes


def lui(rt, hi):
    return struct.pack("<I", (0x0F << 26) | (rt << 16) | hi)


def itype(op, rs, rt, imm):
    return struct.pack("<I", (op << 26) | (rs << 21) | (rt << 16) | (imm & 0xFFFF))


def hi_lo(va):
    return ((va + 0x8000) >> 16) & 0xFFFF, va & 0xFFFF


def image(code, strings):
    """overlay bytes: code at 0, NUL-terminated strings {offset: bytes}, 0xFF filler (no NUL padding: room = JP)"""
    d = bytearray(b"\xff" * 0x200)
    d[:len(code)] = code
    for o, s in strings.items():
        d[o:o + len(s) + 1] = s + b"\0"
    return bytes(d)


def decode_pair(d, a, b):
    hi = struct.unpack_from("<I", d, a)[0] & 0xFFFF
    lo = struct.unpack_from("<I", d, b)[0] & 0xFFFF
    return ((hi << 16) + (lo - 0x10000 if lo & 0x8000 else lo)) & 0xFFFFFFFF


def test_long_strings_move_and_every_ref_follows():
    h, l = hi_lo(B + 0x100)
    code = lui(4, h) + itype(9, 4, 4, l) + b"\0" * 8 + struct.pack("<I", B + 0x140)   # lui/addiu a0 + a pointer
    d = image(code, {0x100: JP, 0x140: JP})
    heap = codetext.Heap()
    out = codetext.fit("op.bin", d, {0x100: b"x" * 20, 0x140: b"y" * 3}, heap)
    va = heap.moved["op.bin"][B + 0x100]
    assert codetext.HEAP_LO <= va < codetext.HEAP_HI
    assert decode_pair(out, 0, 4) == va
    assert heap.buf[va - heap.lo:va - heap.lo + 21] == b"x" * 20 + b"\0"
    assert out[0x100:0x100 + 6] == JP                 # vacated slot keeps its Japanese
    assert B + 0x140 not in heap.moved["op.bin"]      # fits in place
    assert out[0x140:0x144] == b"yyy\0"
    assert struct.unpack_from("<I", out, 0x10)[0] == B + 0x140


def test_pointer_ref_moves():
    d = image(struct.pack("<I", B + 0x100), {0x100: JP})
    heap = codetext.Heap()
    out = codetext.fit("op.bin", d, {0x100: b"z" * 9}, heap)
    assert struct.unpack_from("<I", out, 0)[0] == heap.moved["op.bin"][B + 0x100]


def test_shared_lui_cannot_move():
    h, l1 = hi_lo(B + 0x100)
    _, l2 = hi_lo(B + 0x140)
    code = lui(4, h) + itype(9, 4, 5, l1) + itype(9, 4, 6, l2)       # one lui, two strings
    d = image(code, {0x100: JP, 0x140: JP})
    assert "shared" in codetext.movable("op.bin", d, 0x100)
    with pytest.raises(AssertionError, match="cannot move"):
        codetext.fit("op.bin", d, {0x100: b"x" * 20}, codetext.Heap())


def test_lui_pairs_stop_when_the_register_is_overwritten():
    h, _ = hi_lo(B + 0x100)
    # lui a0; lw a0, 0x3744(s0) (a0 reloaded); lw v1, 0x100(a0): not a pair (the イラ phantom in the EXE)
    code = lui(4, h) + itype(0x23, 16, 4, 0x3744) + itype(0x23, 4, 3, 0x100)
    assert codetext.lui_pairs(image(code, {})) == []


def test_fixed_literal_copy_limits_the_english():
    h, l = hi_lo(B + 0x100)
    # lui v0; addiu t3, v0, lo; lw t0, 0(t3); lb t1, 4(t3)  -> copies 5 bytes (char buf[] = "ab")
    code = lui(2, h) + itype(9, 2, 11, l) + itype(0x23, 11, 8, 0) + itype(0x20, 11, 9, 4)
    d = image(code, {0x100: "あい".encode("cp932")})
    assert codetext.copy_size("op.bin", d, 0x100) == 5
    assert codetext.limit("op.bin", d, 0x100) == 4
    with pytest.raises(AssertionError, match="copies 5"):
        codetext.fit("op.bin", d, {0x100: b"abcde"}, codetext.Heap())


def test_tail_string_with_other_english_moves_the_head():
    # "ペレイラ" with a second string at its tail; the head has a pointer, the tail a pointer too
    s = "ペレイラ".encode("cp932")
    d = image(struct.pack("<II", B + 0x100, B + 0x104), {0x100: s})
    heap = codetext.Heap()
    out = codetext.fit("op.bin", d, {0x100: b"Pereira", 0x104: b"Ira"}, heap)
    assert heap.moved["op.bin"] == {B + 0x100: heap.lo}
    assert out[0x104:0x108] == b"Ira\0"


TREE = ROOT / "work/disc/tree"
needs_tree = pytest.mark.skipif(not (TREE / "SLPS_027.54").is_file() or not (TREE / "FD2BN.LKF").is_file(),
                                reason="no unpacked disc in work/disc/tree")


@needs_tree
def test_real_build_writes_pass_romdiff_and_leave_no_reader(tmp_path):
    import extract
    import insert
    import lkf
    heap = codetext.Heap()
    lk, files, _ = insert.changes("en", heap=heap)
    origs = {e["name"]: b for e, b in lkf.files((TREE / "FD2BN.LKF").read_bytes())}
    origs[extract.EXE] = (TREE / extract.EXE).read_bytes()
    built = dict(lk.get("FD2BN", {}))
    built.update({k: v for k, v in files.items() if k == extract.EXE})
    romdiff = ROOT / "tools/romdiff.py"
    for name, log in heap.log.items():
        o, n, w = tmp_path / f"{name}.orig", tmp_path / f"{name}.new", tmp_path / f"{name}.txt"
        o.write_bytes(origs[name])
        n.write_bytes(built[name])
        w.write_text("".join(f"{a:X} {x.hex()} {y.hex()} {by}\n" for a, x, y, by in log), encoding="utf-8")
        r = subprocess.run([sys.executable, str(romdiff), str(o), str(n), "--writes", str(w)],
                           capture_output=True, text=True)
        assert r.returncode == 0, f"{name}: {r.stdout}{r.stderr}"
    # every reference to a vacated address is gone from the built file (EXE strings: from every code file)
    for name, moved in heap.moved.items():
        scan = codetext.CODE_FILES if name == extract.EXE else (name,)
        for f in scan:
            data = built.get(f, origs[f])
            for old in moved:
                assert not codetext.ref_sites(f, data, old), f"{f} still points at {name} {old:#x}"
    assert heap.lo + len(heap.buf) <= codetext.HEAP_HI
