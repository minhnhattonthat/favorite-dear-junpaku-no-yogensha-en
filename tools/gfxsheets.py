"""gfxsheets.py: labelled contact sheets of the static graphics dump, for the graphics-text survey.

    python -X utf8 tools/tim.py dump work/gfx                 # first: every TIM -> PNG + index.tsv
    python -X utf8 tools/gfxsheets.py work/gfx work/gfx/sheets [--per 30] [--width 1400]

Packs the PNGs listed in index.tsv (in order) into sheets of at most `--per` images, each tile labelled with its
file name, scaled down only when wider than a third of the sheet. Writes sheets/NNN.png and sheets/index.tsv
(sheet -> image names) so a reviewer can name every Japanese cell by image."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--per", type=int, default=30)
    ap.add_argument("--width", type=int, default=1400)
    a = ap.parse_args()
    src, out = Path(a.src), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    names = [l.split("\t")[0] for l in (src / "index.tsv").read_text(encoding="utf-8").splitlines() if l]
    maxw = a.width // 3
    rows_index = []
    for s in range(0, len(names), a.per):
        chunk = names[s:s + a.per]
        tiles = []
        for n in chunk:
            im = Image.open(src / n).convert("RGB")
            if im.width > maxw:
                im = im.resize((maxw, max(1, im.height * maxw // im.width)))
            tiles.append((n, im))
        # shelf packing
        x = y = shelf = 0
        pos = []
        for n, im in tiles:
            if x + im.width > a.width:
                x, y, shelf = 0, y + shelf + 14, 0
            pos.append((x, y))
            x += im.width + 6
            shelf = max(shelf, im.height)
        sheet = Image.new("RGB", (a.width, y + shelf + 14), (40, 40, 40))
        d = ImageDraw.Draw(sheet)
        for (n, im), (px, py) in zip(tiles, pos):
            sheet.paste(im, (px, py + 12))
            d.text((px, py), n.replace(".png", ""), fill=(255, 255, 0))
        k = s // a.per
        sheet.save(out / f"{k:03d}.png")
        rows_index.append(f"{k:03d}\t" + " ".join(chunk))
    (out / "index.tsv").write_text("\n".join(rows_index) + "\n", encoding="utf-8")
    print(len(rows_index), "sheets ->", out)


if __name__ == "__main__":
    main()
