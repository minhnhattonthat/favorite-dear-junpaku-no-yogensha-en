"""mdec.py: PS1 STR (v2 MDEC) frames: read, decode, re-encode single macroblocks, write back.

The v2 bitstream stores each 8x8 block on its own (absolute 10-bit DC, no prediction), so a frame can be edited by
re-encoding only the macroblocks a caption touches and copying every other block's original bits. The frame keeps
its sector count; the new bitstream must fit the frame's chunks (2016 bytes each), else `fit_blocks` thins the
re-encoded blocks' smallest AC levels until it does.

    python -X utf8 tools/mdec.py info work/disc/tree/DEMO.STR            # frames, sizes, qscale
    python -X utf8 tools/mdec.py png work/disc/tree/DEMO.STR 120 out.png  # decode one frame (own decoder)
    python -X utf8 tools/mdec.py selftest work/disc/tree/DEMO.STR 120     # decode -> re-encode every block -> same image

Formats (checked against the disc in `tests/test_mdec.py`):
- sector (as dumpsxiso extracts STR: 2336 bytes) = 8-byte subheader + 2048 user bytes + 280 EDC/ECC (mkpsxiso
  recomputes those). Video sector user data = 0x20-byte chunk header + 2016 bytes of frame data.
- chunk header: u16 0x0160, u16 0x8001, u16 chunk no, u16 chunk count, u32 frame no, u32 frame data size,
  u16 width, u16 height, then a copy of the frame header's 8 bytes, u32 0.
- frame header: u16 MDEC code count / 2 rounded up to 32, u16 0x3800, u16 qscale, u16 version (2).
- bitstream: u16 little-endian words read MSB first. Macroblocks column by column (x outer, y inner); blocks Cr, Cb,
  Y0..Y3; block = 10-bit signed DC, AC VLC codes (MPEG-1 table B.14, "10" = end of block, escape 000001 + 6-bit run
  + 10-bit signed level), then the end code 0111111111 and zero bits to a 32-bit boundary."""
import struct
import sys

import numpy as np

SECTOR = 2336
SUB = 8
USER = 2048
CHUNK_HDR = 0x20
CHUNK_DATA = USER - CHUNK_HDR
MAGIC = b"\x60\x01\x01\x80"

# (code bits without sign) -> (run, level)
_VLC = """11 0 1|011 1 1|0100 0 2|0101 2 1|00101 0 3|00111 3 1|00110 4 1|000110 1 2|000111 5 1|000101 6 1|
000100 7 1|0000110 0 4|0000100 2 2|0000111 8 1|0000101 9 1|00100110 0 5|00100001 0 6|00100101 1 3|00100100 3 2|
00100111 10 1|00100011 11 1|00100010 12 1|00100000 13 1|0000001010 0 7|0000001100 1 4|0000001011 2 3|
0000001111 4 2|0000001001 5 2|0000001110 14 1|0000001101 15 1|0000001000 16 1|000000011101 0 8|000000011000 0 9|
000000010011 0 10|000000010000 0 11|000000011011 1 5|000000010100 2 4|000000011100 3 3|000000010010 4 3|
000000011110 6 2|000000010101 7 2|000000010001 8 2|000000011111 17 1|000000011010 18 1|000000011001 19 1|
000000010111 20 1|000000010110 21 1|0000000011010 0 12|0000000011001 0 13|0000000011000 0 14|0000000010111 0 15|
0000000010110 1 6|0000000010101 1 7|0000000010100 2 5|0000000010011 3 4|0000000010010 5 3|0000000010001 9 2|
0000000010000 10 2|0000000011111 22 1|0000000011110 23 1|0000000011101 24 1|0000000011100 25 1|
0000000011011 26 1|00000000011111 0 16|00000000011110 0 17|00000000011101 0 18|00000000011100 0 19|
00000000011011 0 20|00000000011010 0 21|00000000011001 0 22|00000000011000 0 23|00000000010111 0 24|
00000000010110 0 25|00000000010101 0 26|00000000010100 0 27|00000000010011 0 28|00000000010010 0 29|
00000000010001 0 30|00000000010000 0 31|000000000011000 0 32|000000000010111 0 33|000000000010110 0 34|
000000000010101 0 35|000000000010100 0 36|000000000010011 0 37|000000000010010 0 38|000000000010001 0 39|
000000000010000 0 40|000000000011111 1 8|000000000011110 1 9|000000000011101 1 10|000000000011100 1 11|
000000000011011 1 12|000000000011010 1 13|000000000011001 1 14|0000000000010011 1 15|0000000000010010 1 16|
0000000000010001 1 17|0000000000010000 1 18|0000000000010100 6 3|0000000000011010 11 2|0000000000011001 12 2|
0000000000011000 13 2|0000000000010111 14 2|0000000000010110 15 2|0000000000010101 16 2|0000000000011111 27 1|
0000000000011110 28 1|0000000000011101 29 1|0000000000011100 30 1|0000000000011011 31 1"""
DEC = {}
ENC = {}
for _item in _VLC.replace("\n", "").split("|"):
    _c, _r, _l = _item.split()
    DEC[_c] = (int(_r), int(_l))
    ENC[(int(_r), int(_l))] = _c
