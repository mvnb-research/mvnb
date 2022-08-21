from asyncio import Event, create_task
from functools import singledispatchmethod

from tornado.websocket import websocket_connect

from mvnb.data.output import Data, Output
from mvnb.data.response import Response


class Client(object):
    def __init__(self, config, on_output):
        self._config = config
        self._on_output = on_output
        self._connection = None
        self._request = None
        self._response = Event()

    async def connect(self):
        url = f"ws://{self._config.address}:{self._config.port}"
        self._connection = await websocket_connect(url)
        create_task(self._read_message())

    async def send(self, msg):
        self._request = msg
        await self._connection.write_message(msg.to_json())
        await self._response.wait()
        self._response.clear()

    async def _read_message(self):
        while True:
            txt = await self._connection.read_message()
            msg = Data.from_json(txt)
            await self._handle_message(msg)

    @singledispatchmethod
    async def _handle_message(self, _):
        pass

    @_handle_message.register(Output)
    async def _(self, msg):
        await self._on_output(msg)

    @_handle_message.register(Response)
    async def _(self, msg):
        if self._request.id == msg.request.id:
            self._response.set()
