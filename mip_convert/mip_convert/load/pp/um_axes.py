# (C) British Crown Copyright 2009-2025, Met Office.
# Please see LICENSE.md for license details.
"""Module containing classes representing UM axes."""
__docformat__ = "epytext"


class AbstractHybridHeightCoefficients(object):
    def __new__(cls, *args, **kwargs):
        """Ensures that this is a singleton class."""
        if '_inst' not in vars(cls):
            cls._inst = object.__new__(cls, *args, **kwargs)
        return cls._inst

    def __init__(self):
        """Instantiates a UmL38Axis object."""
        self._zsea_bounds2d = None
        self._c_bounds2d = None

    @property
    def nlevels(self):
        """Number of vertical levels."""
        return len(self._zsea_vals)

    @property
    def zsea_values(self):
        """Return all zsea values."""
        return self._zsea_vals

    @property
    def zsea_bounds(self):
        """Return all zsea boundary values."""
        return self._zsea_bnds

    @property
    def zsea_lbounds(self):
        """Return all zsea lower boundary values."""
        return self._zsea_bnds[:-1]

    @property
    def zsea_ubounds(self):
        """Return all zsea upper boundary values."""
        return self._zsea_bnds[1:]

    @property
    def zsea_bounds2d(self):
        """Return zsea values at lower and upper boundaries as a CF-like 2D array, i.e.
        [[lbnd0, ubnd0], [lbnd1, ubnd1],...]
        """
        if self._zsea_bounds2d:
            return self._zsea_bounds2d
        self._zsea_bounds2d = list()
        for index in range(self.nlevels):
            self._zsea_bounds2d.append([self._zsea_bnds[index], self._zsea_bnds[index + 1]])
        return self._zsea_bounds2d

    @property
    def c_values(self):
        """Return all C co-efficient values."""
        return self._c_vals

    @property
    def c_bounds(self):
        """Return all C co-efficient boundary values."""
        return self._c_bnds

    @property
    def c_lbounds(self):
        """Return all C co-efficient lower boundary values."""
        return self._c_bnds[:-1]

    @property
    def c_ubounds(self):
        """Return all C co-efficient upper boundary values."""
        return self._c_bnds[1:]

    @property
    def c_bounds2d(self):
        """Return C co-efficient values at lower and upper boundaries as a CF-like 2D array, i.e.
        [[lbnd0, ubnd0], [lbnd1, ubnd1],...]
        """
        if self._c_bounds2d:
            return self._c_bounds2d
        self._c_bounds2d = list()
        for index in range(self.nlevels):
            self._c_bounds2d.append([self._c_bnds[index], self._c_bnds[index + 1]])
        return self._c_bounds2d

    def getHeights(self, orography_value):
        """Calculate height coordinates using the specified orography value.
        @param orography_value: The orography value in metres.
        @type  orography_value: float
        @return: A list of height coordinates computed using the specified orography value.
        @rtype: [float]
        """
        heights = list()
        for index in range(self.nlevels):
            heights.append(self._zsea_vals[index] + self._c_vals[index] * orography_value)
        return heights

    def getHeightLowerBounds(self, orography_value):
        """Calculate height coordinates of lower boundaries using the specified orography value.
        @param orography_value: The orography value in metres.
        @type  orography_value: float
        @return: A list of height coordinates computed using the specified orography value.
        @rtype: [float]
        """
        bounds = list()
        for index in range(self.nlevels):
            bounds.append(self._zsea_bnds[index] + self._c_bnds[index] * orography_value)
        return bounds

    def getHeightUpperBounds(self, orography_value):
        """Calculate height coordinates of upper boundaries using the specified orography value.
        @param orography_value: The orography value in metres.
        @type  orography_value: float
        @return: A list of height coordinates computed using the specified orography value.
        @rtype: [float]
        """
        bounds = list()
        for index in range(self.nlevels):
            bounds.append(
                self._zsea_bnds[index + 1] + self._c_bnds[index + 1] * orography_value)
        return bounds

    def getHeightBounds2D(self, orography_value):
        """Calculate height coordinates of lower and upper boundary values as a CF-like 2D array, i.e.
        [[lbnd0, ubnd0], [lbnd1, ubnd1],...]
        @param orography_value: The orography value in metres.
        @type  orography_value: float
        @return: A 2D array of lower and upper boundary height coordinates.
        @rtype: [float]
        """
        bounds = list()
        for index in range(self.nlevels):
            lower = self._zsea_bnds[index] + self._c_bnds[index] * orography_value
            upper = self._zsea_bnds[index + 1] + self._c_bnds[index + 1] * orography_value
            bounds.append([lower, upper])
        return bounds


