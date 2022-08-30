# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest

from header_util import BaseHeader
from mip_convert.common import SITE_TYPE
from mip_convert.model_date import CdDate
from mip_convert.load.pp.pp_axis import (
    DatedPpHeader, PpAxisError, PpAxisFactory, LANDTYPE_AXIS)
from mip_convert.load.pp.pp_variable import PpFieldsFactory, VariableGenerator

# TODO: these tests can be refactored to make them look more similar - and
# then remove the duplication


class DummyTAxis(object):

    def __init__(self, headers):
        self.headers = headers
        self.axis = 'T'

    def __eq__(self, other):
        result = True
        for actual, other in zip(self.headers, other.headers):
            result = result and actual.lbmon == other.lbmon
        return result

    def __ne__(self, other):
        return not self == other


class DummyZAxis(object):

    def __init__(self, headers, extras):
        self.headers = headers
        self.extras = extras
        self.axis = 'Z'

    def __eq__(self, other):
        result = True
        result = result and self.extras == other.extras
        for my_header, other_header in zip(self.headers, other.headers):
            result = result and my_header.blev == other_header.blev
        return result

    def __ne__(self, other):
        return not self == other


class DummyAxis(object):
    def __init__(self, axis, headers):
        self.axis = axis
        self.headers = headers

    def __len__(self):
        return len(self.headers)


class DummyExtraAxis(object):
    def __init__(self, axis, headers, extras):
        self.axis = axis
        self.headers = headers
        self.extras = extras

    def __len__(self):
        return len(self.headers)


class TestTszPpDomain(unittest.TestCase):
    _base_time = CdDate(1859, 12, 1, 0, 0, 0, '360_day')

    def testMoreTimes(self):
        lbnpt = 1
        lbrow = 2
        self.datas = [[1, 2]]
        headers = [BaseHeader(lbnpt=lbnpt, lbrow=lbrow, lbcode=11320)]
        extras = [dict(list(zip(list(range(3, 3 + 6)), [[i] * lbnpt for i in range(6)])))]
        domain = self._getDomain(headers, extras, self)

        self.assertEqual(('T', SITE_TYPE, 'Z'), domain.getAxisOrder())
        self.assertEqual([50070.0, 50085.0], domain.getAxis('T').getValue())
        self.assertEqual(self.s_axis, domain.getAxis(SITE_TYPE))
        self.assertEqual(self.z_axis, domain.getAxis('Z'))
        self.assertEqual((2, 1, 1), domain.shape())

    def getSAxis(self, header, extra):
        self.s_axis = DummyExtraAxis(SITE_TYPE, [header], [extra])
        return self.s_axis

    def getZAxis(self, headers, extras):
        self.z_axis = DummyExtraAxis('Z', headers, extras)
        return self.z_axis

    def _getDomain(self, headers, extras, factory):
        factory = PpFieldsFactory(factory)
        return self._vargen(headers, extras, factory)

    def _vargen(self, headers, extras, factory):
        generator = VariableGenerator(factory)
        return generator.makeVariable(headers, extras, self.datas).domain


class AbstractDomainTest(unittest.TestCase):
    def domainFactory(self):
        return PpFieldsFactory(PpAxisFactory(None))

    def makeExtras(self):
        return [{}] * len(self.makeHeaders())

    def vargen(self):
        headers = self.makeHeaders()
        extras = self.makeExtras()
        generator = VariableGenerator(self.domainFactory())
        return generator.makeVariable(headers, extras, self.makeData())


