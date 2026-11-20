# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-20 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-11-20 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. For names shared with the first game, use `../favorite-dear-en/glossary.md` (series consistency, per-game override). |
| D3 | 2026-11-20 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-20 | Abbreviations | engine work first (default), abbreviate | Default: full names and terms, engine work first; abbreviate only as a flagged last resort. |
| D5 | 2026-11-20 | Graphics text left in Japanese | none (default), list | Translate all (titles, menus, banners, cards); keep the Japanese logo only if it has no official English version. |
| D6 | 2026-11-20 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through checkpoints, report at the end. |
| D7 | 2026-11-20 | Existing saves / memory cards | use them, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-20 | Reference material | - | Per-game override: the first game's project `../favorite-dear-en` may be used as a reference (glossary, style, tools). |
| D9 | 2026-11-21 | How D1 applies to angels, demons, kings and nobles (phase 6 review: 225 rows had "Lord Raphael", "Lord Satan", "Lady Serenis", dropped full-name 様, ＜勇者名＞様 with no suffix; agent's call under D6, not asked) | ask the owner; "Lord/Lady X" for high ranks, -sama elsewhere; apply D1 as written | Apply D1 as written, as the first game ruled in its D12 (series consistency, D2/D8): name + 様/殿/さん/くん/ちゃん -> "-sama/-dono/-san/-kun/-chan" for every personal name, full names and the placeholders (＜勇者名＞-sama) included; the English title it replaced goes ("Lord Raphael" -> "Raphael-sama"). Title words (卿, 王子) and address nouns (天使様 "Angel") stay English. 225 rows changed, each read (`work/qa/review/honorifics.tsv`; 8 by hand: "Fein-san" for フェイン様, "L-Lord Michael" stutter). Lint: `tools/honorifics.py`, run by `batches.py check`. |
