from argparse import ArgumentParser, HelpFormatter, _ActionsContainer
from functools import singledispatchmethod
from shutil import get_terminal_size

from mvnb.record import field


class Parser(ArgumentParser):
    def __init__(self, prog, rec):
        super().__init__(
            prog=prog,
            add_help=False,
            allow_abbrev=False,
            formatter_class=_HelpFormatter,
        )
        for f in rec.fields:
            if isinstance(f, option):
                self.add_argument(f)

    def parse(self, args):
        ns = self.parse_args(args)
        return {k: v for k, v in vars(ns).items() if v is not _unset}


class option(field):
    def __init__(self, *args, **kwargs):
        super().__init__(None)
        self._args = [args]
        self._kwargs = [kwargs]
        self._group = None

    def __call__(self, obj):
        if isinstance(obj, option):
            obj._args.extend(self._args)
            obj._kwargs.extend(self._kwargs)
            return obj
        self._func = obj
        return self


class group(object):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def __call__(self, opt):
        opt._group = self
        return opt


class _HelpFormatter(HelpFormatter):
    def __init__(self, prog):
        width = min(get_terminal_size((88, 24)).columns, 88)
        super().__init__(prog, width=width, max_help_position=width)


def _patch_actionscontainer(method):
    name = method.func.__name__[1:]
    attr = getattr(_ActionsContainer, name)
    setattr(_ActionsContainer, f"_{name}", attr)
    setattr(_ActionsContainer, name, method)


@singledispatchmethod
def _add_argument(self, *args, **kwargs):
    return self._add_argument(*args, **kwargs)


@_add_argument.register(option)
def _(self, opt):
    grp = self.add_argument_group(opt)
    dct = dict(dest=opt.name, default=_unset)
    for args, kwargs in zip(opt._args, opt._kwargs):
        args = args or [f"--{opt.name}"]
        args = map(lambda s: s.replace("_", "-"), args)
        grp.add_argument(*args, **{**kwargs, **dct})


@singledispatchmethod
def _add_argument_group(self, *args, **kwargs):
    return self._add_argument_group(*args, **kwargs)


@_add_argument_group.register(option)
def _(self, opt):
    if not hasattr(self, _groups):
        setattr(self, _groups, {})
    if grp := opt._group:
        t = grp._kwargs.get("title", grp._args[0])
        if t not in self._groups:
            a, k = grp._args[1:], grp._kwargs
            g = self.add_argument_group(t, *a, **k)
            self._groups[t] = g
        return self._groups[t]
    return self


_patch_actionscontainer(_add_argument)

_patch_actionscontainer(_add_argument_group)

_groups = "_groups"

_unset = object()
