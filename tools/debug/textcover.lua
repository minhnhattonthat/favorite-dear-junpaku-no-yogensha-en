-- textcover.lua: log the text the game reads, for tools/textcover.py (phase 8 coverage gate).
-- Append to a warp run on the ORIGINAL disc (row ids are original file offsets / vaddrs; the scripts branch the
-- same way in the build, so what a route reaches on the original it reaches in the build):
--   python -X utf8 tools/debug/warp.py SCENE --lua tools/debug/textcover.lua --debugger --out-dir work/qa/cover
-- Log lines: "FILE f<frame> <name> dst=<dst>" for every LKF load (loader 0x80038D74, as fileslog.lua) and
-- "TREAD <addr>" for the first read of each address in the text buffers since the last load (reads are cleared
-- on every load, since buffers are reused). tools/textcover.py maps each read to (file, offset) and so to a row.
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
local seen = {}
L.on_exec(0x80038D74, function()
  local r = PCSX.getRegisters().GPR.n
  seen = {}
  L.log(string.format("FILE f%d %s dst=%08X", L.frame, cstr(r.a2), r.a1))
end)
local function hit(addr)
  addr = addr & 0x1FFFFF
  if seen[addr] then return end
  seen[addr] = true
  L.log(string.format("TREAD %X", 0x80000000 | addr))
end
-- Buffers (docs/re/space.md): overlays at 0x8009B4B0, .end at 0x80189B90 (0x8000), .ssb/.EVX/.MSG heap block at
-- 0x801A4BB0 (0x169B0). EXE strings are watched one string at a time (TEXTCOVER_EXE, written by textcover.py).
L.on_read(0x8009B4B0, 0x800D7FFF, hit)
L.on_read(0x80189B90, 0x80191B8F, hit)
L.on_read(0x801A4BB0, 0x801BB55F, hit)
if TEXTCOVER_EXE then
  for lo, hi in string.gmatch(TEXTCOVER_EXE, "(%x+)-(%x+)") do
    L.on_read(tonumber(lo, 16), tonumber(hi, 16), hit)
  end
end
