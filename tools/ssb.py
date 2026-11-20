"""ssb.py: tokenizer for the event scripts (*.ssb in SSB_DATA.LKF). Recon stage: model is a guess under test.

    python -X utf8 tools/ssb.py stats [FILES..]     # opcode histogram over all scripts; reports files that fail
    python -X utf8 tools/ssb.py dump FILE [--from 0x10 --to 0x400]

Model (docs/re/events.md): ".ssb" + 12 zero bytes, then a byte stream from 0x10. At each position:
- byte >= 0x80: one Shift-JIS character of message text (2 bytes);
- else byte = argument count N, next byte = opcode, then N little-endian u16 arguments;
- opcode 0x19 (speaker name): its single argument is a character count, followed by that many SJIS characters."""
import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSB_DIR = ROOT / "work/lkf/SSB_DATA"


def tokens(data, start=0x10, end=None):
    end = len(data) if end is None else end
    i = start
    while i < end:
        b = data[i]
        if b >= 0x80:
            yield ("ch", i, data[i:i + 2])
            i += 2
            continue
        if i + 2 > end:
            yield ("tail", i, data[i:end])
            return
        argc, op = b, data[i + 1]
        args = list(struct.unpack_from(f"<{argc}H", data, i + 2))
        j = i + 2 + 2 * argc
        if op == 0x19 and argc == 1:
            s = data[j:j + 2 * args[0]]
            yield ("op", i, (op, args, s))
            i = j + 2 * args[0]
            continue
        yield ("op", i, (op, args, None))
        i = j


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["stats", "dump"])
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
                for kind, off, val in tokens(d):
                    if kind == "op":
                        hist[val[0]] += 1
                        argcs.setdefault(val[0], Counter())[len(val[1])] += 1
                    elif kind == "tail":
                        bad.append((f.name, off, "tail"))
            except struct.error as ex:
                bad.append((f.name, "?", str(ex)))
        for op, n in sorted(hist.items()):
            print(f"op {op:#04x} x{n:6}  argc {dict(argcs[op])}")
        print("files", len(files), "bad", len(bad), bad[:5])
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
                line.append(f"<tail {val.hex()}>")
        print("".join(line))


if __name__ == "__main__":
    main()
