from sys import executable

from pytest import raises

from mvnb import _bootstrap
from mvnb.config import Config


def test_default_values():
    config = Config([])
    assert config.version == "0.0.0"
    assert config.addr == "0.0.0.0"
    assert config.port == 8000
    assert config.repl == [executable, "-i", _bootstrap.__file__]
    assert config.fork == "__fork('__address__')"
    assert config.callback == "__callback('__url__', '__message__')"
    assert config.fork_addr == "__address__"
    assert config.callback_url == "__url__"
    assert config.callback_message == "__message__"


def test_help(capsys_test):
    with raises(SystemExit):
        Config(["--help"])

    capsys_test(
        """
usage: mvnb [--help] [--version] [--addr <addr>] [--port <port>] [--repl <repl>]
            [--fork <code>] [--callback <code>] [--fork-addr <text>]
            [--callback-url <text>] [--callback-message <text>]

options:
  --help                     show help
  --version                  show version
  --addr <addr>              server address
  --port <port>              server port
  --repl <repl>              repl command
  --fork <code>              fork code
  --callback <code>          callback code
  --fork-addr <text>         fork address placeholder
  --callback-url <text>      callback url placeholder
  --callback-message <text>  callback message placeholder
"""
    )
