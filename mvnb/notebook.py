from mvnb.data import field
from mvnb.payload import Payload


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

    @field
    def x(self, raw):
        return raw or 0

    @field
    def y(self, raw):
        return raw or 0

    @field
    def done(self, raw):
        return bool(raw)


class Output(Payload):
    @field
    def id(self, raw):
        return raw

    @field
    def type(self, raw):
        return raw

    @field
    def data(self, raw):
        return raw
