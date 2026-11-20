"""msgforce.py: show every entry of the MSG banks in the game's MSG box, for the text coverage gate (phase 8).

    python -X utf8 tools/msgforce.py [BANK.MSG ..] [--all] [--group 1200] [--out-dir work/qa/msgforce] [-j 2]
    python -X utf8 tools/msgforce.py --evx --all --have work/qa/cover --have work/qa/ssbforce --out-dir work/qa/evxforce
    python -X utf8 tools/msgforce.py --ovl --have DIR .. --out-dir work/qa/ovlforce

MSG entries are chosen by game state, so scenes show a few per bank. This runs the warp scene (default `battle`: its
lines open the MSG box) on the ORIGINAL disc with tools/debug/msgforce.lua, which puts each bank's original bytes
at 0x80010000, logs that as a FILE load and chains the box through every entry (docs/re/text.md, MSG box), so
`tools/textcover.py .. work/qa/msgforce` credits them. Banks are chained in groups of --group entries per run
(<out-dir>/<first bank stem>_<k>/<scene>/). --evx: the EVX message items (the battle shows them in the same box).
--ovl: overlay strings still missing, as one slice per overlay; these are menu labels, prompts and quiz answers
whose own widgets the tour sheets judge: this proves only that the game's text path reads and draws them.
Resumable: a bank whose log has "FORCE bank done NAME" is skipped; entries in the --have dirs are not re-forced.
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import evx  # noqa: E402
import msg  # noqa: E402

WARP = ROOT / "tools" / "debug" / "warp.py"
LUA = ROOT / "tools" / "debug" / "msgforce.lua"
SSB = ROOT / "work" / "lkf" / "SSB_DATA"


def banks(ext=".MSG"):
    """{file name (case as on disc): path of the original bytes} for SSB_DATA files with this extension."""
    out = {}
    for p in sorted(SSB.glob("*")):
        name = p.name.split("_", 1)[-1]
        if name.upper().endswith(ext):
            out[name] = p
    return out


def entries(name, data):
    """[(text offset, byte length, row key)] for every text of the file, in file order. MSG: every entry (speakers
    included). EVX: the message items (speaker, text, choice) the battle copies to 0x80189B90 and shows in the same
    box (rfd2 0x800D4414 -> 0x8002E6C0); unit names and the dev-label title are never read (docs/text_unshown.tsv)."""
    out = []
    if name.upper().endswith(".EVX"):
        for key, kind, text in evx.parse(data)["strings"]:
            if kind in ("text", "speaker", "choice") and text:
                out.append((int(key, 16), len(text), f"evx/{Path(name).stem}.{key}"))
        return sorted(out)
    bank = msg.parse(name, data)
    for key, text in bank.strings:
        off = int(key.rstrip("S"), 16)
        if text:
            out.append((off, len(text), f"msg/{Path(name).stem}.{key}"))
    return sorted(out)


OVL_BASE = 0x8009B4B0


def ovl_bank(name, skip):
    """(file name, slice, entries, lo) for the overlay strings of script/ovl/<name>.tsv not in `skip`: the slice of
    the original overlay from the first to the end of the last such string (it must fit below the EXE at
    0x80010000: 0xE000 bytes), entries relative to it."""
    import csv
    data = (ROOT / "work" / "orig_ovl" / f"{name}.bin").read_bytes()
    with open(ROOT / "script" / "ovl" / f"{name}.tsv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    spans = []
    for r in rows:
        if f"ovl/{r['id']}" in skip:
            continue
        o = int(r["id"].split(".")[1], 16) - OVL_BASE
        n = data.index(b"\0", o) - o
        if n:
            spans.append((o, n, f"ovl/{r['id']}"))
    if not spans:
        return None
    lo, hi = min(o for o, _, _ in spans), max(o + n for o, n, _ in spans)
    assert hi - lo <= 0xE000, (name, hex(hi - lo))
    return f"{name}.bin", data[lo:hi], [(o - lo, n, k) for o, n, k in sorted(spans)], lo


def lua_file(group, path):
    """group: [(bank name, data, entries, lo)]."""
    parts = []
    for name, data, ents, lo in group:
        body = "".join(f"\\x{b:02X}" for b in data)
        lst = ",".join(f"{{{o},{n}}}" for o, n, _ in ents)
        parts.append(f'{{name = "{name}", lo = {lo}, data = "{body}", list = {{{lst}}}}}')
    path.write_text("FORCE_AT = 0x80010000\nFORCE_BANKS = {\n" + ",\n".join(parts) + "\n}\n", encoding="ascii")


def banks_done(out):
    """Bank names a log under `out` finished ("FORCE bank done NAME")."""
    got = set()
    for log in out.rglob("log.txt"):
        for line in open(log, encoding="utf-8", errors="replace"):
            if line.startswith("FORCE bank done "):
                got.add(line.split()[3].lower())
    return got


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("banks", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--evx", action="store_true", help="EVX battle files instead of MSG banks")
    ap.add_argument("--ovl", action="store_true", help="overlay strings (rfd2/pro/ed/op) not in --have and not waived "
                    "(docs/text_unshown.tsv), as slices of each overlay")
    ap.add_argument("--out-dir", default="work/qa/msgforce")
    ap.add_argument("--scene", default="battle")
    ap.add_argument("-j", type=int, default=2)
    ap.add_argument("--per-entry", type=int, default=90, help="frames budgeted per entry")
    ap.add_argument("--group", type=int, default=400, help="entries per run (banks are chained in one battle)")
    ap.add_argument("--mash-every", type=int, default=16)
    ap.add_argument("--have", action="append", default=[], help="coverage dirs: skip entries already reached")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    out = ROOT / a.out_dir
    allb = banks(".EVX" if a.evx else ".MSG")
    want = list(allb) if a.all else a.banks
    have = set()
    if a.have:
        import textcover
        files, _ = textcover.load_rows()
        have = textcover.reached([p for d in a.have for p in Path(d).rglob("log.txt")], files)
    fin = banks_done(out) if out.exists() else set()
    groups, cur = [], []
    if a.ovl:
        skip = set(have)
        wp = ROOT / "docs" / "text_unshown.tsv"
        if wp.exists():
            skip |= {ln.split("\t")[0] for ln in wp.read_text(encoding="utf-8").splitlines() if ln[:1] != "#"}
        want = []
        for n in ("rfd2", "pro", "ed", "op"):
            b = ovl_bank(n, skip)
            if b and b[0].lower() not in fin:
                cur.append(b)
    for name in want:
        path = allb.get(name) or next(p for n, p in allb.items() if n.lower() == name.lower())
        name = path.name.split("_", 1)[-1]
        if name.lower() in fin:
            continue
        data = path.read_bytes()
        ents = [e for e in entries(name, data) if e[2] not in have]
        if not ents:
            continue
        if cur and sum(len(g[2]) for g in cur) + len(ents) > a.group:
            groups.append(cur)
            cur = []
        cur.append((name, data, ents, 0))
    if cur:
        groups.append(cur)
    jobs = []
    for g in groups:
        n = sum(len(e[2]) for e in g)
        k = 0
        while (out / f"{Path(g[0][0]).stem}_{k}").exists():
            k += 1
        d = out / f"{Path(g[0][0]).stem}_{k}"
        frames = 14000 + a.per_entry * n
        jobs.append((g, d, frames))
        print(f"{d.name}: {' '.join(b[0] for b in g)}: {n} entries, {frames} frames", flush=True)
    if a.dry:
        return 0

    def run(job):
        g, d, frames = job
        d.mkdir(parents=True, exist_ok=True)
        lua_file(g, d / "_force.lua")
        cmd = [sys.executable, "-X", "utf8", str(WARP), a.scene, "--lua", str(d / "_force.lua"), "--lua", str(LUA),
               "--debugger", "-j", "1", "--frames", str(frames), "--shot-every", "1500",
               "--timeout", str(300 + frames // 60), "--var", f"MASH_EVERY={a.mash_every}", "--out-dir", str(d)]
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        got = banks_done(d)
        ok = all(b[0].lower() in got for b in g)
        print(f"{d.name}: {len(got)}/{len(g)} banks done (warp exit {r.returncode})", flush=True)
        return ok

    with ThreadPoolExecutor(a.j) as ex:
        res = list(ex.map(run, jobs))
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main())
