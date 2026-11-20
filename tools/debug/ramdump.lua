-- ramdump.lua: write the 2 MB main RAM to RAM_OUT (absolute path) at frame RAM_FRAME (no debugger needed), e.g. to
-- find the GPU packets a screen draws (tools/sprites.py):
--   python -X utf8 tools/debug/warp.py SCENE --lua tools/debug/ramdump.lua --var RAM_FRAME=13300 --var 'RAM_OUT="C:/../ram.bin"'
local mem = PCSX.getMemPtr()
L.on_frame(function(n)
  if n == RAM_FRAME then
    local f = assert(io.open(RAM_OUT, "wb"))
    local t = {}
    for i = 0, 0x1FFFFF do
      t[#t + 1] = string.char(mem[i])
      if #t == 4096 then
        f:write(table.concat(t))
        t = {}
      end
    end
    f:close()
    L.log(string.format("RAM %s f%d", RAM_OUT, n))
  end
end)
