"""STR v2 codec (tools/mdec.py): parse + reassemble gives the original frame bytes (end code and padding included:
a frame without the 0x1FF end code stops the game's movie player), and a re-encoded macroblock decodes close to
its source pixels."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import mdec  # noqa: E402

TREE = Path(__file__).resolve().parents[1] / "work/disc/tree"
pytestmark = pytest.mark.skipif(not (TREE / "DEMO.STR").is_file(), reason="work/disc/tree not unpacked")


@pytest.mark.parametrize("name", ["DEMO.STR", "ENDING.STR"])
def test_roundtrip_bytes(name):
    data = (TREE / name).read_bytes()
    fr = mdec.frames(data)
    for n in sorted(fr)[::300]:
        f = fr[n]
        raw = mdec.frame_data(data, f)
        hdr, blocks = mdec.parse(raw, f["w"], f["h"])
        out = mdec.assemble(hdr["q"], [(b["bits"], mdec.codes_of(b)) for b in blocks])
        assert out == raw[:f["size"]] and not any(raw[f["size"]:]), f"{name} frame {n}"


def test_reencode_macroblock():
    data = (TREE / "DEMO.STR").read_bytes()
    f = mdec.frames(data)[400]
    raw = mdec.frame_data(data, f)
    Y, Cb, Cr = mdec.decode(raw, f["w"], f["h"])
    rgb = mdec.to_rgb(Y, Cb, Cr, f["w"], f["h"]).astype(float)
    rgb[32:48, 64:80] = (250, 240, 200)   # one flat macroblock (4, 2)
    Y2, Cb2, Cr2 = mdec.from_rgb(rgb)
    new, floor = mdec.rebuild(raw, f["w"], f["h"], Y2, Cb2, Cr2, {(4, 2)}, len(f["sectors"]) * mdec.CHUNK_DATA)
    assert floor == 0
    got = mdec.to_rgb(*mdec.decode(new, f["w"], f["h"]), f["w"], f["h"]).astype(int)
    assert np.abs(got[32:48, 64:80] - [250, 240, 200]).max() <= 6
    old = mdec.to_rgb(Y, Cb, Cr, f["w"], f["h"]).astype(int)
    assert (got[:32] == old[:32]).all() and (got[48:] == old[48:]).all()   # other macroblocks untouched
