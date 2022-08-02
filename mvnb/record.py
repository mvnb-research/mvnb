from argparse import ArgumentParser, HelpFormatter, _ActionsContainer
from collections import defaultdict
from functools import cached_property, singledispatch, singledispatchmethod
from json import dumps, loads
from re import sub
from shutil import get_terminal_size

from bidict import bidict


class Record(object):
    def __init_subclass__(cls, abst=False, group=None, prog=None):
        _properties.register(cls, abst, group, prog)

    def __init__(self, **values):
        self._raw = values
        self._cache = {}

    def setdefault(self, **values):
        for k, v in values.items():
            self._raw.setdefault(k, v)

    def to_json(self):
        return _to_json(self)

    @classmethod
    def from_json(cls, json):
        return _from_json(cls, json)

    @classmethod
    def from_args(cls, args):
        return _from_args(cls, args)


def field(func):
    attr = _Attribute()
    attr.func = func
    attr.is_field = True
    return attr


def argument(*args, **kwargs):
    attr = _Attribute()
    attr.args.append(args)
    attr.kwargs.append(kwargs)
    attr.positional = True
    return attr


def option(*args, **kwargs):
    attr = _Attribute()
    attr.args.append(args)
    attr.kwargs.append(kwargs)
    return attr


def group(name):
    def group(attr):
        attr.group = name
        return attr

    return group


class _Attribute(object):
    def __init__(self):
        self.func = None
        self.group = None
        self.args = []
        self.kwargs = []
        self.is_field = False
        self.positional = False

    def __call__(self, obj):
        if isinstance(obj, _Attribute):
            obj.args.extend(self.args)
            obj.kwargs.extend(self.kwargs)
            return obj
        self.func = obj
        return self

    def __get__(self, rec, _):
        if self.name not in rec._cache:
            raw = rec._raw.get(self.name)
            val = self.func(rec, raw)
            if isinstance(val, Exception):
                raise val
            rec._cache[self.name] = val
        return rec._cache[self.name]

    def __set__(self, rec, raw):
        rec._raw[self.name] = raw
        rec._cache.pop(self.name, None)

    @cached_property
    def name(self):
        return self.func.__name__

    @cached_property
    def is_argument(self):
        return bool(self.args)


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
            self._parsers[cls] = _create_parser(cls, prog)

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


class _ArgumentParser(ArgumentParser):
    def __init__(self, prog):
        super().__init__(
            prog=prog,
            add_help=False,
            allow_abbrev=False,
            formatter_class=_HelpFormatter,
        )


class _HelpFormatter(HelpFormatter):
    def __init__(self, prog):
        width = min(get_terminal_size((88, 24)).columns, 88)
        super().__init__(prog, width=width, max_help_position=width)


def _create_parser(cls, prog):
    parser = _ArgumentParser(prog)
    for arg in _find_arguments(cls):
        parser.add_argument(arg)
    return parser


@singledispatchmethod
def _add_argument(self, *args, **kwargs):
    args = map(lambda s: s.replace("_", "-"), args)
    return self._add_argument(*args, **kwargs)


@_add_argument.register(_Attribute)
def _(self, field):
    name = field.name
    pos = field.positional
    dct = dict(dest=name, default=_unset)
    grp = self.add_argument_group(field.group)
    for args, kwargs in zip(field.args, field.kwargs):
        args = args or [name if pos else f"--{name}"]
        kwargs = kwargs if pos else {**kwargs, **dct}
        grp.add_argument(*args, **kwargs)


def _add_argument_group(self, title=None, **kwargs):
    if title:
        groups = _setdefaultattr(self, "_groups", {})
        if title not in groups:
            group = self._add_argument_group(title, **kwargs)
            groups[title] = group
        return groups[title]
    return self


def _setdefaultattr(obj, name, value):
    if not hasattr(obj, name):
        setattr(obj, name, value)
    return getattr(obj, name)


def _extend_actionscontainer(*funcs):
    for func in funcs:
        name = _get_func_name(func)
        if hasattr(_ActionsContainer, name):
            f = getattr(_ActionsContainer, name)
            setattr(_ActionsContainer, f"_{name}", f)
        setattr(_ActionsContainer, name, func)


def _get_func_name(func):
    func = func.func if isinstance(func, singledispatchmethod) else func
    return func.__name__[1:]


def _to_json(rec):
    idx = _properties.names(rec.__class__)
    dct = _to_dict(rec, idx)
    return dumps(dct, separators=(",", ":"))


@singledispatch
def _to_dict(obj, _):
    return obj


@_to_dict.register(list)
def _(lst, names):
    return [_to_dict(e, names) for e in lst]


@_to_dict.register(Record)
def _(rec, names):
    cls = rec.__class__
    dct1 = {_type: names[cls]}
    dct2 = {f.name: getattr(rec, f.name) for f in _find_fields(cls)}
    return {**dct1, **{k: _to_dict(v, names) for k, v in dct2.items()}}


def _from_json(cls, json):
    idx = _properties.classes(cls)
    return _from_dict(loads(json), idx)


@singledispatch
def _from_dict(obj, _):
    return obj


@_from_dict.register(list)
def _(lst, classes):
    return [_from_dict(e, classes) for e in lst]


@_from_dict.register(dict)
def _(dct, classes):
    cls = classes[dct[_type]]
    dct = {f.name: dct[f.name] for f in _find_fields(cls) if f.name in dct}
    return cls(**{k: _from_dict(v, classes) for k, v in dct.items()})


def _from_args(cls, args):
    if _properties.is_abst(cls):
        key, args = args[0], args[1:]
        if cls := _properties.classes(cls).get(key):
            parser = _properties.parser(cls)
            return _load_args(cls, parser, args)
        return None
    parser = _properties.parser(cls)
    return _load_args(cls, parser, args)


def _load_args(cls, parser, args):
    obj = cls()
    args = parser.parse_args(args)
    for k, v in vars(args).items():
        if v is not _unset:
            setattr(obj, k, v)
    return obj


def _find_arguments(cls):
    yield from (a for a in _find_attributes(cls) if a.is_argument)


def _find_fields(cls):
    yield from (a for a in _find_attributes(cls) if a.is_field)


def _find_attributes(cls):
    ks = set()
    for c in reversed(cls.__mro__):
        for k, v in vars(c).items():
            if k not in ks and isinstance(v, _Attribute):
                yield v
                ks.add(k)


def _get_dash_case_name(cls):
    return sub(r"(?<!^)(?=[A-Z])", "-", cls.__name__).lower()


_extend_actionscontainer(_add_argument, _add_argument_group)

_properties = _Properties()

_unset = object()

_type = "_type"
