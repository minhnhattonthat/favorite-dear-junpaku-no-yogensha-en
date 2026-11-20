"""sprites.py: list the textured sprite packets (GP0 0x64-0x67 SPRT, 0x74-0x77 SPRT_8, 0x7C-0x7F SPRT_16) and
textured quads (0x2C-0x2F) found in a main-RAM dump (tools/debug/ramdump.lua), to learn which atlas rect a screen draws.

    python -X utf8 tools/sprites.py RAM.bin [--clut CY,CX] [--screen X0,Y0,X1,Y1]

A packet is taken where its words decode to a sane screen position (-64..447 / -64..303) and size (1..256); the
ordering-table tag word before it (len << 24 | next) must give len = the packet's word count. Prints
addr, cmd, screen x,y, u,v, w,h, clut (cx,cy) one per line."""
import argparse
import struct


def s11(v):
    v &= 0x7FF
    return v - 0x800 if v & 0x400 else v


def scan(ram):
    n = len(ram) // 4
    w = struct.unpack("<%dI" % n, ram[:n * 4])
    out = []
    for i in range(1, n - 4):
        cmd = w[i] >> 24
        tag_len = w[i - 1] >> 24
        if 0x64 <= cmd <= 0x67 and tag_len == 4:
            x, y = s11(w[i + 1]), s11(w[i + 1] >> 16)
            u, v, clut = w[i + 2] & 0xFF, w[i + 2] >> 8 & 0xFF, w[i + 2] >> 16
            ww, hh = w[i + 3] & 0xFFFF, w[i + 3] >> 16
        elif cmd in (0x74, 0x75, 0x76, 0x77, 0x7C, 0x7D, 0x7E, 0x7F) and tag_len == 3:
            x, y = s11(w[i + 1]), s11(w[i + 1] >> 16)
            u, v, clut = w[i + 2] & 0xFF, w[i + 2] >> 8 & 0xFF, w[i + 2] >> 16
            ww = hh = 8 if cmd < 0x7C else 16
        elif 0x2C <= cmd <= 0x2F and tag_len == 9:
            xs = [s11(w[i + k]) for k in (1, 3, 5, 7)]
            ys = [s11(w[i + k] >> 16) for k in (1, 3, 5, 7)]
            us = [w[i + k] & 0xFF for k in (2, 4, 6, 8)]
            vs = [w[i + k] >> 8 & 0xFF for k in (2, 4, 6, 8)]
            x, y, u, v, clut = min(xs), min(ys), min(us), min(vs), w[i + 2] >> 16
            ww, hh = max(us) - u, max(vs) - v
        else:
            continue
        if not (-64 <= x < 448 and -64 <= y < 304 and 0 < ww <= 256 and 0 < hh <= 256):
            continue
        out.append({"addr": 0x80000000 + i * 4, "cmd": cmd, "x": x, "y": y, "u": u, "v": v, "w": ww, "h": hh,
                    "cx": (clut & 0x3F) * 16, "cy": clut >> 6 & 0x1FF})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ram")
    ap.add_argument("--clut", help="CX,CY of the CLUT in VRAM to keep")
    ap.add_argument("--screen", help="X0,Y0,X1,Y1: keep sprites whose top-left is inside")
    a = ap.parse_args()
    ram = open(a.ram, "rb").read()
    for s in scan(ram):
        if a.clut and (s["cx"], s["cy"]) != tuple(map(int, a.clut.split(","))):
            continue
        if a.screen:
            x0, y0, x1, y1 = map(int, a.screen.split(","))
            if not (x0 <= s["x"] < x1 and y0 <= s["y"] < y1):
                continue
        print("%08X %02X xy %4d,%4d uv %3d,%3d wh %3d,%3d clut %d,%d" % (
            s["addr"], s["cmd"], s["x"], s["y"], s["u"], s["v"], s["w"], s["h"], s["cx"], s["cy"]))


if __name__ == "__main__":
    main()
