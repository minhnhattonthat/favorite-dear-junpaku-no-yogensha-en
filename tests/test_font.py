"""Phase 5 English font: pair codes, marker rows, the EXE font patch (docs/re/text.md §English font)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build  # noqa: E402
import font_en  # noqa: E402
import jtext  # noqa: E402

needs_tree = pytest.mark.skipif(not (build.TREE / build.EXE_NAME).is_file(), reason="no unpacked disc (work/disc/tree)")


def test_every_pair_round_trips():
    seen = set()
    for a in font_en.CHARS:
        for b in font_en.CHARS:
            code = font_en.pair_code(a, b)
            assert font_en.decode_pair(code) == (a, b)
            seen.add(code)
    assert len(seen) == font_en.G ** 2


def test_glyphs_fit_their_half():
    font = font_en.load_font()
    for ch in font_en.CHARS:
        px = font_en.glyph_pixels(ch, font)
        assert all(r[font_en.HALF - 1] == 0 for r in px), f"{ch!r} inks its gap column"


def test_to_pairs_keeps_tags_and_japanese():
    b = jtext.encode(font_en.to_pairs("Hi, ＄＄＄＄＄＄!{n}Ok"))
    assert b == (font_en.pair_code("H", "i") + font_en.pair_code(",", " ") + "＄＄＄＄＄＄".encode("cp932")
                 + font_en.pair_code("!", " ") + b"\\l" + font_en.pair_code("O", "k"))


def test_to_pairs_keeps_printf_s():
    b = jtext.encode(font_en.to_pairs("Go to %s?"))
    assert b == font_en.pair_code("G", "o") + font_en.pair_code(" ", "t") + font_en.pair_code("o", " ") + b"%s" \
        + font_en.pair_code("?", " ")


def test_ruler_marks_line_positions():
    import marker
    t = marker.ruler_text("ABC", "あいうえお{n}かき")
    assert t == "ABC :....1....: {n}....:."      # 3 letters per character; odd runs padded with a space


@needs_tree
def test_pair_codes_miss_the_japanese_font():
    import fontinfo
    leads = {c >> 8 for c in fontinfo.charlist(fontinfo.fpk())}
    assert not leads & set(font_en.LEADS)


@needs_tree
def test_marker_rows_keep_their_length():
    import extract
    import marker
    for s in extract.sources():
        raws = {r.id: r.raw for r in s.rows}
        for i, t in marker.texts_for(s).items():
            n = len(s.encode(i, font_en.to_pairs(t)))
            assert n in (len(raws[i]), len(raws[i]) - 1), i      # -1: an odd count of ASCII bytes in the Japanese


@needs_tree
@pytest.mark.skipif(not build.ARMIPS.is_file(), reason="no armips in tools/")
def test_patch_exe_prepends_block_and_hooks():
    orig = (build.TREE / build.EXE_NAME).read_bytes()
    out = build.patch_exe(orig)
    assert len(out) == len(orig) + build.EXE_PAD
    assert struct.unpack_from("<II", out, 0x18) == (0x80020000 - build.EXE_PAD, struct.unpack_from("<I", orig, 0x1C)[0]
                                                    + build.EXE_PAD)
    assert struct.unpack_from("<I", out, 0x10) == struct.unpack_from("<I", orig, 0x10)    # entry point kept

    def word(data, va, base):
        return struct.unpack_from("<I", data, va - base + 0x800)[0]
    hooked = {0x8002C500, 0x8002C504, 0x8002C508, 0x8002C50C, 0x8002C548, 0x8002C5EC, 0x8002C5F0, 0x8002CCD8, 0x8002CCEC, 0x8002CDF0, 0x8002CE00}
    hooked |= {a + 4 * k for a in (0x8002BF50, 0x8002C118, 0x8002C358) for k in range(6)}
    for va in range(0x80020000, 0x80020000 + len(orig) - 0x800, 4):
        if va not in hooked:
            assert word(out, va, 0x8001E000) == word(orig, va, 0x80020000), hex(va)
