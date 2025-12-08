# (C) British Crown Copyright 2011-2025, Met Office.
# Please see LICENSE.md for license details.
"""Module containing classes related to extracting multidimensional variables
from list of pp fields.
"""
import copy
import numpy

from mip_convert.common import cmp_to_key
from mip_convert.load.pp.aggregator import Aggregator
from mip_convert.load.pp.pp_axis import DatedPpHeader

from mip_convert.load.pp.pp_axis import PpLatLonDecorator
from mip_convert.load.pp.pp_axis import PpTimeSeriesDecorator
from mip_convert.load.pp.pp_axis import _isTimeSeries

from mip_convert.load.pp.stash_code import from_header

from mip_convert.variable import variable
from mip_convert.variable import CoordinateDomain


class PpVariableError(Exception):
    """Exception used when there is a problem making a variable from a set of pp fields"""
    pass


class ExpandableTimeSeriesHeader(object):
    """Very simple implementation of a timeseries header with dates"""

    def __init__(self, dated_header):
        self._dated = dated_header

    @property
    def header(self):  # hmm...
        return self._dated._header

    def expand_to(self, other, nrecords):
        """expand the end time an number of times based on the end time in other
        and the number of records.
        """
        self._set_date2(other)
        self._set_number_rows(nrecords)

    def is_contiguous(self, other):
        return self._dated.date2() == other._dated.date1()

    def _set_date2(self, other):
        self._dated.set_date2(other._dated)

    def _set_number_rows(self, nrecords):
        self._dated.set_lbrow(self._dated.lbrow * nrecords)


class TimeSeriesHeaders(object):
    """Class responsible for coping with the fact that sometimes timeseries
    data is spread over more than one record
    """

    def __init__(self, dated_headers, extras, datas):
        self._dated = [ExpandableTimeSeriesHeader(dheader) for dheader in dated_headers]
        self._extra = extras
        self._data = datas
        self._raiseWhenNotContiguous()

    def getHeader(self):
        return self._joinHeaders()

    def getExtra(self):
        return self._extra[0:1]

    def getData(self):
        if self._nrecords() > 1:
            result = [self._joinData(self._data)]
        else:
            result = self._data
        return result

    def _nrecords(self):
        return len(self._dated)

    def _joinData(self, data):
        result = []
        for index in range(len(self._dated)):
            result.extend(data[index])
        return result

    def _joinHeaders(self):
        dated_header = ExpandableTimeSeriesHeader(copy.copy(self._dated[0]._dated))
        if self._nrecords() > 1:
            dated_header.expand_to(self._dated[-1], self._nrecords())
        return [dated_header.header]

    def _raiseWhenNotContiguous(self):
        for dated1, dated2 in zip(self._dated[0:-1], self._dated[1:]):
            if not dated1.is_contiguous(dated2):
                raise PpVariableError('non-contiguous time series headers')


class VariableGenerator(object):
    """Class responsible for making multi-dimensional variables from pp headers,
    extra-data, and data.

    The headers, extradata, and data are provided by clients of instances
    of this class.  This class assumes these are all for the SAME
    multi-dimensional variable and builds the multi-dimensional variable
    domain (space-time-axis information)  from the pp information provided.
    """

    VAR_ATTS = ['lbtim',
                'lbcode',
                'lbhem',
                'lbrow',
                'lbnpt',
                'lbrel',  # not sure?
                'lbfc',
                'lbcfc',
                'lbproc',
                'lbvc',
                'lbrvc',
                'lbexp',
                'lbproj',
                'lbtyp',
                'lbsrce',  # not sure?
                'lbuser1',
                'lbuser4',
                #               'lbuser5', #maychange
                'lbuser7',
                'bdatum',
                'bplat',
                'bplon',
                'bgor',
                'bzy',
                'bdy',
                'bzx',
                'bdx',
                'bmdi',  # maychange
                'bmks'  # maychange
                ]
    """VAR_ATTS is a list of attributes that should be the same for all headers in a variable.
    This excludes time and level locations, and none 'logical/geophysical' header attributes.
    Some things are question marked at the moment
    """

    _TYPE_MAP = {1: numpy.float32}
    """map linking pp types to numpy types."""
    # NOTE: above does not imply you can simply add new types.
    #      You'll need to test what works.

    def __init__(self, fields_factory):
        """return a VariableGenerator that will use the fields_factory

        @param fields_factory: object that will generate pp fields from headers, extra data and datas
        @type fields_factory: L{mip_convert.load.pp.pp_variable.PpFieldsFactory}
        """
        self.fields_factory = fields_factory

    def makeVariable(self, headers, extras, data):
        """return a multi-dimensional variable from the headers, extras, and data

        The parameters types are those corresponding to return types
        for methods from the pypp package.

        @param headers: list of pp headers for the variable
        @param extras: the extra data corresponding to the headers
        @param data: the data records corresponding to the headers
        @raises PpVariableError: when there is an inconsistency in the input parameters
                                 e.g. if they are different lengths, or the headers look
                                 like they are from more than one STASH code.
        """
        self._check(headers, extras, data)
        fields = self.fields_factory.getfields(headers, extras, data)
        return variable(fields.domain(), fields.datas(), headers[0].bmdi, self._TYPE_MAP[headers[0].lbuser1])

    def _check(self, headers, extras, datas):
        self._check_len_against(headers, datas, 'datas')
        self._check_len_against(headers, extras, 'extras')
        self._check_extras(extras)
        self._check_row_len(datas)
        self._check_single_variable(headers)

    def _check_len_against(self, headers, values, name):
        if len(headers) != len(values):
            raise PpVariableError('len headers "%s" and len %s "%s" not equal' % (len(headers), name, len(values)))

    def _check_extras(self, extras):
        for extra in extras:
            if extra != extras[0]:
                raise PpVariableError('extras not equal')

    def _check_row_len(self, data):
        for row in data[1:]:
            if len(data[0]) != len(row):
                raise PpVariableError('data rows not consistent length')

    def _check_single_variable(self, headers):
        self._check_reference_header(headers)
        for header in headers[1:]:
            self._check_against_reference(headers[0], header)

    def _check_against_reference(self, reference, header):
        for att in self.VAR_ATTS:
            self._check_atttribute(reference, header, att)

    def _check_reference_header(self, headers):
        if headers[0].lbuser1 not in self._TYPE_MAP:
            raise PpVariableError('pp data type %d not supported' % headers[0].lbuser1)

    def _check_atttribute(self, reference_header, header, attribute):
        reference_value = getattr(reference_header, attribute)
        value = getattr(header, attribute)
        if reference_value != value:
            message = "header att mismatch: attribute '%s' expected '%s' got '%s'" % (attribute, reference_value, value)
            raise PpVariableError(message)

    def _stash(self, header):
        return from_header(header).asMsi()


