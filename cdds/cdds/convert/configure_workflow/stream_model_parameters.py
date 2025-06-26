# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
import logging

from metomi.isodatetime.parsers import DurationParser
from metomi.isodatetime.data import Duration

from cdds.common.plugins.plugins import PluginStore
from cdds.common.request.request import Request
from cdds.convert.configure_workflow.stream_components import StreamComponents
from cdds.convert.process.memory import scale_memory


class StreamModelParameters:
    def __init__(self, request: Request, stream: str, components: StreamComponents):
        """Class for extracting model parameter information for the given stream.

        :param request: A Request class.
        :type request: Request
        :param stream: The stream to retrieve model parametr information for.
        :type stream: str
        :param components: The grid and substream information.
        :type components: StreamComponents
        """
        self._request = request
        self.stream = stream
        self.stream_components = components.stream_components
        self.stream_substreams = components.stream_substreams
        self._plugin = PluginStore.instance().get_plugin()
        self._model_params = self._plugin.models_parameters(self._request.metadata.model_id)
        self.logger = logging.getLogger()

    def concatenation_period(self) -> Duration:
        """
        Calculate the maximum concatenation window size in years for this model.
        This represents the longest period of data that will be stored in a
        single output file.

        :return: The concatenation period to be used for the given self.stream
        :rtype: Duration
        """
        model_sizing = self._model_params.full_sizing_info()

        if model_sizing is None or model_sizing == {}:
            max_concat_period = 10
        else:
            concatenation_periods = []
            for data_dims in model_sizing.values():
                concatenation_periods += list(data_dims.values())
            max_concat_period = max(concatenation_periods)  # type: ignore

        return Duration(years=max_concat_period)

    def cycling_frequency(self) -> Duration:
        """
        Obtain the cycling frequency for this model and stream from the configs after applying any
        command line overrides.

        :return: A isodatetime Duration representing the cycling frequency.
        :rtype: Duration
        """
        default_cycling_frequency = self._model_params.cycle_length(self.stream)

        cycle_overrides = {}
        for override in self._request.conversion.override_cycling_frequency:
            stream, frequency = override.split('=')
            cycle_overrides[stream] = frequency

        if self.stream in cycle_overrides.keys():
            cycling_frequency = cycle_overrides[self.stream]
            self.logger.info('Overriding cycling frequency for stream "{}": "{}" -> "{}"'
                             ''.format(stream, default_cycling_frequency, cycling_frequency))
            return DurationParser().parse(cycling_frequency)
        else:
            cycling_frequency = default_cycling_frequency

        cycling_frequency = DurationParser().parse(cycling_frequency)

        cycling_frequency = self.check_cycle_freq_exceeds_run_bounds(cycling_frequency)

        return cycling_frequency

    def check_cycle_freq_exceeds_run_bounds(self, cycle_frequency: Duration) -> Duration:
        """
        If the given `cycle_frequency` is larger than the run bounds then a new cycling
        frequency is returned that is smaller or equal to the run bounds durations.

        :param cycle_frequency: The default cycling frequency as a duration string e.g. P5Y
        :type cycle_frequency: Duration
        :return: A cycling frequency compatible with the run bounds.
        :rtype: Duration
        """
        start_date, end_date = self._request.data.start_date, self._request.data.end_date

        if start_date + cycle_frequency > end_date:
            if start_date + DurationParser().parse('P1Y') > end_date:
                return Duration(months=1)
            else:
                return Duration(years=1)

        return cycle_frequency

    @property
    def memory(self) -> dict[str, str]:
        """
        Return the required memory for this stream and apply any scaling if a scaling factor is provided.

        :return: The required memory for this stream.
        :rtype: dict[str, str]
        """
        required_memory = {c: self._model_params.memory(self.stream) for c in self.stream_components[self.stream]}
        scaling_factor = self._request.conversion.scale_memory_limits

        if scaling_factor:
            scaled_memory = {}
            for component, mem_limit in required_memory.items():
                scaled_memory[component] = scale_memory(mem_limit, scaling_factor)
            return scaled_memory
        else:
            return required_memory

    @property
    def mip_convert_temp_sizes(self) -> int:
        """The requested temporary memory for this stream.

        :return: The requested memory.
        :rtype: int
        """
        return self._model_params.temp_space(self.stream)

    def as_jinja2(self) -> dict:
        """A helper method that provides a dictionary with the needed jinja2 template variables.

        :return: A dictionary with Jinja2 template variables.
        :rtype: dict
        """
        return {
            'STREAMS': self.stream,
            'MEMORY_CONVERT': self.memory,
            'MIP_CONVERT_TMP_SPACE': self.mip_convert_temp_sizes,
            'STREAM_COMPONENTS': self.stream_components[self.stream],
            'STREAM_SUBSTREAMS': self.stream_substreams[self.stream],
        }