EOB = "10"
ESC = "000001"
END = "0111111111"   # after the last block: a 10-bit "DC" of 0x1FF ends the frame (the player stops without it)

ZIGZAG = [0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5, 12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7,
          14, 21, 28, 35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51, 58, 59, 52, 45, 38, 31, 39, 46,
          53, 60, 61, 54, 47, 55, 62, 63]
QMAT = [8, 16, 19, 22, 26, 27, 29, 34, 16, 16, 22, 24, 27, 29, 34, 37, 19, 22, 26, 27, 29, 34, 34, 38, 22, 22, 26,
        27, 29, 34, 37, 40, 22, 26, 27, 29, 32, 35, 40, 48, 26, 27, 29, 32, 35, 40, 48, 58, 26, 27, 29, 34, 38, 46,
        56, 69, 27, 29, 35, 38, 46, 56, 69, 83]   # MPEG-1 default intra matrix, raster order

_n = np.arange(8)
DCT = np.sqrt(2 / 8) * np.cos((2 * _n[None, :] + 1) * _n[:, None] * np.pi / 16)
DCT[0] /= np.sqrt(2)   # orthonormal DCT-II: F = DCT @ x @ DCT.T, F[0,0] = 8 * mean


# ---------------------------------------------------------------- sectors and frames

