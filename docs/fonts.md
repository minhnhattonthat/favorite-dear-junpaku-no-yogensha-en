# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/font6.txt | drawn for the owner's Vattroller X translation (`../vattroller-x-en/fonts/font6.txt`, MIT), copied 2026-11-20 | MIT, same owner | yes | every in-game English letter (pair glyphs, `tools/font_en.py`, `asm/font.asm`) | added … ♪ ♥; only the 84 characters in `font_en.CHARS` are used |
| fonts/font_tag.txt | drawn for this project 2026-11-21 | this repo's licence | yes | battle status tags (G3, `tools/banners.py`), album "Prince" (G10) | 3 px lowercase, only the letters the six tags need |
| fonts/crimson/CrimsonText-*.ttf | Crimson Text (https://github.com/google/fonts/tree/main/ofl/crimsontext, fetched 2026-11-21) | SIL OFL 1.1 (`fonts/crimson/OFL.txt`) | yes (only rendered into FMV frames; the font file itself is not in the patch) | FMV captions and staff roll (G14/G15, `tools/fmv.py`) | none |
| fonts/label14.txt | DejaVu Sans Condensed 2.37 (https://github.com/dejavu-fonts/dejavu-fonts/releases/tag/version_2_37, dejavu-fonts-ttf-2.37.zip sha1 bdc4350b771c6c23e8a40b2413595d1055cff2ab), rasterized at 14 px with no smoothing by `tools/labelfont.py make` | Bitstream Vera licence + public domain (DejaVu changes) | yes (the licence allows embedding and modified copies; bitmaps of it are not sold alone) | album profile panel (G10, `tools/album.py`, `gfx/album.tsv`); file and `tools/labelfont.py` copied from `../favorite-dear-en` (same owner) 2026-11-21 | rasterized to 1 bpp, ASCII 0x21-0x7E only |
