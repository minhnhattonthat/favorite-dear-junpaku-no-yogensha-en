"""codetext.py: NUL-terminated SJIS strings in the EXE and the text overlays, with every site that references them.

    python -X utf8 tools/codetext.py dump FILE      # FILE: SLPS_027.54 or an FD2BN overlay (op.bin rfd2.bin ed.bin pro.bin)

Strings are found three ways (docs/re/text.md §EXE and overlay strings):
- the target of an aligned u32 pointer into the file ("ptr" ref, at the pointer's file offset);
- the target of a lui + addiu/ori pair ("lui" ref, at the lui and the low-half instruction);
- a Shift-JIS run (scantext.spans) with no reference, backed up to the previous NUL ("none": base+offset forms or
  records; check before moving such a string).
A string is: >= 1 double-byte SJIS character, only SJIS characters and printable ASCII, ended by a NUL.
fit(): English that does not fit its slot moves to the string heap (HEAP_LO..HEAP_HI, prepended to the EXE)."""
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
            if rs == rt:
                if op in (0x09, 0x23, 0x21, 0x20, 0x24, 0x25, 0x2B, 0x29, 0x28):
                    out.append((o, o2, (hi + (imm - 0x10000 if imm & 0x8000 else imm)) & 0xFFFFFFFF))
                elif op == 0x0D:
                    out.append((o, o2, hi | imm))
            if writes_reg(w2) == rt:
                break  # rX now holds something else (the full address, a load, a reload)
    return out


def writes_reg(w):
    """GPR an R3000 instruction writes (None for stores, branches, mult/div, jr)."""
    op = w >> 26
    if op == 0:
        funct = w & 0x3F
        if funct in (0x08, 0x0C, 0x0D, 0x11, 0x13, 0x18, 0x19, 0x1A, 0x1B):
            return None
        return (w >> 11) & 31
    if op == 3 or (op == 1 and (w >> 16) & 0x10):
        return 31                                   # jal, bltzal/bgezal
    if 0x08 <= op <= 0x0F or 0x20 <= op <= 0x26:
        return (w >> 16) & 31
    if op in (0x10, 0x12) and (w >> 21) & 31 in (0, 2):
        return (w >> 16) & 31                       # mfc/cfc
    return None


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


def room_at(data, o):
    """bytes a string at o may take in place: the original string plus the NUL padding after its terminator."""
    old = string_at(data, o)
    assert old is not None, f"{o:#x}: no string"
    room = len(old)
    while o + room + 1 < len(data) and data[o + room + 1] == 0:
        room += 1
    return room


def replace_in_place(data, new):
    """new: {offset: bytes}; each must fit the original string plus its NUL padding (else see fit())."""
    out = bytearray(data)
    for o, s in new.items():
        room = room_at(data, o)
        assert len(s) <= room, f"{o:#x}: {len(s)} bytes, room {room}"
        out[o:o + room + 1] = s + b"\0" * (room + 1 - len(s))
    return bytes(out)


# --- relocation (phase 7): strings longer than their slot move to the string heap, a RAM block below the EXE's
# original load address that build.patch_exe prepends to the EXE image (docs/re/space.md: zero in every RAM dump,
# battle included; no code references 0x8001xxxx). asm/font.asm owns 0x8001E000-0x80020000.
HEAP_LO, HEAP_HI = 0x80010000, 0x8001E000
CODE_FILES = ("SLPS_027.54", "op.bin", "rfd2.bin", "Battle.bin", "ed.bin", "pro.bin")   # every file with MIPS code


class Heap:
    """Relocated strings, laid out from HEAP_LO (4-byte aligned, identical strings shared).
    moved[file][old vaddr] = new vaddr; log[file] = [(offset, orig bytes, new bytes, by)] for romdiff --writes."""

    def __init__(self, lo=HEAP_LO, hi=HEAP_HI):
        self.lo, self.hi, self.buf, self.at = lo, hi, bytearray(), {}
        self.moved, self.log = {}, {}

    def add(self, s):
        if s not in self.at:
            va = self.lo + len(self.buf)
            self.buf += s + b"\0"
            self.buf += b"\0" * (-len(self.buf) % 4)
            assert self.lo + len(self.buf) <= self.hi, f"string heap full ({len(self.buf)} bytes)"
            self.at[s] = va
        return self.at[s]

    def put(self, name, orig, out, o, b, by):
        self.log.setdefault(name, []).append((o, bytes(orig[o:o + len(b)]), bytes(b), by))
        out[o:o + len(b)] = b


_LUI_CACHE = {}


def lui_values(name, data):
    """{lui offset: {values it forms}} for every lui pair in the file (cached by content)."""
    key = (name, hash(data), len(data))
    if key not in _LUI_CACHE:
        m = {}
        for a, b, v in lui_pairs(data):
            m.setdefault(a, {})[b] = v
        _LUI_CACHE[key] = m
    return _LUI_CACHE[key]


def ref_sites(name, data, va):
    """('ptr', off) and ('lui', lui off, low off) references to vaddr va anywhere in the file."""
    out = []
    for p in range(0, len(data) - 3, 4):
        if struct.unpack_from("<I", data, p)[0] == va:
            out.append(("ptr", p))
    for a, lows in lui_values(name, data).items():
        out += [("lui", a, b) for b, v in lows.items() if v == va]
    return out


