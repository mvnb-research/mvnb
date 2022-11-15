from uuid import uuid4

from mvnb.data import field
from mvnb.payload import Payload


class Request(Payload, abst=True):
    @field
    def id(self, raw):
        return raw or uuid4().hex

    @field
    def cell(self, raw):
        return raw


class CreateCell(Request):
    @field
    def parent(self, raw):
        return raw


class UpdateCell(Request):
    @field
    def source(self, raw):
        return raw


class RunCell(Request):
    pass


class SaveNotebook(Payload):
    pass
