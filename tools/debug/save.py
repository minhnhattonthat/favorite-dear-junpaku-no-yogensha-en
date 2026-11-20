"""save.py: read and edit this game's save files (純白の預言者 ゲームデータ) on a PS1 memory card image.

    python -X utf8 tools/debug/save.py ls CARD.mcd                       every FD2 game file: slot and header fields
    python -X utf8 tools/debug/save.py set CARD.mcd OUT.mcd [--slot N] FIELD=VALUE ..
    python -X utf8 tools/debug/save.py poke CARD.mcd OUT.mcd [--slot N] OFFSET=HEXBYTES ..   raw bytes at a data offset
    python -X utf8 tools/debug/save.py system CARD.mcd OUT.mcd [time=S] [clears=1,1,1,1,1,1,1] [extra=N] [flags=all|HEX]
        write the system file BISLPS-02754.0 (clear data: what OMAKE loads); default every hero cleared once and
        every flag byte 0xFF

Start from a game-written card (tools/debug/cards/fd2_save.mcd: New Game, then Heaven -> データ -> セーブ, slot 1;
scene heaven_saved), never from zeros. The game's save image is 0x200 bytes of card title/icon frames, then the
data the exe's pack routine 0x8002843C builds (unpack: 0x80028A84; RAM buffer 0x80099908). Checksum: u16 at data
+0x9FE = sum of the little-endian u16 words of data +0x000..+0x9FE (mod 0x10000); a wrong one lists the file as
"No Data". set/poke recompute it (tests/test_save.py; in game: scene load_edited). Layout:
tools/debug/save_layout.tsv (data offsets; the header is mapped, the rest is the 7 hero records (0x8002B124/
0x8002B1F8, variable size) and game-state blocks, not yet).
"""
import csv
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mcd  # noqa: E402

PRODUCT = "BISLPS-02754"     # directory filename prefix of this game's files (the first game's: BISLPS-01759)
DATA = 0x200                 # data offset inside the save block (after the SC title frame and icon frames)
LAYOUT = os.path.join(HERE, "save_layout.tsv")
FMT = {"u8": "<B", "u16": "<H", "u32": "<I"}


def layout():
    with open(LAYOUT, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.reader(f, delimiter="\t") if r and not r[0].startswith("#")]
    head = rows[0]
    assert head == ["field", "offset", "type", "note"], head
    return {r[0]: {"offset": int(r[1], 16), "type": r[2], "note": r[3]} for r in rows[1:]}


def slots(card):
    """Slots holding this game's files (first block of each)."""
    return [i for i, state, _size, _nxt, name, _ok in mcd.entries(card) if state == 0x51 and name.startswith(PRODUCT)]


def base(card, slot):
    if slot is None:
        found = slots(card)
        if not found:
            sys.exit("no 純白の預言者 game file on this card")
        slot = found[0]
    elif slot not in slots(card):
        sys.exit(f"slot {slot} holds no 純白の預言者 game file")
    return slot * mcd.BLOCK + DATA


SUM = 0x9FE                  # u16 checksum offset in the data


def checksum(card, b):
    return sum(struct.unpack_from(f"<{SUM // 2}H", card, b)) & 0xFFFF


def stored_sum(card, b):
    return struct.unpack_from("<H", card, b + SUM)[0]


def fix(card, b):
    struct.pack_into("<H", card, b + SUM, checksum(card, b))


def get(card, b, f):
    if f["type"].startswith("bytes"):
        n = int(f["type"][5:])
        return card[b + f["offset"]:b + f["offset"] + n].hex(" ")
    return struct.unpack_from(FMT[f["type"]], card, b + f["offset"])[0]


def put(card, b, f, value):
    if f["type"].startswith("bytes"):
        raw = bytes.fromhex(value)
        assert len(raw) == int(f["type"][5:]), f"{len(raw)} bytes for a {f['type']} field"
        card[b + f["offset"]:b + f["offset"] + len(raw)] = raw
    else:
        struct.pack_into(FMT[f["type"]], card, b + f["offset"], int(value, 0))


SYS_NAME = PRODUCT + ".0"    # the system file: the exe's name table 0x80099578 (.0 system, .1-.C game data 01-12)
SYS_TITLE = "純白の預言者　システム　　　　　"   # exe 0x8008CD74, the card title of the system file
SYS_SIZE = 0x10C             # the system struct (RAM 0x80084010, getter 0x8002B3AC) is data +0x000..+0x10B


