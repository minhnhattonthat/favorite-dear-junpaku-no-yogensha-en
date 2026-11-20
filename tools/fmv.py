"""fmv.py: English captions burned into the STR movies (G14 opening DEMO.STR, G15 ENDING.STR).

Each caption row of `gfx/fmv.tsv` names a movie, a frame span, a sharp reference frame, a screen region and the
English lines. Per frame the Japanese caption layer (warm glow over the picture) is measured and fitted as
alpha x blur(reference layer, sigma), jointly for captions that overlap in time; the Japanese is erased (masked
pixels filled from their neighbours) and the English layer is drawn with the same alpha and blur, so it fades and
smears in and out like the original. Only macroblocks the edit touches are re-encoded (`tools/mdec.py`).

    python -X utf8 tools/fmv.py preview DEMO.STR 150 200 --out work/fmv/prev   # edited frames as PNG, no disc write
    python -X utf8 tools/fmv.py build                                         # build/fmv/<movie> (cached)

Build: `changes()` returns {disc file name: bytes} for build.py; results are cached in build/fmv/ keyed by a hash of
the inputs (this file, mdec.py, gfx/fmv.tsv, the fonts)."""
import argparse
import csv
import hashlib
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mdec  # noqa: E402
import roll  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TREE = ROOT / "work/disc/tree"
TABLE = ROOT / "gfx/fmv.tsv"
FONT = ROOT / "fonts/crimson/CrimsonText-SemiBoldItalic.ttf"
CACHE = ROOT / "build/fmv"
SIGMAS = [0, 1, 2, 3, 5, 8, 12]
TOP = (255, 250, 228)      # English fill, top of the letters
BOTTOM = (246, 206, 120)   # bottom (the JP captions run pale to gold)
GLOW = (170, 80, 10)       # orange glow behind the letters (dark pictures)
GLOW_SCENE = (45, 22, 8)   # dark outline (captions over a bright picture)
WHITE_TOP, WHITE_BOTTOM, GLOW_WHITE = (255, 255, 255), (226, 228, 236), (70, 72, 84)   # mode "white" (ENDING)


def rows():
    with open(TABLE, encoding="utf-8", newline="") as f:
        out = []
        for r in csv.DictReader(f, delimiter="\t"):
            if not r["movie"] or r["movie"].startswith("#"):
                continue
            r["first"], r["last"], r["ref"], r["size"] = int(r["first"]), int(r["last"]), int(r["ref"]), int(r["size"])
            r["region"] = tuple(int(v) for v in r["region"].split(","))
            r["lines"] = r["en"].split("|")
            r["dx"] = float(r.get("dx") or 0)   # px/frame sideways drift of the caption (mode white)
            out.append(r)
        return out


# ---------------------------------------------------------------- image helpers

def gauss(img, s):
    """Separable Gaussian blur of a 2D or 3D (H, W, C) float array."""
    if s <= 0:
        return img
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


def dilate(m, n=1):
    for _ in range(n):
        p = np.pad(m, 1)
        m = p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    return m


def inpaint(rgb, mask, iters=60):
    """Fill masked pixels from their unmasked neighbours (diffusion)."""
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
        n = k[:-2, 1:-1] + k[2:, 1:-1] + k[1:-1, :-2] + k[1:-1, 2:]
        new = (n > 0) & ~known
        out[new] = s[new] / n[new][:, None]
        known = known | new
    return out


def signal(rgb, mode="black"):
    """Japanese caption layer strength. black: the warm excess R - B (pale gold letters with orange glow over a dark
    picture; the feather and sparkles are blue-white). scene: the near-white letter cores, min(R, G, B) over 200
    (white letters with a dark outline over a bright picture; keep the region tight)."""
    if mode == "scene":
        return np.clip(rgb.min(2) - 200, 0, None)
    return np.clip(rgb[..., 0] - rgb[..., 2] - 6, 0, None)


def shift_x(img, dx):
    """img (H, W) moved right by dx px (linear interpolation, zeros enter)."""
    if not dx:
        return img
    W = img.shape[1]
    xs = np.arange(W) - dx
    x0 = np.floor(xs).astype(int)
    f = xs - x0
    ok0 = (x0 >= 0) & (x0 < W)
    ok1 = (x0 + 1 >= 0) & (x0 + 1 < W)
    a = np.where(ok0, img[:, np.clip(x0, 0, W - 1)], 0)
    b = np.where(ok1, img[:, np.clip(x0 + 1, 0, W - 1)], 0)
    return a * (1 - f) + b * f


