# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import unittest

from header_util import BaseHeader
from mip_convert.load.pp.pp_axis import (
    AxisStretchedY, AxisZ, BoundedAxis, DatedPpHeader, HybridHeightFromPp,
    LANDTYPE_AXIS, PpAxisError, PpAxisFactory, TimeExtractor)
from mip_convert.model_date import CdDate, set_base_date, set_default_base_date


class AbstractAxisTest(unittest.TestCase):

    def setUp(self):
        self.axis_factory = PpAxisFactory(None)


class TestZaxis(AbstractAxisTest):

    SUPPORTED_LEVELS = (1, 8, 19, 128, 129)
    LEVEL_UNITS = ('m', 'hPa', 'K', 'm', 'm')

    def _make_multi_level(self, lbvc, levels):
        headers = []
        for level in levels:
            header = BaseHeader()
            header.lbvc = lbvc
            header.blev = level
            headers.append(header)
        return headers
    # none monotonic?

    def _make_axis(self, headers):
        return self.axis_factory.getZAxis(headers, [{}])

    def setUp(self):
        super(self.__class__, self).setUp()
        self.base_header = BaseHeader()

    def testInValidLevType(self):
        self.base_header.blev = 100.
        self.base_header.lbvc = 9
        self.assertRaises(PpAxisError, self._make_axis, [self.base_header])

    def testDifferentLevelCodeError(self):
        headers = []
        for lbvc in self.SUPPORTED_LEVELS:
            header = BaseHeader()
            header.lbvc = lbvc
            header.blev = 10
            headers.append(header)
        self.assertRaises(PpAxisError, self._make_axis, headers)

    def testSameLevelError(self):
        headers = self._make_multi_level(1, (10, 20, 10))
        self.assertRaises(PpAxisError, self._make_axis, headers)

    def testGetLevels(self):
        good_lev_types = self.SUPPORTED_LEVELS
        units = self.LEVEL_UNITS
        levels = [100, 200, 300]

        for (lev_type, unit) in zip(good_lev_types, units):
            headers = self._make_multi_level(lev_type, levels)
            axis = self._make_axis(headers)

            self.assertEqual('Z', axis.axis)
            self.assertEqual(levels, axis.getValue())
            self.assertEqual(unit, axis.units)
            self.assertFalse(axis.is_hybrid_height)
            self.assertEqual(len(levels) == 1, axis.is_scalar)
            self.assertEqual(len(levels), len(axis))


class TestZDepth(AbstractAxisTest):

    def testBounds(self):
        header = BaseHeader()
        header.lbvc = 2
        header.blev = 0.05
        header.brlev = 0.1
        header.brsvd1 = 0
        axis = self.axis_factory.getZAxis([header], [{}])

        self.assertEqual('m', axis.units)
        self.assertEqual([header.blev], axis.getValue())
        self.assertEqual([[header.brsvd1, header.brlev]], axis.getBounds())


class TestBoundedAxis(unittest.TestCase):
    def testSingleValueCollapse(self):
        axis = BoundedAxis('Z', 'm', [1.], [[0.5, 1.5], ])
        collapsed = axis.collapse()
        self.assertEqual(axis, collapsed)

    def testCollapse(self):
        axis = BoundedAxis('Z', 'm', [1., 2.], [[0.5, 1.5], [1.5, 2.5]])
        collapsed = axis.collapse()
        self.assertEqual(BoundedAxis('Z', 'm', [(0.5 + 2.5) / 2], [[0.5, 2.5]]), collapsed)


