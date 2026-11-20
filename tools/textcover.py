"""textcover.py: which script/ rows has any QA run reached? (phase 8 coverage gate)

    python -X utf8 tools/textcover.py work/qa/cover [--waive docs/text_unshown.tsv] [--missing OUT.tsv]

Reads every log.txt under the given folders, written by warp runs with tools/debug/textcover.lua on the ORIGINAL
disc. Each "TREAD addr" is mapped to the file most recently loaded over that address ("FILE ... name dst=..."),
then to the row whose bytes contain that offset (row id = file stem + offset; ovl ids = vaddr, file loaded at
0x8009B4B0). Reads must match the original byte (logged by textcover.lua) on 4 distinct offsets of a row
(`reached`). Rows are keyed folder/id ("ssb/visit_01.0012": ids repeat across ssb/ and evx/). Prints coverage per
script folder, writes the keys never reached (and not waived) to --missing, and exits 1 while any is left.
Waive file: key<TAB>reason (a key, or a prefix ending in '*', e.g. "msg/FryMsg0.*").
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


EXT = {"ssb": "ssb", "evx": "evx", "msg": "msg", "end": "end", "ovl": "bin", "misc": "dat"}


def load_rows():
    """{file name lower (stem.ext): (starts, [(start, end, key)])}, folder of each key. A key is folder/id
    ("evx/ceev03.0012"): the same id can exist in ssb/ and evx/ (ceev03.ssb, ceev03.EVX)."""
    files, folder = {}, {}
    for tsv in sorted((ROOT / "script").rglob("*.tsv")):
        kind = tsv.parent.name if tsv.parent.name != "script" else tsv.stem
        if kind == "exe":
            continue  # EXE strings: not watched (yet); waive or watch per string
        with open(tsv, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                rid = row["id"]
                stem, _, off = rid.rpartition(".")
                start = int(re.match(r"[0-9A-Fa-f]+", off).group(0), 16)  # ids may carry a suffix (01E0S)
                if kind == "ovl":
                    start -= OVL_BASE
                key = f"{kind}/{rid}"
                files.setdefault(f"{stem}.{EXT[kind]}".lower(), []).append((start, start + jp_len(row["jp"]), key))
                folder[key] = kind
    out = {}
    for stem, rows in files.items():
        rows.sort()
        out[stem] = ([r[0] for r in rows], rows)
    return out, folder


_ORIG = {}
NEED = 4


def orig_bytes(stem):
    """The original file's bytes (work/lkf/SSB_DATA/NNNN_name.ext, work/orig_ovl/name.bin), None if not found."""
    if not _ORIG:
        for p in (ROOT / "work/lkf/SSB_DATA").glob("*"):
            _ORIG.setdefault(p.name.split("_", 1)[-1].lower(), p)
        for p in (ROOT / "work/orig_ovl").glob("*.bin"):
            _ORIG.setdefault(p.name.lower(), p)
    if isinstance(_ORIG.get(stem), pathlib.Path):
        _ORIG[stem] = _ORIG[stem].read_bytes()
    return _ORIG.get(stem)


def reached(logs, files):
    """Row keys read in any log. A read counts only if the logged byte equals the original file's byte there (logs
    with values), and a row needs NEED distinct such offsets (fewer if it is that short): a buffer reused for other
    data, whose bytes match the text's here and there by chance, does not count."""
    hit = set()
    tread = re.compile(r"TREAD ([0-9A-F]+)(?: ([0-9A-F]{2}))?")
    fline = re.compile(r"FILE f\d+ (\S+) dst=([0-9A-F]+)(?: size=([0-9A-F]+))?")
    for log in logs:
        count = {}
        bufs = []  # (dst, size or None, stem) newest last
        for line in open(log, encoding="utf-8", errors="replace"):
            m = fline.search(line)
            if m:
                stem = m.group(1).lower()
                size = int(m.group(3), 16) if m.group(3) else None
                bufs.append((int(m.group(2), 16) & 0xFFFFFFFF, size, stem))
                continue
            m = tread.search(line)
            if not m:
                continue
            addr = int(m.group(1), 16) & 0xFFFFFFFF   # early logs sign-extended (LuaJIT): FFFFFFFF800D77B8
            for dst, size, stem in reversed(bufs):
                if addr < dst:
                    continue
                if stem not in files:
                    if size is not None and addr < dst + size:
                        break  # a newer non-text file (an image) sits over this address
                    continue
                starts, rows = files[stem]
                off = addr - dst
                if m.group(2) is not None:
                    data = orig_bytes(stem)
                    if data is not None and off < len(data) and data[off] != int(m.group(2), 16):
                        break  # the buffer holds something else now
                i = bisect.bisect_right(starts, off) - 1
                if i >= 0 and rows[i][0] <= off < rows[i][1]:
                    rid = rows[i][2]
                    offs = count.setdefault(rid, set())
                    offs.add(off)
                    if len(offs) >= min(NEED, rows[i][1] - rows[i][0]) or m.group(2) is None:
                        hit.add(rid)
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
