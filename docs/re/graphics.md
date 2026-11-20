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
  (palettes/rect tables). BLF (`6x624_4.BLF` GRPDATA, `Map220.BLF` FD2SN): "BLF\0", u32 count, u32 header size 0x20,
  u32 entry size 0xA0; each entry is an MDEC bitstream block (`80 00 00 38 05 00 02 00` = STR v2 frame header), so
  it is MDEC-compressed imagery (guess: the 3D battle map / world map backdrop); not decoded. Check it on the tour
  (phase 5); no text expected.

## Rows (every Japanese-on-screen element found)

| # | Element | Image / source | Japanese | Status / plan |
|---|---|---|---|---|
| G1 | Title logo (title screen, two variants) | GRPDATA_1471, 1473 (TIM) | 純白の預言者 (with English "FAVORITE DEAR" above) | D5: keep Japanese only if no official English logo exists; else redraw with an English subtitle (wording from the glossary). Decide in phase 8 |
| G2 | Fairy name list (OPTION / album menu?) | GRPDATA_0049 left column | フェイン クライヴ ルディ ロクス アイリーン レイラ セシア ローザ フロリンダ シェリー リリィ リンクス アクイラ シータス レーパス | English set already sits in the same TIM (Rosa, Florinda...): find which column the game draws; maybe the JP column is unused |
| G3 | Status-effect tags | GRPDATA_0057 row of six tags | パラライズ ポイズン コンフュ 石化 スリープ チャーム | redraw (English words exist in GRPDATA_0002: Paralysis, Poison, Confusion, Stone, Sleep, Charm) |
| G4 | Battle skill banners (6) | GRPDATA_0057 bottom | 速走 移動力+1 / 小回復 HP100回復 / 大回復 HP完全回復 / 自爆... / 恐怖... / 鉄壁 ... | redraw; read exact text at zoom 6 in phase 8 |
| G5 | Small katakana strip | GRPDATA_0057 top-left | small kana glyphs | find use on the tour |
| G6 | Name-entry keyboard font (two colours) | GRPDATA_0051, 0052 | hiragana + katakana grid (A-Z a-z already present) | the keyboard layout itself is code/table-driven: decide in phase 5 whether to drop the kana pages |
| G7 | Battle unit name glyph strips | GRPDATA_0458 (katakana + digits), 0459 (kanji 海竜民兵反乱帝国歩騎重士隊長融合天) | glyph strips | probably composes unit labels at runtime; find the user on the battle tour |
| G8 | Battle unit name plates (88) | GRPDATA `Name_000..087.PIX` (`tools/pix.py`) | enemy and hero names (ウルフ, ホワイトファング, 帝国騎士, フェイン...) | redraw with a small font into 64x12; names from the glossary. Verified format |
| G9 | "キャラ劇" title card (character theatre extra) | GRPDATA_0558 (also small UI labels マンイーター / デッドプラント / アイリーン in the mock) | キャラ劇 | redraw |
| G10 | Album profile text atlas | GRPDATA_1454 | names, jobs (聖職者 魔導士 ...), birthdays (4月24日), heights/weights, homelands (〜王国, 〜の森) | redraw the whole atlas (largest graphics job) |
| G11 | Spell-effect glyphs | GRPDATA_1494 (KANJI.tim) | six large decorative pseudo-kanji (not real characters) | probably keep (they are effect art); confirm on the tour |
| G12 | Developer scraps in sprite sheets | GRPDATA_0095 (防 死 ひざ), 0096 (small notes), 0183/0196 (tiny labels) | tiny notes | almost certainly never drawn; confirm none appears on the tour |
| G13 | "開発中" test screens | GRPDATA_1423, 1424 (test01/02) | 開発中 | test images, guess unused (no reference found yet) |
| G14 | Opening movie captions | DEMO.STR | burned-in lyric/caption lines (うるわしき実り豊かな土地...) | FMV re-encode or subtitle overlay: phase 8 decision |
| G15 | Ending movie captions + logo + staff roll | ENDING.STR (52728 sectors) | 悲しみはよろこびに場所を譲り / 勇者は希望の礎となる──, 純白の預言者 logo, full Japanese cast and staff credits | D3 says credits in English: FMV re-encode (MDEC) or overlay; phase 8 |

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
