# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`base_streams` module contains the code required to
handle basic model streams information for streams.
"""
import os
import re

from abc import ABCMeta
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Tuple, List

from cdds_common.common.io import read_json
from cdds_common.cdds_plugins.streams import StreamInfo, StreamStore


@dataclass
class StreamIdentifier:
    mip_table: str = ""
    default_stream: str = ""
    optionals: Dict[str, str] = field(default_factory=dict)  # key: variable, value: stream

    def add_optionals(self, new_optionals: Dict[str, str]) -> None:
        self.optionals.update(new_optionals)

    def get_stream(self, variable: str = None) -> str:
        if variable:
            return self.optionals.get(variable, self.default_stream)
        else:
            self.default_stream


@dataclass
class StreamLength:
    stream: str = ""
    low_resolution: int = 0
    high_resolution: int = 0

    def length(self, is_high_resolution=False):
        return self.high_resolution if is_high_resolution else self.low_resolution


@dataclass
class StreamAttributes:
    stream: str
    start_date: datetime
    end_date: datetime


class BaseStreamInfo(StreamInfo, metaclass=ABCMeta):

    def __init__(self, configuration_path: str):
        super(BaseStreamInfo, self).__init__()
        if os.path.exists(configuration_path):
            configuration = read_json(configuration_path)
            self._stream_lengths: Dict[str, StreamLength] = {}
            self._streams: Dict[str, StreamIdentifier] = {}
            self._load_stream_lengths(configuration)
            self._load_streams(configuration)
        else:
            raise BaseException("No stream config json file at path: {}".format(configuration_path))

    def _load_stream_lengths(self, configuration: Dict[str, Any]) -> None:
        for stream, lengths in configuration["stream_length"].items():
            stream_length = StreamLength(stream=stream,
                                         low_resolution=lengths["low_resolution"],
                                         high_resolution=lengths["high_resolution"])
            self._stream_lengths[stream] = stream_length

    def _load_streams(self, configuration: Dict[str, Any]) -> None:
        for mip_table, stream_default in configuration["default"].items():
            self._streams[mip_table] = StreamIdentifier(mip_table=mip_table, default_stream=stream_default)
        for mip_table, stream_optionals in configuration["optionals"].items():
            stream_id = self._streams.get(mip_table, StreamIdentifier(mip_table=mip_table))
            stream_id.add_optionals(stream_optionals)
            self._streams[mip_table] = stream_id

    def get_files_per_year(self, stream_id: str, highres: bool = False) -> int:
        return self._stream_lengths[stream_id].length(highres)

    def calculate_expected_number_of_files(
            self, stream_attributes: StreamAttributes, substreams: List[str], highres: bool = False
    ) -> int:
        years = stream_attributes.end_date.year - stream_attributes.start_date.year
        months = stream_attributes.end_date.month - stream_attributes.start_date.month

        files_per_year = self.get_files_per_year(stream_attributes.stream, highres)
        expected_files = ((years * 12 + months) / 12.0 * files_per_year * len(substreams))
        return int(expected_files)

    def retrieve_stream_id(self, variable_name: str, mip_table_id: str) -> Tuple[str, str]:
        try:
            stream = self._streams[mip_table_id].get_stream(variable_name)
        except KeyError:
            stream = 'unknown'

        stream_pattern = r'([\w]+)'
        substream_pattern = r'([\w-]+)'
        pattern = '{}/{}'.format(stream_pattern, substream_pattern)

        substream_search = re.match(pattern, stream)
        if substream_search is not None:
            stream, substream = substream_search.groups()[:2]
        else:
            substream = None
        return stream, substream


class BaseStreamStore(StreamStore, metaclass=ABCMeta):

    def __init__(self, stream_info: BaseStreamInfo) -> None:
        super(BaseStreamStore, self).__init__()
        self._stream_info = stream_info

    def get(self) -> StreamInfo:
        return self._stream_info
