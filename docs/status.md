# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon: in progress (Step 0 setup done 2026-11-20). No build yet.
- **Done (2026-11-20):**
  - Step 0: rom.sha1 pinned, `tools/check.py` + pre-commit hook (a failing test blocks a commit: verified), guard hook
    in `.claude/settings.json` (canary blocked: verified), `tools/skill.py`, tools copied from `../favorite-dear-en`
    (PCSX-Redux, BIOS, mkpsxiso, armips, xdelta; gitignored), boot route `tools/routes/boot.txt` (title menu at ~f6600;
    the original boots, smoke ok, scripted input works). Keyboard input: same PCSX-Redux build and settings as the
    sibling project, not separately tested.
  - Recon so far (`docs/re/`): disc = EXE + 4 `+LKF` archives (format verified, `tools/lkf.py`, byte-exact rebuild
    test); text is plain Shift-JIS (MSG banks, inline in ssb event scripts, EVX unit names, .end narrations, EXE and
    overlay strings); ssb opcode model (`tools/ssb.py`) parses 344/346 files; graphics: 1252 TIMs rendered to 32
    labelled sheets (`work/gfx/sheets/`, regenerate: `tools/tim.py dump work/gfx` then `tools/gfxsheets.py work/gfx
    work/gfx/sheets --per 40 --width 1600`).
- **Next (phase 1, to meet done-when):**
  1. Graphics survey: review the 32 sheets in `work/gfx/sheets/` (a few per read; ~3k tokens each) and list every
     Japanese image in `docs/re/graphics.md` rows; render `Name_NNN.PIX` (88 files, 384 B) and `6x624_4.BLF`; note
     DEMO.STR/ENDING.STR burned-in captions.
  2. Pointers: EXE/overlay string pointer form (lui/addiu or tables; copy `../favorite-dear-en/tools/retools.py`),
     whether the EXE holds its own LKF offsets (search for e.g. SSB_DATA entry offsets), file load buffers (space.md).
  3. Text ranges: list every text-bearing file (`tools/scantext.py summary work/lkf work/disc/tree/SLPS_027.54`; the
     full run is slow on GRPDATA, run it in the background) into `docs/re/text.md`; MSG escapes list.
  4. Web search for earlier patches/tools for this game (none checked yet).
  Then phase 2 (debug tool: warp to any ssb event from cold boot; the New Game name entry needs Start->END, and the
  "これでいいですか？" confirm defaults to No).
- **Open bugs:** none (no build).
- **Waiting on the user:** nothing. codex exec is out of credits until 2026-11-26 (no independent reviewer until then).
