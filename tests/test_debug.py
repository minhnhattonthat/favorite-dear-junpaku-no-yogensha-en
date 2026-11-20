"""Debug warp: scenes.tsv parses (column count, unique names, known kinds) and every file it names is on the disc.
The warp runs themselves are slow emulator runs: `python -X utf8 tools/debug/warp.py --all`."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "debug"))
sys.path.insert(0, str(ROOT / "tools"))

import warp  # noqa: E402

KINDS = {"title", "event", "swap", "battle", "ending"}


def test_scenes_parse():
    scenes = warp.load_scenes()
    assert scenes, "scenes.tsv is empty"
    for s in scenes.values():
        assert s["kind"] in KINDS, s
        assert s["after"] in ("", "mash", "hold"), s
        assert (ROOT / (s["card"] or warp.DEFAULT_CARD)).is_file() or s["card"] == "blank", s


@pytest.mark.skipif(not Path(warp.SSB_LKF).is_file(), reason="disc not unpacked (work/disc/tree)")
def test_scene_files_exist():
    for s in warp.load_scenes().values():
        if s["kind"] in ("event", "swap", "battle"):
            warp.lua_vars(s)  # exits on an unknown name


@pytest.mark.skipif(not Path(warp.EXE).is_file(), reason="disc not unpacked (work/disc/tree)")
def test_battle_ids_in_table():
    table = warp.battle_table()
    assert len(table) == 150 and table[0]["id"] == 3000
    ids = {b["id"] for b in table}
    for s in warp.load_scenes().values():
        if s["kind"] == "battle" and s["arg"]:
            hero, _, bid = s["arg"].partition(":")
            assert 0 <= int(hero) <= 6, s
            assert not bid or int(bid) in ids, s
