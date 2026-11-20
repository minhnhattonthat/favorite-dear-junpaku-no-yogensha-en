"""misctext.py: the small text formats.

- ending narrations (SSB_DATA *.end): plain SJIS, CRLF line breaks, no header. A row is a paragraph (lines between
  blank lines), its line breaks as {n}; blank lines stay as they are.
- GRPDATA Dummy00.DAT: 50-byte records = 48 bytes of text padded with full-width spaces + CRLF (docs/re/text.md;
  guess: unused). A row is a record's text without the padding; build re-pads to 48 bytes.

    end_rows(data) -> [(offset, bytes)]  end_build(data, {offset: bytes}) -> bytes   (row bytes keep CRLF inside)
    rec_rows(data) -> [(offset, bytes)]  rec_build(data, {offset: bytes}) -> bytes"""
import re

CRLF = b"\r\n"
REC, REC_TEXT, PAD = 50, 48, "　".encode("cp932")


def end_rows(data):
    out = []
    for m in re.finditer(rb"(?:[^\r\n]+\r\n)*[^\r\n]+(?=\r\n|$)", data):
        out.append((m.start(), m.group()))
    return out


def end_build(data, new):
    rows = dict(end_rows(data))
    bad = set(new) - set(rows)
    assert not bad, f"no paragraph at {sorted(bad)[:5]}"
    out, pos = bytearray(), 0
    for o in sorted(rows):
        out += data[pos:o] + new.get(o, rows[o])
        pos = o + len(rows[o])
    return bytes(out + data[pos:])


def rec_rows(data):
    assert len(data) % REC == 0
    out = []
    for o in range(0, len(data), REC):
        rec = data[o:o + REC]
        assert rec[REC_TEXT:] == CRLF, o
        t = rec[:REC_TEXT]
        while t.endswith(PAD):
            t = t[:-2]
        out.append((o, t))
    return out


def rec_build(data, new):
    out = bytearray(data)
    for o, t in new.items():
        assert o % REC == 0 and o < len(data), o
        assert len(t) <= REC_TEXT, f"{o}: {len(t)} bytes, record holds {REC_TEXT}"
        pad = PAD * ((REC_TEXT - len(t)) // 2) + b" " * ((REC_TEXT - len(t)) % 2)
        out[o:o + REC_TEXT] = t + pad
    return bytes(out)
