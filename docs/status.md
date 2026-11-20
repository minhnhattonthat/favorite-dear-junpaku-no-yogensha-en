# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4. Extract (phase 3 done: identity build byte-identical as a test, grown-entry build boots).
- **Done (2026-11-20):**
  - Step 0, phase 1 recon, phase 2 debug warp (see git history; `docs/re/README.md`, `docs/re/debug.md`): all 66
    scenes in `tools/debug/scenes.tsv` reached from cold boots with proof shots; `save.py` (game + system file);
    40 states in `work/states/`.
  - **Phase 3 (this session):** `tools/build.py` (check dump -> unpack with dumpsxiso if needed -> rebuild changed
    LKFs with `lkf.build` -> build/<stem>.xml with per-file `source` paths -> mkpsxiso; ~3 s).
    `build.py --identity` re-lays all four LKFs and gives the original SHA-1 (`tests/test_build.py`, in the
    default check). `build.py --grow-test` grows each LKF's first entry by 0x1800: warps title, prologue, tutorial,
    battle_h3, credits, map_menu on it are all `ok` (`work/qa/grow/`), so LKF entries and the files after them can
    move (`docs/re/disc.md` §Grow test). Default build = original bytes for now; smoke ok.
    `warp.py --out-dir D` keeps test-build runs out of `work/qa/warp/`.
- **Next (phase 4, extract):** extract every text source to `script/` TSV with a roundtrip test (re-encoding gives
  the original bytes; ranges fully covered): SSB event scripts (346), MSG banks (108; `BrvMsgQ*` sub-structure still
  undecoded, xfail in `tests/test_formats.py`), `.end` narrations (21), EVX battle setups (269, check for text), EXE
  string block 0x800-0x2100 (`docs/re/text.md`), overlay strings (op/rfd2/pro/ed). Then hand the build step its
  `lkf_changes`/`files` (build.py docstring).
  - Warp batches: run **-j 1** on this machine (-j 2 ran low on memory, -j 4 was killed by the OS).
  - Script buffer size at 0x801A4BB0 unknown: find it before scripts grow (phase 5; `docs/re/space.md`).
  - キャラ劇 (GRPDATA 558 battle.tim) is not in OMAKE and no script or traced scene loads it: probably unused.
    Phase 8: `--all --lua tools/debug/fileslog.lua --debugger`, grep for battle.tim; if never loaded, drop G9.
  - Don't edit warp.lua while a batch runs: runs that start mid-edit fail.
- **Open bugs:** none.
- **Waiting on the user:** nothing. Non-blocking, for phase 8: the FMV captions and the Japanese staff roll in
  DEMO.STR/ENDING.STR (D3 says credits in English): re-encode the MDEC video or overlay subtitles; default plan is to
  re-encode ENDING.STR's credit section with English text. codex exec is out of credits until 2026-11-26 (no
  independent reviewer until then).
