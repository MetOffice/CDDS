# (C) British Crown Copyright 2009-2025, Met Office.
# Please see LICENSE.md for license details.
"""
A common problem is to extract the multi-dimensional axis
information from a list of pp headers.  This module provides support code
for dealing with the multi-dimensional aspect of the list of pp headers.

This support code provides the capability to extract sub lists of headers
where these sub lists contain pp headers for a single axis dimension. These
sub lists can be passed to other class which can extract the axis values.

This implementation tests that the pp headers are ordered 'sensibly',
and fails if they are not.  Where sensibly means that where there are
multi-dimensions the order of variation of the pp headers along each
axis of the mult-dimensions is consistent.  In other words the headers
can be simply reshaped without re-ordering.  For example:

   header(time=1, level=1)
   header(time=1, level=2)
         :
   header(time=1, level=nlevs)
   header(time=2, level=1)
   header(time=2, level=2)
         :
   header(time=2, level=nlevs)
         :
   header(time=ntimes, level=1)
   header(time=ntimes, level=2)
         :
   header(time=ntimes, level=nlevs)

The extraction is performed by a nested object structure.  This reflects
the nested nature of the indexing. In the above example the nesting is
level within time. So the nested data structures look something like:

  NestedIndex(time, NestedIndex(level, InnermostIndex)))

(see documentation for individual classes)
"""


class AggregatorError(Exception):
    """
    Error if the pp meta data records do not appear to
    be from a multi-dimensional array.
    """
    pass


class AbstractIndex(object):
    """
    Abstract class used to document the interface of an Index
    """
    records = None
    """
    records is the list of meta-data (pp header) records that is being indexed
    """

    block_len = None
    """
    The total number of contiguous records needed in the record list to define the axis values for this axis.
    """

    number_blocks = None
    """
    The number of times the contiguous records defining the an axis is repeated in the record list.
    """

    def axis_list(self):
        """
        @return: a list of axis for the list of records.
        """
        raise NotImplementedError('abstract class')


class InnermostIndex(AbstractIndex):
    """
    An InnermostIndex terminates the nested index data structure.
    It adds information to a pp header to allow the indexing algorithm
    to work.
    """

    block_len = 1

    def __init__(self, records):
        """
        @param records: list of meta-data records to extract variable
        """
        self.records = records
        self.number_blocks = len(records)

    def axis_list(self):
        return self.records[0].axis_list()


class NestedIndex(AbstractIndex):

    def __init__(self, inner_index, axis_extractor):
        """
        @param inner_index: the nested index at the level below this one.
        @param axis_extractor: object that deals with the axis type dependent
                               aspects of the headers.  It should be able to
                               extact the axis from a list of meta-data records
                               and also determine whether two records have the same
                               coordinate value along the axis.
        """
        self._inner_index = inner_index
        self._axis_extractor = axis_extractor

        self.len = self._len

        self._check_for_errors()

    def axis_list(self):
        result = [self._axis()]
        result.extend(self._inner_index.axis_list())
        return result

    @property
    def records(self):
        return self._inner_index.records

    @property
    def block_len(self):
        return self.len * self._stride

    @property
    def number_blocks(self):
        return self._inner_index.number_blocks // self.len

    def _axis(self):
        return self._axis_extractor.getAxis((self._get_records()))

    def _get_records(self):
        return [self._ref_record(j) for j in range(self.len)]

    @property
    def _max_len(self):
        return self._inner_index.number_blocks

    @property
    def _stride(self):
        return self._inner_index.block_len

    @property
    def _len(self):
        result = self._max_len
        for index in range(1, self._max_len):
            if self._axis_extractor.equals(self._ref_record(0), self._ref_record(index)):
                result = index
                break
        return result

    def _ref_record(self, index):
        return self.records[index * self._stride]

    def _check_len(self):
        if self.number_blocks * self.len != self._inner_index.number_blocks:
            raise AggregatorError()

    def _check_for_errors(self):
        self._check_len()
        self._check_coordinate_values_constant()

    def _check_coordinate_values_constant(self):
        for index in range(self.len):
            for block in range(0, self.number_blocks):
                self._check_block_for_index(block, index)

    def _check_block_for_index(self, block, index):
        for stride in range(self._stride):
            if not self._axis_extractor.equals(self._record_at(index, 0, 0), self._record_at(index, block, stride)):
                raise AggregatorError('inconsistent values on coordinate')

    def _record_at(self, index, iblock, i):
        return self.records[iblock * self.block_len + index * self._stride + i]


class Aggregator(object):
    # not sure this class will live long

    def __init__(self, records, axis_extractors):
        """
        @param records: list of meta-data records to extract axes from
        @param axis_extractors: list of axis_extractors: one for each axis
        """
        self._records = records
        self._axis_extractors = axis_extractors
        self._make_dim_lens()

    @property
    def _number_dimensions(self):
        return len(self._axis_extractors)

    def _make_dim_lens(self):
        dimension = InnermostIndex(self._records)
        for number_dimension in range(self._number_dimensions):
            dimension = NestedIndex(dimension, self._axis_extractors[self._number_dimensions - 1 - number_dimension])
        self._dim = dimension

    def axis_list(self):
        return self._dim.axis_list()
