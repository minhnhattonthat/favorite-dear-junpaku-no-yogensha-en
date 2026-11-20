# Graphics text survey (in progress)

## Static sweep

`python -X utf8 tools/tim.py dump work/gfx` -> 1252 TIM images from all LKF archives (`work/gfx/index.tsv`; entries
with no TIM listed in `work/gfx/skipped.tsv`: 1158, mostly scripts/sound; in GRPDATA: PIX, SFM, SFA, TMD, BLF, CLT,
RCT, DAT, FPK, BIN). `python -X utf8 tools/gfxsheets.py work/gfx work/gfx/sheets --per 40 --width 1600` -> 32
labelled sheets (`work/gfx/sheets/index.tsv`). **Not reviewed yet**: read each sheet (in chunks, fresh context) and
list every Japanese cell below by image name.

Not covered by the TIM sweep yet (render them next):
- `Name_NNN.PIX` (88 files, 384 bytes each: name-plate bitmaps? 48x16 4bpp or 24x16 8bpp; CLUT unknown);
- `6x624_4.BLF` (432 KB, "BLF" magic) with `6x624_4.CLT/.rct`: likely a 6x624 tile strip, maybe text;
- SFM/SFA (sprite frame maps / animations over TIM sheets: text only via their TIMs);
- FMV: DEMO.STR shows burned-in Japanese captions in the opening (seen at boot f2100-f4500: うるわしき実り豊かな土地...),
  ENDING.STR to check.

## Tour (cold boot, original disc, `work/qa/boot0`, `boot1`, `newgame0..3`)

| Screen | Japanese seen | Source guess |
|---|---|---|
| Title (f6000+) | logo 純白の預言者 (with small English "FAVORITE DEAR"); menu NEW GAME/LOAD GAME/OPTION is already English | TIM in GRPDATA |
| Opening movie DEMO.STR | caption lines in the video | FMV, burned in |
| New Game name/birthday screen | labels Name/Birth already English; message box text (名前を決定します。, これでいいですか？ はい/いいえ) | font text (EXE/overlay strings) |
| Name-entry keyboard | katakana grid, "END" | grid probably font-drawn from a string table; check (English letters needed for names) |

## Rows (to fill: screen, image, layer, source, status)

| # | Element | Image / source | Status |
|---|---|---|---|
