from asyncio import new_event_loop
from functools import singledispatchmethod
from os import isatty
from shlex import split
from sys import stdin

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from mvnb.client import Client
from mvnb.command import Command, Create, Goto, Run, Update
from mvnb.data import CreateCell, ForkCell, RunCell, Stdout, UpdateCell


def start(config):
    console = _Console(config)
    loop = new_event_loop()
    loop.run_until_complete(console.connect())
    _repl(lambda: loop.run_until_complete(console.run()))


class _Console(object):
    def __init__(self, config):
        self.config = config
        self.isatty = stdin.isatty()
        self.command_reader = None
        self.code_reader = None
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
        txt = self.input_command(f"{self.cell or ''}> ")
        txt = self.config.command_prefix.sub("", txt)
        txt = self.config.command_suffix.sub("", txt)
        return txt

    def read_code(self):
        self.code = ""
        self.line = 1
        _repl(self.read_code_line)

    def read_code_line(self):
        i = self.input_code(f"{self.cell}:{self.line}> ")
        if self.config.code_end.match(i):
            raise EOFError()
        self.code += f"{i}\n"
        self.line += 1

    def input_command(self, prompt):
        if self.isatty:
            if self.command_reader is None:
                self.command_reader = _prompt_session(self.config.command_history)
            return self.command_reader.prompt(prompt, in_thread=True)
        return self.input(prompt)

    def input_code(self, prompt):
        if self.isatty:
            if self.code_reader is None:
                self.code_reader = _prompt_session(self.config.code_history)
            return self.code_reader.prompt(prompt, in_thread=True)
        return self.input(prompt)

    def input(self, prompt):
        i = input(prompt)
        print(i)
        return i

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

    @singledispatchmethod
    async def handle_output(self, _):
        pass

    @handle_output.register(Stdout)
    async def _(self, msg):
        print(msg.text, end="")


class _Error(Exception):
    pass


def _prompt_session(history):
    return PromptSession(history=FileHistory(history))


def _repl(func):
    while True:
        try:
            func()
        except _Error as e:
            if s := str(e):
                print(s)
        except KeyboardInterrupt:
            pass
        except EOFError:
            break
