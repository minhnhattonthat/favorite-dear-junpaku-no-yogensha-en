"""Container formats: LKF archives rebuild byte for byte; MSG banks parse. Skipped without the unpacked disc."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
TREE = ROOT / "work/disc/tree"

import lkf  # noqa: E402

needs_disc = pytest.mark.skipif(not (TREE / "SSB_DATA.LKF").is_file(), reason="disc not unpacked (work/disc/tree)")


@needs_disc
@pytest.mark.parametrize("name", ["SSB_DATA", "FD2BN", "FD2SN"])
def test_lkf_rebuild_identical(name):
    data = (TREE / f"{name}.LKF").read_bytes()
    payloads = [blob for _, blob in lkf.files(data)]
    assert lkf.build(data, payloads) == data


@needs_disc
@pytest.mark.xfail(reason="BrvMsgQ* entries have a sub-structure not decoded yet (docs/re/text.md); phase 4", strict=False)
def test_msg_banks_parse():
    for e, blob in lkf.files((TREE / "SSB_DATA.LKF").read_bytes()):
        if not e["name"].upper().endswith(".MSG"):
            continue
        first = struct.unpack_from("<H", blob, 0)[0]
        offs = [struct.unpack_from("<H", blob, i)[0] for i in range(0, first, 2)]
        for i, o in enumerate(offs):
            # an entry is one or more (u16 length, text) parts filling the space up to the next entry
            nxt = offs[i + 1] if i + 1 < len(offs) else len(blob)
            p = o
            while p < nxt:
                n = struct.unpack_from("<H", blob, p)[0]
                blob[p + 2:p + 2 + n].decode("cp932")
                p += 2 + n
            assert p == nxt, (e["name"], i)
