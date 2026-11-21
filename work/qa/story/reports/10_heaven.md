# 10_heaven: story read (phase 9)

Read: all 884 rows (taiken preview, fairy visits Y0xev, FryMsg0-7, HVN_Msg00, T_Msg00/01), JP and EN side by side.

## Fixed
- Minor: `Y07ev_01.03AA` family answer "Yes, it is." did not fit the question ("my day off's not over yet, right?").
  Override: "Yes, that's right."
- Nit: `FryMsg0.1CFE` "Cecia-san" in a line that otherwise says "Cecia-sama" (JP セシア様). Now -sama.
- Nit: `FryMsg0.160C` "Fein Lu Lugus" without -sama, unlike every other report from this fairy (JP 様). Now -sama.
- Nit: `FryMsg1.0AB0` Florin mixed "I" and "Florin" in one sentence. Now "Florin searched ..., but couldn't find a thiiing!"

## Checked, no change
- `T_Msg01.0306` etc. end in `＜勇者名＞....`: the four dots are byte filler that the game overwrites with the hero's
  name (docs/re/text.md, "Code that edits message bytes"). Not visible.
- Fairy voices match docs/style-reference.md (Florin third person, Aquila "Um", Cetus casual, Lepus formal).
- Fairy sexes match glossary (Lepus/Cetus/Lynx male, Aquila female).
- Mid-sentence " / " box splits in long FryMsg reports are line-fit splits from the fit pass, read fine.
- Other FryMsg banks still drop -sama on Fein/Rocus/Cecia in the "has gone missing" headline while keeping it later
  in the same message. Waived: consistent within each bank, reads naturally, and JP keeps 様 throughout.
