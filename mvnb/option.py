from argparse import ArgumentParser, HelpFormatter, _ActionsContainer, _VersionAction
from functools import singledispatchmethod
from shutil import get_terminal_size

from mvnb.data import field


class Parser(ArgumentParser):
    def __init__(self, prog, data):
        super().__init__(
            prog=prog,
            add_help=False,
            allow_abbrev=False,
            formatter_class=_HelpFormatter,
            usage=f"{prog} [options]",
        )
        for f in data.fields:
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

    def __call__(self, obj):
        if isinstance(obj, option):
            obj._args.extend(self._args)
            obj._kwargs.extend(self._kwargs)
            return obj
        self._func = obj
        return self


class _HelpFormatter(HelpFormatter):
    def __init__(self, prog):
        width = min(get_terminal_size().columns, 80)
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
    dct = dict(dest=opt.name, default=_unset)
    for args, kwargs in zip(opt._args, opt._kwargs):
        args = args or [f"--{opt.name}"]
        args = map(lambda s: s.replace("_", "-"), args)
        action = self.add_argument(*args, **{**kwargs, **dct})
        if isinstance(action, _VersionAction):
            action.version = opt._func(None, None)


_patch_actionscontainer(_add_argument)

_unset = object()
