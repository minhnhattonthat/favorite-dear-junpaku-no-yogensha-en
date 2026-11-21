"""unshown.py: write docs/text_unshown.tsv, the text coverage waivers, from rules checked against the coverage logs.

    python -X utf8 tools/unshown.py work/qa/cover work/qa/cover_scenes work/qa/ssbforce work/qa/msgforce ...

Each rule names rows the game never reads, with the evidence: the rule is checked on the logs given (a waived row
that some run did read means the rule is wrong: exit 1, nothing written). tools/textcover.py reads the file.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import textcover  # noqa: E402

OUT = ROOT / "docs" / "text_unshown.tsv"


def evx_rows(kind):
    for tsv in sorted((ROOT / "script" / "evx").glob("*.tsv")):
        with open(tsv, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                if r["notes"].startswith(kind):
                    yield tsv.stem, f"evx/{r['id']}"


OVL_BASE = 0x8009B4B0
CAPTIONS = (0x800A654C, 0x800A6EAC)  # op.bin OMAKE CG caption pointer table (place, title, caption per CG)


def ovl_rows(name):
    with open(ROOT / "script" / "ovl" / f"{name}.tsv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def caption_rows():
    """op.bin rows whose every reference is a u32 pointer inside the caption table (and no lui pair)."""
    import struct
    data = (ROOT / "work" / "orig_ovl" / "op.bin").read_bytes()
    sites = {}
    for o in range(0, len(data) - 3, 4):
        v = struct.unpack_from("<I", data, o)[0]
        sites.setdefault(v, []).append(OVL_BASE + o)
    for r in ovl_rows("op"):
        va = int(r["id"].split(".")[1], 16)
        s = sites.get(va, [])
        if s and "lui" not in r["notes"] and all(CAPTIONS[0] <= a < CAPTIONS[1] for a in s):
            yield f"ovl/{r['id']}"


def main():
    dirs = sys.argv[1:]
    if not dirs:
        print(__doc__)
        return 2
    logs = [p for d in dirs for p in Path(d).rglob("log.txt")]
    files, _ = textcover.load_rows()
    hit = textcover.reached(logs, files)
    loaded = textcover.loaded_files(logs)
    out, bad = [], []
    rules = [
        ("unit", "EVX unit name (32-byte field): battles never read it (read watch over every loaded EVX; their "
                 "speaker/text rows are read); name plates are images"),
        ("dev", "EVX dev label (0x02 title field): never read in game (read watch over every loaded EVX)"),
    ]
    for kind, why in rules:
        keys = list(evx_rows(kind))
        n_loaded = sum(1 for stem, _ in keys if f"{stem}.evx".lower() in loaded)
        read = [k for _, k in keys if k in hit]
        bad += read
        print(f"{kind}: {len(keys)} rows, {n_loaded} in EVX files some run loaded, {len(read)} read")
        out += [f"{k}\t{why}" for _, k in keys]
    caps = list(caption_rows())
    read = [k for k in caps if k in hit]
    bad += read
    print(f"op captions: {len(caps)} rows, {len(read)} read")
    out += [f"{k}\top.bin OMAKE CG caption table 0x800A654C-0x800A6EAC: no pointer or lui reference to the table "
            f"anywhere, and no read of it in the OMAKE album / CG view runs (read watch, work/qa/p8/captab): never "
            f"shown" for k in caps]
    # rows with no Japanese at all (an empty speaker slot, an empty EVX message): nothing to draw or to translate
    empty = []
    for tsv in sorted((ROOT / "script").glob("*/*.tsv")):
        with open(tsv, encoding="utf-8", newline="") as f:
            empty += [f"{tsv.parent.name}/{r['id']}" for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
                      if r["jp"] == ""]
    empty = [k for k in empty if k not in hit]
    print(f"empty: {len(empty)} rows with no Japanese, not reached")
    out += [f"{k}\tempty string (no Japanese, en empty): nothing to draw" for k in empty]
    # GRPDATA Dummy00.DAT: waived only while no run loads it (every event and warp scene runs with the FILE log)
    if "dummy00.dat" in loaded:
        print("Dummy00.DAT was loaded by a run: rule wrong")
        return 1
    with open(ROOT / "script" / "misc" / "Dummy00.tsv", encoding="utf-8", newline="") as f:
        dummy = [f"misc/{r['id']}" for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)]
    print(f"Dummy00.DAT: {len(dummy)} rows, never loaded in {len(logs)} logs")
    out += [f"{k}\tGRPDATA Dummy00.DAT: no run loads it (LKF loader log over every event and warp scene); name and "
            f"content (one-line greetings with no script reference) say dev leftover" for k in dummy]
    if bad:
        print("rows a run did read (rule wrong):", " ".join(bad[:20]))
        return 1
    OUT.write_text("# text coverage waivers: written by tools/unshown.py from its rules (do not edit by hand)\n"
                   + "\n".join(out) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(out)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
