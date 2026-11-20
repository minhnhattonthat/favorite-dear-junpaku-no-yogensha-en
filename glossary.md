# Glossary - Favorite Dear: Junpaku no Yogensha

Binding for every translator and reviewer. Only the controller edits this file. `tools/batches.py check` enforces the
tables: a row whose JP holds a term must contain the EN form (first word group before " ("), and never a spelling
from the Avoid column. Series conventions come from the first game (`../favorite-dear-en/glossary.md`).

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics (D1): kept, hyphenated, on personal names: さん "-san", くん/君 "-kun", ちゃん "-chan", 様/さま "-sama",
  殿/どの "-dono". Titles that are words stay English: 王子 Prince, 姫 Princess, 卿 Lord. Address nouns stay
  English: 天使様 "Angel" (capitalised as an address), 勇者様 "the hero", お父様 "Father". Name order: Western.
- Romanisation (D2): no official English; Western-style spellings of the katakana names, angel/demon names in their
  standard English forms (Raphael, Beelzebub, Satan, Morax, Balam). Names shared with game 1 keep its spelling.
- Credits: English (D3). Abbreviations: full names and terms, engine work first (D4).
- Register: warm fantasy drama, natural modern English, no archaisms except for the higher angels and demons
  (formal, measured). Interjections and SFX: English equivalents (うふふ "Hehe", ククク "Heh heh heh", えっ "Huh?",
  キシシシシ "Kishishishi" for the gremlin-like laugh, monster cries as "Gyaaah!").

## Style rules
- Punctuation: 「」 -> "...", 『』 -> '...', …… / ・・・ -> "...", ！？ -> "?!", （...） inner monologue -> (...),
  《...》 choice -> <...> is not in the font: write choices as plain text in the same layout (《聞く》 -> "Listen").
  Font: printable ASCII except # $ < > @ [ \ ] ^ _ ` { | }, plus … ♪ ♥. ～ -> "~".
- The player's name is ＄＄＄＄＄＄ (keep it exactly; it draws up to 12 letters).
- The player is the angel: keep every line about the angel gender-neutral (no he/she) unless the line only plays for
  one gender.
