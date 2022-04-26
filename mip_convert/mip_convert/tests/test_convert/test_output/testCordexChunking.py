# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Cordex has a specification of how long each output netcdf file should
cover, and where the time boundaries should lie.

Test cases to develop a solution to this.
"""
from unittest.mock import MagicMock
import numpy as np
import unittest

from mip_convert.load.pp.pp_axis import InstantAxis
from mip_convert.model_date import based_date
from mip_convert.save.cmor.cmor_outputter import (
    CmorSaverFactory, EndOfMultipleYears, MipTableVariable, SeasonalDecade)
from mip_convert.variable import Variable, CoordinateDomain, UNROTATED_POLE


class TestCordexVarChunking(unittest.TestCase):
    units = 'm'
    stash_history = 'm01s01i001'
    history = 'history'
    positive = 'up'

    OUTPUTS_PER_FILE = -10

    def setUp(self):
        self.written = list()
        self.closed = False
        self.setUpWriter()

    def setUpWriter(self):
        outputter_factory = CmorSaverFactory(MagicMock(), None)
        request = self.setUpRequest()
        self.writer = outputter_factory.getSaver(request.table, request.entry, outputs_per_file=None)
        self.writer._write_var = self._write_var  # patch
        self.writer._close_file = self._close_file

    def setUpRequest(self):
        request = MagicMock()
        request.table = 'CORDEX_mon'
        request.entry = 'tas'
        request.boundary_finder.return_value = EndOfMultipleYears(abs(self.OUTPUTS_PER_FILE))
        return request

    def write(self, var):
        self.writer.write_var(var)

    def _close_file(self):
        self.closed = True

    def _write_var(self, var):
        self.written.append(var)

    def variable2(self, times):
        domain = CoordinateDomain([times], UNROTATED_POLE)
        variable = Variable(domain, np.ma.zeros(len(times)))
        variable.meta_data(self)
        return variable

    def _based_date(self, yy, mm, dd, hh, minu):
        return based_date(yy, mm, dd, hh, minu, 122)

    def test_first_year_of_decade(self):
        variable = self.variable2(self.time([(1861, 12), (1862, 1)]))
        self.write(variable)
        self.assertEqual(self.time([(1861, 12), (1862, 1)]), self.written[0].time())
        self.assertFalse(self.closed)

    def time(self, year_months):
        return InstantAxis([self.date(year, month) for year, month in year_months])

    def date(self, year, month):
        return self._based_date(year, month, 15, 0, 0)


class _dummyDomain(object):

    def getCmorDomain(self, table, entry):
        return None


class TestMipRequestVariable(unittest.TestCase):

    def testIsMulti(self):
        request = MipTableVariable('CMIP5_Amon', 'tas', _dummyDomain())
        self.assertFalse(request.use_cordex_chunking())

    def testIsCordexMonthly(self):
        for (frequency, expect) in [('mon', 10), ('3h', 1), ('6h', 1), ('day', 5)]:
            request = MipTableVariable('CORDEX_%s' % frequency, 'tas', _dummyDomain())
            self.assertTrue(request.use_cordex_chunking())
            self.assertEqual(expect, request.boundary_finder()._value)

    def testIsCordexSeasonal(self):
        request = MipTableVariable('CORDEX_sem', 'tas', _dummyDomain())
        self.assertTrue(isinstance(request.boundary_finder(), SeasonalDecade))

    def testIsCordexfx(self):
        request = MipTableVariable('CORDEX_fx', 'orog', _dummyDomain())
        self.assertFalse(request.use_cordex_chunking())


if __name__ == '__main__':
    unittest.main()
