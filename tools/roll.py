"""roll.py: the ENDING.STR staff roll in English (G15), used by `tools/fmv.py`.

The roll is one tall strip of credit lines scrolling up at exactly 1.5 px/frame (screen y = Y - 1.5 (n - N0), strip
row Y) from frame N0 until frame STOP, then it holds; beside it the gold ornament panel (x < ~152) scrolls at
0.19 px/frame, and the lines are centred on x = 160, so about half of each line sits on the panel. `gfx/roll.tsv`
has one row per Japanese line: its box in strip coordinates (y0 y1 x0 x1, measured from a median strip of all
frames, `roll.py bands`), a style and the English (`keep` rows are already Latin: URLs, WAND, SOFIX...).

Per frame: every Japanese line box on screen is refilled from nearby frames where that spot is free of text (the
text moved 1.5 px/frame, the panel only 0.19, so a source frame shifted by the panel motion gives the clean panel),
then the English strip (rendered at 2x, cut at the frame's half-pixel offset and averaged down, like the original's
interpolated scroll) is drawn with the measured fade of the Japanese.

    python -X utf8 tools/roll.py bands               # line boxes of the original (to check roll.tsv)
    python -X utf8 tools/roll.py sheet --out work/fmv/roll_en.png   # the English strip, for reading"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "gfx/roll.tsv"
FONTS = ROOT / "fonts/crimson"
MOVIE = "ENDING.STR"
N0, STOP, LAST = 330, 4114, 4218    # scroll origin frame, last scrolling frame, last frame of the movie
SPEED, PANEL = 1.5, 0.19            # px/frame: credit lines, ornament panel
MARGIN = 3                          # px around each Japanese line box
CANDS = [8, -8, 16, -16, 24, -24, 32, -32, 40, -40, 56, -56, 72, -72, 96, -96]
YMIN = -240                         # strip rows above the first line (frames before N0 have negative offsets)
W, H = 320, 224
STYLES = {   # style: (font file, size px at 1x)
    "head": ("CrimsonText-Bold.ttf", 17),
    "crole": ("CrimsonText-SemiBold.ttf", 13),
    "srole": ("CrimsonText-SemiBold.ttf", 14),
    "name": ("CrimsonText-Bold.ttf", 17),
    "name2": ("CrimsonText-Bold.ttf", 15),
    "co": ("CrimsonText-Bold.ttf", 17),
}
COL2 = (28, 169)                  # name2 rows: left edges of the two name columns
CENTRE = 160
FILL = np.array([246, 244, 238], float)
SHADOW = np.array([14, 8, 0], float)
FULL = 252.0                      # 99th-percentile luminance of the Japanese text at full strength


def rows():
    with open(TABLE, encoding="utf-8", newline="") as f:
        out = []
        for r in csv.DictReader(f, delimiter="\t"):
            for k in ("y0", "y1", "x0", "x1"):
                r[k] = int(r[k])
            out.append(r)
    return out


def offset(n):
    return SPEED * (min(n, STOP) - N0)


def gauss(img, s):
    r = int(3 * s + 0.5)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / s) ** 2)
    k /= k.sum()
    out = img
    for axis in (0, 1):
        pad = [(0, 0)] * img.ndim
        pad[axis] = (r, r)
        p = np.pad(out, pad, mode="edge")
        acc = np.zeros_like(out)
        for i, w in enumerate(k):
            sl = [slice(None)] * img.ndim
            sl[axis] = slice(i, i + out.shape[axis])
            acc += w * p[tuple(sl)]
        out = acc
    return out


def font(style, scale=2):
    name, size = STYLES[style]
    return ImageFont.truetype(str(FONTS / name), size * scale)


def english_strip(table):
    """(premultiplied colour (h, 640, 3), alpha (h, 640)) at 2x of every English line, strip row Y at 2 (Y - YMIN)."""
    h = 2 * (max(r["y1"] for r in table) + 40 - YMIN)
    alpha = Image.new("L", (2 * W, h))
    d = ImageDraw.Draw(alpha)
    for r in table:
        if r["style"] == "keep":
            continue
        f = font(r["style"])
        _, ct, _, cb = f.getbbox("H")
        cy = (r["y0"] + r["y1"] + 1) - 2 * YMIN          # band centre at 2x
        y = cy - (ct + cb) / 2
        if r["style"] == "name2":
            parts = r["en"].split("|")
            assert len(parts) == 2, r
            for x, text in zip(COL2, parts):
                if text:
                    tw = d.textlength(text, font=f)
                    assert 2 * x + tw <= 2 * (COL2[1] - 6 if x == COL2[0] else W - 8), f"{text}: too wide"
                    d.text((2 * x, y), text, font=f, fill=255)
            continue
        tw = d.textlength(r["en"], font=f)
        x = 2 * CENTRE - tw / 2
        assert x >= 2 * 8 and x + tw <= 2 * (W - 8), f"{r['en']}: {tw / 2:.0f} px is too wide"
        d.text((x, y), r["en"], font=f, fill=255)
    a = np.asarray(alpha, np.float32) / 255
    sh = np.zeros_like(a)
    sh[2:, 2:] = a[:-2, :-2]
    sh = np.maximum(np.clip(gauss(sh, 1.5) * 1.6, 0, 0.9), np.clip(gauss(a, 1.2) * 1.5, 0, 0.6)) * (1 - a)
    A = a + sh
    col = FILL[None, None, :] * a[..., None] + SHADOW[None, None, :] * sh[..., None]
    return col.astype(np.float32), A.astype(np.float32)


class Roll:
    def __init__(self, movie):
        self.m = movie
        self.table = rows()
        self._eng = None
        self._raw = {}

    def boxes(self, n, keep=True):
        """Screen boxes (x0, y0, x1, y1), with MARGIN, of the Japanese lines on screen in frame n."""
        off = offset(n)
        out = []
        for r in self.table:
            if r["style"] == "keep" and not keep:
                continue
            y0, y1 = int(np.floor(r["y0"] - off)) - MARGIN, int(np.ceil(r["y1"] - off)) + MARGIN + 1
            if y1 <= 0 or y0 >= H:
                continue
            out.append((max(0, r["x0"] - MARGIN), max(0, y0), min(W, r["x1"] + MARGIN + 1), min(H, y1)))
        return out

    def box_mask(self, n, keep=True):
        m = np.zeros((H, W), bool)
        for x0, y0, x1, y1 in self.boxes(n, keep):
            m[y0:y1, x0:x1] = True
        return m

    def frames(self):
        return [n for n in range(N0 - 40, LAST + 1) if n in self.m.fr and self.boxes(n, keep=False)]

    def raw_alpha(self, n):
        """Strength of the Japanese text in frame n: 99th-percentile luminance of its boxes on the black side."""
        if n not in self._raw:
            m = self.box_mask(n)
            m[:, :158] = False
            lum = self.m.rgb(n).mean(2)[m]
            self._raw[n] = None if lum.size < 200 else float(np.percentile(lum, 99)) / FULL
        return self._raw[n]

    def alpha(self, n):
        vals = [v for v in (self.raw_alpha(k) for k in range(n - 3, n + 4) if k in self.m.fr) if v is not None]
        if not vals:
            return 1.0
        a = float(np.median(vals))
        return 1.0 if a > 0.9 else max(0.0, a)

    def clean(self, n, todo):
        """Frame n with the `todo` pixels refilled from text-free spots of nearby frames (panel-aligned)."""
        rgb = self.m.rgb(n)
        out = rgb.copy()
        todo = todo.copy()
        ring = fmv_dilate(todo, 4) & ~todo
        ys = np.arange(H, dtype=float)
        for k in CANDS:
            src_n = n + k
            if src_n not in self.m.fr or src_n < N0 - 40:
                continue
            d = PANEL * (min(src_n, STOP) - min(n, STOP))     # panel at y in frame n is at y - d in frame src_n
            sy = ys - d
            y0 = np.floor(sy).astype(int)
            f = (sy - y0)[:, None, None]
            ok = (y0 >= 0) & (y0 + 1 < H)
            y0c = np.clip(y0, 0, H - 2)
            src = self.m.rgb(src_n)
            samp = src[y0c] * (1 - f) + src[y0c + 1] * f
            cov = self.box_mask(src_n)
            cov = cov[y0c] | cov[y0c + 1] | ~ok[:, None]
            r = ring & ~cov
            g = 1.0
            if r.sum() > 20 and rgb[r].mean() > 12:
                g = np.clip(rgb[r].mean(0) / np.maximum(samp[r].mean(0), 1), 0.6, 1.6)
            use = todo & ~cov
            out[use] = np.clip(samp[use] * g, 0, 255)
            todo &= ~use
            if not todo.any():
                break
        if todo.any():
            out = fmv_inpaint(out, todo)
        return out

    def english(self, n):
        if self._eng is None:
            self._eng = english_strip(self.table)
        col, a = self._eng
        top = int(round(2 * (offset(n) - YMIN)))
        assert top >= 0 and top + 2 * H <= a.shape[0], n
        c = col[top:top + 2 * H].reshape(H, 2, W, 2, 3).mean((1, 3))
        al = a[top:top + 2 * H].reshape(H, 2, W, 2).mean((1, 3))
        return c, al

    def edit(self, n):
        """(edited RGB, changed-pixel mask) of frame n, or None when no Japanese line shows."""
        al = self.alpha(n)
        if al <= 0.02:
            return None
        todo = self.box_mask(n, keep=False)
        out = self.clean(n, todo)
        c, a = self.english(n)
        out = out * (1 - a[..., None] * al) + c * al
        return np.clip(np.round(out), 0, 255), todo | (a * al > 0.01)


def fmv_dilate(m, n):
    for _ in range(n):
        p = np.pad(m, 1)
        m = p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    return m


def fmv_inpaint(rgb, mask, iters=80):
    out = rgb.copy()
    known = ~mask
    out[mask] = 0
    for _ in range(iters):
        if known.all():
            break
        p = np.pad(out, ((1, 1), (1, 1), (0, 0)))
        k = np.pad(known.astype(float), 1)
        s = p[:-2, 1:-1] * k[:-2, 1:-1, None] + p[2:, 1:-1] * k[2:, 1:-1, None] + \
            p[1:-1, :-2] * k[1:-1, :-2, None] + p[1:-1, 2:] * k[1:-1, 2:, None]
        nb = k[:-2, 1:-1] + k[2:, 1:-1] + k[1:-1, :-2] + k[1:-1, 2:]
        new = (nb > 0) & ~known
        out[new] = s[new] / nb[new][:, None]
        known = known | new
    return out


def median_strip(movie):
    """Median over every even scrolling frame of each strip row (the text is still in strip coordinates, the panel
    moves): the Japanese lines on a smeared panel."""
    h = int(offset(STOP)) + H
    out = np.zeros((h, W, 3), np.uint8)
    for Y0 in range(0, h, 100):
        Y1 = min(h, Y0 + 100)
        st = []
        for n in range(N0, STOP + 1, 2):
            off = int(offset(n))
            if off + H <= Y0 or off >= Y1:
                continue
            buf = np.full((Y1 - Y0, W, 3), np.nan, np.float32)
            a, b = max(Y0, off), min(Y1, off + H)
            buf[a - Y0:b - Y0] = movie.rgb(n)[a - off:b - off]
            st.append(buf)
        out[Y0:Y1] = np.nan_to_num(np.nanmedian(np.stack(st), 0)).astype(np.uint8)
        for k in [k for k in movie._rgb if int(offset(k)) + H < Y0]:
            del movie._rgb[k]
    return out


def bands(med):
    """Line boxes (y0, y1, x0, x1) of white low-saturation text in the median strip."""
    med = med.astype(int)
    m = (med.min(2) > 120) & (med.max(2) - med.min(2) < 60)
    on = np.nonzero(m.sum(1) >= 2)[0]
    out = []
    s = p = on[0]
    for y in list(on[1:]) + [10 ** 7]:
        if y > p + 2:
            cols = np.nonzero(m[s:p + 1].sum(0))[0]
            if p - s >= 4:
                out.append((int(s), int(p), int(cols.min()), int(cols.max())))
            s = y
        p = y
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["bands", "sheet"])
    ap.add_argument("--out", default="work/fmv/roll_en.png")
    a = ap.parse_args()
    if a.cmd == "bands":
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import fmv
        got = bands(median_strip(fmv.Movie(MOVIE)))
        want = [(r["y0"], r["y1"], r["x0"], r["x1"]) for r in rows()]
        print(f"{len(got)} lines in the movie, {len(want)} in {TABLE.name}")
        for g, w in zip(got, want):
            if g != w:
                print("differs:", g, w)
        return
    col, al = english_strip(rows())
    img = np.clip(col + 20 * (1 - al[..., None]), 0, 255).astype(np.uint8)
    Image.fromarray(img).save(a.out)
    print(a.out, img.shape)


if __name__ == "__main__":
    main()
