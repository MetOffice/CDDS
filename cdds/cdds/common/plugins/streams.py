# (C) British Crown Copyright 2022-2023, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`streams` module contains the code required to
handle stream information for all supported streams.
"""
import logging

from dataclasses import dataclass, field
from datetime import datetime
from abc import ABCMeta, abstractmethod
from typing import Tuple, Dict


VALID_STREAM_FREQUENCIES = ['quarterly', 'monthly', '10 day', 'daily', 'hourly']


@dataclass
class StreamAttributes:
    """
    Represents the attributes of a stream. Currently supported:
        * name of stream
        * start date of stream
        * end date of stream
        * stream type (pp or nc)
    """
    stream: str
    start_date: datetime
    end_date: datetime
    streamtype: str

    def __init__(self, stream: str, start_date: datetime, end_date: datetime) -> None:
        self.stream = stream
        self.start_date = start_date
        self.end_date = end_date
        self.streamtype = 'pp' if stream.startswith('ap') else 'nc'


@dataclass
class StreamFileFrequency:
    """
    Represents the frequency of files for a stream:
        * frequency (e.g. monthly, daily, ...)
        * name of the stream
    """
    frequency: str = ""
    stream: str = ""

    def __post_init__(self):
        if self.frequency not in VALID_STREAM_FREQUENCIES:
            raise ValueError('The frequency of a stream must be one of {}.'.format(VALID_STREAM_FREQUENCIES))


@dataclass
class StreamFileInfo:
    """
    Represents the information for stream files. It stores information of
    the file frequencies of streams.
    """
    file_frequencies: Dict[str, StreamFileFrequency] = field(default_factory=dict)


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
