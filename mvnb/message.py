from uuid import uuid4

from mvnb.record import Record, field


class Message(Record, abst=True, group=object()):
    @field
    def id(self, raw):
        return raw or uuid4().hex


class CreateCell(Message):
    @field
    def cell(self, raw):
        return raw or Exception()


class ForkCell(Message):
    @field
    def cell(self, raw):
        return raw or Exception()

    @field
    def parent(self, raw):
        return raw or Exception()


class UpdateCell(Message):
    @field
    def cell(self, raw):
        return raw or Exception()

    @field
    def code(self, raw):
        return raw or Exception()


class RunCell(Message):
    @field
    def cell(self, raw):
        return raw or Exception()


class Output(Message, abst=True):
    @field
    def cell(self, raw):
        return raw or Exception()


class Stdout(Output):
    @field
    def text(self, raw):
        return raw or Exception()


class Response(Message, abst=True):
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
