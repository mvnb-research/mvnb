from functools import cached_property


class Record(object):
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
        for c, l in reversed(fs.items()):
            for e in l:
                yield c, e


class field(object):
    def __init__(self, func):
        self._func = func

    def __get__(self, data, _):
        if data:
            if self.name not in data._cache:
                raw = data._raw.get(self.name)
                val = self._func(data, raw)
                data._cache[self.name] = val
            return data._cache[self.name]
        return self

    def __set__(self, data, raw):
        data._raw[self.name] = raw
        data._cache.pop(self.name, None)

    def __delete__(self, data):
        data._raw.pop(self.name, None)
        data._cache.pop(self.name, None)

    @cached_property
    def name(self):
        return self._func.__name__
