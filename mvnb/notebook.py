from mvnb.payload import Payload
from mvnb.record import field


class Notebook(Payload):
    @field
    def cells(self, raw):
        return raw or []


class Cell(Payload):
    @field
    def id(self, raw):
        return raw

    @field
    def source(self, raw):
        return raw

    @field
    def parent(self, raw):
        return raw

    @field
    def outputs(self, raw):
        return raw or []


class Output(Payload):
    @field
    def type(self, raw):
        return raw

    @field
    def data(self, raw):
        return raw
