def data_eq(data1, data2):
    if data1.__class__ is data2.__class__:
        for f in data1.fields:
            if getattr(data1, f.name) != getattr(data2, f.name):
                return False
        return True
    return False
