"""textcover.py: which script/ rows has any QA run reached? (phase 8 coverage gate)

    python -X utf8 tools/textcover.py work/qa/cover [--waive docs/text_unshown.tsv] [--missing OUT.tsv]

Reads every log.txt under the given folders, written by warp runs with tools/debug/textcover.lua on the ORIGINAL
disc. Each "TREAD addr" is mapped to the file most recently loaded over that address ("FILE ... name dst=..."),
then to the row whose bytes contain that offset (row id = file stem + offset; ovl ids = vaddr, file loaded at
0x8009B4B0). Prints coverage per script folder, writes the rows never reached (and not waived) to --missing,
and exits 1 while any is left. Waive file: id<TAB>reason (a row id, or a prefix ending in '*', e.g. "visit_01.*").
"""
import argparse
import bisect
import csv
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OVL_BASE = 0x8009B4B0
CODE = re.compile(r"\{[^}]*\}")


def jp_len(jp):
    """Byte length of a row's JP text: SJIS, each {code} counted as 2 bytes (a guess that only widens the range)."""
    n = len(CODE.findall(jp)) * 2
    try:
        n += len(CODE.sub("", jp).encode("cp932"))
    except UnicodeEncodeError:
        n += 2 * len(CODE.sub("", jp))
    return max(n, 1)


def load_rows():
    """{file stem lower: (starts, [(start, end, id)])}, folder of each id."""
    files, folder = {}, {}
    for tsv in sorted((ROOT / "script").rglob("*.tsv")):
        kind = tsv.parent.name if tsv.parent.name != "script" else tsv.stem
        with open(tsv, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                rid = row["id"]
                stem, _, off = rid.rpartition(".")
                start = int(re.match(r"[0-9A-Fa-f]+", off).group(0), 16)  # ids may carry a suffix (01E0S)
                if kind == "ovl":
                    start -= OVL_BASE
                if kind == "exe":
                    continue  # EXE strings: not watched (yet); waive or watch per string
                files.setdefault(stem.lower(), []).append((start, start + jp_len(row["jp"]), rid))
                folder[rid] = kind
    out = {}
    for stem, rows in files.items():
        rows.sort()
        out[stem] = ([r[0] for r in rows], rows)
    return out, folder


def reached(logs, files):
    hit = set()
    tread = re.compile(r"TREAD ([0-9A-F]+)")
    fline = re.compile(r"FILE f\d+ (\S+) dst=([0-9A-F]+)")
    for log in logs:
        bufs = []  # (dst, stem) newest last
        for line in open(log, encoding="utf-8", errors="replace"):
            m = fline.search(line)
            if m:
                stem = m.group(1).rsplit(".", 1)[0].lower()
                bufs.append((int(m.group(2), 16), stem))
                continue
            m = tread.search(line)
            if not m:
                continue
            addr = int(m.group(1), 16)
            for dst, stem in reversed(bufs):
                if stem not in files or addr < dst:
                    continue
                starts, rows = files[stem]
                off = addr - dst
                i = bisect.bisect_right(starts, off) - 1
                if i >= 0 and rows[i][0] <= off < rows[i][1]:
                    hit.add(rows[i][2])
                    break
                if off < rows[-1][1]:
                    break  # inside this file but between rows (script ops): not text
    return hit


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--waive", default=str(ROOT / "docs/text_unshown.tsv"))
    ap.add_argument("--missing")
    a = ap.parse_args()
    files, folder = load_rows()
    logs = [p for d in a.dirs for p in pathlib.Path(d).rglob("log.txt")]
    hit = reached(logs, files)
    waive = []
    wp = pathlib.Path(a.waive)
    if wp.exists():
        for line in wp.read_text(encoding="utf-8").splitlines():
            if line and not line.startswith("#"):
                waive.append(line.split("\t")[0])

    def waived(rid):
        return any(rid.startswith(w[:-1]) if w.endswith("*") else rid == w for w in waive)

    total, shown, missing = {}, {}, []
    for rid, kind in folder.items():
        total[kind] = total.get(kind, 0) + 1
        if rid in hit:
            shown[kind] = shown.get(kind, 0) + 1
        elif not waived(rid):
            missing.append(rid)
    print(f"{len(logs)} logs")
    for kind in sorted(total):
        print(f"{kind:5} {shown.get(kind, 0):6} / {total[kind]:6} reached")
    print(f"not reached and not waived: {len(missing)} (EXE strings not counted)")
    if a.missing:
        pathlib.Path(a.missing).write_text("".join(f"{m}\n" for m in sorted(missing)), encoding="utf-8")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
