from json import dumps, loads

from util import payload_eq

from mvnb.notebook import Cell, Notebook, Output
from mvnb.output import Stdout
from mvnb.payload import Payload
from mvnb.request import CreateCell, RunCell, UpdateCell
from mvnb.response import DidCreateCell, DidRunCell, DidUpdateCell


def test_notebook_default_fields():
    notebook = Notebook()
    _test(notebook, dict(_type="Notebook", cells=[]))


def test_cell_default_fields():
    cell = Cell()
    _test(
        cell,
        dict(
            _type="Cell",
            id=None,
            source=None,
            parent=None,
            outputs=[],
            x=0,
            y=0,
            done=False,
        ),
    )


def test_output_default_fields():
    output = Output()
    _test(output, dict(_type="Output", id=None, type=None, data=None))


def test_stdout_default_fields():
    stdout = Stdout()
    _test(stdout, dict(_type="Stdout", id=stdout.id, cell=None, text=None))


def test_create_cell_default_fields():
    req = CreateCell()
    assert isinstance(req.id, str)
    assert len(req.id) == 32
    _test(
        req,
        dict(
            _type="CreateCell", id=req.id, user=None, cell=None, parent=None, x=0, y=0
        ),
    )


def test_update_cell_default_fields():
    req = UpdateCell()
    assert isinstance(req.id, str)
    assert len(req.id) == 32
    _test(req, dict(_type="UpdateCell", id=req.id, user=None, cell=None, source=None))


def test_run_cell_default_fields():
    req = RunCell()
    assert isinstance(req.id, str)
    assert len(req.id) == 32
    _test(req, dict(_type="RunCell", id=req.id, user=None, cell=None))


def test_did_create_cell_default_fields():
    res = DidCreateCell()
    _test(res, dict(_type="DidCreateCell", request=None))


def test_did_update_cell_default_fields():
    res = DidUpdateCell()
    _test(res, dict(_type="DidUpdateCell", request=None))


def test_did_run_cell_default_fields():
    res = DidRunCell()
    _test(res, dict(_type="DidRunCell", request=None))


def _test(payload, dct):
    assert loads(payload.to_json()) == dct
    assert payload_eq(Payload.from_json(dumps(dct)), payload)
