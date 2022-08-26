# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`models` module contains the abstract classes required
to handle model parameters information.
"""
import logging

from abc import ABCMeta, abstractmethod
from typing import Dict, List

from cdds_common.cdds_plugins.common import LoadResults
from cdds_common.cdds_plugins.grid import GridInfo, GridType
from cdds_common.cdds_plugins.streams import StreamFileInfo


class ModelParameters(object, metaclass=ABCMeta):
    """
    Abstract class to store the parameters for a specific model.
    """

    @property
    @abstractmethod
    def model_version(self) -> str:
        """
        Returns the model version

        :return: Model version
        :rtype: str
        """
        pass

    @property
    @abstractmethod
    def data_request_version(self) -> str:
        """
        Returns the version of the data request for the model

        :return: Data request version
        :rtype: str
        """
        pass

    @property
    @abstractmethod
    def um_version(self) -> str:
        """
        Returns the um version for the model

        :return: Um version
        :rtype: str
        """
        pass

    @abstractmethod
    def grid_info(self, grid_type: GridType) -> GridInfo:
        """
        Returns the information for the grid with given type (atmosphere or ocean).

        :param grid_type: Type of the Grid
        :type grid_type: GridType
        :return: Information of grid
        :rtype: GridInfo
        """
        pass

    @abstractmethod
    def temp_space(self, stream_id: str) -> int:
        """
        Returns the temporary space of the given stream.

        :param stream_id: Stream ID
        :type stream_id: str
        :return: Temporary space of the stream
        :rtype: int
        """
        pass

    @abstractmethod
    def memory(self, stream_id: str) -> str:
        """
        Returns the memory of the given stream.

        :param stream_id: Stream ID
        :type stream_id: str
        :return: Size of memory
        :rtype: str
        """
        pass

    @abstractmethod
    def cycle_length(self, stream_id: str) -> str:
        """
        Returns the cycle length of the given stream.

        :param stream_id: Stream ID
        :type stream_id: str
        :return: Cycle length
        :rtype: str
        """
        pass

    @abstractmethod
    def sizing_info(self, frequency: str, shape: str) -> float:
        """
        Returns the sizing info for a specific period. The period is specified
        by the given frequency and shape coordinates.

        :param frequency: Frequency
        :type frequency: str
        :param shape: Shape coordinates
        :type shape: str
        :return: The corresponding sizing info
        :rtype: float
        """
        pass

    @abstractmethod
    def full_sizing_info(self) -> Dict[str, Dict[str, float]]:
        """
        Returns all sizing information.

        :return: Sizing information
        :rtype: dict
        """
        pass

    @abstractmethod
    def is_model(self, model_id: str) -> bool:
        """
        Returns if the current class represents the given model.

        :param model_id: Model ID to check
        :type model_id: str
        :return: If given model is represent by the class or not
        :rtype: bool
        """
        pass

    @abstractmethod
    def subdaily_streams(self) -> List[str]:
        """
        Returns a list of subdaily atmospheric streams.

        :return: Subdaily streams
        :rtype: dict
        """
        pass

    def all_ancil_files(self, root_directory: str) -> List[str]:
        """
        Returns the paths to all ancillary files of this model in the
        given root directory.

        :param root_directory: Path to root directory of the files
        :type root_directory: str
        :return: Paths to the ancillary files
        :rtype: List[str]
        """
        pass

    def all_hybrid_heights_files(self, root_directory: str) -> List[str]:
        """
        Returns the paths to all hybrid heights files of this model in the
        given root directory.

        :param root_directory: Path to root directory of the files
        :type root_directory: str
        :return: Paths to the hybrid heights files
        :rtype: List[str]
        """
        pass

    @abstractmethod
    def stream_file_info(self) -> StreamFileInfo:
        pass


class ModelsStore(object, metaclass=ABCMeta):
    """
    Singleton class to store for each model the corresponding parameters.

    The class is a singleton to avoid excessive loading of model parameters
    that can be stored in files or otherwise.
    """

    _instance = None

    def __init__(self) -> None:
        if ModelsStore._instance is not None:
            raise Exception('Class is a singleton and can not initialised twice!')
        self._logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def instance(cls) -> 'ModelsStore':
        """
        Returns the class instance. If none is created, yet, a new instance will
        be created and stored (see Singleton pattern).

        :return: The instance of ModelsStore
        :rtype: ModelsStore
        """
        if cls._instance is None:
            cls._instance = cls.create_instance()
        return cls._instance

    @classmethod
    @abstractmethod
    def create_instance(cls) -> 'ModelsStore':
        """
        Creates a new instance of the class.

        :return: New class instance
        :rtype: ModelsStore
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
    def overload_params(self, dir_path: str) -> LoadResults:
        """
        Overloads model parameters. The new parameters are specified in a json file in the given directory.
        The json file name should match a specific pattern, for example: <model-name>.json

        :param dir_path: Path to the directory
        :type dir_path: str
        :return: Results containing which model values were overloaded
        :rtype: LoadResults
        """
        pass

    @abstractmethod
    def get(self, model_id: str) -> ModelParameters:
        """
        Returns the model parameters data for the given model.

        :param model_id: Model ID
        :type model_id: str
        :return: Class containing the model parameters
        :rtype: ModelParameters
        """
        pass
