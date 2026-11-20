-- Favorite Dear: Junpaku no Yogensha debug warp: cold boot -> any scene, no save and no savestate needed.
-- Normally run through tools/debug/warp.py SCENE, which reads tools/debug/scenes.tsv and sets these globals:
--   KIND   'title' | 'event' | 'swap' | 'map'
--   EVENT  KIND 'event'/'swap': SSB_DATA.LKF file name of an event script (e.g. 'ceev01_01.ssb', any .ssb), run
--          in place of prologue.ssb right after the New Game name entry
--   SWAP_HOST, SWAP_TARGET  KIND 'swap': when the game next loads file SWAP_HOST (any LKF file, e.g. a battle's
--          .EVX), it gets SWAP_TARGET instead; arrival = SWAP_TARGET's bytes at SIGBUF
--   SIG, SIGOFF, SIGBUF  hex of 16 bytes of the (last) target file at offset SIGOFF (warp.py fills them in from
--          the file's middle: every script starts with the same header bytes): arrival = these bytes sit at
--          SIGBUF + SIGOFF (default SIGBUF: the script buffer)
--   PROOF  frames from arrival to the proof shot arrived.png (default 30)
--   AFTER  'mash' (default: press circle every MASH_EVERY frames once there) | 'hold' (no input once there)
--   MASH_EVERY  frames between circle presses after arrival (default 45)
--   POST   presses after arrival, route syntax with ';' between steps ("60 -;6 circle;500 -"); shot post.png
--          when done (STATE is then saved there instead)
--   STATE  absolute path: save a savestate here 60 frames after arrival (or after POST)
-- Log lines: "WARP <stage> f<frame>"; "WARP OK <what> f<frame>" once the scene is reached (warp.py fails without it).
--
-- How it works (docs/re/debug.md): the game finds every LKF file through a by-name directory of 0x38-byte records
-- in RAM (name[0x20], archive ptr @+0x20, u8 flag @+0x24, BCD MSF minute/second/sector @+0x25..+0x27 = the disc
-- position the CD read uses, u32 size @+0x2C, u32 LKF offset @+0x30, u32 @+0x34), built at boot. New Game runs prologue.ssb right after the name entry; for KIND 'event' the prologue's record
-- gets the target's size and offset, so the game's own loader reads the target script instead.
local mem = PCSX.getMemPtr()
local function rd8(a) return mem[a & 0x1FFFFF] end
local function rd16(a) a = a & 0x1FFFFF; return mem[a] | (mem[a + 1] << 8) end
local function rd32(a) return rd16(a) | (rd16(a + 2) << 16) end
local function wr32(a, v)
  a = a & 0x1FFFFF
  for i = 0, 3 do mem[a + i] = (v >> (8 * i)) & 0xFF end
end

local SCRIPT_BUF = 0x801A4BB0          -- event scripts load here (prologue seen by DMA watch)
local DIR_LO, DIR_HI = 0x80100000, 0x80140000
local REC = 0x38

-- find the directory record of NAME (exact, NUL-terminated); nil when the directory isn't built yet
local function find_rec(name)
  local b1, n = name:byte(1), #name
  for a = DIR_LO & 0x1FFFFF, (DIR_HI & 0x1FFFFF) - REC, 4 do
    if mem[a] == b1 and mem[a + n] == 0 and mem[a + 0x1E] == 0 and (rd32(a + 0x20) >> 24) == 0x80 then
      local ok = true
      for i = 2, n do if mem[a + i - 1] ~= name:byte(i) then ok = false; break end end
      if ok then return 0x80000000 | a end
    end
  end
end

KIND = KIND or "event"
AFTER = AFTER or "mash"
MASH_EVERY = MASH_EVERY or 45
PROOF = PROOF or ((KIND == "event" or KIND == "swap") and 600 or 30)   -- a script's first frames are a black fade
SIGBUF = SIGBUF or SCRIPT_BUF
-- record swaps, applied in order; arrival = the last one's target bytes (SIG) at SIGBUF + SIGOFF
SWAPS = {}
if KIND == "event" or KIND == "swap" then
  assert(type(EVENT) == "string" and EVENT:match("%.ssb$"), "EVENT must be an .ssb name")
  SWAPS[#SWAPS + 1] = { host = "prologue.ssb", target = EVENT }
end
if KIND == "swap" then SWAPS[#SWAPS + 1] = { host = SWAP_HOST, target = SWAP_TARGET } end

local function route(steps) for _, s in ipairs(steps) do L.press(s[2], s[1]) end end
-- tools/routes/boot.txt: logos + opening movie (~6000 frames, Start doesn't skip) -> title menu (NEW GAME first)
local TITLE = { {6000, "-"}, {6, "start"}, {600, "-"}, {6, "start"}, {600, "-"} }
-- New Game, then the name and birthday entry: circle through the defaults (name ラビエル, 01/01) ...
local NEWGAME = { {30, "-"}, {6, "circle"}, {600, "-"} }
for _ = 1, 11 do NEWGAME[#NEWGAME + 1] = {6, "circle"}; NEWGAME[#NEWGAME + 1] = {54, "-"} end
-- ... then "これでいいですか？" defaults to いいえ: up + circle (repeated: the birthday digits eat a few presses;
-- the memory-card "create the data?" question that follows also takes up + circle)
for _ = 1, 25 do
  for _, s in ipairs({ {6, "up"}, {30, "-"}, {6, "circle"}, {40, "-"} }) do NEWGAME[#NEWGAME + 1] = s end
end

local stage = "boot"
local arrived_at, post_done = nil, nil
local function go(s) stage = s; L.log(string.format("WARP %s f%d", s, L.frame)) end
local function arrive(what)
  arrived_at = L.frame
  go("arrived")
  L.log(string.format("WARP OK %s f%d", what, L.frame))
end

local function sig_at(a)
  local t = {}
  for i = 0, 15 do t[#t + 1] = string.format("%02x", rd8(a + i)) end
  return table.concat(t)
end

route(TITLE)
if KIND ~= "title" then route(NEWGAME) end
go("newgame")

L.on_frame(function(n)
  if stage == "newgame" then
    if KIND == "title" and L.route_done() then arrive("title") return end
    if #SWAPS > 0 and n > 6000 then
      -- find the records every 60 frames (in case the directory moves), re-patch every frame
      if n % 60 == 0 then
        local found = 0
        for _, s in ipairs(SWAPS) do
          local h, t = find_rec(s.host), find_rec(s.target)
          if h and t then
            if s.rec ~= h then
              L.log(string.format("WARP rec %s %08X <- %s %08X size %d f%d", s.host, h, s.target, t, rd32(t + 0x2C), n))
            end
            s.rec, s.vals = h, { rd32(t + 0x24), rd32(t + 0x2C), rd32(t + 0x30) }
            found = found + 1
          end
        end
        if found < #SWAPS and n % 600 == 0 then L.log(string.format("WARP directory incomplete f%d", n)) end
      end
      for _, s in ipairs(SWAPS) do
        if s.rec then
          wr32(s.rec + 0x24, s.vals[1])   -- flag byte + BCD MSF of the file's first sector: what the CD read uses
          wr32(s.rec + 0x2C, s.vals[2])   -- size
          wr32(s.rec + 0x30, s.vals[3])   -- LKF offset
        end
      end
      if TRACE and n % 30 == 0 then L.log(string.format("TRACE f%d buf %s", n, sig_at(SIGBUF + SIGOFF))) end
      if SWAPS[#SWAPS].rec and sig_at(SIGBUF + SIGOFF) == SIG then arrive(SWAPS[#SWAPS].target) return end
    end
    if L.route_done() and n % MASH_EVERY == 0 then L.press("circle", 6) end
  elseif stage == "arrived" then
    local since = n - arrived_at
    if since == 1 and POST then
      for step in POST:gmatch("[^;]+") do
        local fr, keys = step:match("^%s*(%d+)%s+(%S+)")
        L.press(keys, tonumber(fr))
      end
    end
    if since == PROOF then L.shot("arrived.png") end
    if POST then
      if since > 1 and L.route_done() and not post_done then
        post_done = n
        L.shot("post.png")
        if STATE then L.save_state(STATE) end
      end
    else
      if since == 60 and STATE then L.save_state(STATE) end
      if AFTER == "mash" and since > PROOF and since % MASH_EVERY == 0 and L.route_done() then L.press("circle", 6) end
    end
  end
end)
