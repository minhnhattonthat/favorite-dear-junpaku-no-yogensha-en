"""lint.py: text lint over the merged script/**/*.tsv (the files the build reads). check.py runs it.

    python -X utf8 tools/lint.py [-v]     errors (first 40 unless -v) and one summary line; exit 1 if any

Every row with Japanese in `jp` is checked:
- `en` empty: only ids listed in script/keep_jp.txt (id<TAB>reason) may stay Japanese;
- Japanese or characters outside the English font left in `en` (placeholders, ＄＄＄＄＄＄ and ￥ excepted);
- control codes: the same sequence as the JP, ignoring {n} in wrapped rows; wrapped rows that may add pages may
  also add {wait}{clear};
- wrapped rows: line width (batches.width) and lines per page against batches.wrap_spec; a stub last line (under
  batches.STUB letters) after a break the wrap had to make;
- unwrapped rows (labels in fixed fields): leading / trailing blanks the JP has and the English dropped;
- other rows: width against the box budget in tools/widths.tsv (id prefix / regex -> letters), when one matches.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches as B  # noqa: E402
import extract  # noqa: E402

KEEP = ROOT / "script" / "keep_jp.txt"
WIDTHS = ROOT / "tools" / "widths.tsv"
BLANK = " 　"


def keep_list():
    out = {}
    for line in KEEP.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            i, why = line.split("\t", 1)
            out[i] = why
    return out


def budgets():
    """[(regex on 'file:id', letters, box)]"""
    out = []
    for line in WIDTHS.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            pat, n, box = line.split("\t")
            out.append((re.compile(pat), int(n), box))
    return out


def footprint(jp):
    """the JP's width in letters (a full-width cell is 2)"""
    return sum(1 if ord(c) < 0x80 else 2 for c in B.TAG.sub("", jp))


def plain(s):
    s = B.TAG.sub("", s).replace(B.NAME, "")
    for t in B.GAME_TAGS:
        s = s.replace(t, "")
    return s.replace("￥", "")


def row_errors(p, r, spec, bud):
    jp, en, i = r["jp"], r["en"], r["id"]
    errs = []
    bad = {c for c in plain(en) if c not in B.ALLOWED}
    if bad:
        errs.append(f"characters not in the English font {''.join(sorted(bad))}")
    soft = spec is not None
    cj, ce = jp, en
    if spec and spec[2]:
        if en.count(B.PAGE) < jp.count(B.PAGE):
            errs.append(f"{jp.count(B.PAGE)} pages in the JP, {en.count(B.PAGE)} in the English")
        cj, ce = jp.replace(B.PAGE, ""), en.replace(B.PAGE, "")
    if B.codes(ce, soft) != B.codes(cj, soft):
        errs.append(f"codes {B.codes(ce, soft)} != {B.codes(cj, soft)}")
    for side in (0, -1) if spec is None else ():    # labels padded to a fixed field; dialogue blanks don't matter
        if (jp[side:] or " ")[0] in BLANK and jp.strip(BLANK) and (en[side:] or "x")[0] not in BLANK \
                and B.width(en) < footprint(jp):         # padding to the JP's width (tools/padlabels.py)
            errs.append(f"the JP {'starts' if side == 0 else 'ends'} with a blank, the English does not")
    if spec:
        w, lines_max, _ = spec
        for page in en.split(B.PAGE):
            lines = page.split("{n}")
            if len(lines) > lines_max:
                errs.append(f"{len(lines)} lines on a page (max {lines_max})")
            for ln in lines:
                if B.width(ln) > w:
                    errs.append(f"line of {B.width(ln)} letters (max {w}): {ln[:30]}")
            if len(lines) >= 2 and B.width(lines[-1]) < B.STUB and lines[-1].strip() \
                    and B.width(f"{lines[-2]} {lines[-1]}") > w:
                errs.append(f"stub last line {lines[-1]!r}")
    else:
        key = f"{p.relative_to(B.SCRIPT).as_posix()}:{i}"
        for pat, n, box in bud:
            if pat.search(key):
                for ln in en.split("{n}"):
                    if B.width(ln) > n:
                        errs.append(f"{B.width(ln)} letters, the {box} holds {n}: {ln[:30]}")
                break
    return errs


def lint():
    keep, bud = keep_list(), budgets()
    errs, n, used = [], 0, set()
    for p in B.files():
        for r in extract.read_tsv(p):
            if not B.has_jp(r["jp"]):
                continue
            n += 1
            where = f"{p.relative_to(B.SCRIPT).as_posix()}:{r['id']}"
            if not r["en"]:
                if r["id"] in keep:
                    used.add(r["id"])
                else:
                    errs.append(f"{where}: no English (add it, or list it in script/keep_jp.txt)")
                continue
            errs += [f"{where}: {e}" for e in row_errors(p, r, B.wrap_spec(p, r), bud)]
    errs += [f"keep_jp.txt: {i} is not an untranslated row" for i in keep if i not in used]
    return errs, n


def main(argv):
    errs, n = lint()
    for e in errs if "-v" in argv else errs[:40]:
        print(e)
    print(f"lint: {n} rows, {len(errs)} errors")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
