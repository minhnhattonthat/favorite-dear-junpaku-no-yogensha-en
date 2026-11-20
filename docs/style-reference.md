# Style reference: voices

Binding for translators and reviewers, beside `glossary.md` and `docs/translator-brief.md`. One row per recurring
speaker: the Japanese markers that carry the voice and the English devices that carry them over. A line that reads
neutral where the JP has these markers is **voice flattening, rated Important** in a review, not Minor.

Built 2026-11-21 from the translated script (`python -X utf8 tools/voices.py` lists speakers and marker counts;
`tools/voices.py SPEAKER N` prints N paired examples). Untagged files (fairy reports FryMsgN, BMsgQ chats, mission
replies) follow the same rows by their speaker. The player (the angel) is never gendered: "they", "Angel".

## Heroes

| Speaker | JP markers | EN devices | Paired example (JP / EN) |
|---|---|---|---|
| Fein (フェイン), mage, grim and proud | 俺, お前/貴様 to foes, 君 to the angel, ～だろう, ゆるさんぞ | firm, clipped, contractions; cold to enemies, plain warmth to the angel; no slang | 君も俺たちと気持ちは変わらない… / "Now I know for certain that your heart is no different from ours." |
| Clive (クライヴ), vampire hunter, terse | 俺, お前, 貴様, ～せんぞ, くっ | short sentences, hard verbs, "Ngh..." for くっ; few words, no chatter | 誰が……貴様の元へなど……俺はお前を殺す / "As if I'd... ever come to you... I'm going to kill you..." |
| Rudiere (ルディエール), prince in disguise, breezy | お前, 君, ～ぜ, ～だろ, おれ | easygoing, "you know", "hey", contractions; as Rudi (ルディ) rougher street talk (ぜ -> "Here I come!") | 君を探してたんだぜ / "I was looking for you, you know." |
| Rocus (ロクス), Vice Pope, cynical and vain | 僕, お前, ふん, ～だろう, ～ぞ | sardonic, a little haughty, "Hmph!"; polite only when mocking or with superiors | ふん！お前らごときが… / "Hmph! The likes of you could never match me." |
| Irene (アイリーン), young dragon girl, spirited | 私, あんた to foes, ～わ/～わね/～わよ, お姉ちゃん | lively, teasing, exclamations; "Sis" for her sister; "the likes of you" when angry | あんたたちなんて、私が倒してあげるわ！ / "I'll beat the likes of you myself!" |
| Leyla (レイラ), imperial knight, dignified | 私, あなた, ～わね, ～かしら, ～のですか | composed, formal with superiors, soft and natural off duty ("That's a shame"); no slang | いいえ……私はあなたに負けはしない / "No... I will not lose to you..." |
| Cecia (セシア), forest priestess / Holy Mother | 私, あなた, ～のです, ～ですか | gentle, formal, few contractions, measured | なぜ、勇者のあなたが吸血鬼となったのです……？ / "Why did you, a hero, become a vampire...?" |

## Fairies (the angel's helpers; all call the player 天使様 "Angel")

| Speaker | JP markers | EN devices | Paired example |
|---|---|---|---|
| Rosa (ローザ) | ～のですね, ～られる (honorific) | formal, composed, complete sentences, no contractions in reports | 人間として地上で生きられることに決めたのですね / "So you have decided to live on the surface as a human." |
| Florinda (フロリンダ) | ですぅ, わぁい, third-person フロリン | "Florin" in the third person, stretched vowels ("heeere", "sooo"), "super", "kinda" | わぁい！　天使様、会いたかったですぅ / "Yaaay! Angel, I missed you sooo much!" |
| Shelly (シェリー) | ～ですよね, ではでは | cheerful, polite, light contractions, "So, so," for ではでは | ではでは、さっそくですが… / "So, so, may I have your orders for my search right away?" |
| Lily (リリィ) | 私, ～のです | polite, soft | (see FryMsg3) |
| Lynx (リンクス) | ボク/僕, ～ね！ | boyish, bright, "okay?!" | ボクのこと忘れないでね！ / "Even after you're human, don't forget me, okay?!" |
| Aquila (アクイラ) | 私, hesitant openers | shy: "Um," at line starts, softened requests | (see FryMsg5) |
| Cetus (シータス) | オレ, ～ですよ | casual-polite boy: "Yep", "See ya" | そうです、オレですよ / "Yep, it's me." |
| Lepus (レーパス) | 私, ～のです, formal keigo | very formal, stiff | (see FryMsg7) |

