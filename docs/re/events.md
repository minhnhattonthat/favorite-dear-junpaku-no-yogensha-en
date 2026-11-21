# Event scripts (*.ssb) and battle setups (*.EVX)

## ssb (SSB_DATA.LKF, 346 files; verified by `tools/ssb.py`: all 346 parse and rebuild byte for byte)

`.ssb` + 12 zero bytes, then one byte stream from 0x10 to the end:
- byte >= 0x80: an SJIS character of message text (text is inline, not in a table);
- 0x20 <= byte < 0x80: a single-byte ASCII character. Only two dev leftovers use it: `ＮＵＬＬtext_on;` in
  clev01_01.ssb 0x361 (a speaker named ＮＵＬＬ) and `/イベント/終了` in eiev13_02.ssb 0x2816. Reading these bytes as
  argument counts was the "args run past the end" failure of phase 1;
- else: argc byte N, opcode byte, then N little-endian u16 args. Every opcode has a fixed N (table below);
- opcode 0x19, N=1: speaker name; arg = character count, then that many SJIS characters follow.

| op | N | meaning (guess unless marked) |
|---|---|---|
| 0x02 | 0 | line break in text (verified: splits sentences) |
| 0x05, 0x06 | 0 | wait for key, then close/next page (always paired, 6746 each) |
| 0x19 | 1 | speaker name + chars (verified: セシア, ＄＄＄＄＄＄) |
| 0x1c | 1 | **queue an event id** (the 0x80029B7C queue, `debug.md`): 0-999 (35 uses), 2xxx (256), 3xxx (134 = battles, id % 1000 in the exe table). Verified 2026-11-21 (roev25 0x30, id 2604): the VM stops stepping after it and the game loads the battle's models; the event resumes after the battle. `ssbforce.py --skip-battles` steps over ids >= 2000 |
| 0x78 | 1 | face/expression for the following line (text starts right after) |
| 0x0a | 1 | wait N frames? |
| 0x15/0x1f(8)/0x24 | | script header ops (each file starts `00 15 08 1f ...`) |
| 0x5b | 1 | **goto**: arg = absolute file offset (verified: 1116 of 1128 land on an op, the rest on a text character) |
| 0x5c, 0x5e, 0x5f, 0x62, 0x63 | 3 | **conditional jump**: arg 2 = absolute file offset (100%, 95-98%, rest on text) |
| 0x67 | 1 | **choice**: arg = file offset of the code for this answer; the answer text (`《聞く》`) follows, then `00 02 00 68` |
| 0x68 | 0 | end of a choice's text |
| 0xff | 0 | end of script |
| others | | 0x14 0x16 0x1c 0x1e 0x22 0x23 0x28 0x3c 0x3d 0x50-0x52 0x56 0x57 0x72 0x74 |

**VM (verified, phase 8, `tools/debug/ssbforce.lua`):** rfd2 0x800C2980(ctx) runs one step; the event context is
0x80080DD8: +0x194 script base (0x801A4BB0), +0x198 end, +0x19C offset of the next token (= file offset; the
first fetch is 0x10). Text bytes are fetched at 0x800C29CC/29D0 (up to 0x40 per step), op args at 0x800C2914.
Writing +0x19C at the step entry (0x800C29A4) moves the script. 322 of 346 files end `00 74 00 FF`: op 0x74 (no
args) ends the event, so the VM never fetches the 0xFF; the other 24 end `.. 00 FF` after a wait (0x0a) or 0x14.

**Scripts are not linear**: the jump ops above take absolute offsets, so text can't grow without fixups.
`ssb.build()` re-points every jump (`tests/test_text.py::test_ssb_grow_keeps_jumps` grows every row and checks that
each jump still lands on the same token). 22 jumps land in the middle of a text line; extraction cuts the row there,
so such a line is two rows (the second one starts where the jump lands). Dead bytes: `3a 0a` at loev04_01.ssb
0x4ba (after a goto, before a jump target) are kept as raw bytes; this was the old "op 0x0a with N=58" mis-sync.
No other offsets into a script are known (entry is 0x10); a lengthened-text boot test belongs to phase 5.

## EVX (269 files; battle setups; text verified by `tools/evx.py` roundtrip + coverage)

- 0x02: 30-byte title, NUL-terminated (junk after the NUL in some files): a dev label like `ラストバトル(負ける)`,
  guess not shown in game (180 files have one).
- unit records of 0x3C bytes from 0xA0: u16, 32-byte NUL-padded unit name (セシア, ジャイアント), stats.
- a command stream of records; message records are `14 00 02 00`, u16 cmd, u16 size (whole record), then items
  (u8 type 0x08 speaker / 0x0A text, u8 length incl. NUL, text NUL), then raw bytes to `size`. cmd 0x012A / 0x032A
  text, 0x012C speaker, 0x032D two choices (`《わかりました……》` / `《いいえ……》`). The last record of a file can be
  cut by the end of the file (its size counts bytes that are not there). u8 lengths cap an item at 254 bytes.
- Unknown: whether any field holds an offset into the stream (growth only re-parse-tested; boot-test in phase 5).
