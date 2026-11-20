"""similar.py: show batch rows next to the closest already-translated row of the same file family.

    python -X utf8 tools/similar.py b057 [FIRST LAST] [--min 0.55]

Family = the row id's file name with digits removed (FryMsg0/FryMsg3 -> FryMsg), so parallel files written for
different speakers (fairy reports, hero chat) line up. Prints `id jp`, then `~ ratio id en` of the best match.
Read-only helper for translators; it changes nothing.
"""
import csv
import difflib
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def family(row_id):
    return re.sub(r"\d", "", row_id.split(".")[0]).lower()


def read(path):
    with open(path, encoding="utf8", newline="") as f:
        return [r for r in csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)][1:]


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    minr = 0.55
    if "--min" in argv:
        minr = float(argv[argv.index("--min") + 1])
        args.remove(argv[argv.index("--min") + 1])
    batch = args[0]
    rows = read(os.path.join(ROOT, "trans", "batches", batch + ".tsv"))
    if len(args) >= 3:
        rows = rows[int(args[1]) - 1:int(args[2])]
    jp = {}
    for p in glob.glob(os.path.join(ROOT, "trans", "batches", "b*.tsv")):
        for r in read(p):
            jp[r[0]] = r[-1]
    done = []
    for p in sorted(glob.glob(os.path.join(ROOT, "trans", "en", "b*.tsv"))):
        if os.path.basename(p) == batch + ".tsv":
            continue
        for r in read(p):
            if r[0] in jp and len(r) > 1:
                done.append((r[0], jp[r[0]], r[1]))
    for r in rows:
        rid, src = r[0], r[-1]
        print(f"{rid}\t{r[2] if len(r) > 3 else ''}\t{src}")
        fam = family(rid)
        best = (0.0, None)
        for did, djp, den in done:
            if family(did) != fam:
                continue
            sm = difflib.SequenceMatcher(None, src, djp, autojunk=False)
            if sm.real_quick_ratio() < best[0] or sm.quick_ratio() < best[0]:
                continue
            ratio = sm.ratio()
            if ratio > best[0]:
                best = (ratio, (did, den))
        if best[1] and best[0] >= minr:
            print(f"  ~ {best[0]:.2f} {best[1][0]}\t{best[1][1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
