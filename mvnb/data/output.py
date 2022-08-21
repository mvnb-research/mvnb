from mvnb.data.data import Data
from mvnb.util.record import field


class Output(Data):
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
