"""batches.py: translation batches (docs/translator-brief.md).

    python -X utf8 tools/batches.py split            write trans/batches/bNNN.tsv (refuses if any exist)
    python -X utf8 tools/batches.py check b001 [..]  validate trans/en/bNNN.tsv against its batch; prints OK or errors
    python -X utf8 tools/batches.py merge            check every trans/en/*.tsv, wrap, write `en` into script/
    python -X utf8 tools/batches.py todo             batches without an output file

Rows with the same `jp` form one family: only the first goes into a batch, merge copies its English to the rest.
Batch input: `id<TAB>kind<TAB>speaker<TAB>jp`; in wrapped kinds the soft line breaks ({n} between two characters)
are removed, so the translator writes flowing text and merge wraps it (WRAP below), adding {wait}{clear} pages when
a page runs past its line count. Output: `id<TAB>en` with every other {code} kept in order.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import font_en  # noqa: E402

SCRIPT = ROOT / "script"
BATCHES = ROOT / "trans" / "batches"
OUT = ROOT / "trans" / "en"
GLOSSARY = ROOT / "glossary.md"
BUDGET = 3500          # JP characters per batch (one Read)
ORDER = ["ssb", "msg", "evx", "end", "misc", "ovl", "exe.tsv"]
JP = re.compile(r"[　-鿿＀-￯]")
TAG = re.compile(r"\{[^{}]*\}")
NAME = "＄＄＄＄＄＄"     # the player's name (6 cells = 12 letters)
PAGE = "{wait}{clear}"
ALLOWED = set(font_en.CHARS)
# Runtime placeholders the game substitutes by string match (table in FD2BN.LKF at 0xE0FC): keep them byte-exact.
GAME_TAGS = ["＜勇者名１＞", "＜勇者名２＞", "＜勇者名＞", "＜妖精名＞", "＜イベント名＞", "＜地方名＞",
             "＜目的地名＞", "○○", "＜ボーナスＡＰ＞"]   # last: HVN_Msg00.259E, kept as in the JP


def wrap_spec(path, row):
    """(letters per line, lines per page, may add pages) or None (no wrapping: menus, code strings, names)"""
    d = path.relative_to(SCRIPT).parts[0]
    if row["notes"] in ("speaker", "unit", "choice", "dev") or d in ("ovl", "exe.tsv", "misc"):
        return None
    if d == "end":
        return (42, 99, False)
    if d == "msg" and path.stem.startswith("BTL_EVT"):
        return (44, 2, True)
    return (44, 3, True)


def files():
    out = []
    for d in ORDER:
        p = SCRIPT / d
        out += [p] if p.is_file() else sorted(p.rglob("*.tsv"))
    return out


def has_jp(s):
    return bool(JP.search(TAG.sub("", s)))


def unwrap(jp):
    """drop {n} between two non-tag characters"""
    return re.sub(r"(?<=[^}])\{n\}(?=[^{])", "", jp)


def codes(s, soft=True):
    t = TAG.findall(s)
    return [c for c in t if c != "{n}"] if soft else t


def read_tsv(p):
    rows = []
    for line in Path(p).read_text(encoding="utf-8").splitlines()[1:]:
        f = line.split("\t")
        assert len(f) >= 2, (p, line)
        rows.append(f)
    return rows


def write_tsv(p, head, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    for r in rows:
        assert len(r) == len(head) and not any("\t" in v or "\n" in v for v in r), r
    p.write_text("\n".join(["\t".join(head)] + ["\t".join(r) for r in rows]) + "\n", encoding="utf-8", newline="\n")


def families():
    """{jp: [(path, row, speaker)]} in ORDER"""
    fam = {}
    for p in files():
        speaker = ""
        for r in extract.read_tsv(p):
            if r["notes"] == "speaker":
                speaker = r["jp"]
            if has_jp(r["jp"]):
                fam.setdefault(r["jp"], []).append((p, r, speaker))
    return fam


def split():
    if BATCHES.exists() and any(BATCHES.glob("b*.tsv")):
        sys.exit("trans/batches already has batches; refusing to overwrite")
    batches, cur, n = [], [], 0
    for jp, members in families().items():
        p, r, spk = members[0]
        spec = wrap_spec(p, r)
        kind = "name" if r["notes"] in ("speaker", "unit") else (r["notes"] or "text") if spec is None else \
            f"wrap{spec[0]}x{spec[1]}"
        text = unwrap(jp) if spec else jp
        g = len(TAG.sub("", text))
        if cur and n + g > BUDGET:
            batches.append(cur)
            cur, n = [], 0
        cur.append([r["id"], kind, "" if r["notes"] == "speaker" else spk, text])
        n += g
    batches.append(cur)
    for i, b in enumerate(batches, 1):
        write_tsv(BATCHES / f"b{i:03d}.tsv", ["id", "kind", "speaker", "jp"], b)
    print(f"{len(batches)} batches, {sum(len(b) for b in batches)} entries")


def glossary():
    """[(jp, en, avoid)] from the glossary tables"""
    out = []
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(c) >= 5 and JP.search(c[0]) and c[0] != "JP":
            out.append((c[0], c[1].split(" (")[0], [a.strip() for a in c[4].split(",") if a.strip()]))
    return out


def check(b):
    errs = []
    inp = {r[0]: r for r in read_tsv(BATCHES / f"{b}.tsv")}
    outp = OUT / f"{b}.tsv"
    if not outp.exists():
        return [f"{b}: no {outp.relative_to(ROOT)}"]
    seen = {}
    for f in read_tsv(outp):
        if len(f) != 2:
            errs.append(f"{f[0]}: {len(f)} columns")
            continue
        i, en = f
        if i in seen:
            errs.append(f"{i}: duplicate")
        seen[i] = en
    errs += [f"{i}: missing" for i in inp if i not in seen]
    errs += [f"{i}: not in the batch" for i in seen if i not in inp]
    gl = glossary()
    for i, en in seen.items():
        if i not in inp:
            continue
        _, kind, _, jp = inp[i]
        if en == "-":
            continue          # deliberately untranslated (report it)
        soft = kind.startswith("wrap")
        if codes(en, soft) != codes(jp, soft):
            errs.append(f"{i}: codes {codes(en, soft)} != {codes(jp, soft)}")
        plain = TAG.sub("", en).replace(NAME, "")
        for t in GAME_TAGS:
            if jp.count(t) and not en.count(t):
                errs.append(f"{i}: placeholder {t} is missing")
            plain = plain.replace(t, "")
        if "￥" in jp:        # the prologue quiz's line break (pro.bin tables)
            if en.count("￥") != jp.count("￥"):
                errs.append(f"{i}: {en.count('￥')} ￥ line breaks, the JP has {jp.count('￥')}")
            plain = plain.replace("￥", "")
        bad = {c for c in plain if c not in ALLOWED}
        if bad:
            errs.append(f"{i}: characters not in the font {sorted(bad)}")
        if NAME in jp and NAME not in en:
            errs.append(f"{i}: the player's name {NAME} is missing")
        if re.search(r"\$|\\u|\\n", en):
            errs.append(f"{i}: stray escape")
        if kind == "name" and len(plain) > 12:
            errs.append(f"{i}: name over 12 letters ({len(plain)})")
        if i.endswith(".0002") and len(en.encode("ascii", "replace")) > 30:
            errs.append(f"{i}: EVX title over 30 bytes ({len(en)})")   # evx.build asserts it
        m = re.match(r"fixed (\d+)-byte record", kind)
        if m and len(en.encode("ascii", "replace")) + 1 > int(m.group(1)):   # + terminator
            errs.append(f"{i}: over the {m.group(1)}-byte record with its terminator ({len(en)})")
        if soft:
            w = int(kind[4:].split("x")[0])
            for word in re.split(r"[ ]|\{[^}]*\}", en):
                if len(word) > w:
                    errs.append(f"{i}: word longer than a line: {word[:20]}")
        rest = jp             # a term inside a longer matched term (ルディ in ウルディピア) is that term's
        for gjp, gen, avoid in sorted(gl, key=lambda g: -len(g[0])):
            # a capitalised first letter or title case (menu labels, "Chaos Level") also counts
            if gjp in rest and gen and not any(f in en for f in (gen, gen[0].upper() + gen[1:], gen.title())):
                errs.append(f"{i}: glossary {gjp} -> {gen} missing")
            rest = rest.replace(gjp, "　")
            for a in avoid:
                if re.search(r"\b" + re.escape(a) + r"\b", en):
                    errs.append(f"{i}: avoid {a!r}")
    return errs


def width(s):
    return len(TAG.sub("", s).replace(NAME, "x" * 12))


def wrap(en, spec):
    """greedy word wrap of each page; keeps forced {n}; overflowing pages go on new {wait}{clear} pages"""
    w, lines_max, grow = spec
    pages = en.split(PAGE)
    out = []
    for k, page in enumerate(pages):
        lines = []
        for seg in page.split("{n}"):
            cur = ""
            for word in seg.split(" "):
                cand = f"{cur} {word}" if cur else word
                if cur and width(cand) > w:
                    lines.append(cur)
                    cur = word
                else:
                    cur = cand
            lines.append(cur)
        if grow:
            chunks = [lines[j:j + lines_max] for j in range(0, len(lines), lines_max)]
            out.append(PAGE.join("{n}".join(c) for c in chunks))
        else:
            out.append("{n}".join(lines))
    return PAGE.join(out)


def merge():
    bad = []
    trans = {}
    for outp in sorted(OUT.glob("b*.tsv")):
        e = check(outp.stem)
        if e:
            bad.append(outp.stem)
            print(f"{outp.stem}: {len(e)} errors (skipped)", *e[:5], sep="\n  ")
            continue
        trans.update({f[0]: f[1] for f in read_tsv(outp) if f[1] != "-"})
    rep = {}
    for members in families().values():
        for p, r, _ in members:
            rep[(p, r["id"])] = members[0][1]["id"]
    n = 0
    long_code = []
    for p in files():
        rows = extract.read_tsv(p)
        changed = False
        code = p.parent.name == "ovl" or p.name == "exe.tsv"
        for r in rows:
            k = rep.get((p, r["id"]))
            if k not in trans:
                continue
            spec = wrap_spec(p, r)
            en = wrap(trans[k], spec) if spec else trans[k]
            # EXE/overlay strings are replaced in place until phase 7 relocates them: English longer than
            # the JP bytes (a copy from a dialogue row, or the row's own translation) would break the build,
            # so the script keeps the JP and trans/en keeps the English for phase 7.
            if code and len(extract.jtext.encode(font_en.to_pairs(en))) > len(extract.jtext.encode(r["jp"])):
                long_code.append(f"{r['id']} {r['jp']} -> {en}")
                if r["en"]:
                    r["en"] = ""
                    changed = True
                continue
            if r["en"] != en:
                r["en"] = en
                changed = True
                n += 1
        if changed:
            extract.write_tsv(p, rows)
    if long_code:
        print(f"{len(long_code)} EXE/overlay rows left for phase 7 (longer than the JP):", *long_code, sep="\n  ")
    print(f"merged {len(trans)} translations, {n} rows changed; failed batches: {bad or 'none'}")
    return 1 if bad else 0


def main(argv):
    cmd = argv[0] if argv else ""
    if cmd == "split":
        split()
    elif cmd == "check":
        rc = 0
        for b in argv[1:]:
            e = check(b)
            print(f"{b}: OK" if not e else f"{b}: {len(e)} errors", *e, sep="\n  ")
            rc |= bool(e)
        return rc
    elif cmd == "merge":
        return merge()
    elif cmd == "todo":
        print(" ".join(p.stem for p in sorted(BATCHES.glob("b*.tsv")) if not (OUT / p.name).exists()))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
