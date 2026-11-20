# Synopsis and chapter list

For translators and story reviewers. Names follow `glossary.md`. Written after phase 6 from the translated
script; extend it when a story pass finds something missing.

## Premise
The player is a newly made angel (＄＄＄＄＄＄, gender-neutral in English) sent by the archangel Raphael to Arcaya,
the world below, because the Pure White Prophet's prophecy says a thousand-year-old evil is returning: the Demon
Stones are being stolen and the Grosain Empire, backed by its witch Serenis (possessed by a devil), is invading its
neighbours. The angel recruits seven heroes, directs them through incidents, and is helped by eight fairies (Rosa,
Florinda, Shelly, Lily, Lynx, Aquila, Cetus, Lepus) who scout towns and file reports. The last enemy is Beelzebub.
Ending: in the Heavens (Raph_end), with a branch where the angel gives up wings to stay human with a hero.

## Heroes and their routes (file prefixes)
- **Fein** (feed01, Feev01-31): ex-imperial mage hunted by his own guilt; Serenis was his wife, Zig saved him in his
  past. Guild masters Greza, Reijiher, Rand; the Grand Lodge in Alkmaar. Ends confronting Serenis's death (Feev21,
  Feev24) and his choice to live.
- **Irene** (eied01, eiev01-30): young mage raised in her grandfather's tower on Bremes Isle with her owl Vesta;
  Serenis's younger sister. Snowball fight (eiev18), the Grand Lodge attack, Serenis's death.
- **Rocus** (roed01, roev01-25): cynical priest with healing hands, at odds with the church hierarchy (Pope, Vice
  Pope, cardinals). Clarence "Viper" Langerack steals a Demon Stone; Rocus is exiled from the Holy City,
  the council in Ilyus, the drunk-angel night (roev12), confession and ending; Ion's death.
- **Clive** (cled01, clev01-30): terse vampire hunter, pupil of Irwin, hunting Ravenruft; the Forest of the Holy
  Mother (clev13), Vastir become a Demon Lord, Dark Clive and the last battle; the boy Ion and his beasts.
- **Leyla** (laed01, laev01-25): knight of Grosain, Leyla Vigrid; her father killed in a duel by Alberic of the
  Kreutzfeld house; General Kaiser's duel and Alberic's breakdown.
- **Rudiere** (loed01, loev01-27): Legrance prince travelling as "Rudi Trier" with his elephant Seneca; his brother
  Hugues's assassination, the assassin band of Savio and Savia, the Grand Duke and Chancellor.
- **Cecia** (ceed01, ceev01-24e): girl of the Reyforia Forest; Ion, Serenis, Beelzebub's last battle and the
  Michael/Raphael rescue.

## Chapter list (story order for the story pass)
1. Prologue: pro (quiz), prolog, alkaya (each fairy's intro tour of Arcaya), op gallery captions.
2. One chapter per hero: their ssb events (`xxed01`, `xxev*`) interleaved with their EVX battle scenes and the
   BTL_EVT lines for that hero (bank N = hero N: 0 Fein, 1 Clive, 2 Rudiere, 3 Rocus, 4 Irene, 5 Leyla, 6 Cecia).
3. Angel calls: men1_* (summoned), men2_* (talks), men3_* (gifts), menX_* (refusals), per hero.
4. Heaven and fairies: HVN_Msg00 (Raphael), FryMsg0-7 (fairy reports), Y01ev-Y08ev (fairy days off), T_Msg00/01.
5. Hub dialogue: BMsgQ000-006 / BrvMsgQ (hero chat), BVisit, GenAnsw/GenNG, MssReq/MssAns, NASI_*, EMP_*, items.
6. Endings: Raph_end, the 21 `.end` epilogues, ed (clear-data prompts).
