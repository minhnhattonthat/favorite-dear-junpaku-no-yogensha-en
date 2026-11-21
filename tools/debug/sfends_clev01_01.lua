-- sfends_clev01_01.lua: extra forcing ends for clev01_01.ssb (tools/debug/ssbforce.lua SF_ENDS). At 0x362 the
-- dev-leftover speaker op `01 19 04 00 ＮＵＬＬ` + ASCII `text_on;` stops the VM for good (traced 2026-11-21), so the
-- rows after it and the other branch of the flag test at 0x118 are forced from there. Load before ssbforce.lua:
--   warp.py --event clev01_01.ssb --lua tools/debug/textcover.lua --lua work/qa/ssbforce4/_lua/clev01_01.lua
--     --lua tools/debug/sfends_clev01_01.lua --lua tools/debug/ssbforce.lua --debugger
SF_ENDS = { [0x362] = true }
