from importlib.metadata import version
from json import load
from pathlib import Path
from re import compile
from shlex import split
from sys import executable

from mvnb.option import Parser, group, option
from mvnb.record import Record
from mvnb.server import _bootstrap

_package = __package__.split(".")[0]

_version = version(_package)

_config_file = Path(f"{_package}.json")


class Config(Record):

    meta = group("meta options")

    @option(help="server address", metavar="<addr>")
    def addr(self, raw):
        return raw or "localhost"

    @option(help="server port", metavar="<port>")
    def port(self, raw):
        return int(raw or 8000)

    @option(help="repl command", metavar="<repl>")
    def repl(self, raw):
        raw = self._text_or_file(raw)
        return split(raw or f"'{executable}' -i '{_bootstrap.__file__}'")

    @option(help="fork code", metavar="<code>")
    def fork(self, raw):
        return raw or "__mvnb_fork('__address__')"

    @option(help="callback code", metavar="<code>")
    def callback(self, raw):
        return raw or "__mvnb_callback('__url__', '__message__')"

    @option(help="prompt pattern", metavar="<regex>")
    def prompt(self, raw):
        pat = raw or r"^((>>> )|(\.\.\. ))$"
        return compile(pat.encode())

    @meta
    @option(help="show help", action="help")
    def help(self, _):
        pass

    @meta
    @option(help="show version", action="version", version=_version)
    def version(self, _):
        pass

    @meta
    @option(help="path to config file", metavar="<path>")
    def config_file(self, raw):
        return raw

    @classmethod
    def from_args(cls, args):
        parser = Parser(_package, cls)
        config = Config(**parser.parse(args))
        config._load_config_file()
        return config

    def _load_config_file(self):
        if self.config_file:
            self._load_path(self.config_file)
        elif _config_file.exists():
            self._load_path(_config_file)

    def _load_path(self, path):
        with open(path) as f:
            self.setdefault(**load(f))

    def _text_or_file(self, val):
        if val is None:
            return None
        if val.startswith("@"):
            return Path(val).read_text()
        return val
