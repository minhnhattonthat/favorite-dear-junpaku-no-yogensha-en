"""warp.py: boot the disc cold and land on a scene from tools/debug/scenes.tsv (no save, no savestate).

    python -X utf8 tools/debug/warp.py SCENE [SCENE..] [--cue build/fd2_en.cue] [-j 3] [--state]
    python -X utf8 tools/debug/warp.py --all [-j 3] [--state]      every scene (shots + optional states)
    python -X utf8 tools/debug/warp.py --event ceev04.ssb          any event script by its SSB_DATA name
    python -X utf8 tools/debug/warp.py --list

Each run writes work/qa/warp/<scene>/ (shots every 150 frames, sheet.png, arrived.png, log.txt, emu.txt) and, with
--state, work/states/<scene>.sstate (60 frames after arrival, or after POST). Exit 1 if any scene was not reached
("WARP OK" missing in the log), its proof shot is blank, or (AFTER=mash) the screen never changed after arrival.
Results are appended to work/qa/warp/results.tsv (--out-dir D: D/<scene>/ and D/results.tsv instead). Lua side: tools/debug/warp.lua; how it works: docs/re/debug.md.

scenes.tsv columns:
  scene   name (also the output folder and state name)
  kind    title | event | swap | battle | ending (map -> ed.bin, the staff roll movie)
  arg     kind event: the .ssb to run in place of prologue.ssb; kind swap: HOST=TARGET[@BUF] (when the game loads
          HOST, it gets TARGET; arrival = TARGET's bytes at BUF, default the script buffer); kind battle:
          HERO[:ID] (hero index 0-6, battle id 3000+n from the exe's battle table; empty = the default encounter);
          kind title: optional .ssb to run once POST is done (after loading a save: the event then runs on the
          loaded game file); kind ending: the byte ed.bin branches on (0x8007F17A; 0x10 = game over; empty = the game's value)
  host    kind swap: the event that loads HOST (run in place of prologue.ssb first); else empty
  after   mash (default: circle every 45 frames after arrival) | hold
  frames  run length (default 16000)
  card    memory card image (repo-relative) the run gets a fresh copy of (so no run sees another's saves);
          empty = tools/debug/cards/fd1_clear.mcd, the first game's clear data only. New Game asks to import it,
          and the route answers yes (with a card without it the game loops on "insert the card"); 'blank' = a
          formatted empty card
  post    presses after arrival, route steps joined by ';' (shot post.png when done)
  proof   frames from arrival to arrived.png (default 30)
  note    what the scene shows
"""
import argparse
import csv
import glob
import os
import struct
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools"))
from skill import SKILL  # noqa: E402
import lkf  # noqa: E402

sys.path.insert(0, HERE)
import mcd  # noqa: E402

sys.path.insert(0, os.path.join(SKILL, "scripts"))
import sheet  # noqa: E402

ORIG_CUE = os.path.join(REPO, "rom", "Favorite Dear - Junpaku no Yogensha (Japan).cue")
SSB_LKF = os.path.join(REPO, "work", "disc", "tree", "SSB_DATA.LKF")
EXE = os.path.join(REPO, "work", "disc", "tree", "SLPS_027.54")
EXE_BASE = 0x8001F800   # RAM address of file offset 0 (text 0x80020000 at 0x800)
SCENES = os.path.join(HERE, "scenes.tsv")
COLS = ["scene", "kind", "arg", "host", "after", "frames", "card", "post", "proof", "note"]
SCRIPT_BUF = 0x801A4BB0
DEFAULT_CARD = "tools/debug/cards/fd1_clear.mcd"
EXTRA = []
SHOT_EVERY = 150
OUT_ROOT = os.path.join(REPO, "work", "qa", "warp")
_files = None


def lkf_file(name):
    """Bytes of an SSB_DATA.LKF entry by name (from the unpacked disc: work/disc/tree)."""
    global _files
    if _files is None:
        _files = {e["name"]: b for e, b in lkf.files(open(SSB_LKF, "rb").read())}
    if name not in _files:
        sys.exit(f"{name}: not in SSB_DATA.LKF (names are case-sensitive; lkf.py list shows them)")
    return _files[name]


