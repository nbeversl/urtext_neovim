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
    -- Core Urtext actions
    vim.keymap.set('n', '<leader>za', ':UrtextAction show_all_actions<CR>', { desc = 'Urtext: Show All Actions' })
    vim.keymap.set('n', '<leader>zb', ':UrtextAction node_browser<CR>', { desc = 'Urtext: Node Browser' })
    vim.keymap.set('n', '<leader>z/', ':UrtextAction open_link<CR>', { desc = 'Urtext: Open Link' })

    -- Navigation with arrow keys
    vim.keymap.set('n', '<leader>z<Left>', ':UrtextAction nav_back<CR>', { desc = 'Urtext: Nav Back' })
    vim.keymap.set('n', '<leader>zj', ':UrtextAction nav_back<CR>', { desc = 'Urtext: Nav Back' })
    vim.keymap.set('n', '<leader>zk', ':UrtextAction nav_forward<CR>', { desc = 'Urtext: Nav Forward' })

    -- Additional common actions
    vim.keymap.set('n', '<leader>z-', ':UrtextAction new_file_node<CR>', { desc = 'Urtext: New File Node' })
    vim.keymap.set('n', '<leader>zh', ':UrtextAction open_home<CR>', { desc = 'Urtext: Open Home' })
    vim.keymap.set('n', '<leader>zt', ':UrtextAction insert_timestamp<CR>', { desc = 'Urtext: Insert Timestamp' })
    vim.keymap.set('n', '<leader>zr', ':UrtextAction random_node<CR>', { desc = 'Urtext: Copy Link Here' })
    vim.keymap.set('n', '<leader>zo', ':UrtextAction file_outline<CR>', { desc = 'Ur~/.local/share/nvim/lazy/urtext_neovim/syntax/urtext.vimtext: File Outline Dropdown' })
    vim.keymap.set('n', '<leader>zm', ':UrtextAction browse_metadata<CR>', { desc = 'Urtext: Find By Meta' })
    vim.keymap.set('n', '<leader>zB', ':UrtextAction node_browser_all_projects<CR>', { desc = 'Urtext: All Projects Node Browser' })
    vim.keymap.set('n', '<leader>z1', ':UrtextAction backlinks_browser<CR>', { desc = 'Urtext: Backlinks Browser' })
    vim.keymap.set('n', '<leader>z2', ':UrtextAction forward_links_browser<CR>', { desc = 'Urtext: Forward Links Browser' })
    vim.keymap.set('n', '<leader>zc', ':UrtextAction copy_link_to_here<CR>', { desc = 'Urtext: Copy Link Here' })
    vim.keymap.set('n', '<leader>zC', ':UrtextAction copy_link_to_here_with_project<CR>', { desc = 'Urtext: Copy Link Here With Project' })
    vim.keymap.set('n', '<leader>z[', ':UrtextAction go_to_frame<CR>', { desc = 'Urtext: Go to Frame' })
    vim.keymap.set('n', '<leader>zl', ':UrtextAction link_to_node<CR>', { desc = 'Urtext: Nav Forward' })
    vim.keymap.set('n', '<leader>z8', ':UrtextAction next_node<CR>', { desc = 'Urtext: Next Node' })
    vim.keymap.set('n', '<leader>z9', ':UrtextAction previous_node<CR>', { desc = 'Urtext: Previous Node' })
    vim.keymap.set('n', '<leader>z.', ':UrtextAction pop<CR>', { desc = 'Urtext: Pop' })
    vim.keymap.set('n', '<leader>z,', ':UrtextAction pull<CR>', { desc = 'Urtext: Pull' })
    vim.keymap.set('n', '<leader>zs', ':UrtextAction rename_single_file<CR>', { desc = 'Urtext: Rename Single File' })
    vim.keymap.set('n', '<leader>zp', ':UrtextAction select_project<CR>', { desc = 'Urtext: Select Project' })
end

return M
