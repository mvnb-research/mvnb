from functools import singledispatchmethod
from uuid import uuid4

from mvnb.util._record import Record, field


class Data(Record, abst=True, group=object()):
    @field
    def id(self, raw):
        return raw or uuid4().hex


class CreateCell(Data):
    @field
    def cell(self, raw):
        return raw or Exception()


class ForkCell(Data):
    @field
    def cell(self, raw):
        return raw or Exception()

    @field
    def parent(self, raw):
        return raw or Exception()


class UpdateCell(Data):
    @field
    def cell(self, raw):
        return raw or Exception()

    @field
    def code(self, raw):
        return raw or Exception()


class RunCell(Data):
    @field
    def cell(self, raw):
        return raw or Exception()


class Output(Data, abst=True):
    @field
    def cell(self, raw):
        return raw or Exception()


class Stdout(Output):
    @field
    def text(self, raw):
        return raw or Exception()


class Response(Data, abst=True):
    @field
    def request(self, raw):
        return raw or Exception()


class DidCreateCell(Response):
    pass


class DidForkCell(Response):
    pass


class DidUpdateCell(Response):
    pass


class DidRunCell(Response):
    pass


class Notebook(Data):
    def __init__(self, **values):
        super().__init__(**values)
        self._index = {}

    @field
    def cells(self, raw):
        return raw or []

    def cell(self, name):
        return self._index.get(name)

    def name(self, worker):
        for c in self.cells:
            if c.worker is worker:
                return c.name

    @singledispatchmethod
    def update(self, _):
        pass

    @update.register(DidCreateCell)
    def _(self, msg):
        cell = Cell(name=msg.request.cell)
        self.cells.append(cell)
        self._index[cell.name] = cell

    @update.register(DidForkCell)
    def _(self, msg):
        cell = Cell(name=msg.request.cell, parent=msg.request.parent)
        self.cells.append(cell)
        self._index[cell.name] = cell

    @update.register(DidUpdateCell)
    def _(self, msg):
        cell = self.cell(msg.request.cell)
        cell.code = msg.request.code

    @update.register(Stdout)
    def _(self, msg):
        cell = self.cell(msg.cell)
        result = Result(type="text", data=msg.text)
        cell.results.append(result)


class Cell(Data):
    def __init__(self, **values):
        super().__init__(**values)
        self.worker = None

    @field
    def name(self, raw):
        return raw or Exception()

    @field
    def code(self, raw):
        return raw

    @field
    def parent(self, raw):
        return raw

    @field
    def results(self, raw):
        return raw or []


class Result(Data):
    @field
    def type(self, raw):
        return raw or Exception()

    @field
    def data(self, raw):
        return raw or Exception()
