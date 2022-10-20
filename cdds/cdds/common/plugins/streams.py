# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`streams` module contains the code required to
handle stream information for all supported streams.
"""
import logging

from dataclasses import dataclass, field
from datetime import datetime
from abc import ABCMeta, abstractmethod
from typing import Tuple, List, Dict


@dataclass
class StreamAttributes:
    """
    Represents the attributes of a stream. Currently supported:
        * name of stream
        * start date of stream
        * end date of stream
    """
    stream: str
    start_date: datetime
    end_date: datetime


@dataclass
class StreamFileFrequency:
    """
    Represents the frequency of files for a stream:
        * frequency (e.g. monthly, daily, ...)
        * name of the stream
        * files per year
    """
    frequency: str = ""
    stream: str = ""
    file_per_year: int = 0
    file_size_in_days: int = 0


@dataclass
class StreamFileInfo:
    """
    Represents the information for stream files. It stores information of
    the file frequencies of streams.
    """
    file_frequencies: Dict[str, StreamFileFrequency] = field(default_factory=dict)

    def get_files_per_year(self, stream: str) -> int:
        """
        Calculates how many files of input data are expected per year for a particular stream.

        :param stream: The name of the stream to get the number of files for
        :type stream: str
        :return: Number of files per year for the specified stream
        :rtype: int
        """
        return self.file_frequencies[stream].file_per_year

    def get_file_size_in_days(self, stream: str) -> int:
        """
        Calculates the temporal size of the file in days for a particular stream.

        :param stream: The name of the stream to get the number of files for
        :type stream: str
        :return: Temporal size of the file in days
        :rtype: int
        """
        return self.file_frequencies[stream].file_size_in_days

    def calculate_expected_number_of_files(self, stream_attributes: StreamAttributes, substreams: List[str]) -> int:
        """
        Calculates expected number of files in a particular stream

        :param stream_attributes: Attributes of the stream containing stream name, start date and end date
        :type stream_attributes: StreamAttributes
        :param substreams: List of sub streams
        :type substreams: List[str]
        :return: Expected number of files
        :rtype: int
        """
        years = stream_attributes.end_date.year - stream_attributes.start_date.year
        months = stream_attributes.end_date.month - stream_attributes.start_date.month

        files_per_year = self.get_files_per_year(stream_attributes.stream)
        files_size_in_days = self.get_file_size_in_days(stream_attributes.stream)
        expected_files = ((years * 12 + months) / 12.0 * files_per_year * len(substreams))

        if files_per_year == 360:
            expected_files = expected_files + 1
        return int(expected_files)


class StreamInfo(object, metaclass=ABCMeta):
    """
    Abstract class to store the stream information data.
    """

    @abstractmethod
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
        pass


class StreamStore(object, metaclass=ABCMeta):
    """
    Singleton class to store the stream information data.

    The class is a singleton to avoid excessive loading of model parameters
    that can be stored in files or otherwise.
    """
    _instance = None

    def __init__(self) -> None:
        if StreamStore._instance is not None:
            raise Exception('Class is a singleton and can not initialised twice!')
        self._logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def instance(cls) -> 'StreamStore':
        """
        Returns the class instance. If none is created, yet, a new instance will
        be created and stored (see Singleton pattern).

        :return: The instance of StreamStore
        :rtype: StreamStore
        """
        if cls._instance is None:
            cls._instance = cls.create_instance()
        return cls._instance

    @classmethod
    @abstractmethod
    def create_instance(cls) -> 'StreamStore':
        """
        Creates a new instance of the class.

        :return: New class instance
        :rtype: StreamStore
        """
        pass

    @classmethod
    def clean_instance(cls) -> None:
        """
        Set class instance to none and allow re-creating a new class instance.

        Only used in tests! Do not use in productive code!
        """
        cls._instance = None

    @abstractmethod
    def get(self) -> StreamInfo:
        """
        Returns the stream information data.

        :return: Class containing stream information
        :rtype: StreamInfo
        """
        pass
