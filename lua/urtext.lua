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
        -- Store selected value globally to avoid quoting issues
        vim.g.urtext_selected_value = selection.value
        actions.close(prompt_bufnr)
        -- Pass only the 1-based index; Python will convert to 0-based and prefer mapping by value
        vim.cmd('UrtextCallback ' .. tostring(selection.index))
      end)
      return true
    end,
  }):find()
end

function M.open_file_picker()
  local allow_folders = vim.g.urtext_allow_folders == 1
  local start_dir = vim.g.urtext_start_dir or vim.loop.cwd()
  local opts = {}
  if allow_folders then
    -- Use find_files but allow selecting directories via custom picker
    local seed = vim.fn.shellescape(start_dir)
    local script = [[bash -lc 'printf "%s\n" ]] .. seed .. [[ ; fd -t f -t d -H ]] .. seed .. [[ | sed 's#^\./##'']]
    pickers.new({}, {
      prompt_title = "Pick File or Folder",
      finder = finders.new_oneshot_job({ 'bash', '-lc', script }, {}),
      sorter = sorters.get_generic_fuzzy_sorter(),
      attach_mappings = function(prompt_bufnr, map)
        actions.select_default:replace(function()
          local selection = action_state.get_selected_entry()
          if not selection then return end
          actions.close(prompt_bufnr)
          local path = selection[1]
          if not vim.fn.isdirectory(path) and not vim.fn.filereadable(path) then
            path = vim.fn.fnamemodify(path, ":p")
          end
          -- Fallback: send value through the generic callback channel
          vim.g.urtext_selected_value = path
          vim.cmd('UrtextCallback ' .. vim.fn.shellescape(path))
        end)
        return true
      end,
    }):find()
  else
    telescope.find_files({ cwd = start_dir,
      attach_mappings = function(prompt_bufnr, map)
        actions.select_default:replace(function()
          local selection = action_state.get_selected_entry()
          if not selection then return end
          actions.close(prompt_bufnr)
          local path = vim.fn.fnamemodify(selection[1], ":p")
          vim.g.urtext_selected_value = path
          vim.cmd('UrtextCallback ' .. vim.fn.shellescape(path))
        end)
        return true
      end,
    })
  end
end

return M