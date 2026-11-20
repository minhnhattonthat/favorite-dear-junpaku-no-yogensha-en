"""msg.py: the message banks (SSB_DATA *.MSG). Five layouts (docs/re/text.md §MSG banks):

- plain:  u16 offset table (count = first offset / 2); entry = u16 length + text. Most banks.
- reply:  BrvMsgQ*/BMsgQ*: plain, but entries 3, 6, 9.. (hero replies) start with 2 bytes (face, affection delta?)
          before the length.
- idtab:  MssReq/MssAns*: u32 count, count x (u16 offset, u16 id), entries = u16 length + text.
- names:  EvName: u32 count, count x 24-byte records (u16 id, 22-byte NUL-padded text).
- battle: BTL_EVT*: u16 count, count x (u16 id, u16 offset), u32 0xFFFFFFFF; record = 18 u16 slot offsets (0 = none,
          relative to the record) then messages: u16 length, speaker NUL text, u16 tail (0xFFFF or a value, guess
          voice). Slots are entry points into the record's message stream.

    parse(name, data) -> Bank (strings: list of [key, bytes]); build(bank) -> bytes. build(parse(x)) == x.
    python -X utf8 tools/msg.py dump FILE"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jtext  # noqa: E402


def layout(name):
    n = name.split("_", 1)[-1] if name[:4].isdigit() else name
    if n.startswith(("BrvMsgQ", "BMsgQ")):
        return "reply"
    if n.startswith(("MssReq", "MssAns")):
        return "idtab"
    if n.startswith("EvName"):
        return "names"
    if n.startswith("BTL_EVT"):
        return "battle"
    return "plain"


class Bank:
    """strings: list of [key, bytes]; key is a stable id inside the bank (hex offset of the text in the original)."""

    def __init__(self, kind, data):
        self.kind, self.orig, self.strings, self.meta = kind, data, [], {}

    def texts(self):
        return {k: v for k, v in self.strings}

    def replace(self, new):
        """new: {key: bytes}; unknown keys are an error."""
        keys = {k for k, _ in self.strings}
        bad = set(new) - keys
        assert not bad, f"unknown keys {sorted(bad)[:5]}"
        self.strings = [[k, new.get(k, v)] for k, v in self.strings]


def _u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def parse(name, data):
    kind = layout(name)
    bank = Bank(kind, data)
    if kind in ("plain", "reply"):
        first = _u16(data, 0)
        offs = [_u16(data, i) for i in range(0, first, 2)]
        assert offs == sorted(offs) and offs[0] == first, name
        pre = []
        for i, o in enumerate(offs):
            nxt = offs[i + 1] if i + 1 < len(offs) else len(data)
            p = 2 if (kind == "reply" and i % 3 == 0 and i > 0) else 0
            n = _u16(data, o + p)
            assert o + p + 2 + n == nxt, (name, i)
            pre.append(data[o:o + p])
            bank.strings.append([f"{o + p + 2:04X}", data[o + p + 2:nxt]])
        bank.meta["pre"] = pre
        bank.meta["header"] = first
    elif kind == "idtab":
        cnt = struct.unpack_from("<I", data, 0)[0]
        pairs = [struct.unpack_from("<HH", data, 4 + 4 * i) for i in range(cnt)]
        assert [o for o, _ in pairs] == sorted(o for o, _ in pairs) and pairs[0][0] == 4 + 4 * cnt, name
        for i, (o, _id) in enumerate(pairs):
            nxt = pairs[i + 1][0] if i + 1 < cnt else len(data)
            n = _u16(data, o)
            assert o + 2 + n == nxt, (name, i)
            bank.strings.append([f"{o + 2:04X}", data[o + 2:nxt]])
        bank.meta["ids"] = [i for _, i in pairs]
        bank.meta["header"] = 4 + 4 * cnt
    elif kind == "names":
        cnt = struct.unpack_from("<I", data, 0)[0]
        assert len(data) == 4 + 24 * cnt, name
        ids = []
        for i in range(cnt):
            o = 4 + 24 * i
            ids.append(_u16(data, o))
            field = data[o + 2:o + 24]
            text = field.split(b"\0")[0]
            assert not field[len(text):].strip(b"\0"), (name, i)
            bank.strings.append([f"{o + 2:04X}", text])
        bank.meta["ids"] = ids
        bank.meta["header"] = 4
    else:  # battle
        cnt = _u16(data, 0)
        pairs = [struct.unpack_from("<HH", data, 2 + 4 * i) for i in range(cnt)]
        end = 2 + 4 * cnt
        assert data[end:end + 4] == b"\xff" * 4 and pairs[0][1] == end + 4, name
        recs = []
        for i, (_id, o) in enumerate(pairs):
            nxt = pairs[i + 1][1] if i + 1 < cnt else len(data)
            assert nxt >= o, name
            slots = list(struct.unpack_from("<18H", data, o))
            msgs = []  # (rel offset, tail)
            p = o + 0x24
            while p < nxt:
                n = _u16(data, p)
                body = data[p + 2:p + 2 + n]
                spk, _, text = body.partition(b"\0")
                assert _ == b"\0", (name, i, hex(p))
                msgs.append((p - o, _u16(data, p + 2 + n)))
                bank.strings.append([f"{p + 2:04X}S", spk])
                bank.strings.append([f"{p + 3 + len(spk):04X}", text])
                p += 4 + n
            assert p == nxt, (name, i)
            starts = {rel for rel, _ in msgs}
            assert all(s == 0 or s in starts for s in slots), (name, i)
            recs.append({"id": _id, "slots": slots, "msgs": msgs})
        bank.meta["recs"] = recs
        bank.meta["header"] = end + 4
    return bank


def build(bank):
    kind, strings = bank.kind, bank.strings
    if kind in ("plain", "reply"):
        n = len(strings)
        out = bytearray(2 * n)
        for i, ((_, s), pre) in enumerate(zip(strings, bank.meta["pre"])):
            struct.pack_into("<H", out, 2 * i, len(out))
            out += pre + struct.pack("<H", len(s)) + s
        assert len(out) < 0x10000, "bank over 64 KB (16-bit offsets)"
        return bytes(out)
    if kind == "idtab":
        ids = bank.meta["ids"]
        out = bytearray(struct.pack("<I", len(ids)) + b"\0" * 4 * len(ids))
        for i, ((_, s), _id) in enumerate(zip(strings, ids)):
            struct.pack_into("<HH", out, 4 + 4 * i, len(out), _id)
            out += struct.pack("<H", len(s)) + s
        assert len(out) < 0x10000, "bank over 64 KB (16-bit offsets)"
        return bytes(out)
    if kind == "names":
        ids = bank.meta["ids"]
        out = bytearray(struct.pack("<I", len(ids)))
        for (_, s), _id in zip(strings, ids):
            assert len(s) <= 22, f"EvName text over 22 bytes: {s!r}"  # guess: a NUL is not required at 22
            out += struct.pack("<H", _id) + s + b"\0" * (22 - len(s))
        return bytes(out)
    # battle
    recs = bank.meta["recs"]
    out = bytearray(struct.pack("<H", len(recs)) + b"\0" * 4 * len(recs) + b"\xff" * 4)
    it = iter(strings)
    for i, r in enumerate(recs):
        start = len(out)
        struct.pack_into("<HH", out, 2 + 4 * i, r["id"], start)
        body = bytearray()
        remap = {}
        for rel, tail in r["msgs"]:
            remap[rel] = 0x24 + len(body)
            spk, text = next(it)[1], next(it)[1]
            m = spk + b"\0" + text
            body += struct.pack("<H", len(m)) + m + struct.pack("<H", tail)
        slots = [remap[s] if s else 0 for s in r["slots"]]
        out += struct.pack("<18H", *slots) + body
        assert len(out) < 0x10000, "bank over 64 KB (16-bit offsets)"
    return bytes(out)


def main(argv):
    if len(argv) != 2 or argv[0] != "dump":
        sys.exit(__doc__)
    p = Path(argv[1])
    bank = parse(p.name, p.read_bytes())
    print(f"# {p.name}: {bank.kind}, {len(bank.strings)} strings")
    for k, s in bank.strings:
        print(f"{k}\t{jtext.decode(s)}")


if __name__ == "__main__":
    main(sys.argv[1:])
