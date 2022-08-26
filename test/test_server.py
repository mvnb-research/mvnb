from asyncio import create_task

from pytest import mark
from pytest_asyncio import fixture
from tornado.websocket import websocket_connect

from mvnb.config import Config
from mvnb.data import Data
from mvnb.output import Stdout
from mvnb.request import CreateCell, RunCell, UpdateCell
from mvnb.response import DidCreateCell, DidRunCell, DidUpdateCell
from mvnb.server import Server
from util import data_eq


@mark.asyncio
async def test_create_root_cell(client):
    request = CreateCell(cell="foo")
    await client.send(request)
    response = await client.recv()
    assert isinstance(response, DidCreateCell)
    assert data_eq(response.request, request)


@mark.asyncio
async def test_create_fork_cell(client):
    request = CreateCell(cell="foo")
    await client.send(request)
    response = await client.recv()
    assert isinstance(response, DidCreateCell)
    assert data_eq(response.request, request)

    request = CreateCell(cell="bar", parent="foo")
    await client.send(request)
    response = await client.recv()
    assert isinstance(response, DidCreateCell)
    assert data_eq(response.request, request)


@mark.asyncio
async def test_update_cell(client):
    request = CreateCell(cell="foo")
    await client.send(request)
    response = await client.recv()
    assert isinstance(response, DidCreateCell)
    assert data_eq(response.request, request)

    request = UpdateCell(cell="foo", source="")
    await client.send(request)
    response = await client.recv()
    assert isinstance(response, DidUpdateCell)
    assert data_eq(response.request, request)


@mark.asyncio
async def test_run_cell(client):
    request = CreateCell(cell="foo")
    await client.send(request)
    response = await client.recv()
    assert isinstance(response, DidCreateCell)
    assert data_eq(response.request, request)

    request = UpdateCell(cell="foo", source="print(1)\n")
    await client.send(request)
    response = await client.recv()
    assert isinstance(response, DidUpdateCell)
    assert data_eq(response.request, request)

    request = RunCell(cell="foo")
    await client.send(request)
    output = ""
    while True:
        response = await client.recv()
        if isinstance(response, DidRunCell):
            assert data_eq(response.request, request)
            break
        else:
            assert isinstance(response, Stdout)
            output += response.text
    assert output == "1\n"


@fixture
async def client(config, server):
    client = Client(config)
    await client.open()
    yield client
    await client.close()


@fixture
async def server(config):
    server = Server(config)
    task = create_task(server.start())
    yield server
    server.stop()
    task.cancel()


@fixture
async def config():
    return Config([])


class Client(object):
    def __init__(self, config):
        self._config = config

    async def open(self):
        url = f"ws://{self._config.addr}:{self._config.port}/message"
        self._connection = await websocket_connect(url)

    async def send(self, message):
        await self._connection.write_message(message.to_json())

    async def close(self):
        self._connection.close()
        return await self.recv()

    async def recv(self):
        text = await self._connection.read_message()
        return Data.from_json(text) if text else None
