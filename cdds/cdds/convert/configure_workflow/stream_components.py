# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import collections
import glob
import logging
import os
import re
from typing import List

from cdds.common.cdds_files.cdds_directories import component_directory
from cdds.convert.constants import SECTION_TEMPLATE

from mip_convert.configuration.python_config import PythonConfig


class StreamComponents:
    def __init__(self, arguments, request):
        self._arguments = arguments
        self._request = request
        self._streams_requested = self._arguments.streams
        self.logger = logging.getLogger()

        self.build_stream_components()

    def build_stream_components(self) -> None:
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

    @property
    def streams(self) -> List[str]:
        """
        Return a list of the |streams| to process. This is determined by the streams in the stream info section
        of the JSON request file. If the user has specified streams on the command line, only return streams that
        are both in the request file and specified by the user.

        :return: List of the |streams| to process
        :rtype: List[str]
        """
        streams_to_process = self._request.data.streams

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
    def inactive_streams(self):
        """
        Return a list of the inactive |streams|, which will not be processed as they have no work to do.

        :return: List of the inactive |streams|
        :rtype: List[str]
        """
        return set(self.streams) - set(self.active_streams)
