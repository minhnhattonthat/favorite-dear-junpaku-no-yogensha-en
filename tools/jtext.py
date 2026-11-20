"""jtext.py: Shift-JIS bytes <-> the script's text form (the `jp`/`en` columns of script/*.tsv). Roundtrip-exact.

    decode(b) -> str, encode(str) -> bytes, and encode(decode(b)) == b for any b.

Text form:
- double-byte SJIS characters as themselves (only when cp932 maps them back to the same bytes; NEC/IBM duplicate codes
  and unmapped codes become hex tags);
- printable ASCII as itself, except `{` `}` (tag delimiters) and the backslash escapes below;
- MSG/EVX escapes: `\\l` -> {n} (line break), `\\k` -> {wait} (wait for a key), `\\c` -> {clear} (new page);
- anything else as hex, one tag per byte: {0A}, {FF}.
Callers add their own tags for format codes (ssb ops, .end CRLF) by passing `tags`: {tag name: bytes}."""
import re

LEAD = set(range(0x81, 0xA0)) | set(range(0xE0, 0xFD))
ESC = {b"\\l": "n", b"\\k": "wait", b"\\c": "clear"}
TAG = re.compile(r"\{([^{}]*)\}")


def decode(b, escapes=True):
    out = []
    i, n = 0, len(b)
    while i < n:
        c = b[i]
        if c in LEAD and i + 1 < n:
            pair = b[i:i + 2]
            try:
                ch = pair.decode("cp932")
                if ch.encode("cp932") == pair and len(ch) == 1:
                    out.append(ch)
                    i += 2
                    continue
            except UnicodeDecodeError:
                pass
            out.append(f"{{{c:02X}}}")
            i += 1
            continue
        if escapes and c == 0x5C and b[i:i + 2] in ESC:
            out.append("{" + ESC[b[i:i + 2]] + "}")
            i += 2
            continue
        if 0x20 <= c < 0x7F and c not in (0x7B, 0x7D):
            out.append(chr(c))
        else:
            out.append(f"{{{c:02X}}}")
        i += 1
    return "".join(out)


def encode(s, tags=None):
    """Text form -> bytes. `tags` maps extra tag names to bytes (checked before the built-in ones)."""
    rev = {v: k for k, v in ESC.items()}
    out = bytearray()
    pos = 0
    for m in TAG.finditer(s):
        out += _plain(s[pos:m.start()])
        name = m.group(1)
        if tags and name in tags:
            out += tags[name]
        elif name in rev:
            out += rev[name]
        elif re.fullmatch(r"[0-9A-F]{2}", name):
            out.append(int(name, 16))
        else:
            raise ValueError(f"unknown tag {{{name}}} in {s!r}")
        pos = m.end()
    out += _plain(s[pos:])
    return bytes(out)


def _plain(s):
    if "{" in s or "}" in s:
        raise ValueError(f"stray brace in {s!r}")
    return s.encode("cp932")
