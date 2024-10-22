# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import logging
from typing import Dict

from metomi.isodatetime.parsers import DurationParser

from cdds.common.plugins.plugins import PluginStore
from cdds.convert.process.memory import scale_memory


class StreamModelParameters:
    def __init__(self, request, stream, components):
        self._request = request
        self.stream = stream
        self.components = components.stream_components
        self.sub_streams = components.substreams_dict
        self._plugin = PluginStore.instance().get_plugin()
        self._model_params = self._plugin.models_parameters(self._request.metadata.model_id)
        self.logger = logging.getLogger()

    def concatenation_period(self) -> None:
        """
        Calculate the maximum concatenation window size in years for this run.
        This represents the longest period of data that will be stored in a
        single output file.
        """
        active_streams = [self.stream]
        model_sizing = self._model_params.full_sizing_info()
        if model_sizing is None or model_sizing == {}:
            max_concat_period = 10
        else:
            # get the max file length for all data dimensions for this model
            max_concat_period = max(max(
                output_length for data_dims, output_length in
                list(size_info.items())) for freq, size_info in list(model_sizing.items()))
        max_concat_period = max_concat_period

        _concat_task_periods_years = {
            stream: int(max_concat_period)
            for stream in active_streams
        }
        _concat_task_periods_cylc = {
            stream: 'P{years}Y'.format(years=years)
            for stream, years
            in _concat_task_periods_years.items()}

        return DurationParser().parse(_concat_task_periods_cylc[self.stream])

    def cycling_frequency(self):
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
        cycle_overrides = {}
        for entry in self._request.conversion.override_cycling_frequency:
            stream, frequency = entry.split('=')
            cycle_overrides[stream] = frequency

        cycle_length = self._model_params.cycle_length(self.stream)

        if self.stream in cycle_overrides.keys():
            frequency = cycle_overrides[self.stream]
            self.logger.info('Overriding cycling frequency for stream "{}": "{}" -> "{}"'
                        ''.format(stream, cycle_length, frequency))
            return DurationParser().parse(frequency)
        # elif cycle_freq_exceeds_run_bounds:
        #     # logger.info('Default cycling frequency "{}" for stream "{}" is greater than run bounds.'
        #     #             'Using "{}" as the cycling frequency instead'.format(cycle_length, stream, new_cycling_freq))
        #     return new_cycling_freq
        else:
            return DurationParser().parse(cycle_length)

    @property
    def memory(self) -> Dict[str, str]:
        required_memory = {c: self._model_params.memory(self.stream) for c in self.components[self.stream]}
        # Scale memory limits if included on command line
        if self._request.conversion.scale_memory_limits:
            required_memory = {
                component: scale_memory(mem_limit, self._request.conversion.scale_memory_limits)
                for component, mem_limit in required_memory.items()
            }

        return required_memory

    @property
    def mip_convert_temp_sizes(self) -> int:
        return self._model_params.temp_space(self.stream)

    def as_dict(self):
        return {
            'STREAMS': self.stream,
            'MEMORY_CONVERT': self.memory,
            'MIP_CONVERT_TMP_SPACE': self.mip_convert_temp_sizes,
            'STREAM_COMPONENTS': self.components[self.stream],
            'STREAM_SUBSTREAMS': self.sub_streams[self.stream],
        }
