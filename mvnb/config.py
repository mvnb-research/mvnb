from importlib.metadata import version
from shlex import split
from sys import executable

from mvnb import _bootstrap
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
        return raw or "localhost"

    @option(help="server port", metavar="<port>")
    def port(self, raw):
        return int(raw or 8000)

    @option(help="repl command", metavar="<repl>")
    def repl(self, raw):
        return split(raw) if raw else [executable, "-i", _bootstrap.__file__]

    @option(help="fork code", metavar="<code>")
    def fork(self, raw):
        return raw or f"__fork('{self.fork_addr}')"

    @option(help="callback code", metavar="<code>")
    def callback(self, raw):
        return raw or f"__callback('{self.callback_url}', '{self.callback_message}')"

    @option(help="fork address placeholder", metavar="<text>")
    def fork_addr(self, raw):
        return raw or "__address__"

    @option(help="callback url placeholder", metavar="<text>")
    def callback_url(self, raw):
        return raw or "__url__"

    @option(help="callback message placeholder", metavar="<text>")
    def callback_message(self, raw):
        return raw or "__message__"


_package = __package__.split(".")[0]

_parser = Parser(_package, Config)
