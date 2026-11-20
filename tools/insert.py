"""insert.py: script/*.tsv -> the build's changes. Rows with an empty `<lang>` column keep their original bytes.

    changes(lang="en") -> (lkf_changes {archive: {entry: bytes}}, files {disc file: bytes})   (used by build.py)
    python -X utf8 tools/insert.py [--lang en]     # report how many rows and files would change

EXE/overlay strings longer than their slot move to the string heap (codetext.fit, with a Heap from build.py;
docs/re/space.md); without a heap they must fit in place. English letters become pair codes here
(`font_en.to_pairs`); the glyphs come from asm/font.asm, which build.py applies to the EXE."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import codetext  # noqa: E402
import extract  # noqa: E402
import font_en  # noqa: E402


# Load buffers per SSB_DATA file type (docs/re/space.md; measured with tools/debug/fileslog.lua blk=): .ssb and .EVX
# load into the 0x169C0-byte heap block at 0x801A4BB0, .end into a 0x8010-byte one at 0x80189B90 (both minus the
# 0x10 header). MSG: not measured; capped at the largest original (BTL_EVT banks also keep u16 offsets).
LOAD_CAPS = {"ssb": 0x169B0, "evx": 0x169B0, "end": 0x8000, "msg": 0x6B16}


def changes(lang="en", srcs=None, overrides=None, texts_for=None, heap=None):
    """overrides: {row id: text} applied over the `lang` column (QA builds: build.py --qa).
    texts_for: function(source) -> {row id: text} that replaces the TSV column entirely (marker builds).
    heap: a codetext.Heap; EXE/overlay strings longer than their slot move there (build.patch_exe writes it into
    the EXE). Without one, such a string stops the build."""
    lkf_changes, files, nrows = {}, {}, 0
    overrides = dict(overrides or {})
    srcs = srcs or extract.sources()
    for s in srcs:
        if hasattr(s, "heap"):
            s.heap = heap
    for s in srcs:
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
    for name, data in lkf_changes.get("SSB_DATA", {}).items():
        cap = LOAD_CAPS[name.rsplit(".", 1)[-1].lower()]
        assert len(data) <= cap, f"SSB_DATA {name}: {len(data):#x} bytes, its load buffer holds {cap:#x}"
    if heap is not None:
        repoint_exe_refs(heap, lkf_changes)
    return lkf_changes, files, nrows


def repoint_exe_refs(heap, lkf_changes):
    """Overlays that point at a moved EXE string (item and town names) are re-pointed too. Overlay strings need no
    such pass: the overlays share one load address, so only the overlay itself can reference its strings."""
    moved = heap.moved.get(extract.EXE, {})
    if not moved:
        return
    tree = extract.lkf.files((extract.TREE / "FD2BN.LKF").read_bytes())
    for e, orig in tree:
        name = e["name"]
        if name not in codetext.CODE_FILES:
            continue
        cur = lkf_changes.get("FD2BN", {}).get(name, orig)
        out = bytearray(cur)
        n = 0
        for old, new in moved.items():
            refs = codetext.ref_sites(name, orig, old)
            if refs:
                codetext.repoint(name, orig, out, refs, old, new, heap, "move-exe")
                n += len(refs)
        if n:
            lkf_changes.setdefault("FD2BN", {})[name] = bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="en")
    a = ap.parse_args()
    lk, fl, n = changes(a.lang)
    print(f"{n} translated rows; changed: {sum(len(v) for v in lk.values())} archive entries, {len(fl)} files")


if __name__ == "__main__":
    main()
