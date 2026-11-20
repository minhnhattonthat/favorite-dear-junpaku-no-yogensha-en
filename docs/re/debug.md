# Debug warp (phase 2)

`python -X utf8 tools/debug/warp.py SCENE|--event NAME.ssb|--all [-j 4] [--state] [--cue build/fd2_en.cue]`:
cold boot, no save, no savestate. Scene list: `tools/debug/scenes.tsv` (columns in `warp.py`'s docstring). Lua side:
`tools/debug/warp.lua`. One warp is ~25-40 s (8x emulation); `--all -j 4` ~10 min.

## How it works

- **File directory (verified: DMA watch, CdControl args, a working warp).** At boot the game builds, per LKF
  archive, a by-name directory of 0x38-byte records in RAM (SSB_DATA's around 0x80116xxx-0x8011Axxx, FD2BN's at
  0x800EBAB8): `name[0x20]`, `+0x20` archive pointer, `+0x24` u8 flag, `+0x25..+0x27` BCD MSF (minute, second,
  sector) of the file's first sector, `+0x2C` u32 size, `+0x30` u32 offset in the LKF, `+0x34` u32 (buffer, set
  while loaded). The loader `0x80038D74(mode, dst, rec, ..)` (wrapper `0x80039DF8`) copies the record to
  0x80087B54, rounds the size to sectors and hands **the MSF at +0x25** to CdControl (`0x8005D4BC`, cmd 0xA0 path at
  0x8003A278): patching only `+0x2C/+0x30` changes nothing, the MSF word is what moves the read.
  Consequence for phase 3: the disc position of every LKF entry is taken from the archive header at boot (the MSF is
  computed from the header offset), so entries can grow if the header is rewritten. Not yet a boot test.
- **Event warp.** New Game runs `prologue.ssb` right after the name entry (into the script buffer 0x801A4BB0).
  `warp.lua` copies the target's `+0x24`, `+0x2C` and `+0x30` words into the prologue's record every frame, so the
  game's own loader reads the target. Arrival = 16 bytes from the middle of the target file appear at the same
  offset in the script buffer (all scripts share their first 0x20 bytes, so the head is no signature).
- **Generic swap (`kind swap`).** Same patch for any file pair (HOST=TARGET), e.g. a battle's EVX, once a host
  event that loads HOST is known. Not used yet: no battle reached (below).
- **New Game route.** Title: 6000 frames of logos + DEMO.STR, Start twice. New Game: circle through the name and
  birthday defaults (ラビエル, 01/01), then up+circle: "これでいいですか？" defaults to いいえ, and the next question
  ("前作『フェイバリットディア』のデータを読み込みますか？") is answered yes, so the run needs a card with the first
  game's clear data: every run gets a fresh copy of `tools/debug/cards/fd1_clear.mcd` (a blank card makes the
  game loop on "insert the card"). The run then creates this game's file on that card.
- After a short event (e.g. `TheEnd.ssb`, a single op 0x74) the game goes to the world map; map scenes use that
  plus presses in `post`.

## Battle and ed.bin warps (`kind battle`, `kind ending`; verified by runs)

- **Main loop mode.** `0x8002AD70(mode, p1, p2, p3)` (wrapper `0x8002AD44(mode, p1)`, the one call each overlay
  makes) stores the mode at u16 `0x8007F5B0` (+2/+4/+6 the params) and sets bit 8 of `0x8007EFF0`; the main loop
  then loads overlay `mode` from the table at `0x8006FE38` (12-byte rows: index, ptr to the load address
  0x8009B4B0, entry): 0 op.bin, 1 rfd2.bin, 2 Battle.bin, 3 ed.bin, 4 pro.bin. Each overlay's first word is
  6 + its index.
- **Leaving the map.** rfd2.bin keeps a sub-mode request at `0x80080FF8`: +0x14 u8 pending, +0x15 u8 sub-mode
  (0-6), +0x18/+0x1C args (setter `0x8009ED44`). Sub-mode 6 leaves rfd2 for the overlay in u32 `0x8008103C`,
  which rfd2's init sets to **2** (battle); the ending paths set 3. The event/battle queue (`0x80029B7C`) hands
  out ids by thousands: 1xxx events, 2xxx, 3xxx battles (sub-mode 3, hero, id % 1000).
- **Battle setup** (`Battle.bin 0x800A7C70` -> `0x8009DA90`): hero index = u32 `0x80081010`; battle id = u32
  `0x80081014`, looked up by `0x8002B000` (id % 1000) in the exe's battle table `0x8006EB30` (14-byte rows:
  u16 n, u16 id 3000-3192, u8 flag 255/0, u8, u16 w6 402-463, u16 w8 401-643, u16 9999, u16 9999; 150 rows,
  `warp.battle_table()`). No match: a default encounter for the hero (row built at 0x800D2620). The battle state
  sits at 0x800D3250 (+0x8E hero, +0x94 battle event id); the hero's line file is `BTL_EVT<hero>.MSG`
  (SSB_DATA 710 + hero), plates `Name_B0<hero>.PIX` and `Name_<enemy>.PIX`.
