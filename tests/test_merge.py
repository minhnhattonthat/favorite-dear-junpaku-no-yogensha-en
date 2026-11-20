"""merge keys translations by (id, JP), the script/ text lint, and rows whose bytes the game code edits."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import batches as B  # noqa: E402
import extract  # noqa: E402
import font_en  # noqa: E402


def row(path, i):
    return next(r for r in extract.read_tsv(ROOT / "script" / path) if r["id"] == i)


def test_shared_id_keeps_its_own_text():
    """roev07.0156 is an ssb line and an EVX unit name; the unit name once overwrote the line (phase 7 review)"""
    assert row("ssb/roev07.tsv", "roev07.0156")["en"] == "What's that?{wait}{clear}"
    assert row("evx/roev07.tsv", "roev07.0156")["en"] == "The Boy"


def test_compatibility_tail():
    """rfd2 0x800CF14C copies the hero's name over the LAST 14 BYTES of T_Msg01 messages 8-23 and appends
    rfd2.8009D9E4 (ね。 in the JP): the English must end with ＜勇者名＞ plus exactly 4 bytes of filler."""
    rows = extract.read_tsv(ROOT / "script/msg/T_Msg01.tsv")[8:24]
    tag = "＜勇者名＞".encode("cp932")
    for r in rows:
        assert r["jp"].endswith("＜勇者名＞ね。"), r["id"]
        b = extract.jtext.encode(font_en.to_pairs(r["en"]))
        assert b[-14:-4] == tag and b"\\" not in b[-4:], (r["id"], b[-14:])
    assert row("ovl/rfd2.tsv", "rfd2.8009D9E4")["en"].strip() == ""   # odd-length names end in a space


def test_unit_names_are_names():
    p = ROOT / "script/evx/roev07.tsv"
    assert B.wrap_spec(p, {"notes": "unit name (32-byte field)"}) is None
