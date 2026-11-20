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
    if bad:
        print("rows a run did read (rule wrong):", " ".join(bad[:20]))
        return 1
    OUT.write_text("# text coverage waivers: written by tools/unshown.py from its rules (do not edit by hand)\n"
                   + "\n".join(out) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(out)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
