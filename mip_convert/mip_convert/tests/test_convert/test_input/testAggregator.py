# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
import unittest

from mip_convert.load.pp.aggregator import AggregatorError, Aggregator
from functools import reduce


class TestAggregator(unittest.TestCase):
    RECORD_AXES = [list(range(2)), list(range(3))]
    """The axes attached to each record (in practice these would be lon and lat)"""

    def testAxisList(self):
        for shape in ((), (1,), (10,), (1, 1), (4, 5), (1, 1, 1), (4, 9, 2)):
            example = self.example_factory(shape)
            aggregator = example.get_aggregator()

            self.assertEqual(example.axis_list(), aggregator.axis_list())

    def testCoordinateValueError(self):
        for shape in ((3, 2), (4, 3, 2)):
            example = self.example_factory(shape)

            for records in example.make_corrupt():
                self.assertRaises(AggregatorError, example.get_aggregator_for, records)

    def example_factory(self, shape):
        clazz = {0: Example0D, 1: Example1D, 2: Example2D, 3: Example3D}
        return clazz[len(shape)](shape, self.RECORD_AXES)


class RecordDecorator(object):
    def __init__(self, raw_record, axis_list):
        self._raw_record = raw_record
        self._axis_list = axis_list

    def __getitem__(self, key):
        return self._raw_record[key]

    def axis_list(self):
        return self._axis_list


class ExtractorScalar(object):
    """An example axis extractor - when the record is just a scalar"""

    def equals(self, x, y):
        return x._raw_record == y._raw_record

    def getAxis(self, records):
        return [record._raw_record for record in records]


class Extractor(object):
    """An example axis extractor - when the record is an indexable sequence"""

    def __init__(self, idim):
        self._idim = idim

    def equals(self, x, y):
        return x[self._idim] == y[self._idim]

    def getAxis(self, records):
        return [record[self._idim] for record in records]


class AbstractExample(object):
    """Tests with different record types and different number of dimensions
    need different set up, eg of the records and the axis extractors.  These
    are put in Example classes.  The AbstractExample gives a base class for common
    functionality.
    """

    def __init__(self, shape, record_axis_list):
        self._shape = shape
        self._record_axis_list = record_axis_list

    def _make_record(self, raw_record):
        return RecordDecorator(raw_record, self._record_axis_list)

    def _axis(self, idim):
        return list(range(self._shape[idim]))

    def axis_list(self):
        result = [self._axis(jdim) for jdim in range(len(self._shape))]
        result.extend(self._record_axis_list)
        return result

    def range_elements(self):
        from operator import mul
        return list(range(reduce(mul, self._shape, 1)))

    def get_aggregator_for(self, records):
        return Aggregator(records, self.make_extractors())

    def get_aggregator(self):
        return self.get_aggregator_for(self.make_records())


class Example0D(AbstractExample):
    def make_records(self):
        return [self._make_record(0)]

    def make_extractors(self):
        return []


class Example1D(AbstractExample):

    def make_records(self):
        return [self._make_record(raw_record) for raw_record in self._axis(0)]

    def make_extractors(self):
        return (ExtractorScalar(),)


class Example2D(AbstractExample):

    def make_records(self):
        records = list()
        for j0 in range(self._shape[0]):
            for j1 in range(self._shape[1]):
                records.append(self._make_record((j0, j1)))
        return records

    def make_extractors(self):
        return (Extractor(0), Extractor(1))

    def make_corrupt(self):
        corrupt = list()
        for (i0, i1) in ((0, 1), (1, 0)):
            corruptions = self._corrupt_records(i0, i1)
            corrupt.extend(corruptions)
        return corrupt

    def _corrupt_records(self, i0, i1):
        corruptions = list()
        for i in self.range_elements():
            records = self.make_records()
            records[i] = (records[i][0] + i0, records[i][1] + i1)
            corruptions.append(records)
        return corruptions


class Example3D(AbstractExample):

    def make_records(self):
        records = list()
        for j0 in range(self._shape[0]):
            for j1 in range(self._shape[1]):
                for j2 in range(self._shape[2]):
                    records.append(self._make_record((j0, j1, j2)))
        return records

    def make_extractors(self):
        return (Extractor(0), Extractor(1), Extractor(2))

    def make_corrupt(self):
        # this is not as extensive testing as the 2D case
        corrupt = list()
        for i in self.range_elements():
            records = self.make_records()
            records[i] = (records[i][0] + 1, records[i][1], records[i][2])
            corrupt.append(records)
        return corrupt


if __name__ == '__main__':
    unittest.main()
