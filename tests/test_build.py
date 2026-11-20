"""Phase 3 identity build: unpack -> re-lay every LKF -> mkpsxiso gives the original .bin byte for byte; a grown entry
re-lays its archive with every other entry intact. Skipped without the dump in rom/ (fresh clone)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build  # noqa: E402
import lkf  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ORIG_BIN.is_file() or not (build.TOOLS / "mkpsxiso.exe").is_file(),
                               reason="no dump in rom/ or no mkpsxiso in tools/")


@needs_rom
def test_identity_build_matches_original():
    out = build.build("identity", relay_all=True)
    assert build.sha1(out) == build.orig_sha1()


@needs_rom
@pytest.mark.parametrize("name", build.ARCHIVES)
def test_grown_entry_relays_archive(name):
    orig = (build.TREE / f"{name}.LKF").read_bytes()
    first = lkf.parse(orig)["entries"][0]["name"]
    blob = dict((e["name"], b) for e, b in lkf.files(orig))
    grown = blob[first] + b"\0" * 0x1800
    new = build.rebuild_lkf(name, {first: grown})
    info = lkf.parse(new)
    assert info["count"] == lkf.parse(orig)["count"]
    assert info["biggest"] == max(len(grown), *(len(b) for b in blob.values()))
    for e, b in lkf.files(new):
        assert e["off"] % lkf.SECTOR == 0
        assert b == (grown if e["name"] == first else blob[e["name"]]), e["name"]
