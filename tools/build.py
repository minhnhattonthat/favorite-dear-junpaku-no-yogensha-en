"""build.py: rebuild the disc image from the unpacked original plus the translation's changes.

    python -X utf8 tools/build.py                       -> build/fd2_en.bin/.cue
    python -X utf8 tools/build.py --identity            -> build/identity.bin/.cue, every LKF re-laid by lkf.build,
                                                           no edits; must equal rom.sha1 (tests/test_build.py)
    python -X utf8 tools/build.py --grow-test           -> build/grow.bin/.cue: the first entry of every LKF grown
                                                           (zero bytes appended) so every later entry and every file
                                                           after the archives moves (docs/re/disc.md §Grow test)

Steps: check the dump against rom.sha1; unpack it into work/disc/tree with dumpsxiso if that is missing; rebuild each
LKF that has changed entries (lkf.build, header rewritten); write build/<name>.xml from work/disc/layout.xml with
every file pointing at its original or rebuilt copy; run mkpsxiso. The default build takes its changes from
script/*.tsv `en` columns (tools/insert.py) as `lkf_changes` {archive: {entry name: bytes}} and `files`
{disc file name: bytes}; with no translated rows it equals the original disc."""
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
EXE_NAME = "SLPS_027.54"
ARMIPS = ROOT / "tools/armips/armips.exe"
ASM = ROOT / "asm"
EXE_PAD = 0x10000       # bytes prepended to the EXE image (t_addr 0x80020000 -> 0x80010000): the string heap
                        # 0x80010000-0x8001E000 (tools/codetext.py Heap) and FREE 0x8001E000-0x80020000 (asm/font.asm)


def patch_exe(exe, heap=None):
    """EXE bytes -> EXE with the free block prepended, the string heap written at its start and asm/font.asm
    applied."""
    import struct
    import tempfile
    import codetext
    import font_en
    t_addr, t_size = struct.unpack_from("<II", exe, 0x18)
    assert t_addr == 0x80020000, f"EXE already patched (t_addr {t_addr:#x})"
    load = t_addr - EXE_PAD
    assert load == codetext.HEAP_LO
    head = bytearray(exe[:0x800])
    struct.pack_into("<II", head, 0x18, load, t_size + EXE_PAD)
    pad = bytearray(EXE_PAD)
    if heap is not None:
        assert heap.lo == codetext.HEAP_LO and heap.lo + len(heap.buf) <= codetext.HEAP_HI
        pad[:len(heap.buf)] = heap.buf
    padded = bytes(head) + bytes(pad) + exe[0x800:]
    font_en.write_inc()
    with tempfile.TemporaryDirectory() as td:
        src, dst = Path(td) / "in.exe", Path(td) / "out.exe"
        src.write_bytes(padded)
        r = subprocess.run([str(ARMIPS), "font.asm", "-strequ", "EXE_IN", str(src), "-strequ", "EXE_OUT", str(dst),
                            "-equ", "PAIR_G", str(font_en.G), "-equ", "LOAD_ADDR", hex(load)],
                           cwd=ASM, capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"armips failed ({r.returncode}):\n{r.stdout}\n{r.stderr}")
        out = dst.read_bytes()
    assert len(out) == len(padded), "armips changed the EXE size"
    return out


def write_logs(stem, heap, lkf_changes, files):
    """build/<stem>_writes/<file>.bin (the file before patch_exe) + <file>.txt (its write log), for
    `romdiff.py ORIG NEW --writes LOG` (tests/test_build.py runs it on every changed EXE/overlay)."""
    d = BUILD / f"{stem}_writes"
    d.mkdir(parents=True, exist_ok=True)
    for f in d.iterdir():
        f.unlink()
    for name, log in heap.log.items():
        data = files.get(name) or lkf_changes.get("FD2BN", {}).get(name)
        if data is None:
            continue
        (d / f"{name}.bin").write_bytes(data)
        (d / f"{name}.txt").write_text("".join(f"{o:X} {a.hex()} {b.hex()} {by}\n" for o, a, b, by in log),
                                       encoding="utf-8", newline="\n")


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
    ap.add_argument("--qa", action="append", default=[], metavar="ID=TEXT",
                    help="override one row's text (text form of tools/jtext.py); repeatable")
    ap.add_argument("--stem", default=None, help="output name build/<stem>.bin (default fd2_en, fd2_marker)")
    ap.add_argument("--marker", action="store_true", help="marker build: every row = label + filler (tools/marker.py)")
    ap.add_argument("--ruler", action="store_true",
                    help="width-gate build: growable rows = label + 1.5x-wide position ruler (tools/marker.py)")
    ap.add_argument("--ruler-min", type=int, default=0, metavar="N",
                    help="with --ruler: stretch every line with text to at least N letters (clip test for short rows)")
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
        import insert
        qa = dict(q.split("=", 1) for q in a.qa)
        texts_for = None
        if a.marker:
            import marker
            texts_for = marker.texts_for
        if a.ruler:
            import marker
            texts_for = marker.ruler_texts_for
            marker.RULER_MIN = a.ruler_min
        import codetext
        heap = codetext.Heap()
        lkf_changes, files, nrows = insert.changes("en", overrides=qa, texts_for=texts_for, heap=heap)
        stem = a.stem or ("fd2_ruler" if a.ruler else "fd2_marker" if a.marker else "fd2_en")
        write_logs(stem, heap, lkf_changes, files)
        files[EXE_NAME] = patch_exe(files.get(EXE_NAME) or (TREE / EXE_NAME).read_bytes(), heap)
        out = build(stem, lkf_changes=lkf_changes, files=files)
        moved = sum(len(v) for v in heap.moved.values())
        print(f"{nrows} translated rows; {moved} EXE/overlay strings relocated, heap {len(heap.buf):#x} of "
              f"{codetext.HEAP_HI - codetext.HEAP_LO:#x} bytes")
    print(f"{out}: sha1 {sha1(out)}")


if __name__ == "__main__":
    main()
