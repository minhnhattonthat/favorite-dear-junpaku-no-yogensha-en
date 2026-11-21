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
- [ ] gfx/plates.tsv 77 天竜 battle name plate "Heaven Dragon" (glossary "Heavenly Dragon" is 70 px, the PIX plate 64x12). Waive, or redraw in a narrower face.
- [ ] Name entry opens on the katakana page; the Latin page is one arrow press away. Opening on the Latin page would suit English players (find the page variable in pro.bin near 0x8009BF80).
- [ ] Odd-length Latin player names end in a space (pair glyphs fill whole 12 px cells): "Ray , welcome". Half-cell rendering of the name placeholder would fix it. Same for every runtime placeholder spliced by rfd2 0x800BF280 (strcpy of whole pairs): hero names Cecia/Rocus/Irene/Leyla in fairy reports read "Cecia -sama has resolved" (`work/qa/tour/battle_h*`), odd town names (＜地方名＞/＜目的地名＞) before "." or ",". Fix idea: pad odd names with an unused pair index used as a marker, and after the splice re-pair the buffer (decode pairs, drop markers, re-encode). Event titles (EvName) avoid it: all even, at most 20 letters (lint).
- [ ] gfx/album.tsv G10 cuts forced by fixed atlas rects (computed in code): 天界 "Heaven" (glossary "the Heavens", 32 px rect), レグランス王国 "Legrance" (Kingdom of Legrance), 六王国連合 "Six Kingdoms" (Alliance dropped), 王子 "Prince" in the 3 px tag font (24 px rect). Restore if the album code rects are found and widened.
- [ ] Pair glyphs show a gap inside even-length names on the name-entry field and the angel status panel: "Ravi el" (work/qa/tour/name_entry, heaven_status_angel). The pair glyph "vi" leaves its right half blank; kern the pair glyphs or render narrow letters into one cell.
- [ ] rfd2.8009D0E0 / D010 heaven help bar (fixed ~210 px pill, 30 letters): "Go to another palace" ("in the Heavens" dropped), "Borrow fairies, hear the news". Restore if the pill can be widened.
- [ ] gfx/banners.tsv G3 tags "Paralyze"/"Confuse" (the JP words; the status screen says Paralysis/Confusion) in the narrow tag font: 36 px sprites. Waive or widen the sprites.
- [ ] gfx/roll.tsv G15 staff-roll readings not confirmed by a source (Hepburn guesses, no macrons as in game 1; names shared with game 1's staff roll copied from it: Tsunoda, Atarashi, Karibe, Kozama, Miyagawa, Arata Yasuda...): 服部かりか Karika Hattori, 田中大文 Hirofumi Tanaka, 堀之紀 Yukitoshi Hori, 森麻衣子 Maiko Mori, 難波司 Tsukasa Nanba, 傘木康史 Yasushi Kasagi, 遠山博一 Hirokazu Toyama, 中村静男 Shizuo Nakamura, 森知晴 Tomoharu Mori, 山中瑠奈 Runa Yamanaka, 樋野清史 Kiyoshi Hino, 伊藤英剛 Hidetaka Ito, 永吉幸樹 Koki Nagayoshi, いーのあゆみ Ayumi Ino, 林克洋 Katsuhiro Hayashi, 草嶋一 Hajime Kusajima, 柱将夫 Masao Hashira, 鶴山尚文 Naofumi Tsuruyama, 露木輝 Hikaru Tsuyuki, 中村光毅 Mitsuki Nakamura, 宮崎暁 Akira Miyazaki, 上久保悠里 Yuri Kamikubo. Check against a staff database or waive.
- [ ] ENDING.STR opening caption: where the feather crosses the sharp letters (frames ~80-104) it is erased with them (inpainted streak), and the caption's last blur-out frames 112-118 lose the English smear (the blurred Japanese is erased, nothing drawn). Same class as the DEMO feather minor.

## Phase 9 story pass (2026-11-21; reports in work/qa/story/reports/)
- [x] tenkai.062E - ええ answering "Michael-sama?" was the family's "Of course." (fixed: "Yes.", trans/overrides.tsv)
- [x] Raph_end.00E0 - ご苦労だったな "You did hard work in Arcaya" (fixed: "You went through a great deal in Arcaya.")
- [x] ceed1.01C6 - ここでのみ生きることはできない read as "no one could live in it alone" (fixed: "they could not go on living within it alone")
- [x] ceev16.0D79 (+feev17.0731, roev14.0CD6) - Ion's こいつをやっつけろ！ was "Get her!" in male heroes' fights too (fixed: "Get 'em!")
- [x] clev21.0549 - 帝国の魔女、天竜など、よみがえらせはせん misread as reviving the witch (fixed: "Witch of the Empire... I won't let you revive the Heavenly Dragon...")
- [x] Feev19.09DE, clev20_01.0682, loev04_02.0BAA - ええ as "Of course." where a plain "Yes." is meant (fixed, overrides)
- [x] clev21.09AD - the spellbound Emperor's ああ…… was "Yeah..." (fixed: "Ahh...", override)
- [x] ceev20/ceev20b/eiev14/Feev19/laev20/laev20b/loev21/loev21b/roev21 - the same Emperor ああ…… in the other routes (fixed: "Ahh...", overrides)
- [x] loev13.044E - そうだな…… was "Perhaps..." where Rudiere agrees (fixed: "Yeah...", override)
- [x] BTL_EVT2.4A61 - "Was it you?! You carried off the women!" (fixed: "So it was you?! You're the ones who took the women!")
