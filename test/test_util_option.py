from pytest import raises

from mvnb.util.option import Parser, group, option
from mvnb.util.record import Record, field


def test_no_help(capsys_test):
    parser = Parser("foo")

    run(parser, "--help")
    capsys_test(
        """
usage: foo
foo: error: unrecognized arguments: --help
"""
    )


def test_no_abbrev(capsys_test):
    parser = Parser("foo")
    parser.add_argument("--foo")

    run(parser, "-f", "foo")
    capsys_test(
        """
usage: foo [--foo FOO]
foo: error: unrecognized arguments: -f foo
"""
    )


def test_help_width(capsys_test):
    parser = Parser("foo")
    parser.add_argument(
        "--help",
        action="help",
        help=(
            "This very long help message should be wrapped"
            " so that every line is at most 88 characters long."
        ),
    )

    run(parser, "--help")
    capsys_test(
        """
usage: foo [--help]

options:
  --help  This very long help message should be wrapped so that every line is at most 88
          characters long.
"""
    )


def test_option(capsys_test):
    class Foo(Record):
        @option(help="foo value")
        def foo(self, _):
            pass

    parser = Parser("foo")
    parser.add_arguments(Foo)
    parser.add_argument("--help", action="help")

    run(parser, "--help")
    capsys_test(
        """
usage: foo [--foo FOO] [--help]

options:
  --foo FOO  foo value
  --help
"""
    )


def test_ignore_non_option_field(capsys_test):
    class Foo(Record):
        @field
        def bar(self, _):
            pass

    parser = Parser("foo")
    parser.add_arguments(Foo)
    parser.add_argument("--help", action="help")

    run(parser, "--help")
    capsys_test(
        """
usage: foo [--help]

options:
  --help
"""
    )


def test_option_alternative(capsys_test):
    class Foo(Record):
        @option("--bar", help="bar value")
        @option(help="foo value")
        def foo(self, _):
            pass

    parser = Parser("foo")
    parser.add_arguments(Foo)
    parser.add_argument("--help", action="help")

    run(parser, "--help")
    capsys_test(
        """
usage: foo [--foo FOO] [--bar FOO] [--help]

options:
  --foo FOO  foo value
  --bar FOO  bar value
  --help
"""
    )


def test_group(capsys_test):
    class Foo(Record):
        foo = group("foo options")

        @foo
        @option(help="bar value")
        def bar(self, _):
            pass

        @foo
        @option(help="baz value")
        def baz(self, _):
            pass

    parser = Parser("foo")
    parser.add_arguments(Foo)
    parser.add_argument("--help", action="help")

    run(parser, "--help")
    capsys_test(
        """
usage: foo [--bar BAR] [--baz BAZ] [--help]

options:
  --help

foo options:
  --bar BAR  bar value
  --baz BAZ  baz value
"""
    )


def test_parse():
    class Foo(Record):
        @option(help="foo value")
        def foo(self, _):
            pass

    parser = Parser("foo")
    parser.add_arguments(Foo)

    assert parser.parse([]) == {}
    assert parser.parse(["--foo", "1"]) == {"foo": "1"}


def run(parser, *args):
    with raises(SystemExit):
        parser.parse_args(args)