def frames(data):
    """{frame no: {"sectors": [sector index..], "w", "h", "size", "hdr": first chunk header}} of a 2336-byte STR."""
    out = {}
    for i in range(len(data) // SECTOR):
        u = data[i * SECTOR + SUB:i * SECTOR + SUB + USER]
        if u[:4] != MAGIC:
            continue
        no, cnt, fno, size, w, h = struct.unpack_from("<HHIIHH", u, 4)
        f = out.setdefault(fno, {"sectors": [None] * cnt, "w": w, "h": h, "size": size, "hdr": u[:CHUNK_HDR]})
        f["sectors"][no] = i
    return out


def frame_data(data, f):
    buf = b"".join(data[i * SECTOR + SUB + CHUNK_HDR:i * SECTOR + SUB + USER] for i in f["sectors"])
    return buf


def put_frame(buf, f, bitstream):
    """Write a new frame bitstream (with its 8-byte header) into the frame's sectors of bytearray `buf`."""
    cap = len(f["sectors"]) * CHUNK_DATA
    assert len(bitstream) <= cap, f"frame too big: {len(bitstream)} > {cap}"
    body = bitstream + b"\0" * (cap - len(bitstream))
    size = (len(bitstream) + 3) & ~3
    for k, i in enumerate(f["sectors"]):
        o = i * SECTOR + SUB
        struct.pack_into("<I", buf, o + 0x0C, size)
        buf[o + 0x14:o + 0x1C] = bitstream[:8]
        buf[o + CHUNK_HDR:o + USER] = body[k * CHUNK_DATA:(k + 1) * CHUNK_DATA]


# ---------------------------------------------------------------- bitstream

def _bits(raw):
    w = np.frombuffer(raw[:len(raw) & ~1], dtype="<u2").astype(">u2")
    return "".join(map(str, np.unpackbits(np.frombuffer(w.tobytes(), dtype=np.uint8))))


def _sbits(s):
    v = int(s, 2)
    return v - (1 << len(s)) if s[0] == "1" else v


def parse(raw, w, h):
    """Frame bytes -> (header dict, [block]) with block = {"bits": str, "levels": [(zigzag index, level)], "dc"}.
    Blocks in stream order (6 per macroblock)."""
    count, magic, q, ver = struct.unpack_from("<HHHH", raw)
    assert magic == 0x3800 and ver == 2, (hex(magic), ver)
    bits = _bits(raw[8:])
    pos = 0
    blocks = []
    nmb = ((w + 15) // 16) * ((h + 15) // 16)
    for _ in range(nmb * 6):
        start = pos
        dc = _sbits(bits[pos:pos + 10])
        pos += 10
        levels = []
        i = 0
        while True:
            if bits.startswith(EOB, pos):
                pos += 2
                break
            if bits.startswith(ESC, pos):
                run = int(bits[pos + 6:pos + 12], 2)
                lev = _sbits(bits[pos + 12:pos + 22])
                pos += 22
            else:
                for n in range(2, 17):
                    rl = DEC.get(bits[pos:pos + n])
                    if rl:
                        break
                else:
                    raise ValueError(f"bad VLC at bit {pos}")
                run, lev = rl
                pos += n
                if bits[pos] == "1":
                    lev = -lev
                pos += 1
            i += run + 1
            assert i < 64, f"run past the block at bit {pos}"
            levels.append((i, lev))
        blocks.append({"bits": bits[start:pos], "levels": levels, "dc": dc})
    tail = bits[pos:]
    return {"count": count, "q": q, "tail_bits": len(tail)}, blocks


def block_bits(dc, levels):
    out = [format(dc & 0x3FF, "010b")]
    last = 0
    codes = 1
    for i, lev in levels:
        run = i - last - 1
        last = i
        c = ENC.get((run, abs(lev)))
        if c and lev:
            out.append(c + ("1" if lev < 0 else "0"))
        else:
            out.append(ESC + format(run, "06b") + format(lev & 0x3FF, "010b"))
        codes += 1
    out.append(EOB)
    return "".join(out), codes + 1


def assemble(q, blocks):
    """[block bits] -> frame bytes (header + bitstream). Each block is a (bits, mdec code count) pair."""
    bits = "".join(b for b, _ in blocks) + END
    codes = sum(c for _, c in blocks)
    bits += "0" * (-len(bits) % 32)
    words = np.packbits(np.frombuffer(bits.encode(), dtype=np.uint8) - 48).view(">u2").astype("<u2")
    count = ((codes + 1) // 2 + 31) & ~31
    return struct.pack("<HHHH", count, 0x3800, q, 2) + words.tobytes()


def codes_of(block):
    return len(block["levels"]) + 2


# ---------------------------------------------------------------- pixels

def dequant(dc, levels, q):
    c = np.zeros(64)
    c[0] = 2 * dc
    for i, lev in levels:
        j = ZIGZAG[i]
        c[j] = lev * q * QMAT[j] / 8
    return c.reshape(8, 8)


def idct(c):
    return DCT.T @ c @ DCT


def quantize(px, q):
    """8x8 centred samples (-128..127) -> (dc, [(zigzag index, level)])."""
    c = (DCT @ px @ DCT.T).reshape(64)
    dc = int(np.clip(round(c[0] / 2), -512, 511))
    levels = []
    for i in range(1, 64):
        j = ZIGZAG[i]
        lev = int(np.clip(round(c[j] * 8 / (q * QMAT[j])), -511, 511))
        if lev:
            levels.append((i, lev))
    return dc, levels


def mb_order(w, h):
    """Stream order of macroblocks: [(mx, my)]."""
    return [(x, y) for x in range((w + 15) // 16) for y in range((h + 15) // 16)]


def decode(raw, w, h):
    """Frame bytes -> (Y, Cb, Cr) float planes, Y full size, chroma half size, centred on 0."""
    hdr, blocks = parse(raw, w, h)
    q = hdr["q"]
    W, H = ((w + 15) // 16) * 16, ((h + 15) // 16) * 16
    Y = np.zeros((H, W))
    Cb = np.zeros((H // 2, W // 2))
    Cr = np.zeros((H // 2, W // 2))
    for k, (mx, my) in enumerate(mb_order(w, h)):
        b = [idct(dequant(blk["dc"], blk["levels"], q)) for blk in blocks[k * 6:k * 6 + 6]]
        Cr[my * 8:my * 8 + 8, mx * 8:mx * 8 + 8] = b[0]
        Cb[my * 8:my * 8 + 8, mx * 8:mx * 8 + 8] = b[1]
        for n in range(4):
            y0, x0 = my * 16 + (n // 2) * 8, mx * 16 + (n % 2) * 8
            Y[y0:y0 + 8, x0:x0 + 8] = b[2 + n]
    return Y, Cb, Cr


def to_rgb(Y, Cb, Cr, w, h):
    cb = Cb.repeat(2, 0).repeat(2, 1)
    cr = Cr.repeat(2, 0).repeat(2, 1)
    y = Y + 128
    rgb = np.stack([y + 1.402 * cr, y - 0.344136 * cb - 0.714136 * cr, y + 1.772 * cb], -1)
    return np.clip(np.round(rgb), 0, 255).astype(np.uint8)[:h, :w]


def from_rgb(rgb):
    """RGB uint8 (H, W, 3) padded to 16 -> (Y, Cb, Cr) centred, chroma averaged 2x2."""
    r, g, b = [rgb[..., i].astype(float) for i in range(3)]
    Y = 0.299 * r + 0.587 * g + 0.114 * b - 128
    Cb = -0.168736 * r - 0.331264 * g + 0.5 * b
    Cr = 0.5 * r - 0.418688 * g - 0.081312 * b
    half = lambda p: p.reshape(p.shape[0] // 2, 2, p.shape[1] // 2, 2).mean((1, 3))
    return Y, half(Cb), half(Cr)


def encode_mb(Y, Cb, Cr, mx, my, q):
    """The 6 blocks of macroblock (mx, my) from planes -> [(dc, levels)] in stream order."""
    out = [quantize(Cr[my * 8:my * 8 + 8, mx * 8:mx * 8 + 8], q), quantize(Cb[my * 8:my * 8 + 8, mx * 8:mx * 8 + 8], q)]
    for n in range(4):
        y0, x0 = my * 16 + (n // 2) * 8, mx * 16 + (n % 2) * 8
        out.append(quantize(Y[y0:y0 + 8, x0:x0 + 8], q))
    return out


def rebuild(raw, w, h, Y, Cb, Cr, mbs, cap):
    """Re-encode macroblocks `mbs` (set of (mx, my)) from the edited planes, keep every other block's bits, and
    thin the new blocks' AC (drop the smallest levels, highest frequencies first) until the frame fits `cap` bytes.
    Returns the frame bytes."""
    hdr, blocks = parse(raw, w, h)
    q = hdr["q"]
    order = mb_order(w, h)
    new = {}
    for k, (mx, my) in enumerate(order):
        if (mx, my) in mbs:
            for n, (dc, lev) in enumerate(encode_mb(Y, Cb, Cr, mx, my, q)):
                new[k * 6 + n] = [dc, lev]
    floor = 0
    while True:
        parts = []
        for k, blk in enumerate(blocks):
            if k in new:
                dc, lev = new[k]
                lev = [(i, v) for i, v in lev if abs(v) > floor]
                parts.append(block_bits(dc, lev))
            else:
                parts.append((blk["bits"], codes_of(blk)))
        out = assemble(q, parts)
        if len(out) <= cap or not new:
            assert len(out) <= cap, f"frame does not fit: {len(out)} > {cap}"
            return out, floor
        floor += 1


def main(argv):
    cmd, path = argv[0], argv[1]
    data = open(path, "rb").read()
    fr = frames(data)
    if cmd == "info":
        for no in sorted(fr)[:int(argv[2]) if len(argv) > 2 else None]:
            f = fr[no]
            raw = frame_data(data, f)
            cnt, _, q, ver = struct.unpack_from("<HHHH", raw)
            print(f"frame {no}: {f['w']}x{f['h']} sectors {f['sectors'][0]}+{len(f['sectors'])} size {f['size']} "
                  f"q {q} v{ver} count {cnt} hdr {f['hdr'][0x14:0x20].hex()}")
        print(f"{len(fr)} frames")
    elif cmd == "png":
        from PIL import Image
        f = fr[int(argv[2])]
        Y, Cb, Cr = decode(frame_data(data, f), f["w"], f["h"])
        Image.fromarray(to_rgb(Y, Cb, Cr, f["w"], f["h"])).save(argv[3])
    elif cmd == "selftest":
        f = fr[int(argv[2])]
        raw = frame_data(data, f)
        hdr, blocks = parse(raw, f["w"], f["h"])
        parts = [block_bits(b["dc"], b["levels"]) for b in blocks]
        same = sum(p[0] == b["bits"] for p, b in zip(parts, blocks))
        out = assemble(hdr["q"], parts)
        print(f"{len(blocks)} blocks, {same} re-encoded bit-identical; header count {hdr['count']} -> "
              f"{struct.unpack_from('<H', out)[0]}; size {f['size']} -> {len(out)}; tail bits {hdr['tail_bits']}")


if __name__ == "__main__":
    main(sys.argv[1:])
