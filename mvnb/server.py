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
from mvnb.worker import Worker


class Server(Application):
    def __init__(self, config):
        self._config = config
        self._users = set()
        self._cells = {}
        self._workers = bidict()
        self._notebook = Notebook()
        self._requests = Queue(self._handle_request)
        self._responses = Queue(self._handle_response)
        super().__init__([self._message_handler, self._callback_handler])

    async def start(self):
        self.listen()
        req = self._requests.start()
        res = self._responses.start()
        await wait([req, res], return_when=FIRST_COMPLETED)

    def listen(self):
        return super().listen(address=self._config.addr, port=self._config.port)

    @property
    def _message_handler(self):
        args = dict(users=self._users, requests=self._requests)
        return r"/message", MessageHandler, args

    @property
    def _callback_handler(self):
        args = dict(func=self._callback)
        return r"/callback", CallbackHandler, args

    @singledispatchmethod
    async def _handle_request(self, _):
        pass

    @_handle_request.register(CreateCell)
    async def _(self, message):
        if message.parent:
            await self._create_cell(message)
        else:
            await self._fork_cell(message)

    async def _create_cell(self, message):
        parent = self._workers[self._cells[message.parent].id]
        worker = Worker(self._config, self._responses.put)
        addr, recv = _socket_address(), Event()
        coro = worker.start_fork(message, addr, recv)
        create_task(coro)
        await recv.wait()
        await parent.put(message, addr)

    async def _fork_cell(self, message):
        worker = Worker(self._config, self._responses.put)
        await worker.start_root(message, self._config.repl)

    @_handle_request.register(UpdateCell)
    async def _(self, message):
        res = DidUpdateCell(request=message)
        await self._responses.put(res)

    @_handle_request.register(RunCell)
    async def _(self, message):
        cell = self._cells[message.cell]
        await self._workers[cell.id].put(message, cell.source)

    @singledispatchmethod
    async def _handle_response(self, message, _):
        await self._broadcast(message)

    @_handle_response.register(DidCreateCell)
    async def _(self, message, sender):
        cell = Cell(id=message.request.cell, parent=message.request.parent)
        self._notebook.cells.append(cell)
        self._cells[cell.id] = cell
        self._workers[cell.id] = sender
        await self._broadcast(message)

    @_handle_response.register(DidUpdateCell)
    async def _(self, message):
        cell = self._cells[message.request.cell]
        cell.source = message.request.source
        await self._broadcast(message)

    @_handle_response.register(Stdout)
    async def _(self, message, sender):
        cell = self._cells[self._workers.inverse[sender]]
        message.cell = cell.id
        out = Output(type="text", data=message.text)
        cell.outputs.append(out)
        await self._broadcast(message)

    async def _callback(self, message):
        res = DidRunCell(request=message)
        await self._broadcast(res)

    async def _broadcast(self, message):
        json = message.to_json()
        for user in self._users:
            await user.write_message(json)


def _socket_address():
    return f"{gettempdir()}/{uuid4().hex}.sock"
