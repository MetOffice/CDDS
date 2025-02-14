# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
import unittest

from cdds.common import cmp
from header_util import BaseHeader
from mip_convert.load.pp.pp_axis import (
    BlevExtractor, BoundedExpectExtractor, DatedPpHeader, ExtractorException,
    LandExtractor, PpAxisError, PpAxisFactory, PpLatLonDecorator,
    PpTimeSeriesDecorator, TimeExtractor, ISCCP_PRESSURE_AXIS)
from mip_convert.model_date import CdDate


class DecoratedHeader(object):
    def __init__(self, header, extra):
        self.header = header
        self._dated_header = DatedPpHeader(header)
        self.extra = extra

    def __eq__(self, other):
        return self._dated_header == other._dated_header

    def __ne__(self, other):
        return self._dated_header != other._dated_header

    def __lt__(self, other):
        return self._dated_header < other._dated_header

    def __gt__(self, other):
        return self._dated_header > other._dated_header

    def __le__(self, other):
        return self._dated_header <= other._dated_header

    def __ge__(self, other):
        return self._dated_header >= other._dated_header

    def set_axis_units(self, axis):
        pass


class TestExpectedBoundedExtractor(unittest.TestCase):

    def setUp(self):
        self.expected = [900.0, 740.0, 620.0, 500.0, 375.0, 245.0, 115.0]
        axis = ISCCP_PRESSURE_AXIS
        self.extractor = BoundedExpectExtractor('blev', self.expected, axis, -1)

    def testEquals(self):
        for blevs in ((1, 1), (2, 2), (1, 2)):
            headers = self._make_headers(blevs)
            self.assertEqual(blevs[0] == blevs[1], self.extractor.equals(headers[0], headers[1]))

    def testAxis(self):
        headers = self._make_headers(self.expected)
        axis = self.extractor.getAxis(headers)
        self.assertEqual(ISCCP_PRESSURE_AXIS, axis)

    def testNotInExpectedError(self):
        for blevs in (list(range(3)), list(range(7)), list(range(1, 8))):
            headers = self._make_headers(blevs)
            self.assertRaises(ExtractorException, self.extractor.getAxis, headers)

    def _make_headers(self, blevs):
        headers = list()
        for blev in blevs:
            headers.append(DecoratedHeader(BaseHeader(blev=blev), {}))
        return headers


class TestTimeExtractor(unittest.TestCase):
    # TODO inline with axis test
    def setUp(self):
        self._time_extractor = TimeExtractor()

    def testEquals(self):
        records = self._make_records(2)
        self.assertTrue(self._time_extractor.equals(records[0], records[0]))
        self.assertFalse(self._time_extractor.equals(records[0], records[1]))

    def _make_records(self, length):
        return [DecoratedHeader(BaseHeader(lbyr=1859 + j), {}) for j in range(length)]


class TestLandExtractor(unittest.TestCase):
    def setUp(self):
        self._extractor = LandExtractor(self)

    def testAxis(self):
        records = self._make_records(9)
        self.assertEqual([record.header for record in records], self._extractor.getAxis(records))

    def testEquals(self):
        records = self._make_records(2)
        self.assertTrue(self._extractor.equals(records[0], records[0]))
        self.assertFalse(self._extractor.equals(records[0], records[1]))

    def getPseudoAxis(self, headers):
        return headers

    def _make_records(self, length):
        return [DecoratedHeader(BaseHeader(lbuser5=j), {}) for j in range(length)]


class TestBlevExtractor(unittest.TestCase):

    def testAxis(self):
        extractor = BlevExtractor(self)
        length = 10
        records = [DecoratedHeader(BaseHeader(blev=j), {}) for j in range(length)]
        self.assertEqual(
            ([record.header for record in records], [record.extra for record in records]),
            extractor.getAxis(records))

    def testEquals(self):
        extractor = BlevExtractor(self)
        length = 2
        records = [DecoratedHeader(BaseHeader(blev=j), {}) for j in range(length)]
        self.assertTrue(extractor.equals(records[0], records[0]))
        self.assertFalse(extractor.equals(records[0], records[1]))

    def getZAxis(self, headers, extras):
        return (headers, extras)


class TestPpTimeSeriesDecorator(unittest.TestCase):
    def makeDecorator(self, headers, extras):
        return PpTimeSeriesDecorator([DatedPpHeader(header) for header in headers], extras, None)

    def testInsufficientExtraError(self):
        headers = self.makeHeaders(1)
        extras = [{}]
        self.assertRaises(PpAxisError, self.makeDecorator, headers, extras)

    def testExtraCodeError(self):
        headers = self.makeHeaders(1)
        extras = [dict(list(zip(list(range(9, 9 + 6)), list(range(6)))))]
        self.assertRaises(PpAxisError, self.makeDecorator, headers, extras)

    def testExtraLbpntError(self):
        headers = self.makeHeaders(2)
        extras = [dict(list(zip(list(range(3, 3 + 6)), [[i] for i in range(6)])))]
        self.assertRaises(PpAxisError, self.makeDecorator, headers, extras)

    def makeHeaders(self, lbpnt):
        return [BaseHeader(lbnpt=lbpnt, lbcode=11320)]


