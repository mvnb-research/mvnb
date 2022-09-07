from mvnb.payload import Payload
from mvnb.record import field


class Response(Payload, abst=True):
    @field
    def request(self, raw):
        return raw


class DidCreateCell(Response):
    pass


class DidUpdateCell(Response):
    pass


class DidRunCell(Response):
    pass
