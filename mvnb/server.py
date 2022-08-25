from asyncio import FIRST_COMPLETED, Event, create_task, wait
from functools import singledispatchmethod
from tempfile import gettempdir
from uuid import uuid4

from bidict import bidict
from tornado.web import Application

from mvnb.handler import CallbackHandler, FileHandler, MessageHandler
from mvnb.notebook import Cell, Notebook, Output
from mvnb.output import Stdout
from mvnb.queue import Queue
from mvnb.request import CreateCell, RunCell, UpdateCell
from mvnb.response import DidCreateCell, DidRunCell, DidUpdateCell
from mvnb.worker import Worker


class Server(object):
    def __init__(self, config):
        self._config = config
        self._users = set()
        self._cells = dict()
        self._workers = bidict()
        self._notebook = Notebook()
        self._requests = Queue(self._handle_request)
        self._responses = Queue(self._handle_response)
        self._http = None

    async def start(self):
        self._http = self._start_app()
        await self._start_queues()

    def stop(self):
        if self._http:
            self._http.stop()
        self._requests.stop()
        self._responses.stop()
        for worker in self._workers.values():
            worker.stop()

    def _start_app(self):
        return Application(
            [
                self._message_handler,
                self._callback_handler,
                self._file_handler,
            ]
        ).listen(address=self._config.addr, port=self._config.port)

    def _start_queues(self):
        req = self._requests.start()
        res = self._responses.start()
        return wait([req, res], return_when=FIRST_COMPLETED)

    @property
    def _message_handler(self):
        args = dict(users=self._users, requests=self._requests)
        return MessageHandler.PATH, MessageHandler, args

    @property
    def _callback_handler(self):
        args = dict(func=self._callback)
        return CallbackHandler.PATH, CallbackHandler, args

    @property
    def _file_handler(self):
        return FileHandler.PATH, FileHandler

    @singledispatchmethod
    async def _handle_request(self, _):
        raise Exception()  # pragma: no cover

    @_handle_request.register(CreateCell)
    async def _(self, request):
        if request.parent:
            await self._fork_cell(request)
        else:
            await self._create_cell(request)

    async def _create_cell(self, request):
        worker = Worker(self._config, self._responses.put)
        await worker.start_root(request)

    async def _fork_cell(self, request):
        parent = self._workers[request.parent]
        worker = Worker(self._config, self._responses.put)
        address, event = _socket_address(), Event()
        create_task(worker.start_fork(request, address, event))
        await event.wait()
        await parent.put(request, address)

    @_handle_request.register(UpdateCell)
    async def _(self, request):
        response = DidUpdateCell(request=request)
        await self._responses.put(response)

    @_handle_request.register(RunCell)
    async def _(self, request):
        cell = self._cells[request.cell]
        await self._workers[cell.id].put(request, cell.source)

    @singledispatchmethod
    async def _handle_response(self, response, _):
        raise Exception()  # pragma: no cover

    @_handle_response.register(DidCreateCell)
    async def _(self, response, sender):
        cell = Cell(id=response.request.cell, parent=response.request.parent)
        self._notebook.cells.append(cell)
        self._cells[cell.id] = cell
        self._workers[cell.id] = sender
        await self._broadcast(response)

    @_handle_response.register(DidUpdateCell)
    async def _(self, response):
        cell = self._cells[response.request.cell]
        cell.source = response.request.source
        await self._broadcast(response)

    @_handle_response.register(Stdout)
    async def _(self, response, sender):
        cell = self._cells[self._workers.inverse[sender]]
        response.cell = cell.id
        output = Output(type="text", data=response.text)
        cell.outputs.append(output)
        await self._broadcast(response)

    async def _callback(self, message):
        res = DidRunCell(request=message)
        await self._broadcast(res)

    async def _broadcast(self, message):
        json = message.to_json()
        for user in self._users:
            await user.write_message(json)


def _socket_address():
    return f"{gettempdir()}/{uuid4().hex}.sock"
