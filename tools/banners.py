"""banners.py: English battle status tags (G3) and skill banners (G4) in GRPDATA an_mag_0.tim (entry 0057).

    python -X utf8 tools/banners.py check            # every `en` in gfx/banners.tsv fits (exit 1 if not)
    python -X utf8 tools/banners.py sheet OUT.png    # JP above EN, zoom 3, CLUT 13 (grey ramp) and CLUT 2

The image is 4 bpp with 16 CLUTs; the battle draws it through several of them, and every CLUT keeps the same index
roles (0 transparent, 1-4 dark, c-f light), so the redraw works on indices, never colours.
- Tags (36x16 at (40*idx, 184)): stone texture with outlined light letters. The JP letters are erased by taking, at
  each pixel, the median of the six tags; the English is set in fonts/font_tag.txt (narrow), index 0xF with a 0x2
  outline (8-neighbour), centred.
- Banners (16 rows; idx 0-2 at x 0, y 208/224/240; idx 3-5 at x 104): a gradient pill with dark text. The text rows
  (2-12) of the pill body are rebuilt from the most common light value (>= 0xC) of the six pills at the same column
  (the gradient steps at fixed columns from the left), the right cap from the most common value at the same distance
  from the right end. The pill keeps its original width (the sprite rect is unknown). English in fonts/font6.txt,
  index 0x2, from x 5, cap top on row 3.
The build calls `changes()`: {"GRPDATA": {"an_mag_0.tim": bytes}}."""
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
import tim  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TSV = ROOT / "gfx" / "banners.tsv"
SRC = ROOT / "work" / "lkf" / "GRPDATA" / "0057_an_mag_0.tim"
ENTRY = "an_mag_0.tim"
TAG_FONT = ROOT / "fonts" / "font_tag.txt"
W = 256
TAG_W, TAG_H, TAG_Y = 36, 16, 184
TAG_TOP, TAG_INK, TAG_EDGE = 4, 0xF, 0x2
BAN_Y = (208, 224, 240)
BAN_X = (0, 104)
BAN_LEFT, BAN_TOP, BAN_INK, BAN_ROWS = 5, 3, 0x2, range(2, 13)
LEFT_CAP, RIGHT_CAP, RIGHT_PAD = 4, 4, 4


def rows():
    out = []
    for line in TSV.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        c = line.split("\t")
        assert len(c) in (4, 5), f"banners.tsv: want kind, idx, jp, en[, notes]: {line!r}"
        out.append({"kind": c[0], "idx": int(c[1]), "jp": c[2], "en": c[3]})
    assert [(r["kind"], r["idx"]) for r in out] == [("tag", i) for i in range(6)] + [("banner", i) for i in range(6)]
    return out


def glyph(ch, font):
    g = font[ch]
    return g, max((len(r.rstrip(".")) for r in g), default=0)


def text_width(text, font, space):
    w = 0
    for ch in text:
        w += space if ch == " " else glyph(ch, font)[1] + 1
    return w - 1


def ink(text, font, space):
    """-> set of (x, y) ink pixels, x from 0."""
    pts, x = set(), 0
    for ch in text:
        if ch == " ":
            x += space
            continue
        g, w = glyph(ch, font)
        for y, r in enumerate(g):
            for dx, c in enumerate(r):
                if c == "#":
                    pts.add((x + dx, y))
        x += w + 1
    return pts


def source():
    return tim.parse(SRC.read_bytes())["pix"]


def pill_width(pix, x0, y0):
    """The pill's width on its middle row (the background grid is 0 right after it)."""
    row = pix[(y0 + 7) * W + x0:(y0 + 8) * W]
    e = 0
    while row[e]:
        e += 1
    return e


