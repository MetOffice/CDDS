# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.md for license details.

import unittest
from header_util import BaseHeader

from mip_convert.model_date import CdDate
from mip_convert.load.pp.pp_variable import TimeSeriesHeaders, VariableGenerator
from mip_convert.load.pp.pp_variable import PpFieldsFactory
from mip_convert.load.pp.pp_variable import PpVariableError
from mip_convert.load.pp.pp_axis import PpTimeSeriesDecorator


class DummyDomain(object):
    def shape(self):
        return (1,)


class DummyFields(object):
    def domain(self):
        return DummyDomain()

    def datas(self):
        [list(range(1))]


class TestPpTimeSeries(unittest.TestCase):
    _base_time = CdDate(1859, 12, 1, 0, 0, 0, '360_day')

    def testNonContiguousError(self):
        self.assertRaises(PpVariableError,
                          PpFieldsFactory(self).getfields,
                          [self.makeHeader(1, 2, 1), self.makeHeader(2, 3, 1), self.makeHeader(4, 5, 1)],
                          None,
                          None)

    def testGetFieldsConcatsTimeSeries(self):
        dimension_length = 2
        for start, end in ((1, 2), (1, 4),):
            fields = PpFieldsFactory(self).getfields(
                self.makeHeaderSeries(start, end, dimension_length),
                self.makeExtraSeries(start, end),
                self.makeDataSeries(start, end, dimension_length)
            )
            self.assertEqual(1, len(fields))
            self.assertTrue(isinstance(fields.metadatas()[0], PpTimeSeriesDecorator))  # yuk
            self.assertEqual(
                [self.makeHeader(start, end, (end - start) * dimension_length)],
                [fields.metadatas()[0]._dated_header]
            )
            self.assertEqual(self.extraForRecord(), [fields.metadatas()[0].extra])
            self.assertEqual([self.dataForRecord(0, (end - start) * dimension_length)], fields.datas())

    def makeDataSeries(self, start, end, dlen):
        if (end - start) == 1:
            return [self.dataForRecord(0, dlen)]
        else:
            return [self.dataForRecord(position, dlen) for position in range(end - start)]

    def dataForRecord(self, position, dlen):
        return list(range(position * dlen, (position + 1) * dlen))

    def makeExtraSeries(self, start, end):
        return self.extraForRecord() * (end - start)

    def extraForRecord(self):
        lbnpt = 4  # this should really be header.lbnpt
        return [dict(list(zip(list(range(3, 3 + 6)), [[index] * lbnpt for index in range(6)])))]

    def makeHeaderSeries(self, start, end, lbrow):
        result = []
        for position in range(start, end):
            result.append(self.makeHeader(position, position + 1, lbrow))
        return result

    def makeHeader(self, lbdat, lbdatd, lbrow):
        result = BaseHeader(lbcode=31320)
        result.lbdat = lbdat
        result.lbdatd = lbdatd
        result.lbmon = 1
        result.lbmond = result.lbmon
        result.lbrow = lbrow
        return result


if __name__ == '__main__':
    unittest.main()
