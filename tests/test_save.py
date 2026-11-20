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