class PpFieldsFactory(object):
    """The PpFieldsFactory returns a pp field list"""

    def __init__(self, axis_factory):
        """@param axis_factory: the axis factory for the domains"""
        self.axis_factory = axis_factory

    def getfields(self, headers, extras, data):
        if _isTimeSeries(headers[0]):
            fields = self._time_series_field(headers, extras, data)
        else:
            fields = self._lat_lon_fields(headers, extras, data)
        return fields

    def _dated_headers(self, headers):
        return [DatedPpHeader(header) for header in headers]

    def _time_series_field(self, headers, extras, data):
        time_series = TimeSeriesHeaders(self._dated_headers(headers), extras, data)
        return self._fields(
            PpTimeSeriesDecorator, time_series.getHeader(), time_series.getExtra(), time_series.getData()
        )

    def _lat_lon_fields(self, headers, extras, data):
        return self._fields(PpLatLonDecorator, headers, extras, data)

    def _fields(self, decorator, headers, extras, data):
        """@param headers: pp headers
        @param extras: pp extra data
        @param data: data records
        """
        metas = self._make_records(decorator, self._dated_headers(headers), extras)
        return SortedPpList(metas, data)

    def _make_records(self, decorator, headers, extras):
        return [decorator(header, extra, self.axis_factory) for (header, extra) in zip(headers, extras)]


class PpExternalAxisCmp(object):
    """Comparison of all the values of the external axes of a set of pp fields"""

    def __init__(self, ncmps):
        """@param ncmps: the number of external axes to compare values for"""
        self._ncmps = ncmps

    def __call__(self, ppfield1, ppfield2):
        for index in range(self._ncmps):
            result = ppfield1.cmp_on_axis(ppfield2, index)
            if result != 0:
                break

        return result


class SortedPpList(object):
    """A list of PP fields"""

    def __init__(self, metadatas, datas):
        self._fields = [PpField(header, data) for (header, data) in zip(metadatas, datas)]
        self._fields.sort(key=cmp_to_key(PpExternalAxisCmp(self._nexternal_axes())))
        self._metadata = [field._metadata for field in self._fields]
        self._data = [field._data for field in self._fields]
        self._domain = None  # don't create this yet - test cases are easier

    def __len__(self):
        return len(self._fields)

    def metadatas(self):
        return self._metadata

    def datas(self):
        return self._data

    def domain(self):
        """return the domain for this list of pp fields
        the domain is basically a list of axes
        """
        if self._domain is None:
            self._domain = self._make_domain()
        return self._domain

    def _make_domain(self):
        aggregator = Aggregator(self.metadatas(), self.metadatas()[0].extractors())
        return CoordinateDomain(aggregator.axis_list(), self._pole())

    def _nexternal_axes(self):
        return self._fields[0].nexternal_axis()

    def _pole(self):
        return self.metadatas()[0].pole()


class PpField(object):
    """A combined pp field - meta data and data"""

    def __init__(self, metadata, data):
        self._metadata = metadata
        self._data = data

    def __getattr__(self, attr):
        return getattr(self._metadata, attr)
