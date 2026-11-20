"""honorifics.py: ruling D1/D9 (personal name + honorific -> "Name-sama") for trans/en, reviewed row by row.

    python -X utf8 tools/honorifics.py propose OUT.tsv   rows whose EN lacks a ruled honorific: proposed EN
    python -X utf8 tools/honorifics.py apply OUT.tsv     write the `new` column of reviewed rows into trans/en/bNNN.tsv

Ported from the first game's project (`../favorite-dear-en/tools/honorifics.py`, its D12). `propose` only writes a
proposal file; rows it can't place (the name is missing from the English, or the JP uses the same name both bare and
with an honorific and the English has no title to convert) get `new` = `?` and are fixed by hand. Read every proposed
row before `apply` (columns: batch, id, how, old, new). `batches.check` lints the same rule through `missing()`.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import batches as B  # noqa: E402

KATA = "ァ-ヺー・"
HON = {"さん": "san", "くん": "kun", "君": "kun", "ちゃん": "chan", "様": "sama", "さま": "sama", "殿": "dono",
       "どの": "dono"}
# runtime placeholders and the player's name: the game substitutes a name, so they take a suffix too
SUBST = [B.NAME] + [t for t in B.GAME_TAGS if "名" in t and "イベント" not in t and "地方" not in t
                    and "目的地" not in t]
# English titles that stood in for the honorific; dropped in front of the name
TITLES = r"(?:(?:Lord|Lady|Sir|Master|Mister|Mr\.|Mrs\.|Miss|Ms\.|Dame|Madam|Mistress|Dr\.)\s+)"


def names():
    """{jp katakana name: en} from the glossary's katakana rows"""
    out = {}
    for jp, en, _ in B.glossary():
        if re.fullmatch(f"[{KATA}]+", jp) and en:
            out[jp] = en
    return out


def name_en(who, nm):
    if who in nm:
        return nm[who]
    parts = who.split("・")
    if len(parts) > 1 and all(p in nm for p in parts):
        return " ".join(nm[p] for p in parts)
    return None


def pairs(jp, nm):
    """[(jp name, en name, suffix)] for each name+honorific in the JP text"""
    text = re.sub(r"\{[^}]*\}", "", jp)
    hon = "|".join(sorted(HON, key=len, reverse=True))
    sub = "|".join(re.escape(s) for s in SUBST)
    out = []
    for m in re.finditer(rf"({sub}|[{KATA}]+)({hon})", text):
        who, h = m.groups()
        e = who if who in SUBST else name_en(who, nm)
        if e:
            out.append((who, e, HON[h]))
    return out


def missing(jp, en, nm):
    """lint: ruled `Name-suffix` forms absent from the English"""
    return [f"honorific {who} -> {e}-{suf} missing (D9)" for who, e, suf in dict.fromkeys(pairs(jp, nm))
            if f"{e}-{suf}" not in en]


def propose_row(jp, en, nm):
    new, how = en, "auto"
    hon = "(?:" + "|".join(HON) + ")"
    for who, e, suf in dict.fromkeys(pairs(jp, nm)):
        if f"{e}-{suf}" in new:
            continue
        text = re.sub(r"\{[^}]*\}", "", jp)
        bare = len(re.findall(re.escape(who), text)) - len(re.findall(re.escape(who) + hon, text))
        if bare > 0:
            rx = re.compile(TITLES + re.escape(e) + r"(?![\w-])")
            if not rx.search(new):
                return "mixed", "?"
            new = rx.sub(f"{e}-{suf}", new)
            how = "titled"
            continue
        rx = re.compile(TITLES + "?" + re.escape(e) + r"(?![\w-])")
        if not rx.search(new):
            return "absent", "?"
        new = rx.sub(f"{e}-{suf}", new)
    return how, new


def propose(outp):
    nm = names()
    lines = ["batch\tid\thow\told\tnew"]
    for p in sorted(B.BATCHES.glob("b*.tsv")):
        en = {r[0]: r[1] for r in B.read_tsv(B.OUT / p.name)}
        for rid, _, _, jp in B.read_tsv(p):
            e = en.get(rid, "")
            if e in ("", "-") or not missing(jp, e, nm):
                continue
            how, new = propose_row(jp, e, nm)
            lines.append("\t".join([p.stem, rid, how, e, new]))
    Path(outp).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(lines) - 1} rows -> {outp}")


def apply(inp):
    rows = B.read_tsv(Path(inp))
    by = {}
    for b, rid, _, old, new in rows:
        if new in ("?", ""):
            sys.exit(f"{rid}: unresolved `?` row; fix or delete it first")
        by.setdefault(b, {})[rid] = (old, new)
    for b, fix in by.items():
        p = B.OUT / f"{b}.tsv"
        out = B.read_tsv(p)
        for r in out:
            if r[0] in fix:
                old, new = fix[r[0]]
                if r[1] != old:
                    sys.exit(f"{b} {r[0]}: trans/en changed since propose")
                r[1] = new
        B.write_tsv(p, ["id", "en"], out)
    print(f"applied {len(rows)} rows in {len(by)} batches")


def main(argv):
    if len(argv) != 2 or argv[0] not in ("propose", "apply"):
        print(__doc__)
        return 2
    (propose if argv[0] == "propose" else apply)(argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
