# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool: not started (phase 1 recon done 2026-11-20). No build yet.
- **Done (2026-11-20):**
  - Step 0: rom.sha1 pinned, `tools/check.py` + pre-commit hook (a failing test blocks a commit: verified), guard hook
    in `.claude/settings.json` (canary blocked: verified), `tools/skill.py`, tools copied from `../favorite-dear-en`
    (PCSX-Redux, BIOS, mkpsxiso, armips, xdelta; gitignored), boot route `tools/routes/boot.txt` (title menu at ~f6600;
    the original boots, smoke ok, scripted input works). Keyboard input: same PCSX-Redux build and settings as the
    sibling project, not separately tested.
  - Phase 1 recon (`docs/re/`, index in `docs/re/README.md`): disc = EXE + 4 `+LKF` archives opened by file name,
    entries by index; text is plain Shift-JIS (MSG banks, inline ssb, EVX, .end, EXE/overlay strings); text-bearing
    files listed with volumes (`text.md`); EXE strings all reached by u32 pointer arrays (467) or lui/addiu (52);
    overlays load at 0x8009b4b0 (op.bin tables, rfd2/ed lui; pro.bin only 16/70 found); font FD2Font.FPK carries an
    SJIS character list; graphics survey complete for the static sweep: rows G1-G15 in `graphics.md` (title logo,
    status tags, skill banners, 88 name plates `Name_NNN.PIX`, album profile atlas, キャラ劇 card, glyph strips,
    DEMO/ENDING FMV captions and the Japanese staff roll). No earlier patch or tools exist (web search).
- **Next (phase 2, debug tool):** `tools/debug/warp.py <scene>` + `tools/debug/scenes.tsv`: reach any ssb event,
  menu, battle, ending and the credits from a cold boot, each with a proof shot, no user save. Start points:
  - find the ssb loader/interpreter (event index = SSB_DATA entry index; `events.md`) and the story-flag/day
    variables in RAM (`$SKILL/scripts/ramsearch.py`, Lua `watch.lua`), then warp by writing the next-event id or by
    patching the loader in RAM via Lua;
  - New Game needs the name entry: Start->END, and the "これでいいですか？" confirm defaults to No;
  - scene list must include one entry per character route, each ending (`*.end`, ENDING.STR), the album
    (GRPDATA_1454), キャラ劇, a battle with name plates, game over, the option and memory-card screens.
  - `save.py` (memory-card save editor) only if the warp can't cover something.
  Phase 3 then: identity build (mkpsxiso from `work/disc/layout.xml`), plus the LKF grow-one-entry boot test
  (`space.md`).
- **Open bugs:** none (no build).
- **Waiting on the user:** nothing. Non-blocking, for phase 8: the FMV captions and the Japanese staff roll in
  DEMO.STR/ENDING.STR (D3 says credits in English): re-encode the MDEC video or overlay subtitles; default plan is to
  re-encode ENDING.STR's credit section with English text. codex exec is out of credits until 2026-11-26 (no
  independent reviewer until then).
