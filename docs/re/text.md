# Text

**Encoding: Shift-JIS (cp932)** everywhere seen, with ASCII backslash escapes inside MSG text (verified: MSG, ssb, EVX,
.end and EXE strings decode to readable Japanese with `cp932`; `tools/scantext.py`). No custom table needed;
`tbl/jp.tbl` is not required for decoding. Whether the printer draws half-width ASCII (needed for English) is **not
known**: test in phase 5.

## Fonts

- `GRPDATA FD2Font.FPK` (54 KB; **verified** phase 5: decoded glyphs match the screen, `tools/fontinfo.py sheet`):
  resident in RAM at 0x801CE030 in every scene dumped. Header u16s: +0x02 `0a 0e` (glyph 10x14), +0x04 `0c 0e`
  (cell 12x14), +0x0c count 0x5ac (1452), +0x10 char list offset 0x220 (u16 SJIS codes, sorted), +0x12 glyph data
  0xd78: 35 bytes per glyph = 10x14 px at 2bpp, MSB first, values 0-3 (palette 35AD 6739 7FFF: 3 is the solid ink).
  The list's lead bytes are only 81-83 and 88-98.
- Font struct 0x80084160 (verified, RAM dump): +0 FPK, +4 char list, +8 glyphs, +0xc cell width 3 (VRAM halfwords),
  +0xe 14, +0x10 35, +0x14 LRU clock, +0x18 128 slot records of 8 bytes (+2 u16 SJIS code, +4 u32 last use).
- Draw path (verified by read watches and disassembly): `0x8002BE00 get_slot(code)` (LRU cache of 128 glyph slots,
  called by the dialogue line builder at 0x8002D754) -> `0x8002C474 lookup(code)` (binary search, -1 if absent) ->
  `0x8002C514 render(slot, index)` -> `0x8002C5EC decode(index)` into the 12x14 4bpp cell buffer 0x80084578 (it
  writes 10 of the 12 columns) -> LoadImage at VRAM x 0x380 + 3 * (slot % 16), y 14 * (slot / 16). Three more
  callers search the list inline and call the decoder: 0x8002BF2C (single glyph into slot < 8), 0x8002C080 and
  0x8002C2B0 (a string of up to 22 characters straight into a VRAM row).
- Dialogue layout `0x8002CC80` (verified: patched and seen in game): 3 boxes x 24 cells x 0x40-byte sprite records
  at 0x800845D8; x from 30, **advance 11 px, sprite width 10**, line pitch 15 (y 0xa9..); the name tag records
  (+0x1d0) start at x 25, same advance. The line builder caps a line at 24 cells (0x8002D72C) and expands ＄＄＄＄＄＄
  (12 bytes, compared at 0x8002EA44) into the angel name.
- ASCII bytes are **not** printable in ssb text: a row with ASCII letters made the prologue skip to the map (the
  script reader takes bytes < 0x80 as op argument counts). Hence the pair codes below.
- The only other `+ 11` steps in the EXE (0x80040CE8 / 0x80040F88) are in a scratchpad-based graphics routine, not
  text (checked by disassembly).

## English font (phase 5; verified in game, `work/qa/p5/asc`)

