"""album.py: English OMAKE album profile panel (G10): the text atlas GRPDATA 1454 ALBUM_03.TIM, 4 bpp, 16 CLUTs.

    python -X utf8 tools/album.py check            # every `en` in gfx/album.tsv fits its rect (exit 1 if not)
    python -X utf8 tools/album.py sheet OUT.png    # the atlas, JP left / EN right, zoom 3, CLUT 0

The album draws fixed rects of the atlas (gfx/album.tsv, found with tools/debug/ramdump.lua + tools/sprites.py;
the rects come from code, not a table, so they keep their size and screen place). Each listed rect is cleared to
index 0 (transparent) and its English drawn with ink index 0xE and a 1 px drop shadow (+1,+1) of index 0x3, like the
JP's light glyphs with dark edges. Height/weight rects (216, 32k; "187cm 81kg") are Latin already and stay.
Fonts: label = fonts/label14.txt (DejaVu Sans Condensed 14 px, tools/labelfont.py), small = fonts/font6.txt,
tag = fonts/font_tag.txt. Letters 1 px apart; when a line is 1-2 px too wide, pairs that do not touch close up.
The build calls `changes()`: {"GRPDATA": {"ALBUM_03.TIM": bytes}}."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
import labelfont  # noqa: E402
import tim  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TSV = ROOT / "gfx" / "album.tsv"
SRC = ROOT / "work" / "lkf" / "GRPDATA" / "1454_ALBUM_03.TIM"
ENTRY = "ALBUM_03.TIM"
W = 256
INK, SHADOW = 0xE, 0x3
COL_GAP = 5


def _font_rows(path):
    """font_en format -> {char: (width, [row bit masks])}, cap top row 0, cap height 8 (font6) / 7 (tag)."""
    out = {}
    for ch, rows in font_en.load_font(path).items():
        w = max((len(r.rstrip(".")) for r in rows), default=0)
        out[ch] = (w, [sum(1 << x for x, c in enumerate(r) if c == "#") for r in rows])
    return out


_FONTS = {}


def font(name):
    """-> (glyphs {char: (width, masks)}, first cap row, cap height, space px)"""
    if name not in _FONTS:
        if name == "label":
            _FONTS[name] = (labelfont.glyphs(), labelfont.CAP[0], labelfont.CAP[1] - labelfont.CAP[0] + 1,
                            labelfont.SPACE)
        elif name == "small":
            _FONTS[name] = (_font_rows(font_en.FONT), 0, 8, 3)
        else:
            _FONTS[name] = (_font_rows(ROOT / "fonts" / "font_tag.txt"), 0, 7, 2)
    return _FONTS[name]


def layout(text, fname, tight=False):
    """-> (set of (x, y) ink points, width); y 0 = the font's row 0."""
    g, _, _, space = font(fname)
    pts, x, prev = set(), 0, None
    for ch in text:
        if ch == " ":
            x += space
            prev = None
            continue
        if ch not in g:
            raise KeyError(f"{ch!r} not in font {fname}")
        w, masks = g[ch]
        gap = 1 if x else 0
        if tight and prev is not None:
            last = prev
            first = [m & 1 for m in masks]
            touch = any(first[y] and (last[y] or (y and last[y - 1]) or (y + 1 < len(last) and last[y + 1]))
                        for y in range(min(len(first), len(last))))
            gap = 1 if touch else 0
        if x:
            x += gap
        for y, m in enumerate(masks):
            for dx in range(w):
                if m >> dx & 1:
                    pts.add((x + dx, y))
        prev = [m >> (w - 1) & 1 for m in masks] if w else None
        x += w
    return pts, x


def rows():
    out = []
    for line in TSV.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        c = line.split("\t")
        assert 6 <= len(c) <= 10, f"album.tsv: want u v w h jp en [align tops font notes]: {line!r}"
        c += [""] * (10 - len(c))
        out.append({"u": int(c[0]), "v": int(c[1]), "w": int(c[2]), "h": int(c[3]), "jp": c[4], "en": c[5],
                    "align": c[6] or "l", "tops": [int(t) for t in c[7].split(",")] if c[7] else None,
                    "font": c[8]})
    return out


