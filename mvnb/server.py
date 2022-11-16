from asyncio import FIRST_COMPLETED, Event, create_task, wait
from functools import singledispatchmethod
from pathlib import Path
from tempfile import gettempdir
from traceback import print_exception
from uuid import uuid4

from tornado.web import Application

from mvnb.bidict import BiDict
from mvnb.handler import CallbackHandler, FileHandler, MessageHandler
from mvnb.notebook import Cell, Notebook, Output
from mvnb.output import Stdout
from mvnb.payload import Payload
from mvnb.queue import Queue
from mvnb.request import CreateCell, DeleteCell, RunCell, SaveNotebook, UpdateCell
from mvnb.response import (
    DidCreateCell,
    DidDeleteCell,
    DidRunCell,
    DidSaveNotebook,
    DidUpdateCell,
)
from mvnb.worker import Worker


class Server(object):
    def __init__(self, config):
        self._config = config
        self._users = set()
        self._cells = dict()
        self._workers = BiDict()
        self._requests = Queue(self._handle_request)
        self._responses = Queue(self._handle_response)
        self._notebook = None
        self._http = None

    async def start(self):
        self._notebook = self._load_notebook()
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

    def _load_notebook(self):
        if path := self._config.path:
            return Payload.from_json(path.read_text())
        return Notebook()

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
        args = dict(users=self._users, requests=self._requests, notebook=self._notebook)
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
        cell = Cell(id=req.cell, parent=req.parent, x=req.x, y=req.y)
        self._notebook.cells.append(cell)
        self._cells[cell.id] = cell
        response = DidCreateCell(request=req)
        await self._responses.put(response)

    @_handle_request.register(DeleteCell)
    async def _(self, req):
        self._cells.pop(req.cell)
        self._notebook.cells = [c for c in self._notebook.cells if c.id != req.cell]
        response = DidDeleteCell(request=req)
        await self._responses.put(response)

    @_handle_request.register(UpdateCell)
    async def _(self, req):
        cell = self._cells[req.cell]
        cell.source = req.source
        response = DidUpdateCell(request=req)
        await self._responses.put(response)

    @_handle_request.register(RunCell)
    async def _(self, req):
        cell = self._cells[req.cell]
        if cell.parent:
            parent = self._workers[cell.parent]
            worker = Worker(self._config, self._responses.put)
            addr, event = _socket_address(), Event()
            create_task(worker.start_fork(addr, event))
            await event.wait()
            await parent.fork(addr)
            self._workers[cell.id] = worker
        else:
            worker = Worker(self._config, self._responses.put)
            await worker.start_root()
            self._workers[cell.id] = worker
        await self._workers[cell.id].put(req, cell.source)

    @_handle_request.register(SaveNotebook)
    async def _(self, req):
        if not self._config.path:
            self._config.path = _new_file_path()
        self._config.path.write_text(self._notebook.to_json())
        response = DidSaveNotebook(request=req)
        await self._responses.put(response)

    @singledispatchmethod
    async def _handle_response(self, response):
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


def _new_file_path():
    i = 0
    while True:
        tail = f"-{i}" if i else ""
        path = Path(f"untitled{tail}.mvnb")
        if path.exists():
            i += 1
        else:
            return path


def _socket_address():
    return f"{gettempdir()}/{uuid4().hex}.sock"
