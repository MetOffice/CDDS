# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`streams` module contains the code required to
handle stream information for all supported streams.
"""
import logging

from abc import ABCMeta, abstractmethod
from typing import Tuple


class StreamInfo(object, metaclass=ABCMeta):

    @abstractmethod
    def get_files_per_year(self, stream_id: str, highres=False) -> int:
        pass

    @abstractmethod
    def calculate_expected_number_of_files(self, stream, substreams, highres=False) -> int:
        pass

    @abstractmethod
    def retrieve_stream_id(self, variable_name: str, mip_table_id: str) -> Tuple[str, str]:
        pass


class StreamStore(object, metaclass=ABCMeta):
    _instance = None

    def __init__(self) -> None:
        if StreamStore._instance is not None:
            raise Exception('Class is a singleton and can not initialised twice!')
        self._logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def instance(cls) -> 'StreamStore':
        if cls._instance is None:
            cls._instance = cls.create_instance()
        return cls._instance

    @classmethod
    @abstractmethod
    def create_instance(cls) -> 'StreamStore':
        pass

    @classmethod
    def clean_instance(cls) -> None:
        cls._instance = None

    @abstractmethod
    def get(self) -> StreamInfo:
        pass
