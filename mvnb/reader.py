from readline import (
    clear_history,
    read_history_file,
    set_history_length,
    write_history_file,
)
from sys import stdin


class Reader(object):
    def __init__(self, config):
        self._config = config
        self._history_file = None

    def command_input(self, prompt):
        self._switch_history(self._config.command_history)
        return self._input(prompt)

    def code_input(self, prompt):
        self._switch_history(self._config.code_history)
        return self._input(prompt)

    def save_history(self):
        if self._history_file:
            write_history_file(self._history_file)

    def _input(self, prompt):
        i = input(prompt)
        stdin.isatty() or print(i)
        return i

    def _switch_history(self, path):
        if path is not self._history_file:
            self.save_history()
            self._load_history(path)
            self._history_file = path

    def _load_history(self, path):
        clear_history()
        if path.exists():
            read_history_file(path)
            set_history_length(999)
