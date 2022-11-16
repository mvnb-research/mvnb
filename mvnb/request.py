from uuid import uuid4

from mvnb.data import field
from mvnb.payload import Payload


class Request(Payload, abst=True):
    @field
    def id(self, raw):
        return raw or uuid4().hex

    @field
    def user(self, raw):
        return raw

    @field
    def cell(self, raw):
        return raw


class CreateCell(Request):
    @field
    def parent(self, raw):
        return raw

    @field
    def x(self, raw):
        return raw or 0

    @field
    def y(self, raw):
        return raw or 0


class MoveCell(Request):
    @field
    def x(self, raw):
        return raw or 0

    @field
    def y(self, raw):
        return raw or 0


class DeleteCell(Request):
    pass


class UpdateCell(Request):
    @field
    def source(self, raw):
        return raw


class RunCell(Request):
    pass


class SaveNotebook(Payload):
    pass
