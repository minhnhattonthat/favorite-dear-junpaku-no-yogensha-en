"""tim.py: decode PS1 TIM images (4/8/16 bpp, with or without CLUT) to PNG, and dump every image in GDATA.BIN.

    python -X utf8 tools/tim.py png FILE.TIM OUT.png [--clut N]
    python -X utf8 tools/tim.py dump OUTDIR [--disc work/disc/tree]   every TIM in every LKF archive
                                                                      -> OUTDIR/<arc>_<idx>_<n>.png + index.tsv

TIM: u32 0x10, u32 flags (bits 0-1 pmode 0=4bpp 1=8bpp 2=16bpp, bit 3 = has CLUT), [CLUT block], image block;
block = u32 length, u16 x, u16 y, u16 w (halfwords), u16 h, data. 16-bit colour: bit 15 STP, 5:5:5 BGR.
Colour 0x0000 is transparent on PS1 and drawn as magenta here so text on it stays readable.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
ROOT = Path(__file__).resolve().parents[1]


def rgb(c):
    if c == 0:
        return (255, 0, 255)
    return ((c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3)


def parse(data, off=0):
    """-> dict(bpp, w, h, pix (list of ints), cluts (list of lists)) or None if not a TIM."""
    if len(data) < off + 20:
        return None
    magic, flags = struct.unpack_from("<II", data, off)
    if magic != 0x10 or flags & ~0xF or (flags & 3) == 3:
        return None
    p = off + 8
    cluts = []
    if flags & 8:
        ln, x, y, w, h = struct.unpack_from("<IHHHH", data, p)
        if ln != 12 + w * h * 2 or not w or not h:
            return None
        cl = struct.unpack_from("<%dH" % (w * h), data, p + 12)
        cluts = [list(cl[i:i + w]) for i in range(0, w * h, w)]
        p += ln
    ln, x, y, w, h = struct.unpack_from("<IHHHH", data, p)
    if ln != 12 + w * h * 2 or not w or not h or p + ln > len(data):
        return None
    raw = data[p + 12:p + ln]
    mode = flags & 3
    if mode == 0:
        pix = [b >> s & 15 for b in raw for s in (0, 4)]
        width = w * 4
    elif mode == 1:
        pix = list(raw)
        width = w * 2
    else:
        pix = list(struct.unpack_from("<%dH" % (w * h), raw))
        width = w
    return {"bpp": (4, 8, 16)[mode], "w": width, "h": h, "pix": pix, "cluts": cluts, "end": p + ln, "vram": (x, y)}


def to_image(t, clut=0):
    from PIL import Image
    im = Image.new("RGB", (t["w"], t["h"]))
    if t["bpp"] == 16:
        im.putdata([rgb(c) for c in t["pix"]])
    else:
        pal = t["cluts"][clut % len(t["cluts"])] if t["cluts"] else [i * 0x421 for i in range(256)]
        im.putdata([rgb(pal[i] if i < len(pal) else 0) for i in t["pix"]])
    return im


def with_pixels(data, pix, off=0):
    """data (a 4 bpp TIM at off) with its image indices replaced by pix (row-major, same size) -> new bytes."""
    t = parse(data, off)
    assert t and t["bpp"] == 4 and len(pix) == t["w"] * t["h"], "want a 4 bpp TIM and a full-size index list"
    assert all(0 <= v < 16 for v in pix)
    start = t["end"] - t["w"] * t["h"] // 2
    raw = bytes(pix[i] | pix[i + 1] << 4 for i in range(0, len(pix), 2))
    return data[:start] + raw + data[t["end"]:]


def dump(outdir, disc):
    """Every TIM in every LKF archive (whole entries, plus TIMs packed back to back inside an entry)
    -> OUTDIR/<archive>_<index>_<n>.png + index.tsv. Entries that hold no TIM are listed as skipped."""
    import lkf
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    rows, skipped = [], []
    for arc in sorted(Path(disc).glob("*.LKF")):
        for e, blob in lkf.files(arc.read_bytes()):
            n, off = 0, 0
            while True:
                t = parse(blob, off)
                if t is None:
                    break
                name = f"{arc.stem}_{e['index']:04d}_{n}.png"
                to_image(t).save(out / name)
                rows.append(f"{name}\t{e['name']}\t{off:#x}\t{t['bpp']}\t{t['w']}x{t['h']}\t{len(t['cluts'])}")
                n, off = n + 1, t["end"]
            if n == 0:
                skipped.append(f"{arc.stem}\t{e['index']}\t{e['name']}\t{blob[:4].hex()}")
    (out / "index.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (out / "skipped.tsv").write_text("\n".join(skipped) + "\n", encoding="utf-8")
    print(len(rows), "images;", len(skipped), "entries without a TIM (skipped.tsv)")


if __name__ == "__main__":
    if sys.argv[1] == "png":
        d = Path(sys.argv[2]).read_bytes()
        c = int(sys.argv[sys.argv.index("--clut") + 1]) if "--clut" in sys.argv else 0
        to_image(parse(d), c).save(sys.argv[3])
    elif sys.argv[1] == "dump":
        dump(sys.argv[2], sys.argv[sys.argv.index("--disc") + 1] if "--disc" in sys.argv else ROOT / "work/disc/tree")
