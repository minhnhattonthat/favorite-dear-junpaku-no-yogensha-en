"""buttons.py: find the blue button / bar interiors in a screenshot and print them as inkbox.py rects.

    python -X utf8 tools/buttons.py SHOT.png [--min-w 30] [--min-h 8]

A pixel is "blue" when B > R + 40 and B > G + 30 (the heaven buttons, menu bars, choice highlight). Prints one
x,y,w,h per connected box (bounding box of a 4-connected blue region at least min-w x min-h). Feed them to
$SKILL/scripts/inkbox.py with --ink R,G,B (the label colour), since the button fill is a gradient.
"""
import argparse

import numpy as np
from PIL import Image


def boxes(path, min_w=30, min_h=8):
    a = np.asarray(Image.open(path).convert("RGB")).astype(int)
    blue = (a[..., 2] > a[..., 0] + 40) & (a[..., 2] > a[..., 1] + 30)
    # close the letters' holes row-wise: a row segment counts if it is mostly blue
    H, W = blue.shape
    seen = np.zeros_like(blue)
    out = []
    for y in range(H):
        for x in range(W):
            if not blue[y, x] or seen[y, x]:
                continue
            stack, xs, ys = [(y, x)], [], []
            seen[y, x] = True
            while stack:
                cy, cx = stack.pop()
                xs.append(cx)
                ys.append(cy)
                for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                    if 0 <= ny < H and 0 <= nx < W and blue[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            if x1 - x0 + 1 >= min_w and y1 - y0 + 1 >= min_h:
                out.append((x0, y0, x1 - x0 + 1, y1 - y0 + 1))
    return sorted(out, key=lambda b: (b[1], b[0]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("png")
    ap.add_argument("--min-w", type=int, default=30)
    ap.add_argument("--min-h", type=int, default=8)
    a = ap.parse_args()
    print(" ".join(",".join(map(str, b)) for b in boxes(a.png, a.min_w, a.min_h)))


if __name__ == "__main__":
    main()