class TestNoValueZ(AbstractAxisTest):

    def _makeHeader(self, vc, blev):
        header = BaseHeader()
        header.lbvc = vc
        header.blev = blev
        return header

    def _makeAxis(self, vc, blev):
        header = self._makeHeader(vc, blev)
        axis = self.axis_factory.getZAxis([header], [{}])
        return axis

    def testAxisDirection(self):
        blev = -1.
        for vc in (0, 5, 133, 137, 138):
            axis = self._makeAxis(vc, blev)
            self.assertEqual('Z', axis.axis)
            self.assertFalse(axis.is_hybrid_height)
            self.assertRaises(PpAxisError, axis.getValue)
            self.assertRaises(PpAxisError, axis.getBounds)
            self.assertTrue(axis.is_scalar)

    def testEqualCases(self):
        z1 = self._makeAxis(0, -1.)
        z2 = self._makeAxis(0, -1.)
        self.assertTrue(z1 == z2)
        self.assertFalse(z1 != z2)

    def testNotEqualsCases(self):
        z1 = self._makeAxis(0, -1.)
        z2 = self._makeAxis(133, -1.)
        self.assertFalse(z1 == z2)
        self.assertTrue(z1 != z2)

        z2 = self._makeAxis(0, -2.)
        self.assertFalse(z1 == z2)
        self.assertTrue(z1 != z2)

        z2 = self._makeAxis(1, 1)
        self.assertFalse(z1 == z2)
        self.assertFalse(z2 == z1)
        self.assertTrue(z1 != z2)


class DummyVar(object):

    def __init__(self, data, axes):
        self._values = data
        self._axes = axes

    def getValue(self):
        return self._values

    def getAxis(self, axis_dir):
        return self._axes[axis_dir]


class DummyAxis(object):
    def __init__(self, data, axis):
        self._values = data
        self.axis = axis

    def __eq__(self, other):
        result = True
        result = result and self.axis == other.axis
        result = result and self._values == other._values
        return result

    def different(self):
        data = [x + 1 for x in self._values]
        return DummyAxis(data, self.axis)


class TestSingleHeightOnSite(unittest.TestCase):
    """
    test case in place for situation when the site data
    is not on model levels
    """

    def testSinglHeight(self):
        headers = [BaseHeader(blev=1.5, lbvc=1, lbcode=11320)]
        extras = [{7: [1]}]
        axis_factory = PpAxisFactory(self)
        zaxis = axis_factory.getZAxis(headers, extras)
        self.assertEqual([1.5], zaxis.getValue())

    def testSinglHybrid(self):
        headers = [BaseHeader(blev=20, lbvc=65, lbcode=11320, bdx=0.0)]
        extras = [{7: [1]}]
        axis_factory = PpAxisFactory(self)
        zaxis = axis_factory.getZAxis(headers, extras)
        self.assertEqual([20], zaxis.getValue())


class TestHybridHeightPpAxis(unittest.TestCase):
    units = 'm'

    def getOrography(self, axisX, axisY):
        result = None
        if self.orography.getAxis('X') == axisX and \
           self.orography.getAxis('Y') == axisY:
            result = self.orography
        return result

    def makeSampleHeader(self, value, bvalue):
        """
        return a sample pp header
        """
        header = BaseHeader()
        header.lbvc = 65
        header.blev = value
        header.bhlev = bvalue
        header.brlev = header.blev - 0.5
        header.brsvd1 = header.blev + 1.5
        header.bhrlev = header.bhlev - 1
        header.brsvd2 = header.bhlev + 1
        return header

    def makeAxisOrography(self, headers, extras):
        self.axisX = self.axis_factory.getXAxis(headers[0])
        self.axisY = self.axis_factory.getYAxis(headers, extras)
        self.orography = DummyVar(list(range(10)), axes={'X': self.axisX, 'Y': self.axisY})

    def setUp(self):
        self.axis_factory = PpAxisFactory(self)

    def testInvalidHeader(self):
        header = BaseHeader()
        header.lbvc = 1

        self.makeAxisOrography([header], [{}])

        # leave explicit constructor as protection
        self.assertRaises(PpAxisError, HybridHeightFromPp, [header], self, self.axisX, self.axisY)

    def testRepeatValue(self):
        header1 = self.makeSampleHeader(1.0, 100)
        header2 = self.makeSampleHeader(1.0, 100)
        headers = [header1, header2]
        extras = [{}, {}]
        self.makeAxisOrography(headers, extras)
        self.assertRaises(PpAxisError, self.axis_factory.getZAxis, headers, extras)

    def testAxisWithMultipleHeaders(self):
        header1 = self.makeSampleHeader(1.0, 100)
        header2 = self.makeSampleHeader(2.0, 102)
        headers = [header1, header2]
        extras = [{}, {}]

        self.makeAxisOrography(headers, extras)

        self.axis = self.axis_factory.getZAxis(headers, extras)
        self.assertEqual(self.axis.axis, 'Z')
        self.assertEqual(self.axis.units, 'm')
        self.assertTrue(self.axis.is_hybrid_height)
        self.assertEqual(self.axis.getValue(), [header1.blev, header2.blev])
        self.assertEqual(self.axis.getBounds(), [[header1.brlev, header1.brsvd1], [header2.brlev, header2.brsvd1]])
        self.assertEqual(self.axis.getBvalues(), [header1.bhlev, header2.bhlev])
        self.assertEqual(self.axis.getBbounds(), [[header1.bhrlev, header1.brsvd2], [header2.bhrlev, header2.brsvd2]])
        self.assertEqual(self.axis.getOrography(), self.orography.getValue())
        self.assertEqual(self.axis.getOrographyUnits(), self.units)


