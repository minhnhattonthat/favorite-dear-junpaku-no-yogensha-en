"""labelfont.py: the proportional label font for redrawn status-screen graphics (fonts/label14.txt).

    python -X utf8 tools/labelfont.py make DejaVuSansCondensed.ttf   rasterize ASCII 0x21-0x7E at 14 px, no smoothing
    python -X utf8 tools/labelfont.py png OUT.png                    every glyph, 4x, for checking

The .txt is the source the build reads (no FreeType needed at build time): one glyph per block, a header line
`XX c` (hex code, the character), then HEIGHT rows of '.'/'#', trimmed to the ink columns. A capital spans rows
1-10 (CAP), descenders reach row 13. Letters are set with 1 px between them and SPACE px for a space.
Source font: DejaVu Sans Condensed 2.37 (Bitstream Vera licence + public domain changes; docs/fonts.md)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "fonts" / "label14.txt"
HEIGHT, BASE, SPACE, SIZE = 15, 11, 3, 14  # BASE: make() places the font's 'H' box bottom here (ink ends a row higher)
CAP = (1, 10)


NARROW = ROOT / "fonts" / "narrow3x7.txt"
FONTS = {"label": (SRC, HEIGHT, CAP[0]), "narrow": (NARROW, 7, 0)}  # name: (file, rows, first cap row)


def glyphs(path=SRC, height=HEIGHT):
    """{char: (width, [row bit masks, bit x = column x])}"""
    out, cur = {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("# "):
            continue
        if line[0] in ".#":
            cur[1].append(sum(1 << x for x, ch in enumerate(line) if ch == "#"))
            cur[0] = max(cur[0], len(line))
        else:
            cur = [0, []]
            out[chr(int(line.split()[0], 16))] = cur
    for c, (w, rows) in out.items():
        if len(rows) != height:
            raise ValueError(f"{path}: glyph {c!r} has {len(rows)} rows, not {height}")
    return {c: (w, rows) for c, (w, rows) in out.items()}


def columns(text, path=SRC, height=HEIGHT):
    """the text as a list of column bit masks (bit y = row y), 1 px between letters"""
    g = glyphs(path, height)
    cols = []
    for i, ch in enumerate(text):
        if i:
            cols.append(0)
        if ch == " ":
            cols += [0] * (SPACE - 1)
            continue
        if ch not in g:
            raise ValueError(f"{ch!r} is not in {path.name}")
        w, rows = g[ch]
        cols += [sum(1 << y for y in range(height) if rows[y] >> x & 1) for x in range(w)]
    return cols


def make(ttf):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(str(ttf), SIZE)
    cap_top, base = font.getbbox("H")[1], font.getbbox("H")[3] - 1  # rows of a capital H drawn at y = 0
    lines = [f"# label14: {Path(ttf).name} at {SIZE} px, rasterized with no smoothing by tools/labelfont.py make.",
             f"# {HEIGHT} rows per glyph, baseline row {BASE}; trimmed to ink columns; '#' = ink."]
    for code in range(0x21, 0x7F):
        im = Image.new("1", (32, 32), 0)
        d = ImageDraw.Draw(im)
        d.fontmode = "1"
        d.text((4, 0), chr(code), font=font, fill=1)
        top = base - BASE
        px = im.load()
        cols = [x for x in range(32) if any(px[x, y] for y in range(32))]
        lines.append(f"{code:02X} {chr(code)}")
        for y in range(top, top + HEIGHT):
            lines.append("".join("#" if px[x, y] else "." for x in range(cols[0], cols[-1] + 1)))
        lost = [y for y in range(32) if not top <= y < top + HEIGHT and any(px[x, y] for x in range(32))]
        if lost:
            print(f"{chr(code)!r}: rows {lost} fall outside the {HEIGHT}-row cell (cap top {cap_top})")
    SRC.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(SRC)


def png(out):
    from PIL import Image
    g = glyphs()
    text = "".join(sorted(g))
    cols = columns(text)
    im = Image.new("L", (len(cols) + 4, HEIGHT + 4), 0)
    for x, c in enumerate(cols):
        for y in range(HEIGHT):
            if c >> y & 1:
                im.putpixel((x + 2, y + 2), 255)
    im.resize((im.width * 4, im.height * 4), Image.NEAREST).save(out)
    print(out)


if __name__ == "__main__":
    {"make": make, "png": png}[sys.argv[1]](sys.argv[2])
