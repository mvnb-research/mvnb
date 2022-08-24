from asyncio import create_task, get_event_loop
from contextlib import contextmanager
from functools import singledispatchmethod
from multiprocessing.reduction import recvfds
from os import close, kill, openpty, read, unlink, write
from os.path import exists
from select import select
from signal import SIGKILL
from socket import AF_UNIX, SOCK_STREAM, socket
from subprocess import Popen
from termios import TCSANOW
from tty import setraw

from mvnb.handler import CallbackHandler
from mvnb.output import Stdout
from mvnb.queue import Queue
from mvnb.request import CreateCell, RunCell
from mvnb.response import DidCreateCell


class Worker(object):
    def __init__(self, config, response):
        self._config = config
        self._response = response
        self._fd = None
        self._pid = None
        self._proc = None
        self._requests = Queue(self._handle_request)

    async def start_root(self, request):
        with _openpty() as (fd1, fd2):
            self._fd = fd1
            self._proc = _popen(self._config.repl, fd2)
            self._pid = self._proc.pid
        await self._start(request)

    async def start_fork(self, request, address, event):
        with _connect(address) as sock:
            event.set()
            self._fd = await _recv_fd(sock)
            self._pid = await _recv_pid(sock)
        await self._start(request)

    async def put(self, message, *args):
        await self._requests.put(message, *args)

    def stop(self):
        if self._proc:
            self._proc.terminate()
            self._proc.wait()
        else:
            kill(self._pid, SIGKILL)
        get_event_loop().remove_reader(self._fd)
        close(self._fd)
        self._requests.stop()

    def _start(self, request):
        self._requests.start()
        get_event_loop().add_reader(self._fd, self._read_callback)
        return self._reply(DidCreateCell(request=request))

    def _read_callback(self):
        text = read(self._fd, 1024).decode()
        create_task(self._reply(Stdout(text=text)))

    @singledispatchmethod
    async def _handle_request(self, _):
        raise Exception()  # pragma: no cover

    @_handle_request.register(CreateCell)
    async def _(self, _, addr):
        self._write(self._fork_code(addr))

    @_handle_request.register(RunCell)
    async def _(self, message, code):
        self._write(code)
        self._write(self._callback_code(message))

    def _fork_code(self, addr):
        code = self._config.fork
        code = code.replace(self._config.fork_addr, addr)
        return code

    def _callback_code(self, message):
        url = self._callback_url()
        msg = message.to_json()
        code = self._config.callback
        code = code.replace(self._config.callback_url, url)
        code = code.replace(self._config.callback_message, msg)
        return code

    def _callback_url(self):
        addr = self._config.addr
        port = self._config.port
        path = CallbackHandler.path
        return f"http://{addr}:{port}{path}"

    def _write(self, text):
        data = f"{text}\n".encode()
        while data:
            if fd := _select_write(self._fd):
                data = _write(fd, data)

    def _reply(self, message):
        return self._response(message, self)


def _popen(args, fd):
    return Popen(args, stdin=fd, stdout=fd, stderr=fd)


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
    s.close()
    return f


async def _recv_pid(sock):
    s = await _accept(sock)
    s = _select_read(s)
    i = int(s.recv(8))
    s.close()
    return i


async def _accept(sock):
    s, _ = await get_event_loop().sock_accept(sock)
    return s


def _select_read(fd):
    rlist, _, _ = select((fd,), (), ())
    return rlist[0]


def _select_write(fd):
    _, wlist, _ = select((), (fd,), ())
    return wlist[0]


def _write(fd, data):
    size = write(fd, data)
    return data[size:]