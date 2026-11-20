# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/font6.txt | drawn for the owner's Vattroller X translation (`../vattroller-x-en/fonts/font6.txt`, MIT), copied 2026-11-20 | MIT, same owner | yes | every in-game English letter (pair glyphs, `tools/font_en.py`, `asm/font.asm`) | added … ♪ ♥; only the 84 characters in `font_en.CHARS` are used |
