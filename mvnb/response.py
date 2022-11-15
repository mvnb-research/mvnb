from mvnb.data import field
from mvnb.payload import Payload


class Response(Payload, abst=True):
    @field
    def request(self, raw):
        return raw


class DidCreateCell(Response):
    pass


class DidDeleteCell(Response):
    pass


class DidUpdateCell(Response):
    pass


class DidRunCell(Response):
    pass


class DidSaveNotebook(Response):
    pass
