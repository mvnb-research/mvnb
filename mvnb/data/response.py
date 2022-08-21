from mvnb.data.data import Data
from mvnb.util.record import field


class Response(Data):
    @field
    def request(self, raw):
        return raw


class DidCreateCell(Response):
    pass


class DidUpdateCell(Response):
    pass


class DidRunCell(Response):
    pass
