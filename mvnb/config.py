from importlib.metadata import version
from pathlib import Path
from shlex import split
from sys import executable

from mvnb import _bootstrap, _preprocessor
from mvnb.option import Parser, option
from mvnb.record import Record


class Config(Record):
    def __init__(self, args):
        super().__init__(**_parser.parse(args))

    @option(help="show help", action="help")
    def help(self, _):
        pass  # pragma: no cover

    @option(help="show version", action="version")
    def version(self, _):
        return version(_package)

    @option(help="server address", metavar="<addr>")
    def addr(self, raw):
        return raw or "0.0.0.0"

    @option(help="server port", metavar="<port>")
    def port(self, raw):
        return int(raw or 8000)

    @option(help="repl command", metavar="<repl>")
    def repl(self, raw):
        return split(raw) if raw else [executable, "-i", _bootstrap.__file__]

    @option(help="preprocessor command", metavar="<preproc>")
    def preproc(self, raw):
        return split(raw) if raw else [executable, _preprocessor.__file__]

    @option(help="before-run code", metavar="<code>")
    def before_run(self, raw):
        return self._text_or_file(raw)

    @option(help="after-run code", metavar="<code>")
    def after_run(self, raw):
        return self._text_or_file(raw)

    @option(help="fork code", metavar="<code>")
    def fork(self, raw):
        default = f"__mvnb_fork('{self.fork_addr}')"
        return self._text_or_file(raw) or default

    @option(help="callback code", metavar="<code>")
    def callback(self, raw):
        default = f"__mvnb_callback('{self.callback_url}', '{self.callback_message}')"
        return self._text_or_file(raw) or default

    @option(help="file prefix", metavar="<text>")
    def file_prefix(self, raw):
        return raw or "@"

    @option(help="fork address placeholder", metavar="<text>")
    def fork_addr(self, raw):
        return raw or "__address__"

    @option(help="callback url placeholder", metavar="<text>")
    def callback_url(self, raw):
        return raw or "__url__"

    @option(help="callback message placeholder", metavar="<text>")
    def callback_message(self, raw):
        return raw or "__message__"

    def _text_or_file(self, raw):
        if raw is None:
            return None
        if raw.startswith(self.file_prefix):
            path = raw[len(self.file_prefix) :]
            return Path(path).read_text()
        return raw


_package = __package__.split(".")[0]

_parser = Parser(_package, Config)
