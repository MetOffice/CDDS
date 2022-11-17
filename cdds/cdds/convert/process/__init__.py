# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
Processing components
"""
import collections
import glob
import logging
import os
import re
import shutil

from cdds.common.plugins.plugins import PluginStore
from cdds.common.mappings.mapping import ModelToMip

from cdds.common import (determine_rose_suite_url, configure_logger)
from cdds.deprecated.config import FullPaths
from mip_convert.configuration.python_config import PythonConfig

from cdds import __version__, _NUMERICAL_VERSION, _DEV
from cdds.common.constants import (REQUIRED_KEYS_FOR_PROC_DIRECTORY,
                                   DAYS_IN_YEAR, DAYS_IN_MONTH)
from cdds.common.request import read_request
from cdds.common.variables import RequestedVariablesList
from cdds.convert.constants import (NTHREADS_CONCATENATE, PARALLEL_TASKS,
                                    ROSE_SUITE_ID, SECTION_TEMPLATE,
                                    RESOURCE_FACTOR)
from cdds.convert.exceptions import StreamError
from cdds.convert.process import suite_interface
from cdds.convert.process.memory import scale_memory


class ConvertProcess(object):
    """
    The CDDS Convert process for managing the running of mip_convert.
    """

    def __init__(self, arguments):
        """

        Constructor for the ConvertProcess class.
        Parameters
        ----------
        arguments: :class:`cdds.arguments.Arguments` object
            The arguments specific to the `cdds_convert` script.
        """

        self.logger = logging.getLogger(__name__)
        self.logger.info('Using CDDS Convert version {}'.format(__version__))

        self._request = read_request(arguments.request,
                                     REQUIRED_KEYS_FOR_PROC_DIRECTORY)
        self._arguments = arguments
        self._full_paths = FullPaths(arguments, self._request)

        rv_path = self._full_paths.requested_variables_list_file
        self._rvl_file = RequestedVariablesList(rv_path)
        proc_dir = self._full_paths.proc_directory
        assert os.path.isdir(proc_dir), ('Processing directory "{}" not '
                                         'found').format(proc_dir)
        assert os.access(proc_dir, os.W_OK), ('Permissions on processing '
                                              'directory "{}" do not '
                                              'allow writing'
                                              '').format(proc_dir)
        logdir = self._full_paths.log_directory('convert')
        if not os.path.isdir(logdir):
            os.makedirs(logdir)

        self.skip_extract = arguments.skip_extract
        self.skip_qc = arguments.skip_qc
        self.skip_transfer = arguments.skip_transfer

        self._streams_requested = arguments.streams
        self._streams = []

        plugin = PluginStore.instance().get_plugin()
        self._model_params = plugin.models_parameters(self._request.model_id)

        # Pick up conversion suite name from the config project
        self._convert_suite = ROSE_SUITE_ID
        # Set the branch of the conversion suite to use
        self._rose_suite_branch = None
        self.set_branch(arguments.rose_suite_branch)
        # _last_suite_stage_completed is used to ensure that no attempt is
        # made to perform suite setup and submission out of order.
        self._last_suite_stage_completed = None
        # Initialise internal streams list
        self._streams = []

        # Calculate values required for the suite that require reading from
        # files and are calculated for all streams at once. Many other values
        # required for the suite which are calculated on a per stream basis,
        # these values are all streams at once, so it is done once at the
        # start, the values are stored in object and accessed as needed.
        self._build_stream_components()
        # As this code is not being used comment out to avoid issues when
        # running for certain variables. See CDDS #1706 for details
        # self._get_input_variables()
        # self._calculate_data_sizes()
        # self._calculate_processing_resources()
        # self.report_sizes()
        self._calculate_concat_task_periods()

        self.archive_data_version = arguments.archive_data_version

    def report_sizes(self):
        self.logger.info('esitimated variable sizes:')
        for var1 in self.variables_list:
            size_msg = '{mt}/{vid} - {size}MB'.format(
                mt=var1['mip_table_id'],
                vid=var1['variable_id'],
                size=var1['data_size_year'] / 2.0 ** 20
            )
            self.logger.info(size_msg)

        self.logger.info('maximum data sizes per stream/grid:')
        for stream_id, grids_info in list(self.resources_required.items()):
            for grid_id, resource_info in list(grids_info.items()):
                max_res_msg = '{sid}/{gid} = {mem}MB'.format(
                    sid=stream_id, gid=grid_id,
                    mem=resource_info['memory'] / 2.0 ** 20)
                self.logger.info(max_res_msg)

    @property
    def process(self):
        """
        Name of this process type.

        Returns
        -------
        str
        """
        return 'convert'

    @property
    def local_suite_name(self):
        """
        Name of the suite that will be run. If run with CREM access
        this will include the request index, otherwise the request_id
        be appended to the conversion suite name.
        """
        return '{0}_{1}'.format(self._convert_suite, self._request.request_id)

    def set_branch(self, branch_path):
        """
        Set the branch of the suite to use.

        Parameters
        ----------
        branch_path : str
            Location of the branch within the svn project for the Rose
            suite.
        """
        self._rose_suite_branch = branch_path

    @property
    def rose_suite_svn_location(self):
        """
        Return the svn URL for a rose suite on the SRS.

        Returns
        -------
        str
            SVN url of the repository to check out the conversion suite
            from.

        Raises
        ------
        RuntimeError
            If neither the internal or external repositories are
            accessible.
        """
        # Try internal first
        suite_base_url = determine_rose_suite_url(
            self._convert_suite, internal=True)
        # If that fails try the external
        if not suite_interface.check_svn_location(suite_base_url):
            self.logger.info('Could not access internal repository at "{}"'
                             ''.format(suite_base_url))
            suite_base_url = determine_rose_suite_url(
                self._convert_suite, internal=False)
            # If that fails log a critical message and raise a RuntimeError
            if not suite_interface.check_svn_location(suite_base_url):
                msg = ('Could not access external repository at "{}"'
                       '').format(suite_base_url)
                self.logger.error(msg)
                raise RuntimeError(msg)
        return os.path.join(suite_base_url, self._rose_suite_branch)

    @property
    def suite_destination(self):
        """
        Destination of suite on checkout.

        Returns
        -------
        : str
        The full path of the local copy of the suite.
        """
        return os.path.join(self._full_paths.component_directory('convert'),
                            self.local_suite_name)

    def delete_convert_suite(self):
        """
        Delete the existing conversion suite if it exists.
        OSErrors arising from the deletion are caught and logged, but
        are not raised further.
        """
        if os.path.exists(self.suite_destination):
            self.logger.info('Found existing files at {0.suite_destination}. '
                             'Attempting to delete them.'.format(self))
            try:
                if os.path.isdir(self.suite_destination):
                    shutil.rmtree(self.suite_destination)
                else:
                    os.unlink(self.suite_destination)
            except OSError as error:
                self.logger.error('Permission denied. Error: {}'.format(error))
                self.logger.info('Attempting to continue.')

    def checkout_convert_suite(self, delete_original=True):
        """
        Retreive the source code of the conversion suite from a local directory
        or repository URL and put into the convert proc directory.

        Parameters
        ----------
        delete_original : bool, optional
            If True clear out any existing files at the suite destination.
        """
        if delete_original:
            self.delete_convert_suite()
        if os.path.isdir(self._rose_suite_branch):
            self.logger.info('DEVELOPER MODE: Retrieving suite files '
                             'for suite {0._convert_suite} '
                             'from directory {0._rose_suite_branch} '
                             'to {0.suite_destination}'.format(self))
            shutil.copytree(self._rose_suite_branch,
                            self.suite_destination)
        else:
            self.logger.info('Checking out rose suite {0._convert_suite} '
                             'from ({0._rose_suite_branch}) '
                             'to {0.suite_destination}'
                             ''.format(self))
            try:
                output = suite_interface.checkout_url(
                    self.rose_suite_svn_location,
                    self.suite_destination)
            except suite_interface.SuiteCheckoutError as err:
                self.logger.exception(err)
            else:
                self.logger.info('Suite checkout to {} succeeded'
                                 ''.format(self.suite_destination))
                self.logger.info(
                    'SVN version: {}'.format(output.split('\n')[0]))
        self._last_suite_stage_completed = 'checkout'

    @property
    def request_id(self):
        """
        Get the |request identifier| for the package currently being processed.

        Returns
        -------
        : str
            The |request identifier| for the current package.
        """
        return self._request.request_id

    @property
    def streams(self):
        """
        Return a list of the |streams| to process. This is determined by
        the streams in the stream info section of the JSON request file.
        If the user has specified streams on the command line, only
        return streams that are both in the request file and specified
        by the user.
        """

        streams_to_process = list(self._get_streams_dict().keys())

        # Check if the user specified which streams to process
        if self._streams_requested:
            rejected_streams_cli = [s2 for s2 in self._streams_requested
                                    if s2 not in streams_to_process]
            if rejected_streams_cli:
                self.logger.info(
                    'The following streams were specified on the command line,'
                    'but will not be processed because they are not present '
                    'in the JSON request file:\n{stream_list}'
                    ''.format(stream_list=' '.join(rejected_streams_cli)))
            rejected_streams_request = [s3 for s3 in streams_to_process
                                        if s3 not in self._streams_requested]
            if rejected_streams_request:
                self.logger.info(
                    'The following streams are present in the JSON request '
                    'file, but will not be processed because they were not '
                    'specified on the command line :\n{stream_list}'
                    ''.format(stream_list=' '.join(rejected_streams_request)))
            streams_to_process = [s1 for s1 in streams_to_process
                                  if s1 in self._streams_requested]
        return streams_to_process

    @property
    def active_streams(self):
        """
        Return a list of the active |streams| to process, which are |streams|
        that have been checked and have conversions to be done. This is only
        valid after the __init__ function has run.

        Returns
        -------
        :list
            List of string representing active |streams|.

        """
        try:
            active_streams = list(self.stream_components.keys())
        except AttributeError:
            active_streams = []
        return active_streams

    @property
    def inactive_streams(self):
        """
        Return a list of the inactive |streams|, which will not be processed
        as they have no work to do.

        Returns
        -------
        :list
            List of string representing inactive |streams|.

        """
        inactive_streams = set(self.streams) - set(self.active_streams)
        return inactive_streams

    def _get_streams_dict(self):
        """

        Returns
        -------
        Returns a dict with useful streams related information extracted from
        the request object.
        """
        return self._request.streaminfo

    def year_bounds(self, stream=None):
        """
        Return the first and last year needed to process either
        (a) all |streams| or (b) a subset defined by the |stream identifier| or
        |stream identifiers| specified in the stream argument.

        Parameters
        ----------
        stream : str or list, optional
            Name(s) of the |stream| or |streams| to be processed.

        Returns
        -------
        int
            first year
        int
            last year

        Raises
        ------
        StreamError
            if stream is not active in this request.
        """

        def _streamcheck(i):
            if i not in self.streams:
                raise StreamError('Stream "{}" not found in streams list "{}"'
                                  ''.format(i, repr(self.streams)))

        start_year = 99999
        end_year = -99999

        if stream is None:
            streams_to_consider = self.streams
        elif isinstance(stream, list):
            [_streamcheck(s) for s in stream]
            streams_to_consider = stream
        else:
            _streamcheck(stream)
            streams_to_consider = [stream]

        if len(self.streams) == 0:
            return None, None
        for stream_name, stream_data in self._get_streams_dict().items():
            if stream_name in streams_to_consider:
                entry_start_date = [int(i1) for i1 in
                                    stream_data['start_date'].split('-')]
                entry_end_date = [int(i1) for i1 in
                                  stream_data['end_date'].split('-')]
                entry_start_year = entry_start_date[0]
                entry_end_year = entry_end_date[0]
                # If the end date is 1 January (month==1 and day==1), then
                # we want to process up to the end of the previous year,
                # so subtract 1 from the end year to achieve this
                if (entry_end_date[1] == 1 and
                        entry_end_date[2] == 1):
                    entry_end_year -= 1
                start_year = min(start_year, entry_start_year)
                end_year = max(end_year, entry_end_year)
        return start_year, end_year

    @property
    def ref_year(self):
        """
        Obtain the reference year for this |simulation| (i.e. the year it
        started). This is used for chunking output in the concatenation
        stages of the suite.

        Returns
        -------
        int
        """
        start_date_year = int(self._request.child_base_date.split('-')[0])
        return start_date_year

    def _build_stream_components(self):
        """
        Build a list of the grid identifiers for each |stream identifier|.

        The grid identifier is obtained from the name of each
        |user configuration file|, while the |stream identifier| is
        determined from the stream-related sections in the
        |user configuration file|.

        The method creates a dictionary with one entry per stream of a list
        of components for that stream. This dictionary is stored in the
        self.stream_components object attribute.
        """

        stream_grids = collections.defaultdict(list)
        substreams_dict = collections.defaultdict(dict)
        cfg_dir = self._full_paths.component_directory('configure')
        regex_streams = SECTION_TEMPLATE.format(
            stream_id='(?P<stream_id>[^_]+)',
            substream='(_(?P<substream>[^_]+))?')
        pattern_streams = re.compile(regex_streams)
        pattern_files = re.compile(
            self._arguments.user_config_template_name.format(
                '(?P<grid_id>[\w\-]+)'))
        self.variables_list = []
        for item in glob.glob(os.path.join(cfg_dir, '*')):
            match = pattern_files.match(os.path.basename(item))
            if match:
                substream_fname = match.group('grid_id')
                user_config = PythonConfig(item)
                streams_in_cfg = []
                vars_by_stream = {}
                for s1 in user_config.sections:
                    section_match = pattern_streams.match(s1)
                    if section_match:
                        stream_id = section_match.group('stream_id')
                        substream = section_match.group('substream')
                        streams_in_cfg += [(stream_id, substream)]
                        table_list = user_config.items(s1)
                        for mt, var_list_str in list(table_list.items()):
                            var_list = var_list_str.split(' ')
                            active_vars = var_list
                            _, mip_table_id = mt.split('_')
                            vars_by_stream[stream_id] = [{
                                'mip_table_id': mip_table_id,
                                'variable_id': var_id,
                                'stream_id': stream_id, 'substream': substream,
                                'grid': substream_fname}
                                for var_id in active_vars]

                # this ensures that the only streams included for processing
                # are those that are in the JSON request file, and if
                # the user specifies a list of streams to process, will
                # only include only those that are both in the request file and
                # specified by the user.
                active_streams = [(stream, substream)
                                  for (stream, substream) in streams_in_cfg
                                  if stream in self.streams]
                for (stream, substream) in active_streams:
                    self.variables_list += vars_by_stream[stream]
                    stream_grids[stream].append(substream_fname)
                    if substream is None:
                        substreams_dict[stream][substream_fname] = ''
                    else:
                        substreams_dict[stream][substream_fname] = substream
        self.stream_components = {
            stream_id: list(stream_comps)
            for stream_id, stream_comps in list(stream_grids.items())}
        self.substreams_dict = {
            stream_id: substreams
            for stream_id, substreams in list(substreams_dict.items())}

    def cycling_overrides(self):
        """
        Return the dictionary of cycling overrides constructed from
        the command line argument.
        """
        cycle_overrides = {}
        for entry in self._arguments.override_cycling_freq:
            stream, frequency = entry.split('=')
            cycle_overrides[stream] = frequency
        return cycle_overrides

    def _cycling_frequency(self, stream):
        """
        Obtain the cycling frequency for this model and stream from the
        configs after applying any command line overrides.
        If the default cycling frequency from the config .json has a longer duration
        than the run bounds, a default duration of P1Y is used.

        Parameters
        ----------
        stream: str
            |stream identifier| to calculate value for.

        Returns
        -------
        str
            Cycling frequency configuration information, a string
            representing the number of years formatted for cylc.
        """
        logger = logging.getLogger()
        cycle_length = self._model_params.cycle_length(stream)

        cycle_freq_exceeds_run_bounds, override_cycling_freq = self._check_cycle_freq_exceeds_run_bounds(cycle_length)

        overrides = self.cycling_overrides()
        if stream in overrides:
            frequency = overrides[stream]
            logger.info('Overriding cycling frequency for stream "{}": "{}" -> "{}"'
                        ''.format(stream, cycle_length, frequency))
            return frequency
        elif cycle_freq_exceeds_run_bounds:
            new_cycle_length = 'P{}Y'.format(override_cycling_freq)
            logger.info('Default cycling frequency "{}" for stream "{}" is greater than run bounds.'
                        'Using "{}" as the cycling frequency instead'.format(cycle_length, stream, new_cycle_length))
            return new_cycle_length
        else:
            return cycle_length

    def _check_cycle_freq_exceeds_run_bounds(self, cycle_frequency):
        """
        Function will return True if the cycling frequency duration is larger than the
        run bounds. Will return False if the cycling frequency is in units of Months or Days,
        as convert currently assumes run bounds will always be at least year.

        Parameters
        ----------
        cycle_frequency : str
            the default cycling frequency duration.

        Returns
        -------
        bool
            Returns True if cycling frequency duration exceed bounds, otherwise False.
        run_length : int
            Returns the time bound length in years. Used for new cycling frequency if needed.
        """
        cycling_years = re.match(r'P(?P<nyears>\d+)Y', cycle_frequency)

        if cycling_years:
            start_year, end_year = self.year_bounds()
            cycling_years = int(cycling_years.group('nyears'))
            run_length = end_year - start_year + 1
            return run_length < cycling_years, run_length
        elif re.match(r'P\d+[DM]', cycle_frequency):
            return False, None
        else:
            raise RuntimeError('Unrecognised cycle frequency duration.')

    def _cycling_frequency_value(self, stream):
        """
        Obtain the cycling frequency in years for this model from
        the configs.

        Parameters
        ----------
        stream: str
            Stream name to calculate for.

        Returns
        -------
        str
            Cycling frequency configuration information, an integer
            representing the number of years in a cycle.
        """
        # We need to create a regular expression to extract the actual values
        # of the cycling frequencies from the config files, where they are
        # stored as text values. The text in the config files is formatted in
        # the standard cylc time period format e.g. P5Y for 5 years. They are
        # stored in this format because they are primarily fed directly to
        # cylc to schedule tasks. Some functionality does need to use the
        # values in calculations, hence the need for this function to extract
        # the actual values.
        value_group_name = 'value'
        unit_group_name = 'unit'
        pattern = re.compile(
            'P(?P<{0}>[\d]+)(?P<{1}>[DMY])'.format(value_group_name,
                                                   unit_group_name))
        freq_str = self._cycling_frequency(stream)
        matches = pattern.search(freq_str)
        # Extract the values for each item in the relevant section of the
        # config file.
        unit = matches.group(unit_group_name)
        cycle_length = int(matches.group(value_group_name))
        return (cycle_length, unit)

    @property
    def input_model_run_length(self):
        """
        Get the length in years of the input model run that is being processed.

        Return
        ------
        int
            The length of the input model run in years.
        """
        start1, end1 = self.year_bounds()
        return int(end1) - int(start1) + 1

    def _calculate_concat_task_periods(self):
        self._calculate_max_concat_period()

        self._concat_task_periods_years = {
            stream: int(self.max_concat_period)
            for stream in self.active_streams
        }
        self._concat_task_periods_cylc = {
            stream: 'P{years}Y'.format(years=years)
            for stream, years
            in self._concat_task_periods_years.items()}

    def _calculate_max_concat_period(self):
        """
        Calculate the maximum concatenation window size in years for this run.
        This represents the longest period of data that will be stored in a
        single output file.

        Returns
        -------
        int
            The maximum concatenation window size in years for this run.
        """
        model_sizing = self._model_params.full_sizing_info()
        if model_sizing is None or model_sizing == {}:
            max_concat_period = self.input_model_run_length
        else:
            # get the max file length for all data dimensions for this model
            max_concat_period = max(max(
                output_length for data_dims, output_length in
                list(size_info.items())) for freq, size_info in list(model_sizing.items()))
        self.max_concat_period = max_concat_period

    def _first_concat_cycle_offset(self, stream):
        """
        Calculates the offset from the start year of the first cycle where
        concatenation tasks will run. This needs to be aligned with the
        reference date, so the first window will not necessarily be a full
        window. To define the endpoint of the first concatenation window, we
        want to find the first year after the start year that fits the pattern
        ref_year + n * window_size. The cycle will be 1 mip_convert cycle
        before that year.re.
        For example, if our run has reference 1850, start 1960, end 2200,
        mip_convert cycle frequency 5 years and concatenation window 50 years,
        we want the first |Concatenation Cycle| to run in 1995, producing files
        with data for 1960-1999, then subsequent concatenations will produce
        data for 2000-2049, 2050-2099 etc. and be correctly aligned with the
        reference year.

        Parameters
        ----------
        stream: str
            |stream identifier| to calculate value for.

        Returns
        -------
        dict
            A dict with the offset in years of first |Concatenation Cycle| for
            each stream from the start date of the suite.
        """
        single_concat = self._single_concatenation_cycle(stream)
        start_year, end_year = self.year_bounds()
        if single_concat:
            first_cycle = self._final_concatenation_cycle(stream)
        else:
            mc_cycle_length, mc_cycle_unit = self._cycling_frequency_value(
                stream)
            period = self._concat_task_periods_years[stream]
            # this finds the year where the first concatenation windows ends
            # at the very start of that year. From the docstring example,
            # we're looking for 2000.
            first_window_end = min(
                ((start_year - self.ref_year) // period + 1) * period
                + self.ref_year - start_year,
                end_year - start_year + 1)
            # calculate cycle offset differently  if mip_convert
            # cycle length is specified in config in years or months
            first_cycle = 'P{0}Y-P{1}{2}'.format(first_window_end,
                                                 mc_cycle_length,
                                                 mc_cycle_unit)
        return first_cycle

    def _convert_alignment_cycle_needed(self, stream):
        """
        Calculates for this stream whether a shortened mip_convert cycle is
        needed at the start of the run to align subsequent cycles with the
        reference date. We want cycles to happen on years where:
        cycle_year = reference_year + n * cycle_period. Where this is not true
        for the start year of the run, a short alignment cycle is necessary.

        Parameters
        ----------
        stream: str
            |stream identifier| to calculate value for.

        Returns
        -------
        dict
            A dict with a boolean for each stream that is True if an alignment
            cycle is required.
        """
        return 'P0Y' != self._convert_alignment_cycle_offset(stream)

    def _convert_alignment_cycle_offset(self, stream):
        """
        Calculates for this  stream the length  of the shortened mip_convert
        cycle needed at the start of the run to align subsequent cycles with
        the reference date. We want cycles to happen on years where:
        cycle_year = reference_year + n * cycle_period. Where this is not true
        for the start year of the run, a short alignment cycle is necessary.
        If the reference date is 1850, the start date is 1963 and the
        mip_convert cycle period is 5 years, the first cycle will be 2 years
        long (1963-1964) so that subsequent cycles are aligned
        (1965, 1970 etc.).

        Parameters
        ----------
        stream: str
            |stream identifier| to calculate value for.

        Returns
        -------
        dict
            A dict with a string for each stream that representing the offset
            required in cylc date format.
        """
        start_year, end_year = self.year_bounds()
        start_ref_offset = start_year - self.ref_year
        (freq, freq_unit) = self._cycling_frequency_value(stream)
        if freq_unit == 'Y':
            offset_value = (-start_ref_offset) % freq
            alignment_offset = 'P{0}Y'.format(offset_value)
        elif freq_unit in ['M', 'D']:
            alignment_offset = 'P0Y'
        return alignment_offset

    def _final_concatenation_needed(self, stream):
        """
        Check whether a final concatenation task is needed for the specified
        stream. This is only true where the end of processing is not a number
        of years after the reference date that is a multiple of the window
        size. In that case, an additional task run to concatenate the
        remaining files.

        Parameters
        ----------
        stream: str
            |stream identifier| to calculate value for.

        Returns
        -------
        dict
            A dict with one entry per stream, which is a boolean which is true
            if a final |Concatenation Cycle| is necessary.
        """
        start_year, end_year = self.year_bounds()
        concat_period = self._concat_task_periods_years[stream]
        if self._single_concatenation_cycle(stream):
            return False

        # first check if the concatenation periods line up with the end of
        # the data to be processed.
        final_concat_needed = ((end_year - self.ref_year + 1)
                               % concat_period != 0)

        # next check if the last regularly scheduled concat task will
        # still be able to cover all the data. This happens if the end point of
        # the run falls in the final mip_convert processing period, in which
        # case we don't want to add a final special concat task as we will
        # have duplicated tasks which can interfere and cause errors
        if final_concat_needed:
            final_concat_days = ((end_year - self.ref_year + 1) %
                                 concat_period) * DAYS_IN_YEAR
            concat_period_days = concat_period * DAYS_IN_YEAR
            mip_convert_period, unit = self._cycling_frequency_value(stream)
            if unit == 'Y':
                mip_convert_cycle_days = mip_convert_period * DAYS_IN_YEAR
            elif unit == 'M':
                mip_convert_cycle_days = mip_convert_period * DAYS_IN_MONTH
            elif unit == 'D':
                mip_convert_cycle_days = mip_convert_period
            else:
                raise RuntimeError('unknown cycling period unit')
            if (final_concat_days > (
                    concat_period_days - mip_convert_cycle_days)):
                final_concat_needed = False
        return final_concat_needed

    def _final_concatenation_cycle(self, stream):
        """
        Calculates the cycle point for the final Concatenation Cycles for this
        stream. This is to account for aligning cycles with the reference date.

        Parameters
        ----------
        stream: str
            |stream identifier| to calculate value for.

        Returns
        -------
        str
            A string representing a cylc formatted date when the final cycle
            for this stream will be. This ensures that if the run length is
            not a multiple of the concatenation window length, then all the
            data will still have been processed by the concatenation scripts.

        """
        start_year, end_year = self.year_bounds()
        ref_length_years = end_year - self.ref_year + 1
        # Find the integer multiple of concat window start from the reference
        # year that is before and closest to the end year.
        (cycle_freq, unit) = self._cycling_frequency_value(stream)
        if unit == 'Y':
            offset_years = (
                ((ref_length_years - 1) // cycle_freq) * cycle_freq
                - start_year + self.ref_year)
            final_concat_cycle = 'P{0}Y'.format(offset_years)
        elif unit == 'M':
            offset_months = (((
                ref_length_years * 12) - 1) // cycle_freq) * cycle_freq
            offset_years = (
                (offset_months // 12) - start_year + self.ref_year)
            final_concat_cycle = ('P{0}Y{1}M'.format(offset_years,
                                                     offset_months % 12))
        elif unit == 'D':
            offset_days = (((ref_length_years * DAYS_IN_YEAR) - 1) // cycle_freq) * cycle_freq
            offset_months = ((offset_days // DAYS_IN_MONTH))
            offset_years = ((offset_months // 12) - start_year + self.ref_year)

            final_concat_cycle = ('P{0}Y{1}M{2}D'.format(offset_years,
                                                         offset_months % 12,
                                                         offset_days % DAYS_IN_MONTH))
        return final_concat_cycle

    def _final_concatenation_window_start(self, stream):
        """
        Calculates the start of concatenation window for the final
        concatenation operation in this stream. This is to account for
        aligning cycles with the reference date.

        Parameters
        ----------
        stream: str
            |stream identifier| to calculate value for.

        Returns
        -------
        str
            An an integer representing the start year of the concatenation
            window for the final task in this stream. This is triggered ensures
            that if the run length is not a multiple of the concatenation
            window length, then all the data will still have been processed by
            the concatenation scripts.
        """
        start_year, end_year = self.year_bounds()
        ref_length = end_year - self.ref_year
        # Find the integer multiple of concat window start from the reference
        # year that is before and closest to the end year.
        concat_window = self._concat_task_periods_years[stream]
        if self._single_concatenation_cycle(stream):
            return 0

        final_concat_windows_start_year = (
            (ref_length // concat_window) * concat_window + self.ref_year)
        return final_concat_windows_start_year

    def _single_concatenation_cycle(self, stream):
        """
        Calculates if only one |Concatenation Cycle| is needed by comparing
        the concatenation window for each stream with the run length. If
        the window size for a stream is larger than the run length, then only
        one |Concatenation Cycle| will run.

        Parameters
        ----------
        stream: str
            |stream identifier| to calculate value for.

        Returns
        -------
        bool
            A boolean which is True if only a single |Concatenation Cycle|
            needs to be run and False if the run is long enough to require
            multiple |Concatenation Cycles|.
        """
        run_length = self.input_model_run_length
        window_size = self._concat_task_periods_years[stream]
        return window_size >= run_length

    def _stream_time_override(self, year_bounds, stream):
        """
        Calculate stream time overrides dictionary for suite

        Parameters
        ----------
        year_bounds : tuple
            start and end year for processing
        stream: str
            |stream identifier| to calculate value for.

        Returns
        -------
        str
            stream time override information
        """
        if stream not in self.active_streams:
            return "None"
        entry_bounds = self.year_bounds(stream)
        if entry_bounds == year_bounds:
            stream_time_override = "None"
        else:
            stream_time_override = entry_bounds
        return stream_time_override

    def mip_convert_temp_sizes(self, stream_id):
        """
        Get the size of temporary file space in MB needed for the processing of
        the specified stream.

        Parameters
        ----------
        stream_id: str
            The |Stream identifier| for which to retrieve the size of temporary
            disk space in MB required for MIP convert processing.

        Returns
        -------
        :int
            The size of the temporary space required in MB for MIP convert
            tasks in this stream.
        """
        return self._model_params.temp_space(stream_id)

    def validate_streams(self):
        """
        Ensure there are |streams| to process.

        Raises
        ------
        RuntimeError
            If there are no |streams| to process.
        """
        if not self.active_streams:
            msg = 'No streams to process'
            self.logger.error(msg)
            raise RuntimeError(msg)
        inactive_streams = self.inactive_streams
        if inactive_streams:
            streams_str = ','.join(inactive_streams)
            msg = ('Warning: Skipping streams {streams_str} as there are no '
                   'variables to produce.'.format(streams_str=streams_str))
            self.logger.warning(msg)

    def _update_suite_rose_suite_conf(self, location):
        """
        Update the rose-suite.conf file with suite level settings that are the
        same for all streams. Stream specific settings will be set trhough
        stream-specific optional config files (see _update_suite_opt_conf).

        Parameters
        ----------
        location: str
            The platform on which to run the tasks in the suite.
        """
        year_bounds = self.year_bounds()
        rose_suite_conf_file = os.path.join(self.suite_destination,
                                            'rose-suite.conf')

        # In order to run subtasks in the convert suite (extract, QC and
        # transfer), the suite needs to know the path to the request JSON file.
        # This path is often specified as a relative path, so we need to
        # get the absolute path if this is the case to pass to the suite
        # config.
        if os.path.isabs(self._arguments.request):
            request_json_path = self._arguments.request
        else:
            request_json_path = os.path.abspath(self._arguments.request)

        use_external_plugin = False
        external_plugin = ''
        external_plugin_location = ''
        if self._arguments.external_plugin:
            use_external_plugin = True
            external_plugin = self._arguments.external_plugin
            external_plugin_location = self._arguments.external_plugin_location

        changes_to_apply_all = {
            'MIP_ERA': self._arguments.mip_era,
            'CDDS_CONVERT_PROC_DIR': self._full_paths.component_directory(
                'convert'),
            'CDDS_VERSION': _NUMERICAL_VERSION,
            'DEV_MODE': _DEV,
            'END_YEAR': year_bounds[1],
            'INPUT_DIR': self._full_paths.input_data_directory,
            'OUTPUT_MASS_ROOT': self._arguments.output_mass_root,
            'OUTPUT_MASS_SUFFIX': self._arguments.output_mass_suffix,
            'EMAIL_NOTIFICATIONS': self._arguments.email_notifications,
            'MIP_CONVERT_CONFIG_DIR': self._full_paths.component_directory(
                'configure'),
            'MODEL_ID': self._request.model_id,
            'NTHREADS_CONCATENATE': (
                NTHREADS_CONCATENATE),
            'OUTPUT_DIR': self._full_paths.output_data_directory,
            'PARALLEL_TASKS': PARALLEL_TASKS,
            'REF_YEAR': self.ref_year,
            'REQUEST_JSON_PATH': request_json_path,
            'ROOT_DATA_DIR': self._arguments.root_data_dir,
            'ROOT_PROC_DIR': self._arguments.root_proc_dir,
            'RUN_EXTRACT': not self.skip_extract,
            'RUN_QC': not self.skip_qc,
            'RUN_TRANSFER': not self.skip_transfer,
            'START_YEAR': year_bounds[0],
            'TARGET_SUITE_NAME': self.target_suite_name,
            'USE_EXTERNAL_PLUGIN': use_external_plugin
        }
        if use_external_plugin:
            changes_to_apply_all['EXTERNAL_PLUGIN'] = external_plugin
            changes_to_apply_all['EXTERNAL_PLUGIN_LOCATION'] = external_plugin_location

        if 'CDDS_DIR' in os.environ:
            changes_to_apply_all['CDDS_DIR'] = os.environ['CDDS_DIR']
        else:
            self.logger.info('Environment variable CDDS_DIR not found. '
                             'Skipping interpolation into rose suite')
        if location:
            changes_to_apply_all['LOCATION'] = location

        try:
            changes_applied = suite_interface.update_suite_conf_file(
                rose_suite_conf_file, **changes_to_apply_all)
        except Exception as err:
            self.logger.exception(err)
            raise err
        else:
            self.logger.info('Update to rose-suite.conf successful. '
                             'Changes made: "{}"'
                             ''.format(repr(changes_applied)))

    def _get_required_memory(self, stream):
        components = self.stream_components
        required_memory = {
            c1: self._model_params.memory(stream)
            for c1 in components[stream]}
        # Scale memory limits if included on command line
        if self._arguments.scale_memory_limits is not None:
            required_memory = {
                component: scale_memory(
                    mem_limit, self._arguments.scale_memory_limits)
                for component, mem_limit in required_memory.items()
            }

        return required_memory

    def _update_suite_opt_conf(self, stream):
        """
        Gather together the per stream settings and update the stream specific
        config file in opt/rose-suite-<stream>.conf.

        Parameters
        ----------
        stream: str
            |stream identifier| to calculate value for.

        """
        year_bounds = self.year_bounds()
        components = self.stream_components
        template_path = os.path.join(self.suite_destination, 'opt',
                                     'rose-suite-stream.conf')
        required_memory = self._get_required_memory(stream)
        # currently the memory is only specified per model and stream, we
        # could another layer to the dictionary in constants to specify by
        # component as well. For now I am creatinga dictionary per component
        # and assigning the same value to each component
        stream_opt_conf_path = os.path.join(
            self.suite_destination, 'opt',
            'rose-suite-{stream}.conf'.format(stream=stream))
        shutil.copy(template_path, stream_opt_conf_path)
        changes_to_appy_per_stream = {
            'ACTIVE_STREAM': stream,
            'ARCHIVE_DATA_VERSION': self.archive_data_version,
            'CONCATENATION_FIRST_CYCLE_OFFSET':
                self._first_concat_cycle_offset(stream),
            'CONCATENATION_WINDOW': self._concat_task_periods_cylc[stream],
            'CONVERT_ALIGNMENT_OFFSET':
                self._convert_alignment_cycle_offset(stream),
            'CYCLING_FREQUENCY': self._cycling_frequency(stream),
            'DO_CONVERT_ALIGNMENT_CYCLE':
                self._convert_alignment_cycle_needed(stream),
            'DO_FINAL_CONCATENATE':
                self._final_concatenation_needed(stream),
            'FINAL_CONCATENATION_CYCLE':
                self._final_concatenation_cycle(stream),
            'FINAL_CONCATENATION_WINDOW_START':
                self._final_concatenation_window_start(stream),
            'MEMORY_CONVERT': required_memory,
            'MIP_CONVERT_TMP_SPACE': self.mip_convert_temp_sizes(stream),
            'SINGLE_CONCATENATION_CYCLE':
                self._single_concatenation_cycle(stream),
            'STREAM_COMPONENTS': components[stream],
            'STREAM_SUBSTREAMS': self.substreams_dict[stream],
            'STREAM_TIME_OVERRIDES': self._stream_time_override(year_bounds,
                                                                stream),
        }

        try:
            changes_applied = suite_interface.update_suite_conf_file(
                stream_opt_conf_path, **changes_to_appy_per_stream)
        except Exception as err:
            self.logger.exception(err)
        else:
            self.logger.info(
                'Update to {0} successful. Changes made: "{1}"'
                ''.format(stream_opt_conf_path, repr(changes_applied)))

    def update_convert_suite_parameters(self, location=None):
        """
        Update parameters in the rose-suite.conf file in the conversion
        suite.

        Parameters
        ----------
        location : str, optional
            If set this changes the LOCATION parameter in the Rose
            suite to the value specified. This can break the suite if
            a suitable task family does not exist.
        """
        assert self._last_suite_stage_completed == 'checkout'
        self.logger.info('Updating rose-suite.conf entries')

        self._update_suite_rose_suite_conf(location)

        for stream in self.active_streams:
            self._update_suite_opt_conf(stream)

        self._last_suite_stage_completed = 'update'

    @property
    def target_suite_name(self):
        """
        Return the name of the target suite.

        Returns
        -------
        : str
            Name of the target suite, e.g. "u-ar050".
        """
        return self._request.suite_id

    def _suite_action(self, action_name, action, error, **kwargs):
        words = {'submit': ('Submitting', 'submitted', 'Submission'),
                 'shutdown': ('Shutting down', 'shutdown', 'Shutdown')}

        self.logger.info('{} suite in {}'.format(words[action_name][0],
                                                 self.suite_destination))
        try:
            result = action(self.suite_destination, **kwargs)
            self.logger.info(
                'Suite {} successfully'.format(words[action_name][1]))
            self.logger.info('Suite standard output:\n {}'.format(result))
        except error as err:
            self.logger.error(
                '{} failed: {}'.format(words[action_name][2], err))
            raise err

    def submit_suite(self, **kwargs):
        """
        Submit the rose suite.

        Keyword arguments are passed on to
        cdds.convert.suite_interface.submit_suite.
        """
        assert self._last_suite_stage_completed == 'update'
        self._suite_action('submit', suite_interface.submit_suite,
                           suite_interface.SuiteSubmissionError, **kwargs)
