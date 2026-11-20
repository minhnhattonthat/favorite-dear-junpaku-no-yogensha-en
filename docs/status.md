# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator (27th worker: main gate 193/193 ok, inkbox done, stress saves done, textcover
  tool fixed and piloted. NEXT, in order: (d) textcover bulk runs (see 27th worker entry); (e) final re-tour on the
  final build + verdicts for changed sheets. 26th worker: G14+G15 built into e2206009; choice indent fixed. 25th worker: G15 ending caption + staff roll written; 24th worker: G14 opening captions done; 23rd worker: all 191 sheets have verdicts, EvName overflow fixed, FMV/inkbox/stress/textcover left; 22nd: re-tour of the 17 graphics scenes, ~100 verdicts, help-bar fix; phase 7 done 2026-11-21, 16th worker; phase 6 done pending review: the reviewer
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
- **Phase 8 progress (2026-11-21, 19th worker):** tour COMPLETE: all 66 scenes in `work/qa/tour` on build
  da353c51 (tgs_end's proof frame is blank as before; the scene runs). `tools/qa_sheets.py work/qa/tour` writes
  `qa_sheet*.png` per scene (frames from arrival-300, near-duplicates dropped, full size 3x3), and
  `qa_gate.py init work/qa/manifest.tsv work/qa/tour --build build/fd2_en.bin --glob "qa_sheet*.png"` made a
  186-sheet manifest. Verdicts so far: `work/qa/verdicts/w19_001.tsv` (13 sheets: title*, name_entry, load_save p1,
  omake, album_3 p2, omake_cg p2, demo_menu, prologue p1, tutorial p1, heaven p1, heaven_status p3). Also looked at
  the final frames of heaven_*/map_*/exam/visit/year1/maseki/load_edited (`work/qa/p8/finals_sheet*.png`): fine
  except below. **Fixed:** (1) name entry: pro.bin hard-coded the default ラビエル as kana-grid indices (+0x5E4,
  at 0x8009BF80 and 0x8009D7F4); `asm/pro.asm` (new, `build.patch_pro`) sets "Raviel" and points the commit
  memcpy(0x8007F480, entry+0x612, 12) at `asm/name.asm` (EXE FREE 0x8001FC00), which turns full-width Latin into
  pair codes (model + tests: `font_en.name_to_pairs`, `tests/test_name.py`); prologue now says "Raviel, welc..."
  (`work/qa/p8/name/`). (2) fixture cards: name set to Raviel (save header indices + stored name at data +0x2DC);
  load list shows "Raviel". (3) heaven Move button "St. Azaria Palace" clipped both ends: budget 14 in
  `tools/widths.tsv`, now "Azaria Palace" (polish.md). Not bugs: visit_01.ssb lines "29-00" etc. are the
  original's placeholder ids (JP ２９＿００). **(superseded: build 47e8c2eb has these fixes, 20th worker) build/fd2_en.bin was da353c51; the fixes
  are in `build/fd2_name.bin` (e967f0c9...) only** until the next `build.py`; after all fixes, rebuild fd2_en,
  re-tour (`warp.py --all -j 1`), `qa_sheets.py`, `qa_gate.py init` again (unchanged sheets keep their verdicts).
- **Phase 8 progress (2026-11-21, 20th worker):** **G8 done:** 88 battle name plates in English
  (`gfx/plates.tsv`, rows 0-80 = Name_000..NAME_080 with mixed-case entry names, 81-87 = Name_B00..B06 heroes;
  `tools/plates.py check|sheet` renders them with fonts/font6, proportional, into the build; `tests/test_plates.py`).
  Seen in battle: "Titan", "Fein" (`work/qa/p8/plates/b1.png`). 天竜 plate = "Heaven Dragon" (70 px glossary form
  does not fit 64; polish.md). Build **47e8c2eb** (name fix + plates). The white squares under battle sprites are in
  the original too (`work/qa/jp/battle`, warp on the JP disc): added to `docs/visual-qa-brief.md` standing non-bugs,
  with the other known non-bugs and the open G-rows. Credits sheets = the JP FMV staff roll (G15), all 13 an issue
  until the FMV work. G4 banner texts read at zoom (`work/qa/p8/g34.png`): 逃走 戦闘から退却, 連撃 攻撃を3回繰り返す,
  小回復 HP100回復, 透明 敵の攻撃を3回無効化, 大回復 HP完全回復, 鉄壁(?) 特殊能力カバー上昇; G3 tags パラライズ ポイズン
  コンフュ 石化 スリープ チャーム. an_mag_0.tim (GRPDATA_0057) is 4bpp with 16 CLUTs and the text is drawn in another
  CLUT than 0 (clut 0 shows it magenta/cyan): find the CLUT the battle uses (VRAM dump in a battle) before redrawing;
  tools/tim.py decodes only, needs a 4bpp encoder. **Re-tour on 47e8c2eb was killed for low memory** (host had other
  projects' emulators running) after 46 of 66 scenes: `work/qa/tour/` has album_*, demo_menu, ev_*, exam, heaven_*,
  load_*, map_*, maseki, name_entry, omake*, prologue*, title*, tutorial, visit, year1; still to run: battle,
  battle_3152, battle_h1-h6, credits, end_* (9), game_over, game_over2, tgs_end (`warp.py SCENE.. --cue <abs>/build/
  fd2_en.cue --out-dir work/qa/tour`). The old tour (da353c51) is in `work/qa/tour_da353c51`. Then `qa_sheets.py
  work/qa/tour`, `qa_gate.py init ... --build build/fd2_en.bin` and verdicts.
- **Phase 8 progress (2026-11-21, 21st worker):** re-tour on 47e8c2eb finished: all 21 remaining scenes OK
  (tgs_end blank as known), so `work/qa/tour` has all 67 scenes on 47e8c2eb. **G3 + G4 done:** `tools/banners.py`,
  `gfx/banners.tsv` redraw an_mag_0.tim (GRPDATA 0057) in palette-index space (valid for all 16 CLUTs, no VRAM dump
  needed): tags Paralyze Poison Confuse Stone Sleep Charm (new narrow `fonts/font_tag.txt`, 36 px sprites), banners
  "Flee  Leave battle", "Minor Heal  +100 HP", "Major Heal  Full HP", "Combo  Attack 3 times", "Vanish  Nullify 3
  attacks", "Blessing  Skill cover up" (pills keep their width); `tim.with_pixels` (4 bpp writer). **G10 done:**
  `tools/album.py`, `gfx/album.tsv`; the album's atlas rects came from RAM dumps (`tools/debug/ramdump.lua`, new
  `tools/sprites.py` lists GP0 sprite packets; dumps in `work/qa/p8/album_ram/`), text in label14 (DejaVu 14 px,
  copied from ../favorite-dear-en with `tools/labelfont.py`) / font6 / font_tag; cuts in polish.md. Tests
  `tests/test_banners.py`, `tests/test_album.py`; check.py 65 passed, lint 0. **Build 2e18e967** (graphics only vs
  47e8c2eb: GRPDATA 0057 + 1454), smoke OK. NOT yet seen in game: the re-tour of omake, omake_cg, album_2-8, battle,
  battle_h1-h6, battle_3152 on 2e18e967 was killed by the host for low memory (the first game's project had two
  emulators running) before any scene finished. The G3/G4 sprites may not show in the warp battles at all (they
  appear on status effects / skills): if not, add a battle route that casts a skill, or waive with the redraw sheet.
- **Phase 8 progress (2026-11-21, 22nd worker):** re-tour of the 17 scenes on 2e18e967 (`work/qa/retour_2e18.log`).
  `qa_sheets.py` re-run on the other 50 scenes and `qa_gate.py init` (191 sheets). Sheets with identical pixels
  share a verdict (29 duplicates: every heaven_*/map_* scene opens with the same two map day-cycle sheets).
  Verdicts in `work/qa/verdicts/w22_001..007.tsv` (~100 sheets): name_entry, prologue*, heaven*, load_*, map*,
  ev_* (not ev_fe), exam, maseki, year1, tutorial, title_omake, visit, game_over*, end_raphael, end_cecia.
  **Fixed:** heaven help bar is a fixed ~210 px pill (29 letters fit): "Go to another palace in the Heavens" was
  clipped both ends -> "Go to another palace"; "Borrow fairies, get information" -> "Borrow fairies, hear the
  news"; budget 30 in `tools/widths.tsv` for rfd2.8009CFC0-D0EF (lint 0). Not bugs: the end_* warps all play
  Fein's .end narration (picked by the fixture save, not by the warped ending); after "Save clear data? Yes" the
  game asks to LOAD clear data first (ed.8009B704, original design). **Issues left:** G14 opening movie DEMO.STR
  captions Japanese (game_over2 sheets 2-4 reboot into it), G15 credits (13 sheets). ev_fe's frames were left as
  raw `.psx` dumps by the earlier killed run: re-warped on 757dbe6a, sheets made, verdict owed. Polish gained the
  pair-glyph gap "Ravi el" and the help-bar cuts. The re-tour of the 17 scenes finished OK (all arrived).
  **Build 757dbe6a** (help bar), check.py 65 passed + lint 0, smoke OK; heaven_move re-warped on it shows "Go to
  another palace" in the pill (`work/qa/p8/w22/heaven_move/qa_sheet_3.png`, verdict `fixed`).
- **Phase 8 progress (2026-11-21, 23rd worker):** the 17 re-toured scenes had frames but no sheets: `qa_sheets.py`
  made them, `qa_gate.py init`, and every one of the 191 sheets now has a verdict (`verdicts/w23_001.tsv`, 99 rows):
  `check` = 0 without a verdict, 14 not ok, all FMV (G14 DEMO.STR captions x3, G15 ENDING.STR staff roll x11).
  **Fixed:** fairy reports splice ＜イベント名＞ as whole pair glyphs, so a 21-22 letter EvName title had no zero pair
  and ran into the next record ("Mountain Monster Bird   Giant Centipede Swarm", battle_h4; JP checked on the original
  disc, `work/qa/jp/battle_h4`) and an odd title ended in a space pair ("Giant Spider Plague ."). All 89 titles are
  now even and <= 20 letters (48 reworded, e.g. "Roc of the Mountains", "Giant Spider Swarm", "X Under Attack" for
  侵攻 towns); `msg.py` asserts 20, `lint.py` fails odd/long EvName rows. Re-warped h4/h5 on the new build: fixed.
  Same class, not fixed (polish.md, needs a re-pairing hook after rfd2 0x800BF280): odd hero names "Cecia -sama has
  resolved", odd town names before "." Battle black boxes over sprites (battle_h1) predate the plates (tour_da353c51):
  not ours. **Build 68d392eb**, check.py 65 passed + lint 0.
- **Phase 8 progress (2026-11-21, 24th worker):** **G14 done:** the 7 DEMO.STR captions are English, re-encoded
  in place. `tools/mdec.py` is a PS1 STR v2 codec (2336-byte sectors, chunk headers, MPEG-1 B.14 VLC, column-major
  macroblocks Cr Cb Y0-3): parse + reassemble is byte-identical (`tests/test_mdec.py`), and `rebuild` re-encodes
  only the touched macroblocks (the other blocks keep their original bits). **Gotcha:** every frame ends with a
  10-bit 0x1FF end code; without it the game's player quits the movie (first build went black, then straight to
  the title). `tools/fmv.py` + `gfx/fmv.tsv` (movie, frame span, sharp ref frame, region, size, mode, line anchors
  `at`, clean frames, jp, en): per frame the JP layer is fitted as alpha x blur(ref) (joint fit where captions
  overlap) and the English is drawn with the same alpha/blur, so it fades and smears like the original. Modes:
  black (warm R-B signal, inpaint), scene (box rebuilt from caption-free frames moved by a local phase-correlation
  shift, gain-matched; stained-glass pan), box (inpaint the whole tight box; morphing clouds). Font Crimson Text
  SemiBold Italic (OFL, `fonts/crimson/`, docs/fonts.md). `build.py` adds `fmv.changes()` (cached in build/fmv/,
  ~3 min to re-encode DEMO). Emulator cold boot shows every caption (`work/qa/p8/demo/`, `work/qa/p8/demo_emu.png`;
  movie frames f1830-f4000). Minor: the feather is clipped for 2-3 frames where it crosses an old caption (polish).
  **Build 6376499a**, check.py 68 passed + lint 0. Movie frame numbers: `python tools/mdec.py info X.STR`; all
  frames as PNG: `python tools/str2352.py X.STR work/fmv/X.raw; ffmpeg -f psxstr -i work/fmv/X.raw dir/f%04d.png`.
  **G15 plan (next worker):** ENDING.STR = 4218 frames (`work/fmv/ending/t01.png` overview). (a) caption
  悲しみはよろこびに場所を譲り / 勇者は希望の礎となる── on black near the start: one `gfx/fmv.tsv` row (black mode).
  (b) the 純白の預言者 logo: leave (D-style: the title logo stays JP everywhere). (c) the staff roll scrolls on the
  black right half beside a gold ornament panel on the left: measure the scroll speed and the black text column,
  transcribe every credit (role + name), romanize (cast names: check spellings of the well-known voice actors;
  staff: Hepburn, note uncertain readings in docs/polish.md), and add a "roll" mode to fmv.py that paints the
  column black and draws one tall English strip offset by the scroll per frame (no fit needed). Read the frames in
  chunks (decode once to work/fmv/ending_all/, sheets of ~10 frames), not one by one.
