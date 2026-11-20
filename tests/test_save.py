"""save.py: the game-written fixture card checks out, and an edit keeps the checksum valid. The in-game proof is the
warp scene load_edited (a card edited by save.py lists and loads)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "debug"))

import save  # noqa: E402

CARD = ROOT / "tools" / "debug" / "cards" / "fd2_save.mcd"


def test_fixture_checksum():
    card = bytearray(CARD.read_bytes())
    (slot,) = save.slots(card)
    b = save.base(card, slot)
    assert save.checksum(card, b) == save.stored_sum(card, b)


def test_set_keeps_checksum(tmp_path):
    out = tmp_path / "edited.mcd"
    assert save.main(["set", str(CARD), str(out), "playtime=45296", "month=7", "day=15"]) == 0
    card = bytearray(out.read_bytes())
    b = save.base(card, None)
    f = save.layout()
    assert save.get(card, b, f["playtime"]) == 45296 and save.get(card, b, f["day"]) == 15
    assert save.checksum(card, b) == save.stored_sum(card, b)
    orig = CARD.read_bytes()
    diff = [i for i in range(len(orig)) if orig[i] != card[i]]
    assert all(b <= i < b + save.SUM + 2 for i in diff), "edit wrote outside the save data"


def test_system_file(tmp_path):
    out = tmp_path / "clear.mcd"
    assert save.main(["system", str(CARD), str(out), "clears=1,2,3,4,5,6,7", "time=100"]) == 0
    card = bytearray(out.read_bytes())
    ents = {name: i for i, st, _s, _n, name, ok in save.mcd.entries(card) if st == 0x51 and ok}
    slot = ents[save.SYS_NAME]
    b = slot * save.mcd.BLOCK + save.DATA
    assert save.checksum(card, b) == save.stored_sum(card, b)
    assert card[b:b + save.SYS_SIZE] == save.system_data(100, (1, 2, 3, 4, 5, 6, 7))
    assert save.mcd.title(card, slot) == save.SYS_TITLE
    # a second write rewrites the same file instead of adding another
    assert save.main(["system", str(out), str(out), "clears=0,0,0,0,0,0,0"]) == 0
    card2 = out.read_bytes()
    assert [n for _i, st, _s, _x, n, _o in save.mcd.entries(card2) if n == save.SYS_NAME] == [save.SYS_NAME]
    assert card2[b + 4:b + 11] == bytes(7)


def test_system_file_matches_game_written():
    """fd2_cleared.mcd = fd2_sys0.mcd (save.py system, nothing cleared) after the game's own clear save (scene
    end_cecia_clear): rebuilding .0 from its struct gives the game's bytes exactly."""
    cleared = (ROOT / "tools" / "debug" / "cards" / "fd2_cleared.mcd").read_bytes()
    slot = {n: i for i, st, _s, _x, n, _o in save.mcd.entries(cleared) if st == 0x51}[save.SYS_NAME]
    blk = slot * save.mcd.BLOCK
    struct_bytes = cleared[blk + save.DATA:blk + save.DATA + save.SYS_SIZE]
    card = bytearray(CARD.read_bytes())
    assert save.put_system(card, struct_bytes) == slot
    assert card[blk:blk + save.mcd.BLOCK] == cleared[blk:blk + save.mcd.BLOCK]
    assert card[slot * 128:slot * 128 + 128] == cleared[slot * 128:slot * 128 + 128]
