# Favorite Dear: Junpaku no Yogensha (PS1, NEC Interchannel, 2000) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, printed by `python tools/skill.py`). Read it before ROM, text or QA work.
Reference project: the first game, `../favorite-dear-en` (same series, different engine/disc layout; reuse its glossary, style and tool ideas).

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py`        -> build/fd2_en.bin/.cue (checks the dump against `rom.sha1` first; not written yet)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this; `git config core.hooksPath tools/hooks` once per clone)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py C:/abs/path/build/fd2_en.cue --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py <scene>` (not written yet; scenes: `tools/debug/scenes.tsv`; never ask the user to play to a scene)
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original disc: `rom/Favorite Dear - Junpaku no Yogensha (Japan).bin/.cue` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Unpacked: `work/disc/tree/` + `work/disc/layout.xml` (dumpsxiso).
- Emulator: this repo's own PCSX-Redux in `tools/pcsx/` (nightly 32119.20261119.34 x64, `$SKILL/scripts/fetch_emu.py pcsx`; gitignored); BIOS `tools/bios/scph5500.bin` (`fetch_emu.py psx-bios`). Savestates: `work/states/`.
- Disc tools (gitignored, from GitHub releases): `tools/mkpsxiso/` (Lameguy64/mkpsxiso v2.30 win64), `tools/armips/` (Kingcom/armips v0.11.0), `tools/xdelta/` (jmacd/xdelta-gpl v3.1.0).
- Text: `script/` (TSV). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the agent types (translator, reviewer, visual-qa, playtester, graphics) shipped by the plugin as `translate-retro-game:<type>` (Claude Code), `.codex/agents/` (Codex) or `.opencode/agents/` (opencode), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- From Git Bash give Python Windows paths (`C:/...`); emu.py needs an absolute path to the .cue.
- Boot to title takes ~6000 frames: Start does not skip the logos or the opening movie (DEMO.STR).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
