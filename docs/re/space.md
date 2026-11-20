# Space and limits (candidates only)

- Disc: files are rebuilt with mkpsxiso, so archives and the EXE can grow on disc (later LBAs shift; savestates go
  stale). Not tested yet (phase 3 identity build first).
- LKF entries can grow (`lkf.build` re-lays them). Unknown: whether the EXE/overlays hold their own copy of entry
  offsets/sizes (search before resizing), and the RAM load buffer size per file type (ssb, MSG): find the loader and
  its buffer, and enforce the limit in the build.
- MSG banks: u16 offsets, so each bank < 64 KB (largest 27 KB).
- EXE: no free-space survey yet. Overlays: tails must not be touched.
