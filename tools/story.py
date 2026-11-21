"""story.py: chapter files for the story pass (skill `references/translation.md` §Review, `docs/synopsis.md`).

    python -X utf8 tools/story.py                -> work/qa/story/chapters/NN_name.txt (every chapter)
    python -X utf8 tools/story.py --list         chapter -> files, rows, sizes

Each chapter holds every shown row of its script files in story order: `>> id | speaker | kind`, `JP:`, `EN:`.
Soft breaks ({n}) are dropped and pages ({wait}{clear}) shown as " / ", so a reviewer reads flowing text. Speaker
name rows and fields the game never shows (dev labels, unit-name fields) are left out; their names show as the
speaker of the lines that follow. Every script file must fall into exactly one chapter (the tool fails otherwise),
so the story pass reads the whole script. Regenerate after every script edit, then
`qa_gate.py init work/qa/story/manifest.tsv work/qa/story/chapters --glob "*.txt"`.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "script"
OUT = ROOT / "work" / "qa" / "story" / "chapters"

HEROES = [("fein", "fe", 0), ("clive", "cl", 1), ("rudiere", "lo", 2), ("rocus", "ro", 3), ("irene", "ei", 4),
          ("leyla", "la", 5), ("cecia", "ce", 6)]
# (chapter, predicate on (dir, stem)); first match wins, so order matters.
CHAPTERS = [("01_prologue", lambda d, s: (d == "ssb" and s in ("prologue", "alkaya", "tenkai", "maseki"))
             or (d == "ssb" and s.startswith("exam_")) or (d == "ovl" and s == "pro"))]
for n, (name, pre, bank) in enumerate(HEROES):
    CHAPTERS.append((f"{n + 2:02d}_{name}", lambda d, s, pre=pre, bank=bank:
                     (d in ("ssb", "evx") and re.match(rf"{pre}e[dv]", s, re.I) is not None)
                     or (d == "msg" and s == f"BTL_EVT{bank}")))
CHAPTERS += [
    ("09_angel_calls", lambda d, s: d == "ssb" and s.lower().startswith("men")),
    ("10_heaven", lambda d, s: (d == "msg" and re.match(r"(HVN_Msg|FryMsg|T_Msg)", s) is not None)
     or (d == "ssb" and re.match(r"(Y0\dev|taiken|visit_)", s) is not None)),
    ("11_hub", lambda d, s: d == "msg"),
    ("12_endings", lambda d, s: d == "end" or (d == "ssb" and s in ("Raph_end", "TGS_END"))
     or (d == "ovl" and s == "ed")),
    ("13_system", lambda d, s: d in ("ovl", "misc", "exe")),
]
UNSHOWN = ("dev label", "unit name")   # notes of fields never read as dialogue


def natural(stem):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", stem.lower())]


def files():
    out = []
    for p in sorted(SCRIPT.rglob("*.tsv")):
        d = "exe" if p.parent == SCRIPT else p.parent.name
        out.append((d, p.stem, p))
    return out


def assign():
    chap = {c: [] for c, _ in CHAPTERS}
    for d, s, p in files():
        hit = [c for c, f in CHAPTERS if f(d, s)]
        if not hit:
            raise SystemExit(f"story.py: {p.relative_to(ROOT)} is in no chapter")
        chap[hit[0]].append((d, s, p))
    for c in chap:   # story order: hero events and their battles interleave by event number
        chap[c].sort(key=lambda t: (t[0] == "msg", t[0] == "end", natural(t[1]), t[0] != "ssb"))
    return chap


def flow(s, sep):
    """sep: what a soft break becomes ("" in Japanese, " " in English)."""
    return s.replace("{wait}{clear}", " / ").replace("{n}", sep).strip(" /")


def rows(p):
    speaker = "-"
    for line in p.read_text(encoding="utf-8").splitlines()[1:]:
        f = line.split("\t") + ["", ""]
        rid, jp, en, notes = f[0], f[1], f[2], f[3]
        if notes == "speaker":
            speaker = en or jp
            continue
        if notes.startswith(UNSHOWN) or not jp:
            continue
        yield rid, speaker, notes or "-", flow(jp, ""), flow(en, " ")


def main(argv):
    chap = assign()
    if "--list" in argv:
        for c, fs in chap.items():
            n = sum(1 for _, _, p in fs for _ in rows(p))
            print(f"{c}: {len(fs)} files, {n} rows")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.txt"):
        old.unlink()
    for c, fs in chap.items():
        body, seen, dup = [], {}, 0
        for d, s, p in fs:
            body += [f"## {d}/{s}", ""]
            for rid, spk, kind, jp, en in rows(p):
                if (spk, jp, en) in seen:   # an exact repeat (the same line in another bank or event copy)
                    dup += 1
                    continue
                seen[(spk, jp, en)] = rid
                body += [f">> {rid} | {spk} | {kind}", f"JP: {jp}", f"EN: {en}", ""]
        out = [f"# {c}: {len(fs)} files in story order, {len(seen)} rows ({dup} exact repeats left out)."
               " Synopsis: docs/synopsis.md; voices: docs/style-reference.md; glossary: glossary.md", ""] + body
        (OUT / f"{c}.txt").write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"{len(chap)} chapters -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
