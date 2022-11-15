from pathlib import Path

from tornado.web import RequestHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler

from mvnb.payload import Payload


class MessageHandler(WebSocketHandler):

    PATH = r"/message"

    def check_origin(self, origin):
        return True

    def initialize(self, users, requests, notebook):
        self._users = users
        self._requests = requests
        self._notebook = notebook

    async def open(self):
        self._users.add(self)
        await self.write_message(self._notebook.to_json())

    def on_close(self):
        self._users.remove(self)

    async def on_message(self, msg):
        payload = Payload.from_json(msg)
        await self._requests.put(payload)


class CallbackHandler(RequestHandler):

    PATH = r"/callback"

    def initialize(self, func):
        self._func = func

    async def post(self):
        msg = Payload.from_json(self.request.body)
        await self._func(msg)


class FileHandler(StaticFileHandler):

    PATH = r"/(.*)"

    def initialize(self):
        super().initialize(
            path=Path(__file__).parent / "gui",
            default_filename="index.html",
        )
