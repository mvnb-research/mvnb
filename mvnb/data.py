from functools import cached_property
from itertools import chain


class Data(object):
    def __init__(self, **raw):
        self._raw = raw
        self._cache = {}

    @classmethod
    @property
    def fields(cls):
        fs, ks = {}, set()
        for c in cls.__mro__:
            for k, v in vars(c).items():
                if k not in ks and isinstance(v, field):
                    fs.setdefault(c, []).append(v)
                    ks.add(k)
        return chain(*reversed(fs.values()))


class field(object):
    def __init__(self, func):
        self._func = func

    def __get__(self, rec, _):
        if rec:
            if self.name not in rec._cache:
                raw = rec._raw.get(self.name)
                val = self._func(rec, raw)
                rec._cache[self.name] = val
            return rec._cache[self.name]
        return self

    def __set__(self, rec, raw):
        rec._raw[self.name] = raw
        rec._cache.pop(self.name, None)

    def __delete__(self, rec):
        rec._raw.pop(self.name, None)
        rec._cache.pop(self.name, None)

    @cached_property
    def name(self):
        return self._func.__name__
