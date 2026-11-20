# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator (phase 7 done 2026-11-21, 16th worker; phase 6 done pending review: the reviewer
  pass so far was a SAMPLE (~90 rows + scans, not independent), so the full per-batch review below is owed before
  phase 9; phase 5 done 2026-11-21: marker build toured, width gate measured, torture line ok).
- **Phase 7 review fixes (2026-11-21, 17th worker; `../.harness/reviews/...-phase7.md`):** Critical 1: ids repeat
  across script/ (19 ssb/ vs evx/), so `merge` keyed by id put EVX unit name "The Boy" on the ssb line roev07.0156;
  `merge` now keys by (id, batch JP), `check` fails a batch with a repeated id (`tests/test_merge.py`). Important 1:
  new `tools/lint.py` over the merged script/ (codes, widths, lines/page, stub last lines, leftover JP, empty `en`
  vs `script/keep_jp.txt` (58 rows with reasons), label padding, box budgets in `tools/widths.tsv`) runs in
  `check.py`: 0 errors. Important 2: `batches.wrap_lines` re-breaks a segment whose last line is under 6 letters
  over the same line count, balanced (685 rows rewrapped, page counts unchanged). Important 3: 7 lines over 44
  shortened (BMsgQ002/006.0190 + their rfd2 copies, rfd2 D760/D7DC/D8DC, SLPS D260/D288); budgets for rfd2 talk,
  memory-card and ed boxes. OMAKE captions NOT measured yet: they are (place, title, caption) triplets in a
  pointer table at op 0x800A68D0 with no direct code reference found; not shown on the album grid or the CG view
  (phase 8: find the screen, measure, add the budget). Important 4: rfd2.8009D9E4 ね。 is appended by rfd2
  0x800CF14C after it strcpys the hero name over the LAST 14 BYTES of T_Msg01 messages 8-23 (fairy compatibility):
  the English ended `is ＜勇者名＞.` (12 bytes), so the name would have eaten two letters; now `is...{n}＜勇者名＞....`
  (10 + 4 bytes overwritten) and ね。 = " " (odd-length names end in a space; a "." would read "Cecia ."); test
  in `tests/test_merge.py`, check in game in phase 8 (heaven, Titania, compatibility). Fixed-field labels padded to
  the JP width (`tools/padlabels.py`: rfd2 status/item types, right-aligned region suffixes). Minors: unit names
  are `name` kind now (wrap_spec), PH_WIDTH comment, `tests/test_hooks.py` (no branch into a font hook),
  `tests/test_lkf_leaves.py` (rebuilt LKFs: same entries, only insert's entries differ). Build sha1 da353c51...,
  check.py 54 passed + lint 0, smoke OK. New `tools/refs.py` disassembles every reference to a string.
- **Phase 7 result (2026-11-21, 16th worker):** build green (sha1 423a5f2f...), every batch `check` OK (width, pages, control codes,
  placeholders, glossary), 47 tests, smoke + 13 warps OK (`work/qa/p7`, `p7b`: map menus, fairy list, heaven,
  OMAKE CG, prologue, exam, battle x2, game over, title load, Rocus ending). **EXE/overlay relocation:** all 451
  held-back rows are in; `codetext.fit` moves 372 strings that outgrow their slot to a string heap at
  0x80010000-0x8001E000 (prepended to the EXE: `EXE_PAD` 0x10000, ~0x2F00 used) and re-points every ptr/lui
  reference, overlay refs to moved EXE strings too (`insert.repoint_exe_refs`). Per-file write logs
  (`build/fd2_en_writes/`) pass `romdiff.py --writes` for the EXE and op/rfd2/pro/ed (`tests/test_codetext.py`
  runs it, plus "no reader left" on every vacated address). Fixed on the way: `lui_pairs` kept pairing after the
  register was overwritten (phantom string イラ at SLPS.80020114 inside ペレイラ, and relocation would have rewritten
  unrelated loads; one debug printf row dropped too); tail-sharing strings (one string's tail is another's start)
  move the head; inline literal copies (`char buf[] = "..."`, lw/lb into a stack buffer) cap the English at the
  copied byte count (`codetext.copy_size`): 混乱度： "Chaos:" (9), 探索を中断し/同行を中断し "Stop search"/"Stop
  escort" + " and stand by?" (13), "Choose a fairy to command." (29), "＄＄＄＄＄＄, you get" + N + " bonus AP." (27);
  `batches.py merge` now holds back only rows that cannot be placed and says why (none left); `TERM_WAIVE` lets
  one row drop a glossary term with a reason. **Buffers** (`docs/re/space.md`): .ssb and .EVX load into the
  0x169B0-byte heap block at 0x801A4BB0 (largest built 0x6E3C), .end into 0x8000 at 0x80189B90; `insert.LOAD_CAPS`
  enforces them (MSG capped at the largest original, unmeasured). `fileslog.lua` logs each load's block size.
  **Placeholders:** the substitution code (rfd2 0x800BF280..) strncmps the tag and strcpys from EXE tables
  (heroes 0x8006F538, fairies 0x8006FE18, 57 towns 0x8006F3FC), all English now; `batches.width` counts each
  placeholder at its widest value (`PH_WIDTH`: event title 22, town 10, fairy 8...), 49 FryMsg/HVN rows rewrapped.
  The heaven "ラビエル" tag is the player's name (＄＄＄＄＄＄) from the kana-grid default: phase 8 name entry.
- **Phase 6 external review fixes (2026-11-21, 15th worker; review in `../.harness/reviews/...-phase6.md`):**
  Important 2: 様 on personal names was "Lord/Lady X" or dropped in 225 rows; D9 (`docs/decisions.md`) applies D1
  as written like game 1's D12 ("Raphael-sama", "Leyla Vigrid-sama", "＜勇者名＞-sama"); every row read
  (`work/qa/review/honorifics.tsv`, 8 by hand), new lint `tools/honorifics.py` runs in `batches.py check` (tests in
  `tests/test_honorifics.py`), glossary rulings line updated, Souza/Leoni rows added. Important 3: new
  `docs/style-reference.md` (voice rows for heroes, fairies, angels, villains, old men; JP markers -> EN devices
  with pairs; `tools/voices.py` lists speakers/markers/examples); Greza's old-man voice fixed (polish ticked).
  Minor 3: `check` fails an ordinal suffix after a variable. Minor 5: glossary says which D2 source applied.
  Important 1 (OPEN, before phase 9): the full per-batch review. `python -X utf8 tools/review_pairs.py` writes
  `work/qa/review/pairs/bNNN.txt` (`>> id | speaker | kind`, JP, EN); run `codex exec -s read-only` (credits back
  2026-11-26 10:32) with the reviewer brief, 3-5 batches per run, reports to `work/qa/review/bNNN.md`, fix
  Critical/Important per batch (voice flattening = Important per the style reference), Minors to polish.md. Point
  it at the late reveals in `docs/synopsis.md` (Serenis possessed, Viper = Clarence, Dark Clive, Savio) so early
  foreshadowing is checked (Minor 1). Without codex, do it in fresh read-only passes, a few batches per worker.
- **Phase 6 reviewer pass (2026-11-21, 14th worker; codex out of credits, so done in-session):** all 92 batches
  `check` OK; whole-script scans with the new `tools/review_scan.py` (near-miss names, katakana -> English
  consistency, the angel gendered, EN/JP length outliers for omissions; median EN/JP 2.06, no gutted rows), voice
  checks (Florinda's 18 "Florin" self-references kept; quirk endings ですぅ/だぜ/のじゃ by speaker) and a manual
  read of ~90 rows sampled across every route, EVX, BTL_EVT, men*, Raph_end, BMsgQ and FryMsg. Fixed (Important):
  スゥオレ written "Suole" in 8 alkaya rows (EXE/MssReq say "Suore"; glossary now enforces it), op.8009C928 gendered
  the angel as "it". No Critical/Important left; 6 Minors in `docs/polish.md`. `docs/synopsis.md` written (premise,
  routes, chapter list for the phase 9 story pass). Build + check.py + smoke green (build sha1 703fb02c...).
- **Phase 5 result:** width gate complete in `docs/re/text.md` §Width gate: dialogue / MSG / exam / battle boxes 44
  letters per line (3 lines; battle 2; last line 43 for the page gem), name tags 12 letters, .end narration 42,
  menu buttons ~12-14, help bar ~40. Glyph torture line renders all 84 glyphs (`work/qa/p5/torture/zoom.png`).
  Marker build reached all 66 scenes (game_over/game_over2 added). New `build.py --ruler-min N` stretches every
  line to N letters for clip tests. Non-text rows excluded: debug printfs, memory-card titles, printf `%s`.
- **Phase 6 progress (2026-11-21):** `tools/batches.py` split the script into 92 batches (b001-b092, ~3500 JP chars
  each; one row per distinct JP, merge copies it to every duplicate; order ssb, msg, evx, end, misc, ovl, exe).
  Done: **b001-b013** (alkaya fairy intros for Rosa, Florinda, Shelly, Lily, Lynx, Aquila, Cetus, Lepus; Cecia's
  ceed01/ceev01-24; Clive's cled01/clev01-25; Irene's eied01/eiev01-18, b013 ends mid snowball fight eiev18.049A).
  2026-11-21 (2nd worker): b009-b013 merged, build + check.py green, `warp.py --event eiev12.ssb --event
  eiev13_02.ssb` both OK with English (`work/qa/warp/ev_eiev1*`). Glossary gained Vesta (Irene's owl), Alkmaar,
  Grosain, Six Kingdoms, Master (tag), and batch rulings (chapter labels, gendered variants, five-＄ rows).
  2026-11-21 (3rd worker): **b014-b018** done (Irene eiev18-Eiev29 ending, preview-version exam_01-07 with Florinda/Lynx,
  Fein Feed01, Feev01-Feev14; b018 ends at Feev14.0244). Build + check.py green; `warp.py --event feev02_01.ssb --event
  feev07_01.ssb --cue <abs>/build/fd2_en.cue` both OK with English (`work/qa/warp/ev_feev0*`). Glossary gained Raynor
  (Grand Master, "Elder"), Lehan, Zern, Raviel, Lynx, Basel, Lefkas, Warlock, Black Mage; "Guild" now capitalised
  everywhere, ディアナ様 = "Diana-sama" (b005 fixed).
  2026-11-21 (4th worker): **b019-b022** done (Fein Feev14-feev31 incl. his death/ending branch, Leyla laed01,
  laev01-laev24, Rudiere loed01/loev01_01; b022 ends at loev01_01.0626). Build + check.py green; `warp.py --event
  laev10.ssb --event Feev24.ssb --cue <abs>/build/fd2_en.cue` both OK with English (`work/qa/warp/ev_laev10`,
  `ev_Feev24`; event names are case-sensitive). Glossary gained Kreutzfeld, Kaiser, Seneca (Rudiere's elephant),
  Serenis notes (Fein's wife, Irene's sister).
  2026-11-21 (5th worker): **b023-b028** done (Rudiere loev01_01-loev27_01 incl. his brother Hugues's assassination
  and ending, Michael's Demon Stone talk maseki, then the call-the-angel scenes men1_* for every hero and men2_Ce01-02;
  b028 ends at men2_Ce02.0210). Build + check.py green; `warp.py --event loev05_02.ssb --event loev10_02.ssb --event
  men1_Ro01.ssb --cue <abs>/build/fd2_en.cue` all OK with English. Glossary gained Hugues, Seneca "she", Rudiere-route
  rulings (Grand Duke, Chancellor, Endymion = Grosain's emperor, "Rudi's Mom", chapter labels over 12 letters
  shortened: "Regicide").
  2026-11-21 (6th worker): **b029-b033** done (men2_* call scenes for every hero, men3_* gift scenes, menX_* refusals,
  prologue with Raphael and every fairy's intro, Raph_end ending in the Heavens incl. the stay-human branch, roed01,
  Rocus roev01_01-roev02; b033 ends at roev02.046C). Build + check.py green; `warp.py --event roev01_01.ssb --event
  men3_Ei02.ssb --cue <abs>/build/fd2_en.cue` both OK with English (Vice Pope tag fits). Glossary gained Aquila, Cetus,
  Lepus, Titania, Gabriel, Vice Pope, the gift item list (EXE item names must match it in phase 7), Thug / Tavern Girls.
  2026-11-21 (7th worker): **b034-b037** done (Rocus roev02-roev25: tavern, Clarence "Viper" Langerack and the stolen
  Demon Stone, exile from the Holy City, the council in Ilyus, drunk-angel night, healing-hands story, confession and
  ending; then taiken/TGS preview notices, tenkai, visit_01 debug labels "01-00", Rosa's Y01ev_01 spider web; b037
  ends at Y01ev_01.0496). Build + check.py green; `warp.py --event roev05_02.ssb --event roev12.ssb --cue
  <abs>/build/fd2_en.cue` both OK with English. Glossary gained Langerack, Elias, Zeam/Azuria/Ryan (tags), Valese,
  Ilyus, Azaria, and Rocus-route rulings (Pope, archbishop, cardinal, sacred jewel, healing hands).
  2026-11-21 (8th worker): **b038-b044** done (fairy day-off events Y01ev-Y08ev, B_ItemRes item replies, hero chat
  files BMsgQ000 Fein, 001 Clive, 002 Rudiere, 003 Rocus, 004 Irene, 005 Leyla up to the Empire topic; b044 ends at
  BMsgQ005.2DBA). Build + check.py green; `warp.py --event Y02ev_01.ssb --event Y07ev_01.ssb --event Y08ev_01.ssb
  --cue <abs>/build/fd2_en.cue` all OK with English. `batches.py merge` now skips copying a dialogue translation into
  an EXE/overlay row when it is longer than the JP (it broke the build: op 夜 -> "Night") and lists those rows; the
  rfd2 overlay holds the chat prompts (まだ話があるのか？ ...) that need relocation in phase 7. Glossary gained Bremes
  (Isle), Fanlan, and the BMsgQ notes.
  2026-11-21 (9th worker): **b045-b055** done (Leyla BMsgQ005 end, Cecia BMsgQ006, BMsgQ1xx/BrvMsgQ leftovers,
  every hero's battle lines BTL_EVT0-6, BVisit greetings, EMP_NG/EMP_OK replies, EQP_Item, EvName incident titles,
  fairy reports FryMsg0 (Rosa) and FryMsg1 up to Rocus's intro; b055 ends at FryMsg1.10FA). Build + check.py green;
  `warp.py battle battle_h1` boots the grown BTL_EVT build (`work/qa/p6c/`). **Found:** ＜勇者名＞ ＜妖精名＞ ＜イベント名＞
  ＜地方名＞ ＜目的地名＞ ＜勇者名１/２＞ ○○ are runtime placeholders the game substitutes by string match (table in
  FD2BN.LKF at 0xE0FC): English keeps them byte-exact and `batches.py check` now allows them (GAME_TAGS). Phase 7: the
  values substituted (hero/fairy names, EvName titles, region names) come from tables that need English, and the
  wrap counts each placeholder as its JP width; verify a fairy report in game. Glossary gained the fairy-report
  towns, Celesta/Courrege/Ellora/Linares/Araras/Darg/Reizefut/Fes, battle name tags (12-letter rulings).
  `batches.py todo` lists the rest. Glossary gained (2026-11-21): Holy Mother, Demon Stone, Heavenly Dragon, Crimson
  Moon King, archangel, Lake Dreihaup (b001 spelling kept), Mount Delphinia, Clive Saingrent (Ravenruft is the vampire
  king, his father), Irwin, Viper, Zig, Titan. Grown ssb boot test: `warp.py --event clev11.ssb --event ceev14.ssb
  --cue <abs>/build/fd2_en.cue` both OK, English renders and wraps (`work/qa/p6b/`); warp.py's default cue is the
  ORIGINAL disc, so always pass `--cue` for the build. Workflow per batch (no subagents under Orca): Read
  `trans/batches/bNNN.tsv` in ~25-50-line parts, write `trans/parts/bNNN_K.tsv` (id<TAB>en), join with
  `(echo -e "id\ten"; cat trans/parts/bNNN_*.tsv) > trans/en/bNNN.tsv`, `batches.py check bNNN`, then `merge` and
  `build.py`. ~4 batches fit one worker context; brief in `docs/translator-brief.md`, terms in `glossary.md` (seeded
  this session: heroes Fein, Irene, Rocus, Clive, Leyla, Rudiere, Cecia; places Grosain, Ecclesia, Six Kingdoms
  Alliance, Legrance, Reyforia Forest...; extend it as names appear).
  Open for phase 7: merge's wrap adds `{wait}{clear}` pages when a page runs over 3 lines, which can leave a
  one-word orphan page (alkaya.0238 "tundra."): rebalance in the fit pass; script buffer size still unknown (two
  grown event scripts boot fine, the rest are untested). No `docs/synopsis.md` / style reference yet: write them once the story
  scripts are read (voices so far in the brief). Review pass not done (codex out of credits until 2026-11-26).
  2026-11-21 (10th worker): **b056-b069** done (fairy reports FryMsg1 end, FryMsg2 Shelly, 3 Lily, 4 Lynx, 5 Aquila
  (shy "Um,"), 6 Cetus, 7 Lepus (very formal); GenAnsw/GenNG incident yes/no replies for heroes 0-6; HVN_Msg00
  Raphael's level-up, gift and advice lines; MssAns0-6 mission replies; b069 ends at MssAns6.066C). Build +
  check.py green; `warp.py map_fairy heaven --cue <abs>/build/fd2_en.cue` both OK with English (heaven tag
  ラファエル still JP: name-tag table, phase 7). New `tools/similar.py bNNN [first last]` prints each row with the
  closest translated row of the same file family (FryMsgN/GenAnswN/MssAnsN are parallel files: translate from the
  parallel, in the speaker's voice; read its output via a code runner in 10-20-row chunks). `batches.py check`: a
  glossary term inside a longer matched term is skipped (ルディ in ウルディピア); ＜ボーナスＡＰ＞ kept as a tag.
  Glossary gained Raphael's equipment list (Elivagar ... Graal: the EXE item names at SLPS.80020A04-0BF8 must
  match), 混乱度 "chaos level", and MssAns places (Karnal, Cadiz, Salem, Larissa, Lanas, Erlanges/Jotun, Seriphos,
  Dilolo, Ragwort, Zarha, Rooak, Kaluga); クラン "Kran" (MssAns2, not in the table: it matches クランク etc.).
  Angel magic: 大回復 "Great Heal", 透明 "Invisibility", 連撃 "Flurry".
  2026-11-21 (11th worker): **b070-b078** done (MssAns6 end, MssReq mission requests with ~90 new place names,
  NASI_NG/NASI_OK replies, SUP_Item, T_Msg00 hero advice and T_Msg01 fairy compatibility (templated by a throwaway
  script), Cecia EVX ceev03-ceev24e incl. Ion, Serenis, Beelzebub's last battle and the Michael/Raphael rescue, Clive
  EVX clev01-clev17; b078 ends at clev17.070D). Build + check.py green; `warp.py --event clev13.ssb` shows the Holy
  Mother EVX in English (`work/qa/p6d/clev13_zoom.png`; its "blank" verdict is a black arrival frame, the scene runs);
  `--event ceev16.ssb` lands on feev17's EVX (Fein, still JP: b081+). New `tools/termfind.py JP..` shows how a term
  was already translated. Glossary gained the MssReq places, fairy sexes (Aquila f, Cetus/Lepus m), Vastir, Ion.
  2026-11-21 (12th worker): **b079-b082** done (Clive EVX clev17-clev30 incl. Dark Clive and the last battle, Irene
  EVX eiev02-eiev30 incl. the Grand Lodge attack and Serenis's death, Fein EVX feev01-Feev31, Leyla laev02-laev05_0;
  b082 ends at laev05_0.04F3). Build + check.py green; `warp.py --event eiev13_03.ssb --event Feev26.ssb` both OK
  with English. Event names: `lkf.py list work/disc/tree/SSB_DATA.LKF` (EVX file names like eiev05e are not events).
  `batches.py check` now fails EVX titles (.0002) over 30 bytes (evx.build asserts it). New names: レイジハー
  Reijiher, グレザ Greza, ランド Rand (guild masters/mages, feev02-03); 帝国戦士 tag "Warrior".
  Same worker: **b083-b084** done (Leyla laev05-laev25 incl. General Kaiser's duel and Alberic's breakdown, Rudiere
  loev02-Loev15A_01 incl. Savia/Savio's backstory; b084 ends at Loev15A_01.0C8A). Build + check.py green; `warp.py
  --event laev07_01.ssb --event loev09.ssb` both OK. New names: ソーザ Souza (noble), レオニ Leoni (boy); tags 衛兵
  "Guard", 街の娘 "Town Girl"; Rudi's alias ルディ・トライア "Rudi Trier".
  2026-11-21 (13th worker): **b085-b092** done, `batches.py todo` is empty (Rudiere EVX loev15-27 incl. Savio's end,
  Rocus EVX roev06-25 incl. Ion's death, Viper's end and his healing visits to every hero; all 21 .end epilogues;
  Dummy00; ed clear-data prompts; op gallery captions; pro quiz; rfd2 field/heaven menus; EXE town table, item and
  equipment names, memory-card messages). Build + check.py + smoke green; `warp.py --event loev16.ssb --event
  roev20_09.ssb` and `warp.py heaven map_fairy` all OK with English. Tool changes: `batches.py merge` now holds back
  EVERY EXE/overlay row whose English is longer than the JP (451 rows, listed by merge; the English stays in
  `trans/en/` for phase 7) and clears a stale `en`; `check` fails `fixed N-byte record` rows over N-1 bytes (Dummy00
  broke the build), allows ￥ (quiz line break) when the JP count matches, and accepts a capitalised / title-case
  glossary term ("Chaos Level"). Left Japanese on purpose (`-`): debug printfs, memory-card titles, the kana grid
  pro.800A1864, the ＜...＞ placeholder keys and ００/００００/full-width digits in rfd2 (string-match keys and number
  glyphs), blank/space rows. Phase 7 notes: rfd2 builds sentences from fragments (`[fairy]を[hero]に同行させますか？`,
  `これは N 個持っているわね。`): English fragments were written to read in JP order (", accompany " + "?",
  "Of these, you have " + "."), check them in game; rfd2.8009D958 (Titania on a fairy, 彼女) written neutral;
  SLPS パレーゼ treated as Valese (バレーゼ). Glossary gained the EXE town table, heaven palaces, Holy Nation.
- **Phase 8 progress (2026-11-21, 18th worker):** build re-verified (sha1 da353c51...). Full tour
  `warp.py --all -j 1 --cue <abs>/build/fd2_en.cue --out-dir work/qa/tour` was killed by the host for low memory
  after 48 of 66 scene folders: re-run the rest (`warp.py SCENE.. --out-dir work/qa/tour`) with nothing else open, then
  `qa_gate.py init work/qa/manifest.tsv work/qa/tour --build build/fd2_en.bin` and verdicts. `docs/visual-qa-brief.md`
  copied (add standing non-bugs). New, UNTESTED in the emulator: `tools/debug/textcover.lua` (logs LKF loads + first
  reads of the overlay/.end/script buffers; run on the ORIGINAL disc with `--lua tools/debug/textcover.lua --debugger
  --out-dir work/qa/cover`) and `tools/textcover.py` (maps reads to script/ rows, waivers in docs/text_unshown.tsv;
  EXE strings not watched yet). First test: one event scene; check that loading does not read whole files (memcpy
  would fake full coverage) and that the run speed is usable.
- **Next (phase 8):** QA in the emulator per the skill's phase 8 done-when (tour sheets + visual-QA verdicts via
  `qa_gate.py`, graphics text G-rows incl. the OMAKE profile panel (stylized-font graphic, still JP), chapter cards,
  game over, credits; `inkbox.py` on choice/menu boxes; stress saves; `textcover.py`). Carried from phase 7: add a
  warp scene that shows a fairy report with placeholders (FryMsg: ＜イベント名＞ / ＜目的地名＞ lines) and check the
  substituted English fits; check the rfd2 sentence fragments in game (fairy command confirmations "Stop search and
  stand by?", "[fairy], accompany [hero]?", item counts); measure the OMAKE gallery caption width (op captions
  are up to 73 letters, never measured); name entry Latin page + the default name ラビエル (kana grid). From the
  phase 7 review: inkbox the menX_* `Yes`/`No` choices (JP indents one cell, maybe for the cursor; `warp.py --event
  menX_Ce01.ssb --out-dir work/qa/p8` reaches the scene, text fine at f010350, but the mash clicks past the choice
  between shots: add a scenes.tsv row with after=hold and a short route) and the
  right-aligned region suffixes; find out whether EVX unit names (151 over 12 letters, e.g. ceev20.0192) are ever
  drawn (battle plates are PIX graphics) and apply the 12-letter budget if so, else record it in text.md. Polish
  list gained the 12-letter name-tag / chapter-label cuts and the fixed-copy labels (engine work first, D4).
  Earlier (15th worker): orphan pages:
  `batches.wrap` breaks an overflowing page at the latest sentence end that fills 2+ lines, else joins a lone short
  last line with the line before (`tests/test_wrap.py`); 177 rows rewrapped, short last pages 135 -> 4, page count
  unchanged; build + check.py (40) + smoke green (sha1 c13b00b5...), `warp.py --event laev14.ssb` OK.
  Cuts to revisit when the name-tag table is relocated (D4, review Minor 2): 帝国兵 "Soldier", 帝国戦士 "Warrior",
  第10節「王暗殺」 "Regicide" and the other 12-letter name-tag / chapter-label shortenings in the glossary notes;
  restore the full forms if the relocated table allows, else waive each in polish.md with the reason.
  Budgets: BTL_EVT banks 64 KB cap, EvName 22 bytes, EXE/overlay strings any length (relocated) except inline
  literal copies, shared-lui and pro quiz table slots (`batches.py merge` says which).
  Name entry: kana grid (G6) has A-Z a-z on the keyboard font; decide the Latin page in phase 8.
- **Done (2026-11-20):**
  - Step 0, phases 1-3 (see git history; `docs/re/README.md`, `docs/re/debug.md`, `docs/re/disc.md`): 66 warp scenes
    from cold boots, `save.py`, 40 states in `work/states/`; identity build byte-identical as a test; grown LKF
    entries boot.
  - **Phase 4 (this session):** `tools/extract.py` writes 692 TSVs / 32292 rows (`docs/re/text.md` §Extraction):
    MSG (5 layouts decoded, incl. BrvMsgQ reply prefixes and BTL_EVT slot records), ssb (jump ops found: scripts
    are NOT linear; `ssb.build` re-points jumps), EVX (dialogue records, unit names, choices), .end paragraphs,
    Dummy00.DAT, EXE + overlay strings with their pointer/lui sites (pro.bin quiz = fixed tables). `tests/test_text.py`:
    rows and files round-trip, coverage (every SJIS run inside a row), script/ in sync, ssb/EVX grow tests.
    `tools/insert.py` turns `en` columns into the build's changes; default build = original sha1 (0 rows translated).
- **Open items from phase 4 (still open):**
  - ssb name rows: op 0x19 counts characters; `ssb.build` asserts an even byte count. Decide how ASCII names count.
  - EVX growth only re-parse-tested; boot-test a grown EVX battle (warp `battle_*`).
  - Prologue quiz text uses `￥` as its line break; EvName fields hold 22 bytes; EVX unit names 32 bytes.
  - Memory-card save titles in the EXE (`純白の預言者　ゲームデータ０１`) show in the BIOS card manager (full-width only).
  - Warp batches: run **-j 1** on this machine (-j 2 ran low on memory, -j 4 was killed by the OS).
  - キャラ劇 (GRPDATA 558 battle.tim) is not in OMAKE and no script or traced scene loads it: probably unused.
    Phase 8: `--all --lua tools/debug/fileslog.lua --debugger`, grep for battle.tim (and Dummy00.DAT); if never
    loaded, drop G9.
  - Don't edit warp.lua while a batch runs: runs that start mid-edit fail.
- **Open bugs:** none.
- **Waiting on the user:** nothing. Non-blocking, for phase 8: the FMV captions and the Japanese staff roll in
  DEMO.STR/ENDING.STR (D3 says credits in English): re-encode the MDEC video or overlay subtitles; default plan is to
  re-encode ENDING.STR's credit section with English text. codex exec is out of credits until 2026-11-26 (no
  independent reviewer until then).
