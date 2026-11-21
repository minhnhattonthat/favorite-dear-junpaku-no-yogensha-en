-- endcount.lua: for the end_<x>ed<n> swap scenes. The ending narration draws as many lines as ed.bin's table says
-- for the file the game CHOSE (0x8009CD18 reads the count; docs/re/text.md §.end files), so a swapped-in .end
-- would be cut at the host's count (feed3: 35). This sets the count to the swapped-in file's own.
--   python -X utf8 tools/debug/warp.py end_ceed2 --lua tools/debug/textcover.lua --lua tools/debug/endcount.lua --debugger
-- Counts: the original ed.bin table (tools/lint.py end_counts; ceed3 = 34 there, 38 with asm/ed.asm: use 38 here
-- so the coverage run reads the whole file, as the English build draws it).
local COUNT = {
  ["feed1.end"] = 46, ["feed2.end"] = 46, ["feed3.end"] = 35, ["cled1.end"] = 46, ["cled2.end"] = 46,
  ["cled3.end"] = 38, ["loed1.end"] = 47, ["loed2.end"] = 46, ["loed3.end"] = 38, ["roed1.end"] = 46,
  ["roed2.end"] = 46, ["roed3.end"] = 38, ["eied1.end"] = 46, ["eied2.end"] = 46, ["eied3.end"] = 39,
  ["laed1.end"] = 46, ["laed2.end"] = 46, ["laed3.end"] = 34, ["ceed1.end"] = 46, ["ceed2.end"] = 46,
  ["ceed3.end"] = 38,
}
local mem = PCSX.getMemPtr()
local want = KIND == "swap" and COUNT[(SWAP_TARGET or ""):lower()]
if want then
  L.on_exec(0x8009CD18, function()        -- ed.bin: lhu v0, 0(v0) = the line count
    if (mem[0x9B4B0] or 0) ~= 9 then return end   -- only while ed.bin (overlay id 9) is loaded
    local a = PCSX.getRegisters().GPR.n.v0 & 0x1FFFFF
    mem[a], mem[a + 1] = want & 0xFF, want >> 8
    L.log(string.format("ENDCOUNT f%d %s -> %d", L.frame, SWAP_TARGET, want))
  end)
end
