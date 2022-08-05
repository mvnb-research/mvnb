from asyncio import (
    FIRST_COMPLETED,
    Event,
    create_task,
    new_event_loop,
    set_event_loop,
    wait,
)
from functools import singledispatchmethod
from tempfile import gettempdir
from threading import Thread
from uuid import uuid4

from tornado.web import Application
from tornado.websocket import WebSocketHandler

from mvnb.data import (
    CreateCell,
    Data,
    DidCreateCell,
    DidForkCell,
    DidUpdateCell,
    ForkCell,
    Notebook,
    RunCell,
    Stdout,
    UpdateCell,
)
from mvnb.pipeline import Pipeline
from mvnb.worker import Worker


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
        self.notebook = Notebook()
        self.requests = Pipeline(self.handle_request)
        self.responses = Pipeline(self.handle_response)

    async def start(self):
        dct = dict(users=self.users, requests=self.requests)
        app = Application([("/", _Handler, dct)])
        app.listen(address=self.config.address, port=self.config.port)

        req = self.requests.start()
        res = self.responses.start()
        await wait([req, res], return_when=FIRST_COMPLETED)

    @singledispatchmethod
    async def handle_request(self, _):
        pass

    @handle_request.register(CreateCell)
    async def _(self, msg):
        worker = Worker(self.config, self.responses.put)
        await worker.start_root(msg, self.config.repl)

    @handle_request.register(ForkCell)
    async def _(self, msg):
        parent = self.notebook.cell(msg.parent).worker
        worker = Worker(self.config, self.responses.put)
        addr, recv = _socket_address(), Event()
        coro = worker.start_fork(msg, addr, recv)
        create_task(coro)
        await recv.wait()
        await parent.put(msg, addr)

    @handle_request.register(UpdateCell)
    async def _(self, msg):
        self.notebook.update(msg)
        res = DidUpdateCell(request=msg)
        await self.responses.put(res, self)

    @handle_request.register(RunCell)
    async def _(self, msg):
        cell = self.notebook.cell(msg.cell)
        await cell.worker.put(msg, cell.code)

    @singledispatchmethod
    async def handle_response(self, msg, _):
        self.notebook.update(msg)
        await self.broadcast(msg)

    @handle_response.register(DidCreateCell)
    async def _(self, msg, sender):
        self.notebook.update(msg)
        cell = self.notebook.cell(msg.request.cell)
        cell.worker = sender
        await self.broadcast(msg)

    @handle_response.register(DidForkCell)
    async def _(self, msg, sender):
        self.notebook.update(msg)
        cell = self.notebook.cell(msg.request.cell)
        cell.worker = sender
        await self.broadcast(msg)

    @handle_response.register(Stdout)
    async def _(self, msg, sender):
        msg.cell = self.notebook.name(sender)
        self.notebook.update(msg)
        await self.broadcast(msg)

    async def broadcast(self, msg):
        txt = msg.to_json()
        for usr in self.users:
            await usr.write_message(txt)


class _Handler(WebSocketHandler):
    def initialize(self, users, requests):
        self.users = users
        self.requests = requests

    def open(self):
        self.users.add(self)

    def on_close(self):
        self.users.remove(self)

    async def on_message(self, msg):
        msg = Data.from_json(msg)
        await self.requests.put(msg)


def _socket_address():
    return f"{gettempdir()}/{uuid4().hex}.sock"
