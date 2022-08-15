from asyncio import create_task, get_event_loop
from contextlib import contextmanager
from functools import singledispatchmethod
from multiprocessing.reduction import recvfds
from os import close, openpty, read, unlink, write
from os.path import exists
from select import select
from socket import AF_UNIX, SOCK_STREAM, socket
from subprocess import Popen
from termios import TCSANOW
from tty import setraw

from .data import DidCreateCell, DidForkCell, ForkCell, RunCell, Stdout
from .pipeline import Pipeline


class Worker(object):
    def __init__(self, config, response):
        self._config = config
        self._response = response
        self._fd = None
        self._pid = None
        self._requests = Pipeline(self._handle_request)

    async def start_root(self, msg, cmd):
        with _openpty() as (fd1, fd2):
            self._fd = fd1
            self._pid = _popen(cmd, fd2)
        self._start()
        res = DidCreateCell(request=msg)
        await self._response(res, self)

    async def start_fork(self, msg, addr, recv):
        with _connect(addr) as sock:
            recv.set()
            self._fd = await _recv_fd(sock)
            self._pid = await _recv_pid(sock)
        self._start()
        res = DidForkCell(request=msg)
        await self._response(res, self)

    async def put(self, msg, *args):
        await self._requests.put(msg, *args)

    def _start(self):
        get_event_loop().add_reader(self._fd, self._read_callback)
        self._requests.start()

    def _read_callback(self):
        txt = read(self._fd, 1024).decode()
        create_task(self._response(Stdout(text=txt), self))

    @singledispatchmethod
    async def _handle_request(self, _):
        pass

    @_handle_request.register(ForkCell)
    async def _(self, _, addr):
        fork = self._config.fork
        fork = fork.replace("__address__", addr)
        self._write(fork)

    @_handle_request.register(RunCell)
    async def _(self, msg, code):
        url = f"http://{self._config.address}:{self._config.port}/callback"
        callback = self._config.callback
        callback = callback.replace("__url__", url)
        callback = callback.replace("__message__", msg.to_json())
        self._write(f"{code}\n{callback}")

    def _write(self, text):
        data = f"{text}\n".encode()
        while data:
            if fd := _select_write(self._fd):
                data = _write(fd, data)


@contextmanager
def _openpty():
    try:
        fd1, fd2 = openpty()
        setraw(fd1, TCSANOW)
        yield fd1, fd2
    except Exception:
        close(fd1)
        raise
    finally:
        close(fd2)


def _popen(args, fd):
    return Popen(
        args, stdin=fd, stdout=fd, stderr=fd, start_new_session=True
    ).pid


@contextmanager
def _connect(addr):
    try:
        sock = socket(AF_UNIX, SOCK_STREAM)
        sock.bind(addr)
        sock.listen(1)
        sock.setblocking(False)
        yield sock
    finally:
        sock.close()
        exists(addr) and unlink(addr)


async def _recv_fd(sock):
    s = await _accept(sock)
    s = _select_read(s)
    f = recvfds(s, 1)[0]
    return f


async def _recv_pid(sock):
    s = await _accept(sock)
    s = _select_read(s)
    return int(s.recv(8))


async def _accept(sock):
    s, _ = await get_event_loop().sock_accept(sock)
    return s


def _select_read(fd):
    return select((fd,), (), ())[0][0]


def _select_write(fd):
    return select((), (fd,), ())[1][0]


def _write(fd, data):
    size = write(fd, data)
    return data[size:]