- Common terms: 天使 angel; 勇者 hero (the angel's champion); 妖精 fairy; 堕天使 fallen angel; 天界 the Heavens;
  地上界 the surface world / the world below; 魔族 demon(s); 魔物/モンスター monster; 魔王 Demon Lord; 悪魔 devil;
  預言者 prophet; 純白の預言者 the Pure White Prophet; 魂 soul; 相性 compatibility; 経験 experience;
  ギルド guild; アイテム item; レベル level; ストレス stress; イベント event.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| フェイン | Fein | | hero, Fein Lu Lugus | |
| ルー・ルグス | Lu Lugus | | | |
| アイリーン | Irene | | hero, Irene Tirnag | Eileen |
| ティルナーグ | Tirnag | | | |
| ロクス | Rocus | | hero, Rocus Las Flores | |
| フロレス | Flores | | | |
| クライヴ | Clive | | hero, vampire hunter, Clive Saingrent; terse, 俺 | |
| セイングレント | Saingrent | | Clive's surname | |
| レイブンルフト | Ravenruft | | king of the vampires, Clive's enemy | |
| アーウィン | Irwin | | Clive's master, a vampire hunter | Erwin |
| ヴァイパー | Viper | | | |
| ティタン | Titan | | enemy faction occupying a town (clev16) | |
| ジグ | Zig | | saved Fein in his past | |
| レイラ | Leyla | | hero, Leyla Vigrid | Layla |
| ヴィグリード | Vigrid | | | |
| ルディエール | Rudiere | | hero, Rudiere Trier Legrance; ルディ "Rudi" | |
| ルディ | Rudi | | | |
| トライア | Trier | | | |
| レグランス | Legrance | | | |
| セシア | Cecia | | | |
| セレニス | Serenis | | | |
| クラレンス | Clarence | | | |
| ラファエル | Raphael | | archangel | |
| ミカエル | Michael | | archangel | |
| イオン | Ion | | | |
| エンディミオン | Endymion | | | |
| アルベリック | Alberic | | | |
| サヴィオ | Savio | | | |
| サヴィア | Savia | | | |
| ディアナ | Diana | | | |
| レイフォリア | Reyforia | | | |
| リベザル | Ribezal | | | |
| ウェスタ | Vesta | | Irene's owl (female) | Westa |
| マスター | Master | | name tag for the Grand Master (eiev13_02) | |
| ライノール | Raynor | | the Grand Master, Zig's senior apprentice; Fein calls him 老師 "Elder" | |
| レーアン | Lehan | | a regional guild master (Master Lehan) | |
| ゼルン | Zern | | Marquis Zern (ゼルン侯/候) | |
| ラビエル | Raviel | | default angel name in the preview version (game 1 spelling) | |
| リンクス | Lynx | | fairy, boyish (僕) | |
| ローザ | Rosa | | fairy (formal, composed) | |
| フロリンダ | Florinda | | fairy; calls herself フロリン "Florin" | |
| フロリン | Florin | | | |
| シェリー | Shelly | | fairy | |
| リリィ | Lily | | | |
| サタン | Satan | | | |
| ベルゼバブ | Beelzebub | | | |
| ノスフェラトゥ | Nosferatu | | | |
| モラクス | Morax | | | |
| バラム | Balam | | | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| アルカヤ | Arcaya | | the world below | Alkaya |
| イェラセル | Yerasel | | the Yerasel continent | |
| カヴァキア | Kavakia | | the Kavakia peninsula | |
| インフォス | Infos | | game 1's world | |
| ドライハウプ | Dreihaup | | Lake Dreihaup (湖), largest lake on Yerasel | |
| デルフィニア | Delphinia | | Mount Delphinia (山) | |
| アルクマール | Alkmaar | | town/city with the Guild's Grand Lodge | |
| グローサイン | Grosain | | the Grosain Empire (帝国) | |
| 六王国 | Six Kingdoms | | | |
| バーゼル | Basel | | country; Alkmaar is in Basel | |
| レフカス | Lefkas | | where the Demon Stone was kept before Alkmaar | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| グランドマスター | Grand Master | | | |
| グランドロッジ | Grand Lodge | | | |
| 聖母 | Holy Mother | | Cecia's order; 聖母の森 the Forest of the Holy Mother | |
| 魔石 | Demon Stone | | shattered into three, one per ancient hero | |
| 天竜 | Heavenly Dragon | | | |
| 紅月王 | Crimson Moon King | | | |
| 大天使 | archangel | | the archangel / Lord Raphael | |
| ウォーロック | Warlock | | sword-trained guild mage (Fein) | |
| 黒衣の魔導士 | Black Mage | | name tag, Feev01_01 | |

## Decisions from earlier batches
- Chapter labels `xxNN.0012` (第N節「...」, ...エンディング): title only, no number ("Cursed Soul", "Confession").
- Choices 《...》: plain text ending in `{n}`. Lines with a wrong speaker column (the angel's line tagged as a hero,
  or the reverse) are translated by content.
- Gendered angel variants exist (あれ？/あら？ copies, 女同士, 悪い男 vs 好きな女の子): translate each copy for its gender.
- A source row with five ＄ (eiev11.079A, eiev12.1530) is written with the full six.
- ギルド is "the Guild" (capitalised, the mages' association); ロッジ "lodge" ("Guild lodge", "the Grand Lodge").
  ディアナ様 is "Diana-sama" (D1), never "Lady Diana". 老師 (Fein to Raynor) is "Elder". 聖都 "the Holy City".
- Scene labels like フェイン・０９節 / フェイン・スカウト二回目 (name kind, 12 letters): "Fein Part 9", "Fein Scout 2".
