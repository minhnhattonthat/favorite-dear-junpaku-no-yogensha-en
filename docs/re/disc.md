# Disc layout

Unpack: `tools/mkpsxiso/mkpsxiso-2.30-win64/dumpsxiso.exe -x work/disc/tree -s work/disc/layout.xml "rom/Favorite Dear - Junpaku no Yogensha (Japan).bin"`
(15 files, one Mode2 data track; `license_data.dat` = licence sectors). Boot: SYSTEM.CNF -> `SLPS_027.54` (main EXE,
496 KB). Unlike the first game (PSX.EXE + GDATA.BIN, see `../favorite-dear-en/docs/re/disc.md`) this one keeps its
data in four `+LKF` archives. Identity rebuild with mkpsxiso: not yet tested (phase 3).

| File | What | State |
|---|---|---|
| SLPS_027.54 | main EXE; SJIS strings (place names, menu text: 513 runs) | verified (scan) |
| FD2BN.LKF | 5 code overlays: op.bin, rfd2.bin, Battle.bin, ed.bin, pro.bin (first u32 = overlay id 6..10). op/rfd2/pro/ed hold SJIS strings, Battle.bin none | verified (scan) |
| FD2SN.LKF | sound: se.bin, VH/VB banks, SEQ | guess (names, headers) |
| GRPDATA.LKF (85 MB, 1560 files) | graphics: FD2Font.FPK (font), 1249 TIM, PIX (88, Name_NNN.PIX 384 B name plates?), SFM/SFA (sprite frames/animations, "SFM "/"SFA " magic), TMD (3D), BLF/CLT/RCT, DAT | partly mapped |
| SSB_DATA.LKF (744 files) | text and scripts: 346 `.ssb` event scripts, 108 `.MSG` message banks, 269 `.EVX` battle setups, 21 `.end` ending narrations | verified (decoded; `events.md`, `text.md`) |
| *.STR | FMV, 2336-byte sectors as extracted (`tools/str2352.py` for ffmpeg): CI_LOGO (company logos), DEMO (opening, burned-in JP captions), DRA16/DRAGON16/MONO (dragon sequences, no text), ENDING (JP caption, logo, Japanese staff roll). EXE also names SOFIX.STR, not on the disc | verified (decoded, `graphics.md` G14/G15) |
| VOICE.XA | XA voice audio | not looked at |
| DUMMY.BMP | 27 MB padding | guess |

## LKF archive (verified: `tools/lkf.py list|extract`, every entry lines up with a file magic)

Header 0x20 bytes: `"+LKF"`, u32 count, u32 data start (= first entry's offset), u32 size of the largest entry,
16 zero bytes. Then `count` entries of 0x20 bytes: name[16] ASCII NUL-padded, 7 zero bytes, u8 flags (0x20 in every
entry seen), u32 offset, u32 size. Data is sector (0x800) aligned, in entry order, zero-padded, and the packer always pads at least
one byte: a file ending exactly on a sector boundary is followed by a whole zero sector (FD2SN ASIA_B.VB).
`lkf.build()` re-lays entries the same way and rebuilds SSB_DATA, FD2BN and FD2SN byte for byte
(`tests/test_formats.py`; GRPDATA not in the test, 85 MB); whether the game reads offsets from the archive header or from a table in the EXE/overlays is
**not yet known** (search the EXE for the archive's offsets before changing any entry size).

Extracted copies: `work/lkf/<ARCHIVE>/<index>_<name>` (`lkf.py extract`).
