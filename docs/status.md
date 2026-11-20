# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress: event warp works; battle, game over, credits, album, キャラ劇 not reached yet.
- **Done (2026-11-20):**
  - Step 0 and phase 1 recon (see git history; `docs/re/README.md`).
  - Phase 2 (part): `tools/debug/warp.py` + `warp.lua` + `scenes.tsv` (how it works: `docs/re/debug.md`). Cold boot
    -> New Game -> any `.ssb` event in place of `prologue.ssb`, by patching the prologue's record in the game's
    by-name LKF directory in RAM (the CD read uses the BCD MSF at record +0x25). ~30 s per warp. Every run gets a
    fresh copy of `tools/debug/cards/fd1_clear.mcd` (first-game clear data, which New Game asks to import).
    Scenes reached with a proof shot (`work/qa/warp/<scene>/`, contact sheet of the menus: `work/qa/warp/proof_menus.png`):
    title, title_load, title_option, name_entry, prologue, map, map_menu, map_fairy, map_status, map_status_fairy,
    map_heaven, tutorial, heaven, exam, demo_menu, visit, maseki, year1, ev_cecia, ev_claire, ev_lo, ev_ro, ev_ei,
    ev_la, ev_fe (arrived; proof shot missing because the run was cut), end_cecia (arrived; ceed01 seen earlier in
    full: event, .end narration, Fin, clear-data save). `tests/test_debug.py` checks scenes.tsv.
  - Also learned: the game takes every LKF entry's disc position from the archive header at boot (good for phase 3);
    overlays at 0x8009B4B0: pro.bin = title + name entry, rfd2.bin = events + map, Battle.bin, ed.bin.
- **Next (phase 2, to finish):**
  - Re-run the rows not yet proven: `python -X utf8 tools/debug/warp.py ev_fe end_cecia end_cl end_lo end_ro end_ei end_la end_fe end_raphael tgs_end -j 2`
    (the last `--all -j 4` was stopped by the OS reaper for low memory; use -j 2).
  - Battle with name plates (`kind swap` on an EVX is ready once one battle is reachable), game over, credits
    (ENDING.STR staff roll: no `*ed01.ssb` nor `Raph_end.ssb` plays it), album, キャラ劇 (try OPTION -> OMAKE),
    memory-card save/load screens in game. Leads in `docs/re/debug.md` §Not reached yet.
  - Then `--all --state` to build `work/states/`, and phase 3 (identity build + LKF grow-one-entry boot test).
- **Open bugs:** none (no build).
- **Waiting on the user:** nothing. Non-blocking, for phase 8: the FMV captions and the Japanese staff roll in
  DEMO.STR/ENDING.STR (D3 says credits in English): re-encode the MDEC video or overlay subtitles; default plan is to
  re-encode ENDING.STR's credit section with English text. codex exec is out of credits until 2026-11-26 (no
  independent reviewer until then).
