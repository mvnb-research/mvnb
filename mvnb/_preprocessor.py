if __name__ == "__main__":
    from code import compile_command
    from sys import stdin

    buf = ""
    for line in stdin:
        buf += line
        if compile_command(buf):
            print(buf, end="")
            if 1 < buf.count("\n"):
                print()
            buf = ""
    if buf:
        exit(1)
