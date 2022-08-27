from os import kill
from signal import SIGINT
from socket import AF_INET, SOCK_STREAM, socket
from subprocess import Popen
from sys import executable
from time import sleep

from pytest import fixture, mark
from pytest_cov.embed import cleanup_on_sigterm
from tornado.httpclient import AsyncHTTPClient


@mark.asyncio
async def test_main(unused_tcp_port):
    client = AsyncHTTPClient()
    response = await client.fetch(f"http://localhost:{unused_tcp_port}/")
    client.close()
    assert response.body


@fixture(autouse=True)
def server(unused_tcp_port):
    try:
        proc = Popen([executable, __file__, str(unused_tcp_port)])
        for _ in range(10):
            with socket(AF_INET, SOCK_STREAM) as s:
                if not s.connect_ex((localhost, unused_tcp_port)):
                    yield proc
                    break
            sleep(0.1)
        else:
            raise Exception()
    finally:
        kill(proc.pid, SIGINT)
        proc.wait()


localhost = "localhost"

if __name__ == "__main__":
    from sys import argv

    from mvnb.__main__ import main

    cleanup_on_sigterm()
    main(["--port", argv[1]])