class DummyRecord(object):
    def __init__(self, header):
        self._dated_header = DatedPpHeader(header)


class AbstractTimeAxisTest(AbstractAxisTest):

    def _make_records(self, headers):
        return [DummyRecord(header) for header in headers]

    def getAxis(self, headers):
        return TimeExtractor().getAxis(self._make_records(headers))


class TestClimatologyAxis(AbstractTimeAxisTest):
    def _make_headers(self, lbmon, lbyrd, lbmond):
        header = BaseHeader(lbproc=128, lbtim=32, lbyr=1859, lbmon=lbmon)
        header.lbyrd = lbyrd
        header.lbmond = lbmond
        return [header]

    def test_axis_values(self):
        set_base_date(CdDate(1859, 1, 1, 0, 0, 0, '360_day'))
        axis = self.getAxis(self._make_headers(1, 1859 + 1, 1 + 1))
        self.assertEqual([15.], axis.getValue())
        self.assertEqual([[0, 360 * 1 + 30]], axis.getBounds())

    def test_year_end_values(self):
        set_base_date(CdDate(1859, 12, 1, 0, 0, 0, '360_day'))
        axis = self.getAxis(self._make_headers(12, 1870, 1))
        self.assertEqual([15.], axis.getValue())
        self.assertEqual([[0, 360 * 10 + 30]], axis.getBounds())

    def tearDown(self):
        set_default_base_date()


