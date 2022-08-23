from asyncio import FIRST_COMPLETED, Event, create_task, wait
from functools import singledispatchmethod
from tempfile import gettempdir
from uuid import uuid4

from bidict import bidict
from tornado.web import Application

from mvnb.handler import CallbackHandler, MessageHandler
from mvnb.notebook import Cell, Notebook, Output
from mvnb.output import Stdout
from mvnb.queue import Queue
from mvnb.request import CreateCell, RunCell, UpdateCell
from mvnb.response import DidCreateCell, DidRunCell, DidUpdateCell
from mvnb.server.worker import Worker


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

    async def on_callback(self, message):
        res = DidRunCell(request=message)
        await self.broadcast(res)

    @singledispatchmethod
    async def handle_request(self, _):
        pass

    @handle_request.register(CreateCell)
    async def _(self, message):
        if message.parent:
            parent = self.workers[self.cells[message.parent].id]
            worker = Worker(self.config, self.responses.put)
            addr, recv = _socket_address(), Event()
            coro = worker.start_fork(message, addr, recv)
            create_task(coro)
            await recv.wait()
            await parent.put(message, addr)
        else:
            worker = Worker(self.config, self.responses.put)
            await worker.start_root(message, self.config.repl)

    @handle_request.register(UpdateCell)
    async def _(self, message):
        res = DidUpdateCell(request=message)
        await self.responses.put(res)

    @handle_request.register(RunCell)
    async def _(self, message):
        cell = self.cells[message.cell]
        await self.workers[cell.id].put(message, cell.source)

    @singledispatchmethod
    async def handle_response(self, message, _):
        await self.broadcast(message)

    @handle_response.register(DidCreateCell)
    async def _(self, message, sender):
        cell = Cell(id=message.request.cell, parent=message.request.parent)
        self.notebook.cells.append(cell)
        self.cells[cell.id] = cell
        self.workers[cell.id] = sender
        await self.broadcast(message)

    @handle_response.register(DidUpdateCell)
    async def _(self, message):
        cell = self.cells[message.request.cell]
        cell.source = message.request.source
        await self.broadcast(message)

    @handle_response.register(Stdout)
    async def _(self, message, sender):
        cell = self.cells[self.workers.inverse[sender]]
        message.cell = cell.id
        out = Output(type="text", data=message.text)
        cell.outputs.append(out)
        await self.broadcast(message)

    async def broadcast(self, message):
        txt = message.to_json()
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