- **Pair glyphs** (`tools/font_en.py`, `asm/font.asm`, font `fonts/font6.txt`): two 5-px letters (+1 px gap) per
  12x14 cell, as a two-byte code with a lead byte the Japanese font never uses (84-87, 99-9F, E0-FC), so English
  costs one byte per letter, exactly what a Japanese character costs per cell. 84 characters: space, `!"%&'()*+,-./`,
  digits, `:;=?`, A-Z, a-z, `~ … ♪ ♥`. n = left * 84 + right; lead = LEADS[n // 188], trail = TRAILS[n % 188].
- Hooks: lookup returns 0x8000 | n for a pair code; the decoder draws the two letters for index >= 0x8000 (and blanks
  columns 10-11 for Japanese glyphs); the slot renderer no longer rejects index > count; the three inline searches
  call the lookup; the dialogue layout uses **advance 12 and sprite width 12** for text and name tag.
- Code and glyphs live in a block prepended to the EXE: t_addr 0x80020000 -> 0x8001E000 (+0x2000 bytes), which is
  zero in every RAM dump (`tools/ramzero.py`) and not touched at boot. `build.patch_exe` does it on every build
  except `--identity`.
- Text form: English in `en` is plain ASCII (+ … ♪ ♥); `insert.py` turns it into pair codes (`font_en.to_pairs`);
  an odd-length run gets a trailing space. Tags and Japanese characters (＄ name placeholder) pass through.

## Width gate (measured in game; `work/qa/p5/asc/prologue_hold/final.png`)

| Variant | Budget | How measured |
|---|---|---|
| Dialogue box (event scripts, prologue) | 44 letters per line (22 cells), 3 lines per page; line 3: 43 letters (the page-wait gem is at x 289-293) | a 48-letter line: letters 1-45 show, the 45th touches the frame (x 294-299), clip at x 300 |
| System message box (save/load, `SLPS.8008D5C8`) | same box as dialogue: 44 | `work/qa/p5/marker/load_save/final.png` |
| Map command buttons (rfd2 勇　者 / 妖　精 / ステータス / 天界へ) | ~12 letters (frame x 120-195, text centred) | `map_menu/final.png`, pixel scan; clip not yet seen (slots hold only 7-11 bytes in place) |
| Heaven menu / choice buttons (データ, 休　息, セーブ / ロード) | ~14 letters (frame ~92-96 px, centred) | `map_heaven`, `heaven_data`, `load_save` final.png; clip not yet seen |
| Heaven help bar (rfd2.8009D084) | to the screen edge, ~40 letters (bar from x 64) | `map_heaven/final.png`; whether the bar sizes to the text: unknown |

| MSG conversation (visit), event scripts (ev_cecia, end_cecia, tutorial), exam | 44 letters, 3 lines (same box) | `build.py --ruler --ruler-min 60` (every line >= 60 letters) -> `work/qa/p5/r60/sheet_all.png`: clip after letter 44-45 in every one |
| Battle message box (BTL_EVT) | 44 letters, 2 lines | `--qa BTL_EVT0.01E9=<60-letter ruler>{n}<ruler>` -> `work/qa/p5/tags/` (battle): clip after 44 |
| Name tag (event speaker, battle speaker) | **12 letters** (13th touches the frame, 14th clipped; a 20-letter event tag drew nothing at all) | `--qa ceev01_01.006E=ABCDEFGHIJKLMN`, `BTL_EVT0.01E0S=...`: `work/qa/p5/tags/sheet_all.png` |
| .end narration (full screen, 15 lines) | 42 letters per line (the Japanese maximum, 21 chars, draws in full from x 35 to 284) | `work/qa/p5/r60m/end_cecia/f014880.png`: a 60-letter line wraps back over the start of its own line, so > 42 corrupts |
| Status windows (angel / hero) | labels are English graphics in the original; only the player name is text | `work/qa/p5/marker/heaven_status_angel/final.png` |
| Glyph torture line (all 84 glyphs + double spaces) | renders correctly, no missing glyph | `build.py --stem torture --qa prologue.03E6=...` -> `work/qa/p5/torture/zoom.png` |

Limits for phase 7: BTL_EVT banks pass 64 KB (16-bit offsets) when every line grows to 60 letters, so battle text
growth is bounded per bank (largest JP bank now ~27 KB in T_Msg; check BTL_EVT sizes in the fit lint). EvName records
hold 22 bytes = 22 letters. The prologue quiz (pro.bin fixed 0x8C/0x30 records) and EXE/overlay strings are
same-length until relocation (phase 7).
Non-text rows excluded from marker builds: the debug printfs `FontEntryBuf() ～ ...`, `BraveChgStat() ～ ...`
(TTY only) and the memory-card titles. printf `%s` (4 rfd2 rows) stays raw ASCII (`font_en.FMT`).
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
| GRPDATA `Dummy00.DAT` | 1 | 35 | 840 | fixed 50-byte records (48 bytes of full-width-padded dialogue + CRLF, `久しぶりだな、ラビエル。　　...`); name says dummy, guess unused: extracted anyway (`script/misc/`); confirm with fileslog.lua in phase 8 |
| GRPDATA `FD2Font.FPK` | 1 | 7 | 320 | the font's character list (not text) |
| GRPDATA `*.tim/.blf/.rct`, FD2SN `*.seq/.vb/.blf` | ~1090 | - | - | false hits: pixel/sound bytes that decode as SJIS. Not text |

## MSG banks (SSB_DATA *.MSG; all 108 verified: `tools/msg.py` parses and rebuilds every bank byte for byte)

Five layouts (`msg.layout()` picks by name):

| layout | banks | format |
|---|---|---|
| plain | 57 (FryMsg, GenAnsw/GenNG, EMP_*, NASI_*, B_ItemRes, BVisit, T_Msg, HVN_Msg00, EQP_Item, SUP_Item, ...) | u16 offset table at 0 (count = first offset / 2); entry = u16 length + text, back to back |
| reply | BrvMsgQ0-6, BMsgQ* (42) | plain, but entries 3, 6, 9.. (the hero's reply in each topic / question / reply triple) start with 2 bytes before the length: (face?, s8 affection delta?), e.g. `00 00`, `04 00`, `00 f6` (-10), `00 05` |
| idtab | MssReq, MssAns0-6 | u32 count, count x (u16 offset, u16 id; ids 0..1056 not contiguous), entries = u16 length + text |
| names | EvName | u32 count, count x 24-byte records: u16 id + 22-byte NUL-padded text |
| battle | BTL_EVT0-6 | u16 count, count x (u16 id 3000.., u16 offset), u32 0xFFFFFFFF; record = 18 u16 slot offsets (0 = none, relative to the record) + messages: u16 length, speaker NUL text, u16 tail (0xFFFF, or a value like 0x09DD/0x0446: guess, a voice id). Slots are entry points into the message stream (a slot's run continues into the next slot's messages). Empty records are 36 zero bytes |

Offsets are 16-bit, so a bank must stay under 64 KB (largest now 27 KB, T_Msg00; `msg.build` asserts it). Escapes
(complete list, grep over every MSG/EVX): `\l` line break, `\k` wait for a key, `\c` clear the box (new page); EVX has
`\l` only. A 0x5C byte is also a Shift-JIS trail byte (表 95 5C, ソ 83 5C), so escapes are read only at character
boundaries (`tools/jtext.py`).

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
- **Extraction (phase 4, verified by `tests/test_text.py::test_coverage`): `tools/codetext.py`** walks u32 pointers
  and lui pairs, so every string has its referencing sites (the `notes` column: `ptrxN`, `luixN`). Every string in
  the EXE and the four overlays now has a reference. pro.bin's remaining 54: the prologue personality quiz, fixed
  tables reached as base + index * stride (base 0x800A03C4 is lui-built): 20 questions x 0x8C bytes from
  0x800A03C4, 40 answers x 0x30 from 0x800A0EB4 (answer A of question k at k, answer B at 20 + k: 円すい形 / 立方体).
  Quiz text uses **`￥` (81 8F) as its line break**. `codetext.NOT_TEXT` lists the 13 pointer/lui hits that are code
  (one kanji like 蝣 屁 鳥; the 鳥 hits are `jal` words `92 b9 00 0c`). Not text either: the two glyph-index tables at
  EXE 0x8007E203/0x8007E813 (waived in the test).
- Memory-card save titles (`純白の預言者　ゲームデータ０１　`, EXE 0x8008CD74..) are what the BIOS card manager shows: full-width
  SJIS only there. Keep or translate in full-width letters (phase 7 decision).

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

**Code that edits message bytes.** rfd2 0x800CEFD0(fairy) picks the hero whose relationship byte with the fairy is
largest (|value| > 12), fetches T_Msg01 message fairy+8 (good) or fairy+16 (bad), strcpys the hero's name from the
EXE table 0x8006F538 over the message's **last 14 bytes** (`＜勇者名＞ね。` in the JP) and strcats rfd2.8009D9E4
(`ね。`). So those 16 English messages must end in `＜勇者名＞` + exactly 4 bytes of filler, and the appended tail
is a blank (`tests/test_merge.py::test_compatibility_tail`). Other strings built from fragments: `docs/status.md`
(rfd2 fragments, phase 7 notes). `python -X utf8 tools/refs.py FILE VA` disassembles every reference to a string.

**Where MSG banks load and how entries are fetched (phase 8, textcover; verified by read watches on the original).**
Not every bank goes to the script heap: BTL_EVT<hero>.MSG loads to 0x801A4BB0, but FryMsg<n>.MSG loads to
0x801203E0 (the shared image/sound buffer, reused by the next .tim/.VB), so `tools/debug/textcover.lua` watches each
text file's [dst, dst + record size) from its first load. There is **no common get-message function**: each caller
inlines the fetch. Fairy report: rfd2 0x800BF070 (s4 = entry index, bank pointer u32 at [s2 + 0x1EB0]) reads the
u16 offset, copies the entry to bank + 0x4000 through 0x800BF120 (placeholder substitution) and queues it
(0x8002E6C0, 0x8002DBEC, 0x8002CAA0); the function returns at once and the box draws over later frames, so a
Lua jump-back loop over the index does not show more entries (tried: 0x800BF100 -> 0x800BF070 every 3 frames,
one report shown). Battle lines: EXE code called from 0x80040A44 walks the BTL_EVT record table (reads at 0x80040AA8 /
0x80040ADC / 0x80040B10). The MSG box start is EXE **0x8002E6C0(text, len)**: stores text at
[0x800857D8] + 0x4AC, len at +0x4B0, resets the 3 x 24-cell box (y from 0xA9, pitch 15). Callers: rfd2 0x800B2368
.. 0x800D440C (18 sites), Battle.bin 0x8009E340/E484/E5E8/E790; none in op/ed/pro. ssb events do **not** use it
(0 calls in men1_Ro01, `work/qa/p8/msgstart`), so an event run cannot carry forced MSG entries. A force hook there
(swap a0/a1 for the next unshown entry, written into scratch RAM) needs scenes that start many MSG boxes (visit
conversations, heaven chats, fairy reports) or a way to re-enter a caller after its box closes.

## Extraction (phase 4; `tools/extract.py`, tests in `tests/test_text.py`)

`script/` TSVs, columns `id jp en notes`; ids = `<file stem>.<hex offset of the text in the original file>` (ssb rows:
offset of the row's first token; EXE/overlays: `SLPS.<vaddr>`, `<overlay>.<vaddr>`). One Source per file
(`extract.sources()`): its rows and a `build({id: text})` that the insert step (`tools/insert.py`, called by
`build.py`) uses with the `en` texts.

| dir | from | rows | row = |
|---|---|---|---|
| `msg/` (108) | SSB_DATA *.MSG | 15130 | one entry (BTL_EVT: speaker `....S` and text rows per message) |
| `ssb/` (287) | SSB_DATA *.ssb | 9821 | a run of text tokens with ops 02/05/06 as {n}/{wait}/{clear}, cut at jump targets; speaker names (op 0x19) are their own rows (notes `speaker`) |
| `evx/` (269) | SSB_DATA *.EVX | 5855 | one item: title (dev label), unit name (32-byte field), speaker, text, choice |
| `end/` (21) | SSB_DATA *.end | 198 | a paragraph; CRLF inside as {n} |
| `misc/Dummy00.tsv` | GRPDATA Dummy00.DAT | 35 | a record (re-padded to 48 bytes with full-width spaces) |
| `ovl/` (4), `exe.tsv` | FD2BN op/rfd2/ed/pro.bin, SLPS_027.54 | 1253 | one NUL-terminated string; notes give the reference kinds; replaced in place only until relocation (phase 7) |

Text form (`tools/jtext.py`): SJIS characters as themselves, `{n}` `{wait}` `{clear}`, `{XX}` for any other byte
(unmapped or NEC/IBM duplicate codes too), so `encode(decode(b)) == b` for any bytes. Tests: every row and every file
round-trips; every SJIS run in a source file starts inside a row (`test_coverage`, after skipping op arguments and
header tables; 3+ characters in the EXE/overlays, 1+ elsewhere); `script/` matches the disc; ssb and EVX files keep
their jumps / record sizes when every row grows.
