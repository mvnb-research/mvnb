from pytest import raises

from mvnb.data import Data, field
from mvnb.option import Parser, option


def test_no_help(capsys_test):
    parser = Parser("foo", Data)

    run(parser, "--help")
    capsys_test(
        """
usage: foo [options]
foo: error: unrecognized arguments: --help
"""
    )


def test_no_abbrev(capsys_test):
    parser = Parser("foo", Data)
    parser.add_argument("--foo")

    run(parser, "-f", "foo")
    capsys_test(
        """
usage: foo [options]
foo: error: unrecognized arguments: -f foo
"""
    )


def test_help_width(capsys_test):
    parser = Parser("foo", Data)
    parser.add_argument(
        "--help",
        action="help",
        help=(
            "This very long help message should be wrapped"
            " so that every line is at most 80 characters long."
        ),
    )

    run(parser, "--help")
    capsys_test(
        """
usage: foo [options]

options:
  --help  This very long help message should be wrapped so that every line is at
          most 80 characters long.
"""
    )


def test_option(capsys_test):
    class Foo(Data):
        @option(help="foo value")
        def foo(self, _):
            pass

    parser = Parser("foo", Foo)
    parser.add_argument("--help", action="help")

    run(parser, "--help")
    capsys_test(
        """
usage: foo [options]

options:
  --foo FOO  foo value
  --help
"""
    )


def test_ignore_non_option_field(capsys_test):
    class Foo(Data):
        @field
        def bar(self, _):
            pass

    parser = Parser("foo", Foo)
    parser.add_argument("--help", action="help")

    run(parser, "--help")
    capsys_test(
        """
usage: foo [options]

options:
  --help
"""
    )


def test_option_alternative(capsys_test):
    class Foo(Data):
        @option("--bar", help="bar value")
        @option(help="foo value")
        def foo(self, _):
            pass

    parser = Parser("foo", Foo)
    parser.add_argument("--help", action="help")

    run(parser, "--help")
    capsys_test(
        """
usage: foo [options]

options:
  --foo FOO  foo value
  --bar FOO  bar value
  --help
"""
    )


def test_version(capsys_test):
    class Foo(Data):
        @option(action="version")
        def version(self, _):
            return "foo"

    parser = Parser("foo", Foo)
    run(parser, "--version")
    capsys_test("foo\n")


def test_parse():
    class Foo(Data):
        @option(help="foo value")
        def foo(self, _):
            pass

    parser = Parser("foo", Foo)
    assert parser.parse([]) == {}
    assert parser.parse(["--foo", "1"]) == {"foo": "1"}


def run(parser, *args):
    with raises(SystemExit):
        parser.parse_args(args)
