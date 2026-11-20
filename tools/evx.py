"""evx.py: battle setups (SSB_DATA *.EVX): the text in them (docs/re/events.md §EVX).

    python -X utf8 tools/evx.py dump FILE

- 0x02: 30-byte NUL-padded title (a dev label like "ラストバトル(負ける)"; guess: not shown in game).
- unit records of 0x3C bytes from 0xA0: u16, then a 32-byte NUL-padded unit name (セシア, ジャイアント); the run of
  records ends at the first one with no name.
- message records: u16 0x14, u16 2, u16 cmd, u16 size (whole record), then items (u8 type 0x08/0x0A, u8 length
  incl. NUL, text NUL), then raw bytes to `size`. cmd low byte: 0x2A text, 0x2C speaker, 0x2D choices (two items).
  Found by pattern and checked by size; u8 lengths cap one item at 254 bytes of text.
Unknown: whether anything holds offsets into the record stream (growth untested: phase 5)."""
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jtext  # noqa: E402

REC = re.compile(rb"\x14\x00\x02\x00[\x2a\x2c\x2d][\x01\x03]", re.S)
TITLE = (0x02, 30)
UNIT0, UNIT_STRIDE, UNIT_NAME = 0xA0, 0x3C, 32


def _items(data, p, end):
    """[(type offset, text offset, text bytes)] of the items from p; stops at the first non-item."""
    out = []
    while p + 2 <= end and data[p] in (0x08, 0x0A):
        n = data[p + 1]
        s = data[p + 2:p + 2 + n]
        if n == 0 or p + 2 + n > end or not s.endswith(b"\0") or b"\0" in s[:-1]:
            break
        out.append((p, p + 2, s[:-1]))
        p += 2 + n
    return out


def parse(data):
    """{"strings": [[key, kind, bytes]], "recs": [(rec offset, size, [item offsets])]}; key = hex offset of the text."""
    strings, recs = [], []
    t = data[TITLE[0]:TITLE[0] + TITLE[1]]
    title = t.split(b"\0")[0]  # some fields carry junk after the NUL; build leaves it
    if title:
        strings.append([f"{TITLE[0]:04X}", "title", title])
    k = 0
    while UNIT0 + UNIT_STRIDE * (k + 1) <= len(data):
        o = UNIT0 + UNIT_STRIDE * k + 2
        fld = data[o:o + UNIT_NAME]
        nm = fld.split(b"\0")[0]
        if not nm or fld[len(nm):].strip(b"\0"):
            break
        try:
            nm.decode("cp932")
        except UnicodeDecodeError:
            break
        strings.append([f"{o:04X}", "unit", nm])
        k += 1
    for m in REC.finditer(data):
        o = m.start()
        size = struct.unpack_from("<H", data, o + 6)[0]
        if size < 10:
            continue
        # the last record of some files is cut by the end of the file (its size counts bytes that are not there)
        its = _items(data, o + 8, min(o + size, len(data)))
        if not its:
            continue
        try:
            for _, _, s in its:
                s.decode("cp932")
        except UnicodeDecodeError:
            continue
        kind = {0x2A: "text", 0x2C: "speaker", 0x2D: "choice"}[data[o + 4]]
        recs.append((o, size, [it[0] for it in its]))
        for _, so, s in its:
            strings.append([f"{so:04X}", kind, s])
    return {"strings": strings, "recs": recs, "units": k}


def build(data, new=None):
    """EVX bytes with strings replaced: new = {key: bytes}. Fixed fields are NUL-padded; record sizes and item
    lengths are rewritten."""
    new = new or {}
    info = parse(data)
    keys = {k for k, _, _ in info["strings"]}
    bad = set(new) - keys
    assert not bad, f"unknown keys {sorted(bad)[:5]}"
    out = bytearray(data)
    for key, kind, _ in info["strings"]:
        if key in new and kind in ("title", "unit"):
            o = int(key, 16)
            width = TITLE[1] if kind == "title" else UNIT_NAME
            s = new[key]
            assert len(s) <= width, f"{key}: {len(s)} bytes, field holds {width} (a full title has no NUL)"
            if kind == "title":
                out[o:o + len(s) + (len(s) < width)] = s + b"\0" * (len(s) < width)
            else:
                out[o:o + width] = s + b"\0" * (width - len(s))
    if not any(k in new for k, kind, _ in info["strings"] if kind not in ("title", "unit")):
        return bytes(out)
    # records: rebuild back to front so earlier offsets stay valid
    for o, size, items in reversed(info["recs"]):
        body = bytearray()
        for p in items:
            n = data[p + 1]
            key = f"{p + 2:04X}"
            s = new.get(key, data[p + 2:p + 1 + n])
            assert len(s) + 1 <= 0xFF, f"{key}: item over 254 bytes"
            body += bytes([data[p], len(s) + 1]) + s + b"\0"
        last = items[-1]
        end = min(o + size, len(data))
        rest = data[last + 2 + data[last + 1]:end]
        rec = bytearray(data[o:o + 8]) + body + rest
        grow = len(rec) - (end - o)
        assert size + grow < 0x10000
        struct.pack_into("<H", rec, 6, size + grow)
        out[o:end] = rec
    return bytes(out)


def main(argv):
    if len(argv) != 2 or argv[0] != "dump":
        sys.exit(__doc__)
    info = parse(Path(argv[1]).read_bytes())
    for key, kind, s in info["strings"]:
        print(f"{key}\t{kind}\t{jtext.decode(s)}")


if __name__ == "__main__":
    main(sys.argv[1:])
