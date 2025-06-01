from urtext.project_list import ProjectList
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

    @pynvim.command('Urtest', nargs='*')
    def load(self, args):
        editor_methods = {
            'open_file_to_position': self.open_file_to_position,
            'get_line_and_cursor': self.get_line_and_cursor,
            'info_message' : self.info_message,
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
            'write_to_console' : self.nvim.out_write,
            'get_current_folder': self.get_current_folder,
            'status_message' : self.nvim.out_write,
            'close_file': self.close_file,
            'save_file': self.save_file,
            'retarget_view' : self.retarget_view,
            # 'select_file_or_folder': select_file_or_folder,
            # 'refresh_files' : refresh_views,
            # 'get_open_files': get_open_files,
            # 'preview_file_at_position' : preview_file_at_position,
            # 'close_inactive': close_inactive,
            # 'open_file_dialog': open_file_dialog,
            'set_position': self.set_position,
            # 'hover_popup': hover_popup,
            # 'get_selection': get_selection
        }
        self.project_list = ProjectList("/Users/nathanielbeversluis/Documents/Urtext Projects/Urtext Development",
            editor_methods=editor_methods)

    @pynvim.command('UrAction', nargs='*')
    def action(self, args):
        if len(args):
            self.project_list.run_action(args[0])

    def get_current_folder(self):
        path = self.nvim.current.buffer.name
        return os.path.dirname(path) if path else None

    @pynvim.autocmd('BufWritePost', pattern='*', sync=True, eval='expand("<afile>")')
    def on_buf_write_post(self, filename):
        self.project_list.on_modified(filename)

    def show_panel(self, selections, callback, on_highlight=None):
        self.urtext_callback = callback
        if len(selections) and isinstance(selections[0],list):
            selections = [i[0] for i in selections]
        self.nvim.vars['my_plugin_items'] = selections
        self.nvim.command('lua require("urtext").open_telescope()')

    @pynvim.command('UrtextCallback', nargs='*', sync=True)
    def on_selected(self, args):
        if self.urtext_callback:
            arg0 = args[0]
            arg0 = arg0.strip("'\"")
            idx = int(arg0) 
            self.urtext_callback(idx-1)

    def get_buffer(self, filename):
        self.nvim.async_call(self._get_buffer, filename)

    def _get_buffer(self, filename):
        for buf in self.nvim.buffers:
            if buf.name == filename:
                return "\n".join(buf[:])

    def set_buffer(self, contents):
        self.nvim.current.buffer[:] = contents.split("\n")

    def insert_text(self, text):
        def _insert():
            buf = self.nvim.current.buffer
            row, col = self.nvim.current.window.cursor
            line = buf[row - 1]
            new_line = line[:col] + text + line[col:]
            buf[row - 1] = new_line
            self.nvim.current.window.cursor = (row, col + len(text))
        self.nvim.async_call(_insert)

    def open_file_to_position(self, filename, line=None, character=None, highlight_range=None, new_window=False):
        self.nvim.async_call(self.nvim.command, ':enew')
        self.nvim.async_call(self.nvim.command, ':e '+filename)
        if character:
            self.set_position(character)

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
        self.nvim.async_call(_set_position)

    def get_current_filename(self):
        return self.nvim.current.buffer.name

    def find_buffer_by_path(self, full_path):
        for buf in self.nvim.buffers:
            if buf.name == full_path:
                return buf

    def scratch_buffer(self, contents):
        self.nvim.async_call(self.nvim.command, ':enew')
        buf = self.nvim.current.buffer
        buf.options['buftype'] = 'nofile'
        buf[:] = contents

    def save_current(self):
        self.nvim.command('write') 

    def get_position(self):
        full_line, col_pos, file_pos, [file_pos, file_pos] = self.get_line_and_cursor()
        self.info_message(str(file_pos))
        return file_pos

    def info_message(self, message):
        self.nvim.async_call(self.nvim.api.notify, message, 3, {})

    def get_line_and_cursor(self):
        full_line = self.nvim.current.line
        [row, col_pos] = self.nvim.current.window.cursor
        lines_before = self.nvim.current.buffer[:row - 1]
        chars_before = sum(len(l) + 1 for l in lines_before) 
        file_pos = chars_before + col_pos
        return full_line, col_pos, file_pos, [file_pos, file_pos]

    def set_clipboard(self, string):
        self.nvim.funcs.setreg('+', string)

    def replace(self, filename='', start=0, end=0, full_line=False, replacement_text=''):
        if filename:
            buf = self.find_buffer_by_path(filename)
        else:
            buf = self.nvim.current.buffer
        buf[start:end] = replacement_text

    def open_external_file(self, filepath):
        if sys.platform.startswith('darwin'):
            subprocess.run(['open', filepath])
        elif sys.platform.startswith('linux'):
            subprocess.run(['xdg-open', filepath])
        elif sys.platform.startswith('win'):
            os.startfile(filepath)

    def close_current(self):
        self.nvim.command('bdelete')

    def close_file(self, filename):
        buffer = self.find_buffer_by_path(filename)
        if buffer:
            if buffer.options['modified']:
                self.nvim.command(f'confirm bdelete {buffer.number}')
            else:
                self.nvim.command(f'bdelete {buffer.number}')

    def save_file(self, filename):
        buffer = self.find_buffer_by_path(filename)
        if buffer:
            self.nvim.command(f'write {buffer.number}')

    def retarget_view(self, filename):
        buffer = self.find_buffer_by_path(filename)
        if buffer:
            self.nvim.command(f"checktime {buffer.number}")


