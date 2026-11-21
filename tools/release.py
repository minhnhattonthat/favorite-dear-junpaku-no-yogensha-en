"""release.py: build, gate and package a release (xdelta patch + README.txt in a zip).

    python -X utf8 tools/release.py [--version 1.0] [--force]

Stops at the first failure: build -> tests + lint (tools/check.py) -> smoke boot -> leftover Japanese
(tools/jpcheck.py) -> qa_gate.py check on every work/qa/**/manifest.tsv (visual tour, stress, story pass) ->
textcover.py over the coverage runs -> no unticked line in docs/polish.md -> no template placeholder in README.md ->
debug tool off -> xdelta patch -> re-apply the patch to the original and compare -> zip.
Output: release/Favorite_Dear_Junpaku_no_Yogensha_EN_v<version>.zip (patch + README.txt); the playable image stays
in build/. An existing version is never overwritten without --force. Publishing is the owner's call.
"""
import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

ORIG_NAME = "Favorite Dear - Junpaku no Yogensha (Japan)"
ORIG_BIN = ROOT / "rom" / f"{ORIG_NAME}.bin"
BUILT_BIN = ROOT / "build" / "fd2_en.bin"
BUILT_CUE = ROOT / "build" / "fd2_en.cue"
XDELTA = ROOT / "tools" / "xdelta" / "xdelta3-3.1.0-x86_64.exe"
OUT = ROOT / "release"
SCRIPTS = Path(SKILL) / "scripts"
PY = [sys.executable, "-X", "utf8"]
# the coverage runs textcover reads (docs/status.md, phase 8 done); waivers come from docs/text_unshown.tsv
COVER = ["work/qa/cover", "work/qa/cover_scenes", "work/qa/ssbforce", "work/qa/msgforce", "work/qa/p8",
         "work/qa/ovlforce", "work/qa/cover_end", "work/qa/evxforce", "work/qa/ssbforce2", "work/qa/ssbforce3",
         "work/qa/ssbforce4", "work/qa/ssbforce5"]


def step(name, cmd, **kw):
    print(f"== {name}: {' '.join(map(str, cmd))}", flush=True)
    r = subprocess.run([str(c) for c in cmd], cwd=ROOT, **kw)
    if r.returncode:
        sys.exit(f"release stopped: {name} failed (exit {r.returncode})")


def fail(msg):
    sys.exit(f"release stopped: {msg}")


def hashes(path):
    crc, md5, sha1 = 0, hashlib.md5(), hashlib.sha1()
    with open(path, "rb") as f:
        while b := f.read(1 << 24):
            crc = zlib.crc32(b, crc)
            md5.update(b)
            sha1.update(b)
    return {"size": path.stat().st_size, "crc32": f"{crc:08X}", "md5": md5.hexdigest(), "sha1": sha1.hexdigest()}


def verdict_dir(m):
    """The verdicts folder that goes with a manifest: work/qa/manifest.tsv -> work/qa/verdicts,
    work/qa/stress_manifest.tsv -> work/qa/stress_verdicts, work/qa/story/manifest.tsv -> work/qa/story/verdicts."""
    return m.parent / m.name.replace("manifest.tsv", "verdicts")


def gates():
    manifests = sorted(p for p in (ROOT / "work" / "qa").rglob("*manifest.tsv"))
    if not any(m.parent.name == "story" for m in manifests):
        fail("no story-pass manifest (work/qa/story/manifest.tsv; tools/story.py + qa_gate.py init)")
    for m in manifests:
        step(f"qa_gate {m.relative_to(ROOT).as_posix()}", PY + [SCRIPTS / "qa_gate.py", "check", m, verdict_dir(m)])
    step("textcover", PY + ["tools/textcover.py", *COVER])
    open_lines = [x for x in (ROOT / "docs" / "polish.md").read_text(encoding="utf-8").splitlines()
                  if x.lstrip().startswith("- [ ]")]
    if open_lines:
        fail(f"docs/polish.md has {len(open_lines)} unticked line(s): {open_lines[0]}")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    ph = re.findall(r"<[A-Za-z][^<>\n]*>", readme)
    if ph:
        fail(f"README.md still has template placeholders: {ph[:5]}")
    print("== polish list, README: ok")


def debug_off():
    """The debug warp (tools/debug/warp.py + warp.lua) runs inside the emulator: the build must not pull anything in
    from it, and build.py has no debug mode."""
    for f in ("build.py", "insert.py"):
        src = (ROOT / "tools" / f).read_text(encoding="utf-8")
        src = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))  # comments cite debug tools
        if re.search(r"tools[/\\]debug|warp\.lua|--debug|import debug", src):
            fail(f"tools/{f} refers to the debug tool")
    if any("debug" in p.name.lower() for p in (ROOT / "asm").glob("*")):
        fail("asm/ holds a debug patch")
    print("== debug tool: off (emulator-side only, not in the build)")