def banners():
    return [(BAN_X[i // 3], BAN_Y[i % 3]) for i in range(6)]


def tag_budget():
    return TAG_W - 4


def banner_budget(pix, i):
    x0, y0 = banners()[i]
    return pill_width(pix, x0, y0) - BAN_LEFT - RIGHT_PAD


def render(pix, rs=None):
    """-> new index list with every row that has an `en`."""
    rs = rs or rows()
    out = list(pix)
    tf, bf = font_en.load_font(TAG_FONT), font_en.load_font()
    for r in rs:
        if not r["en"]:
            continue
        if r["kind"] == "tag":
            x0 = TAG_W * 0 + 40 * r["idx"]
            for y in range(TAG_H):
                for x in range(TAG_W):
                    out[(TAG_Y + y) * W + x0 + x] = int(statistics.median_low(
                        pix[(TAG_Y + y) * W + 40 * k + x] for k in range(6)))
            pts = ink(r["en"], tf, 2)
            tw = text_width(r["en"], tf, 2)
            left = x0 + (TAG_W - tw) // 2
            edge = {(x + dx, y + dy) for x, y in pts for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - pts
            for col, ps in ((TAG_EDGE, edge), (TAG_INK, pts)):
                for x, y in ps:
                    out[(TAG_Y + TAG_TOP + y) * W + left + x] = col
        else:
            x0, y0 = banners()[r["idx"]]
            wid = pill_width(pix, x0, y0)
            pills = [(bx, by, pill_width(pix, bx, by)) for bx, by in banners()]
            for ry in BAN_ROWS:
                for rx in range(LEFT_CAP, wid):
                    from_right = wid - rx
                    if from_right <= RIGHT_CAP:
                        vals = [pix[(by + ry) * W + bx + pw - from_right] for bx, by, pw in pills]
                        v = Counter(vals).most_common(1)[0][0]
                    else:
                        vals = [pix[(by + ry) * W + bx + rx] for bx, by, pw in pills if rx < pw - RIGHT_CAP]
                        vals = [v for v in vals if v >= 0xC]
                        v = Counter(vals).most_common(1)[0][0] if vals else out[(y0 + ry) * W + x0 + rx - 1]
                    out[(y0 + ry) * W + x0 + rx] = v
            for x, y in ink(r["en"], bf, 3):
                out[(y0 + BAN_TOP + y) * W + x0 + BAN_LEFT + x] = BAN_INK
    return out


def changes():
    data = SRC.read_bytes()
    return {"GRPDATA": {ENTRY: tim.with_pixels(data, render(tim.parse(data)["pix"]))}}


def check():
    pix = source()
    tf, bf = font_en.load_font(TAG_FONT), font_en.load_font()
    bad = []
    for r in rows():
        if not r["en"]:
            continue
        if r["kind"] == "tag":
            missing = [c for c in r["en"] if c != " " and c not in tf]
            w, budget = (text_width(r["en"], tf, 2) if not missing else 999), tag_budget()
        else:
            missing = [c for c in r["en"] if c != " " and c not in bf]
            w, budget = (text_width(r["en"], bf, 3) if not missing else 999), banner_budget(pix, r["idx"])
        if missing or w > budget:
            bad.append(f"{r['kind']} {r['idx']} {r['en']!r}: {w} px > {budget}" + (f" (no glyph {missing})" if missing else ""))
    for b in bad:
        print(b)
    print(f"banners: {len(rows())} rows, {len(bad)} over budget")
    return not bad


def sheet(out, zoom=3):
    from PIL import Image
    data = SRC.read_bytes()
    t = tim.parse(data)
    t2 = dict(t, pix=render(t["pix"]))
    crop = (0, 180, 232, 256)
    parts = [tim.to_image(x, c).crop(crop) for c in (13, 2) for x in (t, t2)]
    w, h = crop[2] - crop[0], crop[3] - crop[1]
    im = Image.new("RGB", (w, h * len(parts)))
    for i, p in enumerate(parts):
        im.paste(p, (0, i * h))
    im.resize((w * zoom, h * len(parts) * zoom), Image.NEAREST).save(out)
    print(out)


if __name__ == "__main__":
    if sys.argv[1:2] == ["check"]:
        sys.exit(0 if check() else 1)
    if sys.argv[1:2] == ["sheet"]:
        sheet(sys.argv[2])
