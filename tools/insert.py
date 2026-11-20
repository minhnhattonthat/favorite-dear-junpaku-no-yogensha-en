"""insert.py: script/*.tsv -> the build's changes. Rows with an empty `<lang>` column keep their original bytes.

    changes(lang="en") -> (lkf_changes {archive: {entry: bytes}}, files {disc file: bytes})   (used by build.py)
    python -X utf8 tools/insert.py [--lang en]     # report how many rows and files would change

Width checks, fitting and EXE/overlay relocation are phase 5/7 work: codetext strings are replaced in place only
(an English string longer than its slot stops the build). English letters become pair codes here
(`font_en.to_pairs`); the glyphs come from asm/font.asm, which build.py applies to the EXE."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import font_en  # noqa: E402


def changes(lang="en", srcs=None, overrides=None, texts_for=None):
    """overrides: {row id: text} applied over the `lang` column (QA builds: build.py --qa).
    texts_for: function(source) -> {row id: text} that replaces the TSV column entirely (marker builds)."""
    lkf_changes, files, nrows = {}, {}, 0
    overrides = dict(overrides or {})
    for s in srcs or extract.sources():
        if not s.rows or not s.tsv.exists():
            continue
        if texts_for:
            texts = texts_for(s)
        else:
            rows = extract.read_tsv(s.tsv) if lang in extract.COLS else None
            assert rows is not None, f"no column {lang!r} in {extract.COLS}"
            texts = {r["id"]: r[lang] for r in rows if r[lang]}
        ids = {r.id for r in s.rows}
        for k in [k for k in overrides if k in ids]:
            texts[k] = overrides.pop(k)
        if not texts:
            continue
        unknown = set(texts) - {r.id for r in s.rows}
        assert not unknown, f"{s.tsv}: rows not in the extraction {sorted(unknown)[:5]} (run tools/extract.py)"
        nrows += len(texts)
        data = s.build({k: font_en.to_pairs(t) for k, t in texts.items()})
        if data == s.data:
            continue
        if s.where[0] == "lkf":
            lkf_changes.setdefault(s.where[1], {})[s.where[2]] = data
        else:
            files[s.where[1]] = data
    assert not overrides, f"override ids not in any source: {sorted(overrides)[:5]}"
    return lkf_changes, files, nrows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="en")
    a = ap.parse_args()
    lk, fl, n = changes(a.lang)
    print(f"{n} translated rows; changed: {sum(len(v) for v in lk.values())} archive entries, {len(fl)} files")


if __name__ == "__main__":
    main()