class TestBoundedTAxis(AbstractTimeAxisTest):
    # lbproc same?
    # monotonic
    # equal spaced?
    # start date different, end date the same? not sure about this test?

    def _headers_with_time(self, ntimes, lbproc, lbtim=22):
        headers = list()
        for month in range(ntimes):
            header = BaseHeader(lbproc=lbproc, lbtim=lbtim, lbyr=1900, lbmon=1 + month, lbday=1)
            headers.append(header)
        return headers

    def assertOnAddHeaders(self, headers):
        self.assertRaises(PpAxisError, self.getAxis, headers)

    def assertOnAxis(self, axis, values, bounds):
        self.assertEqual('T', axis.axis)
        self.assertEqual('days since 1900-01-01', axis.units)
        self.assertEqual(values, axis.getValue())
        self.assertEqual(bounds, axis.getBounds())

    def setUp(self):
        super(self.__class__, self).setUp()
        self.base_header = BaseHeader()

    def testNon360Day(self):
        self.base_header.lbtim = 1  # why isn't this failing?
        self.assertOnAddHeaders([self.base_header])

    def testNonTimeMean(self):
        self.base_header.lbproc = 0
        self.base_header.lbtim = 22
        self.assertOnAddHeaders([self.base_header])

    def testAxisValues(self):
        self.make_axis_factory(1900, 1, 1, '360_day')
        for lbproc in (128, 4096, 8192, 128 + 4096):
            headers = self._headers_with_time(2, lbproc, 322)
            axis = self.getAxis(headers)

            self.assertOnAxis(axis, [15.0, 45.0], [[0.0, 30.0], [30.0, 60.0]])

    def testAxisValuesGregorian(self):

        self.make_axis_factory(1900, 1, 1, 'proleptic_gregorian')
        for lbproc in (128, 4096, 8192, 128 + 4096):
            headers = self._headers_with_time(2, lbproc, 21)
            axis = self.getAxis(headers)

            self.assertOnAxis(axis, [(0. + 31) / 2, 31 + 28 / 2], [[0, 31], [31, 31 + 28]])

    def make_axis_factory(self, year, mon, day, calendar):
        set_base_date(CdDate(year, mon, day, 0, 0, 0, calendar))
        self.axis_factory = PpAxisFactory(None)

    def tearDown(self) -> None:
        set_default_base_date()


class TestInstantaneousTime(AbstractTimeAxisTest):
    def makeExampleHeaders(self, lbtime):
        headers = list()
        for month in range(1, 3):
            header = BaseHeader(lbtim=lbtime, lbproc=0, lbyr=1990, lbmon=month, lbdat=1, lbhr=0, lbmin=0)
            headers.append(header)
        return headers

    def testMultiHeaders(self):
        for time, values, year, calendar in ((12, [0, 30], 1990, '360_day'),
                                             (12, [360, 390], 1989, '360_day'),
                                             (11, [0, 31], 1990, 'proleptic_gregorian'),
                                             (11, [365, 365 + 31], 1989, 'proleptic_gregorian')):
            set_base_date(CdDate(year, 1, 1, 0, 0, 0, calendar))
            self.axis_factory = PpAxisFactory(None)
            headers = self.makeExampleHeaders(time)
            axis = self.getAxis(headers)

            self.assertEqual(values, axis.getValue())
            self.assertEqual(None, axis.getBounds())

    def testPpLbproc2176(self):
        set_base_date(CdDate(1989, 1, 1, 0, 0, 0, 'proleptic_gregorian'))
        headers = self.makeExampleHeaders(21)
        for header in headers:
            header.lbproc = 2176
        self.getAxis(headers)

    def testInconsistentHeaders(self):
        headers = self.makeExampleHeaders(12)
        headers[-1].lbtim = 22
        self.assertRaises(PpAxisError, self.getAxis, headers)

    def testInconsistenLbproc(self):
        headers = self.makeExampleHeaders(12)
        headers[-1].lbproc = 128
        self.assertRaises(PpAxisError, self.getAxis, headers)

    def tearDown(self):
        set_default_base_date()


