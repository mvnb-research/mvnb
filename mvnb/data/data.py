from functools import singledispatch
from json import dumps, loads

from bidict import bidict

from mvnb.util.record import Record


class Data(Record):
    def __init_subclass__(cls):
        _classes[cls.__name__] = cls

    @staticmethod
    def from_json(json):
        return _from_json(json)

    def to_json(self):
        return _to_json(self)


def _to_json(data):
    return dumps(_to_dict(data), separators=(",", ":"))


def _from_json(json):
    return _from_dict(loads(json))


@singledispatch
def _to_dict(obj):
    return obj


@_to_dict.register(list)
def _(lst):
    return [_to_dict(e) for e in lst]


@_to_dict.register(Data)
def _(data):
    cls = data.__class__
    dct1 = {_type: _classes.inverse[cls]}
    dct2 = {f.name: getattr(data, f.name) for _, f in cls.fields}
    return {**dct1, **{k: _to_dict(v) for k, v in dct2.items()}}


@singledispatch
def _from_dict(obj):
    return obj


@_from_dict.register(list)
def _(lst):
    return [_from_dict(e) for e in lst]


@_from_dict.register(dict)
def _(dct):
    cls = _classes[dct[_type]]
    dct = {f.name: dct[f.name] for _, f in cls.fields if f.name in dct}
    return cls(**{k: _from_dict(v) for k, v in dct.items()})


_classes = bidict()

_type = "_type"
