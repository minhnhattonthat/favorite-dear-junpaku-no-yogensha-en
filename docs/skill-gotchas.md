# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.

- SKILL.md Step 0: in an Orca worker session the plugin skill was not registered (`Skill` said unknown) and its guard hook did not load; adding the `hooks` block with the stable marketplace path to `.claude/settings.json` made the guard live in the same session (canary then blocked).
- references/setup.md: context-mode trims any Bash output over ~5 KB to a search stub; keep recon commands' output short (`cut -c1-120`, `head`) or write to a file and summarise.
- references/platform-ps1.md: dumpsxiso extracts `.STR` files as 2336-byte Mode2 sectors (subheader + data, no sync/header); ffmpeg's `psxstr` demuxer rejects them ("Invalid parameters") until each sector gets the 12-byte sync + 4-byte header back (`tools/str2352.py`), then `ffmpeg -f psxstr` decodes the FMV fine.
- references/pipeline.md §Recon (PS1 overlays): find an overlay's load address by trying every base in steps of 4 and counting string starts hit by u32 pointers or lui/addiu pairs; the right base stood out at 327/329 here (0x8009b4b0, which the EXE marks with an overlay-id word).
- references/pipeline.md §Recon: a pure-Python byte-by-byte SJIS scanner over an 85 MB graphics archive runs for many minutes; scan text archives first and the graphics archive in the background.
