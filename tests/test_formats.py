"""Container formats: LKF archives rebuild byte for byte; MSG banks parse. Skipped without the unpacked disc."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
TREE = ROOT / "work/disc/tree"

import lkf  # noqa: E402
import msg  # noqa: E402

needs_disc = pytest.mark.skipif(not (TREE / "SSB_DATA.LKF").is_file(), reason="disc not unpacked (work/disc/tree)")


@needs_disc
@pytest.mark.parametrize("name", ["SSB_DATA", "FD2BN", "FD2SN"])
def test_lkf_rebuild_identical(name):
    data = (TREE / f"{name}.LKF").read_bytes()
    payloads = [blob for _, blob in lkf.files(data)]
    assert lkf.build(data, payloads) == data


@needs_disc
def test_msg_banks_parse():
    """All five MSG layouts parse and rebuild byte for byte (msg.py; docs/re/text.md §MSG banks)."""
    kinds = set()
    for e, blob in lkf.files((TREE / "SSB_DATA.LKF").read_bytes()):
        if not e["name"].upper().endswith(".MSG"):
            continue
        bank = msg.parse(e["name"], blob)
        kinds.add(bank.kind)
        assert msg.build(bank) == blob, e["name"]
    assert kinds == {"plain", "reply", "idtab", "names", "battle"}