def battle_table():
    """The exe's battle table (0x8006EB30, 14-byte rows, ends at a row whose first u16 >= 999): what Battle.bin's
    setup looks the id at 0x80081014 up in. Fields after id: guesses (docs/re/debug.md §Battle)."""
    d = open(EXE, "rb").read()
    out, a = [], 0x8006EB30 - EXE_BASE
    while True:
        n, bid, b4, b5, w6, w8, wa, wc = struct.unpack_from("<HHBBHHHH", d, a)
        if n >= 999:
            return out
        out.append({"n": n, "id": bid, "b4": b4, "b5": b5, "w6": w6, "w8": w8, "wa": wa, "wc": wc})
        a += 14


def sig(name):
    """(offset, hex) of 16 bytes from the file's middle: every script starts with the same header bytes."""
    b = lkf_file(name)
    o = max(0, min((len(b) // 2) & ~3, len(b) - 16))
    return o, b[o:o + 16].hex()


def load_scenes():
    with open(SCENES, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.reader(f, delimiter="\t") if r and not r[0].startswith("#")]
    head, rows = rows[0], rows[1:]
    assert head == COLS, f"scenes.tsv header {head} != {COLS}"
    out = {}
    for r in rows:
        assert len(r) == len(COLS), f"scenes.tsv row has {len(r)} columns, want {len(COLS)}: {r}"
        d = dict(zip(COLS, r))
        assert d["scene"] not in out, f"duplicate scene {d['scene']}"
        out[d["scene"]] = d
    return out


def frame_of(log, tag):
    for line in log.splitlines():
        if line.startswith(tag):
            return int(line.rsplit(" f", 1)[1])
    return None


def lua_vars(sc):
    kind = sc["kind"]
    v = [f"KIND='{kind}'", f"AFTER='{sc['after'] or 'mash'}'"]
    if kind == "event":
        o, h = sig(sc["arg"])
        v += [f"EVENT='{sc['arg']}'", f"SIG='{h}'", f"SIGOFF={o}", f"SIGBUF={SCRIPT_BUF}"]
    elif kind == "swap":
        pair, _, buf = sc["arg"].partition("@")
        host, target = pair.split("=")
        o, h = sig(target)
        v += [f"EVENT='{sc['host']}'", f"SWAP_HOST='{host}'", f"SWAP_TARGET='{target}'", f"SIG='{h}'",
              f"SIGOFF={o}", f"SIGBUF={int(buf, 16) if buf else SCRIPT_BUF}"]
    elif kind in ("battle", "ending"):
        o, h = sig("TheEnd.ssb")
        v += ["EVENT='TheEnd.ssb'", f"SIG='{h}'", f"SIGOFF={o}", f"SIGBUF={SCRIPT_BUF}"]
        if sc["arg"] and kind == "ending":
            v.append(f"ENDING={int(sc['arg'], 0)}")
        elif sc["arg"]:
            hero, _, bid = sc["arg"].partition(":")
            v += [f"HERO={int(hero)}"] + ([f"BATTLE={int(bid)}"] if bid else [])
    elif kind == "title" and sc["arg"]:
        lkf_file(sc["arg"])  # exits on an unknown name
        v.append(f"RUN_EVENT={list(_files).index(sc['arg'])}")
    if sc.get("post"):
        v.append(f"POST='{sc['post']}'")
    if sc.get("proof"):
        v.append(f"PROOF={int(sc['proof'])}")
    return v


def card_for(sc, out):
    """The memory card for this run: the scene's card, or a blank formatted one (emu.py copies it again)."""
    dst = os.path.join(out, "card.mcd")
    card = sc.get("card") or DEFAULT_CARD
    if card == "blank":
        with open(dst, "wb") as g:
            g.write(mcd.blank())
    else:
        src = os.path.join(REPO, card)
        assert os.path.exists(src), f"{sc['scene']}: card {src} missing"
        with open(src, "rb") as f, open(dst, "wb") as g:
            g.write(f.read())
    return dst


def run(sc, cue, state, timeout):
    out = os.path.join(OUT_ROOT, sc["scene"])
    os.makedirs(out, exist_ok=True)
    for f in glob.glob(os.path.join(out, "*.png")):
        os.remove(f)
    lua = lua_vars(sc)
    if state:
        p = os.path.join(REPO, "work", "states", sc["scene"] + ".sstate").replace("\\", "/")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        lua.append(f"STATE='{p}'")
    cmd = [sys.executable, "-X", "utf8", os.path.join(SKILL, "scripts", "emu.py"), os.path.abspath(cue),
           "--out", out, "--script", os.path.join(HERE, "warp.lua"), "--frames", sc["frames"] or "16000",
           "--shot-every", str(SHOT_EVERY), "--timeout", str(timeout), "--sav", card_for(sc, out)]
    for v in lua:
        cmd += ["--var", v]
    cmd += EXTRA
    with open(os.path.join(out, "emu.txt"), "w", encoding="utf-8") as fo:
        rc = subprocess.call(cmd, stdout=fo, stderr=subprocess.STDOUT)
    logp = os.path.join(out, "log.txt")
    log = open(logp, encoding="utf-8", errors="replace").read() if os.path.exists(logp) else ""
    ok_at = frame_of(log, "WARP OK")
    verdict, distinct = "ok", 0
    if rc != 0:
        verdict = f"emu exit {rc}"
    elif ok_at is None:
        verdict = "not reached"
    else:
        shots = sorted(f for f in os.listdir(out) if f[0] == "f" and f[1:7].isdigit() and f.endswith(".png")
                       and int(f[1:7]) >= ok_at + 150)
        seen = []
        for f in shots:
            im = sheet.read_png(os.path.join(out, f))
            if not any(sheet.diff(im, s) < 0.002 for s in seen):
                seen.append(im)
        distinct = len(seen)
        if (sc["after"] or "mash") == "mash" and distinct < 2:
            verdict = "stuck"
        proof = os.path.join(out, "post.png" if sc.get("post") else "arrived.png")
        if not os.path.exists(proof):
            verdict = "no " + os.path.basename(proof)
        elif sheet.is_blank(sheet.read_png(proof)):
            verdict = "blank"
        sheet.make(out, lo=max(0, ok_at - 300), limit=16, changed=0.002)
    return sc["scene"], verdict, ok_at, distinct


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--event", action="append", default=[], help="ad-hoc event by SSB_DATA name (ceev04.ssb)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--cue", default=ORIG_CUE)
    ap.add_argument("--state", action="store_true", help="also save work/states/<scene>.sstate")
    ap.add_argument("-j", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--frames", help="override every scene's run length")
    ap.add_argument("--lua", action="append", default=[], help="extra Lua hook appended after warp.lua (repeatable)")
    ap.add_argument("--var", action="append", default=[], help="extra NAME=LUA global (repeatable)")
    ap.add_argument("--debugger", action="store_true", help="interpreter mode (needed for L.on_exec hooks)")
    ap.add_argument("--shot-every", type=int, default=150, help="frames between shots (default 150)")
    ap.add_argument("--out-dir", help="folder for the scene folders and results.tsv (default work/qa/warp)")
    a = ap.parse_args()
    global SHOT_EVERY, OUT_ROOT
    SHOT_EVERY = a.shot_every
    if a.out_dir:
        OUT_ROOT = os.path.abspath(a.out_dir)
    for f in a.lua:
        EXTRA.extend(["--script", os.path.abspath(f)])
    for v in a.var:
        EXTRA.extend(["--var", v])
    if a.debugger:
        EXTRA.append("--debugger")
    table = load_scenes()
    if a.list:
        for s in table.values():
            print(f"{s['scene']:<18} {s['kind']:<6} {s['arg']:<28} {s['note']}")
        return 0
    todo = list(table.values()) if a.all else []
    for name in a.scenes:
        if name not in table:
            sys.exit(f"unknown scene {name}; --list shows them")
        todo.append(table[name])
    for ev in a.event:
        todo.append({"scene": "ev_" + ev.rsplit(".", 1)[0], "kind": "event", "arg": ev, "host": "", "after": "mash",
                     "frames": "16000", "card": "", "post": "", "proof": "", "note": ""})
    if not todo:
        ap.error("name a scene, --event NAME or --all")
    if a.frames:
        todo = [dict(s, frames=a.frames) for s in todo]
    for s in todo:
        lua_vars(s)  # fail on an unknown file name before any emulator starts
    with ThreadPoolExecutor(max_workers=a.j) as ex:
        res = list(ex.map(lambda s: run(s, a.cue, a.state, a.timeout), todo))
    os.makedirs(OUT_ROOT, exist_ok=True)
    with open(os.path.join(OUT_ROOT, "results.tsv"), "a", encoding="utf-8") as f:
        for r in res:
            f.write("\t".join(str(x) for x in r) + "\n")
    bad = 0
    for name, verdict, at, distinct in res:
        print(f"{name:<18} {verdict:<12} arrived f{at}  distinct shots after arrival: {distinct}")
        bad += verdict != "ok"
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
