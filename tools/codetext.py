"""codetext.py: NUL-terminated SJIS strings in the EXE and the text overlays, with every site that references them.

    python -X utf8 tools/codetext.py dump FILE      # FILE: SLPS_027.54 or an FD2BN overlay (op.bin rfd2.bin ed.bin pro.bin)

Strings are found three ways (docs/re/text.md §EXE and overlay strings):
- the target of an aligned u32 pointer into the file ("ptr" ref, at the pointer's file offset);
- the target of a lui + addiu/ori pair ("lui" ref, at the lui and the low-half instruction);
- a Shift-JIS run (scantext.spans) with no reference, backed up to the previous NUL ("none": base+offset forms or
  records; check before moving such a string).
A string is: >= 1 double-byte SJIS character, only SJIS characters and printable ASCII, ended by a NUL."""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jtext  # noqa: E402
import scantext  # noqa: E402

EXE_BASE = 0x80020000 - 0x800  # vaddr of file offset 0 (PS-X EXE header is 0x800 bytes)
OVL_BASE = 0x8009B4B0
OVERLAYS = ("op.bin", "rfd2.bin", "ed.bin", "pro.bin")
# fixed-width string tables reached as base + index * stride (no pointer per string): file -> [(vaddr, stride, count, what)]
TABLES = {
    "pro.bin": [(0x800A03C4, 0x8C, 20, "prologue quiz question"), (0x800A0EB4, 0x30, 40, "prologue quiz answer")],
}
# hits that are code, not text (a pointer or lui pair that lands on bytes which decode as one kanji): file -> vaddrs
NOT_TEXT = {
    "SLPS_027.54": {0x80028378: "code", 0x80028380: "code", 0x80028388: "code", 0x80067970: "code", 0x8007E8E6: "code"},
    "op.bin": {0x800A003A: "code"},
    "rfd2.bin": {0x800D4D54: "code"},
    "ed.bin": {0x8009DEB0: "jal 92 b9 00 0c", 0x8009E014: "jal 92 b9 00 0c"},
    "pro.bin": {0x8009C764: "jal 92 b9 00 0c", 0x8009C944: "jal 92 b9 00 0c", 0x8009F5D4: "jal 92 b9 00 0c"},
}


def base_of(name):
    return EXE_BASE if name.upper().startswith("SLPS") else OVL_BASE


def string_at(data, o):
    """bytes of a plausible string starting at o (without the NUL), or None."""
    if not 0 <= o < len(data):
        return None
    end = data.find(b"\0", o)
    if end <= o:
        return None
    s = data[o:end]
    i, dbl = 0, 0
    while i < len(s):
        c = s[i]
        if c in jtext.LEAD and i + 1 < len(s):
            try:
                s[i:i + 2].decode("cp932")
            except UnicodeDecodeError:
                return None
            dbl += 1
            i += 2
        elif 0x20 <= c < 0x7F or c in (0x0A,):
            i += 1
        else:
            return None
    return s if dbl else None


def lui_pairs(data, code_end=None):
    """(lui offset, low offset, value) for lui rX + addiu/ori/load/store on rX within 16 instructions."""
    n = len(data) if code_end is None else code_end
    out = []
    for o in range(0, n - 4, 4):
        w = struct.unpack_from("<I", data, o)[0]
        if w >> 26 != 0x0F:
            continue
        rt, hi = (w >> 16) & 31, (w & 0xFFFF) << 16
        for k in range(1, 17):
            o2 = o + 4 * k
            if o2 + 4 > n:
                break
            w2 = struct.unpack_from("<I", data, o2)[0]
            op, rs, imm = w2 >> 26, (w2 >> 21) & 31, w2 & 0xFFFF
            if rs != rt:
                if op == 0x0F and ((w2 >> 16) & 31) == rt:
                    break  # rX reloaded
                continue
            if op in (0x09, 0x23, 0x21, 0x20, 0x24, 0x25, 0x2B, 0x29, 0x28):
                out.append((o, o2, (hi + (imm - 0x10000 if imm & 0x8000 else imm)) & 0xFFFFFFFF))
            elif op == 0x0D:
                out.append((o, o2, hi | imm))
    return out


def strings(name, data):
    """{file offset: {"bytes": b, "refs": [(kind, site offsets..)]}} sorted by offset."""
    base = base_of(name)
    lo, hi = base, base + len(data)
    found = {}

    def add(o, ref):
        s = string_at(data, o)
        if s is None:
            return False
        e = found.setdefault(o, {"bytes": s, "refs": []})
        if ref:
            e["refs"].append(ref)
        return True

    for p in range(0, len(data) - 3, 4):
        w = struct.unpack_from("<I", data, p)[0]
        if lo <= w < hi:
            add(w - base, ("ptr", p))
    for a, b, v in lui_pairs(data):
        if lo <= v < hi:
            add(v - base, ("lui", a, b))
    for va, stride, count, _ in TABLES.get(name, []):
        for k in range(count):
            assert add(va - base + k * stride, ("tab", va, stride, k)), f"{name}: table slot {va:#x}+{k}"
    # runs nothing points at
    for st, en, _ in scantext.spans(data):
        if any(o <= st < o + len(e["bytes"]) for o, e in found.items()):
            continue
        o = st
        while o > 0 and st - o < 64 and data[o - 1] != 0:
            o -= 1
        if not add(o, None):
            add(st, None)
    for va in NOT_TEXT.get(name, {}):
        assert found.pop(va - base, None) is not None, f"{name}: NOT_TEXT {va:#x} is no longer found"
    return dict(sorted(found.items()))


def replace_in_place(data, new):
    """new: {offset: bytes}; each must fit the original string plus its NUL padding (relocation: phase 7)."""
    out = bytearray(data)
    for o, s in new.items():
        old = string_at(data, o)
        assert old is not None, f"{o:#x}: no string"
        room = len(old)
        while o + room + 1 < len(data) and data[o + room + 1] == 0:
            room += 1
        assert len(s) <= room, f"{o:#x}: {len(s)} bytes, room {room}"
        out[o:o + room + 1] = s + b"\0" * (room + 1 - len(s))
    return bytes(out)


def main(argv):
    if len(argv) != 2 or argv[0] != "dump":
        sys.exit(__doc__)
    p = Path(argv[1])
    name = p.name.split("_", 1)[1] if p.name[:4].isdigit() else p.name
    base = base_of(name)
    for o, e in strings(name, p.read_bytes()).items():
        refs = ",".join(r[0] for r in e["refs"]) or "none"
        print(f"{base + o:08X}\t{refs}\t{jtext.decode(e['bytes'])}")


if __name__ == "__main__":
    main(sys.argv[1:])
