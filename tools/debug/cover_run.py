"""cover_run.py: resumable textcover runs over every ssb event (phase 8 coverage gate).

    python -X utf8 tools/debug/cover_run.py [--out-dir work/qa/cover] [-j 2] [--chunk 4] [--only a,b] [--dry]

Calls `warp.py --event X.ssb --lua tools/debug/textcover.lua --debugger` on the ORIGINAL disc in chunks, so a
killed run (low memory) loses at most one chunk. An event counts as done when its folder's log.txt has
"final frame" and a " size=" FILE line (older textcover logs lack it and are re-run). Run length grows with the
event's row count (16000 / 21000 / 27000 frames). Report: `python -X utf8 tools/textcover.py work/qa/cover ...`.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WARP = ROOT / "tools" / "debug" / "warp.py"
LUA = ROOT / "tools" / "debug" / "textcover.lua"


def done(folder):
    log = folder / "log.txt"
    if not log.exists():
        return False
    t = log.read_text(encoding="utf-8", errors="replace")
    return "final frame" in t and " size=" in t


def frames_for(rows):
    return 16000 if rows < 40 else 21000 if rows < 90 else 27000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="work/qa/cover")
    ap.add_argument("-j", type=int, default=2)
    ap.add_argument("--chunk", type=int, default=4)
    ap.add_argument("--only", default="")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    out = ROOT / a.out_dir
    only = {s.lower() for s in a.only.split(",") if s}
    todo = {}
    for tsv in sorted((ROOT / "script" / "ssb").glob("*.tsv")):
        stem = tsv.stem
        if only and stem.lower() not in only:
            continue
        if done(out / f"ev_{stem}"):
            continue
        rows = sum(1 for _ in tsv.open(encoding="utf-8")) - 1
        todo.setdefault(frames_for(rows), []).append(stem)
    n = sum(len(v) for v in todo.values())
    print(f"{n} events to run", flush=True)
    for frames, stems in sorted(todo.items()):
        for i in range(0, len(stems), a.chunk):
            part = stems[i:i + a.chunk]
            cmd = [sys.executable, "-X", "utf8", str(WARP), "--lua", str(LUA), "--debugger", "-j", str(a.j),
                   "--frames", str(frames), "--shot-every", "600", "--timeout", "1500", "--out-dir", str(out)]
            for s in part:
                cmd += ["--event", s + ".ssb"]
            print(" ".join(part), frames, flush=True)
            if not a.dry:
                subprocess.run(cmd, cwd=ROOT)
    left = [s for v in todo.values() for s in v if not done(out / f"ev_{s}")]
    print(f"left: {len(left)}", " ".join(left[:40]), flush=True)


if __name__ == "__main__":
    main()