def region_mask(shape, region):
    x, y, w, h = region
    m = np.zeros(shape, bool)
    m[y:y + h, x:x + w] = True
    return m


# ---------------------------------------------------------------- English layer

def bands(sig, region, thr=20):
    """Text line bands (y0, y1, x0, x1) of the reference layer inside region (rows with glow but no letter core
    count as gaps, so staggered lines whose glows touch still split)."""
    m = (sig > thr) & region_mask(sig.shape, region)
    rows_on = np.nonzero(m.sum(1) > max(4, 0.12 * m.sum(1).max()))[0]
    out = []
    if not len(rows_on):
        return out
    s = p = rows_on[0]
    for y in list(rows_on[1:]) + [10 ** 6]:
        if y > p + 3:
            cols = np.nonzero(m[s:p + 1].sum(0))[0]
            if p - s >= 6:
                out.append((s, p, cols.min(), cols.max()))
            s = y
        p = y
    return out


def english_layer(shape, lines, ref_bands, size, glow_rgb=GLOW, top=TOP, bottom=BOTTOM):
    """RGBA float layer (H, W, 4), alpha 0..1, with each English line placed on its Japanese line: left edge on the
    JP left edge (moved left if it would run off the frame), vertically centred on the JP band."""
    H, W = shape
    font = ImageFont.truetype(str(FONT), size)
    fill = Image.new("RGB", (W, H))
    alpha = Image.new("L", (W, H))
    da = ImageDraw.Draw(alpha)
    assert len(lines) == len(ref_bands), f"{len(lines)} English lines for {len(ref_bands)} JP lines {ref_bands}"
    boxes = []
    for text, (y0, y1, x0, x1) in zip(lines, ref_bands):
        l, t, r, b = da.textbbox((0, 0), text, font=font)
        tw, th = r - l, b - t
        x = min(x0, W - 6 - tw)
        y = (y0 + y1) // 2 - th // 2 - t
        da.text((x, y), text, font=font, fill=255)
        boxes.append((x + l, y + t, tw, th))
    grad = np.zeros((H, W, 3))
    for (x, y, tw, th) in boxes:
        f = np.clip((np.arange(H) - y) / max(th, 1), 0, 1)[:, None]
        grad[y:y + th + 2] = (np.array(top) * (1 - f) + np.array(bottom) * f)[y:y + th + 2][:, None, :]
    a = np.asarray(alpha, float) / 255
    dark = glow_rgb == GLOW_SCENE   # a bright picture needs a firmer outline
    ga = np.clip(gauss(a, 1.3 if dark else 1.6) * (3.5 if dark else 2.2), 0, 1) * (1.0 if dark else 0.85) * (1 - a)
    out_a = a + ga
    premult = grad * a[..., None] + np.array(glow_rgb) * ga[..., None]
    full = np.dstack([premult / np.maximum(out_a, 1e-6)[..., None], out_a])
    if not dark:
        return full, full
    return full, np.dstack([grad, a])   # (with outline, letters only: a dark outline smeared by blur is a dark box)


# ---------------------------------------------------------------- per frame

