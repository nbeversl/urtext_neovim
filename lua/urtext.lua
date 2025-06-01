local telescope = require("telescope.builtin")
local pickers = require("telescope.pickers")
local finders = require("telescope.finders")
local conf = require("telescope.config").values
local sorters = require("telescope.sorters")
local actions = require('telescope.actions')
local action_state = require('telescope.actions.state')

local M = {}

function M.open_telescope()
  local items = vim.g.my_plugin_items or {}

  pickers.new({}, {
    prompt_title = "My Plugin Items",
    finder = finders.new_table {
      results = items,
    },
    sorter = sorters.get_generic_fuzzy_sorter(),
     attach_mappings = function(prompt_bufnr, map)
      actions.select_default:replace(function()
        local selection = action_state.get_selected_entry()
        actions.close(prompt_bufnr)
        vim.cmd('UrtextCallback' .. vim.fn.shellescape(selection.index))
      end)
      return true
    end,
  }):find()
end

return M