def repoint(name, orig, out, refs, old, new, heap, by):
    """Point every ref (ptr / lui) at `new` instead of `old`. A lui whose register also forms another value (a
    second string, a struct field) cannot be rewritten: that stops the build."""
    lv = lui_values(name, orig)
    luis = {}
    for r in refs:
        if r[0] == "ptr":
            assert struct.unpack_from("<I", orig, r[1])[0] == old, f"{name} {r}: not {old:#x}"
            heap.put(name, orig, out, r[1], struct.pack("<I", new), by)
        elif r[0] == "lui":
            luis.setdefault(r[1], set()).add(r[2])
        else:
            raise AssertionError(f"{name} {old:#x}: {r[0]} reference cannot be re-pointed")
    for a, lows in luis.items():
        other = {b: v for b, v in lv[a].items() if v != old}
        assert not other, f"{name} {old:#x}: lui at {a:#x} also forms {[hex(v) for v in other.values()]}"
        assert set(lv[a]) == lows, f"{name} {old:#x}: lui at {a:#x} has lows {sorted(lv[a])} != refs {sorted(lows)}"
        kinds = {struct.unpack_from("<I", orig, b)[0] >> 26 == 0x0D for b in lows}
        assert len(kinds) == 1, f"{name} {old:#x}: lui at {a:#x} mixes ori and signed lows"
        hi = (new >> 16) if kinds.pop() else ((new + 0x8000) >> 16) & 0xFFFF
        w = struct.unpack_from("<I", orig, a)[0]
        heap.put(name, orig, out, a, struct.pack("<I", (w & 0xFFFF0000) | hi), by)
        for b in lows:
            w = struct.unpack_from("<I", orig, b)[0]
            heap.put(name, orig, out, b, struct.pack("<I", (w & 0xFFFF0000) | (new & 0xFFFF)), by)


_WIDTH = {0x20: 1, 0x24: 1, 0x21: 2, 0x25: 2, 0x22: 4, 0x26: 4, 0x23: 4}


def copy_size(name, data, o):
    """Bytes the code copies from the string at o when it inlines a short literal (`char buf[] = "..."`: addiu rT,
    then lw/lb at fixed offsets of rT into a stack buffer), else None. The English plus its NUL must fit that
    count wherever the string lives: the copy does not stop at the NUL."""
    e = _strings_cached(name, data).get(o)
    best = None
    for r in (e or {}).get("refs", []):
        if r[0] != "lui":
            continue
        w = struct.unpack_from("<I", data, r[2])[0]
        if w >> 26 != 0x09:
            continue
        rt, size = (w >> 16) & 31, 0
        for k in range(1, 41):
            if r[2] + 4 * (k + 1) > len(data):
                break
            w2 = struct.unpack_from("<I", data, r[2] + 4 * k)[0]
            op, rs, imm = w2 >> 26, (w2 >> 21) & 31, w2 & 0xFFFF
            if op in _WIDTH and rs == rt and imm < 0x100:
                size = max(size, imm + _WIDTH[op])
            if writes_reg(w2) == rt or 1 <= op <= 7 or (op == 0 and (w2 & 0x3E) == 0x08):
                break   # rT reused, or a branch / jump / jr ends the straight-line copy
        if size:
            best = size if best is None else min(best, size)
    return best


def _strings_cached(name, data):
    key = ("strings", name, hash(data), len(data))
    if key not in _LUI_CACHE:
        _LUI_CACHE[key] = strings(name, data)
    return _LUI_CACHE[key]


def limit(name, data, o):
    """Most bytes (without the NUL) the string at o may take in place: its slot, or a fixed literal copy."""
    room = room_at(data, o)
    c = copy_size(name, data, o)
    return room if c is None else min(room, c - 1)


def movable(name, data, o, found=None):
    """None if the string at o can be relocated, else the reason (no reference, or a fixed table slot)."""
    e = (found or _strings_cached(name, data)).get(o)
    if e is None or not e["refs"]:
        return "no reference to re-point"
    bad = {r[0] for r in e["refs"]} - {"ptr", "lui"}
    if bad:
        return f"{'/'.join(sorted(bad))} reference"
    va =base_of(name) + o
    lv = lui_values(name, data)
    for r in e["refs"]:
        if r[0] == "lui" and any(v != va for v in lv[r[1]].values()):
            return f"lui at {r[1]:#x} shared with other values"
    return None


def fit(name, data, new, heap):
    """new: {offset: bytes}. A string that fits its slot is written in place; a longer one goes to `heap` and every
    reference to it in this file is re-pointed (heap.moved records it for other files: build re-points those too).
    The vacated slot keeps its Japanese, so a reader the build missed shows Japanese, not garbage."""
    out = bytearray(data)
    found = None
    base = base_of(name)
    done = 0        # end of the last in-place write: a later string starting before it is a tail of that string
    for o, s in sorted(new.items()):
        room = room_at(data, o)
        c = copy_size(name, data, o)
        assert c is None or len(s) < c, f"{name} {base + o:#x}: {len(s)} bytes, the code copies {c} (with the NUL)"
        if o < done:
            # tail sharing (ペレイラ / イラ): the head was written already; keep the tail there only when the head's
            # English ends in exactly this string, else move it
            if out[o:o + len(s) + 1] == s + b"\0":
                continue
        elif len(s) <= room:
            buf = s + b"\0" * (room + 1 - len(s))
            tails = [t for t in new if o < t < o + room + 1]
            clash = [t for t in tails if buf[t - o:t - o + len(new[t]) + 1] != new[t] + b"\0"]
            if not clash or movable(name, data, o) is not None:
                heap.put(name, data, out, o, buf, "text")
                done = o + room + 1
                continue
            # else: the head moves and its tail string is written in place over the vacated Japanese
        found = found or strings(name, data)
        why = movable(name, data, o, found)
        assert why is None, f"{name} {base + o:#x}: {len(s)} bytes, room {room}, cannot move: {why}"
        va = heap.add(s)
        repoint(name, data, out, found[o]["refs"], base + o, va, heap, "move")
        heap.moved.setdefault(name, {})[base + o] = va
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
