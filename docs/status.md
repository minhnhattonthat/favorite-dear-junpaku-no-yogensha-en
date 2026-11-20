# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool: every scene reached (OMAKE and the clear save now too); left: re-record 24 scenes in one batch.
- **Done (2026-11-20):**
  - Step 0 and phase 1 recon (see git history; `docs/re/README.md`).
  - Phase 2: `tools/debug/warp.py` + `warp.lua` + `scenes.tsv` (how: `docs/re/debug.md`). Cold boot -> New Game
    -> any `.ssb` event in place of `prologue.ssb`; ~30-60 s per warp. Proof shots in `work/qa/warp/<scene>/`.
    Reached with proof: title, title_load, title_option, title_omake, name_entry, prologue, map + map menus,
    tutorial, heaven, exam, demo_menu, visit, maseki, year1, every route's first event, every ending (end_*),
    tgs_end; battles (battle, battle_h1..h6, battle_3152); staff roll (`credits`); game over (`game_over`,
    `game_over2`); Heaven menus; `heaven_saved`; `load_save`, `load_edited`.
  - **Clear data / OMAKE (this session):** the clear data is the system file `BISLPS-02754.0` (0x10C-byte struct:
    play time, clear counts, 0x100 unlock flags; `docs/re/debug.md` §System file). The game's clear save only
    updates an existing `.0` (it retried forever without one). `save.py system` builds `.0`; a game-written one
    matches it byte for byte apart from the struct (`tests/test_save.py`). New scenes: `omake` (album page 1),
    `omake_cg` (a CG full screen), `album_2`..`album_8` (the 7 heroes + 天界), all from cold boots;
    `end_cecia_clear` now runs the Cecia ending on a loaded file and writes the clear data (card kept as the run's
    memcard1.mcd; fixture `cards/fd2_cleared.mcd`). OMAKE holds only the album.
  - Probes for warp runs: `tools/debug/cardtrace.lua` (BIOS card calls), `fileslog.lua` (every LKF file loaded),
    `stateat.lua` (a state at frame N for play.py).
- **Next (phase 2, to finish):**
  - `results.tsv` has no `ok` row for 24 scenes proven before it existed, and `prologue` lost its proof shot to a
    stopped batch: title title_load title_option name_entry prologue map map_menu map_fairy map_status
    map_status_fairy map_heaven heaven exam demo_menu visit maseki year1 ev_cecia ev_claire ev_lo ev_ro ev_ei ev_la
    game_over2. Re-run them, **-j 1**, with `--state`: `python -X utf8 tools/debug/warp.py <those> -j 1 --state`.
    The session's `--all -j 2 --state` was stopped by Claude Code for low system memory (states saved for the
    first 16 scenes, through name_entry); a -j 4 run was killed by the OS earlier. Then the remaining states
    (`--all` minus those done) and phase 3 (identity build + LKF grow-one-entry boot test).
  - キャラ劇 (GRPDATA 558 battle.tim) is not in OMAKE and no script or traced scene loads it: probably unused.
    Phase 8: `--all --lua tools/debug/fileslog.lua --debugger`, grep for battle.tim; if never loaded, drop G9.
  - Don't edit warp.lua while a batch runs: runs that start mid-edit fail.
- **Open bugs:** none (no build).
- **Waiting on the user:** nothing. Non-blocking, for phase 8: the FMV captions and the Japanese staff roll in
  DEMO.STR/ENDING.STR (D3 says credits in English): re-encode the MDEC video or overlay subtitles; default plan is to
  re-encode ENDING.STR's credit section with English text. codex exec is out of credits until 2026-11-26 (no
  independent reviewer until then).