- **Phase 8 progress (2026-11-21, 25th worker):** **G15 written, NOT YET BUILT.** Ending caption: two `gfx/fmv.tsv`
  rows, new mode `white` + `dx` column (white letters drifting sideways: line 1 +0.325 px/frame, line 2 -0.444;
  "Sorrow gives way to joy," / "and the hero becomes a spear of hope—"; JP is 槍 "spear", not 礎). Staff roll: new
  `tools/roll.py` + `gfx/roll.tsv` (143 lines: strip box, style head/crole/srole/name/name2/co/keep, English;
  Western order, no macrons, game-1 spellings reused from `../favorite-dear-en/trans/staff/en.tsv`). Measured: roll
  scrolls exactly 1.5 px/frame from frame 330 to 4114 then holds; the gold panel 0.19 px/frame; lines centred on
  x=160, half over the panel. Each JP line box is refilled from panel-aligned frames +-8..96 away where that spot
  is text-free, the English strip is drawn at 2x and cut at the half-pixel offset, alpha follows the JP fade.
  Previews (`tools/fmv.py preview ENDING.STR a b`) look right: `work/fmv/ending/cmp1.png` (cast/staff), `cmp2.png`
  (start, feather, NEC/SOFIX card, fade-out), `cmpc.png` (caption). `tests/test_roll.py`; check.py 71 passed + lint 0.
  **The `fmv.py build` run (DEMO + ENDING re-encode, ~3900 roll frames, cache key now includes roll files so DEMO
  re-encodes too) was killed by the host for low memory** before writing anything to build/fmv/. Next: with no
  other emulators/projects running, `python -X utf8 tools/fmv.py build` (if memory is tight, lower the `_rgb`
  eviction window in `Movie.build`, 120 frames x 1.7 MB float64, or store rgb as uint8), then `build.py`, smoke,
  `warp.py credits --cue <abs>/build/fd2_en.cue`, re-sheet credits (+ end_* / game_over2 if they include FMV) and
  write verdicts; the 13 credits sheets are the only `not ok` left besides G14's 3 (now fixed, re-verdict).
