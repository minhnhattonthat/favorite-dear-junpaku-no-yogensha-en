"""padlabels.py: pad unwrapped labels to the JP's fixed field (lint: "the JP starts/ends with a blank").

    python -X utf8 tools/padlabels.py [--write]     list (or write into trans/en) the padded English

A JP label padded with full-width blanks ("睡眠中　　　　　　　", "　　　　王国") fills a fixed field: trailing blanks
erase the previous value drawn there, leading ones right-align. The English gets ASCII spaces up to the JP's width
in letters (a full-width cell = 2 letters = 2 bytes, so the padded English is never more bytes than the JP).
Run `batches.py merge` afterwards."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches as B  # noqa: E402
import extract  # noqa: E402
import lint  # noqa: E402


def padded(jp, en):
    n = lint.footprint(jp) - B.width(en)
    if n <= 0:
        return en
    if jp[:1] in lint.BLANK and en[:1] not in lint.BLANK:
        return " " * n + en
    if jp[-1:] in lint.BLANK and en[-1:] not in lint.BLANK:
        return en + " " * n
    return en


def main(argv):
    want = {}                                    # (rep id, batch jp) -> padded en
    for jp, members in B.families().items():
        p0, r0, _ = members[0]
        if B.wrap_spec(p0, r0) is not None or not r0["en"]:
            continue
        en = padded(jp, r0["en"])
        if en != r0["en"]:
            want[(r0["id"], jp)] = en
    n = 0
    for outp in sorted(B.OUT.glob("b*.tsv")):
        inp = {r[0]: r[3] for r in B.read_tsv(B.BATCHES / outp.name)}
        rows = B.read_tsv(outp)
        hit = False
        for f in rows:
            k = (f[0], inp.get(f[0]))
            if k in want and f[1] != "-":
                print(f"{outp.stem} {f[0]}: {f[1]!r} -> {want[k]!r}")
                f[1] = want[k]
                hit = True
                n += 1
        if hit and "--write" in argv:
            B.write_tsv(outp, ["id", "en"], rows)
    print(f"{n} labels padded{'' if '--write' in argv else ' (dry run)'}")


if __name__ == "__main__":
    main(sys.argv[1:])
