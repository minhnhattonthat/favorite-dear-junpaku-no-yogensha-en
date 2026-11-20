-- msgforce.lua: show every entry of MSG banks in the game's MSG box (text coverage, tools/msgforce.py drives it).
-- MSG entries are picked by game state (fairy reports, chats, battle lines), so a scene shows a few per bank. This
-- hook rides on a scene that opens the MSG box (battle: Battle.bin starts it through EXE 0x8002E6C0) and, each
-- time the box's step function 0x8002DFE4 reaches the end of its text (0x8002E030: cursor +0x4B2 >= length
-- +0x4B0), points the box at the next entry instead of letting it close: text +0x4AC, length, cursor 0xFFFE,
-- s1 = text - 2, then jumps to the `\c` (clear page) call at 0x8002E0E8, whose return path adds 2 to both
-- (docs/re/text.md). Each bank's original bytes are put at FORCE_AT (free RAM below the EXE on the original disc)
-- and logged as a FILE line, so tools/textcover.py credits the box's reads exactly as for a game load.
-- Globals (written by tools/msgforce.py into a Lua file passed with --lua before this one):
--   FORCE_BANKS  { {name = "BMsgQ000.MSG", data = <original bytes>, list = { {text offset, byte length}, .. }}, .. }
--   FORCE_AT     load address (0x80010000)
-- Log: "FORCE <bank> entries N", "FORCE <bank> <i> f<frame>" every 25 entries, "FORCE bank done <bank> f<frame>",
-- "FORCE done f<frame>" (the run ends 300 frames later).
local mem = PCSX.getMemPtr()
local AT = FORCE_AT or 0x80010000
local A = AT & 0x1FFFFF
local function u16(a) a = a & 0x1FFFFF; return mem[a] | (mem[a + 1] << 8) end
local function u32(a) return u16(a) + u16(a + 2) * 65536 end
local function w16(a, v) a = a & 0x1FFFFF; mem[a] = v % 256; mem[a + 1] = math.floor(v / 256) % 256 end
local function w32(a, v) w16(a, v % 65536); w16(a + 2, math.floor(v / 65536) % 65536) end

local bi, idx, done_at, loaded = 1, 0, nil, false
local seen = {}
local maxn = 0
for _, b in ipairs(FORCE_BANKS) do maxn = math.max(maxn, #b.data) end

local function intact(b)
  local n = #b.data
  for i = 0, n - 1, math.max(1, math.floor(n / 64)) do
    if mem[A + i] ~= b.data:byte(i + 1) then return false end
  end
  return true
end
local function put(b)
  for i = 0, #b.data - 1 do mem[A + i] = b.data:byte(i + 1) end
  seen = {}
  L.log(string.format("FILE f%d %s dst=%08X size=%X", L.frame, b.name, AT, #b.data))
end
L.on_read(AT, AT + maxn - 1, function(a)
  a = a & 0x1FFFFF
  if seen[a] then return end
  seen[a] = true
  L.log(string.format("TREAD %08X %02X", 0x80000000 + a, mem[a]))
end)

for _, b in ipairs(FORCE_BANKS) do L.log(string.format("FORCE %s entries %d", b.name, #b.list)) end
L.on_exec(0x8002E030, function()
  if done_at then return end
  local b = FORCE_BANKS[bi]
  idx = idx + 1
  while b and not b.list[idx] do
    L.log(string.format("FORCE bank done %s f%d", b.name, L.frame))
    bi, idx, loaded = bi + 1, 1, false
    b = FORCE_BANKS[bi]
  end
  if not b then
    L.log(string.format("FORCE done f%d", L.frame))
    done_at = L.frame + 300
    return
  end
  if not loaded or not intact(b) then put(b); loaded = true end
  local e = b.list[idx]
  local obj = u32(0x800857D8)
  w32(obj + 0x4AC, AT + e[1]); w16(obj + 0x4B0, e[2]); w16(obj + 0x4B2, 0xFFFE)
  local r = PCSX.getRegisters()
  r.GPR.n.s1 = AT + e[1] - 2
  r.pc = 0x8002E0E8
  if idx % 25 == 1 then L.log(string.format("FORCE %s %d f%d", b.name, idx, L.frame)) end
end)
L.on_frame(function(n)
  if done_at and n >= done_at then L.shot("final.png"); L.log("final frame " .. n); L.finish(0) end
end)
