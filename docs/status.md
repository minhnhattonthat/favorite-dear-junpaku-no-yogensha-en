# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress: everything but OMAKE (clear data) reached; then `--all --state`.
- **Done (2026-11-20):**
  - Step 0 and phase 1 recon (see git history; `docs/re/README.md`).
  - Phase 2: `tools/debug/warp.py` + `warp.lua` + `scenes.tsv` (how: `docs/re/debug.md`). Cold boot -> New Game
    -> any `.ssb` event in place of `prologue.ssb`; ~30-60 s per warp. Proof shots in `work/qa/warp/<scene>/`.
    Reached with proof: title, title_load, title_option, title_omake (the clear-data prompt), name_entry,
    prologue, map + map menus, tutorial, heaven, exam, demo_menu, visit, maseki, year1, every route's first event,
    every ending (end_*), tgs_end; **battles** (`kind battle`, HERO:ID: battle, battle_h1..h6, battle_3152: name
    plates, battle lines, enemy turns); **staff roll** (`credits`, ed.bin, ENDING.STR); **game over**
    (`game_over`, `game_over2`); Heaven menus (heaven_data/save/load/status/status_angel/rest/move);
    `heaven_saved` (writes a real save); `load_save`, `load_edited`; `end_cecia_clear` (ending on a loaded file).
  - `tools/debug/save.py` + `save_layout.tsv`: lists/edits FD2 saves on a card, fixes the u16 checksum; the
    edited fixture `cards/fd2_edited.mcd` shows its edited time/date in game and loads (scene load_edited).
    Tests: `tests/test_debug.py`, `tests/test_save.py`.
- **Next (phase 2, to finish):**
  - OMAKE needs this game's clear data on the card; the clear-data save does not land yet (`docs/re/debug.md`
    §Not reached yet has what was tried and the next two leads). Album and キャラ劇 are probably inside OMAKE.
  - Then `python -X utf8 tools/debug/warp.py --all -j 2 --state` (not -j 4: the OS killed a -j 4 run for low
    memory) to build `work/states/`, and phase 3 (identity build + LKF grow-one-entry boot test).
  - Don't edit warp.lua while a batch runs: runs that start mid-edit fail (seen this session).
- **Open bugs:** none (no build).
- **Waiting on the user:** nothing. Non-blocking, for phase 8: the FMV captions and the Japanese staff roll in
  DEMO.STR/ENDING.STR (D3 says credits in English): re-encode the MDEC video or overlay subtitles; default plan is to
  re-encode ENDING.STR's credit section with English text. codex exec is out of credits until 2026-11-26 (no
  independent reviewer until then).
