from asyncio import run

from mvnb.config import Config
from mvnb.server.server import _Server


def main(args=None):
    try:
        config = Config(args)
        server = _Server(config)
        run(server.start())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
