"""ssbforce.py: play the event-script rows no coverage run reached (phase 8 text coverage gate).

    python -X utf8 tools/ssbforce.py --have work/qa/cover [--have DIR ..] [--out-dir work/qa/ssbforce] [-j 2]
                                     [--only a,b] [--dry]

For each script/ssb file with rows not reached in the --have dirs, runs `warp.py --event NAME.ssb` on the ORIGINAL
disc with tools/debug/textcover.lua (logging) and tools/debug/ssbforce.lua, which moves the script VM to each
missing row whenever the script would end or loop (docs/re/events.md, VM context). Choice-answer rows (《..》) are
never jump targets: jumping into a choice's text outside its op would print it as plain text. Report afterwards:
`python -X utf8 tools/textcover.py work/qa/cover work/qa/ssbforce ...`. Resumable: an event whose folder log has
"SFORCE done" is skipped. Second pass: a NEW --out-dir (a run overwrites its event's folder and so the reads it
logged), the first pass as --have, and a larger --base for events that go into a battle.
"""
import argparse
import csv
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import textcover  # noqa: E402

WARP = ROOT / "tools" / "debug" / "warp.py"
COVER = ROOT / "tools" / "debug" / "textcover.lua"
FORCE = ROOT / "tools" / "debug" / "ssbforce.lua"


def rows_of(stem):
    with open(ROOT / "script" / "ssb" / f"{stem}.tsv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def done(d):
    log = d / "log.txt"
    return log.exists() and "SFORCE done" in log.read_text(encoding="utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--have", action="append", default=[])
    ap.add_argument("--out-dir", default="work/qa/ssbforce")
    ap.add_argument("-j", type=int, default=2)
    ap.add_argument("--only", default="")
    ap.add_argument("--per-row", type=int, default=250, help="frames budgeted per wanted row")
    ap.add_argument("--base", type=int, default=14000, help="frames before the first forced row (arrival ~10050; "
                    "events with a battle need ~30000)")
    ap.add_argument("--skip-battles", action="store_true", help="step over `01 1c N`, N >= 2000 (op 0x1c queues an "
                    "event id; 2xxx/3xxx start battles, which a mash run can lose or never end) so the rows after play")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    out = ROOT / a.out_dir
    files, _ = textcover.load_rows()
    have = textcover.reached([p for d in a.have for p in Path(d).rglob("log.txt")], files)
    only = {s.lower() for s in a.only.split(",") if s}
    jobs = []
    for tsv in sorted((ROOT / "script" / "ssb").glob("*.tsv")):
        stem = tsv.stem
        if (only and stem.lower() not in only) or done(out / f"ev_{stem}"):
            continue
        data = textcover.orig_bytes(f"{stem}.ssb".lower())
        spans = files[f"{stem}.ssb".lower()][1]
        jp = {r["id"]: r["jp"] for r in rows_of(stem)}
        rows, want = [], 0
        for s, e, key in spans:
            rid = key.split("/", 1)[1]
            w = int(key not in have and not jp[rid].startswith("《"))
            rows.append((s, e, w))
            want += w
        if not want:
            continue
        sig = [(o, data[o]) for o in range(0x10, len(data), max(1, len(data) // 16))]
        gen = out / "_lua" / f"{stem}.lua"
        gen.parent.mkdir(parents=True, exist_ok=True)
        gen.write_text(f'SF_NAME = "{stem}.ssb"\nSF_ROWS = {{' + ",".join(f"{{{s},{e},{w}}}" for s, e, w in rows)
                       + "}\nSF_SIG = {" + ",".join(f"{{{o},{b}}}" for o, b in sig) + "}\n"
                       + ("SF_SKIPBATTLE = true\n" if a.skip_battles else ""), encoding="ascii")
        jobs.append((stem, gen, a.base + a.per_row * want, want))
    print(f"{len(jobs)} events, {sum(j[3] for j in jobs)} rows wanted", flush=True)
    if a.dry:
        for stem, _, frames, want in jobs:
            print(stem, want, frames)
        return 0
    def run(job):
        stem, gen, frames, want = job
        cmd = [sys.executable, "-X", "utf8", str(WARP), "--event", f"{stem}.ssb", "--lua", str(COVER),
               "--lua", str(gen), "--lua", str(FORCE), "--debugger", "-j", "1", "--frames", str(frames),
               "--shot-every", "1500", "--timeout", str(300 + frames // 60), "--out-dir", str(out)]
        subprocess.run(cmd, cwd=ROOT, capture_output=True)
        log = out / f"ev_{stem}" / "log.txt"
        t = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
        print(f"{stem}: {want} wanted, {'done' if 'SFORCE done' in t else 'not done'}", flush=True)

    with ThreadPoolExecutor(a.j) as ex:
        list(ex.map(run, jobs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
