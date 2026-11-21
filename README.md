# Favorite Dear: Junpaku no Yogensha English translation

Unofficial English fan translation of **Favorite Dear: Junpaku no Yogensha** ("The Pure White Prophet"; PlayStation,
NEC Interchannel, 2000, SLPS-02754): the source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue and story events, battle text, fairy reports, hero chats, missions, endings | Translated |
| Menus, items, status screens, system messages | Translated |
| Graphics with text (menus, battle plates, album, status tags) | Translated; the title logo keeps its 純白の預言者 lettering under the English "FAVORITE DEAR" |
| Opening movie captions, staff roll | Translated (re-encoded video) |
| Name entry | Works with Latin letters (the game's own letter page, one arrow press from the kana pages it opens on) |
| Voice acting, songs | Left in Japanese (audio) |
| Memory-card save titles in the console's card manager | Left in Japanese (the BIOS draws full-width characters only) |

Known issues: names with an odd number of letters are followed by a space ("Ray , welcome"; also hero and
town names in fairy reports), some letter pairs show a small gap on the name-entry field and the angel status panel,
and some fixed-size labels use shorter English forms; see [Issues](../../issues).

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched disc image

Needs Python 3.12+, your own dump of the Japanese disc, and the disc tools listed in `AGENTS.md` (mkpsxiso, armips,
xdelta).

```sh
git clone https://github.com/minhnhattonthat/favorite-dear-junpaku-no-yogensha-en
cd favorite-dear-junpaku-no-yogensha-en
# copy your dump (Redump "Favorite Dear - Junpaku no Yogensha (Japan)") to:
#   rom/Favorite Dear - Junpaku no Yogensha (Japan).bin  (567401184 bytes, CRC32 B433678A,
#     MD5 8be97d515553773081ece79ece7c8c42, SHA-1 b948c46436cb2290c5a87903336e0d404705c73d)
#   rom/Favorite Dear - Junpaku no Yogensha (Japan).cue  (the build refuses any other dump, see rom.sha1)
python -X utf8 tools/build.py                          # -> build/fd2_en.bin + .cue
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is NEC Interchannel's and is included only
so the translation can be checked against it. Favorite Dear: Junpaku no Yogensha is (c) NEC Interchannel; this project
is not affiliated with them. Do not share patched disc images.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
