# Text

**Encoding: Shift-JIS (cp932)** everywhere seen, with ASCII backslash escapes inside MSG text (verified: MSG, ssb, EVX,
.end and EXE strings decode to readable Japanese with `cp932`; `tools/scantext.py`). No custom table needed;
`tbl/jp.tbl` is not required for decoding. Whether the printer draws half-width ASCII (needed for English) is **not
known**: test in phase 5 (FD2Font.FPK = the font, format not decoded yet).

Volume (characters incl. escapes, `scantext.py summary`, 2026-11-20): MSG 368k (13.6k runs, 108 files),
ssb 169k (11.7k runs, 287 of 346 files), EVX 70k (5.2k runs, mostly repeated unit names), .end 8.5k (21 files),
overlays 8k (op.bin 325 runs, rfd2.bin 167, pro.bin 68, ed.bin 9), EXE 3k (513 runs), GRPDATA Dummy00.DAT 0.8k
(probably unused).

## MSG banks (SSB_DATA *.MSG; verified by decoding FryMsg0, T_Msg00, MssAns0)

u16 offset table at 0 (entry count = first offset / 2), then per entry: u16 byte length, then that many bytes of
SJIS text, entries back to back (no gap). **Not all banks**: BrvMsgQ0 entry 3 is `00 00 94 00` + 148 bytes of text +
`0a 00` + 10 bytes..., so some entries hold several (u16 length, text) parts, and even that model fails on a later
BrvMsg entry (`tests/test_formats.py::test_msg_banks_parse`, xfail). Decode the BrvMsgQ/BMsgQ layout in phase 4. Offsets are 16-bit, so a bank must stay under 64 KB (largest now 27 KB,
T_Msg00). Escapes seen: `\l` line break, `\k` wait for a key, `\c` clear the box (new page). Others: list them in
phase 4 (grep `\\.`). Names: FryMsg (fairy?), BrvMsgQ/BMsgQ (hero messages), MssReq/MssAns (missions),
T_Msg (teacher/tutor? "Tell me about Fein"), GenAnsw/GenNG, EMP_OK/NG, NASI_OK/NG, BTL_EVT, men3_*.

## .end files (endings; verified: feed1.end)

Plain SJIS with CRLF line breaks, no header. 21 files (feed1-3, ceed, roed...).

## EXE / overlays

SJIS strings, NUL-terminated, from 0x888 in SLPS_027.54 (place names: レイテ, ミルザプル...). Pointer form not
checked yet (expect `lui/addiu` pairs or pointer tables; phase 4).

## Name placeholder

`＄＄＄＄＄＄` (six full-width ＄, SJIS 81 90) in ssb text = the player's angel name (default ラビエル, entered at New
Game; 4 katakana max seen in the name-entry screen). Verified in ceev01_01.ssb context.
