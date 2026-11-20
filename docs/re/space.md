# Space and limits (candidates only)

- Disc: the archives and FMVs are opened by file name through the ISO9660 directory (EXE 0x844 names, opener at
  0x80023168), so mkpsxiso can re-lay files and let archives grow (later LBAs shift; savestates go stale). Verified
  by the grow test (`disc.md` §Grow test).
- LKF entries can grow (`lkf.build` re-lays them; verified, `disc.md` §Grow test): the game takes each entry's
  position from the archive header at boot. The header's "largest entry" u32 (0x0c) may be a load-buffer size:
  `lkf.build` keeps it updated. An SSB_DATA script grown past the old maximum (0x6b16 -> 0x7be8) still ran; the
  real limit for scripts is the script buffer at 0x801A4BB0 (size unknown, phase 4/5).
- RAM load buffer per file type (ssb, MSG): find the loader and its buffer in phase 4/5, and enforce the limit in the
  build.
- MSG banks: u16 offsets, so each bank < 64 KB (largest 27 KB).
- EXE strings at 0x800-0x2100: packed, all referenced from u32 pointer arrays, so the block can be rewritten whole
  (`text.md`). Free space inside the EXE: no survey yet. The EXE image (t_size 0x7b800, to 0x8009b800) ends in
  zero padding from file 0x7bcb4; at 0x8009b4b0 (file 0x7bcb0) sits a lone u32 `05` = overlay id slot (the overlays'
  first u32 is their id, 6..10), so the overlay area starts there and the EXE's code/data must not grow past
  0x8009b4b0 (verified by hexdump). Prefer rewriting the string block.
- Overlays load at 0x8009b4b0; their size bounds what follows them in RAM (unknown: Battle.bin is 0x39d8c, the
  largest). Overlay strings grow only within the overlay's slack until that is measured.
- Name plates (`Name_NNN.PIX`): fixed 64x12 pixels each. Graphics atlases (TIMs): fixed VRAM rectangles.
