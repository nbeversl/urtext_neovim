from urtext.project_list import ProjectList
import re
import subprocess
import threading
import pynvim
import sys
import os

@pynvim.plugin
class UrtextNeoVim:
    def __init__(self, nvim):
        self.nvim = nvim
        self.urtext_callback = None
        self._last_line_cursor = None  # (full_line, col_pos, file_pos, [file_pos, file_pos])
        self._last_filename = None
        self._main_thread = threading.current_thread()
        self._last_selections_count = 0
        self.project_list = None
        self.editor_methods = {
            'open_file_to_position': self.open_file_to_position,
            'get_line_and_cursor': self.nvim_get_line_and_cursor,
            'info_message' : self.info_message,
            'error_message' : self.error_message,
            'get_current_filename': self.get_current_filename,
            'get_position': self.get_position,
            'scratch_buffer': self.scratch_buffer,
            'get_buffer':self.get_buffer,
            'set_buffer': self.set_buffer,
            'show_panel': self.show_panel,
            'insert_text' : self.insert_text,
            'save_current' : self.save_current,
            'set_clipboard' : self.set_clipboard,
            'open_external_file' : self.open_external_file,
            'replace' : self.replace,
            'close_current': self.close_current,
            'write_to_console' : self.write_to_console,
            'get_current_folder': self.get_current_folder,
            'status_message' : self.write_to_console,
            'close_file': self.close_file,
            'save_file': self.save_file,
            'retarget_view' : self.retarget_view,
            'refresh_files' : self.refresh_files,
            'get_open_files': self.get_open_files,
            # 'select_file_or_folder': select_file_or_folder,
            # 'get_open_files': get_open_files,
            # 'preview_file_at_position' : preview_file_at_position,
            # 'close_inactive': close_inactive,
            'open_file_dialog': self.open_file_dialog,
            'set_position': self.set_position,
            # 'hover_popup': hover_popup,
            # 'get_selection': get_selection
        }

    def _run_on_main_and_wait(self, func, *args, **kwargs):
        # If already on the main thread (e.g., synchronous RPC handler), call directly
        if threading.current_thread() is self._main_thread:
            return func(*args, **kwargs)
        # Otherwise, schedule on main and wait
        result = {}
        error = {}
        event = threading.Event()

        def _wrapper():
            result['value'] = func(*args, **kwargs)
            event.set()

        self.nvim.async_call(_wrapper)
        event.wait()
        if 'exc' in error:
            raise error['exc']
        return result.get('value')

    @pynvim.command('Urtext', nargs='*')
    def load(self, args):
        open_file = self.get_current_filename()

        if open_file:
            if self.project_list is None:
                self.project_list = ProjectList(open_file, editor_methods=self.editor_methods)
            else:
                self.project_list.init_project(open_file)

    @pynvim.command('UrtextAction', nargs='*')
    def action(self, args):
        if len(args):
            selection = ' '.join(args)
            if not self.project_list:
                self.info_message('No Urtext project is active')
                return
            self.project_list.run_action(selection)

    def get_current_folder(self):
        name = self.get_current_filename()
        return os.path.dirname(name) if name else None

    @pynvim.autocmd('BufWritePost', pattern='*', sync=True, eval='expand("<afile>")')
    def on_buf_write_post(self, filename):
        if self.project_list:
            self.project_list.on_modified(os.path.abspath(filename))

    @pynvim.autocmd('BufEnter', pattern='*', sync=False, eval='expand("<afile>")')
    def on_buf_enter(self, filename):
        # Keep main thread identity stable; do not reset here
        self._last_filename = filename
        self._schedule_update_line_cursor()

    @pynvim.autocmd('CursorMoved', pattern='*', sync=False)
    def on_cursor_moved(self):
        self._schedule_update_line_cursor()

    @pynvim.autocmd('CursorMovedI', pattern='*', sync=False)
    def on_cursor_moved_insert(self):
        self._schedule_update_line_cursor()

    @pynvim.autocmd('TextChanged', pattern='*', sync=False)
    def on_text_changed(self):
        self._schedule_update_line_cursor()

    @pynvim.autocmd('TextChangedI', pattern='*', sync=False)
    def on_text_changed_insert(self):
        self._schedule_update_line_cursor()

    def _schedule_update_line_cursor(self):
        def _update():
            self._last_line_cursor = self._compute_line_cursor()
        self.nvim.async_call(_update)

    def _compute_line_cursor(self):
        buf = self.nvim.current.buffer
        row, col_pos = self.nvim.current.window.cursor
        row_index = max(0, row - 1)
        full_line = buf[row_index] if row_index < len(buf) else ''
        lines_before = buf[:row_index]
        chars_before = sum(len(l) + 1 for l in lines_before)
        file_pos = chars_before + col_pos
        start_of_line = chars_before
        end_of_line = chars_before + len(full_line)
        return (full_line, col_pos, file_pos, [start_of_line, end_of_line])

    def show_panel(self, selections, callback, on_highlight=None):
        # Store selections and callbacks
        self.urtext_callback = callback
        self._callback_expects_value = False
        self._selections = selections
        # Build a display list preserving order and an index-to-id map when needed
        if len(selections) and isinstance(selections[0], list):
            display = [i[0] for i in selections]
        else:
            display = selections

        def cb():
            self.nvim.vars['my_plugin_items'] = display
            self.nvim.command('lua require("urtext").open_telescope()')

        self.nvim.async_call(cb)

    def open_file_dialog(self, callback, allow_folders=False):
        # Use Telescope to pick files/folders; synchronous return via callback invocation
        self.urtext_callback = callback
        self._callback_expects_value = True
        def _cb():
            self.nvim.vars['urtext_allow_folders'] = 1 if allow_folders else 0
            # start directory = current buffer's folder
            start_dir = os.path.dirname(self.get_current_filename())
            if start_dir:
                self.nvim.vars['urtext_start_dir'] = start_dir
            self.nvim.command('lua require("urtext").open_file_picker()')
        self.nvim.async_call(_cb)

    @pynvim.command('UrtextFilePicked', nargs='*', sync=True)
    def on_file_picked(self, args):
        # receives a single arg: full path string
        if not self.urtext_callback:
            return ''
        if not args:
            return ''
        a0 = args[0]
        selected = a0[0] if isinstance(a0, list) and a0 else a0
        selected = str(selected).strip("'\"")
        cb = self.urtext_callback
        self.urtext_callback = None
        cb(selected)
        return selected


    @pynvim.command('UrtextCallback', nargs='*', sync=True)
    def on_selected(self, args):
        if not self.urtext_callback:
            return -1
        if not args:
            return -1
        a0 = args[0]
        s = a0[0] if isinstance(a0, list) and a0 else a0
        s = str(s).strip("'\"")
        cb = self.urtext_callback
        # If a raw value was expected (e.g., file picker), pass it through
        if getattr(self, '_callback_expects_value', False):
            # Clear state before invoking to avoid stale state if callback errors
            self.urtext_callback = None
            self._callback_expects_value = False
            self._selections = None
            cb(s)
            return s
        # Otherwise expect a 1-based index and convert to 0-based
        if not s.isdigit():
            return -1
        idx0 = int(s) - 1
        if hasattr(self, '_selections') and self._selections is not None:
            if not (0 <= idx0 < len(self._selections)):
                return -1
        # Clear state before invoking to avoid stale state if callback errors
        self.urtext_callback = None
        self._callback_expects_value = False
        self._selections = None
        cb(idx0)
        return idx0

    def get_buffer(self, filename):
        def _do():
            # 1. Try to resolve by filename directly
            bufnr = self.nvim.funcs.bufnr(filename, 0)  # 0 = don't create if missing
            if bufnr > 0 and self.nvim.funcs.bufexists(bufnr):
                return "\n".join(self.nvim.funcs.getbufline(bufnr, 1, '$'))

            # 2. If still not found, create/load it without opening
            bufnr = self.nvim.funcs.bufadd(filename)
            self.nvim.buffers[bufnr].options['swapfile'] = False

            # Remove stale swap if present
            swap_path = self.nvim.funcs.swapname(bufnr)
            if isinstance(swap_path, str) and swap_path and os.path.exists(swap_path):
                os.remove(swap_path)

            self.nvim.funcs.bufload(bufnr)

            if self.nvim.funcs.bufexists(bufnr):
                return "\n".join(self.nvim.funcs.getbufline(bufnr, 1, '$'))

            return ""

        return self._run_on_main_and_wait(_do)


    def set_buffer(self, filename, contents, identifier=None):
        def _do():
            target = None
            if filename:
                for b in self.nvim.buffers:
                    if b.name == filename:
                        target = b
                        break
            if target is None:
                target = self.nvim.current.buffer
            target[:] = (contents or '').split("\n")
        self._run_on_main_and_wait(_do)

    def insert_text(self, text):
        def _do():
            buf = self.nvim.current.buffer
            row, col = self.nvim.current.window.cursor
            line = buf[row - 1]
            new_line = line[:col] + text + line[col:]
            buf[row - 1] = new_line
            self.nvim.current.window.cursor = (row, col + len(text))
        self._run_on_main_and_wait(_do)

    def open_file_to_position(self, filename, line=None, character=None, highlight_range=None, new_window=False):
        def _do():
            # Save current buffer if possible
            cur = self.nvim.current.buffer
            if cur.valid and cur.options.get("modifiable", True) and cur.name:
                if self.nvim.funcs.getbufvar(cur.number, "&modified"):
                    self.nvim.command("silent write")

            # Find or create target buffer
            bufnr = self.nvim.funcs.bufnr(filename, 0)
            if bufnr <= 0 or not self.nvim.funcs.bufexists(bufnr):
                bufnr = self.nvim.funcs.bufadd(filename)
                self.nvim.buffers[bufnr].options["swapfile"] = False
                swap_path = self.nvim.funcs.swapname(bufnr)
                if isinstance(swap_path, str) and swap_path and os.path.exists(swap_path):
                    os.remove(swap_path)
                self.nvim.funcs.bufload(bufnr)

            # Switch directly via API (bypasses E37)
            self.nvim.api.set_current_buf(self.nvim.buffers[bufnr])

            if character:
                self.set_position(character)

        self._run_on_main_and_wait(_do)

    def set_position(self, char_pos):
        def _set_position():
            buf = self.nvim.current.buffer
            text = "\n".join(buf[:])
            if char_pos > len(text):
                char_pos_ = len(text)
            else:
                char_pos_ = char_pos
            lines = text[:char_pos_].split('\n')
            line_num = len(lines)
            col_num = len(lines[-1])
            self.nvim.current.window.cursor = (line_num, col_num)
        self._run_on_main_and_wait(_set_position)

    async def get_current_filename(self):
        return await self.nvim_get_current_filename()

    def find_buffer_by_path(self, full_path):
        def _lookup():
            target_real = os.path.realpath(full_path)
            # Exact or realpath match
            for buf in self.nvim.buffers:
                name = buf.name
                if not name:
                    continue
                if name == full_path:
                    return buf
                if os.path.realpath(name) == target_real:
                    return buf
            return None
        return self._run_on_main_and_wait(_lookup)

    def scratch_buffer(self, contents):
        def _do():
            self.nvim.command(':enew')
            buf = self.nvim.current.buffer
            buf.options['buftype'] = 'nofile'
            buf[:] = (contents or '').splitlines()
            return buf.number
        return self._run_on_main_and_wait(_do)


    def save_current(self):
        def _do():
            self.nvim.command('write')

        self._run_on_main_and_wait(_do)

    def get_position(self):
        # Compute fresh on main thread to avoid stale cache. Return an int.
        value = self._run_on_main_and_wait(self._compute_line_cursor)
        return int(value[2])

    def info_message(self, message):
        self.nvim.async_call(self.nvim.api.notify, message, 3, {})

    def error_message(self, message):
        self.nvim.async_call(self.nvim.api.notify, message, 1, {})

    async def get_line_and_cursor(self):
        # Retained for compatibility; delegate to sync version
        return self.nvim_get_line_and_cursor()


    def set_clipboard(self, string):
        def _do():
            self.nvim.funcs.setreg('+', string)
            return string
        return self._run_on_main_and_wait(_do)

    def replace(self, filename='', start=0, end=0, full_line=False, replacement_text=''):
        def _do():
            # Access buffer directly on main thread (avoid nested waits)
            if filename:
                target_buf = None
                for b in self.nvim.buffers:
                    if b.name == filename:
                        target_buf = b
                        break
                buf = target_buf if target_buf else self.nvim.current.buffer
            else:
                buf = self.nvim.current.buffer
            # Replace by character range over the whole buffer
            text = "\n".join(buf[:])
            start_pos = max(0, min(int(start), len(text)))
            end_pos = max(0, min(int(end), len(text)))
            if end_pos < start_pos:
                start_pos, end_pos = end_pos, start_pos
            new_text = text[:start_pos] + (replacement_text or '') + text[end_pos:]
            buf[:] = new_text.split("\n")
        self._run_on_main_and_wait(_do)

    def open_external_file(self, filepath):
        if sys.platform.startswith('darwin'):
            subprocess.run(['open', filepath])
        elif sys.platform.startswith('linux'):
            subprocess.run(['xdg-open', filepath])
        elif sys.platform.startswith('win'):
            os.startfile(filepath)

    def close_current(self):
        def _do():
            self.nvim.command('bdelete!')
        self._run_on_main_and_wait(_do)

    def close_file(self, filename):
        def _do():
            buffer = self.find_buffer_by_path(filename)
            if buffer:
                # Force delete to avoid interactive prompts during RPC
                self.nvim.command(f'bdelete! {buffer.number}')
        self._run_on_main_and_wait(_do)

    def refresh_files(self, file_list):
        """Reload the given filename(s) from disk, discarding edits."""
        def _do():
            files = file_list if isinstance(file_list, list) else [file_list]
            current_bufnr = self.nvim.current.buffer.number
            for f in files:
                target_real = os.path.realpath(f)
                target = None
                for b in self.nvim.buffers:
                    name = b.name
                    if not name:
                        continue
                    if name == f or os.path.realpath(name) == target_real:
                        target = b
                        break
                if not target:
                    continue
                need_restore = (target.number != current_bufnr)
                if need_restore:
                    self.nvim.command(f"buffer {target.number}")
                self.nvim.command("silent edit!")  # reload from disk
                if need_restore:
                    self.nvim.command(f"buffer {current_bufnr}")
            return len(files)
        return self._run_on_main_and_wait(_do)


    def save_file(self, filename):
        def _do():
            buffer = self.find_buffer_by_path(filename)
            if not buffer:
                return 0
            # Remember current buffer, switch, write, and restore
            current_bufnr = self.nvim.current.buffer.number
            if current_bufnr != buffer.number:
                self.nvim.command(f'buffer {buffer.number}')
            self.nvim.command('silent write')
            if current_bufnr != buffer.number:
                self.nvim.command(f'buffer {current_bufnr}')
            return 1
        self._run_on_main_and_wait(_do)

    def retarget_view(self, *args):
        # Reload the contents of the buffer for the given filename (no window moves)
        # Supports both signatures: (filename) or (old_filename, new_filename)
        def _do():
            filename = None
            if len(args) == 1:
                filename = args[0]
            elif len(args) >= 2:
                filename = args[1]
            if not filename:
                return
            buffer = self.find_buffer_by_path(filename)
            if not buffer:
                return
            current_bufnr = self.nvim.current.buffer.number
            need_restore = current_bufnr != buffer.number
            if need_restore:
                self.nvim.command(f'buffer {buffer.number}')
            # Do not clobber modified buffers
            if self.nvim.current.buffer.options['modified']:
                if need_restore:
                    self.nvim.command(f'buffer {current_bufnr}')
                return
            # Reload from disk silently
            self.nvim.command('silent checktime')
            self.nvim.command('silent edit')
            if need_restore:
                self.nvim.command(f'buffer {current_bufnr}')
        return self._run_on_main_and_wait(_do)

    def get_open_files(self):
        def _do():
            paths = {}
            for buf in self.nvim.buffers:
                name = buf.name
                if not name:
                    continue
                buftype = buf.options['buftype']
                if buftype:
                    # Skip non-file buffers such as help, terminal, nofile
                    continue
                full_path = os.path.realpath(name)
                if full_path:
                    paths[full_path] = bool(buf.options['modified'])
            return paths
        return self._run_on_main_and_wait(_do)

    async def nvim_get_current_filename(self):
        # Retained for compatibility; prefer get_current_filename()
        return self.get_current_filename()

    def get_current_filename(self):
        # Always resolve on main thread to ensure freshness
        def _do():
            name = self.nvim.current.buffer.name
            self._last_filename = name
            return name or ''
        return self._run_on_main_and_wait(_do)

    async def nvim_write_out(self, contents):
        await self.nvim.call('nvim_out_write', contents + "\n")

    def write_to_console(self, contents):
        def _do():
            self.nvim.api.out_write((contents or '') + "\n")
        return self._run_on_main_and_wait(_do)

    def nvim_get_line_and_cursor(self):
        # Always compute synchronously on main thread to avoid stale values
        full_line, col_pos, file_pos, span = self._run_on_main_and_wait(self._compute_line_cursor)
        col_pos = int(col_pos)
        file_pos = int(file_pos)
        span = [int(span[0]), int(span[1])]
        return (full_line or '', col_pos, file_pos, span)
