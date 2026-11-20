"""Text extraction (phase 4): every row round-trips to the original bytes, every Japanese run in a text file is inside
a row, script/*.tsv matches the disc, and scripts/battle setups survive growing text. Skipped without the disc."""
import bisect
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
TREE = ROOT / "work/disc/tree"

import evx  # noqa: E402
import extract  # noqa: E402
import jtext  # noqa: E402
import scantext  # noqa: E402
import ssb  # noqa: E402

needs_disc = pytest.mark.skipif(not (TREE / "SSB_DATA.LKF").is_file(), reason="disc not unpacked (work/disc/tree)")

# Japanese runs that are not text, by source TSV name and file offset (with the reason)
WAIVE = {
    # glyph-index tables: every Nth character of the JIS order, no NUL (docs/re/text.md §Fonts)
    "exe.tsv": {0x5EA03: "glyph table", 0x5EA27: "glyph table", 0x5EA47: "glyph table",
                0x5F013: "glyph table", 0x5F037: "glyph table", 0x5F057: "glyph table"},
}


def _inside(ranges, x):
    """end of the sorted, non-overlapping-start range holding x, or None"""
    i = bisect.bisect_right(ranges, (x, float("inf"))) - 1
    return ranges[i][1] if i >= 0 and ranges[i][0] <= x < ranges[i][1] else None
CODE = ("exe.tsv", "ovl")


@pytest.fixture(scope="module")
def srcs():
    return extract.sources()


@needs_disc
def test_jtext_roundtrip_all_bytes():
    blob = bytes(range(256)) * 2 + "テスト{表}\\l\\k\\c".encode("cp932") + bytes([0x81, 0x40, 0x87, 0x40, 0xFC, 0x40])
    assert jtext.encode(jtext.decode(blob)) == blob


@needs_disc
def test_rows_roundtrip(srcs):
    bad = []
    for s in srcs:
        for r in s.rows:
            if s.encode(r.id, r.jp) != r.raw:
                bad.append(r.id)
        if s.build({r.id: r.jp for r in s.rows}) != s.data:
            bad.append(str(s.tsv))
        if s.build({}) != s.data:
            bad.append(f"{s.tsv} (no edits)")
    assert not bad, bad[:10]


@needs_disc
def test_rows_point_at_their_bytes(srcs):
    bad = [r.id for s in srcs for r in s.rows if s.data[r.off:r.off + len(r.raw)] != r.raw]
    assert not bad, bad[:10]


@needs_disc
def test_coverage(srcs):
    """Every SJIS run (scantext; 3+ characters in code files, 1+ elsewhere) starts inside a row, once moved past
    any structure it starts in (an op's argument bytes, a header table)."""
    missing = []
    for s in srcs:
        rel = str(s.tsv.relative_to(extract.SCRIPT)).replace("\\", "/")
        code = rel.startswith(CODE)
        spans = sorted((r.off, r.off + len(r.raw)) for r in s.rows)
        skip = sorted(s.skip)
        waive = WAIVE.get(rel, {})
        for st, en, text in scantext.spans(s.data, 3 if code else 1):
            if st in waive:
                continue
            while (end := _inside(skip, st)) is not None:
                st = end
            if st >= en:
                continue
            if _inside(spans, st) is None:
                missing.append((rel, hex(st), text[:20]))
    assert not missing, missing[:20]
    for rel, offs in WAIVE.items():
        src = next(s for s in srcs if str(s.tsv.relative_to(extract.SCRIPT)).replace("\\", "/") == rel)
        starts = {st for st, _, _ in scantext.spans(src.data, 3)}
        assert set(offs) <= starts, f"stale waiver in {rel}: {sorted(set(offs) - starts)}"


@needs_disc
def test_tsv_in_sync(srcs):
    """script/ holds exactly the extracted rows, with the same jp (run tools/extract.py after changing a codec)."""
    bad = []
    for s in srcs:
        if not s.rows:
            continue
        got = extract.read_tsv(s.tsv) if s.tsv.exists() else []
        if [(r["id"], r["jp"]) for r in got] != [(r.id, r.jp) for r in s.rows]:
            bad.append(str(s.tsv))
    assert not bad, bad[:10]


@needs_disc
def test_ssb_grow_keeps_jumps():
    """Growing every text row moves code; every jump must still land on the same token it did."""
    for f in sorted((ROOT / "work/lkf/SSB_DATA").glob("*.ssb")):
        data = f.read_bytes()
        toks, _ = ssb.parse(data)
        rows = ssb.rows(data)
        text = {o: raw + "あい".encode("cp932") for o, kind, raw in rows if kind == "text"}
        names = {o: raw + "ア".encode("cp932") for o, kind, raw in rows if kind == "name"}
        grown = ssb.build(data, {**text, **names})
        gt, _ = ssb.parse(grown)
        assert len(grown) == len(data) + 4 * len(text) + 2 * len(names), f.name
        old_ops = [t for t in toks if t[0] == "op" and t[2][0] in ssb.JUMPS]
        new_ops = [t for t in gt if t[0] == "op" and t[2][0] in ssb.JUMPS]
        assert len(old_ops) == len(new_ops), f.name
        at_old = {o: (k, v) for k, o, v in toks}
        at_new = {o: (k, v) for k, o, v in gt}
        for a, b in zip(old_ops, new_ops):
            ia, ib = ssb.JUMPS[a[2][0]], ssb.JUMPS[b[2][0]]
            ta, tb = a[2][1][ia], b[2][1][ib]
            if ta >= len(data):
                continue
            ka, va = at_old[ta]
            kb, vb = at_new[tb]
            assert ka == kb, (f.name, hex(ta), hex(tb))
            if ka == "op":
                assert va[0] == vb[0], (f.name, hex(ta), hex(tb))


@needs_disc
def test_evx_grow_reparses():
    for f in sorted((ROOT / "work/lkf/SSB_DATA").glob("*.EVX")):
        data = f.read_bytes()
        info = evx.parse(data)
        new = {k: s + "あい".encode("cp932") for k, kind, s in info["strings"] if kind not in ("title", "unit")}
        grown = evx.build(data, new)
        again = evx.parse(grown)
        assert [s for _, _, s in again["strings"]] == [new.get(k, s) for k, _, s in info["strings"]], f.name
        for o, size, _ in again["recs"]:
            assert struct.unpack_from("<H", grown, o + 6)[0] == size
