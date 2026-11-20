"""lkf.py: the game's "+LKF" archives (FD2SN/FD2BN/GRPDATA/SSB_DATA.LKF).

    python -X utf8 tools/lkf.py list  work/disc/tree/FD2SN.LKF
    python -X utf8 tools/lkf.py extract work/disc/tree/FD2SN.LKF work/lkf/FD2SN

Layout (docs/re/disc.md): header 0x20 bytes = "+LKF", u32 count, u32 data start (first entry's offset),
u32 largest entry size, 16 zero bytes. Then `count` entries of 0x20 bytes from 0x20:
name[16] (NUL-padded ASCII), 7 zero bytes, u8 flags (0x20 seen everywhere), u32 offset, u32 size.
Entries are sector (0x800) aligned and stored in offset order; the gap after each file is zero padding."""
import struct
import sys
from pathlib import Path

SECTOR = 0x800


def parse(data):
    assert data[:4] == b"+LKF", "not an LKF archive"
    count, start, biggest = struct.unpack_from("<III", data, 4)
    entries = []
    for i in range(count):
        base = 0x20 + 0x20 * i
        name = data[base:base + 16].split(b"\0")[0].decode("ascii")
        pad = data[base + 16:base + 23]
        flags = data[base + 23]
        off, size = struct.unpack_from("<II", data, base + 24)
        entries.append({"index": i, "name": name, "flags": flags, "off": off, "size": size, "pad": pad})
    return {"count": count, "start": start, "biggest": biggest, "entries": entries}


def files(data):
    """Yield (entry, bytes) for every entry."""
    for e in parse(data)["entries"]:
        yield e, data[e["off"]:e["off"] + e["size"]]


def build(header_src, contents):
    """Rebuild an archive from the original header bytes and a list of entry payloads (same order).
    Payloads are laid out back to back, each starting on a sector boundary, like the original."""
    info = parse(header_src)
    out = bytearray(header_src[:info["start"]])
    pos = info["start"]
    biggest = 0
    for e, payload in zip(info["entries"], contents):
        assert len(out) == pos
        struct.pack_into("<II", out, 0x20 + 0x20 * e["index"] + 24, pos, len(payload))
        out += payload
        # the original packer always pads at least one byte: a payload ending exactly on a sector boundary
        # is followed by a whole zero sector (FD2SN ASIA_B.VB), so next = floor(size / sector) + 1 sectors
        pos += (len(payload) // SECTOR + 1) * SECTOR
        out += b"\0" * (pos - len(out))
        biggest = max(biggest, len(payload))
    struct.pack_into("<I", out, 12, biggest)
    return bytes(out)


def main(argv):
    if len(argv) < 2 or argv[0] not in ("list", "extract"):
        sys.exit(__doc__)
    data = Path(argv[1]).read_bytes()
    info = parse(data)
    if argv[0] == "list":
        print(f"count {info['count']} start {info['start']:#x} biggest {info['biggest']:#x}")
        for e in info["entries"]:
            print(f"{e['index']:4} {e['off']:#010x} {e['size']:#09x} {e['flags']:#04x} {e['name']} {data[e['off']:e['off']+4].hex()}")
    else:
        out = Path(argv[2])
        out.mkdir(parents=True, exist_ok=True)
        for e, payload in files(data):
            (out / f"{e['index']:04d}_{e['name']}").write_bytes(payload)
        print(f"{info['count']} files -> {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
