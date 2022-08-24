from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

from mvnb.data import Data


class MessageHandler(WebSocketHandler):

    path = r"/message"

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

    path = r"/callback"

    def initialize(self, func):
        self._func = func

    async def post(self):
        message = Data.from_json(self.request.body)
        await self._func(message)