class TestRegularLong(AbstractAxisTest):

    def testGetXAxis(self):
        header = BaseHeader()
        header.lbnpt = 3
        header.bdx = 0.5
        header.bzx = 1
        axis = self.axis_factory.getXAxis(header)
        self.assertEqual('degrees_east', axis.units)
        self.assertEqual([header.bzx + (x + 1) * header.bdx for x in range(header.lbnpt)], axis.getValue())
        self.assertEqual([[1.25, 1.75], [1.75, 2.25], [2.25, 2.75]], axis.getBounds())

    def testGetXAxisRegionalUnRotatedWithWrap(self):
        header = BaseHeader()
        header.lbnpt = 3
        header.bdx = 2.
        header.bzx = 356
        axis = self.axis_factory.getXAxis(header)
        self.assertEqual('degrees_east', axis.units)
        self.assertEqual([-2., 0., 2.], axis.getValue())
        self.assertEqual([[-3., -1.], [-1., 1.], [1., 3.]], axis.getBounds())

    def testZonalMeanOnLbproc(self):
        header = BaseHeader()
        header.lbnpt = 1
        header.bdx = 358.125

        for proc in (64, 192):
            for zx in (-0.938, -1.875):
                header.bzx = zx
                header.lbproc = proc
                axis = self.axis_factory.getXAxis(header)
                self.assertEqual('degrees_east', axis.units)
                self.assertEqual([180.], axis.getValue())
                self.assertEqual([[0., 360]], axis.getBounds())

    def testZonalMeanOnSingleLon(self):
        header = BaseHeader()
        header.lbnpt = 1
        header.bdx = 360
        header.proc = 128
        header.bzx = 1.0
        axis = self.axis_factory.getXAxis(header)
        self.assertEqual('degrees_east', axis.units)
        self.assertEqual([180.], axis.getValue())
        self.assertEqual([[0., 360]], axis.getBounds())

    def testErrorIfLbprocZonalNptNotOne(self):
        header = BaseHeader()
        header.lbnpt = 2
        header.bdx = 360
        header.lbproc = 64
        header.bzx = 1.0
        self.assertRaises(PpAxisError, self.axis_factory.getXAxis, header)


class TestRotatedRegularLong(AbstractAxisTest):

    def testGetXAxis(self):
        header = self._get_header(1)

        axis = self.axis_factory.getXAxis(header)

        self.assertEqual('degrees', axis.units)
        self.assertEqual([header.bzx + (x + 1) * header.bdx for x in range(header.lbnpt)], axis.getValue())

    def testGetYaxis(self):
        header = self._get_header(1)
        axis = self.axis_factory.getYAxis([header], [{}])

        self.assertEqual('degrees', axis.units)
        self.assertEqual([header.bzy + (y + 1) * header.bdy for y in range(header.lbrow)], axis.getValue())

    def _get_header(self, zx=1):
        header = BaseHeader()
        header.lbcode = 101
        header.lbrow = 3
        header.lbnpt = 3
        header.bdy = 0.5
        header.bzy = 1
        header.bdx = 0.5
        header.bzx = zx
        return header


class TestRegularLatForHigem(AbstractAxisTest):
    def testLatExtremes(self):
        header = BaseHeader()
        header.lbrow = 217
        scale = 1
        for scale in (1, -1):
            header.bdy = 0.83333 * scale
            header.bzy = -90.833333 * scale
            axis = self.axis_factory.getYAxis([header], [None])
            self.assertEqual(-90. * scale, axis.getValue()[0], 'scale: %d' % scale)
            self.assertEqual(-90. * scale,
                             axis.getBounds()[0][0], 'scale: %d bounds %f' % (scale, axis.getBounds()[0][0]))
            self.assertEqual(90. * scale, axis.getBounds()[-1][1], 'scale: %d' % scale)

    def testN216(self):
        header = BaseHeader()
        header.lbrow = 325
        header.bdy = 0.555555582047
        header.bzy = -90.555557251
        axis = self.axis_factory.getYAxis([header], [None])
        self.assertEqual(90., axis.getValue()[-1])
        self.assertTrue(axis.getBounds()[-2][1] == axis.getBounds()[-1][0])


