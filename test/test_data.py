from json import dumps, loads

from util import data_eq

from mvnb.data import Data
from mvnb.notebook import Cell, Notebook, Output
from mvnb.output import Stderr, Stdout
from mvnb.request import CreateCell, RunCell, UpdateCell
from mvnb.response import DidCreateCell, DidRunCell, DidUpdateCell


def test_notebook_default_fields():
    notebook = Notebook()
    _test(notebook, dict(_type="Notebook", cells=[]))


def test_cell_default_fields():
    cell = Cell()
    _test(cell, dict(_type="Cell", id=None, source=None, parent=None, outputs=[]))


def test_output_default_fields():
    output = Output()
    _test(output, dict(_type="Output", type=None, data=None))


def test_stdout_default_fields():
    stdout = Stdout()
    _test(stdout, dict(_type="Stdout", cell=None, text=None))


def test_stderr_default_fields():
    stderr = Stderr()
    _test(stderr, dict(_type="Stderr", cell=None, text=None))


def test_create_cell_default_fields():
    req = CreateCell()
    assert isinstance(req.id, str)
    assert len(req.id) == 32
    _test(req, dict(_type="CreateCell", id=req.id, cell=None, parent=None))


def test_update_cell_default_fields():
    req = UpdateCell()
    assert isinstance(req.id, str)
    assert len(req.id) == 32
    _test(req, dict(_type="UpdateCell", id=req.id, cell=None, source=None))


def test_run_cell_default_fields():
    req = RunCell()
    assert isinstance(req.id, str)
    assert len(req.id) == 32
    _test(req, dict(_type="RunCell", id=req.id, cell=None))


def test_did_create_cell_default_fields():
    res = DidCreateCell()
    _test(res, dict(_type="DidCreateCell", request=None))


def test_did_update_cell_default_fields():
    res = DidUpdateCell()
    _test(res, dict(_type="DidUpdateCell", request=None))


def test_did_run_cell_default_fields():
    res = DidRunCell()
    _test(res, dict(_type="DidRunCell", request=None))


def _test(data, dct):
    assert loads(data.to_json()) == dct
    assert data_eq(Data.from_json(dumps(dct)), data)
