# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest

from mip_convert.load.pp.pp_fixed import PpFixedFile, HeaderFixer

from header_util import BaseHeader


class TestFixVerticalLevels(unittest.TestCase):

    def loadField(self, pos):
        """stub for pp file"""
        self.loaded = pos
        return self.data

    def unloadField(self, pos):
        """stub for pp file"""
        self.unloaded = pos

    def getExtraDataVectors(self, pos):
        """stub for pp file"""
        self.extra = pos
        return self.extra_data

    def close(self):
        """stub for pp file"""
        self.closed = True

    def _make_header(self, lbuser4, lbuser7, lbvc, blev):
        """return a header using values of lbuser4, lbuser7 lbvc, blev"""
        return BaseHeader(lbuser4=lbuser4, lbuser7=lbuser7,
                          lbvc=lbvc, blev=blev)

    def assertOnHeader(self, header, expect):
        """asserts that headers are equal"""
        for attribute in ('lbuser4', 'lbuser7', 'lbvc', 'blev'):
            message = 'stash %s attr %s expect %s got %s'
            self.assertEqual(getattr(expect, attribute), getattr(header, attribute),
                             message % (header.lbuser4, attribute, getattr(expect, attribute),
                                        getattr(header, attribute)))

    def _add_unchanged_header(self, example):
        """add a header that should not be changed to the
        test list
        """
        self._add_header_with_result(example, example)

    def _add_header_with_result(self, input, output):
        # TODO: the adding of headers could be rationalised
        # to reflect the fact that sub model and stash should
        # never change
        self.headers.append(self._make_header(*input))
        self.expected_headers.append(self._make_header(*output))

    def _add_unchanged_examples(self):
        examples = [
            (1, 1, 1, -1.),
            (3237, 1, 1, 2.5),
            (3237, 2, 1, -1.),
            (3237, 1, 2, -1.),
        ]
        for example in examples:
            self._add_unchanged_header(example)

    def _add_near_surface_temperature(self):
        self._add_header_with_result((3236, 1, 1, -1.), (3236, 1, 1, 1.5))

    def _add_near_surface_winds(self):
        for lbuser4 in (3225, 3226, 3227):
            self._add_header_with_result((lbuser4, 1, 1, -1.), (lbuser4, 1, 1, 10.))

    def _add_soil_moisture(self):
        examples = [(1., 0.05), (2., 0.225)]
        for (inner_level, outer_level) in examples:
            self._add_header_with_result((8223, 1, 6, inner_level), (8223, 1, 2, outer_level))

    def _add_humidity(self):
        for lbuser4 in (3237, 3245):
            self._add_header_with_result((lbuser4, 1, 1, -1.), (lbuser4, 1, 1, 1.5))

    def _add_convection_indicators(self):
        for lbuser4 in (3309, 3310):
            self._add_header_with_result((lbuser4, 1, 129, 0.), (lbuser4, 1, 0, -1))

    def _add_precip_related(self):
        self._add_header_with_result((5216, 1, 129, 0.), (5216, 1, 0, -1))
        for lbuser4 in (3297, 8233):
            self._add_header_with_result((lbuser4, 1, 275, -1.0), (lbuser4, 1, 0, -1))

    def _add_hybrid_height(self):
        self._add_header_with_result((2261, 1, 9, 1.0), (2261, 1, 65, 1.0))

    def _get_file_headers(self):
        return self.pp_file.headers

    def setUp(self):
        self.closed = False
        self.headers = []
        self.expected_headers = []
        self.pp_file = PpFixedFile(self)

    def testHeaders(self):
        self._add_unchanged_examples()
        self._add_near_surface_temperature()
        self._add_soil_moisture()
        self._add_humidity()
        self._add_near_surface_winds()
        self._add_convection_indicators()
        self._add_hybrid_height()
        self._add_precip_related()

        self.pp_file = PpFixedFile(self)  # have to make file after headers

        headers = self._get_file_headers()
        for (expected, header) in zip(self.expected_headers, headers):
            self.assertOnHeader(header, expected)

    def testRhoLike(self):
        self._add_header_with_result((2417, 1, 65, 9.998206), (2417, 1, 65, 0))
        self.pp_file = PpFixedFile(self)  # have to make file after headers

        headers = self._get_file_headers()
        for (expected, header) in zip(self.expected_headers, headers):
            self.assertOnHeader(header, expected)

    def testFieldLoads(self):
        self.data = list(range(9, 2))
        for pos in range(10):
            data = self.pp_file.loadField(pos)
            self.assertEqual(pos, self.loaded)
            self.assertEqual(self.data, data)

            self.pp_file.unloadField(pos)
            self.assertEqual(pos, self.unloaded)

    def testExtraData(self):
        self.extra_data = list(range(5, 3))
        extra = self.pp_file.getExtraDataVectors(1)
        self.assertEqual(1, self.extra)
        self.assertEqual(self.extra_data, extra)

    def testClose(self):
        self.pp_file.close()
        self.assertTrue(self.closed)
        # headers freed to avoid growth of memory
        self.assertEqual([], self.pp_file.headers)

    def testPathName(self):
        self.filename = 'apath'
        self.assertEqual('apath', self.pp_file.pathname)


class TestVcBoundsChange(unittest.TestCase):
    # TODO:it may be better to inline this test with others

    def testExample(self):
        lbvcout = 2
        blevout = 0.225
        brlev = 0.35
        brsvd1 = 0.1
        outatts = {
            'lbvc': lbvcout,
            'blev': blevout,
            'brlev': brlev,
            'brsvd1': brsvd1
        }

        fixer = HeaderFixer(outatts)

        header = BaseHeader()
        header.lbvc = 6
        header.blev = 2.
        header.brsvd1 = 0.
        out = fixer.fix(header)
        self.assertEqual(out.lbvc, lbvcout)
        self.assertEqual(out.blev, blevout)
        self.assertEqual(out.brlev, brlev)
        self.assertEqual(out.brsvd1, brsvd1)

    def testOceanDms(self):
        header_in = BaseHeader(lbuser4=30253, lbuser7=2, lbvc=2, blev=5.0, brlev=-1073741824.0, brsvd1=0.)
        header_out = BaseHeader(lbuser4=30253, lbuser7=2, lbvc=2, blev=5.0, brlev=10., brsvd1=0.)
        fixer = HeaderFixer({'brlev': 10})
        self.assertEqual(header_out.brlev, fixer.fix(header_in).brlev)


if __name__ == '__main__':
    unittest.main()
