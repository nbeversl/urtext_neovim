local telescope = require("telescope.builtin")
local pickers = require("telescope.pickers")
local finders = require("telescope.finders")
local sorters = require("telescope.sorters")
local actions = require("telescope.actions")
local action_state = require("telescope.actions.state")

local M = {}

-- Handle different line ending formats automatically
vim.opt.fileformats = "unix,dos,mac"

-- Word Wrap for Urtext file type
-- Global prose word wrap
vim.opt.wrap = true
vim.opt.linebreak = true
vim.opt.breakindent = true

local function safe_require(mod)
    local ok, m = pcall(require, mod)
    if not ok then return nil end
    return m
end

function M.open_telescope()
    local pickers = safe_require("telescope.pickers")
    local finders = safe_require("telescope.finders")
    local actions = safe_require("telescope.actions")
    local action_state = safe_require("telescope.actions.state")
    local tconf_values = safe_require("telescope.config")
    if not (pickers and finders and actions and action_state and tconf_values) then
        vim.notify("Telescope is required for Urtext picker", vim.log.levels.ERROR)
        return
    end
    local conf = tconf_values.values

    local items = vim.g.my_plugin_items or {}
    pickers.new({}, {
        prompt_title = "Urtext Actions",
        finder = finders.new_table { results = items },
        sorter = conf.generic_sorter({}),
        attach_mappings = function(prompt_bufnr)
            actions.select_default:replace(function()
                local selection = action_state.get_selected_entry()
                actions.close(prompt_bufnr)
                vim.cmd('UrtextCallback ' .. tostring(selection.index))
            end)
            return true
        end,
    }):find()
end

function M.open_file_picker()
    local builtin = safe_require("telescope.builtin")
    local pickers = safe_require("telescope.pickers")
    local finders = safe_require("telescope.finders")
    local actions = safe_require("telescope.actions")
    local action_state = safe_require("telescope.actions.state")
    local tconf_values = safe_require("telescope.config")
    if not (pickers and finders and actions and action_state and tconf_values and builtin) then
        vim.notify("Telescope is required for Urtext file picker", vim.log.levels.ERROR)
        return
    end
    local conf = tconf_values.values

    local allow_folders = tonumber(vim.g.urtext_allow_folders or 0) == 1
    local start_dir = vim.g.urtext_start_dir or vim.loop.cwd()

    if not allow_folders then
        builtin.find_files({
            cwd = start_dir,
            attach_mappings = function(prompt_bufnr)
                actions.select_default:replace(function()
                    local selection = action_state.get_selected_entry()
                    actions.close(prompt_bufnr)
                    local path = selection.path or selection.value
                    -- Ensure absolute path
                    if path and not path:match('^/') then
                        path = vim.fn.fnamemodify(start_dir .. "/" .. path, ":p")
                    else
                        path = vim.fn.fnamemodify(path, ":p")
                    end
                    vim.cmd(string.format("UrtextFilePicked %s", vim.fn.shellescape(path)))
                end)
                return true
            end,
        })
        return
    end

    local function list_dirs(path)
        local uv = vim.loop
        local dirs = {}
        local fd = uv.fs_scandir(path)
        if not fd then return dirs end
        while true do
            local name, t = uv.fs_scandir_next(fd)
            if not name then break end
            if t == 'directory' then table.insert(dirs, name .. '/') end
        end
        table.sort(dirs)
        return dirs
    end

    local function browse_dir(dir)
        local entries = { '[Select this folder]', '../' }
        for _, d in ipairs(list_dirs(dir)) do table.insert(entries, d) end
        pickers.new({}, {
            prompt_title = 'Select folder: ' .. dir,
            finder = finders.new_table { results = entries },
            sorter = conf.generic_sorter({}),
            attach_mappings = function(prompt_bufnr)
                actions.select_default:replace(function()
                    local selection = action_state.get_selected_entry().value
                    actions.close(prompt_bufnr)
                    if selection == '[Select this folder]' then
                        -- Ensure absolute path for selected folder
                        local abs_dir = vim.fn.fnamemodify(dir, ":p")
                        vim.cmd(string.format("UrtextFilePicked %s", vim.fn.shellescape(abs_dir)))
                        return
                    end
                    local next_dir
                    if selection == '../' then
                        next_dir = vim.fn.fnamemodify(dir, ':h')
                    else
                        next_dir = dir .. '/' .. selection:gsub('/$', '')
                    end
                    browse_dir(next_dir)
                end)
                return true
            end,
        }):find()
    end

    browse_dir(start_dir)
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
