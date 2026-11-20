"""textcover.reached: reads count only when the byte matches the original file, on enough distinct offsets, and
a newer non-text file over the buffer ends the old file's mapping."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import textcover as T  # noqa: E402

DST = 0x801203E0
DATA = bytes(range(0x40, 0x80))
FILES = {"test.msg": ([0x10, 0x20], [(0x10, 0x18, "msg/TEST.0010"), (0x20, 0x28, "msg/TEST.0020")])}


def run(tmp_path, lines):
    T._ORIG.clear()
    T._ORIG["test.msg"] = DATA
    T._ORIG["x"] = None  # keep the cache from scanning work/
    log = tmp_path / "log.txt"
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        return T.reached([log], FILES)
    finally:
        T._ORIG.clear()


def reads(offs, value=None):
    return [f"TREAD {DST + o:08X} {DATA[o] if value is None else value:02X}" for o in offs]


def test_whole_row_read(tmp_path):
    hit = run(tmp_path, [f"FILE f1 TEST.MSG dst={DST:08X} size=40", *reads(range(0x10, 0x18))])
    assert hit == {"msg/TEST.0010"}


def test_wrong_bytes_do_not_count(tmp_path):
    hit = run(tmp_path, [f"FILE f1 TEST.MSG dst={DST:08X} size=40", *reads(range(0x20, 0x28), value=0)])
    assert hit == set()


def test_same_offset_twice_is_one(tmp_path):
    lines = [f"FILE f1 TEST.MSG dst={DST:08X} size=40", *reads([0x10]),
             f"FILE f2 TEST.MSG dst={DST:08X} size=40", *reads([0x10])]
    assert run(tmp_path, lines) == set()


def test_newer_image_ends_mapping(tmp_path):
    lines = [f"FILE f1 TEST.MSG dst={DST:08X} size=40", f"FILE f2 pic.tim dst={DST:08X} size=8000",
             *reads(range(0x10, 0x18))]
    assert run(tmp_path, lines) == set()


def test_old_logs_without_values(tmp_path):
    hit = run(tmp_path, [f"FILE f1 TEST.MSG dst={DST:08X}", f"TREAD {DST + 0x21:08X}"])
    assert hit == {"msg/TEST.0020"}
