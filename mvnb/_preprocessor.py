from code import compile_command
from sys import stdin


def main():
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


if __name__ == "__main__":
    main()
