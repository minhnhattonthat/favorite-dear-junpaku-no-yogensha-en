"""The dump in rom/ matches rom.sha1 (skipped when rom/ is absent, e.g. on a fresh clone)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_rom  # noqa: E402


@pytest.mark.skipif(not any((ROOT / "rom").glob("*.bin")), reason="no dump in rom/")
def test_rom_matches_sha1():
    check_rom.check()
