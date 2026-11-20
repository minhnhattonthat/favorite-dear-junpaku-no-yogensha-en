"""ssb.py: the event scripts (*.ssb in SSB_DATA.LKF): tokenizer, text rows, rebuild with jump fixups.

    python -X utf8 tools/ssb.py stats [FILES..]     # opcode histogram over all scripts; reports files that fail
    python -X utf8 tools/ssb.py dump FILE [--from 0x10 --to 0x400]
    python -X utf8 tools/ssb.py rows FILE           # the text rows extract.py writes

Model (docs/re/events.md): ".ssb" + 12 zero bytes, then a byte stream from 0x10. At each position:
- byte >= 0x80: one Shift-JIS character of message text (2 bytes);
- 0x20 <= byte < 0x80: one ASCII character (dev leftovers only: "text_on;", "/イベント/");
- else byte = argument count N, next byte = opcode, then N little-endian u16 arguments;
- opcode 0x19 (speaker name): its single argument is a character count, followed by that many SJIS characters.
Jumps (JUMPS: opcode -> index of the argument that is an absolute file offset) land on a token start, sometimes in
the middle of a text line. Bytes the linear walk would read across a jump target are dead bytes ("raw" tokens:
0184_loev04_01.ssb 0x4ba, `3a 0a` after a goto)."""
import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jtext  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SSB_DIR = ROOT / "work/lkf/SSB_DATA"
HEADER = 0x10
JUMPS = {0x5B: 0, 0x5C: 2, 0x5E: 2, 0x5F: 2, 0x62: 2, 0x63: 2, 0x67: 0}
TEXT_OPS = {0x02: "n", 0x05: "wait", 0x06: "clear"}  # ops that live inside a text row, as tags
TAGS = {name: bytes([0, op]) for op, name in TEXT_OPS.items()}
NAME = 0x19


def _token_end(data, i):
    b = data[i]
    if b >= 0x80:
        return i + 2
    if b >= 0x20:
        return i + 1
    if i + 2 > len(data):
        return len(data)
    argc, op = b, data[i + 1]
    j = i + 2 + 2 * argc
    if op == NAME and argc == 1 and j <= len(data):
        j += 2 * struct.unpack_from("<H", data, i + 2)[0]
    return j


def tokens(data, start=HEADER, end=None, targets=frozenset()):
    """Yield (kind, offset, value): ("ch", off, bytes), ("op", off, (op, args, name bytes or None)), ("raw", off,
    bytes), ("tail", off, bytes). A token that would span a jump target is cut there as "raw"."""
    end = len(data) if end is None else end
    i = start
    while i < end:
        j = _token_end(data, i)
        cut = [t for t in targets if i < t < j]
        if cut:
            t = min(cut)
            yield ("raw", i, data[i:t])
            i = t
            continue
        if j > end:
            yield ("tail", i, data[i:end])
            return
        b = data[i]
        if b >= 0x20:
            yield ("ch", i, data[i:j])
        else:
            argc, op = b, data[i + 1]
            args = list(struct.unpack_from(f"<{argc}H", data, i + 2))
            name = data[i + 2 + 2 * argc:j] if op == NAME and argc == 1 else None
            yield ("op", i, (op, args, name))
        i = j


def jump_targets(toks):
    return {v[1][JUMPS[v[0]]] for k, _, v in toks if k == "op" and v[0] in JUMPS}


def parse(data):
    """Token list with jump re-sync and dead bytes as "raw" (merged)."""
    assert data[:4] == b".ssb", "not an ssb"
    targets = set()
    for _ in range(8):
        toks = list(tokens(data, targets=frozenset(targets)))
        new = {t for t in jump_targets(toks) if HEADER <= t < len(data)}
        if new <= targets:
            break
        targets |= new
    # ASCII "characters" right before dead bytes and after an unconditional end of flow are dead too
    for i, (k, o, v) in enumerate(toks):
        if k == "raw":
            j = i - 1
            while j >= 0 and toks[j][0] == "ch" and len(toks[j][2]) == 1:
                j -= 1
            if j >= 0 and toks[j][0] == "op" and toks[j][2][0] in (0x5B, 0xFF):
                for m in range(j + 1, i):
                    toks[m] = ("raw", toks[m][1], toks[m][2])
    merged = []
    for t in toks:
        if t[0] == "raw" and merged and merged[-1][0] == "raw" and merged[-1][1] + len(merged[-1][2]) == t[1]:
            merged[-1] = ("raw", merged[-1][1], merged[-1][2] + t[2])
        else:
            merged.append(t)
    starts = {o for _, o, _ in merged}
    bad = [t for t in jump_targets(merged) if t not in starts]
    assert not bad, f"jump targets not on a token: {[hex(t) for t in bad]}"
    assert not [t for t in merged if t[0] == "tail"], "stream runs past the end"
    return merged, targets


def units(toks, targets):
    """Text rows: (kind, first token index, last token index + 1) for "text" (characters and TEXT_OPS, starting
    at a character, split at jump targets) and "name" (an op 0x19 payload)."""
    out = []
    i, n = 0, len(toks)
    while i < n:
        k, o, v = toks[i]
        if k == "op" and v[0] == NAME and v[2] is not None:
            out.append(("name", i, i + 1))
            i += 1
            continue
        if k != "ch":
            i += 1
            continue
        j = i + 1
        while j < n and toks[j][1] not in targets and (toks[j][0] == "ch" or (toks[j][0] == "op" and toks[j][2][0] in TEXT_OPS)):
            j += 1
        out.append(("text", i, j))
        i = j
    return out


