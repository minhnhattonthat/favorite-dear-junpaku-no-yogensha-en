"""pix.py: GRPDATA Name_NNN.PIX battle unit name plates (docs/re/graphics.md).

    python -X utf8 tools/pix.py sheet work/lkf/GRPDATA OUT.png     # all plates tiled 8 per row, zoom 3

Format (verified by rendering all 88: enemy and hero names in katakana/kanji): 384 bytes, no header,
4bpp linear, 64x12 pixels (32 bytes per row, low nibble = left pixel), values 0-7 = antialiased grey level
(0 transparent). Drawn text is about 40-60 px wide; English names must fit 64 px."""
import glob
import os
import sys

from PIL import Image

W, H = 64, 12


def decode(data):
    px = []
    for b in data[: W * H // 2]:
        px += [min(255, (b & 15) * 36), min(255, (b >> 4) * 36)]
    im = Image.new("L", (W, H))
    im.putdata(px)
    return im


def sheet(src_dir, out, cols=8, zoom=3):
    files = sorted(glob.glob(os.path.join(src_dir, "*Name_*.PIX")))
    rows = (len(files) + cols - 1) // cols
    img = Image.new("L", ((W + 2) * cols, (H + 2) * rows), 60)
    for k, f in enumerate(files):
        img.paste(decode(open(f, "rb").read()), ((k % cols) * (W + 2), (k // cols) * (H + 2)))
    img.resize((img.width * zoom, img.height * zoom), Image.NEAREST).save(out)
    print(f"{out}: {len(files)} plates, row-major from {os.path.basename(files[0])}")


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] != "sheet":
        sys.exit(__doc__)
    sheet(sys.argv[2], sys.argv[3])
