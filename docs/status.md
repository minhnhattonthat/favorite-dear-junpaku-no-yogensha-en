# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6. Translate (phase 5 done 2026-11-21: marker build toured, width gate measured, torture line ok).
- **Phase 5 result:** width gate complete in `docs/re/text.md` §Width gate: dialogue / MSG / exam / battle boxes 44
  letters per line (3 lines; battle 2; last line 43 for the page gem), name tags 12 letters, .end narration 42,
  menu buttons ~12-14, help bar ~40. Glyph torture line renders all 84 glyphs (`work/qa/p5/torture/zoom.png`).
  Marker build reached all 66 scenes (game_over/game_over2 added). New `build.py --ruler-min N` stretches every
  line to N letters for clip tests. Non-text rows excluded: debug printfs, memory-card titles, printf `%s`.
- **Phase 6 progress (2026-11-21):** `tools/batches.py` split the script into 92 batches (b001-b092, ~3500 JP chars
  each; one row per distinct JP, merge copies it to every duplicate; order ssb, msg, evx, end, misc, ovl, exe).
  Done: **b001-b008** (alkaya fairy intros for Rosa, Florinda, Shelly, Lily, Lynx, Aquila, Cetus, Lepus; Cecia's
  ceed01/ceev01-24; Clive's cled01/clev01-20_01, ends at Raphael's "from whom were humans born" talk).
  `batches.py todo` lists the rest. Glossary gained (2026-11-21): Holy Mother, Demon Stone, Heavenly Dragon, Crimson
  Moon King, archangel, Lake Dreihaup (b001 spelling kept), Mount Delphinia, Clive Saingrent (Ravenruft is the vampire
  king, his father), Irwin, Viper, Zig, Titan. Grown ssb boot test: `warp.py --event clev11.ssb --event ceev14.ssb
  --cue <abs>/build/fd2_en.cue` both OK, English renders and wraps (`work/qa/p6b/`); warp.py's default cue is the
  ORIGINAL disc, so always pass `--cue` for the build. Workflow per batch (no subagents under Orca): Read
  `trans/batches/bNNN.tsv` in ~25-50-line parts, write `trans/parts/bNNN_K.tsv` (id<TAB>en), join with
  `(echo -e "id\ten"; cat trans/parts/bNNN_*.tsv) > trans/en/bNNN.tsv`, `batches.py check bNNN`, then `merge` and
  `build.py`. ~4 batches fit one worker context; brief in `docs/translator-brief.md`, terms in `glossary.md` (seeded
  this session: heroes Fein, Irene, Rocus, Clive, Leyla, Rudiere, Cecia; places Grosain, Ecclesia, Six Kingdoms
  Alliance, Legrance, Reyforia Forest...; extend it as names appear).
  Open for phase 7: merge's wrap adds `{wait}{clear}` pages when a page runs over 3 lines, which can leave a
  one-word orphan page (alkaya.0238 "tundra."): rebalance in the fit pass; script buffer size still unknown (two
  grown event scripts boot fine, the rest are untested). No `docs/synopsis.md` / style reference yet: write them once the story
  scripts are read (voices so far in the brief). Review pass not done (codex out of credits until 2026-11-26).
- **Next (phase 6):** continue at b009 (`batches.py todo`; clev20_01 continues there). Budgets above; BTL_EVT banks have a 64 KB cap
  (keep battle lines near the JP length), EvName 22 bytes, EXE/overlay strings same-length until phase 7 relocation.
  Name entry: kana grid (G6) has A-Z a-z on the keyboard font; decide the Latin page in phase 8.
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
- **Open items from phase 4 (still open):**
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
