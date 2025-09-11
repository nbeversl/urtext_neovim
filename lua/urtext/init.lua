local telescope = require("telescope.builtin")
local pickers = require("telescope.pickers")
local finders = require("telescope.finders")
local sorters = require("telescope.sorters")
local actions = require("telescope.actions")
local action_state = require("telescope.actions.state")

local M = {}

function M.open_telescope()
    local items = vim.g.my_plugin_items or {}
    pickers.new({}, {
        prompt_title = "My Plugin Items",
        finder = finders.new_table { results = items },
        sorter = sorters.get_generic_fuzzy_sorter(),
        attach_mappings = function(prompt_bufnr)
            actions.select_default:replace(function()
                local selection = action_state.get_selected_entry()
                vim.g.urtext_selected_value = selection.value
                actions.close(prompt_bufnr)
                vim.cmd('UrtextCallback ' .. tostring(selection.index))
            end)
            return true
        end,
    }):find()
end

function M.open_file_picker()
    -- your previous open_file_picker code here
end

function M.setup()
    -- keymaps
    vim.keymap.set('n', '<leader>za', ':UrtextAction show_all_actions<CR>', { desc = 'Urtext: Show All Actions' })
    vim.keymap.set('n', '<leader>ze', ':UrtextAction node_browser<CR>', { desc = 'Urtext: Node Browser' })
    -- add the rest of your keymaps here
end

return M