## Heaven and the enemy

| Speaker | JP markers | EN devices | Paired example |
|---|---|---|---|
| Raphael (ラファエル), archangel | 私たち, あなた, ～のです | formal, measured, warm; no contractions | その理由をまだ私たちはつかめていないのです / "We have not yet grasped the reason for it." |
| Michael (ミカエル), archangel | 俺, お前, ～だろう, ～ぞ | blunt, soldierly, contractions; crude when angry (てめえ) | 俺では不服なのか？ / "Or am I not good enough for you?" |
| Holy Mother (聖母) | あなた, ～のです, ～ですか | serene, formal, no contractions | あなたは、どこから来たのですか？ / "Where have you come from?" |
| Ravenruft (レイブンルフト), vampire king | 我が, 私, お前, ～だろう | archaic-tinged menace, slow ellipses, "my blood", "as I" | お前もいつか……私と同じ道を歩むだろう / "One day you too... will walk the same path as I..." |
| Endymion (エンディミオン), Grosain's emperor | 余/我/私, フハハハ, ～なのだ | grandiose, "Ha ha ha!!!", contempt for humans | 愚かな……しかしその愚かさが、人間なのだろうな / "Foolish... But perhaps that foolishness is what makes you human..." |
| Alberic (アルベリック), imperial general | 私 (public), 僕 (private, breakdown), 我が剣, 君 | formal and cold in command; when 僕 appears he cracks, softer and younger | せいぜい吠えるがいい / "Howl all you like. Against my sword, you are no more than a babe..." |
| Clarence / Viper (クラレンス), thief | 俺, お前, ～ぜ, ～ねえ, 兄ちゃん | slangy: "ya", "wanna", "pal" for 兄ちゃん, swagger | すげえ迫力だぜ、兄ちゃん / "Some intensity you got there, pal." |
| Serenis (セレニス), Irene's sister | 私, あなた, ～わね | cool, distant, cutting | あなたは私の妹でもなんでもないわね / "Then you're no sister of mine, either." |
| Savia (サヴィア) / Savio (サヴィオ) | Savia 私/あなた/～わね; Savio 俺/お前/～語らん | Savia frank, bitter at nobles; Savio curt warrior | これ以上はお前には語らん / "but I'll tell you no more..." |
| Ion (イオン), boy | 僕, お兄ちゃん/お姉ちゃん | childlike, "mister", "big sister" | お姉ちゃんの名前……教えて / "Tell me... your name, big sister..." |
| Imperial knights / soldiers (帝国騎士, 帝国兵) | 我ら, 貴様 | stiff military: "We", "you cur" sparingly, no slang | |

## Old men and rough speech (the voices most often flattened)

| JP marker | EN devices |
|---|---|
| ワシ/わし, ～じゃ, ～じゃろう, ～のじゃ, ～せねば, ～ん (old man: Greza, Raynor, village elders) | "lad", "eh", "aye", "I'll not", "ought to", "this very moment"; slower phrasing. Greza feev02_03: "I'd like to bid you welcome, lad... but there's no time for a long talk." |
| ～ぜ, ～ねえ, てめえ, ～ってんだ (thugs, Clarence, Rudi) | dropped g's sparingly, "ya", "gonna", "ain't" for the roughest only |
| ～でございます, ～ませ (servants, maids) | "if you please", "my lady/my lord" as address only |
| ですぅ, っス, ～のじゃ as a quirk | keep the quirk as a fixed English tic per speaker (Florinda's stretched vowels) |

Honorifics follow D1/D9 (`glossary.md`): "Raphael-sama", "Alberic-dono", never "Lord Raphael".
