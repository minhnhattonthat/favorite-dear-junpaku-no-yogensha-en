"""fontinfo.py: look at FD2Font.FPK (GRPDATA) and find it in a RAM dump.

    python -X utf8 tools/fontinfo.py header            header words and the character list
    python -X utf8 tools/fontinfo.py find RAM.bin       where the FPK (or pieces of it) sit in a 2 MB RAM dump"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lkf  # noqa: E402

TREE = ROOT / "work" / "disc" / "tree"


def fpk():
    d = (TREE / "GRPDATA.LKF").read_bytes()
    e = [e for e in lkf.parse(d)["entries"] if e["name"].lower() == "fd2font.fpk"][0]
    return d[e["off"]:e["off"] + e["size"]]


GLYPH_W, GLYPH_H, GLYPH_BYTES = 10, 14, 35


def charlist(f):
    n, off = struct.unpack_from("<H", f, 0x0c)[0], struct.unpack_from("<H", f, 0x10)[0]
    return list(struct.unpack_from(f"<{n}H", f, off))


def glyph(f, i):
    """Glyph i as rows of 2bpp values, decoded like 0x8002C5EC: pixels MSB-first, 4 per byte; in each pair of
    pixels the first goes to the high nibble of the 4bpp buffer byte (= the right pixel on screen)."""
    base = struct.unpack_from("<H", f, 0x12)[0] + GLYPH_BYTES * i
    px = [(f[base + (k >> 2)] >> (6 - 2 * (k & 3))) & 3 for k in range(GLYPH_W * GLYPH_H)]
    rows = []
    for y in range(GLYPH_H):
        r = px[y * GLYPH_W:(y + 1) * GLYPH_W]
        rows.append([r[x ^ 1] for x in range(GLYPH_W)])
    return rows


def sheet(f, codes, path, zoom=4):
    from PIL import Image
    cl = charlist(f)
    pal = [(40, 40, 90), (90, 90, 90), (200, 200, 200), (255, 255, 255)]
    im = Image.new("RGB", (len(codes) * 12, 14))
    for n, c in enumerate(codes):
        for y, r in enumerate(glyph(f, cl.index(c))):
            for x, v in enumerate(r):
                im.putpixel((n * 12 + x, y), pal[v])
    im.resize((im.width * zoom, im.height * zoom), Image.NEAREST).save(path)


def main(argv):
    f = fpk()
    if argv[0] == "sheet":     # sheet OUT.png TEXT: render the characters of TEXT
        sheet(f, [int.from_bytes(ch.encode("cp932"), "big") for ch in argv[2]], argv[1])
        return
    if argv[0] == "header":
        print("size", hex(len(f)))
        print(" ".join(f"{w:04x}" for w in struct.unpack_from("<32H", f, 0)))
        print(f[0x200:0x2c0].hex(" "))
    elif argv[0] == "find":
        ram = Path(argv[1]).read_bytes()
        for off in range(0, len(f) - 16, 0x400):
            i = ram.find(f[off:off + 16])
            print(f"fpk+{off:05x} -> {'ram ' + hex(0x80000000 + i) if i >= 0 else '-'}")


if __name__ == "__main__":
    main(sys.argv[1:])