class TestExtractedTzyxDomain(AbstractDomainTest):
    def makeData(self):
        data = list()
        for month in self.mons:
            for blev in self.blevs:
                data.append(self._record_data(month * blev))
        return data

    def _record_data(self, base_value):  # limited use
        return [[base_value for values in range(self.lbnpt * self.lbrow)]]

    def expectdata(self):
        data = list()
        source = self.makeData()
        for month in self.mons:
            data_time = list()
            for blev in self.expect_blevs:
                data_time.append(self._record_data(month * blev))
            data.append(data_time)
        return data

    def makeHeaders(self):
        headers = list()
        for month in self.mons:
            for blev in self.blevs:
                header = BaseHeader(blev=blev,
                                    lbvc=8,
                                    lbuser4=1,
                                    lbmon=month,
                                    lbmond=month + 1,
                                    lbnpt=self.lbnpt,
                                    lbrow=self.lbrow,
                                    lbcode=self.lbcode,
                                    bplat=self.bplat,
                                    bplon=self.bplon)
                headers.append(header)
        return headers

    def setUp(self):
        super(TestExtractedTzyxDomain, self).setUp()
        self.lbnpt = 1
        self.lbrow = 1
        self.lbcode = 1
        self.bplat = 90.
        self.bplon = 0.
        self.mons = (2, 3)
        self.blevs = [900.0,
                      740.0,
                      620.0,
                      500.0,
                      375.0,
                      245.0,
                      115.0]

    def testRotatedGrid(self):
        self.expect_blevs = self.blevs
        self.lbcode = 101
        self.bplat = 45.
        self.blon = 45.

        variable = self.vargen()

        self.assertOnMetaData(variable)
        self.assertOnAxes(variable)
        self.assertOnData(variable)
        self.assertTrue(variable.is_rotated)
        self.assertEqual([self.bplat, self.bplon], variable.domain.pole_coords())

    def testUnRotatedRegionalGrid(self):
        self.expect_blevs = self.blevs
        self.lbcode = 1
        self.bplat = 90.
        self.bplon = 180.
        self.lbhem = 3

        variable = self.vargen()

        self.assertOnMetaData(variable)
        self.assertOnAxes(variable)
        self.assertOnData(variable)
        self.assertFalse(variable.is_rotated)
        #      self.assertEquals([self.bplat, self.bplon], var.domain.pole_coords())

    def testData(self):
        self.expect_blevs = self.blevs
        variable = self.vargen()

        self.assertOnMetaData(variable)
        self.assertOnAxes(variable)
        self.assertOnData(variable)
        self.assertEqual([90, 0], variable.domain.pole_coords())

    def testLevelOrder(self):
        self._swap_levels()
        self._sort_for_expected_levels()

        variable = self.vargen()

        self.assertOnMetaData(variable)
        self.assertOnAxes(variable)
        self.assertOnData(variable)

    def assertOnMetaData(self, var):
        self.assertEqual(self.makeHeaders()[0].bmdi, var.missing_value)

    def assertOnAxes(self, var):
        self.assertEqual(('T', 'Z', 'Y', 'X'), var.getAxisOrder())
        self.assertEqual([50115.0, 50145.0], var.getAxisList()[0].getValue())  # improve
        self.assertEqual(self.expect_blevs, var.getAxisList()[1].getValue())
        self.assertEqual([0.0], var.getAxisList()[2].getValue())
        self.assertEqual([0.0], var.getAxisList()[3].getValue())
        self.assertEqual(4, len(var.getAxisList()))
        self.assertEqual((2, 7, 1, 1), var.getValue().shape)

    def assertOnData(self, var):
        self.assertEqual(self.expectdata(), var.getValue().tolist())

    def _swap_levels(self):
        tmp_level = self.blevs[1]
        self.blevs[1] = self.blevs[2]
        self.blevs[2] = tmp_level

    def _sort_for_expected_levels(self):
        import copy
        self.expect_blevs = copy.copy(self.blevs)
        self.expect_blevs.sort()
        self.expect_blevs.reverse()  # its a pressure coordinate


class TestExtractedYxDomain(AbstractDomainTest):
    def expectdata(self):
        return [[0.0, 1.0, 2.0, 3.0], [4.0, 5.0, 6.0, 7.0], [8.0, 9.0, 10.0, 11.0]]

    def makeData(self):
        return [list(range(self.lbpnt * self.lbrow))]

    def makeHeaders(self):
        return [BaseHeader(lbuser4=33, lbpnt=self.lbpnt, lbrow=self.lbrow)]

    def testData(self):
        self.lbpnt = 4
        self.lbrow = 3

        var = self.vargen()
        self.assertEqual(('Y', 'X'), var.getAxisOrder())
        self.assertEqual(2, len(var.getAxisList()))
        self.assertEqual((3, 4), var.getValue().shape)
        self.assertEqual(self.expectdata(), var.getValue().tolist())


class TestLandCoverExtractedDomain(AbstractDomainTest):
    def makeData(self):
        return [[1]] * len(self.makeHeaders())

    def makeHeaders(self):
        headers = list()
        for month in self.mons:
            for pseudo in self.pseudos:
                header = BaseHeader(lbuser4=19013, lbuser5=pseudo, lbmon=month, lbmond=month + 1, lbnpt=1, lbrow=1)
                headers.append(header)
        return headers

    def testAxisOrder(self):
        self.mons = (2, 3)
        self.pseudos = list(range(1, 10))

        variable = self.vargen()

        self.assertEqual(('T', LANDTYPE_AXIS, 'Y', 'X'), variable.getAxisOrder())
        self.assertEqual((len(self.mons), len(self.pseudos), 1, 1), variable.getValue().shape)
        self.assertEqual(4, len(variable.getAxisList()))
        self.assertEqual(len(self.mons), len(variable.getAxis('T')))


