# Polish list

Minor review findings, deferred to one polish pass before release. Tick each `[x]` as fixed or `waived: reason`;
the release refuses to run while any line is unticked.

## Phase 6 reviewer pass (2026-11-21)
- [x] feev02_03.0563-0738 - Greza's old-man speech (ワシ, じゃ, のじゃ, じゃろ) reads neutral; give him a light elderly register (fixed 2026-11-21: "lad", "aye", "I'll not")
- [x] laev07.077B - アルベリック殿 rendered "Lord Alberic"; ruling D1 says 殿 = "-dono" (fixed: "Alberic-dono", D9)
- [ ] BTL_EVT4.370A - だったら、どうしようってんだ？ means "so what are you gonna do about it?", EN has "So what if we are?"
- [ ] men3_Ei03.01DA - ぬいぐるみ written "stuffed bear": confirm the gift item is a bear, else "stuffed toy"
- [ ] roev12.0DEA - なんだよ…… rendered "Look who's talking..." (a liberty; fine if kept)
- [x] op.8009C0CC - the angel "show itself" in a gallery caption: use a neutral wording that is not "it" when the line is refitted in phase 7 (fixed 2026-11-21: "reveal their presence"; the caption is relocated)

## Phase 7 fit (2026-11-21)
The EXE/overlay strings no longer limit the English (relocated), but the name-tag frame draws 12 letters
(`docs/re/text.md` §Width gate): that is the drawn frame, not a table, so D4's engine-first route is to widen the
tag frame or draw long tags with narrower letters. Restore each full form if that works, else waive it here.
- [ ] Name tags cut to 12 letters (glossary notes): 帝国兵 "Soldier" (Imperial Soldier), 帝国騎士 "Knight", 帝国戦士 "Warrior", 帝国歩兵 "Foot Soldier", 融合兵 "Fused Troop", 私兵 "Hired Guard", 王の女 "King's Lady"
- [ ] Chapter labels over 12 letters (EVX titles / scene labels): 第10節「王暗殺」 "Regicide" and the other shortened labels
- [ ] rfd2.8009BABC 混乱度： "Chaos:" (the code copies a fixed 9 bytes into a stack buffer; "Chaos Level:" needs that copy rewritten, `codetext.copy_size`); likewise rfd2.8009C2BC/C2CC "Stop search"/"Stop escort" + " and stand by?" (13-byte copies)

## Phase 8 QA (2026-11-21)
- [ ] rfd2.8009D628 聖アザリア宮 heaven Move button "Azaria Palace" (St. dropped: the 14-letter button clipped "St. Azaria Palace" at both ends; full name kept in dialogue). Restore if the button sprite is widened.
- [ ] Name entry opens on the katakana page; the Latin page is one arrow press away. Opening on the Latin page would suit English players (find the page variable in pro.bin near 0x8009BF80).
- [ ] Odd-length Latin player names end in a space (pair glyphs fill whole 12 px cells): "Ray , welcome". Half-cell rendering of the name placeholder would fix it.
