"""marker.py: the phase-5 marker build. Every text row becomes `<label> <filler>` in English pair glyphs, at exactly
the row's Japanese byte length (one Japanese character = one cell = two letters), so no file, record or jump moves
and every box shows which row it came from.

    python -X utf8 tools/build.py --marker               -> build/fd2_marker.bin/.cue
    python -X utf8 tools/marker.py LABEL [LABEL..]       label -> row id and Japanese text
    python -X utf8 tools/marker.py --id ROW_ID           row id -> label

Label = the row's index in extract order, in base 36 (3 characters, upper case). Tags ({n}, {wait}, ops) stay in
place; ＄ (name placeholder) and ￥ (quiz line break) stay as they are. Rows left Japanese: rows with no Japanese
character, and the memory-card save titles (the BIOS card screen draws them with its own font)."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import font_en  # noqa: E402

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
FILLER = "quick brown fox jumps over the lazy dog. "
KEEP = {"＄", "￥"}
SKIP_JP = ("純白の預言者　ゲームデータ",)
DEBUG = re.compile(r"\w+\(\) ～ ")          # FontEntryBuf() ～ ... : debug printf to the TTY, never on screen


def label(n):
    s = ""
    for _ in range(3):
        n, d = divmod(n, 36)
        s = DIGITS[d] + s
    assert n == 0
    return s


def labels():
    """{row id: label} over every source, in extract order (stable while script/ is)."""
    out, n = {}, 0
    for s in extract.sources():
        for r in s.rows:
            out[r.id] = label(n)
            n += 1
    return out


def is_japanese(ch):
    return ord(ch) >= 0x3000 and ch not in KEEP


def marker_text(lab, jp):
    if not any(is_japanese(ch) for p in font_en.FMT.split(jp) if not font_en.FMT.fullmatch(p) for ch in p):
        return None
    if any(k in jp for k in SKIP_JP) or DEBUG.search(jp):
        return None
    stream = (lab + " " + FILLER * 200).replace("_", "-")
    pos, out = 0, []
    for part in font_en.FMT.split(jp):
        if not part:
            continue
        if font_en.FMT.fullmatch(part):
            out.append(part)
            continue
        run = 0                                  # letters (= bytes) to fill
        for ch in part:
            if ch in KEEP:
                out.append(stream[pos:pos + run - run % 2])
                pos += run - run % 2
                run = 0
                out.append(ch)
            else:
                run += 1 if ord(ch) < 0x80 else 2
        out.append(stream[pos:pos + run - run % 2])
        pos += run - run % 2
    return "".join(out)


_LABELS = None


def texts_for(source):
    global _LABELS
    if _LABELS is None:
        _LABELS = labels()
    out = {}
    for r in source.rows:
        t = marker_text(_LABELS[r.id], r.jp)
        if t is not None:
            out[r.id] = t
    return out


LINE_TAGS = {"{n}", "{clear}", "\\l", "\\c"}


def ruler_char(p):
    """letter at 1-based line position p: a digit every 10, ':' every 5, '.' else"""
    return str(p // 10 % 10) if p % 10 == 0 else ":" if p % 5 == 0 else "."


def ruler_text(lab, jp, scale=3):
    """Width-gate build (build.py --ruler): each Japanese character becomes `scale` letters (3 = 1.5 cells) of a
    position ruler that restarts at every line break, so the clip column of each box variant reads off the screen;
    the row's label replaces the first 4 letters."""
    if marker_text(lab, jp) is None:
        return None
    out, p, first = [], 0, True
    for part in font_en.FMT.split(jp):
        if not part:
            continue
        if font_en.FMT.fullmatch(part):
            out.append(part)
            if part in LINE_TAGS or "clear" in part:
                p = 0
            continue
        buf = []
        for ch in part:
            if ch in KEEP:
                buf.append(ch)
                continue
            n = scale if ord(ch) >= 0x80 else 1
            for _ in range(n):
                p += 1
                buf.append(ruler_char(p))
        s = "".join(buf)
        if first and s:
            s = (lab + " " + s[4:]) if len(s) >= 4 else s
            first = False
        letters = sum(1 for c in s if c not in KEEP)
        out.append(s + (" " if letters % 2 else ""))
    return "".join(out)


def ruler_texts_for(source):
    """ruler rows where the source can grow; marker rows (same length) where it can't (fixed fields, EXE/overlays)"""
    global _LABELS
    if _LABELS is None:
        _LABELS = labels()
    texts = {}
    for r in source.rows:
        t = ruler_text(_LABELS[r.id], r.jp)
        if t is not None:
            texts[r.id] = t
    marker = texts_for(source)
    fixed = {r.id for r in source.rows if any(w in r.notes for w in ("field", "record", "label"))}
    for cand in (texts, {k: marker[k] if k in fixed else t for k, t in texts.items()}):
        try:
            source.build({k: font_en.to_pairs(t) for k, t in cand.items()})
            return cand
        except (AssertionError, ValueError) as e:
            err = str(e)[:60]
    print(f"ruler: {source.tsv.name} stays marker ({err})", file=sys.stderr)
    return marker


def main(argv):
    lab = labels()
    if argv and argv[0] == "--id":
        for i in argv[1:]:
            print(i, lab.get(i))
        return
    rev = {v: k for k, v in lab.items()}
    jp = {}
    for s in extract.sources():
        for r in s.rows:
            jp[r.id] = r.jp
    for a in argv:
        i = rev.get(a.upper())
        print(a.upper(), i, jp.get(i, "")[:80])


if __name__ == "__main__":
    main(sys.argv[1:])
