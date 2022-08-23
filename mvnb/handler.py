from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

from mvnb.data import Data


class MessageHandler(WebSocketHandler):
    def initialize(self, users, requests):
        self._users = users
        self._requests = requests

    def open(self):
        self._users.add(self)

    def on_close(self):
        self._users.remove(self)

    async def on_message(self, msg):
        msg = Data.from_json(msg)
        await self._requests.put(msg)


class CallbackHandler(RequestHandler):
    def initialize(self, func):
        self._func = func

    async def post(self):
        msg = Data.from_json(self.request.body)
        await self._func(msg)