def unit_bytes(toks, u):
    kind, a, b = u
    if kind == "name":
        return toks[a][2][2]
    return b"".join(_tok_bytes(t) for t in toks[a:b])


def decode_row(raw, kind):
    """Row bytes -> text form. Text rows tag ops 02/05/06; names are plain characters."""
    if kind == "name":
        return jtext.decode(raw, escapes=False)
    out, i = [], 0
    while i < len(raw):
        if raw[i] == 0 and i + 1 < len(raw) and raw[i + 1] in TEXT_OPS:
            out.append("{" + TEXT_OPS[raw[i + 1]] + "}")
            i += 2
            continue
        j = i
        while j < len(raw) and not (raw[j] == 0 and j + 1 < len(raw) and raw[j + 1] in TEXT_OPS):
            j += 2 if raw[j] >= 0x80 else 1
        out.append(jtext.decode(raw[i:j], escapes=False))
        i = j
    return "".join(out)


def encode_row(text, kind):
    return jtext.encode(text, tags=None if kind == "name" else TAGS)


def _tok_bytes(t):
    k, o, v = t
    if k != "op":
        return v
    op, args, name = v
    return bytes([len(args), op]) + struct.pack(f"<{len(args)}H", *args) + (name or b"")


def rows(data):
    """[(row offset, kind, bytes)] for every text unit; row offset = the unit's first byte (a name row: its op)."""
    toks, targets = parse(data)
    return [(toks[u[1]][1], u[0], unit_bytes(toks, u)) for u in units(toks, targets)]


def build(data, new=None):
    """Script bytes with rows replaced: new = {row offset: bytes} (bytes as encode_row gives). Jumps are re-pointed.
    A name row's bytes must be whole double-byte characters (its argument counts them; English names: phase 5)."""
    new = new or {}
    toks, targets = parse(data)
    us = {toks[u[1]][1]: u for u in units(toks, targets)}
    bad = set(new) - set(us)
    assert not bad, f"no row at {sorted(bad)[:5]}"
    out = bytearray(data[:HEADER])
    newpos, fix = {}, []
    i = 0
    while i < len(toks):
        k, o, v = toks[i]
        newpos[o] = len(out)
        if o in new:
            kind, a, b = us[o]
            if kind == "name":
                nm = new[o]
                assert len(nm) % 2 == 0, f"name row {o:#x}: odd byte count"
                out += bytes([1, NAME]) + struct.pack("<H", len(nm) // 2) + nm
            else:
                out += new[o]
            i = b
            continue
        if k == "op" and v[0] in JUMPS:
            fix.append((len(out) + 2 + 2 * JUMPS[v[0]], v[1][JUMPS[v[0]]]))
        out += _tok_bytes(toks[i])
        i += 1
    newpos[len(data)] = len(out)
    for at, old in fix:
        if HEADER <= old <= len(data):
            assert old in newpos, f"jump to {old:#x} inside a replaced row"
            struct.pack_into("<H", out, at, newpos[old])
        # else: an out-of-file value is kept as is
    assert len(out) < 0x10000, "script over 64 KB (16-bit jump offsets)"
    return bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["stats", "dump", "rows"])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--from", dest="start", default="0x10")
    ap.add_argument("--to", default=None)
    a = ap.parse_args()
    files = [Path(f) for f in a.files] or sorted(SSB_DIR.glob("*.ssb"))
    if a.cmd == "stats":
        hist, argcs, bad = Counter(), {}, []
        for f in files:
            d = f.read_bytes()
            try:
                toks, _ = parse(d)
                for kind, off, val in toks:
                    if kind == "op":
                        hist[val[0]] += 1
                        argcs.setdefault(val[0], Counter())[len(val[1])] += 1
                    elif kind == "raw":
                        bad.append((f.name, hex(off), "raw " + val.hex()))
            except (AssertionError, struct.error) as ex:
                bad.append((f.name, "?", str(ex)))
        for op, n in sorted(hist.items()):
            print(f"op {op:#04x} x{n:6}  argc {dict(argcs[op])}")
        print("files", len(files), "notes", len(bad), bad[:5])
    elif a.cmd == "rows":
        for off, kind, raw in rows(files[0].read_bytes()):
            print(f"{off:04X}\t{kind}\t{decode_row(raw, kind)}")
    else:
        d = files[0].read_bytes()
        end = int(a.to, 0) if a.to else None
        line = []
        for kind, off, val in tokens(d, int(a.start, 0), end):
            if kind == "ch":
                line.append(val.decode("cp932", "replace"))
            elif kind == "op":
                op, args, s = val
                txt = f"<{op:02x}{':' + ','.join(map(str, args)) if args else ''}>"
                if s is not None:
                    txt += s.decode("cp932", "replace")
                line.append(txt)
            else:
                line.append(f"<{kind} {val.hex()}>")
        print("".join(line))


if __name__ == "__main__":
    main()
