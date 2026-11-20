"""build.py: rebuild the disc image from the unpacked original plus the translation's changes.

    python -X utf8 tools/build.py                       -> build/fd2_en.bin/.cue
    python -X utf8 tools/build.py --identity            -> build/identity.bin/.cue, every LKF re-laid by lkf.build,
                                                           no edits; must equal rom.sha1 (tests/test_build.py)
    python -X utf8 tools/build.py --grow-test           -> build/grow.bin/.cue: the first entry of every LKF grown
                                                           (zero bytes appended) so every later entry and every file
                                                           after the archives moves (docs/re/disc.md §Grow test)

Steps: check the dump against rom.sha1; unpack it into work/disc/tree with dumpsxiso if that is missing; rebuild each
LKF that has changed entries (lkf.build, header rewritten); write build/<name>.xml from work/disc/layout.xml with
every file pointing at its original or rebuilt copy; run mkpsxiso. Insertion steps (later phases) hand their files to
build() as `lkf_changes` {archive: {entry name: bytes}} and `files` {disc file name: bytes}."""
import argparse
import hashlib
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402
import lkf  # noqa: E402

TOOLS = ROOT / "tools/mkpsxiso/mkpsxiso-2.30-win64"
ORIG_BIN = ROOT / "rom/Favorite Dear - Junpaku no Yogensha (Japan).bin"
DISC = ROOT / "work/disc"
TREE = DISC / "tree"
LAYOUT = DISC / "layout.xml"
BUILD = ROOT / "build"
ARCHIVES = ["FD2BN", "FD2SN", "SSB_DATA", "GRPDATA"]


def unpack():
    """work/disc/tree + layout.xml from the original .bin (once)."""
    if (TREE / "SLPS_027.54").is_file() and LAYOUT.is_file():
        return
    DISC.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(TOOLS / "dumpsxiso.exe"), "-x", str(TREE), "-s", str(LAYOUT), str(ORIG_BIN)], check=True)


def rebuild_lkf(name, changes):
    """Archive bytes with entries replaced by name (bytes) and the header re-laid."""
    data = (TREE / f"{name}.LKF").read_bytes()
    entries = lkf.parse(data)["entries"]
    names = [e["name"] for e in entries]
    assert len(set(names)) == len(names), f"{name}: duplicate entry names"
    unknown = set(changes) - set(names)
    assert not unknown, f"{name}: no such entries {sorted(unknown)}"
    payloads = [changes.get(e["name"], data[e["off"]:e["off"] + e["size"]]) for e in entries]
    return lkf.build(data, payloads)


def build(stem="fd2_en", lkf_changes=None, files=None, relay_all=False):
    """Write build/<stem>.bin/.cue and return the .bin path.
    lkf_changes: {archive: {entry name: bytes}}; files: {disc file name: bytes} (whole files, e.g. the EXE);
    relay_all: rebuild every LKF through lkf.build even with no changes (the identity test of the packer)."""
    check_rom.check()
    unpack()
    lkf_changes = lkf_changes or {}
    files = dict(files or {})
    stage = BUILD / f"{stem}_files"
    stage.mkdir(parents=True, exist_ok=True)
    for name in ARCHIVES:
        if name in lkf_changes or relay_all:
            files[f"{name}.LKF"] = rebuild_lkf(name, lkf_changes.get(name, {}))
    tree = ET.parse(LAYOUT)
    root = tree.getroot()
    root.find("track/license").set("file", str(TREE / "license_data.dat"))
    seen = set()
    for f in root.iter("file"):
        name = f.get("name")
        if name in files:
            path = stage / name
            path.write_bytes(files[name])
            seen.add(name)
        else:
            path = TREE / name
        f.set("source", str(path))
    assert seen == set(files), f"not on the disc: {sorted(set(files) - seen)}"
    xml = BUILD / f"{stem}.xml"
    tree.write(xml, encoding="utf-8", xml_declaration=True)
    out_bin, out_cue = BUILD / f"{stem}.bin", BUILD / f"{stem}.cue"
    r = subprocess.run([str(TOOLS / "mkpsxiso.exe"), "-y", "-q", "-o", str(out_bin), "-c", str(out_cue), str(xml)],
                       cwd=DISC, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"mkpsxiso failed ({r.returncode}):\n{r.stdout}\n{r.stderr}")
    return out_bin


def sha1(path):
    with open(path, "rb") as f:
        return hashlib.file_digest(f, "sha1").hexdigest()


def orig_sha1():
    for line in (ROOT / "rom.sha1").read_text(encoding="utf-8").splitlines():
        if line.strip().endswith(".bin"):
            return line.split()[0].lower()
    raise SystemExit("rom.sha1 lists no .bin")


GROW = 0x1800   # bytes appended to each archive's first entry in --grow-test (3 sectors: every later LBA moves)


def grow_changes():
    out = {}
    for name in ARCHIVES:
        data = (TREE / f"{name}.LKF").read_bytes()
        e = lkf.parse(data)["entries"][0]
        out[name] = {e["name"]: data[e["off"]:e["off"] + e["size"]] + b"\0" * GROW}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--identity", action="store_true", help="no edits, all archives re-laid; compare with rom.sha1")
    ap.add_argument("--grow-test", action="store_true", help="grow each LKF's first entry (build/grow.bin)")
    a = ap.parse_args()
    if a.identity:
        out = build("identity", relay_all=True)
        got = sha1(out)
        ok = got == orig_sha1()
        print(f"{out}: sha1 {got} {'identical to the original' if ok else 'DIFFERS from the original'}")
        sys.exit(0 if ok else 1)
    if a.grow_test:
        out = build("grow", lkf_changes=grow_changes())
    else:
        out = build()   # insertion steps (phase 7) pass their lkf_changes/files here
    print(f"{out}: sha1 {sha1(out)}")


if __name__ == "__main__":
    main()
