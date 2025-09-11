-- file: lua/urtext/init.lua
local M = {}

function M.setup()
  -- load keymaps
  require("urtext.keymaps").setup()

  -- other setup code for urtext plugin can go here
end

return M
