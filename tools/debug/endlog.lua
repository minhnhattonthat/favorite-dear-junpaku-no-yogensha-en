-- endlog.lua: who loads an ending narration (.end) and what the ending timer does (docs/re/text.md §.end files).
-- Logs "ENDLOAD f<frame> <name> rec=<rec> ra=<ra> s0..s3" when the loader 0x80038D74 reads a .end record, and a
-- RAM dump of 64 bytes around the caller's stack frame for finding the variant index.
--   python -X utf8 tools/debug/warp.py end_fe --lua tools/debug/endlog.lua --debugger
local mem = PCSX.getMemPtr()
local function cstr(a)
  a = a & 0x1FFFFF
  local t = {}
  for i = 0, 31 do
    local c = mem[a + i]
    if c == 0 or c < 32 or c > 126 then break end
    t[#t + 1] = string.char(c)
  end
  return table.concat(t)
end
L.on_exec(0x80038D74, function()
  local r = PCSX.getRegisters().GPR.n
  local name = cstr(r.a2)
  if name:lower():find("%.end$") then
    L.log(string.format("ENDLOAD f%d %s rec=%08X dst=%08X ra=%08X s0=%08X s1=%08X s2=%08X s3=%08X s4=%08X sp=%08X",
      L.frame, name, r.a2, r.a1, r.ra, r.s0, r.s1, r.s2, r.s3, r.s4, r.sp))
    local t = {}
    for i = 0, 31 do   -- the wrapper 0x80039DF8 keeps its caller's ra at sp+0x18; return addresses further up
      local a = (r.sp + 4 * i) & 0x1FFFFF
      t[#t + 1] = string.format("%08X", mem[a] | (mem[a + 1] << 8) | (mem[a + 2] << 16) | (mem[a + 3] << 24))
    end
    L.log("ENDSTACK " .. table.concat(t, " "))
  end
end)