README_TXT = """Favorite Dear: Junpaku no Yogensha - English fan translation v{version}
==========================================================================

Unofficial English patch for Favorite Dear: Junpaku no Yogensha ("The Pure White Prophet";
PlayStation, NEC Interchannel, 2000, SLPS-02754).
Source, tools and bug reports: https://github.com/minhnhattonthat/favorite-dear-junpaku-no-yogensha-en

What you need
-------------
Your own dump of the Japanese disc, one .bin + .cue
(Redump: "{orig}", http://redump.org/disc/ - search for SLPS-02754):
  {orig}.bin
  size   {o[size]} bytes
  CRC32  {o[crc32]}
  MD5    {o[md5]}
  SHA-1  {o[sha1]}
Any other dump (another revision, an already-patched copy, .iso/.chd conversions) will not patch correctly.

How to patch
------------
1. Apply {patch} to "{orig}.bin" with xdelta3 or a front-end such as
   Delta Patcher (https://github.com/marco-calautti/DeltaPatcher) or the web patcher at
   https://www.marcrobledo.com/RomPatcher.js/ . Command line:
     xdelta3 -d -s "{orig}.bin" {patch} "Favorite Dear - Junpaku no Yogensha (English).bin"
2. Copy the .cue, rename it to match, and change the FILE line inside it to the new .bin name.

Patched result: {b[size]} bytes, CRC32 {b[crc32]}, SHA-1 {b[sha1]}

Tested in PCSX-Redux with the SCPH-5500 BIOS. Start from a cold boot: emulator savestates made with
the Japanese game carry its old code and text.

Translation status
------------------
English: all dialogue and story events, battle text, fairy reports, heaven, the hero chats, missions,
menus, items, status screens, the opening movie captions, the endings and the staff roll.
Graphics with text: English, except the title logo, which keeps its 純白の預言者 lettering under the
English "FAVORITE DEAR" (there is no official English logo).
Name entry: the kana pages are still there; the Latin letter page is one arrow press away.
Left in Japanese: the voice acting and songs, and the memory-card save titles the console's
memory-card manager shows (it draws Japanese full-width characters only).

Known issues
------------
- A short name with an odd number of letters is followed by a space ("Ray , welcome"); names are
  drawn as letter pairs. Hero and town names in fairy reports can show the same space
  ("Cecia -sama"). On the name-entry field and the angel status panel some letter pairs show
  a small gap ("Ravi el").
- Staff-roll name readings are best guesses where no source was found.
- Some fixed-size labels (battle name plates, the album, the heaven help bar) use shorter English
  forms than the dialogue.
- Bug reports: https://github.com/minhnhattonthat/favorite-dear-junpaku-no-yogensha-en/issues

Credits
-------
Translation, hacking and tools: minhnhattonthat, with extensive AI assistance (Claude by Anthropic).
Fonts: Crimson Text (SIL Open Font License 1.1) in the movie captions and staff roll, DejaVu Sans
Condensed (Bitstream Vera licence) in the album panel; details in docs/fonts.md in the repository.
Corrections are very welcome.

This is an unofficial fan work, not affiliated with NEC Interchannel. Favorite Dear: Junpaku no
Yogensha is (c) NEC Interchannel. No game data is included; do not share patched disc images.
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's files in release/")
    a = ap.parse_args(argv)
    name = f"Favorite_Dear_Junpaku_no_Yogensha_EN_v{a.version}"
    patch, zpath = OUT / f"{name}.xdelta", OUT / f"{name}.zip"
    if (patch.exists() or zpath.exists()) and not a.force:
        fail(f"{zpath.name} or {patch.name} exists; pass --force to rebuild this version")
    if not XDELTA.is_file():
        fail(f"missing {XDELTA} (jmacd/xdelta-gpl v3.1.0, AGENTS.md)")

    step("build", PY + ["tools/build.py"])
    step("tests", PY + ["tools/check.py"])
    step("smoke", PY + [SCRIPTS / "emu.py", BUILT_CUE.resolve(), "--out", "work/qa/smoke", "--route",
                        "tools/routes/boot.txt", "--smoke"])
    step("leftover Japanese", PY + ["tools/jpcheck.py"])
    gates()
    debug_off()

    OUT.mkdir(exist_ok=True)
    o, b = hashes(ORIG_BIN), hashes(BUILT_BIN)
    step("patch", [XDELTA, "-e", "-9", "-f", "-B", str(max(o["size"], b["size"])), "-s", ORIG_BIN, BUILT_BIN, patch])
    check = OUT / f"{name}.reapply.bin"
    step("re-apply", [XDELTA, "-d", "-f", "-s", ORIG_BIN, patch, check])  # as README.txt tells players
    got = hashes(check)
    check.unlink()
    if got["sha1"] != b["sha1"]:
        fail(f"re-applied patch gives {got['sha1']}, build is {b['sha1']}")
    print(f"== re-apply: ok ({b['sha1']})")

    readme = README_TXT.format(version=a.version, o=o, b=b, patch=patch.name, orig=ORIG_NAME)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_STORED) as z:
        z.write(patch, patch.name)
        z.writestr("README.txt", readme.replace("\n", "\r\n"))
    psha = hashlib.sha1(patch.read_bytes()).hexdigest()
    print(f"release: {zpath.relative_to(ROOT)} ({zpath.stat().st_size} bytes); patch {patch.name} "
          f"{patch.stat().st_size} bytes sha1 {psha}; built image {b['sha1']} CRC32 {b['crc32']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
