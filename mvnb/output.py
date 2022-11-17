from uuid import uuid4

from mvnb.data import field
from mvnb.payload import Payload


class Output(Payload, abst=True):
    @field
    def id(self, raw):
        return raw or uuid4().hex

    @field
    def cell(self, raw):
        return raw


class Stdout(Output):
    @field
    def text(self, raw):
        return raw


class RawData(Output):
    @field
    def type(self, raw):
        return raw

    @field
    def data(self, raw):
        return raw
