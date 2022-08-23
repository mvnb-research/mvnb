from asyncio import (
    FIRST_COMPLETED,
    Event,
    create_task,
    new_event_loop,
    run,
    set_event_loop,
    wait,
)
from functools import singledispatchmethod
from tempfile import gettempdir
from threading import Thread
from uuid import uuid4

from bidict import bidict
from tornado.web import Application

from mvnb.config import Config
from mvnb.handler import CallbackHandler, MessageHandler
from mvnb.notebook import Cell, Notebook, Output
from mvnb.output import Stdout
from mvnb.queue import Queue
from mvnb.request import CreateCell, RunCell, UpdateCell
from mvnb.response import DidCreateCell, DidRunCell, DidUpdateCell
from mvnb.server.worker import Worker


def main(args=None):
    config = Config(args)
    server = _Server(config)
    try:
        run(server.start())
    except KeyboardInterrupt:
        pass


def start(config):
    args = config, new_event_loop()
    Thread(target=_start, args=args, daemon=True).start()


def _start(config, loop):
    set_event_loop(loop)
    server = _Server(config)
    loop.run_until_complete(server.start())


class _Server(object):
    def __init__(self, config):
        self.config = config
        self.users = set()
        self.cells = {}
        self.workers = bidict()
        self.notebook = Notebook()
        self.requests = Queue(self.handle_request)
        self.responses = Queue(self.handle_response)

    async def start(self):
        app = _Application(self.config, self.users, self.requests, self.on_callback)
        app.listen()

        req = self.requests.start()
        res = self.responses.start()
        await wait([req, res], return_when=FIRST_COMPLETED)

    async def on_callback(self, msg):
        res = DidRunCell(request=msg)
        await self.broadcast(res)

    @singledispatchmethod
    async def handle_request(self, _):
        pass

    @handle_request.register(CreateCell)
    async def _(self, msg):
        if msg.parent:
            parent = self.workers[self.cells[msg.parent].id]
            worker = Worker(self.config, self.responses.put)
            addr, recv = _socket_address(), Event()
            coro = worker.start_fork(msg, addr, recv)
            create_task(coro)
            await recv.wait()
            await parent.put(msg, addr)
        else:
            worker = Worker(self.config, self.responses.put)
            await worker.start_root(msg, self.config.repl)

    @handle_request.register(UpdateCell)
    async def _(self, msg):
        res = DidUpdateCell(request=msg)
        await self.responses.put(res)

    @handle_request.register(RunCell)
    async def _(self, msg):
        cell = self.cells[msg.cell]
        await self.workers[cell.id].put(msg, cell.source)

    @singledispatchmethod
    async def handle_response(self, msg, _):
        await self.broadcast(msg)

    @handle_response.register(DidCreateCell)
    async def _(self, msg, sender):
        cell = Cell(id=msg.request.cell, parent=msg.request.parent)
        self.notebook.cells.append(cell)
        self.cells[cell.id] = cell
        self.workers[cell.id] = sender
        await self.broadcast(msg)

    @handle_response.register(DidUpdateCell)
    async def _(self, msg):
        cell = self.cells[msg.request.cell]
        cell.source = msg.request.source
        await self.broadcast(msg)

    @handle_response.register(Stdout)
    async def _(self, msg, sender):
        cell = self.cells[self.workers.inverse[sender]]
        msg.cell = cell.id
        out = Output(type="text", data=msg.text)
        cell.outputs.append(out)
        await self.broadcast(msg)

    async def broadcast(self, msg):
        txt = msg.to_json()
        for usr in self.users:
            await usr.write_message(txt)


class _Application(Application):
    def __init__(self, config, users, requests, callback):
        self.config = config
        super().__init__(
            [
                (r"/", MessageHandler, dict(users=users, requests=requests)),
                (r"/callback", CallbackHandler, dict(func=callback)),
            ]
        )

    def listen(self):
        super().listen(address=self.config.addr, port=self.config.port)


def _socket_address():
    return f"{gettempdir()}/{uuid4().hex}.sock"
