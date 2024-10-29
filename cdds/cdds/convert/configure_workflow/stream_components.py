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

    def user_configs(self) -> dict[str, PythonConfig]:
        """Identify and parse the user configuration files.

        :raises FileNotFoundError: If no user configs are found.
        :return: Return a dictionary of {component:config} pairs.
        :rtype: dict[str, PythonConfig]
        """
        configure_directory = component_directory(self._request, "configure")
        pattern_files = re.compile(self._arguments.user_config_template_name.format(r"(?P<grid_id>[\w\-]+)"))
        user_configs = {}

        for item in glob.glob(os.path.join(configure_directory, "*")):
            match = pattern_files.match(os.path.basename(item))
            if match:
                substream_fname = match.group("grid_id")
                user_config = PythonConfig(item)
                user_configs[substream_fname] = user_config

        if not user_configs:
            msg = f"No configuration files were found in {configure_directory}"
            self.logger.critical(msg)
            raise FileNotFoundError(msg)

        return user_configs

    def build_stream_components(self) -> None:
        """_summary_
        """
        regex_streams = SECTION_TEMPLATE.format(
            stream_id="(?P<stream_id>[^_]+)", substream="(_(?P<substream>[^_]+))?"
        )
        pattern_streams = re.compile(regex_streams)

        self.stream_substreams = collections.defaultdict(dict)

        for component_fname, user_config in self.user_configs().items():
            streams_in_cfg = []
            for section in user_config.sections:
                section_match = pattern_streams.match(section)
                if section_match:
                    stream_id = section_match.group("stream_id")
                    substream = section_match.group("substream")
                    streams_in_cfg += [(stream_id, substream)]
            for stream, substream in streams_in_cfg:
                if not substream:
                    substream = ""
                self.stream_substreams[stream][component_fname] = substream

        self.stream_substreams = {
            k: v for k, v in self.stream_substreams.items() if k in self.streams
        }

        self.stream_components = {}
        for stream, components in self.stream_substreams.items():
            self.stream_components[stream] = list(components.keys())

    def validate_streams(self) -> None:
        """Ensure there are streams to process.

        :raises RuntimeError: If there are no streams to process.
        """
        if not self.active_streams:
            msg = "No streams to process"
            self.logger.error(msg)
            raise RuntimeError(msg)
        inactive_streams = set(self.streams) - set(self.active_streams)
        if inactive_streams:
            streams_str = ",".join(inactive_streams)
            msg = ("Warning: Skipping streams {streams_str} as there are no "
                   "variables to produce.".format(streams_str=streams_str))
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
            rejected_streams_cli = [
                stream
                for stream in self._streams_requested
                if stream not in streams_to_process
            ]
            if rejected_streams_cli:
                self.logger.info(
                    "The following streams were specified on the command line, but will not be processed "
                    "because they are not present in the JSON request file:\n{stream_list}"
                    "".format(stream_list=" ".join(rejected_streams_cli))
                )
            rejected_streams_request = [
                stream
                for stream in streams_to_process
                if stream not in self._streams_requested
            ]
            if rejected_streams_request:
                self.logger.info(
                    "The following streams are present in the JSON request file, but will not be processed "
                    "because they were not specified on the command line :\n{stream_list}"
                    "".format(stream_list=" ".join(rejected_streams_request))
                )
            streams_to_process = [
                stream
                for stream in streams_to_process
                if stream in self._streams_requested
            ]
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
