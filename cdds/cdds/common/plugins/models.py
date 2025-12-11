# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`models` module contains the abstract classes required
to handle model parameters information.
"""
import logging

from abc import ABCMeta, abstractmethod
from typing import Dict, List

from cdds.common.plugins.common import LoadResults
from cdds.common.plugins.grid import GridInfo, GridType
from cdds.common.plugins.streams import StreamFileInfo
from cdds.common.plugins.grid_mapping import GridMapping


class ModelParameters(object, metaclass=ABCMeta):
    """Abstract class to store the parameters for a specific model."""

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Returns the model version

        Returns
        -------
        str
            Model version
        """
        pass

    @property
    @abstractmethod
    def data_request_version(self) -> str:
        """Returns the version of the data request for the model

        Returns
        -------
        str
            Data request version
        """
        pass

    @property
    @abstractmethod
    def um_version(self) -> str:
        """Returns the um version for the model

        Returns
        -------
        str
            Um version
        """
        pass

    @property
    @abstractmethod
    def halo_removal_info(self) -> dict:
        """Returns halo removal information for the model.

        Returns
        -------
        dict
            Halo removal info
        """
        pass

    @abstractmethod
    def grid_info(self, grid_type: GridType) -> GridInfo:
        """Returns the information for the grid with given type (atmosphere or ocean).

        Parameters
        ----------
        grid_type : GridType
            Type of the Grid

        Returns
        -------
        GridInfo
            Information of grid
        """
        pass

    @abstractmethod
    def streams(self) -> List[str]:
        pass

    @abstractmethod
    def temp_space(self, stream_id: str) -> int:
        """Returns the temporary space of the given stream.

        Parameters
        ----------
        stream_id : str
            Stream ID

        Returns
        -------
        int
            Temporary space of the stream
        """
        pass

    @abstractmethod
    def memory(self, stream_id: str) -> str:
        """Returns the memory of the given stream.

        Parameters
        ----------
        stream_id : str
            Stream ID

        Returns
        -------
        str
            Size of memory
        """
        pass

    @abstractmethod
    def cycle_length(self, stream_id: str) -> str:
        """Returns the cycle length of the given stream.

        Parameters
        ----------
        stream_id : str
            Stream ID

        Returns
        -------
        str
            Cycle length
        """
        pass

    @abstractmethod
    def sizing_info(self, frequency: str, shape: str) -> float:
        """Returns the sizing info for a specific period. The period is specified
        by the given frequency and shape coordinates.

        Parameters
        ----------
        frequency : str
            Frequency
        shape : str
            Shape coordinates

        Returns
        -------
        float
            The corresponding sizing info
        """
        pass

    @abstractmethod
    def full_sizing_info(self) -> Dict[str, Dict[str, float]]:
        """Returns all sizing information.

        Returns
        -------
        dict
            Sizing information
        """
        pass

    @abstractmethod
    def is_model(self, model_id: str) -> bool:
        """Returns if the current class represents the given model.

        Parameters
        ----------
        model_id : str
            Model ID to check

        Returns
        -------
        bool
            If given model is represent by the class or not
        """
        pass

    @abstractmethod
    def subdaily_streams(self) -> List[str]:
        """Returns a list of subdaily atmospheric streams.

        Returns
        -------
        List[str]
            Subdaily streams
        """
        pass

    @abstractmethod
    def all_ancil_files(self, root_directory: str) -> List[str]:
        """Returns the paths to all ancillary files of this model in the
        given root directory.

        Parameters
        ----------
        root_directory : str
            Path to root directory of the files

        Returns
        -------
        List[str]
            Paths to the ancillary files
        """
        pass

    @abstractmethod
    def all_ancil_variables(self) -> List[str]:
        """Returns all ancillary variables of this model that should
        be removed.

        Returns
        -------
        List[str]
            Ancillary variables
        """
        pass

    @abstractmethod
    def all_hybrid_heights_files(self, root_directory: str) -> List[str]:
        """Returns the paths to all hybrid heights files of this model in the
        given root directory.

        Parameters
        ----------
        root_directory : str
            Path to root directory of the files

        Returns
        -------
        List[str]
            Paths to the hybrid heights files
        """
        pass

    @abstractmethod
    def stream_file_info(self) -> StreamFileInfo:
        """Returns information about the stream files that the model supports.

        Returns
        -------
        StreamFileInfo
            Information about the stream files
        """
        pass

    @abstractmethod
    def grids_mapping(self) -> GridMapping:
        """Returns mapping information about the grids for the MIP requested variables.

        Returns
        -------
        GridMapping
            Grids mappings for the MIP requested variables
        """
        pass


class ModelsStore(object, metaclass=ABCMeta):
    """Singleton class to store for each model the corresponding parameters.

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
        """Returns the class instance. If none is created, yet, a new instance will
        be created and stored (see Singleton pattern).

        Returns
        -------
        ModelsStore
            The instance of ModelsStore
        """
        if cls._instance is None:
            cls._instance = cls.create_instance()
        return cls._instance

    @classmethod
    @abstractmethod
    def create_instance(cls) -> 'ModelsStore':
        """Creates a new instance of the class.

        Returns
        -------
        ModelsStore
            New class instance
        """
        pass

    @classmethod
    def clean_instance(cls) -> None:
        """Set class instance to none and allow re-creating a new class instance.

        Only used in tests! Do not use in productive code!
        """
        cls._instance = None

    @abstractmethod
    def overload_params(self, dir_path: str) -> LoadResults:
        """Overloads model parameters. The new parameters are specified in a json file in the given directory.
        The json file name should match a specific pattern, for example: <model-name>.json

        Parameters
        ----------
        dir_path : str
            Path to the directory

        Returns
        -------
        LoadResults
            Results containing which model values were overloaded
        """
        pass

    @abstractmethod
    def get(self, model_id: str) -> ModelParameters:
        """Returns the model parameters data for the given model.

        Parameters
        ----------
        model_id : str
            Model ID

        Returns
        -------
        ModelParameters
            Class containing the model parameters
        """
        pass
