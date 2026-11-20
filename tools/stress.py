"""stress.py: write the phase 8 stress saves (worst-case angel names and numbers) from the fixture card.

    python -X utf8 tools/stress.py            regenerate work/saves/stress_<case>.mcd (scenes stress_* in scenes.tsv)

Only the angel's name and the header numbers are player-variable in this game (heroes, fairies, towns and items have
fixed names, all inside the width lint). The name is stored twice: name-entry grid indices in the save header (+4,
what the load list shows; A=0x00, a=0x20, katakana ラ=C6 ビ=E1 エ=A3 ル=C8, FE = empty slot) and the
committed name at data +0x2DC (12 bytes: SJIS for kana, pair codes for Latin, see asm/name.asm). Cases:
  kana   6 katakana: the widest name (6 full 12-px cells = 12 letters), play time 99:59:59, 9999 days
  wide   WWWWWW: the longest Latin name (6 letters, 3 pair cells)
  short  A: a 1-letter name (odd: the pair is "A "), play time 0, day 1
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "debug"))
import font_en  # noqa: E402
import save  # noqa: E402

SRC = os.path.join(ROOT, "tools", "debug", "cards", "fd2_edited.mcd")
OUT = os.path.join(ROOT, "work", "saves")
NAME_AT = 0x2DC

KANA = {"ラ": 0xC6, "ビ": 0xE1, "エ": 0xA3, "ル": 0xC8}


def latin_index(ch):
    return ord(ch) - ord("A") if ch.isupper() else 0x20 + ord(ch) - ord("a")


def name_fields(name):
    """(header grid indices, 16 bytes; stored name, 12 bytes)."""
    if all(ch in KANA for ch in name):
        idx = bytes(KANA[ch] for ch in name)
        stored = name.encode("shift_jis")
    else:
        idx = bytes(latin_index(ch) for ch in name)
        stored = font_en.name_to_pairs(name.translate({c: c + 0xFEE0 for c in range(0x21, 0x7F)}).encode("shift_jis"))
    idx = idx.ljust(6, b"\xfe")          # the entry's 6 slots, FE = empty (pro.bin wrote ラビエル as C6 E1 A3 C8 FE FE)
    return idx.ljust(16, b"\0"), stored.ljust(12, b"\0")


CASES = {
    "kana": ("ラビエルラビ", {"playtime": 359999, "days": 9999}),
    "wide": ("WWWWWW", {}),
    "short": ("A", {"playtime": 0, "days": 1}),
}


def make(case):
    name, nums = CASES[case]
    card = bytearray(open(SRC, "rb").read())
    b = save.base(card, None)
    fields = save.layout()
    idx, stored = name_fields(name)
    save.put(card, b, fields["name"], idx.hex())
    for k, v in nums.items():
        save.put(card, b, fields[k], str(v))
    card[b + NAME_AT:b + NAME_AT + 12] = stored
    save.fix(card, b)
    return bytes(card)


def main():
    os.makedirs(OUT, exist_ok=True)
    for case in CASES:
        path = os.path.join(OUT, f"stress_{case}.mcd")
        open(path, "wb").write(make(case))
        print("wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
