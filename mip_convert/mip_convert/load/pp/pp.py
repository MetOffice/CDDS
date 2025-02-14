# (C) British Crown Copyright 2009-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Classes to deal with pp input.
"""
from mip_convert.common import ObjectWithLogger
from mip_convert.load.pp.pp_axis import DatedPpHeader
from mip_convert.load.pp.pp_fixed import PpFixedFile
from mip_convert.load.pp.stash_code import from_msi


class PpError(Exception):
    """
    Exception used when there is a problem related to reading the pp files
    """
    pass


class PpSelectableFile(ObjectWithLogger):
    """
    A pp file that supports selection based on pp header elements
    """

    def __init__(self, timestep, pp_file, var_generator, opener):
        """
        @param timestep: the timestep of the model for this file factory
        @param pp_file: a pp file to read from (support list of headers, read of extras, read of data)
        @param var_generatord: an object capable of generating multi-dimensional variables from a list of pp fields
        @param opener: an object capable of opening a file of this type
        """
        super(self.__class__, self).__init__()
        self.raw_pp_file = pp_file
        self._var_generator = var_generator
        self.timestep = timestep
        self.opener = opener

    @property
    def pathname(self):
        """
        return the path name that the variable is selected from
        """
        return self.raw_pp_file.pathname

    def read_selection(self, stash, **kwargs):
        """
        returns a variable for stash code and request
        """
        return self._selector(PpMatch(from_msi(stash), **kwargs)).getVariable()

    def _chck_selection(self, matcher, indexes):
        if len(indexes) == 0:
            raise PpError("cannot match %s in file %s" % (matcher, self.raw_pp_file.pathname))

    @property
    def _headers(self):
        return self.raw_pp_file.headers

    def _get_index(self, matcher):
        return matcher.get_index(self._headers)

    def _selector(self, matcher):
        indexes = self._get_index(matcher)
        self._chck_selection(matcher, indexes)  # move to ppmatch?
        return PpSelectedVariable(self.raw_pp_file, indexes, self._var_generator)

    def close(self):
        self.logger.debug('closing')
        self.raw_pp_file.close()


class PpSelectedVariable(object):
    """
    Instances of PpSelectedVariable are responsible for reading a set
    of pp headers extra data and data from a pp file and passing those
    onto a variable generator that can build a multi-dimensional
    variable from the data.  The pp fields read in are determined by
    the index of the pp field in a file.

    This avoids the potentially expensive read of data when it may not
    be necessary.  (though I am not so convinced that this is the slow
    operation).
    """

    def __init__(self, raw_pp_file, indexes, variable_generator):
        """
        @param raw_pp_file: the pp file to read from
        @param indexes: list of pp field (header+data+extradata) in the
                        raw_pp_file from which variable will be made
        @param fields_factory: object needed to generate the pp domains
        """
        self._raw_pp_file = raw_pp_file
        self._indexes = indexes
        self._var_gen = variable_generator

    def getVariable(self):
        """
        returns a variable with meta-data for this selection
        """
        return self._var_gen.makeVariable(self._getHeaders(), self._getExtraDataVectors(), self._getData())

    def _getHeaders(self):
        headers = []
        for index in self._indexes:
            headers.append(self._raw_pp_file.headers[index])
        return headers

    def _getExtraDataVectors(self):
        extra_data = []
        for index in self._get_indicies():
            extra_data.append(self._raw_pp_file.getExtraDataVectors(index))
        return extra_data

    def _getData(self):
        data = []
        for i in self._get_indicies():
            data.append(self._raw_pp_file.loadField(i).baseData)
            self._raw_pp_file.unloadField(i)
        return data

    def _get_indicies(self):
        result = []
        for index in self._indexes:
            result.append(index + 1)  # pp_file is indexed  + 1
        return result


class PpFileFactory(object):
    """
    Class to act as the route to interact with files.

    There are two main services offered - the ability to open files,
    and the ability to read a single variable from a file.

    If you are going to read many variables from the same file then use open.
    For files that are going to be read just once then use the readVar function.

    It could be two classes to reflect the two services, but as neither
    is particulary big leave as one for now.  Refactor later if necessary.
    """
    _SELECTABLE = PpSelectableFile
    """
    _SELECTABLE is the class to use to generate the file types
    """

    def __init__(self, timestep, pp_module, variable_generator):
        """
        @param timestep: the timestep of the model for this file factory
        @param pp_module: the module providing the basic pp reading capability
        @type pp_module: an object with an openpp method
        @param fields_factory: an object which can extract multi dimensional axis informat from a list of pp headers
        @type fields_factory: L{mip_convert.load.pp.pp_variable.PpFieldsFactory}
        """
        self.pp_module = pp_module
        self._var_generator = variable_generator
        self._timestep = timestep

    def openFile(self, filename):
        """
        open a file for reading

        @param filename: the path of the file to be opened
        @type filename: string
        @return: pp file that supports selection of variables based on pp header elements
        @rtype: L{PpSelectableFile}
        """
        return self.openFiles([filename])

    def openFiles(self, filenames):
        """
        open a set of files as a composite for reading

        this was added as a way of getting at some ancillary fields spread
        across multiple files.  Consider a refactor with openFile if you
        find yourself using it too often.
        """
        fixed_files = [PpFixedFile(self.pp_module.openpp(filename, failOnError=True)) for filename in filenames]
        return self._SELECTABLE(self._timestep, PpComposite(fixed_files), self._var_generator, self)

    def readVar(self, filename, stashcode):
        """
        read a variable from the filename

        this is a utility method for use when only one variable will
        be read from a file

        @param filename: the full path of the file to be read from
        @type filename: string
        @param stashcode: the stashcode of the variable to be read
        @type stashcode: string in msi format
        """
        selectable = self.openFile(filename)
        result = selectable.read_selection(stashcode)
        selectable.close()
        return result


class PpComposite(object):
    """
    Treat multiple pp files as a single file.

    Partial implementation only - good enough for the ancillary case it
    was designed to solve.

    I suggest it should be replaced with an implementation based on pph files,
    and the generalised meta-split indexes
    """
    # TODO: think about 1 offset - this info is spread a bit at the moment
    _IMPLEMENTATION = 'currently a cut down implementation on just 2 files'

    def __init__(self, pp_files):
        if len(pp_files) > 2:
            raise NotImplementedError(self._IMPLEMENTATION)
        self._files = pp_files

    @property
    def headers(self):
        result = list()
        for current in self._files:
            result.extend(current.headers)
        return result

    @property
    def pathname(self):
        return ','.join([afile.pathname for afile in self._files])

    def getExtraDataVectors(self, field_number):
        input_file = self._file_for_field(field_number)
        index = self._index_in_file(field_number)
        return self._files[input_file].getExtraDataVectors(index)

    def loadField(self, field_number):
        input_file = self._file_for_field(field_number)
        index = self._index_in_file(field_number)
        return self._files[input_file].loadField(index)

    def unloadField(self, field_number):
        input_file = self._file_for_field(field_number)
        index = self._index_in_file(field_number)
        self._files[input_file].unloadField(index)

    def close(self):
        for current in self._files:
            current.close()

    def _file_for_field(self, field_number):
        return 0 if field_number - 1 < len(self._files[0].headers) else 1

    def _index_in_file(self, field_number):
        if self._file_for_field(field_number) == 0:
            result = field_number
        else:
            result = field_number - len(self._files[0].headers)
        return result


class PpElementComparitor(object):
    """
    Abstract Class for matchers on individual pp header elements
    """

    def __init__(self, att, value):
        """
        @param att: name of the pp header element to compare against
        @param value: the value to match
        """
        self._att = att
        self._tomatch = value

    def compare(self, dated_header):
        """
        return True of the value of the header element matches the value
        of this ElementComparitor
        """
        return self._compare(self.attr_header_element(dated_header))

    def attr_header_element(self, header):
        return getattr(header, self._att)


class ListComparitor(PpElementComparitor):
    """
    Compares the header value to a list of possible values
    """

    def _compare(self, value):
        self._check_only_one_match(value)
        return value in self._tomatch

    def _check_only_one_match(self, value):
        if self._tomatch.count(value) > 1:
            raise PpError('%s matches more than one value')


class ScalarComparitor(PpElementComparitor):
    """
    Compares the header value to required value
    """

    def _compare(self, value):
        return value == self._tomatch


class FloatForCompare(object):
    """
    Simple float wrapper to enable floating point comparisons, within a tolerance
    """

    def __init__(self, value, tol):
        self._value = value
        self._tol = tol

    def __eq__(self, other):
        return abs(self._value - other) < self._tol


class PpMatch(object):
    """
    Instances of PpMatch select pp headers from a sequence of pp headers.
    """

    _SCALAR_ATT = ('lbtim', 'lbproc', 'lbuser5', 'delta_time_in_days')
    _FLOAT_LIST_ATT = ('blev',)

    def __init__(self, stashcode, blev_tol=1.e-06, first_only=False, **kwargs):
        """
        match pp header against pp header elements
        @param stashcode: the stashcode to select on
        @type stashcode: L{mip_convert.load.pp.stash_code.StashCode}
        @param blev_tol: tolerance to use when blev_checking.
        @param **kwargs: key-value pair where the key is a pp header
                         element to select on, and value the value to select.
                         allowed keys are taken from L{keywords}.

        examples:
        >>> from mip_convert.load.pp.stash_code import StashCode
        >>> match = PpMatch(StashCode(1, 1, 1), lbtim = 322)
        """
        self._first = first_only
        self._match_atts = stashcode.asDict()
        self._tol = blev_tol
        self._ini_match(kwargs)
        self._make_cmps()

    def __str__(self):
        return '%s' % self._match_atts

    @classmethod
    def matchables(cls):
        """
        return tuple of possible header elements to match
        """
        return cls._SCALAR_ATT + cls._FLOAT_LIST_ATT

    @classmethod
    def keywords(cls):
        """
        return tuple of possible keyword parameters
        """
        return cls.matchables() + ('blev_tol', 'first_only')

    def _match(self, header):
        """
        returns True if the header matches the clauses of this matcher
        """
        result = True
        for acmp in self._cmps:
            result = result and acmp.compare(DatedPpHeader(header))
        return result

    def get_index(self, headers):
        self._done_matching = False
        indexes = list()
        for index, header in enumerate(headers):
            if self._done_matching:
                break
            if self._match(header):
                indexes.append(index)
                self._set_has_matched()
        return indexes

    def _ini_match(self, kwargs):
        """
        initialise the attributes to be matched
        """
        for att, value in list(kwargs.items()):
            if att not in self.matchables():
                raise PpError('select on "%s" not supported' % att)
            self._match_atts[att] = value

    def _make_cmps(self):
        self._cmps = []
        for att, value in list(self._match_atts.items()):
            self._cmps.append(self._element_comparitor(att, value))

    def _set_has_matched(self):
        if self._first:
            self._done_matching = True

    def _element_comparitor(self, att, value):
        if att in self._FLOAT_LIST_ATT:
            mvalue = [FloatForCompare(tomatch, self._tol) for tomatch in value]
            return ListComparitor(att, mvalue)

        return ScalarComparitor(att, value)


class QueryOrographyProvider(object):
    """
    Hybrid height axes need an orography field to fully specify the
    CF meta-data.  In the HadGEM2 model the orography is on different grids
    because of the numerical scheme.  Instances of this class can be
    used to choose the orography for the correct grid from a list of
    orography fields,
    """

    units = 'm'
    """
    the units orography is in in a pp file
    """

    def __init__(self, orography_reader):
        self._orog = orography_reader.getOrographyList()

    def _match_orog(self, axis_x, axis_y):
        result = None
        for orog in self._orog:
            if orog.getAxis('X') == axis_x and orog.getAxis('Y') == axis_y:
                result = orog
        return result

    def getOrography(self, axis_x, axis_y):
        """
        return the orography field on the required axes

        @param axis_x: longitude axis to look for orography on
        @param axis_y: latitude axis to look for orography on
        @raises PpError: if orography not available on the required axes.
        """
        result = self._match_orog(axis_x, axis_y)
        if result is None:
            raise PpError('orography not found for axes')  # better message?
        return result


class OrographyReader(object):
    """
    This class provides the capability to read in all the orography fields
    from a pp file and return them as a list of variables for use elsewhere
    (e.g. in L{QueryOrographyProvider})
    """
    _MSG_FORMAT = 'OrographyReader: skipped field with lbuser4 %s'
    _SELECTED_VARIABLE = PpSelectedVariable
    _OROGRAPHY_LBUSER4 = 33
    _OROGRAPHY_LBUSER7 = 1

    def __init__(self, pp_file, variable_generator, messanger):
        """
        return an OrographyReader

        @param pp_file: the pp file to find orography in
        @param variable_generator: object to pass pp fields to
                                   to generate multi-dimensional variables
        @param messanger: object to receive messages.
        """
        self._pp_file = pp_file
        self._variable_generator = variable_generator
        self._messanger = messanger

    def getOrographyList(self):
        """
        return the list of orography fields

        @raises PpError: if there are no orography fields
        """
        indexes = self._getOrographyFieldIndexes()
        self._check_orography_found(indexes)
        return self._getOrographyFields(indexes)

    def _isOrography(self, header):
        return header.lbuser4 == self._OROGRAPHY_LBUSER4 and header.lbuser7 == self._OROGRAPHY_LBUSER7

    def _getOrographyFieldIndexes(self):
        indexes = list()
        for (index, header) in enumerate(self._pp_file.headers):
            if self._isOrography(header):
                indexes.append(index)
            else:
                self._messanger.write(self._MSG_FORMAT % header.lbuser4)
        return indexes

    def _getOrographyFields(self, indexes):
        result = list()
        for index in indexes:
            result.append(self._getOrographyAt(index))
        return result

    def _getOrographyAt(self, index):
        selected = self._SELECTED_VARIABLE(self._pp_file, [index], self._variable_generator)
        return selected.getVariable()

    def _check_orography_found(self, result):
        if len(result) == 0:
            raise PpError('no orgraphy in headers')