class TestIsccpDomain(AbstractDomainTest):
    def makeData(self):
        return [[1]] * len(self.makeHeaders())

    def makeHeaders(self):
        headers = list()
        for month in self.mons:
            for pseudo in self.pseudos:
                for blev in self.blevs:
                    header = BaseHeader(lbuser4=2337,
                                        lbuser5=pseudo,
                                        lbvc=8,
                                        blev=blev,
                                        lbmon=month,
                                        lbmond=month + 1,
                                        lbnpt=1,
                                        lbrow=1)
                    headers.append(header)
        return headers

    def testAxisOrder(self):
        self.mons = (2, 3)
        self.pseudos = list(range(1, 8))
        self.blevs = [900.0, 740.0, 620.0, 500.0, 375.0, 245.0, 115.0]

        variable = self.vargen()

        self.assertEqual(('T', 'tau', 'Z', 'Y', 'X'), variable.getAxisOrder())
        self.assertEqual((len(self.mons), 7, 7, 1, 1), variable.getValue().shape)
        self.assertEqual(5, len(variable.getAxisList()))
        self.assertEqual(7, len(variable.getAxis('tau')))


class TestClcalipsoDomain(AbstractDomainTest):
    def makeData(self):
        return [[1]] * len(self.makeHeaders())

    def makeHeaders(self):
        headers = list()
        for month in self.mons:
            for blev in self.blevs:
                header = BaseHeader(lbuser4=self.lbuser4,
                                    lbvc=1,
                                    blev=blev,
                                    lbmon=month,
                                    lbmond=month + 1,
                                    lbnpt=1,
                                    lbrow=1)
                headers.append(header)
        return headers

    def testAxisOrder(self):
        for lbuser4 in (2371, 2325):
            self.lbuser4 = lbuser4
            self.single_stash()

    def single_stash(self):
        self.mons = (2, 3)
        self.blevs = self._make_float_list(
            '240. 720. 1200. 1680. 2160. 2640. 3120. 3600. 4080. 4560. 5040. '
            '5520. 6000. 6480. 6960. 7440. 7920. 8400. 8880. 9360. 9840. '
            '10320. 10800. 11280. 11760. 12240. 12720. 13200. 13680. 14160. '
            '14640. 15120. 15600. 16080. 16560. 17040. 17520. 18000. 18480. '
            '18960.')

        bounds = self._make_float_list(
            '0. 480. 480. 960. 960. 1440. 1440. 1920. 1920. 2400. 2400. 2880. '
            '2880. 3360. 3360. 3840. 3840. 4320. 4320. 4800. 4800. 5280. '
            '5280. 5760. 5760. 6240. 6240. 6720. 6720. 7200. 7200. 7680. '
            '7680. 8160. 8160. 8640. 8640. 9120. 9120. 9600. 9600. 10080. '
            '10080. 10560. 10560. 11040. 11040. 11520. 11520. 12000. 12000. '
            '12480. 12480. 12960. 12960. 13440. 13440. 13920. 13920. 14400. '
            '14400. 14880. 14880. 15360. 15360. 15840. 15840. 16320. 16320. '
            '16800. 16800. 17280. 17280. 17760. 17760. 18240. 18240. 18720. '
            '18720. 19200.')
        expect_bounds = [[upper, lower] for upper, lower in zip(bounds[0::2], bounds[1::2])]
        variable = self.vargen()
        self.assertEqual(('T', 'Z', 'Y', 'X'), variable.getAxisOrder())
        self.assertEqual(expect_bounds, variable.getAxis('Z').getBounds())

    def _make_float_list(self, y_string):
        return list(map(float, y_string.split(' ')))


class TestParasolRefl(unittest.TestCase):

    def testHasSza(self):
        headers = [BaseHeader(lbuser4=2348, blev=1e-10), BaseHeader(lbuser4=2348, blev=-20)]
        extras = [{}] * len(headers)
        data = [list(range(headers[0].lbnpt * headers[0].lbrow))] * len(headers)
        generator = VariableGenerator(self.domainFactory())
        variable = generator.makeVariable(headers, extras, data)
        self.assertEqual(('T', 'sza5', 'Y', 'X'), variable.getAxisOrder())
        self.assertEqual([-20, 0], variable.getAxis('sza5').getValue())

    def domainFactory(self):
        return PpFieldsFactory(PpAxisFactory(None))


if __name__ == '__main__':
    unittest.main()
