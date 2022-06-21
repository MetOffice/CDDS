# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`streams` module contains the code required to
handle stream information for all supported streams.
"""
import logging

from dataclasses import dataclass
from datetime import datetime
from abc import ABCMeta, abstractmethod
from typing import Tuple, Any, List


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


class StreamInfo(object, metaclass=ABCMeta):
    """
    Abstract class to store the stream information data.
    """

    @abstractmethod
    def get_files_per_year(self, stream: str, high_resolution=False) -> int:
        """
        Calculates how many files of input data are expected per year for a particular stream.

        :param stream: The name of the stream to get the number of files for
        :type stream: str
        :param high_resolution: True if processing high resolution model data
        :type high_resolution: bool
        :return: Number of files per year for the specified stream
        :rtype: int
        """
        pass

    @abstractmethod
    def calculate_expected_number_of_files(
            self, stream_attributes: StreamAttributes, substreams: List[str], high_resolution=False
    ) -> int:
        """
        Calculates expected number of files in a particular stream

        :param stream_attributes: Attributes of the stream containing stream name, start date and end date
        :type stream_attributes: Any storing stream attributes
        :param substreams: List of sub streams
        :type substreams: List[str]
        :param high_resolution: True if processing high resolution model data
        :type high_resolution: bool
        :return: Expected number of files
        :rtype: int
        """
        pass

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
