# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.

- SKILL.md Step 0: in an Orca worker session the plugin skill was not registered (`Skill` said unknown) and its guard hook did not load; adding the `hooks` block with the stable marketplace path to `.claude/settings.json` made the guard live in the same session (canary then blocked).
- references/setup.md: context-mode trims any Bash output over ~5 KB to a search stub; keep recon commands' output short (`cut -c1-120`, `head`) or write to a file and summarise.
- references/pipeline.md §Recon: a pure-Python byte-by-byte SJIS scanner over an 85 MB graphics archive runs for many minutes; scan text archives first and the graphics archive in the background.
