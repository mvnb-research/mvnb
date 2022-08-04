from uuid import uuid4

from mvnb.record import Record, field


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
