"""qa_sheets.py: post-arrival contact sheets for the visual-QA gate.

    python -X utf8 tools/qa_sheets.py work/qa/tour [SCENE..] [--before 300] [--changed 0.02]

For each scene folder written by tools/debug/warp.py, finds the arrival frame ("WARP arrived fNNN" in log.txt) and
writes qa_sheet.png (+ qa_sheet_2.png ...) from the frames after (arrival - BEFORE), dropping near-duplicate frames,
at full size (--div 1, 3x3 per page) so dialogue is readable. The 6000-frame boot (logos, DEMO.STR) is left out:
it is the same in every run and judged once in the `title` scene. Then:

    qa_gate.py init work/qa/manifest.tsv work/qa/tour --build build/fd2_en.bin --glob "qa_sheet*.png"
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill import SKILL  # noqa: E402


def arrival(folder: Path):
    log = folder / "log.txt"
    if not log.exists():
        return None
    m = re.search(r"WARP arrived f(\d+)", log.read_text(encoding="utf-8", errors="replace"))
    return int(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tour")
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--before", type=int, default=300)
    ap.add_argument("--changed", default="0.02")
    a = ap.parse_args()
    tour = Path(a.tour)
    folders = [tour / s for s in a.scenes] if a.scenes else sorted(p for p in tour.iterdir() if p.is_dir())
    bad = 0
    for f in folders:
        for old in f.glob("qa_sheet*.png"):
            old.unlink()
        arr = arrival(f)
        lo = 0 if arr is None else max(0, arr - a.before)
        cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), str(f), "--from", str(lo),
               "--changed", a.changed, "--div", "1", "--cols", "3", "--max", "9", "--out", str(f / "qa_sheet.png")]
        r = subprocess.run(cmd, capture_output=True, text=True)
        n = len(list(f.glob("qa_sheet*.png")))
        print(f"{f.name}\tarrived={arr}\tpages={n}" + ("" if r.returncode == 0 else f"\tERROR {r.stderr.strip()[-200:]}"))
        bad += r.returncode != 0 or arr is None
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
