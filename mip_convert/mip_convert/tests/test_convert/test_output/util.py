# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.


class AnyStruct(object):
    """
    a structure that can be added to
    """

    def __init__(self, **kwargs):
        for arg, value in list(kwargs.items()):
            setattr(self, arg, value)


class DummyVar(AnyStruct):
    is_rotated = False
    is_tripolar = False

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

    def time(self):
        return self.getAxis('T')

    def getAxisList(self):
        return self.axes

    def getAxisOrder(self):
        result = list()
        for axis in self.getAxisList():
            result.append(axis.axis)
        return tuple(result)

    def getAxis(self, axis_direction):
        for axis in self.axes:
            if axis.axis == axis_direction:
                return axis
        raise Exception('no axis on test class')

    def getValue(self):
        return self.data


class DummyAxis(AnyStruct):
    def __init__(self, no_bounds=False, **kwargs):
        super(DummyAxis, self).__init__(**kwargs)
        self.is_hybrid_height = False
        self.no_bounds = no_bounds

    def __len__(self):
        return self.len

    @property
    def id(self):
        return self.axis

    @property
    def len(self):
        return len(self.getValue())

    @property
    def is_scalar(self):
        return self.len == 1

    def getValue(self):
        return self.data

    def getBounds(self):
        if self.no_bounds:
            return None
        else:
            return [self.data, self.data]
    bounds = property(getBounds)


class DummyHybrid(DummyAxis):

    def __init__(self, **kwargs):
        super(DummyHybrid, self).__init__(**kwargs)
        self.is_hybrid_height = True

    def getBvalues(self):
        return self.b

    def getBbounds(self):
        return self.b_bounds

    def getOrography(self):
        return self.orog

    def getOrographyUnits(self):
        return self.orog_units
