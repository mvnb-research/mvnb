def payload_eq(payload1, payload2):
    if payload1.__class__ is payload2.__class__:
        for f in payload1.fields:
            if getattr(payload1, f.name) != getattr(payload2, f.name):
                return False
        return True
    return False