- **Phase 8 progress (2026-11-21, 26th worker):** `fmv.py` frame cache is float32 now (the float64 cache got the
  25th worker's run killed); DEMO + ENDING re-encoded (~17 min; 1014 ENDING frames drop AC levels <= 1..4 to fit
  their sectors, `work/fmv/log/build.txt`). **Build e2206009**, check.py 72 passed + lint 0, smoke OK. `warp.py
  credits` on it: the roll is English in game (`work/qa/tour/credits`, 13 sheets; pages 1/4/8/13 read, ok, in
  `verdicts/w26_001.tsv`; pages 3,5,6,7,9-12 still need reading). qa_gate manifest re-inited with `--glob
  "qa_sheet*.png"` (without it init adds every sheet.png: 157 junk rows, removed). **Choice indent:** the menX_*
  《はい》/《いいえ》 options are indented one cell under the question in the JP (not for a cursor: the highlight
  bar spans the box, `work/qa/jp/choice/z2.png`); `trans/en` had "  Yes" but `batches.wrap_lines` dropped leading
  spaces; it keeps them now (`tests/test_wrap.py`), 14 menX rows indented. New scene `choice_menx` (event
  menX_Ce01.ssb, hold): the choice is up at ~f010430 on the build and is then auto-answered ~f010460 (shoot with
  `--shot-every 10 --frames 10560`). **Merge was not stable:** the 23rd worker's EvName rewordings were edited in
  script/ only, so `batches.py merge` reverted them; they are now in `trans/en/b053.tsv` too, and merge copies them to
  their duplicate JP rows (op.* OMAKE titles, eiev05.0002). **Inkbox** (`docs/inkbox.tsv`, rects from the new
  `tools/buttons.py`): heaven Save/Load, heaven menu, card Slot 1/2, Heroes/Status pass; **FAIL: odd-length centred
  button labels sit 3 px left** ("Fairies" 11/19 px in the 70-px map/heaven-status button, "Angel", "To Heaven"
  5/13, heaven Move "Azaria Palace"/"Emilia Palace" 1/9). Cause: the game centres by byte count and a label is
  pair codes, so an odd label carries a blank half-pair at its end. Lead: label reads on the original
  (`work/qa/p8/watch_btn/map_menu/log.txt`): BIOS strlen, then EXE 0x8002E9A8 (a0 dest, a1 str; returns 0 for
  an odd strlen, converts the string into glyph codes at 0x8007F480, max 0x30); its only EXE caller 0x8002D6C8 is
  a generic line writer (strlen in s6), so the x maths is further up: break there and walk RA to the button
  routine, then either hook it (x += 3 when the last pair ends in a space) or reword to even lengths (as EvName).
