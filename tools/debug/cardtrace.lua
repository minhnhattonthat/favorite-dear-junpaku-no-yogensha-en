-- cardtrace.lua: log the BIOS memory-card file calls (B0 table: open/read/write/close/firstfile/nextfile/delete)
-- with their arguments and return values. Append to a warp run (needs the interpreter):
--   python -X utf8 tools/debug/warp.py SCENE --lua tools/debug/cardtrace.lua --debugger
-- Log lines: "CARD <call> f<frame> a0=.. a1=.. a2=.. name=.. ra=.." and "CARD ret <call> v0=..".
local mem = PCSX.getMemPtr()
local function cstr(a)
  if (a >> 24) ~= 0x80 and (a >> 24) ~= 0x00 then return "" end
  a = a & 0x1FFFFF
  local t = {}
  for i = 0, 31 do
    local c = mem[a + i]
    if c == 0 then break end
    t[#t + 1] = (c >= 32 and c < 127) and string.char(c) or string.format("\\x%02x", c)
  end
  return table.concat(t)
end
local B0 = { [0x32] = "open", [0x33] = "lseek", [0x34] = "read", [0x35] = "write", [0x36] = "close",
             [0x42] = "firstfile", [0x43] = "nextfile", [0x44] = "rename", [0x45] = "erase",
             [0x4A] = "InitCARD", [0x4B] = "StartCARD", [0x4E] = "_card_write", [0x4F] = "_card_read" }
L.on_exec(0xB0, function()
  local r = PCSX.getRegisters().GPR.n
  local fn = r.t1 & 0xFF
  local name = B0[fn]
  if not name then return end
  local s = ""
  if fn == 0x32 or fn == 0x42 or fn == 0x45 or fn == 0x44 then s = " name=" .. cstr(r.a0) end
  L.log(string.format("CARD %s f%d a0=%08X a1=%08X a2=%08X%s ra=%08X", name, L.frame, r.a0, r.a1, r.a2, s, r.ra))
end)
-- return values: add L.on_exec(<ra>, ..) hooks logging GPR.n.v0 at the return sites the first run printed
