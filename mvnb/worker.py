from asyncio import create_task, get_event_loop
from contextlib import contextmanager
from functools import singledispatchmethod
from multiprocessing.reduction import recvfds
from os import close, kill, openpty, read, unlink, write
from os.path import exists
from select import select
from signal import SIGKILL
from socket import AF_UNIX, SOCK_STREAM, socket
from subprocess import PIPE, Popen
from termios import TCSANOW
from tty import setraw

from mvnb.handler import CallbackHandler, SideChannelHandler
from mvnb.output import Stdout
from mvnb.queue import Queue
from mvnb.request import RunCell


class Worker(object):
    def __init__(self, cell_id, config, response):
        self._cell_id = cell_id
        self._config = config
        self._response = response
        self._fd = None
        self._pid = None
        self._proc = None
        self._requests = Queue(self._handle_request)

    async def start_root(self):
        with _openpty() as (fd1, fd2):
            self._fd = fd1
            self._proc = _popen(self._config, fd2)
            self._pid = self._proc.pid
        self._start()

    async def start_fork(self, addr, event):
        with _connect(addr) as sock:
            event.set()
            self._fd = await _recv_fd(sock)
            self._pid = await _recv_pid(sock)
        self._start()

    async def put(self, msg, *args):
        await self._requests.put(msg, *args)

    async def fork(self, addr):
        self._write(self._fork_code(addr))

    def stop(self):
        if self._proc:
            self._proc.terminate()
            self._proc.wait()
        else:
            kill(self._pid, SIGKILL)
        get_event_loop().remove_reader(self._fd)
        close(self._fd)
        self._requests.stop()

    def _start(self):
        self._requests.start()
        get_event_loop().add_reader(self._fd, self._read_callback)

    def _read_callback(self):
        try:
            text = read(self._fd, 1024).decode()
            create_task(self._reply(Stdout(text=text)))
        except OSError as e:
            if e.errno == 5:
                get_event_loop().remove_reader(self._fd)
            else:
                raise

    @singledispatchmethod
    async def _handle_request(self, _):
        raise Exception()  # pragma: no cover

    @_handle_request.register(RunCell)
    async def _(self, msg, code):
        self._write(self._sidechannel_code())
        if self._config.before_run:
            self._write(self._config.before_run)
        self._write(code)
        if self._config.after_run:
            self._write(self._config.after_run)
        self._write(self._callback_code(msg))

    def _fork_code(self, addr):
        code = self._config.fork
        code = code.replace(self._config.fork_addr, addr)
        return code

    def _sidechannel_code(self):
        url = self._sidechannel_url()
        code = self._config.sidechannel
        code = code.replace(self._config.sidechannel_url, url)
        code = code.replace(self._config.sidechannel_cell_id, self._cell_id)
        return code

    def _sidechannel_url(self):
        addr = self._config.addr
        port = self._config.port
        path = SideChannelHandler.PATH
        return f"http://{addr}:{port}{path}"

    def _callback_code(self, msg):
        url = self._callback_url()
        msg = msg.to_json()
        code = self._config.callback
        code = code.replace(self._config.callback_url, url)
        code = code.replace(self._config.callback_payload, msg)
        return code

    def _callback_url(self):
        addr = self._config.addr
        port = self._config.port
        path = CallbackHandler.PATH
        return f"http://{addr}:{port}{path}"

    def _write(self, text):
        data = f"{text}\n".encode()
        proc = Popen(self._config.preproc, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        data = proc.communicate(data)[0]
        while data:
            if fd := _select_write(self._fd):
                data = _write(fd, data)

    def _reply(self, msg):
        return self._response(msg, self)


def _popen(config, fd):
    args = config.repl_command, *config.repl_arguments
    return Popen(args, stdin=fd, stdout=fd, stderr=fd)


@contextmanager
def _openpty():
    try:
        fd1, fd2 = openpty()
        setraw(fd1, TCSANOW)
        yield fd1, fd2
    except Exception:  # pragma: no cover
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