def system_data(time=0, clears=(1,) * 7, extra=0, flags=b"\xff" * 0x100):
    """The system struct: u32 total play time (s), u8 clear count per hero x7 (+4), u8 count (+0xB), 0x100 flag
    bytes (+0xC; each ending ORs in RAM 0x8007F2EC: 0x8002B3B8). The clear save (mode 5) and system save (mode 2)
    write it; system load (OMAKE) copies it back (0x80090E48)."""
    assert len(clears) == 7 and len(flags) == 0x100
    return struct.pack("<I7BB", time, *clears, extra) + bytes(flags)


def put_system(card, data):
    """Write (or rewrite) BISLPS-02754.0 holding DATA, its header frames copied from a game file on the card."""
    games = [s for s in slots(card) if not mcd.entries(card)[s - 1][4].endswith(".0")]
    if not games:
        sys.exit("need a game-written 純白の預言者 game file on the card to copy the header and icon from")
    ents = mcd.entries(card)
    have = [i for i, st, _s, _n, name, _ok in ents if st == 0x51 and name == SYS_NAME]
    free = [i for i, st, *_ in ents if st == 0xA0]
    slot = (have or free or [None])[0]
    if slot is None:
        sys.exit("no free block on the card")
    o = slot * mcd.FRAME
    frame = bytearray(mcd.FRAME)
    struct.pack_into("<IIH", frame, 0, 0x51, mcd.BLOCK, 0xFFFF)
    frame[10:10 + len(SYS_NAME)] = SYS_NAME.encode("ascii")
    frame[127] = mcd.xor(frame[:127])
    card[o:o + mcd.FRAME] = frame
    blk, src = slot * mcd.BLOCK, games[0] * mcd.BLOCK
    card[blk:blk + mcd.BLOCK] = bytes(mcd.BLOCK)
    card[blk:blk + DATA] = card[src:src + DATA]
    title = SYS_TITLE.encode("shift_jis")
    card[blk + 4:blk + 68] = title + bytes(64 - len(title))
    card[blk + DATA:blk + DATA + len(data)] = data
    fix(card, blk + DATA)
    return slot


def main(argv):
    if not argv or argv[0] not in ("ls", "set", "poke", "system"):
        print(__doc__)
        return 2
    cmd, path = argv[0], argv[1]
    card = bytearray(open(path, "rb").read())
    if cmd == "system":
        kw = dict(kv.partition("=")[::2] for kv in argv[3:])
        flags = kw.pop("flags", "all")
        data = system_data(time=int(kw.pop("time", "0"), 0),
                           clears=tuple(int(x, 0) for x in kw.pop("clears", "1,1,1,1,1,1,1").split(",")),
                           extra=int(kw.pop("extra", "0"), 0),
                           flags=b"\xff" * 0x100 if flags == "all" else bytes.fromhex(flags).ljust(0x100, b"\0"))
        if kw:
            sys.exit(f"unknown system field(s): {', '.join(kw)}; known: time clears extra flags")
        slot = put_system(card, data)
        open(argv[2], "wb").write(card)
        print(f"wrote {argv[2]} ({SYS_NAME} in slot {slot})")
        return 0
    fields = layout()
    if cmd == "ls":
        for s in slots(card):
            print(f"slot {s}: {mcd.title(card, s)}")
            b = s * mcd.BLOCK + DATA
            ok = "ok" if checksum(card, b) == stored_sum(card, b) else f"BAD (want {checksum(card, b):04X})"
            print(f"  checksum     {stored_sum(card, b):04X} {ok}")
            for name, f in fields.items():
                print(f"  {name:<12} {get(card, b, f)!s:<24} {f['note']}")
        return 0
    out, rest = argv[2], argv[3:]
    slot = None
    if rest[:1] == ["--slot"]:
        slot, rest = int(rest[1]), rest[2:]
    b = base(card, slot)
    for kv in rest:
        k, _, v = kv.partition("=")
        if cmd == "set":
            if k not in fields:
                sys.exit(f"unknown field {k}; known: {', '.join(fields)}")
            put(card, b, fields[k], v)
        else:
            raw = bytes.fromhex(v)
            card[b + int(k, 16):b + int(k, 16) + len(raw)] = raw
    fix(card, b)
    open(out, "wb").write(card)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
