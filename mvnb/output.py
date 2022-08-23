from mvnb.data import Data
from mvnb.record import field


class Output(Data, abst=True):
    @field
    def cell(self, raw):
        return raw


class Stdout(Output):
    @field
    def text(self, raw):
        return raw


class Stderr(Output):
    @field
    def text(self, raw):
        return raw
