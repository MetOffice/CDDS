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
from typing import Dict, Any, Tuple

from cdds.common.io import read_json
from cdds.common.plugins.streams import StreamInfo, StreamStore


@dataclass
class StreamIdentifier:
    """
    Represents the streams for a MIP table. It contains:
        * name of the MIP table
        * the default supported stream
        * the overrides supported streams according MIP requested variables
    """
    mip_table: str = ""
    default_stream: str = ""
    overrides: Dict[str, str] = field(default_factory=dict)  # key: variable, value: stream

    def add_overrides(self, new_overrides: Dict[str, str]) -> None:
        """
        Add new overrides supported streams according MIP request variables

        :param new_overrides: New overrides (key: MIP request variable, value: stream)
        :type new_overrides: Dict[str, str]
        """
        self.overrides.update(new_overrides)

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
            return self.overrides.get(variable, self.default_stream)
        else:
            return self.default_stream


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
            self._streams: Dict[str, StreamIdentifier] = {}
            self._load_streams(configuration)
        else:
            raise BaseException("No stream config json file at path: {}".format(configuration_path))

    def _load_streams(self, configuration: Dict[str, Any]) -> None:
        """
        Loads and extracts information of the stream of the MIP tables from the given configuration dictionary.

        The configuration dictionary must contain a section <default> and <overrides>. The <default> section
        contains the default stream of a MIP table. The <overrides> section contains all streams that override
        the default stream of a MIP table for a specific variable.

        Example of a configuration dictionary:
        {
            "default": {
                "AERmon": "ap4",
                 "Amon": "ap5"
            },
            "overrides": {
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
        for mip_table, stream_overrides in configuration["overrides"].items():
            stream_id = self._streams.get(mip_table, StreamIdentifier(mip_table=mip_table))
            stream_id.add_overrides(stream_overrides)
            self._streams[mip_table] = stream_id

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
