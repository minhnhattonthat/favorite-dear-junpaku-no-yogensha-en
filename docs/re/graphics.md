# Graphics text survey

Static sweep reviewed 2026-11-20 (all 32 TIM sheets, the PIX name plates, BLF headers, every FMV). Phase 5's marker
tour adds any screen the sweep can't see (text composed at runtime from glyph strips, the name-entry keyboard).

## Static sweep (how to regenerate)

- TIMs: `python -X utf8 tools/tim.py dump work/gfx` -> 1252 TIM images from all LKF archives (`work/gfx/index.tsv`;
  entries with no TIM in `work/gfx/skipped.tsv`: 1158, mostly scripts/sound). Sheets:
  `python -X utf8 tools/gfxsheets.py work/gfx work/gfx/sheets --per 40 --width 1600` (32 sheets, `index.tsv`).
  Reviewed: sheets 000-007 and 029-031 at full size with zoomed crops (`sheet.py --zoom 3`); 008-028 (character
  portraits and event CGs, the `Xxpo/Xxev/Xxed` sets) three per image at 40% (large lettering only; none of those
  CGs carried small text in the full-size sample, sheet 007).
- Name plates: `python -X utf8 tools/pix.py sheet work/lkf/GRPDATA work/gfx/name_plates.png` (format in `pix.py`).
- FMV: `python tools/str2352.py work/disc/tree/X.STR work/fmv/X.raw`, then
  `ffmpeg -f psxstr -i work/fmv/X.raw -vf "fps=1/3,scale=160:-1,tile=8x8" work/fmv/x/t%02d.png`.
- Not image data: SFM/SFA (sprite frame maps over TIM sheets), TMD (3D models, textures are TIMs), CLT/RCT
  (palettes/rect tables). BLF (`6x624_4.BLF` and `Map88.BLF` GRPDATA, `Map220.BLF` FD2SN): "BLF\0", u32 count, u32 header size 0x20,
  u32 entry size 0xA0; each entry is an MDEC bitstream block (`80 00 00 38 05 00 02 00` = STR v2 frame header), so
  it is MDEC-compressed imagery (guess: the 3D battle map / world map backdrop); not decoded. Check it on the tour
  (phase 5); no text expected.

## Rows (every Japanese-on-screen element found)

