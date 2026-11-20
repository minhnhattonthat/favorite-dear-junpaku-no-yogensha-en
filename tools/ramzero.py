"""ramzero.py: zero runs that stay zero in every given RAM dump (candidate free RAM; still prove with a write watch).

    python -X utf8 tools/ramzero.py [--min 0x400] [--lo 0x80010000] [--hi 0x80200000] RAM.bin..."""
import argparse
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dumps", nargs="+")
    ap.add_argument("--min", type=lambda s: int(s, 0), default=0x400)
    ap.add_argument("--lo", type=lambda s: int(s, 0), default=0x80010000)
    ap.add_argument("--hi", type=lambda s: int(s, 0), default=0x80200000)
    a = ap.parse_args()
    rams = [Path(p).read_bytes() for p in a.dumps]
    lo, hi = a.lo - 0x80000000, a.hi - 0x80000000
    nz = bytearray(hi - lo)
    for r in rams:
        seg = r[lo:hi]
        for i in range(0, len(seg), 4):
            if seg[i:i + 4] != b"\0\0\0\0":
                nz[i] = 1
    start = None
    for i in range(0, len(nz) + 4, 4):
        z = i < len(nz) and not nz[i]
        if z and start is None:
            start = i
        elif not z and start is not None:
            if i - start >= a.min:
                print(f"{0x80000000 + lo + start:08x}-{0x80000000 + lo + i:08x}  {i - start:#x}")
            start = None


if __name__ == "__main__":
    main()
