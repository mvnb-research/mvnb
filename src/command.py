from random import choices
from string import ascii_lowercase

from .record import Record, argument, option


class Command(Record, abst=True, group=object()):
    @option(help="show help", action="help")
    def help(self, _):
        pass


class Goto(Command):
    @argument(help="cell name", nargs="?")
    def cell(self, raw):
        return raw


class Create(Command):
    @argument(help="cell name", nargs="?")
    def cell(self, raw):
        return raw or "".join(choices(ascii_lowercase, k=6))


class Update(Command):
    pass


class Run(Command):
    pass


class Exit(Command):
    pass
