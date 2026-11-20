-- fileslog.lua: log every LKF file the game loads (the loader 0x80038D74(mode, dst, rec, ..); rec = the 0x38-byte
-- directory record, name at +0, docs/re/debug.md). Append to a warp run (needs the interpreter):
--   python -X utf8 tools/debug/warp.py SCENE --lua tools/debug/fileslog.lua --debugger
-- Log lines: "FILE f<frame> <name> dst=<dst> mode=<mode>". Use it to find which scene shows an image or script.
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
  L.log(string.format("FILE f%d %s dst=%08X mode=%d", L.frame, cstr(r.a2), r.a1, r.a0))
end)