class UmL38Axis(AbstractHybridHeightCoefficients):
    """Singleton class for representing the 38-level vertical coordinate system used, for example, in
    the HadGEM1 and HadGEM2 atmosphere models.
    """

    # Array of 38 zsea hybrid height values. Equivalent to 'a' parameter in CF
    # formula terms.
    _zsea_vals = [
        20.0, 80.0, 180.0, 320.0, 500.0, 720.0, 980.0, 1280.0, 1620.0, 2000.0, 2420.0, 2880.0, 3380.0,
        3920.0, 4500.0, 5120.0, 5780.0, 6480.0, 7220.0, 8000.0, 8820.0, 9680.0, 10580.0, 11520.0,
        12500.0, 13520.0, 14580.8, 15694.6, 16875.3, 18138.6, 19503.0, 20990.2, 22626.1, 24458.3,
        26583.6, 29219.1, 32908.7, 39254.8]

    # Lower and upper zsea bounds conflated into a single array since layers are non-overlapping.
    # Note: this vector contains one more value than the _zsea_vals vector -
    # the upper bound for level 38.
    _zsea_bnds = [
        0.0, 50.0, 130.0, 250.0, 410.0, 610.0, 850.0, 1130.0, 1450.0, 1810.0, 2210.0, 2650.0, 3130.0,
        3650.0, 4210.0, 4810.0, 5450.0, 6130.0, 6850.0, 7610.0, 8410.0, 9250.0, 10130.0, 11050.0,
        12010.0, 13010.0, 14050.4, 15137.7, 16285.0, 17507.0, 18820.8, 20246.6, 21808.1, 23542.2,
        25521.0, 27901.4, 31063.9, 36081.8, 42427.9]

    # Array of 38 C co-efficients. Equivalent to 'b' parameter in CF formula
    # terms.
    _c_vals = [
        0.997716, 0.990882, 0.979543, 0.963777, 0.943695, 0.919438, 0.891178, 0.859118, 0.823493,
        0.784571, 0.742646, 0.698050, 0.651143, 0.602314, 0.551989, 0.500620, 0.448693, 0.396726,
        0.345265, 0.294891, 0.246215, 0.199878, 0.156554, 0.116948, 0.0817952, 0.0518637, 0.0279368,
        0.0107165, 0.00130179, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    # Lower and upper C co-efficients bounds conflated into a single array since layers are non-overlapping.
    # Note: this vector contains one more value than the _c_vals vector - the
    # upper bound for level 38.
    _c_bnds = [
        1.0, 0.994296, 0.985204, 0.971644, 0.953710, 0.931527, 0.905253, 0.875075, 0.841212,
        0.803914, 0.763465, 0.720176, 0.674393, 0.626491, 0.576877, 0.525991, 0.474301, 0.422310,
        0.370549, 0.319582, 0.270005, 0.222443, 0.177555, 0.136030, 0.0985881, 0.0659808, 0.0389824,
        0.0183147, 0.00487211, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


class RadHalfLevelAxis(AbstractHybridHeightCoefficients):
    """Singleton class for representing the 38-level vertical coordinate system used, for example, in
    the HadGEM1 and HadGEM2 atmosphere models.
    """

    _zsea_vals = [
        0, 49.9988822937012, 130.000228881836, 249.998336791992,
        410.001037597656, 610.00048828125, 850.000610351562, 1130.00146484375,
        1449.9990234375, 1810.00109863281, 2210, 2649.99951171875,
        3129.99975585938, 3650.00073242188, 4209.99853515625, 4810.0009765625,
        5450, 6129.99951171875, 6850, 7610.0009765625, 8409.9990234375,
        9250.0009765625, 10130, 11050, 12010.0009765625, 13010.001953125,
        14050.400390625, 15137.7197265625, 16284.9736328125, 17506.96875,
        18820.8203125, 20246.599609375, 21808.13671875, 23542.18359375,
        25520.9609375, 27901.357421875, 31063.888671875, 36081.76171875,
        42427.90234375]  # better values?

    _zsea_bnds = [
        0,
        20.000337600708,
        80.001350402832,
        179.999114990234,
        320.00146484375,
        500.000579833984,
        720.000366210938,
        980.000854492188,
        1279.998046875,
        1619.99987792969,
        1999.99841308594,
        2420.00170898438,
        2880.00146484375,
        3379.99829101562,
        3919.99951171875,
        4500.00146484375,
        5120,
        5779.99951171875,
        6479.99951171875,
        7220,
        8000.00146484375,
        8820,
        9679.9990234375,
        10579.998046875,
        11519.998046875,
        12499.9990234375,
        13520.0009765625,
        14580.7998046875,
        15694.6396484375,
        16875.310546875,
        18138.626953125,
        19503.009765625,
        20990.1875,
        22626.08203125,
        24458.28515625,
        26583.640625,
        29219.080078125,
        32908.69140625,
        39254.83203125,
        42427.90234375]

    _c_vals = [
        1., 0.994296252727509, 0.985203862190247,
        0.971644043922424, 0.953709840774536, 0.931527435779572,
        0.905253052711487, 0.875074565410614, 0.84121161699295, 0.80391401052475,
        0.763464510440826, 0.720175802707672, 0.674392521381378,
        0.626490533351898, 0.576877355575562, 0.525990784168243,
        0.474301367998123, 0.422309905290604, 0.370548874139786, 0.3195820748806,
        0.270004868507385, 0.222443267703056, 0.177555426955223,
        0.136030226945877, 0.0985881090164185, 0.0659807845950127,
        0.0389823913574219, 0.0183146875351667, 0.00487210927531123, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0]

    _c_bnds = [
        1, 0.99771648645401,
        0.990881502628326,
        0.979542553424835,
        0.9637770652771,
        0.943695485591888,
        0.919438362121582,
        0.891178011894226,
        0.859118342399597,
        0.823493480682373,
        0.784570515155792,
        0.742646217346191,
        0.698050200939178,
        0.651142716407776,
        0.602314412593842,
        0.55198872089386,
        0.500619947910309,
        0.44869339466095,
        0.39672577381134,
        0.34526526927948,
        0.294891387224197,
        0.24621507525444,
        0.199878215789795,
        0.156554222106934,
        0.116947874426842,
        0.0817952379584312,
        0.0518637150526047,
        0.0279368180781603,
        0.0107164792716503,
        0.00130179093685001,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0]
