from asyncio import run

from mvnb.config import Config
from mvnb.server import Server


def main():
    try:
        config = Config(None)
        server = Server(config)
        run(server.start())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
