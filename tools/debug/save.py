"""save.py: read and edit this game's save files (純白の預言者 ゲームデータ) on a PS1 memory card image.

    python -X utf8 tools/debug/save.py ls CARD.mcd                       every FD2 game file: slot and header fields
    python -X utf8 tools/debug/save.py set CARD.mcd OUT.mcd [--slot N] FIELD=VALUE ..
    python -X utf8 tools/debug/save.py poke CARD.mcd OUT.mcd [--slot N] OFFSET=HEXBYTES ..   raw bytes at a data offset

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


def main(argv):
    if not argv or argv[0] not in ("ls", "set", "poke"):
        print(__doc__)
        return 2
    cmd, path = argv[0], argv[1]
    card = bytearray(open(path, "rb").read())
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
