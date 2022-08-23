from collections import defaultdict
from re import sub

from bidict import bidict

from mvnb.util.option import Parser
from mvnb.util.record import Record as Record_


class Record(Record_):
    def __init_subclass__(cls, abst=False, group=None, prog=None):
        _properties.register(cls, abst, group, prog)

    def setdefault(self, **values):
        for k, v in values.items():
            self._raw.setdefault(k, v)

    @classmethod
    def from_args(cls, args):
        return _from_args(cls, args)


class _Properties(object):
    def __init__(self):
        self._names = defaultdict(bidict)
        self._groups = {}
        self._parsers = {}

    def register(self, cls, abst, group, prog):
        if group:
            self._groups[cls] = group
        if not abst:
            group = self.group(cls)
            name = _get_dash_case_name(cls)
            prog = prog or name
            self._names[group][cls] = name
            p = Parser(prog)
            p.add_arguments(cls)
            self._parsers[cls] = p

    def is_abst(self, cls):
        return cls not in self.names(cls)

    def names(self, cls):
        return self._names[self.group(cls)]

    def classes(self, cls):
        return self.names(cls).inverse

    def name(self, cls):
        return self.names(cls)[cls]

    def group(self, cls):
        for c in cls.__mro__:
            if g := self._groups.get(c):
                return g

    def parser(self, cls):
        return self._parsers.get(cls)


def _from_args(cls, args):
    if _properties.is_abst(cls):
        key, args = args[0], args[1:]
        if cls := _properties.classes(cls).get(key):
            parser = _properties.parser(cls)
            return cls(**parser.parse_args(args))
        return None
    parser = _properties.parser(cls)
    return cls(**parser.parse(args))


def _get_dash_case_name(cls):
    return sub(r"(?<!^)(?=[A-Z])", "-", cls.__name__).lower()


_properties = _Properties()
