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
| セレニス | Serenis | | Fein's wife, Irene's elder sister; 帝国の魔女 "the Empire's witch", possessed by a devil | |
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
| クロイツフェルド | Kreutzfeld | | great noble house; the father is chancellor, Alberic is the son | |
| カイゼル | Kaiser | | General Kaiser (将軍), imperial officer (laev05) | |
| セネカ | Seneca | | Rudiere's elephant, "she" (パオーン "Pawoooo!", パオー "Pawooo!") | |
| ユーグ | Hugues | | King of Legrance, Rudiere's elder brother (Hugues Legrance), assassinated loev10 | |
| リンクス | Lynx | | fairy, boyish (僕) | |
| ローザ | Rosa | | fairy (formal, composed) | |
| フロリンダ | Florinda | | fairy; calls herself フロリン "Florin" | |
| フロリン | Florin | | | |
| シェリー | Shelly | | fairy | |
| リリィ | Lily | | | |
| アクイラ | Aquila | | fairy | |
| シータス | Cetus | | fairy, オレ, casual | |
| レーパス | Lepus | | fairy, very formal | |
| ティタニア | Titania | | fairy queen; "Titania-sama" | |
| ガブリエル | Gabriel | | archangel (game 1's superior) | |
| 副教皇 | Vice Pope | | Ecclesia, Rocus's superior (name tag roev01_01) | |
| ランゲラック | Langerack | | Clarence Langerack, "Viper" (ヴァイパー), the gambler who beats Rocus (roev03-roev16) | |
| エリアス | Elias | | first Pope, founder of Ecclesia | |
| ゼアム | Zeam | | Archbishop Zeam (name tag "Zeam", roev09_02) | |
| アズリア | Azuria | | Archbishop Azuria (name tag "Azuria") | |
| ライアン | Ryan | | Cardinal Ryan (name tag "Ryan") | |
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
| バレーゼ | Valese | | country; its church in Ilyus shelters the clergy after the Holy City falls | |
| イリュウス | Ilyus | | town in Valese | |
| アザリア | Azaria | | 聖アザリア宮 the Palace of St. Azaria (Raphael's seat) | |

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
- Rudiere's route (b023-b026): 大公 "Grand Duke" (Rudiere's title), 宰相 "Chancellor" (Kreutzfeld, Grosain's),
  エンディミオン = Endymion, the young Grosain emperor (余 "we" in audience, "I" in private); 旧東方王国 "the old
  Eastern Kingdom"; ルディの母 tag "Rudi's Mom" (he calls her "Mom"); 王の側近 "King's Aide"; Savio = the armored man
  in cursed armor, Savia = the girl who frees Rudiere. Chapter labels over 12 letters get a shorter title
  (第10節「王暗殺」 "Regicide").
- Gift items (men3_*, b030-b031; the EXE item list at SLPS.80020Cxx/800212xx must match in phase 7): ハシバミの実
  hazelnuts, サンザシの実 hawthorn berries, オリーブの実 olives, 花束 bouquet, 森のしずく Forest Dew, 銀のナイフ silver
  knife, 銀のてい鉄 silver horseshoe, ゾンビパウダー zombie powder, 銀のロザリオ silver rosary, 銘刀のつば guard of a
  famous sword, ヤドリギの枝 mistletoe sprig, 羽ペン quill pen, クマのぬいぐるみ teddy bear, 古い腕輪 old bracelet,
  魔導書 grimoire, ギルドの護符 Guild amulet, 麦わら帽子 straw hat, 命の水 Water of Life (it's liquor), 魔導士のローブ
  mage's robe, 銀の指輪 silver ring, タラブローチ Tara brooch, 決闘用の手袋 dueling gloves, 騎士道の教本 manual of
  chivalry, クラダーリング Claddagh ring, 銀のレイピア silver rapier, シルクのハンカチ silk handkerchief, 象の置物
  elephant figurine, 象牙のナイフ ivory knife, 珍しいスパイス rare spices, 魔除けのクリス warding kris, 聖水 holy water,
  聖者のローブ saint's robe, 年代物のワイン vintage wine, タローカード tarot cards, 金のメダイユ gold medallion.
  戒律 "precept(s)". menX 同行しますか？ "Accompany <name>?" with "  Yes" / "  No" (full-width space -> two spaces).
- Name tags: 柄の悪い男 "Thug", 酒場の女達 "Tavern Girls". Rocus to the angel early on: formal and flirty ("my
  beautiful angel"), crude when angry (俺, てめえ). ミカエル様 "Lord Michael" like "Lord Raphael".
- Rocus's route (b034-b037): 教皇 "Pope" (教皇候補 "candidate for Pope"; Clarence's mocking 教皇さま "His Holiness"),
  大司教 "archbishop", 枢機卿 "cardinal", 宝玉 "the sacred jewel" (= the Church's Demon Stone), 秘宝 "the treasure",
  癒しの手 "healing hands" (the mark of the Pope); 蛇君/毒蛇君 "Mr. Snake"/"Mr. Viper". Name tags: ロクスの知人
  "Rocus's Pal", 男の声 "Man's Voice". Debug labels ０１＿００ (visit_01) -> "01-00" (no _ in the font).
- Scene labels like フェイン・０９節 / フェイン・スカウト二回目 (name kind, 12 letters): "Fein Part 9", "Fein Scout 2".
