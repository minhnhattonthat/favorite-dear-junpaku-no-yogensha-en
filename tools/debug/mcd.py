"""mcd.py: PS1 memory card images (128 KB raw .mcd, the format PCSX-Redux reads with -memcard1).

    python -X utf8 tools/debug/mcd.py blank OUT.mcd        a formatted, empty card
    python -X utf8 tools/debug/mcd.py ls CARD.mcd          directory: slot, state, product code/name, size, title
    python -X utf8 tools/debug/mcd.py check CARD.mcd       exit 1 if any directory frame XOR is wrong

Layout: block 0 = header frame ("MC"), 15 directory frames (128 bytes: u32 state 0x51 first block / 0x52 middle /
0x53 last / 0xA0 free, u32 size, u16 next block, 20-byte filename "BISLPS-01759..."), broken-frame list,
then 15 save blocks of 8 KB each (block 1+: "SC" title frame, icon frames, data). Every directory frame ends
with the XOR of its first 127 bytes."""
import struct
import sys

FRAME, BLOCK, SIZE = 128, 8192, 131072


def xor(b):
    x = 0
    for c in b:
        x ^= c
    return x


def blank():
    d = bytearray(SIZE)
    d[0:2] = b"MC"
    d[127] = xor(d[:127])
    for i in range(1, 16):
        o = i * FRAME
        d[o] = 0xA0
        d[o + 8:o + 10] = b"\xff\xff"
        d[o + 127] = xor(d[o:o + 127])
    for i in range(16, 36):
        o = i * FRAME
        d[o:o + 4] = b"\xff\xff\xff\xff"
        d[o + 8:o + 10] = b"\xff\xff"
        d[o + 127] = xor(d[o:o + 127])
    d[63 * FRAME:64 * FRAME] = d[0:FRAME]
    return bytes(d)


def entries(d):
    out = []
    for i in range(1, 16):
        o = i * FRAME
        state, size, nxt = struct.unpack_from("<IIH", d, o)
        name = d[o + 10:o + 30].split(b"\0")[0].decode("ascii", "replace")
        ok = d[o + 127] == xor(d[o:o + 127])
        out.append((i, state, size, nxt, name, ok))
    return out


def title(d, slot):
    b = d[slot * BLOCK + 4:slot * BLOCK + 68]
    try:
        return b.split(b"\0")[0].decode("shift_jis", "replace")
    except Exception:
        return "?"


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("blank", "ls", "check"):
        print(__doc__)
        return 2
    cmd, path = sys.argv[1], sys.argv[2]
    if cmd == "blank":
        open(path, "wb").write(blank())
        return 0
    d = open(path, "rb").read()
    assert len(d) == SIZE, f"{path}: {len(d)} bytes, want {SIZE}"
    bad = 0
    for i, state, size, nxt, name, ok in entries(d):
        bad += not ok
        if cmd == "ls" and state != 0xA0:
            print(f"{i:2} {state:#04x} {name:<20} {size:6} next={nxt:#06x} {title(d, i) if state == 0x51 else ''}"
                  f"{'' if ok else '  BAD XOR'}")
    if cmd == "check" and bad:
        print(f"{bad} directory frame(s) with a bad XOR")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