def line_points(text, fname, colx, tight):
    """A line with an optional ' | ' second column (starting at colx) -> (points, width)."""
    cols = text.split(" | ")
    assert len(cols) <= 2
    pts, last = set(), 0
    for i, col in enumerate(cols):
        p, w = layout(col, fname, tight)
        x = colx if i else 0
        pts |= {(a + x, b) for a, b in p}
        last = x + w
    return pts, last


def place(r):
    """-> (font, {(x, y) ink in the rect}) or raise ValueError when nothing fits."""
    lines = r["en"].split(" / ")
    names = [r["font"]] if r["font"] else ["label", "small", "tag"]
    n = len(lines)
    for fname in names:
        for tight in (False, True):
            _, cap0, caph, _ = font(fname)
            g = font(fname)[0]
            if any(ch not in g for ln in lines for ch in ln.replace(" | ", "") if ch != " "):
                break
            line_h = r["h"] // n
            tops = r["tops"] or [i * line_h for i in range(n)]
            ink, ok = set(), True
            colx = max((layout(ln.split(" | ")[0], fname, tight)[1] for ln in lines if " | " in ln), default=0)
            for i, ln in enumerate(lines):
                pts, w = line_points(ln, fname, colx + COL_GAP, tight)
                al = r["align"][i] if i < len(r["align"]) else r["align"][-1]
                x0 = 1 if al == "l" else r["w"] - 1 - w - 1 if al == "r" else (r["w"] - 1 - w) // 2
                lh = (tops[i + 1] if i + 1 < n else r["h"]) - tops[i] if r["tops"] else line_h
                y0 = tops[i] + (lh - caph) // 2 - cap0 if not r["tops"] else tops[i] + max(0, (lh - 1 - caph) // 2) - cap0
                low = max(b for _, b in pts) + y0 - (tops[i] + lh - 2)   # descenders: nudge up, at most 3 px
                if 0 < low <= 3 and min(b for _, b in pts) + y0 - low >= tops[i]:
                    y0 -= low
                for a, b in pts:
                    x, y = x0 + a, y0 + b
                    if not (0 <= x < r["w"] - 1 and 0 <= y < r["h"] - 1):
                        ok = False
                    ink.add((x, y))
            if ok:
                return fname + (" tight" if tight else ""), ink
    raise ValueError(f"{r['en']!r} does not fit {r['w']}x{r['h']}")


def render(pix):
    out = list(pix)
    for r in rows():
        if not r["en"]:
            continue
        _, ink = place(r)
        for y in range(r["h"]):
            for x in range(r["w"]):
                out[(r["v"] + y) * W + r["u"] + x] = 0
        shadow = {(x + 1, y + 1) for x, y in ink} - ink
        for col, pts in ((SHADOW, shadow), (INK, ink)):
            for x, y in pts:
                out[(r["v"] + y) * W + r["u"] + x] = col
    return out


def changes():
    data = SRC.read_bytes()
    return {"GRPDATA": {ENTRY: tim.with_pixels(data, render(tim.parse(data)["pix"]))}}


def check(verbose=False):
    bad = 0
    for r in rows():
        try:
            f, _ = place(r)
            if verbose:
                print(f"{r['u']:3d},{r['v']:3d} {r['w']}x{r['h']} {f:12s} {r['en']}")
        except (ValueError, KeyError) as e:
            print(f"{r['u']},{r['v']}: {e}")
            bad += 1
    print(f"album: {len(rows())} rows, {bad} do not fit")
    return not bad


def sheet(out, zoom=3, clut=0):
    from PIL import Image
    t = tim.parse(SRC.read_bytes())
    a = tim.to_image(t, clut)
    b = tim.to_image(dict(t, pix=render(t["pix"])), clut)
    im = Image.new("RGB", (W * 2 + 4, 256), (0, 0, 0))
    im.paste(a, (0, 0))
    im.paste(b, (W + 4, 0))
    im.resize((im.width * zoom, im.height * zoom), Image.NEAREST).save(out)
    print(out)


if __name__ == "__main__":
    if sys.argv[1:2] == ["check"]:
        sys.exit(0 if check(verbose=True) else 1)
    if sys.argv[1:2] == ["sheet"]:
        sheet(sys.argv[2])
