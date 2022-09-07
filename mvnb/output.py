from mvnb.data import field
from mvnb.payload import Payload


class Output(Payload, abst=True):
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
