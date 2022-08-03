def __mvnb__(addr):
    from multiprocessing.reduction import sendfds
    from os import close, dup2, fork, getpid, openpty
    from socket import AF_UNIX, SOCK_STREAM, socket
    from termios import TCSANOW
    from tty import setraw

    fd1, fd2 = openpty()
    setraw(fd1, TCSANOW)
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


if __name__ == "__main__":
    import readline

    readline.set_auto_history(False)
