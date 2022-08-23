from mvnb.data import Data
from mvnb.record import field


class Notebook(Data):
    @field
    def cells(self, raw):
        return raw or []


class Cell(Data):
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


class Output(Data):
    @field
    def type(self, raw):
        return raw

    @field
    def data(self, raw):
        return raw