class TestPpLatLonDecorator(unittest.TestCase):
    AXIS_VAL_INCRS = (-1, 0, 1)

    def testDelegateAttributes(self):
        lbuser5 = 18
        pp_meta = self._decorate(lbuser5=lbuser5)
        self.assertEqual(lbuser5, pp_meta.lbuser5)

    # make axis factory forwarding more obvious
    def testSimpleExtract(self):
        lbnpt = 3
        bdx = 0.5
        bzx = 1

        pp_meta = self._decorate(lbnpt=3, bdx=0.5, bzx=1)
        [axisy, axisx] = pp_meta.axis_list()
        self.assertEqual('X', axisx.axis)
        self.assertEqual([bzx + (ix + 1) * bdx for ix in range(lbnpt)], axisx.getValue())
        self.assertEqual('Y', axisy.axis)  # get tests in here from testPpAxis

    def testNExternal(self):
        """
        static fields should only have internal pp dimensions
        """
        for static_stash in (30, 33):
            pp_meta = self._decorate(lbuser4=static_stash)
            self.assertEqual(0, pp_meta.nexternal_axis())

    def testDepthCmp(self):
        self._level_tests(2, 1)

    def testPressureCmp(self):
        self._level_tests(8, -1)

    def testLandCmp(self):
        pp_meta_ref = self._decorate(lbuser4=19013, lbuser5=2)
        pp_meta = self._land_type_from_ref(pp_meta_ref)
        self._assert_cmp_lbuser5(pp_meta_ref, pp_meta)

    def testInstantCmp(self):
        pp_meta_ref = self._decorate(lbuser4=1, lbtim=12, lbproc=0, lbyr=1990, lbmon=1, lbdat=2)
        pp_meta = self._times_from_ref(pp_meta_ref)
        self._assert_cmp_times(pp_meta_ref, pp_meta)

    def testMeanCmp(self):
        pp_meta_ref = self._decorate(lbuser4=1, lbtim=22, lbproc=128, lbyr=1990, lbmon=1, lbdat=2)
        pp_meta = self._times_from_ref(pp_meta_ref)
        self._assert_cmp_times(pp_meta_ref, pp_meta)

    def _level_tests(self, lbvc, direction_factor):
        blev_ref = 2
        pp_meta_ref = self._decorate(lbuser4=1, lbvc=lbvc, blev=blev_ref)
        pp_meta = self._levels_from_ref(pp_meta_ref)
        self._assert_cmp_blev(pp_meta_ref, pp_meta, direction_factor)

    def _levels_from_ref(self, pp_meta_ref):
        pp_meta = list()
        for inc in self.AXIS_VAL_INCRS:
            header = self._decorate(lbuser4=pp_meta_ref.lbuser4, lbvc=pp_meta_ref.lbvc, blev=pp_meta_ref.blev + inc)
            pp_meta.append(header)
        return pp_meta

    def _land_type_from_ref(self, pp_meta_ref):
        pp_meta = list()
        for inc in self.AXIS_VAL_INCRS:
            pp_meta.append(self._decorate(lbuser4=pp_meta_ref.lbuser4, lbuser5=pp_meta_ref.lbuser5 + inc))
        return pp_meta

    def _times_from_ref(self, pp_meta_ref):
        pp_meta = list()
        for inc in self.AXIS_VAL_INCRS:
            pp_meta.append(self._decorate(lbuser4=pp_meta_ref.lbuser4,
                                          lbtim=pp_meta_ref.lbtim,
                                          lbproc=pp_meta_ref.lbproc,
                                          lbyr=pp_meta_ref.lbyr,
                                          lbmon=pp_meta_ref.lbmon,
                                          lbdat=pp_meta_ref.lbdat + inc)
                           )
        return pp_meta

    def _assert_cmp_blev(self, pp_meta_ref, pp_meta, direction_factor):
        # not sure this is the best place to test?
        self.assertEqual(2, pp_meta_ref.nexternal_axis())
        for i, lev_inc in enumerate(self.AXIS_VAL_INCRS):
            expected = direction_factor * cmp(pp_meta_ref.blev, pp_meta_ref.blev + lev_inc)
            self.assertEqual(expected, pp_meta_ref.cmp_on_axis(pp_meta[i], 1))

    def _assert_cmp_lbuser5(self, pp_meta_ref, pp_meta):
        # not sure this is the best place to test?
        self.assertEqual(2, pp_meta_ref.nexternal_axis())
        for i, lev_inc in enumerate(self.AXIS_VAL_INCRS):
            expected = cmp(pp_meta_ref.lbuser5, pp_meta_ref.lbuser5 + lev_inc)
            self.assertEqual(expected, pp_meta_ref.cmp_on_axis(pp_meta[i], 1))

    def _assert_cmp_times(self, pp_meta_ref, pp_meta):
        # not sure this is the best place to test?
        self.assertEqual(2, pp_meta_ref.nexternal_axis())
        for i, inc in enumerate(self.AXIS_VAL_INCRS):
            self.assertEqual(cmp(pp_meta_ref.lbdat, pp_meta_ref.lbdat + inc), pp_meta_ref.cmp_on_axis(pp_meta[i], 0))

    def _decorate(self, **kwargs):
        header = BaseHeader(**kwargs)
        return self._make_decorator(header, {})

    def _make_decorator(self, header, extra):
        return PpLatLonDecorator(DatedPpHeader(header), extra, PpAxisFactory(None))


if __name__ == '__main__':
    unittest.main()
