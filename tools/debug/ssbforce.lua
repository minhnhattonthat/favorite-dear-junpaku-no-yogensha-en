-- ssbforce.lua: play the rows of an event script that a mash run never reaches (other choice branches, conditional
-- paths), for the text coverage gate. tools/ssbforce.py drives it; append after tools/debug/textcover.lua on a
-- `warp.py --event NAME.ssb` run of the ORIGINAL disc.
-- The ssb VM (rfd2 0x800C2980, one step per call; docs/re/events.md) keeps its context at 0x80080DD8: +0x194 the
-- script base (0x801A4BB0), +0x198 the end, +0x19C the offset of the next token (= file offset). At each step entry
-- (0x800C29A4, before it loads +0x19C) the hook notes the row the VM is in; when the VM is about to run the end op
-- (00 74 or 00 FF) or re-enters a row it already played in this run (a menu loop), it moves +0x19C to the next row still
-- wanted, so the script's own text ops print it and the script carries on from there.
-- Globals (from the Lua file tools/ssbforce.py writes): SF_NAME, SF_ROWS = { {start, end, want}, .. } (file offsets;
-- want 1 = still to show, 0 = shown elsewhere or not a target), SF_SIG = { {offset, byte}, .. } (the file's bytes,
-- to tell it from an EVX loaded over the same buffer).
local mem = PCSX.getMemPtr()
local function u16(a) a = a & 0x1FFFFF; return mem[a] | (mem[a + 1] << 8) end
local function u32(a) return u16(a) + u16(a + 2) * 65536 end
local function w16(a, v) a = a & 0x1FFFFF; mem[a] = v % 256; mem[a + 1] = math.floor(v / 256) % 256 end
local function w32(a, v) w16(a, v % 65536); w16(a + 2, math.floor(v / 65536) % 65536) end
local CTX, BUF = 0x80080DD8, 0x801A4BB0
local B = BUF & 0x1FFFFF

local rows = SF_ROWS
local left = 0
for _, r in ipairs(rows) do if r[3] == 1 then left = left + 1 end end
L.log(string.format("SFORCE %s rows %d wanted %d", SF_NAME, #rows, left))
local start = {}
for i, r in ipairs(rows) do start[r[1]] = i end
-- row ends come from the JP length estimate (textcover.jp_len widens them), so neighbours can overlap: a row's own
-- start wins
local function row_of(off)
  if start[off] then return start[off] end
  -- else the last row starting at or before off, if off is inside it
  local lo, hi, best = 1, #rows, nil
  while lo <= hi do
    local m = math.floor((lo + hi) / 2)
    if rows[m][1] <= off then best, lo = m, m + 1 else hi = m - 1 end
  end
  if best and off < rows[best][2] then return best end
  return nil
end
local function ours()
  for _, s in ipairs(SF_SIG) do if mem[B + s[1]] ~= s[2] then return false end end
  return true
end
local played, done_at, last = {}, nil, nil
local function next_want()
  for i, r in ipairs(rows) do if r[3] == 1 and not played[i] then return i end end
  return nil
end
L.on_exec(0x800C29A4, function()
  if done_at then return end
  local r = PCSX.getRegisters().GPR.n
  local ctx = r.s1 & 0xFFFFFFFF
  if SF_DEBUG and SF_DEBUG > 0 then
    SF_DEBUG = SF_DEBUG - 1
    L.log(string.format("SFDBG f%d ctx=%08X base=%08X ours=%s pc=%X", L.frame, ctx, u32(ctx + 0x194), tostring(ours()),
      u32(ctx + 0x19C)))
  end
  -- registers come back sign-extended (FFFFFFFF80080DD8): compare physical addresses
  if (ctx & 0x1FFFFF) ~= (CTX & 0x1FFFFF) or u32(ctx + 0x194) ~= BUF or not ours() then return end
  local pc = u32(ctx + 0x19C)
  -- SF_SKIPBATTLE (ssbforce.py --skip-battles): step over `01 1C N` with N >= 2000 (op 0x1c queues an event id:
  -- 2xxx/3xxx start battles, docs/re/events.md), which the mash can lose or never end, so the rows after it play
  if SF_SKIPBATTLE and mem[B + pc] == 1 and mem[B + pc + 1] == 0x1C and u16(BUF + pc + 2) >= 2000 then
    w32(ctx + 0x19C, pc + 4)
    L.log(string.format("SFORCE skipbattle %X id %d f%d", pc, u16(BUF + pc + 2), L.frame))
    return
  end
  local i = row_of(pc)
  local loop = i and played[i] and pc == rows[i][1] and i ~= last
  if i and not loop then
    if not played[i] and rows[i][3] == 1 then left = left - 1 end
    played[i] = true
    last = i
  end
  -- 00 74 (op 0x74, no args) ends the event before the closing 00 FF (322 of the 346 files end 00 74 00 FF)
  local at_end = mem[B + pc] == 0 and (mem[B + pc + 1] == 0xFF or mem[B + pc + 1] == 0x74)
  -- with SF_SKIPBATTLE, `01 14 N` (hand over to another event; it loads over the buffer) counts as an end too
  if SF_SKIPBATTLE and mem[B + pc] == 1 and mem[B + pc + 1] == 0x14 then at_end = true end
  -- SF_ENDS = { [offset] = true }: extra offsets treated as ends (clev01_01 0x362: the dev-leftover speaker
  -- `ＮＵＬＬtext_on;` stops the VM for good, so force before it)
  if SF_ENDS and SF_ENDS[pc] then at_end = true end
  if at_end or loop then
    local t = next_want()
    if not t then
      L.log(string.format("SFORCE done f%d", L.frame))
      done_at = L.frame + 600
      return
    end
    w32(ctx + 0x19C, rows[t][1])
    -- counted as played now: if the VM does not print it (a map-mode wait), the next end moves on; textcover.py
    -- decides from the reads whether it was shown
    played[t], last = true, t
    left = left - 1
    L.log(string.format("SFORCE %X f%d%s", rows[t][1], L.frame, loop and " loop" or ""))
  end
end)
L.on_frame(function(n)
  if done_at and n >= done_at then L.log("final frame " .. n); L.finish(0) end
end)
