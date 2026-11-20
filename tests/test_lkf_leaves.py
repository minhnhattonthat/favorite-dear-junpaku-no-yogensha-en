"""Rebuilt LKF archives (SSB/MSG/EVX/END payloads) keep the original entry set: same names, flags and order; an
entry differs from the original only if insert.py changed it, and then it holds exactly insert's bytes (skill
§Checks: compare decoded leaves of re-laid archives)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

TREE = ROOT / "work" / "disc" / "tree"


@pytest.mark.skipif(not (TREE / "FD2SN.LKF").is_file(), reason="unpacked disc not present")
def test_lkf_leaves():
    import build
    import codetext
    import insert
    import lkf
    changes, _, _ = insert.changes("en", heap=codetext.Heap())
    assert changes, "no LKF changes"
    for arc, ch in changes.items():
        orig = (TREE / f"{arc}.LKF").read_bytes()
        new = build.rebuild_lkf(arc, ch)
        eo, en = lkf.parse(orig)["entries"], lkf.parse(new)["entries"]
        assert [(e["name"], e["flags"]) for e in eo] == [(e["name"], e["flags"]) for e in en], arc
        for a, b in zip(eo, en):
            old = orig[a["off"]:a["off"] + a["size"]]
            got = new[b["off"]:b["off"] + b["size"]]
            if a["name"] in ch:
                assert got == ch[a["name"]] and got != old, (arc, a["name"])
            else:
                assert got == old, (arc, a["name"])
