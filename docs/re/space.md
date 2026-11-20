# Space and limits (candidates only)

- Disc: the archives and FMVs are opened by file name through the ISO9660 directory (EXE 0x844 names, opener at
  0x80023168), so mkpsxiso can re-lay files and let archives grow (later LBAs shift; savestates go stale). Verified
  by the grow test (`disc.md` §Grow test).
- LKF entries can grow (`lkf.build` re-lays them; verified, `disc.md` §Grow test): the game takes each entry's
  position from the archive header at boot. The header's "largest entry" u32 (0x0c) may be a load-buffer size:
  `lkf.build` keeps it updated. An SSB_DATA script grown past the old maximum (0x6b16 -> 0x7be8) still ran.
- **Script buffer (measured, phase 7):** 0x801A4BB0 is the data of a heap block whose 0x10-byte header sits at
  0x801A4BA0: u32 prev 0x80191B90, u32 next 0x801BB560, u32 size 0x169C0 (header included), the same in all 22 RAM
  dumps (events, map, heaven, battle, title). So a script may take **0x169B0 bytes**. It is a shared file buffer:
  events load the .ssb at its start and the rest holds stale data from an earlier 0x11A20-byte `.ti` load (map
  scenes fill it to +0x16997); nothing else is placed after the script while it runs. Largest built script:
  alkaya.ssb 0x6E3C. `tools/debug/fileslog.lua` now logs each load's block size (`blk=`), the way to measure the
  other buffers. Measured the same way (`work/qa/p7buf`: `warp.py end_ro --event roev25.ssb --lua
  tools/debug/fileslog.lua --debugger`): **EVX** loads into the same 0x801A4BB0 block (over the script);
  **.end** into a 0x8010-byte block at 0x80189B90 (0x8000 bytes of data; largest built roed1.end 0x57C). TIMs and
  VB sound banks use a 0x697B0-byte block at 0x801203E0. MSG not measured. `insert.LOAD_CAPS` enforces these.
- RAM load buffer per file type (ssb, MSG): find the loader and its buffer in phase 4/5, and enforce the limit in the
  build.
- MSG banks: u16 offsets, so each bank < 64 KB (largest 27 KB).
- EXE strings at 0x800-0x2100: packed, all referenced from u32 pointer arrays, so the block can be rewritten whole
  (`text.md`). Free space inside the EXE: no survey yet. The EXE image (t_size 0x7b800, to 0x8009b800) ends in
  zero padding from file 0x7bcb4; at 0x8009b4b0 (file 0x7bcb0) sits a lone u32 `05` = overlay id slot (the overlays'
  first u32 is their id, 6..10), so the overlay area starts there and the EXE's code/data must not grow past
  0x8009b4b0 (verified by hexdump). Prefer rewriting the string block.
- **String heap 0x80010000-0x8001E000 (used, phase 7):** zero in all 22 RAM dumps incl. three battle dumps
  (`work/re/bh1`, `bh2`, `bp3`), and no lui in the EXE builds a 0x8001xxxx address. `build.patch_exe` prepends
  0x10000 bytes (t_addr 0x80010000); `codetext.fit` puts EXE/overlay strings that outgrow their slot there and
  re-points every `ptr`/`lui` reference (overlays too, for moved EXE strings). Used ~0x2F00 of 0xE000.
  Limits that stay: a string the code copies inline (`char buf[] = "..."`: lw/lb at fixed offsets,
  `codetext.copy_size`) keeps its byte count wherever it lives; a `lui` shared with another value, a fixed table
  slot (pro quiz) or an unreferenced string cannot move. `batches.py merge` holds such rows back and says why.
- **FREE block 0x8001E000-0x80020000 (used, phase 5):** below the EXE's load address, zero in RAM dumps of 10 scenes
  (prologue, map, heaven, event, game over, OMAKE CG, title, status, exam, visit; `tools/ramzero.py`). The build
  prepends it to the EXE (t_addr moved down) and puts the pair-glyph hook and glyphs there (`asm/font.asm`, ~4.2 KB
  of 8 KB). 0x80010000-0x8001E000 is zero too (more room if needed; battle not dumped yet).
- Overlays load at 0x8009b4b0; their size bounds what follows them in RAM (unknown: Battle.bin is 0x39d8c, the
  largest). Overlay strings grow only within the overlay's slack until that is measured.
- Name plates (`Name_NNN.PIX`): fixed 64x12 pixels each. Graphics atlases (TIMs): fixed VRAM rectangles.
