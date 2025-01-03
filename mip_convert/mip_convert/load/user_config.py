# (C) British Crown Copyright 2009-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
Requests for MIP variables are made in a set of 'request config
files'.  There is one request config file per stream. The request
files have the naming convention '<stream>_variables'.

Each file is made up of a number of sections, one section for each requested
variable.  Each section specifies things like the MIP table and MIP variable
entry to output to, along with information on the mapping to use to produce
the variable.  Optionally the section can also contiain pp-element selections
to specify which pp fields in the file should be used to build the variable.

This module contains classes needed to read the config files.

During the run of mip_convert a number of variables are read
from the data source and written to output.  These variables are
determined by user requests.  This module contains classes related
to the object representation of user requests.
"""
import regex as re

from mip_convert.plugins.plugins import PluginStore
from mip_convert.load.model_output_config import AbstractDataSourceUser
from mip_convert.common import ObjectWithLogger
from mip_convert.load.pp.pp import PpMatch
from mip_convert.process import quality_control as qc
import mip_convert.save.cmor.cmor_lite


class RequestError(Exception):
    """
    Exception to deal with the any errors associated with user requests
    """
    pass


class CompositeRequestProvider(object):
    """
    The requests may come from multiple request providers.
    This class acts as a composite of these providers, giving a uniform
    interface to all request providers.
    """

    def __init__(self):
        self.providers = list()

    def add(self, provider):
        """
        add a provider to the composite
        """
        self.providers.append(provider)

    def var_seq(self):
        """
        returns a sequence of CMOR requested variables
        """
        if len(self.providers) == 0:
            raise RequestError('No providers added to composite')

        request_variables = list()
        for provider in self.providers:
            request_variables.extend(provider.var_seq())
        return request_variables


class PpRequestVariable(ObjectWithLogger):
    """
    An object representation of a request for a mip variable from
    a pp input file.

    In a sense this is the key bit of logic in the code: each request
    is responsible for coordinating the reading of data from the source for
    a requested variable, and then passing the variable onto the outputter.
    """
    ATTS = PpMatch.keywords()
    """
    supported key words to select on
    """

    def __init__(self, table, entry, stream, processor):
        super(PpRequestVariable, self).__init__()
        self.table = table
        self.entry = entry
        self.stream = stream
        self.output = None
        self.outputs_per_file = None
        self._processor = processor
        self._do_bounds_check = None   # updated in the process() method
        self._bounds_checker = None    # ditto
        self.min_fixed = 0             # ditto
        self.max_fixed = 0             # ditto

    def output_name(self):
        """
        returns the name use in outputing the request
        """
        return '%s_%s' % (self.table, self.entry)

    def read_and_write(self, input_file):
        self.output.write_var(self._process(input_file))

    def _process(self, input_file):
        variable = self._processor.getVariable(self, input_file)
        return self._bounds_processed(variable)

    def match_keys(self):
        kwargs = {}
        for attr in self.ATTS:
            if hasattr(self, attr):
                kwargs[attr] = getattr(self, attr)
        return kwargs

    def _bounds_processed(self, variable):
        if self._do_bounds_check is None:
            self._set_bounds_checker(variable.getValue())

        if self._do_bounds_check:
            min_fixed, max_fixed = self._run_bounds_checker(variable.getValue())
            # If some fixes were applied then update overall totals and log a warning message.
            if (min_fixed + max_fixed) > 0:
                self.min_fixed += min_fixed
                self.max_fixed += max_fixed

                message = '%s_%s: min values fixed = %d, max values fixed = %d'
                self.logger.warning(message % (self.entry, self.table.split('_')[-1], min_fixed, max_fixed))

        variable.history = self.get_bounds_comment()
        return variable

    def _set_bounds_checker(self, array):
        """
        If required, create a bounds checker object for this request variable.
        """
        self._do_bounds_check = False

        # Read any min/max bounds properties specified for this variable in the xxx_variables file.
        kwargs = {}
        kwargs['fill_value'] = array.get_fill_value()
        for key in ('valid_min', 'valid_max', 'tol_min', 'tol_max'):
            if key in vars(self):
                kwargs[key] = getattr(self, key)

        # Actions need to be converted from string properties to one of the constants defined in
        # the qc module. default action is to pass values through to CMOR
        default_action = qc.PASS_VALUE
        for key in ('tol_min_action', 'tol_max_action', 'oob_action'):
            if key in vars(self):
                action = getattr(self, key)
                kwargs[key] = getattr(qc, action.upper(), default_action)
                self._do_bounds_check = True
            else:
                kwargs[key] = default_action

        # Create a BoundsChecker instance if at least one bounds-checking action was specified.
        if self._do_bounds_check:
            if PluginStore.instance().has_plugin_loaded():
                plugin = PluginStore.instance().get_plugin()
                self._bounds_checker = plugin.bounds_checker(
                    fill_value=kwargs.get('fill_value', qc.UM_MDI),
                    valid_min=kwargs.get('valid_min'),
                    valid_max=kwargs.get('valid_max'),
                    tol_min=kwargs.get('tol_min'),
                    tol_max=kwargs.get('tol_max'),
                    tol_min_action=kwargs.get('tol_min_action'),
                    tol_max_action=kwargs.get('tol_max_action'),
                    oob_action=kwargs.get('oob_action')
                )
            else:
                self._bounds_checker = qc.MaskedArrayBoundsChecker(fill_value=kwargs.get('fill_value', qc.UM_MDI),
                                                                   valid_min=kwargs.get('valid_min'),
                                                                   valid_max=kwargs.get('valid_max'),
                                                                   tol_min=kwargs.get('tol_min'),
                                                                   tol_max=kwargs.get('tol_max'),
                                                                   tol_min_action=kwargs.get('tol_min_action'),
                                                                   tol_max_action=kwargs.get('tol_max_action'),
                                                                   oob_action=kwargs.get('oob_action'))
            self.logger.debug("Created bounds-checker object using the following properties:\n%s" % kwargs)

    def _run_bounds_checker(self, array):
        """
        If configured, run the bounds-checker for this request variable.
        """
        min_fixed = max_fixed = 0
        if self._do_bounds_check and self._bounds_checker:
            try:
                number_fixed = self._bounds_checker.check_bounds(array)
                if number_fixed:
                    min_fixed = self._bounds_checker.stats['tol_min'] + self._bounds_checker.stats['oob_min']
                    max_fixed = self._bounds_checker.stats['tol_max'] + self._bounds_checker.stats['oob_max']
            except qc.OutOfBoundsError as exception:
                self.logger.error('One or more data values fall outside specified min/max bounds.')
                raise exception
            except Exception as exception:
                self.logger.error(str(exception))
                raise exception

        return min_fixed, max_fixed

    def get_bounds_history(self):
        attributes = set(vars(self).keys())
        text = ""
        if set(['tol_min', 'valid_min', 'tol_min_action']) <= attributes:
            if self.tol_min_action == 'SET_TO_VALID_VALUE':
                text += "(%s <= x < %s) => set to %s, " % (self.tol_min, self.valid_min, self.valid_min)
            elif self.tol_min_action == 'SET_TO_FILL_VALUE':
                text += "(%s <= x < %s) => set to fill value, " % (self.tol_min, self.valid_min)
        if set(['tol_max', 'valid_max', 'tol_max_action']) <= attributes:
            if self.tol_max_action == 'SET_TO_VALID_VALUE':
                text += "(%s < x <= %s) => set to %s, " % (self.valid_max, self.tol_max, self.valid_max)
            elif self.tol_max_action == 'SET_TO_FILL_VALUE':
                text += "(%s < x <= %s) => set to fill value, " % (self.valid_max, self.tol_max)
        if set(['valid_min', 'valid_max', 'oob_action']) <= attributes:
            if self.oob_action == 'SET_TO_FILL_VALUE':
                text += "(%s > x > %s) => set to fill value" % (self.valid_min, self.valid_max)
        return text.rstrip(', ')

    def _has_bounds_history(self):
        return self.get_bounds_history() != ''

    def _time_stamp_text(self, text):
        from datetime import datetime
        timestamp = datetime.now().replace(microsecond=0)
        return timestamp.isoformat() + text

    def get_bounds_comment(self):
        """
        Return a compact text string describing any user-specified bounds-checking properties.
        """
        if not self._has_bounds_history():
            return ''
        else:
            return self._time_stamp_text(" out-of-bounds adjustments: " + self.get_bounds_history())


# TODO: I think there are too many classes involved in setting up the request lists
class CmorRequestBuilder(AbstractDataSourceUser):
    """
    Build requests from multiple request files.
    """
    STREAMFILE = '%s_variables'

    def __init__(self, config, parser_factory, reader):
        self._project_config = config
        self.factory = parser_factory
        self._reader = reader

    def _getStreamFileName(self, stream):
        return self.STREAMFILE % stream

    def _getConfigParser(self, stream):
        return self.factory.getReadParser(self._getStreamFileName(stream))

    def _streamRequest(self, stream):
        configuration = self._getConfigParser(stream)
        return CmorStreamRequestProvider(stream, configuration, self._reader)

    def build(self, composite):
        for stream in self.streamnames:
            composite.add(self._streamRequest(stream))


class CmorStreamRequestProvider(object):
    """
    Handle the requests from one stream request file.
    """

    def __init__(self, stream, config, reader):
        self.config = config
        self._stream = stream
        self._reader = reader

    def var_seq(self):
        variables = self.config.sections()
        variables.sort()
        requests = list()
        for variable in variables:
            requests.append(self._reader.readRequest(self._stream, variable, self.config))
        return requests


class PpRequestVariableReader(object):
    """
    Instances of this class will read the relavant variable section from the
    config file.

    Will look for optional attributes.
    """

    INT_ATTRS = ('lbproc', 'lbtim', 'lbuser5', 'outputs_per_file')
    """optional integer options"""

    FLOAT_ATTRS = ('fill_value', 'valid_min', 'valid_max', 'tol_min', 'tol_max', 'blev_tol', 'delta_time_in_days')
    """optional real options"""

    FLOAT_LIST_ATTRS = ('blev',)
    """optional real list options"""

    STRING_ATTRS = ('tol_min_action', 'tol_max_action', 'oob_action')
    """optional string options"""

    def __init__(self, processor_factory, outputter_factory=None):
        """
        stream - the stream name for this request
        stream_config - an opened, read ConfigParser
        """
        self._processor_factory = processor_factory
        self._request_section = None

    def readRequest(self, stream, request_id, config):
        self.stream = stream
        self.config = config
        return self._makeVarRequest(request_id)

    def _getOption(self, option):
        """
        reads option from the configuration file
        """
        return self.config.get(self._request_section, option)

    def _floatList(self, option_value):
        return [float(x) for x in option_value.split(' ')]

    def _set_optionals(self, request, attributes, as_type):
        """
        sets any optional attributes on var_request

        request - the request to set attributes on
        attrs  - attributes to set
        as_type - the function to use to convert from string to attribute
        """
        for attribute in attributes:
            if self._has_option(attribute):
                setattr(request, attribute, as_type(self._getOption(attribute)))

    def _readVarRequest(self, request):
        """
        read the integer and float options for request
        """
        self._set_boolean(request)
        self._set_optionals(request, self.INT_ATTRS, int)
        self._set_optionals(request, self.FLOAT_ATTRS, float)
        self._set_optionals(request, self.STRING_ATTRS, str)
        self._set_optionals(request, self.FLOAT_LIST_ATTRS, self._floatList)
        return request

    def _set_boolean(self, request):
        # should this use _set_optionals?
        request.first_only = False
        if self._has_option('first_only'):
            request.first_only = self.config.getboolean(self._request_section, 'first_only')

    def _entry(self):
        """
        returns the MIP table entry based on the variable id
        """
        return re.sub(r'_\d+', '', self._request_section)

    def _makeVarRequest(self, request_id):
        """
        make a request for the section request_id from the config parser
        @param request_id:  the variable to read.
                            This is the section in the config file.
                            The request_id should be made of the
                            MIP variable_entry, and optionaly an '_' followed
                            by an integer.  This allows use of multiple-MIP tables
                            from the same stream
        """
        self._request_section = request_id
        processor = self._processor_factory.getProcessor(self._get_mapping_id())
        request = PpRequestVariable(self._getOption('MIPtable'), self._entry(), self.stream, processor)

        # TODO: this needs tidying up
        request.outputs_per_file = None
        request = self._readVarRequest(request)
        request.output = self._get_request_output(request)
        return request

    def _get_mapping_id(self):
        if self._has_option('mapping_id'):
            result = self._getOption('mapping_id')
        else:
            (project, table) = self._getOption('MIPtable').split('_')
            result = MappingId(project, table, self._entry()).asPublished()
        return result

    def _has_option(self, option):
        return self.config.has_option(self._request_section, option)

    @staticmethod
    def _get_request_output(request):
        return mip_convert.save.cmor.cmor_lite.get_saver(request.table, request.entry, request.outputs_per_file)


class MappingId(object):
    """
    class to deal with the different formats of the mapping id or
    published string
    """

    def __init__(self, project, table, variable_entry):
        self._project = project
        self._table = table
        self._entry = variable_entry

    def asPublished(self):
        return '%s (%s, %s)' % (self._project, self._table, self._entry)
