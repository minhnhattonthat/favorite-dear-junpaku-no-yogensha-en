"""plates.py: English battle unit name plates (G8, GRPDATA Name_NNN.PIX; format in tools/pix.py).

    python -X utf8 tools/plates.py check              # every `en` in gfx/plates.tsv fits 64 px (exit 1 if not)
    python -X utf8 tools/plates.py sheet OUT.png      # preview: JP plate above the English one, zoom 3

The build calls `changes()`: {"GRPDATA": {entry name: 384 bytes}} for every row with an `en`. Letters come from
fonts/font6.txt (the in-game English font), set proportionally: each glyph's ink width + 1 px, space 3 px, cap top on
plate row 2 like the Japanese glyphs (rows 2-10), descenders to row 11. Ink = level 7 (the plates' brightest)."""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
import pix  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TSV = ROOT / "gfx" / "plates.tsv"
SRC = ROOT / "work" / "lkf" / "GRPDATA"
W, H = pix.W, pix.H
TOP, LEFT, SPACE, INK = 2, 1, 3, 7


def rows():
    out = []
    for line in TSV.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        c = line.split("\t")
        assert len(c) in (3, 4), f"plates.tsv: want idx, jp, en[, notes]: {line!r}"
        c += [""] * (4 - len(c))
        out.append({"idx": int(c[0]), "jp": c[1], "en": c[2], "notes": c[3]})
    assert [r["idx"] for r in out] == list(range(88)), "plates.tsv: want rows 0-87 in order"
    return out


def _src(idx):
    """work/lkf/GRPDATA file of plate idx, in archive order: 0-80 = Name_000..NAME_080 (enemies and event units;
    the case varies), 81-87 = Name_B00..B06 (the seven heroes)."""
    files = sorted(p for p in SRC.iterdir() if p.name.lower().endswith(".pix") and "_name_" in p.name.lower())
    assert len(files) == 88, len(files)
    return files[idx]


def entry_name(idx):
    """The LKF entry name as the archive spells it."""
    return _src(idx).name.split("_", 1)[1]


def glyph(ch, font):
    g = font[ch]
    width = max((len(r.rstrip(".")) for r in g), default=0)
    return g, width


def width(text, font=None):
    font = font or font_en.load_font()
    w = 0
    for ch in text:
        w += SPACE if ch == " " else glyph(ch, font)[1] + 1
    return LEFT + w - 1


def render(text, font=None):
    """64x12 list of levels 0-7."""
    font = font or font_en.load_font()
    assert width(text, font) <= W, f"{text!r}: {width(text, font)} px > {W}"
    px = [[0] * W for _ in range(H)]
    x = LEFT
    for ch in text:
        if ch == " ":
            x += SPACE
            continue
        g, w = glyph(ch, font)
        for y, r in enumerate(g):
            for dx, c in enumerate(r):
                if c == "#":
                    px[TOP + y][x + dx] = INK
        x += w + 1
    return px


def encode(px):
    out = bytearray()
    for row in px:
        for x in range(0, W, 2):
            out.append(row[x] | row[x + 1] << 4)
    assert len(out) == W * H // 2
    return bytes(out)


def changes():
    font = font_en.load_font()
    return {"GRPDATA": {entry_name(r["idx"]): encode(render(r["en"], font)) for r in rows() if r["en"]}}


def check():
    font = font_en.load_font()
    bad = []
    for r in rows():
        if not r["en"]:
            bad.append(f"{r['idx']} {r['jp']}: no English")
            continue
        miss = [ch for ch in r["en"] if ch != " " and ch not in font]
        if miss:
            bad.append(f"{r['idx']} {r['en']!r}: no glyph for {miss}")
        elif width(r["en"], font) > W:
            bad.append(f"{r['idx']} {r['en']!r}: {width(r['en'], font)} px > {W}")
    for b in bad:
        print(b)
    print(f"plates: {88 - len(bad)}/88 ok")
    return not bad


def sheet(out, cols=4, zoom=3):
    font = font_en.load_font()
    rs = rows()
    cell_h = 2 * H + 3
    img = Image.new("L", ((W + 2) * cols, cell_h * ((len(rs) + cols - 1) // cols)), 60)
    for k, r in enumerate(rs):
        x, y = (k % cols) * (W + 2), (k // cols) * cell_h
        img.paste(pix.decode(_src(r["idx"]).read_bytes()), (x, y))
        if r["en"] and width(r["en"], font) <= W:
            img.paste(pix.decode(encode(render(r["en"], font))), (x, y + H + 1))
    img.resize((img.width * zoom, img.height * zoom), Image.NEAREST).save(out)
    print(out)


if __name__ == "__main__":
    if sys.argv[1:2] == ["check"]:
        sys.exit(0 if check() else 1)
    if sys.argv[1:2] == ["sheet"] and len(sys.argv) == 3:
        sheet(sys.argv[2])
        sys.exit(0)
    sys.exit(__doc__)
