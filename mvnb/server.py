from asyncio import (
    FIRST_COMPLETED,
    Event,
    Queue,
    create_task,
    new_event_loop,
    set_event_loop,
    wait,
)
from functools import singledispatchmethod
from tempfile import gettempdir
from threading import Thread
from uuid import uuid4

from bidict import bidict
from tornado.web import Application
from tornado.websocket import WebSocketHandler

from mvnb.message import CreateCell, ForkCell, Message, RunCell, UpdateCell
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
        self.workers = bidict()
        self.requests = Queue()
        self.responses = Queue()

    async def start(self):
        dct = dict(users=self.users, requests=self.requests)
        app = Application([("/", _Handler, dct)])
        app.listen(address=self.config.address, port=self.config.port)

        req = self.watch_requests()
        res = self.watch_responses()
        await wait([req, res], return_when=FIRST_COMPLETED)

    async def watch_requests(self):
        while True:
            txt = await self.requests.get()
            msg = Message.from_json(txt)
            await self.handle_request(msg)

    async def watch_responses(self):
        while True:
            msg = await self.responses.get()
            await self.handle_response(msg)

    @singledispatchmethod
    async def handle_request(self, _):
        pass

    @handle_request.register(CreateCell)
    async def _(self, msg):
        worker = self.create_worker(msg.cell)
        await worker.start_root(msg, self.config.repl)

    @handle_request.register(ForkCell)
    async def _(self, msg):
        parent = self.workers[msg.parent]
        worker = self.create_worker(msg.cell)
        addr, recv = _socket_address(), Event()
        coro = worker.start_fork(msg, addr, recv)
        create_task(coro)
        await recv.wait()
        await parent.put(msg, addr)

    @handle_request.register(UpdateCell)
    async def _(self, msg):
        await self.workers[msg.cell].put(msg)

    @handle_request.register(RunCell)
    async def _(self, msg):
        await self.workers[msg.cell].put(msg)

    @singledispatchmethod
    async def handle_response(self, msg):
        txt = msg.to_json()
        for usr in self.users:
            await usr.write_message(txt)

    def create_worker(self, name):
        worker = Worker(name, self.config, self.responses.put)
        self.workers[name] = worker
        return worker


class _Handler(WebSocketHandler):
    def initialize(self, users, requests):
        self.users = users
        self.requests = requests

    def open(self):
        self.users.add(self)

    def on_close(self):
        self.users.remove(self)

    async def on_message(self, msg):
        await self.requests.put(msg)


def _socket_address():
    return f"{gettempdir()}/{uuid4().hex}.sock"
