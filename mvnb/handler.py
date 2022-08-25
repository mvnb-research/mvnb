from pathlib import Path

from tornado.web import RequestHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler

from mvnb.data import Data


class MessageHandler(WebSocketHandler):

    PATH = r"/message"

    def initialize(self, users, requests):
        self._users = users
        self._requests = requests

    def open(self):
        self._users.add(self)

    def on_close(self):
        self._users.remove(self)

    async def on_message(self, message):
        data = Data.from_json(message)
        await self._requests.put(data)


class CallbackHandler(RequestHandler):

    PATH = r"/callback"

    def initialize(self, func):
        self._func = func

    async def post(self):
        message = Data.from_json(self.request.body)
        await self._func(message)


class FileHandler(StaticFileHandler):

    PATH = r"/(.*)"

    def initialize(self):
        super().initialize(
            path=Path(__file__).parent / "gui",
            default_filename="index.html",
        )
