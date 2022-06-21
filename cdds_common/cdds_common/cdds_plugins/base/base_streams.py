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
from typing import Dict, Any, Tuple, List

from cdds_common.common.io import read_json
from cdds_common.cdds_plugins.streams import StreamInfo, StreamStore, StreamAttributes


@dataclass
class StreamIdentifier:
    """
    Represents the streams for a MIP table. It contains:
        * name of the MIP table
        * the default supported stream
        * the optionals supported streams according MIP requested variables
    """
    mip_table: str = ""
    default_stream: str = ""
    optionals: Dict[str, str] = field(default_factory=dict)  # key: variable, value: stream

    def add_optionals(self, new_optionals: Dict[str, str]) -> None:
        self.optionals.update(new_optionals)

    def get_stream(self, variable: str = None) -> str:
        """
        Return the supported stream for the given MIP requested variable. If the MIP requested variable
        is NONE, the default stream is returned.

        :param variable: MIP requested variable
        :type variable: str
        :return: The stream for the MIP requested variable
        :rtype: str
        """
        if variable:
            return self.optionals.get(variable, self.default_stream)
        else:
            return self.default_stream


@dataclass
class StreamLength:
    """
    Represents the length of a stream. The length can vary between
    low resolution and high resolution.
    """
    stream: str = ""
    low_resolution: int = 0
    high_resolution: int = 0

    def length(self, is_high_resolution=False) -> int:
        """
        Returns the length of the stream for the given resolution.

        :param is_high_resolution: If true, high resolution is considered otherwise low resolution
        :type is_high_resolution: bool
        :return: length of stream
        :rtype: int
        """
        return self.high_resolution if is_high_resolution else self.low_resolution


class BaseStreamInfo(StreamInfo, metaclass=ABCMeta):
    """
    Abstract class to store the information for a stream.
    The information of a stream are defined in a json file.

    The class loads the information from a json in a specific location.
    The json contains all necessary stream information.
    """

    def __init__(self, configuration_path: str) -> None:
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
        """
        Loads and extracts information of the stream lengths from the given configuration dictionary.

        The configuration dictionary must contain a section <stream_length> that contains the desired
        information. The section <stream_length> contains of dictionaries where each dictionary represent
        a single stream length. The key specifies the name of the stream and the values <low_resolution> and
        <high_resolution> specify the length of the stream according the given resolution.

        Example of a configuration dictionary:
        {
            "stream_length": {
                "ap4": {
                    "low_resolution": 12,
                    "high_resolution": 12
                },
                "ap5": {
                    "low_resolution": 12,
                    "high_resolution": 12
                }
            }
        }

        :param configuration: Configuration dictionary
        :type configuration: Dict[str, Any]
        """
        for stream, lengths in configuration["stream_length"].items():
            stream_length = StreamLength(stream=stream,
                                         low_resolution=lengths["low_resolution"],
                                         high_resolution=lengths["high_resolution"])
            self._stream_lengths[stream] = stream_length

    def _load_streams(self, configuration: Dict[str, Any]) -> None:
        """
        Loads and extracts information of the stream of the MIP tables from the given configuration dictionary.

        The configuration dictionary must contain a section <default> and <optionals>. The <default> section
        contains the default stream of a MIP table. The <optionals> section contains all streams that override
        the default stream of a MIP table for a specific variable.

        Example of a configuration dictionary:
        {
            "default": {
                "AERmon": "ap4",
                 "Amon": "ap5"
            },
            "optionals": {
                "AERmon": {
                        "tntrl": "apu"
                },
                "Amon": {
                    "tasmax": "ap6",
                    "tasmin": "ap6"
                }
            }
        }

        :param configuration: Configuration dictionary
        :type configuration: Dict[str, Any]
        """
        for mip_table, stream_default in configuration["default"].items():
            self._streams[mip_table] = StreamIdentifier(mip_table=mip_table, default_stream=stream_default)
        for mip_table, stream_optionals in configuration["optionals"].items():
            stream_id = self._streams.get(mip_table, StreamIdentifier(mip_table=mip_table))
            stream_id.add_optionals(stream_optionals)
            self._streams[mip_table] = stream_id

    def get_files_per_year(self, stream: str, high_resolution: bool = False) -> int:
        """
        Calculates how many files of input data are expected per year for a particular stream.

        :param stream: The name of the stream to get the number of files for
        :type stream: str
        :param high_resolution: True if processing high resolution model data
        :type high_resolution: bool
        :return: Number of files per year for the specified stream
        :rtype: int
        """
        return self._stream_lengths[stream].length(high_resolution)

    def calculate_expected_number_of_files(
            self, stream_attributes: StreamAttributes, substreams: List[str], high_resolution: bool = False
    ) -> int:
        """
        Calculates expected number of files in a particular stream

        :param stream_attributes: Attributes of the stream containing stream name, start date and end date
        :type stream_attributes: StreamAttributes
        :param substreams: List of sub streams
        :type substreams: List[str]
        :param high_resolution: True if processing high resolution model data
        :type high_resolution: bool
        :return: Expected number of files
        :rtype: int
        """
        years = stream_attributes.end_date.year - stream_attributes.start_date.year
        months = stream_attributes.end_date.month - stream_attributes.start_date.month

        files_per_year = self.get_files_per_year(stream_attributes.stream, high_resolution)
        expected_files = ((years * 12 + months) / 12.0 * files_per_year * len(substreams))
        return int(expected_files)

    def retrieve_stream_id(self, variable: str, mip_table: str) -> Tuple[str, str]:
        """
        Returns the stream and its sub streams of the MIP table for the given MIP requested variable.
        If no stream is found, ``unknown`` is returned.

        :param variable: MIP requested variable
        :type variable: str
        :param mip_table: The MIP table that streams should be considered
        :type mip_table: str
        :return: Tuple of stream and substream of the MIP table for the MIP requestd variable
        :rtype: Tuple[str, str]
        """
        try:
            stream = self._streams[mip_table].get_stream(variable)
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
    """
    Singleton class to store for each stream the corresponding stream information.

    The class is a singleton to avoid excessive loading of the information.
    """

    def __init__(self, stream_info: BaseStreamInfo) -> None:
        super(BaseStreamStore, self).__init__()
        self._stream_info = stream_info

    def get(self) -> BaseStreamInfo:
        """
        Returns the stored stream information data.

        :return: Class containing the stream information
        :rtype: BaseStreamInfo
        """
        return self._stream_info
