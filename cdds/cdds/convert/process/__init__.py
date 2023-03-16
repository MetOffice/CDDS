# (C) British Crown Copyright 2017-2023, Met Office.
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

from metomi.isodatetime.data import Calendar
from metomi.isodatetime.parsers import (DurationParser, TimePointParser,
                                        TimeRecurrenceParser)

from cdds import _DEV, _NUMERICAL_VERSION, __version__
from cdds.common import determine_rose_suite_url
from cdds.common.constants import REQUIRED_KEYS_FOR_PROC_DIRECTORY
from cdds.common.plugins.plugins import PluginStore
from cdds.common.request import read_request
from cdds.common.variables import RequestedVariablesList
from cdds.convert.constants import (NTHREADS_CONCATENATE, PARALLEL_TASKS,
                                    ROSE_SUITE_ID, SECTION_TEMPLATE)
from cdds.convert.process import suite_interface
from cdds.convert.process.memory import scale_memory
from cdds.deprecated.config import FullPaths
from mip_convert.configuration.python_config import PythonConfig


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
        self.set_calendar()
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
        self.skip_extract_validation = arguments.skip_extract_validation
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

        self._calculate_concat_task_periods()

        self.archive_data_version = arguments.archive_data_version

    def set_calendar(self):
        """Set the calendar for metomi.isodatetime based on the request

        :raises RuntimeError: If an unsupported calendar is used.
        """
        if self._request.calendar in Calendar.default().MODES.keys():
            Calendar.default().set_mode(self._request.calendar)
        else:
            msg = "Unsupported metomi.isodate calendar: {}".format(self._request.calendar)
            raise RuntimeError(msg)

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

    def run_bounds(self):
        """
        Return the start date and end date needed to process all |streams|.

        :return: A tuple containing the start and end date of the simulation.
        :rtype: tuple (TimePoint, TimePoint)
        """

        start_date, end_date = self._request.run_bounds.split()

        start_date = "-".join(start_date.split('-')[:3])
        end_date = "-".join(end_date.split('-')[:3])

        start_date = TimePointParser().parse(start_date)
        end_date = TimePointParser().parse(end_date) - DurationParser().parse('P1D')

        return start_date, end_date

    @property
    def ref_date(self):
        """
        Obtain the reference date for this |simulation| (i.e. the date it
        started). This is used for chunking output in the concatenation
        stages of the suite.

        :return: The reference date in the form 18500101
        :rtype: TimePoint
        """
        reference_date = "".join(self._request.child_base_date.split('-')[:3])
        reference_date = TimePointParser().parse(reference_date)
        return reference_date

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

        :return: A dictionary of stream overrides.
        :rtype: dict
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
            start_date, end_date = self.run_bounds()
            start_year, end_year = start_date.year, end_date.year
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

        :return: The length of the input model run in years.
        :rtype: int
        """
        start_date, end_date = self.run_bounds()
        start_year, end_year = start_date.year, end_date.year
        return end_year - start_year + 1

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

        :return: The maximum concatenation window size in years for this run.
        :rtype: int
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

        :param stream: The |stream identifier| to calculate value for.
        :type stream: str
        :return: A cylc formatted duration string in days. E.g, P720D
        :rtype: str
        """
        single_concat = self._single_concatenation_cycle(stream)

        if single_concat:
            first_cycle = self._final_concatenation_cycle(stream)
            return first_cycle
        else:
            concat_period = self._concat_task_periods_cylc[stream]
            aligned_concatenation_dates = TimeRecurrenceParser().parse(f'R/{self.ref_date}/{concat_period}')
            start_date, _ = self.run_bounds()
            concat_window_date = aligned_concatenation_dates.get_first_after(start_date)
            cycling_frequency = self._cycling_frequency(stream)
            first_cycle = concat_window_date - DurationParser().parse(cycling_frequency)
            first_cycle = str(first_cycle - start_date)
        return first_cycle

    def _convert_alignment_cycle_needed(self, stream):
        """
        Calculates for this stream whether a shortened mip_convert cycle is
        needed at the start of the run to align subsequent cycles with the
        reference date. We want cycles to happen on years where:
        cycle_year = reference_year + n * cycle_period. Where this is not true
        for the start year of the run, a short alignment cycle is necessary.

        :param stream: The |stream identifier| to calculate the value for.
        :type stream: str
        :return: A cylc formatted duration string in days. E.g, P720D
        :rtype: str
        """
        return 'P0D' != self._convert_alignment_cycle_offset(stream)

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

        :param stream: The |stream identifier| to calculate vthe alue for.
        :type stream: str
        :return: A cylc formatted duration string in days. E.g, P720D
        :rtype: str
        """
        start_date, _ = self.run_bounds()
        cycling_frequency = self._cycling_frequency(stream)
        recurrence = TimeRecurrenceParser().parse(f'R/{self.ref_date}/{cycling_frequency}')
        if not recurrence.get_is_valid(start_date):
            alignment_offset = str(recurrence.get_first_after(start_date) - start_date)
        else:
            alignment_offset = 'P0D'

        return alignment_offset

    def _final_concatenation_needed(self, stream):
        """
        Check whether a final concatenation task is needed for the specified
        stream. This is only true where the end of processing is not a number
        of years after the reference date that is a multiple of the window
        size. In that case, an additional task run to concatenate the
        remaining files.

        :param stream: The |stream identifier| to calculate a value for.
        :type stream: str
        :returns: A boolean which is true if a final |Concatenation Cycle| is necessary.
        :rtype: bool
        """

        if self._single_concatenation_cycle(stream):
            return False

        start_date, _ = self.run_bounds()
        final_concatenation_cycle = DurationParser().parse(self._final_concatenation_cycle(stream)) + start_date
        concat_period = self._concat_task_periods_cylc[stream]
        first_concat_cycle_offset = self._first_concat_cycle_offset(stream)
        first_concat_cycle = start_date + DurationParser().parse(first_concat_cycle_offset)
        recurrence = TimeRecurrenceParser().parse(f'R/{first_concat_cycle}/{concat_period}')
        return not recurrence.get_is_valid(final_concatenation_cycle)

    def _final_concatenation_cycle(self, stream):
        """
        Calculates the cycle point for the final Concatenation Cycles for this
        stream. This is to account for aligning cycles with the reference date.

        :param stream: The |stream identifier| to calculate value for.
        :type stream: str
        :return: A string representing a cylc formatted date when the final cycle
            for this stream will be. This ensures that if the run length is
            not a multiple of the concatenation window length, then all the
            data will still have been processed by the concatenation scripts.
        :rtype: str
        """
        start_date, end_date = self.run_bounds()
        cycling_frequency = self._cycling_frequency(stream)
        cycling_freq_recurrence = TimeRecurrenceParser().parse(f'R/{self.ref_date}/{cycling_frequency}')
        final_concatenation_cycle = cycling_freq_recurrence.get_prev(cycling_freq_recurrence.get_first_after(end_date))
        final_concatenation_cycle_in_days = str(final_concatenation_cycle - start_date)
        return final_concatenation_cycle_in_days

    def _final_concatenation_window_start(self, stream):
        """
        Calculates the start of concatenation window for the final
        concatenation operation in this stream. This is to account for
        aligning cycles with the reference date.

        :param stream: The |stream identifier| to calculate a value for.
        :param type: str
        :return: A string representing the start year of the concatenation
            window for the final task in this stream. This is triggered ensures
            that if the run length is not a multiple of the concatenation
            window length, then all the data will still have been processed by
            the concatenation scripts.
        :rtype: str
        """
        if self._single_concatenation_cycle(stream):
            return 0

        _, end_date = self.run_bounds()
        period = self._concat_task_periods_cylc[stream]
        recurrence = TimeRecurrenceParser().parse(f'R/{self.ref_date}/{period}')
        final_concat_windows_start_year = str(recurrence.get_prev(recurrence.get_first_after(end_date)))

        return final_concat_windows_start_year

    def _single_concatenation_cycle(self, stream):
        """
        Calculates if only one |Concatenation Cycle| is needed by comparing
        the concatenation window for each stream with the run length. If
        the window size for a stream is larger than the run length, then only
        one |Concatenation Cycle| will run.

        :param stream: The |stream identifier| to calculate value for.
        :type stream: str
        :return: A boolean which is True if only a single |Concatenation Cycle|
            needs to be run and False if the run is long enough to require
            multiple |Concatenation Cycles|.
        :rtype: bool
        """
        start_date, end_date = self.run_bounds()
        window_size = DurationParser().parse(self._concat_task_periods_cylc[stream])

        return start_date + window_size >= end_date

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
        section_name = 'jinja2:suite.rc'
        run_bounds = self.run_bounds()
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
            'END_DATE': str(run_bounds[1]),
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
            'REF_YEAR': self.ref_date.year,
            'REQUEST_JSON_PATH': request_json_path,
            'ROOT_DATA_DIR': self._arguments.root_data_dir,
            'ROOT_PROC_DIR': self._arguments.root_proc_dir,
            'RUN_EXTRACT': not self.skip_extract,
            'RUN_EXTRACT_VALIDATION': not self.skip_extract_validation,
            'RUN_QC': not self.skip_qc,
            'RUN_TRANSFER': not self.skip_transfer,
            'START_DATE': str(run_bounds[0]),
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
            changes_applied = suite_interface.update_suite_conf_file(rose_suite_conf_file, section_name,
                                                                     changes_to_apply_all, raw_value=False)
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
        section_name = 'jinja2:suite.rc'
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
        }

        try:
            changes_applied = suite_interface.update_suite_conf_file(stream_opt_conf_path, section_name,
                                                                     changes_to_appy_per_stream, raw_value=False)
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
