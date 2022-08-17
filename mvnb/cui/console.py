from asyncio import new_event_loop
from functools import singledispatchmethod
from shlex import split
from sys import stdin

from mvnb.cui.client import Client
from mvnb.cui.command import Command, Create, Exit, Goto, Run, Update
from mvnb.cui.reader import Reader
from mvnb.data._data import CreateCell, ForkCell, RunCell, Stdout, UpdateCell
from mvnb.util.config import Config


def main(args=None):
    config = Config.from_args(args)
    start(config)


def start(config):
    console = _Console(config)
    loop = new_event_loop()
    loop.run_until_complete(console.connect())
    _repl(lambda: loop.run_until_complete(console.run()))


class _Console(object):
    def __init__(self, config):
        self.config = config
        self.reader = Reader(config)
        self.client = Client(config, self.handle_output)
        self.cell = None
        self.code = None
        self.line = None

    async def connect(self):
        await self.client.connect()

    async def run(self):
        txt = self.read_command()
        if toks := split(txt):
            try:
                cmd = Command.from_args(toks)
            except SystemExit:
                raise _Error()
            if cmd:
                await self.handle_command(cmd)
            else:
                raise _Error(f"unknown command: {toks[0]}")

    def read_command(self):
        txt = self.reader.command_input(f"{self.cell or ''}> ")
        txt = self.config.command_prefix.sub("", txt)
        txt = self.config.command_suffix.sub("", txt)
        return txt

    def read_code(self):
        self.code = ""
        self.line = 1
        _repl(self.read_code_line)

    def read_code_line(self):
        i = self.reader.code_input(f"{self.cell}:{self.line}> ")
        if self.config.code_end.match(i):
            raise EOFError()
        self.code += f"{i}\n"
        self.line += 1

    @singledispatchmethod
    async def handle_command(self, _):
        pass

    @handle_command.register(Goto)
    async def _(self, cmd):
        self.cell = cmd.cell

    @handle_command.register(Create)
    async def _(self, cmd):
        if self.cell:
            msg = ForkCell(cell=cmd.cell, parent=self.cell)
            await self.client.send(msg)
            self.cell = cmd.cell
        else:
            msg = CreateCell(cell=cmd.cell)
            await self.client.send(msg)
            self.cell = cmd.cell

    @handle_command.register(Update)
    async def _(self, _):
        self.read_code()
        msg = UpdateCell(cell=self.cell, code=self.code)
        await self.client.send(msg)

    @handle_command.register(Run)
    async def _(self, _):
        msg = RunCell(cell=self.cell)
        await self.client.send(msg)

    @handle_command.register(Exit)
    async def _(self, _):
        raise _Exit()

    @singledispatchmethod
    async def handle_output(self, _):
        pass

    @handle_output.register(Stdout)
    async def _(self, msg):
        print(msg.text, end="")


class _Error(Exception):
    pass


class _Exit(Exception):
    pass


def _repl(func):
    while True:
        try:
            func()
        except _Error as e:
            if s := str(e):
                print(s)
        except _Exit:
            break
        except KeyboardInterrupt:
            stdin.isatty() and print()
        except EOFError:
            stdin.isatty() and print()
            break
