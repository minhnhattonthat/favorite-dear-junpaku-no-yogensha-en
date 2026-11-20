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
| `text.md` | Shift-JIS encoding, MSG banks, .end files, EXE strings, name placeholder, text volume | encoding + MSG verified |
| `events.md` | ssb event-script byte stream (opcodes, inline text), EVX battle setups | tokenizer verified on 344/346 files; linearity a guess |
| `graphics.md` | graphics-text survey: TIM dump, sheets, tour findings | sweep rendered, not reviewed |
| `space.md` | growth and buffer limits | candidates only |

Prior work: the first game's project `../favorite-dear-en` (different engine and disc layout; its glossary and style
carry over). No earlier English patch for this game checked yet (web search still to do).

Helpers: `tools/lkf.py` (LKF list/extract/build), `tools/scantext.py` (SJIS run scan), `tools/ssb.py` (ssb
tokenizer), `tools/tim.py` (TIM -> PNG, dump every TIM in the LKFs), `tools/gfxsheets.py` (labelled sheets).
