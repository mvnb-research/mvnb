from mvnb.config import Config
from mvnb.console import start as start_console
from mvnb.server import start as start_server


def main(args=None):
    config = Config.from_args(args)
    start_server(config)
    start_console(config)


if __name__ == "__main__":
    main()
