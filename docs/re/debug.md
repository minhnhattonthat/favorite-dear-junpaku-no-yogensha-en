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

## Overlays (verified by RAM compare at the 0x8009B4B0 overlay base)

| file (FD2BN) | resident during |
|---|---|
| op.bin | (title? not caught resident at title: pro.bin was) |
| rfd2.bin | events and the world map (the main game) |
| Battle.bin | battles (not yet reached) |
| ed.bin | ending (guess, by name) |
| pro.bin | title menu and the name entry |

## Not reached yet (next session)

- **Battle** (name plates, EVX units): find what starts one. EVX are map-event setups; an event registers its
  sub-events with op `5c:25,i,..` (ceev04 registers seven, matching EVX ceev04_0..6). Ideas: give a hero a quest and
  pass time (待機), or find the mode switch that loads Battle.bin (watch reads of its record 0x800EBB28 while a
  battle starts; the heap allocator polls 0x800EBA70 every frame, so keep it out of the watch range).
- **Game over**, **credits / ENDING.STR staff roll** (not played by any `*ed01.ssb` nor `Raph_end.ssb`: they end in
  the .end narration, "Fin" and the clear-data save), **album** (GRPDATA_1454), **キャラ劇**: first look at the
  OPTION screen's **OMAKE** (extras) line (bottom of `title_option`'s proof), then the 天界へ menu (`map_heaven`).
- `save.py` (memory-card save editor) if a warp can't reach them.