class Movie:
    def __init__(self, name):
        self.name = name
        self.data = (TREE / name).read_bytes()
        self.fr = mdec.frames(self.data)
        self.caps = [r for r in rows() if r["movie"] == name]
        self.roll = roll.Roll(self) if name == roll.MOVIE else None   # G15 staff roll (tools/roll.py)
        self._rgb = {}
        self._shift = {}
        self.refs = {}
        self.letters = {}

    def rgb(self, n):
        if n not in self._rgb:
            f = self.fr[n]
            Y, Cb, Cr = mdec.decode(mdec.frame_data(self.data, f), f["w"], f["h"])
            self._rgb[n] = mdec.to_rgb(Y, Cb, Cr, f["w"], f["h"]).astype(float)
        return self._rgb[n]

    def shift(self, n, m, region):
        """Integer (dy, dx) with frame n(p) ~ frame m(p - d) near `region` (phase correlation on the region grown
        by 32 px: the scene captions sit on a pan, and its layers move at different speeds)."""
        key = n, m, region
        if key not in self._shift:
            x, y, w, h = region
            H, W = self.rgb(n).shape[:2]
            y0, y1, x0, x1 = max(0, y - 32), min(H, y + h + 32), max(0, x - 32), min(W, x + w + 32)
            a, b = self.rgb(n)[y0:y1, x0:x1].mean(2), self.rgb(m)[y0:y1, x0:x1].mean(2)
            R = np.fft.fft2(a - a.mean()) * np.conj(np.fft.fft2(b - b.mean()))
            r = np.fft.ifft2(R / (abs(R) + 1e-9)).real
            y, x = np.unravel_index(r.argmax(), r.shape)
            self._shift[key] = (y - r.shape[0] if y > r.shape[0] // 2 else y, x - r.shape[1] if x > r.shape[1] // 2 else x)
        return self._shift[key]

    def clean(self, n, cap):
        """Frame n's caption region rebuilt from the caption-free frames cap["clean"] = "t0,t1" (before / after the
        span), moved by the pan; nearest frame first, the other where the first runs off the picture."""
        rgb = self.rgb(n)
        H, W = rgb.shape[:2]
        x, y, w, h = cap["region"]
        out = rgb.copy()
        todo = region_mask((H, W), cap["region"])
        srcs = sorted((int(t) for t in cap["clean"].split(",")), key=lambda t: abs(t - n))
        ring = dilate(region_mask((H, W), cap["region"]), 6) & ~region_mask((H, W), cap["region"])
        for t in srcs:
            dy, dx = self.shift(n, t, cap["region"])
            src = np.zeros_like(rgb)
            ys, xs = np.nonzero(np.ones((H, W), bool))
            sy, sx = ys - dy, xs - dx
            ok = (sy >= 0) & (sy < H) & (sx >= 0) & (sx < W)
            src[ys[ok], xs[ok]] = self.rgb(t)[sy[ok], sx[ok]]
            valid = np.zeros((H, W), bool)
            valid[ys[ok], xs[ok]] = True
            r = ring & valid   # the picture fades: match the source's level to the frame around the box
            gain = rgb[r].mean(0) / np.maximum(src[r].mean(0), 1) if r.any() else 1
            use = todo & valid
            out[use] = np.clip(src[use] * gain, 0, 255)
            todo &= ~use
        assert not todo.any(), f"{self.name} frame {n}: no clean source for {int(todo.sum())} pixels"
        return out

    def scene_signal(self, n, cap):
        return np.clip(self.rgb(n).mean(2) - self.clean(n, cap).mean(2) - 8, 0, None) * \
            region_mask(self.rgb(n).shape[:2], cap["region"])

    def ref(self, cap):
        key = cap["ref"], cap["region"]
        if key not in self.refs:
            mode = cap.get("mode") or "black"
            if mode == "scene":
                sig = self.scene_signal(cap["ref"], cap)
            elif mode == "white":   # letters = bright pixels (grown), signal = their excess over the inpainted picture
                rgb = self.rgb(cap["ref"])
                letters = dilate((rgb.mean(2) > 110) & region_mask(rgb.shape[:2], cap["region"]), 3)
                self.letters[key] = letters
                sig = np.clip(rgb.mean(2) - inpaint(rgb, letters).mean(2) - 4, 0, None) * letters
            else:
                sig = signal(self.rgb(cap["ref"]), mode) * region_mask(self.rgb(cap["ref"]).shape[:2], cap["region"])
            if cap.get("at"):   # explicit "x,cy;x,cy": left edge and centre line of each JP line
                b = [(cy - 8, cy + 8, x, x) for x, cy in (map(int, p.split(",")) for p in cap["at"].split(";"))]
            else:
                b = bands(sig, cap["region"])
            if mode == "white":
                eng = english_layer(sig.shape, cap["lines"], b, cap["size"], GLOW_WHITE, WHITE_TOP, WHITE_BOTTOM)
            else:
                eng = english_layer(sig.shape, cap["lines"], b, cap["size"], GLOW_SCENE if mode == "scene" else GLOW)
            self.refs[key] = (sig, eng)
        return self.refs[key]

    def edit(self, n):
        """(edited RGB, changed-pixel mask) of frame n, or None if no caption is active."""
        if self.roll and n >= roll.N0 - 40:
            return self.roll.edit(n)
        active = [c for c in self.caps if c["first"] <= n <= c["last"]]
        if not active:
            return None
        rgb = self.rgb(n)
        shape = rgb.shape[:2]
        reg = np.zeros(shape, bool)
        sig = np.zeros(shape)
        mask = np.zeros(shape, bool)
        lum = rgb.mean(2)
        cleaned = {}
        for c in active:
            r = region_mask(shape, c["region"])
            reg |= r
            if c.get("mode") == "scene":   # the whole box comes from the clean plate
                sig += self.scene_signal(n, c)
                cleaned[id(c)] = (self.clean(n, c), r)
                continue
            if c.get("mode") == "white":   # handled below, after the shifted letters are erased
                continue
            s = signal(rgb, c.get("mode") or "black") * r
            sig += s
            if c.get("mode") == "box":   # smooth picture that morphs (clouds): fill the whole tight box
                # keep a bright object passing through (the feather): bright here but not where the static
                # letters are bright in the reference frame
                ref = self.rgb(c["ref"]).mean(2)
                text = dilate((ref > np.median(ref[r]) + 35) & r, 3)
                feather = dilate((lum > 235) & ~text, 1)
                mask |= r & ~feather
                continue
            warm = (s > 4) & r
            # the letter cores are near white (R ~ B): take bright pixels next to the warm glow too, else the
            # fill floods white from them
            far = ~dilate(warm, 6) & r
            bg = lum[far].mean() if far.any() else 0
            core = dilate(warm, 4) & ((lum > 50 + bg) | (lum < bg - 25))   # + dark drop shadow on a lit picture
            mask |= dilate(warm | core, 2) & r
        whites = {}
        base = mask.copy()
        for c in active:
            if c.get("mode") == "white":   # white letters drifting sideways (ENDING.STR opening caption)
                self.ref(c)
                sh = c["dx"] * (n - c["ref"])
                lm = (shift_x(self.letters[(c["ref"], c["region"])].astype(float), sh) > 0.25) & \
                    region_mask(shape, c["region"])
                core = lm
                lm = dilate(lm, 5)   # room for the blur-out at the end of the caption
                whites[id(c)] = (sh, lm, core)
                mask |= lm
        out = inpaint(rgb, mask)
        for sh, lm, core in whites.values():
            sig += np.clip(lum - out.mean(2) - 4, 0, None) * lm
        refs = [shift_x(self.ref(c)[0], whites[id(c)][0]) if id(c) in whites else self.ref(c)[0] for c in active]
        fit = self.fit(sig, refs)
        if whites:
            # a blurred caption spreads past its letters: erase the halo too; a caption that has (nearly) faded
            # out is left alone, so the feather crossing it is not erased with it
            mask = base.copy()
            for c, (a, s) in zip(active, fit):
                if id(c) in whites and a >= 0.12:
                    mask |= dilate(whites[id(c)][1], int(s)) if s >= 3 else whites[id(c)][1]
            out = inpaint(rgb, mask)
        if whites:   # keep what the Japanese layer cannot explain around the letters (the feather flying by)
            expect = sum(a * gauss(r, s) for (a, s), r in zip(fit, refs))
            cores = dilate(np.any([whites[id(c)][2] & (s < 5) for c, (a, s) in zip(active, fit) if id(c) in whites]
                                  + [np.zeros(shape, bool)], 0), 1)   # (sharp letters only: a smeared one hides less)
            extra = dilate((lum - out.mean(2) - expect) > 60, 2) & mask & ~cores
            out[extra] = rgb[extra]
        for clean, r in cleaned.values():
            w = gauss(r.astype(float) * dilate(~r, 3).__invert__(), 1.5)[..., None]   # feathered box edge
            out = out * (1 - w) + clean * w
            mask |= w[..., 0] > 0.01
        for c, (a, s) in zip(active, fit):
            full, letters = self.ref(c)[1]
            if a <= 0.02:
                continue
            if id(c) in whites:
                full, letters = (np.dstack([shift_x(e[..., i], whites[id(c)][0]) for i in range(4)])
                                 for e in (full, letters))
            k = max(0.0, 1 - s / 5)
            eng = full * k + letters * (1 - k)
            col = gauss(eng[..., :3] * eng[..., 3:], s)
            al = np.clip(gauss(eng[..., 3], s) * a, 0, 1)
            col = col / np.maximum(gauss(eng[..., 3], s), 1e-6)[..., None]
            out = out * (1 - al[..., None]) + col * al[..., None]
            mask |= al > 0.01
        return np.clip(np.round(out), 0, 255), mask

    @staticmethod
    def fit(sig, refs):
        """Best (alpha, sigma) per reference so that sum alpha_k * blur(ref_k, sigma_k) ~ sig."""
        blurred = [{s: gauss(r, s) for s in SIGMAS} for r in refs]
        best = None
        import itertools
        for combo in itertools.product(SIGMAS, repeat=len(refs)):
            A = np.stack([blurred[k][s].ravel() for k, s in enumerate(combo)], 1)
            coef, *_ = np.linalg.lstsq(A, sig.ravel(), rcond=None)
            coef = np.clip(coef, 0, 1.2)
            err = ((A @ coef - sig.ravel()) ** 2).sum()
            if best is None or err < best[0]:
                best = (err, coef, combo)
        return [(min(float(a), 1.0), s) for a, s in zip(best[1], best[2])]

    def frames_to_edit(self):
        out = {n for c in self.caps for n in range(c["first"], c["last"] + 1) if n in self.fr}
        if self.roll:
            out |= set(self.roll.frames())
        return sorted(out)

    def build(self):
        buf = bytearray(self.data)
        for n in self.frames_to_edit():
            for k in [k for k in self._rgb if k < n - 120]:   # the roll reads frames up to 96 away
                del self._rgb[k]
            res = self.edit(n)
            if res is None:
                continue
            out, mask = res
            f = self.fr[n]
            W, H = ((f["w"] + 15) // 16) * 16, ((f["h"] + 15) // 16) * 16
            pad = np.zeros((H, W, 3))
            pad[:f["h"], :f["w"]] = out
            Y, Cb, Cr = mdec.from_rgb(pad)
            ys, xs = np.nonzero(mask)
            mbs = {(x // 16, y // 16) for x, y in zip(xs, ys)}
            raw = mdec.frame_data(self.data, f)
            new, floor = mdec.rebuild(raw, f["w"], f["h"], Y, Cb, Cr, mbs, len(f["sectors"]) * mdec.CHUNK_DATA)
            mdec.put_frame(buf, f, new)
            if floor:
                print(f"{self.name} frame {n}: AC levels <= {floor} dropped to fit")
        return bytes(buf)


def inputs_hash(name):
    h = hashlib.sha1()
    for p in (Path(__file__), ROOT / "tools/mdec.py", TABLE, FONT, ROOT / "tools/roll.py", roll.TABLE,
              *sorted(roll.FONTS.glob("*.ttf"))):
        h.update(p.read_bytes())
    h.update(name.encode())
    return h.hexdigest()[:16]


def changes():
    """{disc file name: bytes} of every movie with captions in gfx/fmv.tsv (cached in build/fmv/)."""
    out = {}
    for name in sorted({r["movie"] for r in rows()} | {roll.MOVIE}):
        key = inputs_hash(name)
        path = CACHE / f"{name}.{key}"
        if not path.exists():
            CACHE.mkdir(parents=True, exist_ok=True)
            for old in CACHE.glob(f"{name}.*"):
                old.unlink()
            print(f"fmv: re-encoding {name} captions ...")
            path.write_bytes(Movie(name).build())
        out[name] = path.read_bytes()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["preview", "build"])
    ap.add_argument("movie", nargs="?")
    ap.add_argument("first", nargs="?", type=int)
    ap.add_argument("last", nargs="?", type=int)
    ap.add_argument("--every", type=int, default=1)
    ap.add_argument("--out", default="work/fmv/prev")
    a = ap.parse_args()
    if a.cmd == "build":
        for name, data in changes().items():
            print(f"{name}: {len(data)} bytes")
        return
    m = Movie(a.movie)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for n in range(a.first, a.last + 1, a.every):
        res = m.edit(n)
        img = m.rgb(n) if res is None else res[0]
        Image.fromarray(img.astype(np.uint8)).save(out / f"f{n:04d}.png")
    print(f"{out}: frames {a.first}..{a.last}")


if __name__ == "__main__":
    main()
