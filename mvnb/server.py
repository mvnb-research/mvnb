from asyncio import FIRST_COMPLETED, Event, create_task, wait
from functools import singledispatchmethod
from tempfile import gettempdir
from traceback import print_exception
from uuid import uuid4

from tornado.web import Application

from mvnb.bidict import BiDict
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
        self._workers = BiDict()
        self._notebook = Notebook()
        self._requests = Queue(self._handle_request)
        self._responses = Queue(self._handle_response)
        self._http = None

    async def start(self):
        self._http = self._start_app()
        done, _ = await self._start_queues()
        for t in done:
            if e := t.exception():
                print_exception(e)

    def stop(self):
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
    async def _(self, req):
        if req.parent:
            await self._fork_cell(req)
        else:
            await self._create_cell(req)

    async def _create_cell(self, req):
        worker = Worker(self._config, self._responses.put)
        await worker.start_root(req)

    async def _fork_cell(self, req):
        parent = self._workers[req.parent]
        worker = Worker(self._config, self._responses.put)
        addr, event = _socket_address(), Event()
        create_task(worker.start_fork(req, addr, event))
        await event.wait()
        await parent.put(req, addr)

    @_handle_request.register(UpdateCell)
    async def _(self, req):
        cell = self._cells[req.cell]
        cell.source = req.source
        response = DidUpdateCell(request=req)
        await self._responses.put(response)

    @_handle_request.register(RunCell)
    async def _(self, req):
        cell = self._cells[req.cell]
        await self._workers[cell.id].put(req, cell.source)

    @singledispatchmethod
    async def _handle_response(self, response):
        await self._broadcast(response)

    @_handle_response.register(DidCreateCell)
    async def _(self, response, sender):
        cell = Cell(id=response.request.cell, parent=response.request.parent)
        self._notebook.cells.append(cell)
        self._cells[cell.id] = cell
        self._workers[cell.id] = sender
        await self._broadcast(response)

    @_handle_response.register(Stdout)
    async def _(self, response, sender):
        cell = self._cells[self._workers.find_key(sender)]
        response.cell = cell.id
        output = Output(type="text", data=response.text)
        cell.outputs.append(output)
        await self._broadcast(response)

    async def _callback(self, msg):
        res = DidRunCell(request=msg)
        await self._responses.put(res)

    async def _broadcast(self, msg):
        json = msg.to_json()
        for user in self._users:
            await user.write_message(json)


def _socket_address():
    return f"{gettempdir()}/{uuid4().hex}.sock"
