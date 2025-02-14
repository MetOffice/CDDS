# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest

from header_util import BaseHeader

from mip_convert.load.pp.stash_code import from_header
from mip_convert.load.pp.pp import PpMatch
from mip_convert.load.pp.pp import PpError


class TestPpMatch(unittest.TestCase):

    def assertTrueFalseExamples(self, matcher):
        self.assertTrue(matcher._match(self.header1))
        self.assertFalse(matcher._match(self.header2))

    def setUp(self):
        lbuser4 = 2
        lbuser7 = 1
        self.header1 = BaseHeader(lbuser4=lbuser4, lbuser7=lbuser7, lbtim=122)
        self.header2 = BaseHeader(lbuser4=lbuser4, lbuser7=lbuser7, lbtim=122)
        self.stash = from_header(self.header1)

    def incrAttrToDifferent(self, attribute):
        """
        increment the value in attribute attr, simply to make it
        a different value during match
        """
        setattr(self.header2, attribute, getattr(self.header2, attribute) + 1)

    def makeMatcher(self, attribute):
        self.incrAttrToDifferent(attribute)
        if attribute == 'lbuser4':
            kwargs = {}
        else:
            kwargs = {attribute: getattr(self.header1, attribute)}
        return PpMatch(self.stash, **kwargs)

    def testMatches(self):
        for attribute in ('lbuser4', 'lbproc', 'lbuser5'):
            matcher = self.makeMatcher(attribute)
            self.assertTrueFalseExamples(matcher)

    def testMatchFloatListWithTol(self):
        blevs = [0., 1.]
        match = PpMatch(self.stash, blev=blevs, blev_tol=1.e-5)

        good_levs = blevs + [blev + 1.e-6 for blev in blevs] + [blev - 1.e-6 for blev in blevs]
        for blev in good_levs:
            self.header1.blev = blev
            self.assertTrue(match._match(self.header1))

        bad_levs = [blevs[-1] + 1, blevs[-1] + 1.e-4, blevs[-1] - 1e-4]
        for blev in bad_levs:
            self.header1.blev = blev
            self.assertFalse(match._match(self.header1))

    def testMatchasString(self):
        match = PpMatch(self.stash, lbproc=128)
        expected = self.stash.asDict()
        expected.update({'lbproc': 128})
        self.assertEquals("%s" % expected, "%s" % match)

    def testErrorOnMultiMatch(self):
        blevs = [0., 0.1]
        match = PpMatch(self.stash, blev=blevs, blev_tol=blevs[1] - blevs[0])
        self.header1.blev = (blevs[0] + blevs[1]) * 0.5
        self.assertRaises(PpError, match.get_index, [self.header1])

    def testErrorOnUnsupportedSearch(self):
        # use try/except idiom rather than assertRaises because
        # of keyword argument.  If you know a better idiom please use.
        try:
            PpMatch(self.stash, lbuser3=10)
            self.fail()
        except PpError:
            self.assertTrue(True)


class TestTenDayMeanFilter(unittest.TestCase):

    def testOneDayMean(self):
        header = self._time_mean_header(1, 1, 2, 1)
        match = PpMatch(from_header(header), delta_time_in_days=1)
        self.assertTrue(match._match(header))

    def testTenDayMean(self):
        lbmon = 1
        for lbdat in (1, 11, 21):
            header = self._ten_day_mean_header(lbdat, lbmon)
            match = PpMatch(from_header(header), delta_time_in_days=1)
            self.assertFalse(match._match(header))

    def _ten_day_mean_header(self, lbdat, lbmon):
        return self._time_mean_header(
            lbdat=lbdat, lbmon=lbmon,
            lbdatd=(10 + lbdat) % 30,
            lbmond=(lbmon + (10 + lbdat) / 30)
        )

    def _time_mean_header(self, lbdat, lbmon, lbdatd, lbmond):
        return BaseHeader(lbproc=128, lbtim=622,
                          lbdat=lbdat,
                          lbmon=lbmon,
                          lbdatd=lbdatd,
                          lbmond=lbmond)


class TestFirstFieldFilter(unittest.TestCase):

    def testMatchWithFirstFieldFilter(self):
        lbuser4 = 2
        lbuser7 = 1
        headers = [BaseHeader(lbuser4=lbuser4, lbuser7=lbuser7), BaseHeader(lbuser4=lbuser4, lbuser7=lbuser7)]
        stash = from_header(headers[0])
        match = PpMatch(stash, first_only=True)
        self.assertEqual([0], match.get_index(headers))


if __name__ == '__main__':
    unittest.main()
