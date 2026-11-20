# Event scripts (*.ssb) and battle setups (*.EVX)

## ssb (SSB_DATA.LKF, 346 files; model verified by `tools/ssb.py stats`: 344 of 346 parse cleanly)

`.ssb` + 12 zero bytes, then one byte stream from 0x10 to the end:
- byte >= 0x80: an SJIS character of message text (text is inline, not in a table);
- else: argc byte N, opcode byte, then N little-endian u16 args. Every opcode has a fixed N (table below);
- opcode 0x19, N=1: speaker name; arg = character count, then that many SJIS characters follow.

| op | N | meaning (guess unless marked) |
|---|---|---|
| 0x02 | 0 | line break in text (verified: splits sentences) |
| 0x05, 0x06 | 0 | wait for key, then close/next page (always paired, 6746 each) |
| 0x19 | 1 | speaker name + chars (verified: セシア, ＄＄＄＄＄＄) |
| 0x78 | 1 | face/expression for the following line (text starts right after) |
| 0x0a | 1 | wait N frames? (one instance with N=58: likely mis-sync, see below) |
| 0x15/0x1f(8)/0x24 | | script header ops (each file starts `00 15 08 1f ...`) |
| 0x67/0x68 | 1/0 | paired 443 each: choice or branch? check |
| 0xff | 0 | end of script |
| others | | 0x14 0x16 0x1c 0x1e 0x22 0x23 0x28 0x3c 0x3d 0x50-0x52 0x56 0x57 0x5b 0x5c 0x5e 0x5f 0x62 0x63 0x72 0x74 |

No opcode found so far takes a byte offset into the script, so scripts look **linear** (branches as separate files:
ceev01_01/_02/_03). If true, text can grow without pointer fixups. **Not verified**: confirm in phase 4 by checking
0x67/0x68 and every op whose args look like offsets, and by a lengthened-text boot test.

Failures to fix in phase 4: `0029_clev01_01.ssb` (args run past the end) and one more file (`ssb.py stats` lists it); an
op 0x0a with N=58 is the same mis-sync.

## EVX (269 files; battle setups, guess)

0x20-byte header, then unit records with names in fixed-width NUL-padded SJIS fields (セシア, ジャイアント), followed
by stats. Field width to measure in phase 4 (names will need to fit or be remapped).
