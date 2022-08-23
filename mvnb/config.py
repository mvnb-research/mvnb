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
        pass

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
        return raw or "__fork('__address__')"

    @option(help="callback code", metavar="<code>")
    def callback(self, raw):
        return raw or "__callback('__url__', '__message__')"


_package = __package__.split(".")[0]

_parser = Parser(_package, Config)
