if __name__ == "__main__":

    def __mvnb_fork(addr):
        from multiprocessing.reduction import sendfds
        from os import close, dup2, fork, getpid, openpty
        from socket import AF_UNIX, SOCK_STREAM, socket

        fd1, fd2 = openpty()
        pid = fork()
        if pid == 0:
            with socket(AF_UNIX, SOCK_STREAM) as sock:
                sock.connect(addr)
                sendfds(sock, [fd1])
            with socket(AF_UNIX, SOCK_STREAM) as sock:
                sock.connect(addr)
                sock.send(f"{getpid()}".encode())
            dup2(fd2, 0)
            dup2(fd2, 1)
            dup2(fd2, 2)
        close(fd1)
        close(fd2)

    def __mvnb_callback(endpoint, payload):
        from urllib.request import Request, urlopen

        data = payload.encode("utf8")
        head = {"content-type": "application/json"}
        args = dict(data=data, headers=head, method="POST")
        urlopen(Request(endpoint, **args))

    def __mvnb_init():
        import readline
        import sys

        readline.set_auto_history(False)
        sys.ps1 = sys.ps2 = ""

    __mvnb_init()