class TestStretchedYAxis(AbstractAxisTest):
    def setUp(self):
        super(self.__class__, self).setUp()
        self.header = None

    def _make_y_axis(self, header, extra_data):
        return self.axis_factory.getYAxis([header], [extra_data])

    def _make_grid_header(self):
        header = BaseHeader()
        header.lbcode = 1  # check this
        header.lbext = 1
        return header

    def _make_regular_header(self):
        header = self._make_grid_header()
        header.lbext = 0
        header.bdy = 2.5
        return header

    def _make_stretched_header(self):
        header = self._make_grid_header()
        header.lbext = 1
        header.bdy = 0
        return header

    def testErrorOnGridCode(self):
        header = self._make_regular_header()
        # leave explict
        self.assertRaises(PpAxisError, AxisStretchedY, header, None)

    def testErrorOnIncompleteExtraData(self):
        header = self._make_stretched_header()
        extra_data = {
            2: list(range(1)),
            14: list(range(1)),
        }
        self.assertRaises(PpAxisError, self._make_y_axis, header, extra_data)

    def testGetDataFromExtra(self):
        header = self._make_stretched_header()
        extra_data = {
            2: [2., 4.],
            14: [1., 3.],
            15: [3., 5.]
        }
        expect_bounds = [[1., 3.], [3., 5.]]
        axis = self._make_y_axis(header, extra_data)
        self.assertEqual('degrees_north', axis.units)
        self.assertEqual('Y', axis.axis)
        self.assertEqual(extra_data[2], axis.getValue())
        self.assertEqual(expect_bounds, axis.getBounds())

    def testEqualBoundsOnStretchedAxis(self):
        header1 = self._make_stretched_header()
        extra_data1 = {
            2: [2., 4.],
            14: [1., 3.],
            15: [3., 5.]
        }
        header2 = self._make_stretched_header()
        extra_data2 = {
            2: [2., 4.],
            14: [1.5, 3.5],
            15: [3., 5.]
        }
        axis1 = self._make_y_axis(header1, extra_data1)
        axis2 = self._make_y_axis(header2, extra_data2)
        self.assertFalse(axis1 == axis2)


class TestAxisEquals(AbstractAxisTest):

    def _make_z_axes(self, attribute, values):
        axes = list()
        for value in values:
            header = BaseHeader()
            setattr(header, attribute, value)
            axis = self.axis_factory.getZAxis([header], [])
            axes.append(axis)
        return axes

    def setUp(self):
        super(TestAxisEquals, self).setUp()
        self.header = BaseHeader()

    def testUnEqualAxis(self):
        y_axis = self.axis_factory.getYAxis([self.header], [None])
        x_axis = self.axis_factory.getXAxis(self.header)
        self.assertFalse(x_axis == y_axis)

    def testUnEqualsUnits(self):
        axes = self._make_z_axes('lbvc', (1, 8))
        self.assertFalse(axes[0] == axes[1])

    def testUnEqualsValues(self):
        axes = self._make_z_axes('blev', (10, 100))
        self.assertFalse(axes[0] == axes[1])

    def testEqualAxis(self):
        axis1 = self.axis_factory.getXAxis(self.header)
        axis2 = self.axis_factory.getXAxis(self.header)
        self.assertTrue(axis1 == axis2)


class TestPsuedoLandAxis(unittest.TestCase):

    def setUp(self):
        self.axis_factory = PpAxisFactory(self)

    def makeHeaders(self, example):
        headers = list()
        for pseudo in example:
            header = BaseHeader()
            header.lbuser4 = 19013
            header.lbuser5 = pseudo
            headers.append(header)
        return headers

    def testPseudoErrors(self):
        examples = [[]]

        header = BaseHeader()
        header.lbuser4 = 101
        examples.append([header])

        for example in examples:
            self.assertRaises(PpAxisError, self.axis_factory.getPseudoAxis, example)

    def testPseudoLevels(self):
        type_descriptions = [
            'broadleaf trees',
            'needleleaf trees',
            'C3 (temperate) grass',
            'C4 (tropical) grass',
            'shrubs',
            'urban',
            'inland water',
            'bare soil',
            'ice'
        ]
        for example in ((1,), (2,), (1, 2,)):
            headers = self.makeHeaders(example)
            axis = self.axis_factory.getPseudoAxis(headers)

            self.assertEqual(LANDTYPE_AXIS, axis.axis)
            self.assertEqual('1', axis.units)
            self.assertEqual([type_descriptions[x - 1] for x in example], axis.getValue())
            self.assertEqual(len(example), len(axis))


if __name__ == '__main__':
    unittest.main()
