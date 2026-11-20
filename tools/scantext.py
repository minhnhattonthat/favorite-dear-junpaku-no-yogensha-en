"""scantext.py: Shift-JIS text runs in files (recon and leftover checks).

    python -X utf8 tools/scantext.py summary DIR_OR_FILE..      # per file: runs, chars (only files with hits)
    python -X utf8 tools/scantext.py runs FILE [--min 3]         # offset<TAB>text for every run

A run is a stretch of double-byte SJIS characters (plus ASCII backslash escapes like \\l \\k \\c and ASCII
letters/digits between them) holding at least `--min` double-byte characters and at least one kana, so TIM pixels and
code bytes rarely count."""
import argparse
import re
from pathlib import Path

LEAD = set(range(0x81, 0xA0)) | set(range(0xE0, 0xF0))


def runs(data, min_chars=3):
    return [(start, s) for start, _, s in spans(data, min_chars)]


def spans(data, min_chars=3):
    """(start, end, text) for every run; end is exclusive (trailing ASCII spaces included in the bytes)."""
    i, n = 0, len(data)
    out = []
    while i < n:
        start, chars, kana, j = i, 0, 0, i
        text = []
        while j < n:
            b = data[j]
            if b in LEAD and j + 1 < n and 0x40 <= data[j + 1] <= 0xFC and data[j + 1] != 0x7F:
                ch = data[j:j + 2]
                try:
                    c = ch.decode("cp932")
                except UnicodeDecodeError:
                    break
                if 0x3041 <= ord(c) <= 0x30FF:
                    kana += 1
                text.append(c)
                chars += 1
                j += 2
            elif chars and 0x20 <= b < 0x7F:
                text.append(chr(b))
                j += 1
            else:
                break
        if chars >= min_chars and kana:
            s = "".join(text).rstrip(" ")
            out.append((start, j, s))
            i = j
        else:
            i = start + 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["summary", "runs"])
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--min", type=int, default=3)
    a = ap.parse_args()
    files = []
    for p in map(Path, a.paths):
        files += sorted(f for f in p.rglob("*") if f.is_file()) if p.is_dir() else [p]
    for f in files:
        r = runs(f.read_bytes(), a.min)
        if a.cmd == "summary":
            if r:
                print(f"{len(r):6} {sum(len(s) for _, s in r):8} {f}")
        else:
            for off, s in r:
                print(f"{off:#08x}\t{s}")


if __name__ == "__main__":
    main()
