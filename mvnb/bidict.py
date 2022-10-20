from collections.abc import MutableMapping


class BiDict(MutableMapping):
    def __init__(self):
        self._dct = {}
        self._rev = {}

    def __getitem__(self, key):
        return self._dct[key]

    def __setitem__(self, key, val):
        self._dct[key] = val
        self._rev[val] = key

    def __delitem__(self, key):
        val = self[key]
        del self._dct[key]
        del self._rev[val]

    def __iter__(self):
        return iter(self._dct)

    def __len__(self):
        return len(self._dct)

    def find_key(self, val):
        return self._rev.get(val)
