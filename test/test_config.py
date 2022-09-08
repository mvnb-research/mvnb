from pathlib import Path
from sys import executable

from pytest import raises

from mvnb import _bootstrap, _preprocessor
from mvnb.config import Config


def test_default_values():
    config = Config([])
    assert config.version == "0.0.0"
    assert config.addr == "0.0.0.0"
    assert config.port == 8000
    assert config.repl == [executable, "-i", _bootstrap.__file__]
    assert config.preproc == [executable, _preprocessor.__file__]
    assert config.before_run is None
    assert config.after_run is None
    assert config.fork == "__mvnb_fork('__address__')"
    assert config.callback == "__mvnb_callback('__url__', '__message__')"
    assert config.fromfile_prefix == "@"
    assert config.fork_addr == "__address__"
    assert config.callback_url == "__url__"
    assert config.callback_message == "__message__"


def test_file_read():
    config = Config([])
    config.before_run = "@README.md"
    assert config.before_run == Path("README.md").read_text()

    config.before_run = "README.md"
    assert config.before_run == "README.md"


def test_help(capsys_test):
    with raises(SystemExit):
        Config(["--help"])

    capsys_test(
        """
usage: mvnb [--help] [--version] [--addr <addr>] [--port <port>] [--repl <repl>]
            [--preproc <preproc>] [--before-run <code>] [--after-run <code>]
            [--fork <code>] [--callback <code>] [--fromfile-prefix <text>]
            [--fork-addr <text>] [--callback-url <text>] [--callback-message <text>]

options:
  --help                     show help
  --version                  show version
  --addr <addr>              server address
  --port <port>              server port
  --repl <repl>              repl command
  --preproc <preproc>        preprocessor command
  --before-run <code>        before-run code
  --after-run <code>         after-run code
  --fork <code>              fork code
  --callback <code>          callback code
  --fromfile-prefix <text>   fromfile prefix
  --fork-addr <text>         fork address placeholder
  --callback-url <text>      callback url placeholder
  --callback-message <text>  callback message placeholder
"""
    )
