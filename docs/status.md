# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build (phase 4 done: every text source extracted to `script/`, roundtrip and
  coverage tests green).
- **Done (2026-11-20):**
  - Step 0, phases 1-3 (see git history; `docs/re/README.md`, `docs/re/debug.md`, `docs/re/disc.md`): 66 warp scenes
    from cold boots, `save.py`, 40 states in `work/states/`; identity build byte-identical as a test; grown LKF
    entries boot.
  - **Phase 4 (this session):** `tools/extract.py` writes 692 TSVs / 32292 rows (`docs/re/text.md` §Extraction):
    MSG (5 layouts decoded, incl. BrvMsgQ reply prefixes and BTL_EVT slot records), ssb (jump ops found: scripts
    are NOT linear; `ssb.build` re-points jumps), EVX (dialogue records, unit names, choices), .end paragraphs,
    Dummy00.DAT, EXE + overlay strings with their pointer/lui sites (pro.bin quiz = fixed tables). `tests/test_text.py`:
    rows and files round-trip, coverage (every SJIS run inside a row), script/ in sync, ssb/EVX grow tests.
    `tools/insert.py` turns `en` columns into the build's changes; default build = original sha1 (0 rows translated).
- **Next (phase 5, marker build):** font/VWF decision (FD2Font.FPK char list, `text.md` §Fonts; does the printer draw
  ASCII?), then a marker build: every row's `en` = `[id]`-style marker (write it to a scratch language column or
  pass texts to `insert.changes` directly, don't fill `en`), boot and warp through scenes, find non-text "strings",
  and measure every box variant's width in game (width gate). Open items found in phase 4:
  - ssb name rows: op 0x19 counts characters; `ssb.build` asserts an even byte count. Decide how ASCII names count.
  - EVX growth only re-parse-tested; boot-test a grown EVX battle (warp `battle_*`).
  - EXE/overlay strings are replaced in place only (`codetext.replace_in_place`); relocation for longer English is
    phase 7 (every string's sites are known: `codetext.strings()` refs).
  - Prologue quiz text uses `￥` as its line break; EvName fields hold 22 bytes; EVX unit names 32 bytes.
  - Memory-card save titles in the EXE (`純白の預言者　ゲームデータ０１`) show in the BIOS card manager (full-width only).
  - Warp batches: run **-j 1** on this machine (-j 2 ran low on memory, -j 4 was killed by the OS).
  - Script buffer size at 0x801A4BB0 unknown: find it before scripts grow (`docs/re/space.md`).
  - キャラ劇 (GRPDATA 558 battle.tim) is not in OMAKE and no script or traced scene loads it: probably unused.
    Phase 8: `--all --lua tools/debug/fileslog.lua --debugger`, grep for battle.tim (and Dummy00.DAT); if never
    loaded, drop G9.
  - Don't edit warp.lua while a batch runs: runs that start mid-edit fail.
- **Open bugs:** none.
- **Waiting on the user:** nothing. Non-blocking, for phase 8: the FMV captions and the Japanese staff roll in
  DEMO.STR/ENDING.STR (D3 says credits in English): re-encode the MDEC video or overlay subtitles; default plan is to
  re-encode ENDING.STR's credit section with English text. codex exec is out of credits until 2026-11-26 (no
  independent reviewer until then).