| # | Element | Image / source | Japanese | Status / plan |
|---|---|---|---|---|
| G1 | Title logo (title screen, two variants) | GRPDATA_1471, 1473 (TIM) | 純白の預言者 (with English "FAVORITE DEAR" above) | **kept** (phase 8, D5): no official English logo exists, so 純白の預言者 stays under the English "FAVORITE DEAR" (title verdict). rogo_00.tim (1471) is never loaded (FILE logs of all 613 coverage/tour runs, 2026-11-21) |
| G2 | Fairy name list (OPTION / album menu?) | GRPDATA_0049 left column | フェイン クライヴ ルディ ロクス アイリーン レイラ セシア ローザ フロリンダ シェリー リリィ リンクス アクイラ シータス レーパス | **no change needed** (phase 8): T_NAME_0 loads in nearly every run, and every fairy name on the 200 tour sheets (album, fairy lists, status) is English: the game draws the English column; no sheet shows the JP one |
| G3 | Status-effect tags | GRPDATA_0057 row of six tags | パラライズ ポイズン コンフュ 石化 スリープ チャーム | DONE 2026-11-21 (`tools/banners.py`, `gfx/banners.tsv`): 36x16 tags at (40*i, 184); Paralyze Poison Confuse Stone Sleep Charm in the narrow `fonts/font_tag.txt` (Paralysis/Confusion don't fit 36 px; the JP words are paralyze/confu) |
| G4 | Battle skill banners (6) | GRPDATA_0057 bottom (16-row pills at y 208/224/240, x 0 and 104) | 逃走 戦闘から退却 / 小回復 HP100回復 / 大回復 HP完全回復 / 連撃 攻撃を3回繰り返す / 透明 敵の攻撃を3回無効化 / 祝福 特殊能力カバー上昇 | DONE 2026-11-21 (`tools/banners.py`): Flee Leave battle / Minor Heal +100 HP / Major Heal Full HP / Combo Attack 3 times / Vanish Nullify 3 attacks / Blessing Skill cover up; pills keep their width. 4 bpp, 16 CLUTs: redrawn in index space, valid for every CLUT |
| G5 | Small katakana strip | GRPDATA_0057 top-left | small kana glyphs | **not seen** (phase 8): an_mag_0 loads in the 57 battle runs; no battle sheet shows small kana (all battle sheets ok) |
| G6 | Name-entry keyboard font (two colours) | GRPDATA_0051, 0052 | hiragana + katakana grid (A-Z a-z already present) | **kept** (phase 8): the kana pages stay (input, not text); the Latin page is one arrow press away and names are stored as pair glyphs (`asm/name.asm`); opening on the Latin page is in polish.md |
| G7 | Battle unit name glyph strips | GRPDATA_0458 (katakana + digits), 0459 (kanji 海竜民兵反乱帝国歩騎重士隊長融合天) | glyph strips | **never drawn** (phase 8): BAT_NM00/01.TIM are never loaded in the FILE logs of all 613 coverage/tour runs (every event, battle and warp scene); battle names are the G8 plates |
| G8 | Battle unit name plates (88) | GRPDATA `Name_000..087.PIX` (`tools/pix.py`) | enemy and hero names (ウルフ, ホワイトファング, 帝国騎士, フェイン...) | DONE 2026-11-21: `gfx/plates.tsv` (88 rows: 0-80 Name_000..NAME_080, 81-87 Name_B00..B06 heroes) rendered by `tools/plates.py` with fonts/font6 into the build; seen in game (`work/qa/p8/plates`) |
| G9 | "キャラ劇" title card (character theatre extra) | GRPDATA_0558 (also small UI labels マンイーター / デッドプラント / アイリーン in the mock) | キャラ劇 | **never drawn** (phase 8): battle.tim is never loaded in the FILE logs of all 613 coverage/tour runs; dropped |
| G10 | Album profile text atlas | GRPDATA_1454 | names, jobs (聖職者 魔導士 ...), birthdays (4月24日), heights/weights, homelands (〜王国, 〜の森) | DONE 2026-11-21 (`tools/album.py`, `gfx/album.tsv`): the album draws fixed rects of the atlas, computed in code (no table found in op.bin or the EXE); found with `tools/debug/ramdump.lua` + `tools/sprites.py` (GP0 0x64 packets, CLUT word 0x7C0C) on every album page. Names 24 rows high at v 0/24/48, jobs v 72/96/120 (right-aligned on screen), birthdays 88,144+16k 48x16, homeland blocks (出身地 + place) 144,32k 72x32, height/weight 216,32k 40x32 (Latin, untouched), page 8 list 0,144 80x112. English in label14 (DejaVu 14 px) where it fits, else font6, else font_tag ("Prince" in 24 px); 天界 "Heaven" (32 px) |
| G11 | Spell-effect glyphs | GRPDATA_1494 (KANJI.tim) | six large decorative pseudo-kanji (not real characters) | **kept** (phase 8): effect art, not readable text; loaded only in clev20_01 |
| G12 | Developer scraps in sprite sheets | GRPDATA_0095 (防 死 ひざ), 0096 (small notes), 0183/0196 (tiny labels) | tiny notes | **not seen** (phase 8): the sheets load with their enemies (battle_h3, roev06-14, clev01/02, eiev02), but no tour sheet shows the notes; off-sprite scraps |
| G13 | "開発中" test screens | GRPDATA_1423, 1424 (test01/02) | 開発中 | **never drawn** (phase 8): test01/02.tim are never loaded in the FILE logs of all 613 coverage/tour runs |
| G14 | Opening movie captions | DEMO.STR | burned-in lyric/caption lines (うるわしき実り豊かな土地...) | **done** (2026-11-21): 7 captions re-encoded in place (`tools/fmv.py`, `gfx/fmv.tsv`, codec `tools/mdec.py`); seen in the emulator boot (`work/qa/p8/demo_emu.png`). The title logo in the movie stays (same as the title screen) |
| G15 | Ending movie captions + logo + staff roll | ENDING.STR (52728 sectors) | 悲しみはよろこびに場所を譲り / 勇者は希望の槍となる──, 純白の預言者 logo, full Japanese cast and staff credits | **done** (2026-11-21, 25th worker): caption = two `gfx/fmv.tsv` rows in mode `white` (white letters drifting sideways, line 1 +0.325 px/frame, line 2 -0.444, `dx` column); staff roll = `tools/roll.py` + `gfx/roll.tsv` (143 lines: strip boxes measured from a median strip, style, English; roll scrolls 1.5 px/frame from frame 330 to 4114, panel 0.19 px/frame; each line box refilled from panel-aligned nearby frames, English strip drawn at 2x and cut at the half-pixel offset). The 純白の預言者 logo stays (like the title logo, G14). |

Already English in the original (no work): menu labels and stats (GRPDATA_0001, 0002, 0049 right part, 0054
Name/Birth), title menu NEW GAME/LOAD GAME/OPTION (1474), Game Over (1487, 1488), "Fin" (0055, 0056), tarot-style
cards (1514, 1515), battle grid letters. CI_LOGO, DRA16, DRAGON16, MONO.STR carry no Japanese (logos and an
untexted dragon sequence).

## Tour (cold boot, original disc, `work/qa/boot0`, `boot1`, `newgame0..3`)

| Screen | Japanese seen | Source |
|---|---|---|
| Title (f6000+) | logo 純白の預言者 (G1); menu already English | GRPDATA_1471/1473 |
| Opening movie DEMO.STR | captions (G14) | FMV |
| New Game name/birthday screen | labels English; message box text (名前を決定します。, これでいいですか？ はい/いいえ) | font text (EXE/overlay strings) |
| Name-entry keyboard | katakana grid, "END" | G6 + a code table |
