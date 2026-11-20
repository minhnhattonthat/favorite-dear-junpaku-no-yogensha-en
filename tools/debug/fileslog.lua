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
local function u32(a)
  a = a & 0x1FFFFF
  return mem[a] | (mem[a + 1] << 8) | (mem[a + 2] << 16) | (mem[a + 3] << 24)
end
-- blk=<size>: the heap block header 0x10 bytes before dst (prev, next, size incl. header; docs/re/space.md), so
-- the buffer holds size - 0x10 bytes when next == dst - 0x10 + size
L.on_exec(0x80038D74, function()
  local r = PCSX.getRegisters().GPR.n
  local h = r.a1 - 0x10
  L.log(string.format("FILE f%d %s dst=%08X mode=%d blk=%X next=%08X", L.frame, cstr(r.a2), r.a1, r.a0,
    u32(h + 8), u32(h + 4)))
end)
