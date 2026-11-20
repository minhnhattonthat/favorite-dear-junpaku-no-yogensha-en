# Text

**Encoding: Shift-JIS (cp932)** everywhere seen, with ASCII backslash escapes inside MSG text (verified: MSG, ssb, EVX,
.end and EXE strings decode to readable Japanese with `cp932`; `tools/scantext.py`). No custom table needed;
`tbl/jp.tbl` is not required for decoding. Whether the printer draws half-width ASCII (needed for English) is **not
known**: test in phase 5.

## Fonts

- `GRPDATA FD2Font.FPK` (54 KB): header `81 01 0a 0e 0c 0e ...`, u16 0x5ac (=1452, guess: glyph count) at 0x0c; an
  SJIS character list from 0x221 (`、。．・：？！...` then digits, then katakana `アィイゥ...`): **guess** glyph index =
  position in that list, so the printer maps SJIS -> list position -> cell. English needs glyphs (and list entries)
  for the letters we use. Decode in phase 5.
- EXE 0x5e9d9 and 0x5efe9: two more SJIS character lists (`：ゞ‥《≠￠□ ５ＤＳｂｑあけだはまろ ェザヅフャヲΓΣβρ ...`,
  every Nth character of a full JIS row order): guess, a glyph-index table for a second font or the name-entry grid.
- Graphics glyph strips (no SJIS): GRPDATA_0051/0052 (keyboard), 0458/0459 (battle labels), see `graphics.md`.

## Text-bearing files (text ranges)

Full per-file list: `python -X utf8 tools/scantext.py summary work/lkf work/disc/tree/SLPS_027.54 > work/scan_summary.txt`
(1782 files with hits, ~2 min). Totals (files, runs, characters incl. escapes), 2026-11-20:

| Where | Files | Runs | Chars | Format |
|---|---|---|---|---|
| SSB_DATA `*.MSG` | 108 | 13641 | 368300 | message banks (below) |
| SSB_DATA `*.ssb` | 287 of 346 | 11702 | 168637 | inline in event scripts (`events.md`) |
| SSB_DATA `*.EVX` | 269 | 5173 | 69935 | battle setups, mostly repeated unit names (`events.md`) |
| SSB_DATA `*.end` | 21 | 645 | 8535 | ending narrations, plain SJIS + CRLF |
| FD2BN overlays | op.bin, rfd2.bin, ed.bin, pro.bin | 569 | 7958 | NUL-terminated SJIS, pointers below |
| SLPS_027.54 | 1 | 513 | 3020 | NUL-terminated SJIS, pointers below |
| GRPDATA `Dummy00.DAT` | 1 | 35 | 840 | fixed 50-byte records of full-width-padded dialogue (`久しぶりだな、ラビエル。　　...`); name says dummy, guess unused: check for a reader in phase 4 |
| GRPDATA `FD2Font.FPK` | 1 | 7 | 320 | the font's character list (not text) |
| GRPDATA `*.tim/.blf/.rct`, FD2SN `*.seq/.vb/.blf` | ~1090 | - | - | false hits: pixel/sound bytes that decode as SJIS. Not text |

## MSG banks (SSB_DATA *.MSG; verified by decoding FryMsg0, T_Msg00, MssAns0)

u16 offset table at 0 (entry count = first offset / 2), then per entry: u16 byte length, then that many bytes of
SJIS text, entries back to back (no gap). **Not all banks**: BrvMsgQ0 entry 3 is `00 00 94 00` + 148 bytes of text +
`0a 00` + 10 bytes..., so some entries hold several (u16 length, text) parts, and even that model fails on a later
BrvMsg entry (`tests/test_formats.py::test_msg_banks_parse`, xfail). Decode the BrvMsgQ/BMsgQ layout in phase 4. Offsets are 16-bit, so a bank must stay under 64 KB (largest now 27 KB,
T_Msg00). Escapes seen: `\l` line break, `\k` wait for a key, `\c` clear the box (new page). Others: list them in
phase 4 (grep `\\.`). Names: FryMsg (fairy?), BrvMsgQ/BMsgQ (hero messages), MssReq/MssAns (missions),
T_Msg (teacher/tutor? "Tell me about Fein"), GenAnsw/GenNG, EMP_OK/NG, NASI_OK/NG, BTL_EVT, men3_*.

## .end files (endings; verified: feed1.end)

Plain SJIS with CRLF line breaks, no header. 21 files (feed1-3, ceed, roed...).

## EXE and overlay strings: pointer forms

`tools/retools.py` (dis / xref / va; copied from `../favorite-dear-en`). EXE: PS-X EXE, t_addr 0x80020000, file
offset = vaddr - 0x80020000 + 0x800, 0x7c000 bytes.

- **EXE (verified by count):** of 537 string starts (runs of >= 2 SJIS chars, backed up to the previous NUL), 467 are
  the target of a u32 vaddr in a pointer array and 52 are built by `lui`/`addiu` (2 both); the 18 left are code bytes
  that happen to decode, not strings. Pointer arrays (u32, stride 4): file 0x46ffc-0x472e4 (187), 0x48188-0x483f4
  (156), 0x48860-0x48914 (44), 0x4fbd8-0x4fd50 (70), 0x50618-0x50634 (8), 0x79dac-0x79dc0 (6). They point at the
  place/item/name strings at 0x800-0x2100, packed back to back (each NUL-terminated and zero-padded to a 4-byte
  boundary: 0x888 レイテ, 0x890 ミルザプル, 0x89c ...), so the block can be rewritten whole with every pointer
  updated (verified by hexdump). `lui/addiu` strings: system and memory-card messages around 0x6d4a8-0x6de00 (`メモリーカードを抜き差し
  しないで下さい。`, `純白の預言者　ゲームデータ０６`...).
- **Overlays (verified by fit):** all four text overlays load at **0x8009b4b0** (file offset 0 = that address; first
  u32 = overlay id 6..10; the EXE itself holds id 5 at that address). With that base: op.bin 325 of 329 string starts hit a u32 pointer (tables), 2 lui; rfd2.bin
  136 lui + 30 table of 176; ed.bin 10 of 11 lui; pro.bin only 16 of 70 (the rest: guess, offsets added at run time
  or strings inside longer records; find in phase 4). Battle.bin has no text.
- Extraction should walk these pointers (and record every referencing site) rather than scan, so an English string
  can move to free space and every site be repointed.

## LKF entry lookup

The EXE names the archives (`FD2bn.LKF`, `FD2sn.LKF`, `GrpData.LKF`, `SSB_Data.LKF`, `VOICE.XA` at file 0x844) and
opens all four at 0x80023168 (function table call through 0x8007611c+0x20, handles at 0x8007efa8). No entry names
appear in the EXE or overlays, so files are addressed by index. Guess: entry offsets and sizes come from each
archive's header at run time (no table of them found; a u32 search for the first 60 entry offsets/sectors hit only
small common numbers). Verified in phase 3: the in-RAM directory is built from the header, and a build with grown
entries boots and reaches every scene tried (`disc.md` §Grow test).

## Name placeholder

`＄＄＄＄＄＄` (six full-width ＄, SJIS 81 90) in ssb text = the player's angel name (default ラビエル, entered at New
Game; 4 katakana max seen in the name-entry screen). Verified in ceev01_01.ssb context.