- **Phase 8 progress (2026-11-21, 27th worker):** **Gate:** credits pages 3,5-7,9-12, choice_menx and the re-warped
  game_over2 (DEMO captions English in game, `work/qa/tour/game_over2`) read: `verdicts/w27_001.tsv`; `qa_gate.py
  check work/qa/manifest.tsv work/qa/verdicts` = 193 sheets, 0 not ok. **Odd-label centring fixed:** button text width
  is set by string renderer 1 (EXE 0x8002C080, text w = cell x strlen x 2 at obj +0x18; the button helpers 0x8002FEDC
  / 0x8002FFDC centre on it); `asm/font.asm` `trim_hook` (at 0x8002C218) drops one byte when the last pair's right
  letter is a space. Fairies 14/16 (was 11/19), To Heaven 8/10, Azaria/Emilia Palace 4/6, help bar centred too;
  other renderer-1 scenes unchanged pixel for pixel except those (`work/qa/p8/w27/cmp_*.png`). Rows in
  `docs/inkbox.tsv` (all ok; Angel 20/24 is the narrow l glyph). **Build 2401529b**, check.py 72 passed + lint 0.
  **Stress saves:** `tools/stress.py` writes work/saves/stress_{kana,wide,short}.mcd from fd2_edited.mcd (6-katakana
  name = widest, 99 h play time, 9999 days; WWWWWW; 1-letter A); scenes stress_* (title load list, loaded heaven,
  Data -> Save list); all fit, `qa_gate.py check work/qa/stress_manifest.tsv work/qa/stress_verdicts` = 6/6 ok. Gotcha:
  header name slots are 6 grid indices padded with FE (zeros show as "A"). After a load the heaven menu ignores
  up/down (circle opens Data), so the angel status panel isn't on the stress route (covered by heaven_status_angel
  and the 12-letter name budget). Only the angel name and header numbers are player-variable; in-game state (items,
  stats) is not mapped in save.py, so no full-list / max-stat saves (fixed lists: 7 heroes, 8 fairies).
  **textcover:** `tools/debug/textcover.lua` fixed: LuaJIT sign-extended addresses (FFFFFFFF800D77B8), event warps
  logged the host name prologue.ssb (now the warp's EVENT / SWAP_TARGET), overlays logged as FILE lines when the
  word at 0x8009B4B0 changes (6 op, 7 rfd2, 8 Battle, 9 ed, 10 pro). Pilot `warp.py --event men1_Ro01.ssb --lua
  tools/debug/textcover.lua --debugger --cue "<abs>/rom/Favorite Dear - Junpaku no Yogensha (Japan).cue" --out-dir
  work/qa/cover`: ~100 s per run, men1_Ro01 36/38 rows (the 2 left are the other choice branch / a speaker tag),
  ovl 32: partial, so loads don't fake coverage. `textcover.py work/qa/cover --missing work/qa/cover_missing.tsv`.
  **Next for textcover:** run every ssb event (288 files in script/ssb; ~8 h at -j 1, run in background batches of
  ~30 `--event` args into work/qa/cover), plus the existing scenes (`--all`) with the hook; then MSG (15130 rows:
  fairy reports, chats, battle lines) and EVX (5834) need scenes or reasoned waivers in docs/text_unshown.tsv (not
  created yet); EXE strings are not counted.
- **Next (phase 8):** remaining done-when items: (1) G15 FMV (G14 done, see above): English captions for DEMO.STR (3 caption cards in
  the opening) and the ENDING.STR staff roll + "悲しみはよろこびに場所を譲り 勇者は希望の槍となる──" caption (D3: credits
  in English; default plan re-encode the MDEC frames with English text, see Waiting on the user); (2) `inkbox.py` on
  choice / centred menu boxes (menX_* Yes/No, heaven buttons); (3) stress saves (longest names, full lists, max
  numbers) with menu sheets; (4) `textcover.py` exit 0; (5) final full re-tour on the final build (`warp.py --all -j
  1`), `qa_sheets.py`, `qa_gate.py init`, verdicts for changed sheets only. Carried items below still apply.
  Older next list: re-tour on 2e18e967 the 17 scenes above (`warp.py omake omake_cg album_2 .. album_8 battle
  battle_h1 .. battle_h6 battle_3152 -j 1 --cue <abs>/build/fd2_en.cue --out-dir work/qa/tour`, with no other
  emulators running); the other 50 scenes' text is identical between 47e8c2eb and 2e18e967 (only GRPDATA 0057/1454
  changed), so record that with the manifest. Then read the remaining sheets (`qa_gate.py todo work/qa/manifest.tsv work/qa/verdicts --size
  20 --out-dir work/qa/chunks`; ~1k tokens per sheet, so ~60 sheets per worker; write `verdicts/w<N>_NNN.tsv`):
  battles (G3/G4/G7/G8 graphics likely still JP), credits (13 pages, D3: English credits = ENDING.STR FMV work),
  the 7 endings, game over, tgs_end, ev_*, exam, year1, maseki, end_cecia*. Graphics left: G9 if used (fileslog
  check), G7 glyph strips (find the user), and the FMV captions/credits (G14/G15).
  Earlier list: QA in the emulator per the skill's phase 8 done-when (tour sheets + visual-QA verdicts via
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
