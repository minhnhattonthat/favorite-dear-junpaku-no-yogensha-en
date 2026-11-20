# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| `disc.md` | disc files, LKF archive format | LKF verified; identity rebuild not tested |
| `text.md` | Shift-JIS encoding, fonts, text-bearing files (ranges), MSG banks, .end files, EXE/overlay string pointer forms, overlay base, LKF entry lookup, name placeholder | encoding, MSG, pointer forms verified; BrvMsg layout and pro.bin pointers open |
| `events.md` | ssb event-script byte stream (opcodes, inline text), EVX battle setups | tokenizer verified on 344/346 files; linearity a guess |
| `graphics.md` | graphics-text survey: TIM sweep (reviewed), name plates, BLF, FMV, rows G1-G15 | static sweep complete; tour rows added in phase 5 |
| `debug.md` | debug warp: LKF by-name directory in RAM (MSF read), event swap, New Game route, overlays | event warp verified (scenes.tsv); battle/credits/game over open |
| `space.md` | growth and buffer limits | candidates; overlay base verified |

Prior work: the first game's project `../favorite-dear-en` (different engine and disc layout; its glossary and style
carry over). No earlier patch or tools for this game found (web search 2026-11-20: no English or other fan patch,
no community tools).

Helpers: `tools/lkf.py` (LKF list/extract/build), `tools/scantext.py` (SJIS run scan), `tools/ssb.py` (ssb
tokenizer), `tools/tim.py` (TIM -> PNG, dump every TIM in the LKFs), `tools/gfxsheets.py` (labelled sheets),
`tools/retools.py` (MIPS disassembly, lui/addiu xrefs), `tools/pix.py` (name plates), `tools/str2352.py` (FMV sectors
for ffmpeg).
