-- stateat.lua: save a savestate at frame STATE_FRAME to STATE_AT (absolute path), e.g. to hand a warp run's
-- mid-scene moment to play.py:
--   python -X utf8 tools/debug/warp.py SCENE --lua tools/debug/stateat.lua --var STATE_FRAME=19950 --var 'STATE_AT="C:/../x.sstate"'
L.on_frame(function(n)
  if n == STATE_FRAME then
    L.save_state(STATE_AT)
    L.log(string.format("STATE %s f%d", STATE_AT, n))
  end
end)
