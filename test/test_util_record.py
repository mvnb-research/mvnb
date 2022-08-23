from random import random

from mvnb.util.record import Record, field


def test_get_field():
    class Foo(Record):
        @field
        def foo(self, raw):
            return raw

    foo = Foo()
    assert foo.foo is None

    foo = Foo(foo=1)
    assert foo.foo == 1


def test_set_field():
    class Foo(Record):
        @field
        def foo(self, raw):
            return raw

    foo = Foo()
    foo.foo = 1
    assert foo.foo == 1

    foo.foo = 2
    assert foo.foo == 2


def test_del_field():
    class Foo(Record):
        @field
        def foo(self, raw):
            return raw

    foo = Foo()
    foo.foo = 1
    del foo.foo
    assert foo.foo is None


def test_field_cache():
    class Foo(Record):
        @field
        def foo(self, _):
            return random()

    foo = Foo()
    assert foo.foo == foo.foo


def test_get_field_object():
    class Foo(Record):
        @field
        def foo(self, _):
            pass

    assert isinstance(Foo.foo, field)
    assert Foo.foo.name == "foo"


def test_get_fields():
    class Foo(Record):
        @field
        def foo(self, _):
            pass

        @field
        def bar(self, _):
            pass

    fields = list(Foo.fields)
    assert len(fields) == 2
    assert fields[0] is Foo.foo
    assert fields[1] is Foo.bar


def test_get_fields_inheritance():
    class Foo(Record):
        @field
        def foo(self, _):
            pass

        @field
        def bar(self, _):
            pass

    class Bar(Foo):
        @field
        def foo(self, _):
            pass

        @field
        def baz(self, _):
            pass

    fields = list(Bar.fields)
    assert len(fields) == 3
    assert fields[0] is Foo.bar
    assert fields[1] is Bar.foo
    assert fields[2] is Bar.baz
