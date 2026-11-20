-- textcover.lua: log the text the game reads, for tools/textcover.py (phase 8 coverage gate).
-- Append to a warp run on the ORIGINAL disc (row ids are original file offsets / vaddrs; the scripts branch the
-- same way in the build, so what a route reaches on the original it reaches in the build):
--   python -X utf8 tools/debug/warp.py SCENE --lua tools/debug/textcover.lua --debugger --out-dir work/qa/cover
-- Log lines: "FILE f<frame> <name> dst=<dst> size=<size>" for every LKF load (loader 0x80038D74, as fileslog.lua)
-- and "TREAD <addr> <byte>" for the first read of each address in the text buffers since the last load (reads are
-- cleared on every load, since buffers are reused). tools/textcover.py maps each read to (file, offset) and so to a
-- row, if the byte is the original file's.
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
-- warp.lua makes the game load its target under the host's record (event warps: prologue.ssb -> EVENT; swaps:
-- SWAP_HOST -> SWAP_TARGET), so the record name is the host's: log the file actually loaded.
local function real_name(name)
  if KIND == "swap" and name:lower() == (SWAP_HOST or ""):lower() then return SWAP_TARGET end
  if EVENT and name:lower() == "prologue.ssb" then return EVENT end
  return name
end
local function u32(a)
  a = a & 0x1FFFFF
  return mem[a] | (mem[a + 1] << 8) | (mem[a + 2] << 16) | (mem[a + 3] << 24)
end
local hit
-- Text files outside the three fixed buffers (MSG banks also load to 0x801203E0, the shared image buffer): watch
-- [dst, dst+size) from the first load on. size = the directory record's +0x2C (docs/re/debug.md).
local watched = {}
local function fixed(a) return (a >= 0x9B4B0 and a < 0xD8000) or (a >= 0x189B90 and a < 0x191B90)
  or (a >= 0x1A4BB0 and a < 0x1BB560) end
L.on_exec(0x80038D74, function()
  local r = PCSX.getRegisters().GPR.n
  seen = {}
  local name = real_name(cstr(r.a2))
  local dst = r.a1 & 0x1FFFFF
  local size = u32(r.a2 + 0x2C)
  L.log(string.format("FILE f%d %s dst=%08X size=%X", L.frame, name, 0x80000000 + dst, size))
  local ext = name:upper():match("%.(%w+)$") or ""
  if (ext == "MSG" or ext == "SSB" or ext == "EVX" or ext == "END") and not fixed(dst) then
    local w = watched[dst]
    if not w or w < size then
      watched[dst] = size
      L.on_read(0x80000000 + dst, 0x80000000 + dst + size - 1, function(a) hit(a) end)
    end
  end
end)
-- Overlays don't come through the LKF loader: 0x8002AD70 loads one from the disc to 0x8009B4B0, and its first
-- word is 6 + its index (docs/re/debug.md, Main loop mode). Log a FILE line when that word changes.
local OVL = { [6] = "op.bin", [7] = "rfd2.bin", [8] = "Battle.bin", [9] = "ed.bin", [10] = "pro.bin" }
local ovl_word = -1
function hit(addr)
  addr = addr & 0x1FFFFF
  if addr >= 0x9B4B0 and addr < 0xD8000 then
    local w = mem[0x9B4B0] | (mem[0x9B4B1] << 8)
    if w ~= ovl_word then
      ovl_word = w
      local k
      for a, _ in pairs(seen) do if a >= 0x9B4B0 and a < 0xD8000 then k = k or {}; k[#k + 1] = a end end
      for _, a in ipairs(k or {}) do seen[a] = nil end
      L.log(string.format("FILE f%d %s dst=8009B4B0", L.frame, OVL[w] or ("ovl" .. w)))
    end
  end
  if seen[addr] then return end
  seen[addr] = true
  -- the byte read: textcover.py counts a read only if it equals the file's byte there (a reused buffer would
  -- otherwise credit the last text file loaded there)
  L.log(string.format("TREAD %08X %02X", 0x80000000 + addr, mem[addr]))   -- +, not |: LuaJIT bit ops are signed
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