- **The warp:** TheEnd.ssb -> map, 2400 frames, then write hero/id, `0x8008103C` = 2 (or 3) and sub-mode 6.
  Arrival = mode word and the overlay's first word.
- **ed.bin** (mode 3) branches on u8 `0x8007F17A`: 0x10 = game over (loads g_over*.tim, GRPDATA 1485),
  another high-nibble value = state 0x20, 0 = state 0x40. It is the only caller of the movie player
  `0x80098930(.., 4)` = ENDING.STR (movie table at 0x80099660, 0x20 per row: DEMO, DRA16, CI_LOGO, SOFIX,
  ENDING). op.bin plays the others; rfd2 also calls the player (`0x800D3CC8`).

## Overlays (verified by RAM compare at the 0x8009B4B0 overlay base)

| file (FD2BN) | resident during |
|---|---|
| op.bin | (title? not caught resident at title: pro.bin was) |
| rfd2.bin | events and the world map (the main game) |
| Battle.bin | battles |
| ed.bin | staff roll (ENDING.STR) and game over |
| pro.bin | title menu and the name entry |

## Saves (`tools/debug/save.py`, fixtures in `tools/debug/cards/`)

- `fd2_save.mcd`: written by the game (scene `heaven_saved`: New Game, Heaven -> データ -> セーブ, slot 1).
  `fd2_edited.mcd`: the same after `save.py set .. playtime=45296 month=7 day=15`; scene `load_edited` shows
  "time 012:34:56, Date 00,07,15" in the load list and loads into Heaven.
- Format (save.py docstring, `save_layout.tsv`): data at block +0x200, packed by `0x8002843C`, unpacked by
  `0x80028A84`, RAM image 0x80099708 (data 0x80099908); u16 checksum at data +0x9FE = sum of the u16 words before
  it. A bad sum lists the file as "No Data".
- **Run an event on a loaded file:** kind `title` with POST (the load) and an .ssb in `arg`: warp.lua then requests
  rfd2 sub-mode 1 with the SSB_DATA index at 0x80081010 (New Game itself requests 0x117 = prologue.ssb).

## System file = clear data (verified: card trace, a game-written file, OMAKE scenes)

- File names come from the exe table 0x80099578: `BISLPS-02754.0` = "純白の預言者　システム" (the system file),
  `.1`-`.C` = game data 01-12. Card manager modes (u32 at 0x8009A570+0x9C): 1 system load, 2 system save,
  3 game save, 4 game load, 5 clear save, 6 the first game's data. Modes other than 3/4 use file `.0`.
- **System struct** RAM 0x80084010 (getter 0x8002B3AC), 0x10C bytes = data +0x000..+0x10B of `.0`: u32 total play
  time in seconds; u8 x7 a clear count per index (+4 + u32 0x8008103C; else +0xB); 0x100 flag bytes (+0xC) ORed with
  RAM 0x8007F2EC at each clear (0x8002B3B8; the Cecia ending set +0xD5/+0xD6). Same u16 checksum at +0x9FE as a
  game file (0x80095E84); system load copies the struct back (0x80090E48).
- **The clear save reads `.0` before writing it** (BIOS open mode 0x8001; `tools/debug/cardtrace.lua` log): with
  no `.0` on the card it retries forever, which is why earlier ending runs never wrote. With one, it asks
  "ファイルがすでに存在します 上書きしますか？" (いいえ by default: left, wait ~40 frames, circle), then writes.
  Scene `end_cecia_clear` does all of it from a cold boot; `tools/debug/cards/fd2_cleared.mcd` is that write.
- `save.py system` builds `.0` (header and icon copied from the card's game file; only the struct and checksum
  differ from a game-written one, compared byte for byte). Cards: `fd2_clear.mcd` (every hero cleared, every flag
  0xFF: scenes `omake`, `omake_cg`, `album_2`-`album_8`), `fd2_sys0.mcd` (nothing cleared: the host for
  `end_cecia_clear`).
- **OMAKE** loads `.0` and opens the CG album straight away: 8 pages (R1/L1): the 7 heroes (profile panel drawn as
  graphics: name, title, birthday, height, weight, birthplace) and 天界 (angels and fairies); circle shows a CG.
  The album is op.bin's (the getter's callers: op.bin 0x8009FA58, 0x800A2858).
- **キャラ劇** (GRPDATA 558 `battle.tim`, a title card on a mock battle screen) is not behind OMAKE and no event
  loads it with the image op (`05 3c <u16 index>`); `fileslog.lua` on scenes `battle` and `tutorial` never loads
  it either. Probably unused (a mock-up); to settle it in phase 8, run `--all --lua tools/debug/fileslog.lua
  --debugger` and grep the logs for battle.tim.

## Probes (append to a warp run with `--lua F --debugger`)

- `tools/debug/cardtrace.lua`: BIOS card calls (open/read/write/firstfile ..) with file names and callers.
- `tools/debug/fileslog.lua`: every LKF file the loader 0x80038D74 reads ("FILE f<frame> <name>").
- `tools/debug/stateat.lua` (no debugger needed): a savestate at frame STATE_FRAME, to step on with play.py.
