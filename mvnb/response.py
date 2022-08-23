from mvnb.data import Data
from mvnb.record import field


class Response(Data, abst=True):
    @field
    def request(self, raw):
        return raw


class DidCreateCell(Response):
    pass


class DidUpdateCell(Response):
    pass


class DidRunCell(Response):
    pass
