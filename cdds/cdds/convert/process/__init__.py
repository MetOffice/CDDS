# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
Processing components
"""
import collections
import glob
import logging
import os
import re
import shutil

from argparse import Namespace
from typing import List, Dict, Tuple, Union, Set, TYPE_CHECKING

from metomi.isodatetime.data import Calendar
from metomi.isodatetime.parsers import (DurationParser, TimeRecurrenceParser)

from metomi.isodatetime.data import TimePoint

from cdds import _DEV, _NUMERICAL_VERSION, __version__
from cdds.common import determine_rose_suite_url
from cdds.common.plugins.plugins import PluginStore
from cdds.common.cdds_files.cdds_directories import component_directory, input_data_directory, output_data_directory
from cdds.common.request.request import Request
from cdds.common.variables import RequestedVariablesList
from cdds.convert.constants import (NTHREADS_CONCATENATE, PARALLEL_TASKS,
                                    ROSE_SUITE_ID, SECTION_TEMPLATE)
from cdds.convert.process import workflow_interface
from cdds.convert.process.memory import scale_memory
from mip_convert.configuration.python_config import PythonConfig

if TYPE_CHECKING:
    from cdds.convert.arguments import ConvertArguments


class ConvertProcess(object):
    """
    The CDDS Convert process for managing the running of mip_convert.
    """

    def __init__(self, arguments: 'ConvertArguments', request: Request):
        """

        Constructor for the ConvertProcess class.
        Parameters
        ----------
        arguments: ConvertArguments object
            The arguments specific to the `cdds_convert` script.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info('Using CDDS Convert version {}'.format(__version__))

        self._request = request
        self._arguments = arguments

        self.set_calendar()
        self._plugin = PluginStore.instance().get_plugin()
        proc_dir = self._plugin.proc_directory(request)

        rv_path = os.path.join(proc_dir, 'prepare', self._plugin.requested_variables_list_filename(request))
        self._rvl_file = RequestedVariablesList(rv_path)

        assert os.path.isdir(proc_dir), 'Processing directory "{}" not found'.format(proc_dir)
        assert os.access(proc_dir, os.W_OK), ('Permissions on processing directory "{}" do not allow writing'
                                              '').format(proc_dir)

        logdir = os.path.join(proc_dir, 'convert', 'log')
        if not os.path.isdir(logdir):
            os.makedirs(logdir)

        self.skip_extract = request.conversion.skip_extract
        self.skip_extract_validation = request.conversion.skip_extract_validation
        self.skip_qc = request.conversion.skip_qc
        self.skip_transfer = request.conversion.skip_archive

        self._streams_requested = self._arguments.streams
        self._model_params = self._plugin.models_parameters(self._request.metadata.model_id)

        # Pick up conversion suite name from the config project
        self._convert_suite = ROSE_SUITE_ID
        # Set the branch of the conversion suite to use
        self._rose_suite_branch = None
        self.set_branch(request.conversion.cdds_workflow_branch)
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

        self.archive_data_version = request.data.data_version

    def set_calendar(self) -> None:
        """
        Set the calendar for metomi.isodatetime based on the request
        """
        if self._request.metadata.calendar in Calendar.default().MODES.keys():
            Calendar.default().set_mode(self._request.metadata.calendar)
        else:
            msg = "Unsupported metomi.isodate calendar: {}".format(self._request.metadata.calendar)
            raise RuntimeError(msg)

    @property
    def process(self) -> str:
        """
        Returns the name of this process type.

        :return: Name of this process type
        :rtype: str
        """
        return 'convert'

    @property
    def local_suite_name(self) -> str:
        """
        Returns the name of the suite that will be run. If run with CREM access this will include the request index,
        otherwise the request_id be appended to the conversion suite name.

        :return: Name of the suite that will be run
        :rtype: str
        """
        return '{0}_{1}'.format(self._convert_suite, self._request.common.workflow_basename)

    def set_branch(self, branch_path: str) -> None:
        """
        Set the branch of the Cylc workflow to use.

        :param branch_path: Location of the branch within the svn project for the Cylc Workflow.
        :type branch_path: str
        """
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
    def rose_suite_svn_location(self) -> str:
        """
        Returns the SVN URL for a cylc workflow on the SRS.

        :return: SVN url of the repository to check out the conversion suite from.
        :rtype: str
        """
        # Try internal first
        suite_base_url = determine_rose_suite_url(self._convert_suite, internal=True)
        # If that fails try the external
        if not workflow_interface.check_svn_location(suite_base_url):
            self.logger.info('Could not access internal repository at "{}"'.format(suite_base_url))
            suite_base_url = determine_rose_suite_url(self._convert_suite, internal=False)

            # If that fails log a critical message and raise a RuntimeError
            if not workflow_interface.check_svn_location(suite_base_url):
                msg = 'Could not access external repository at "{}"'.format(suite_base_url)
                self.logger.error(msg)
                raise RuntimeError(msg)

        # Check the branch is also valid
        suite_full_url = os.path.join(suite_base_url, self._rose_suite_branch)
        if not workflow_interface.check_svn_location(suite_full_url):
            msg = 'Could not access branch "{}" at "{}"'.format(self._rose_suite_branch, suite_full_url)
            self.logger.error(msg)
            raise RuntimeError(msg)
        return suite_full_url

    @property
    def suite_destination(self) -> str:
        """
        Returns the destination of the Cylc workflow on checkout.

        :return: The full path of the local copy of the Cylc workflow.
        :rtype: str
        """
        component_dir = component_directory(self._request, 'convert')
        return os.path.join(component_dir, self.local_suite_name)

    def delete_convert_suite(self) -> None:
        """
        Deletes the existing conversion suite if it exists.
        OSErrors arising from the deletion are caught and logged, but are not raised further.
        """
        if os.path.exists(self.suite_destination):
            self.logger.info('Found existing files at {0.suite_destination}. Attempting to delete them.'.format(self))
            try:
                if os.path.isdir(self.suite_destination):
                    shutil.rmtree(self.suite_destination)
                else:
                    os.unlink(self.suite_destination)
            except OSError as error:
                self.logger.error('Permission denied. Error: {}'.format(error))
                self.logger.info('Attempting to continue.')

    def checkout_convert_workflow(self, delete_original: bool = True) -> None:
        """
        Retrieves the source code of the conversion suite from a local directory
        or repository URL and put into the convert proc directory.

        :param delete_original: If True clear out any existing files at the suite destination.
        :type delete_original: bool
        """
        if delete_original:
            self.delete_convert_suite()
        if os.path.isdir(self._rose_suite_branch):
            self.logger.info('DEVELOPER MODE: Retrieving suite files for suite {0._convert_suite} '
                             'from directory {0._rose_suite_branch} to {0.suite_destination}'.format(self))
            shutil.copytree(self._rose_suite_branch, self.suite_destination)
        else:
            self.logger.info('Checking out rose suite {0._convert_suite} from ({0._rose_suite_branch}) '
                             'to {0.suite_destination}'.format(self))
            try:
                output = workflow_interface.checkout_url(self.rose_suite_svn_location, self.suite_destination)
            except workflow_interface.SuiteCheckoutError as err:
                self.logger.exception(err)
            else:
                self.logger.info('Suite checkout to {} succeeded'.format(self.suite_destination))
                self.logger.info('SVN version: {}'.format(output.split('\n')[0]))
        self._last_suite_stage_completed = 'checkout'

    @property
    def request_id(self) -> str:
        """
        Get the |request identifier| for the package currently being processed.

        :return: The |request identifier| for the current package.
        :rtype: str
        """
        return self._request.common.workflow_basename

    @property
    def streams(self) -> List[str]:
        """
        Return a list of the |streams| to process. This is determined by the streams in the stream info section
        of the JSON request file. If the user has specified streams on the command line, only return streams that
        are both in the request file and specified by the user.

        :return: List of the |streams| to process
        :rtype: List[str]
        """
        streams_to_process = self._get_streams_list()

        # Check if the user specified which streams to process
        if self._streams_requested:
            rejected_streams_cli = [stream for stream in self._streams_requested if stream not in streams_to_process]
            if rejected_streams_cli:
                self.logger.info(
                    'The following streams were specified on the command line, but will not be processed '
                    'because they are not present in the JSON request file:\n{stream_list}'
                    ''.format(stream_list=' '.join(rejected_streams_cli))
                )
            rejected_streams_request = [
                stream for stream in streams_to_process if stream not in self._streams_requested
            ]
            if rejected_streams_request:
                self.logger.info(
                    'The following streams are present in the JSON request file, but will not be processed '
                    'because they were not specified on the command line :\n{stream_list}'
                    ''.format(stream_list=' '.join(rejected_streams_request))
                )
            streams_to_process = [stream for stream in streams_to_process if stream in self._streams_requested]
        return streams_to_process

    @property
    def active_streams(self) -> List[str]:
        """
        Returns a list of the active |streams| to process, which are |streams| that have been checked and
        have conversions to be done. This is only valid after the __init__ function has run.

        :return: List of the active |streams| to process
        :rtype: List[str]
        """
        try:
            active_streams = list(self.stream_components.keys())
        except AttributeError:
            active_streams = []
        return active_streams

    @property
    def inactive_streams(self) -> Set[str]:
        """
        Return a list of the inactive |streams|, which will not be processed as they have no work to do.

        :return: List of the inactive |streams|
        :rtype: List[str]
        """
        return set(self.streams) - set(self.active_streams)

    def _get_streams_list(self) -> List[str]:
        """
        Returns a dict with useful streams related information extracted from
        the request object.

        Returns
        -------
        Returns a dict with useful streams related information extracted from
        the request object.
        """
        return self._request.data.streams

    def run_bounds(self) -> Tuple[TimePoint, TimePoint]:
        """
        Create start and end dates from the dates given in the request.json

        :return: A tuple of TimePoint Objects
        :rtype: Tuple
        """
        return self._request.data.start_date, self._request.data.end_date

    def final_cycle_point(self, stream) -> TimePoint:
        """
        Calulate the final cycling point for use in the cdds_convert processing suite for
        this particular stream.

        :param stream: Stream
        :type str:
        :return: A TimePoint object representing the final cycle point of processing. (This
            will almost always be an earlier point in time than the processing end_date.)
        :rtype: TimePoint
        """
        # See issue 224 metomi.isodatetime as to why this conditional logic exists.
        _, end_date = self.run_bounds()
        cycling_frequency = self._cycling_frequency(stream)
        recurrence = TimeRecurrenceParser().parse(f'R/{self.ref_date}/{cycling_frequency}')
        if recurrence.get_is_valid(end_date):
            final_cycle_point = recurrence.get_prev(end_date)
        else:
            final_cycle_point = recurrence.get_prev(recurrence.get_first_after(end_date))

        return final_cycle_point

    @property
    def ref_date(self) -> TimePoint:
        """
        Obtain the reference date for this |simulation| (i.e. the date it
        started). This is used for chunking output in the concatenation
        stages of the suite.

        :return: The reference date in the form 18500101
        :rtype: TimePoint
        """
        return self._request.metadata.base_date

    def _build_stream_components(self) -> None:
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
        cfg_dir = component_directory(self._request, 'configure')

        regex_streams = SECTION_TEMPLATE.format(
            stream_id='(?P<stream_id>[^_]+)',
            substream='(_(?P<substream>[^_]+))?')
        pattern_streams = re.compile(regex_streams)
        pattern_files = re.compile(self._arguments.user_config_template_name.format(r'(?P<grid_id>[\w\-]+)'))

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

    def cycling_overrides(self) -> Dict[str, str]:
        """
        Return the dictionary of cycling overrides constructed from
        the command line argument.

        :return: A dictionary of stream overrides.
        :rtype: dict
        """
        cycle_overrides = {}
        for entry in self._request.conversion.override_cycling_frequency:
            stream, frequency = entry.split('=')
            cycle_overrides[stream] = frequency
        return cycle_overrides

    def _cycling_frequency(self, stream: str) -> str:
        """
        Obtain the cycling frequency for this model and stream from the configs after applying any
        command line overrides.
        If the default cycling frequency from the config .json has a longer duration than the run bounds,
        a default duration of P1Y is used.

        :param stream: |stream identifier| to calculate value for.
        :type stream: str
        :return: Cycling frequency configuration information, a string representing the number of years
            formatted for cylc.
        :rtype: str
        """
        logger = logging.getLogger()
        cycle_length = self._model_params.cycle_length(stream)

        cycle_freq_exceeds_run_bounds, new_cycling_freq = self._check_cycle_freq_exceeds_run_bounds(cycle_length)

        overrides = self.cycling_overrides()
        if stream in overrides:
            frequency = overrides[stream]
            logger.info('Overriding cycling frequency for stream "{}": "{}" -> "{}"'
                        ''.format(stream, cycle_length, frequency))
            return frequency
        elif cycle_freq_exceeds_run_bounds:
            logger.info('Default cycling frequency "{}" for stream "{}" is greater than run bounds.'
                        'Using "{}" as the cycling frequency instead'.format(cycle_length, stream, new_cycling_freq))
            return new_cycling_freq
        else:
            return cycle_length

    def _check_cycle_freq_exceeds_run_bounds(self, cycle_frequency: str) -> Tuple[bool, Union[str, None]]:
        """
        If the given `cycle_frequency` is larger than the run bounds then a tuple is returned
        where the first value is a bool of True and the second value is an appropriate new cycling
        frequency, otherwise (False, True) is returned.

        :param cycle_frequency: The default cycling frequency as a duration string e.g. P5Y
        :type cycle_frequency: str
        :raises RuntimeError: If an invalid cycle frequency is given.
        :return: Whether the cycle_frequency does exceed bounds and the new cycling frequency.
        :rtype: tuple (bool, str or None)
        """
        start_date, end_date = self.run_bounds()

        if not re.match(r'P\d+[DMY]', cycle_frequency):
            raise RuntimeError('Unrecognised cycle frequency duration.')

        if start_date + DurationParser().parse(cycle_frequency) > end_date:
            if start_date + DurationParser().parse('P1Y') > end_date:
                return True, 'P1M'
            else:
                return True, 'P1Y'
        else:
            return False, None

    def _cycling_frequency_value(self, stream: str) -> Tuple[int, str]:
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
            r'P(?P<{0}>[\d]+)(?P<{1}>[DMY])'.format(value_group_name,
                                                    unit_group_name))
        freq_str = self._cycling_frequency(stream)
        matches = pattern.search(freq_str)
        # Extract the values for each item in the relevant section of the
        # config file.
        unit = matches.group(unit_group_name)
        cycle_length = int(matches.group(value_group_name))
        return (cycle_length, unit)

    @property
    def input_model_run_length(self) -> int:
        """
        Get the length in years of the input model run that is being processed.

        :return: The length of the input model run in years.
        :rtype: int
        """
        start_date, end_date = self.run_bounds()
        start_year, end_year = start_date.year, end_date.year
        return end_year - start_year

    def _calculate_concat_task_periods(self) -> None:
        self._calculate_max_concat_period()

        self._concat_task_periods_years = {
            stream: int(self.max_concat_period)
            for stream in self.active_streams
        }
        self._concat_task_periods_cylc = {
            stream: 'P{years}Y'.format(years=years)
            for stream, years
            in self._concat_task_periods_years.items()}

    def _calculate_max_concat_period(self) -> None:
        """
        Calculate the maximum concatenation window size in years for this run.
        This represents the longest period of data that will be stored in a
        single output file.
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

    def _first_concat_cycle_offset(self, stream: str) -> str:
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
            start_date, _ = self.run_bounds()
            concat_period = self._concat_task_periods_cylc[stream]
            aligned_concatenation_dates = TimeRecurrenceParser().parse(f'R/{self.ref_date}/{concat_period}')
            concat_window_date = aligned_concatenation_dates.get_first_after(start_date)
            cycling_frequency = self._cycling_frequency(stream)
            first_cycle = concat_window_date - DurationParser().parse(cycling_frequency)
            first_cycle = str(first_cycle - start_date)
        return first_cycle

    def _convert_alignment_cycle_needed(self, stream: str) -> bool:
        """
        Calculates for this stream whether a shortened mip_convert cycle is
        needed at the start of the run to align subsequent cycles with the
        reference date. We want cycles to happen on years where:
        cycle_year = reference_year + n * cycle_period. Where this is not true
        for the start year of the run, a short alignment cycle is necessary.

        :param stream: The |stream identifier| to calculate the value for.
        :type stream: str
        :return: Is stream is a shortened mip_covert cycle is needed (offset != P0D)
        :rtype: bool
        """
        return 'P0D' != self._convert_alignment_cycle_offset(stream)

    def _convert_alignment_cycle_offset(self, stream: str) -> str:
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

    def _final_concatenation_needed(self, stream: str) -> bool:
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

    def _final_concatenation_cycle(self, stream) -> str:
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
        final_cycle_point = self.final_cycle_point(stream)
        final_concatenation_cycle_in_days = str(final_cycle_point - start_date)
        return final_concatenation_cycle_in_days

    def _final_concatenation_window_start(self, stream) -> Union[str, int]:
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
        if recurrence.get_is_valid(end_date):
            final_concat_windows_start_year = str(recurrence.get_prev(end_date))
        else:
            final_concat_windows_start_year = str(recurrence.get_prev(recurrence.get_first_after(end_date)))

        return final_concat_windows_start_year

    def _single_concatenation_cycle(self, stream: str) -> bool:
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
        window_size = DurationParser().parse(self._concat_task_periods_cylc[stream])
        start_date, end_date = self.run_bounds()
        return start_date + window_size >= end_date

    def mip_convert_temp_sizes(self, stream_id: str) -> int:
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

    def validate_streams(self) -> None:
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

    def _update_suite_rose_suite_conf(self, location: str) -> None:
        """
        Update the rose-suite.conf file with suite level settings that are the same for all streams.
        Stream specific settings will be set trhough stream-specific optional config files
        (see _update_suite_opt_conf).

        :param location: The platform on which to run the tasks in the suite.
        :type location: str
        """
        section_name = 'template variables'
        rose_suite_conf_file = os.path.join(self.suite_destination, 'rose-suite.conf')
        start_date, end_date = self.run_bounds()
        # In order to run subtasks in the convert suite (extract, QC and transfer), the suite needs to know
        # the path to the request cfg file. This path is often specified as a relative path, so we need to
        # get the absolute path if this is the case to pass to the suite config.
        if os.path.isabs(self._arguments.request_path):
            request_cfg_path = self._arguments.request_path
        else:
            request_cfg_path = os.path.abspath(self._arguments.request_path)

        use_external_plugin = False
        external_plugin = ''
        external_plugin_location = ''
        if self._request.common.external_plugin:
            use_external_plugin = True
            external_plugin = self._request.common.external_plugin
            external_plugin_location = self._request.common.external_plugin_location

        changes_to_apply_all = {
            'MIP_ERA': self._request.metadata.mip_era,
            'CDDS_CONVERT_PROC_DIR': component_directory(self._request, 'convert'),
            'CDDS_VERSION': _NUMERICAL_VERSION,
            'CALENDAR': self._request.metadata.calendar,
            'DEV_MODE': _DEV,
            'END_DATE': str(end_date),
            'MODEL_PARAMS_DIR': self._request.conversion.model_params_dir,
            'INPUT_DIR': input_data_directory(self._request),
            'OUTPUT_MASS_ROOT': self._request.data.output_mass_root,
            'OUTPUT_MASS_SUFFIX': self._request.data.output_mass_suffix,
            'EMAIL_NOTIFICATIONS': not self._request.conversion.no_email_notifications,
            'MIP_CONVERT_CONFIG_DIR': component_directory(self._request, 'configure'),
            'MODEL_ID': self._request.metadata.model_id,
            'NTHREADS_CONCATENATE': (NTHREADS_CONCATENATE),
            'OUTPUT_DIR': output_data_directory(self._request),
            'PARALLEL_TASKS': PARALLEL_TASKS,
            'REF_DATE': str(self.ref_date),
            'REQUEST_CONFIG_PATH': request_cfg_path,
            'ROOT_DATA_DIR': self._request.common.root_data_dir,
            'ROOT_PROC_DIR': self._request.common.root_proc_dir,
            'RUN_EXTRACT': not self.skip_extract,
            'RUN_EXTRACT_VALIDATION': not self.skip_extract_validation,
            'RUN_QC': not self.skip_qc,
            'RUN_TRANSFER': not self.skip_transfer,
            'START_DATE': str(start_date),
            'TARGET_SUITE_NAME': self.target_suite_name,
            'USE_EXTERNAL_PLUGIN': use_external_plugin,
            'RELAXED_CMOR': self._request.common.is_relaxed_cmor(),
            'CONTINUE_IF_MIP_CONVERT_FAILED': self._request.conversion.continue_if_mip_convert_failed
        }
        if use_external_plugin:
            changes_to_apply_all['EXTERNAL_PLUGIN'] = external_plugin
            changes_to_apply_all['EXTERNAL_PLUGIN_LOCATION'] = external_plugin_location

        if 'CDDS_DIR' in os.environ:
            changes_to_apply_all['CDDS_DIR'] = os.environ['CDDS_DIR']
        else:
            self.logger.info('Environment variable CDDS_DIR not found. Skipping interpolation into rose suite')
        if location:
            changes_to_apply_all['LOCATION'] = location

        try:
            changes_applied = workflow_interface.update_suite_conf_file(rose_suite_conf_file, section_name,
                                                                        changes_to_apply_all, raw_value=False)
        except Exception as err:
            self.logger.exception(err)
            raise err
        else:
            self.logger.info('Update to rose-suite.conf successful. '
                             'Changes made: "{}"'
                             ''.format(repr(changes_applied)))

    def _get_required_memory(self, stream: str) -> Dict[str, str]:
        components = self.stream_components
        required_memory = {c: self._model_params.memory(stream) for c in components[stream]}
        # Scale memory limits if included on command line
        if self._request.conversion.scale_memory_limits:
            required_memory = {
                component: scale_memory(mem_limit, self._request.conversion.scale_memory_limits)
                for component, mem_limit in required_memory.items()
            }

        return required_memory

    def _update_suite_opt_conf(self, stream: str) -> None:
        """
        Gather together the per stream settings and update the stream specific
        config file in opt/rose-suite-<stream>.conf.

        Parameters
        ----------
        stream: str
            |stream identifier| to calculate value for.

        """
        section_name = 'template variables'
        components = self.stream_components
        template_path = os.path.join(self.suite_destination, 'opt', 'rose-suite-stream.conf')
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
            'CONCATENATION_FIRST_CYCLE_OFFSET': self._first_concat_cycle_offset(stream),
            'CONCATENATION_WINDOW': self._concat_task_periods_cylc[stream],
            'CONVERT_ALIGNMENT_OFFSET': self._convert_alignment_cycle_offset(stream),
            'CYCLING_FREQUENCY': self._cycling_frequency(stream),
            'DO_CONVERT_ALIGNMENT_CYCLE': self._convert_alignment_cycle_needed(stream),
            'DO_FINAL_CONCATENATE': self._final_concatenation_needed(stream),
            'FINAL_CONCATENATION_CYCLE': self._final_concatenation_cycle(stream),
            'FINAL_CONCATENATION_WINDOW_START': self._final_concatenation_window_start(stream),
            'FINAL_CYCLE_POINT': str(self.final_cycle_point(stream)),
            'MEMORY_CONVERT': required_memory,
            'MIP_CONVERT_TMP_SPACE': self.mip_convert_temp_sizes(stream),
            'SINGLE_CONCATENATION_CYCLE': self._single_concatenation_cycle(stream),
            'STREAM_COMPONENTS': components[stream],
            'STREAM_SUBSTREAMS': self.substreams_dict[stream],
        }

        try:
            changes_applied = workflow_interface.update_suite_conf_file(stream_opt_conf_path, section_name,
                                                                        changes_to_appy_per_stream, raw_value=False)
        except Exception as err:
            self.logger.exception(err)
        else:
            self.logger.info(
                'Update to {0} successful. Changes made: "{1}"'.format(stream_opt_conf_path, repr(changes_applied))
            )

    @property
    def target_suite_name(self) -> str:
        """
        Return the name of the target suite.

        Returns
        -------
        : str
            Name of the target suite, e.g. "u-ar050".
        """
        return self._request.data.model_workflow_id

    def update_convert_workflow_parameters(self, location: str = None) -> None:
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

    def submit_workflow(self, **kwargs) -> None:
        """_summary_

        :raises err: _description_
        """
        assert self._last_suite_stage_completed == 'update'
        self.logger.info('Submitting workflow located in {}'.format(self.suite_destination))
        try:
            result = workflow_interface.run_workflow(self.suite_destination, **kwargs)
            self.logger.info('Workflow submitted successfully')
            self.logger.info('Workflow standard output:\n {}'.format(result))
        except workflow_interface.WorkflowSubmissionError as err:
            self.logger.error('Workflow submission failed: {}'.format(err))
            raise err
