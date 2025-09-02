# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`base_models` module contains the code required to
handle basic model parameters information for models.
"""
import os
import logging

from dataclasses import dataclass
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any, Dict, List

from cdds.common.enum_utils import ABCEnumMeta
from cdds.common.io import read_json
from cdds.common.plugins.common import LoadResult, LoadResults
from cdds.common.plugins.grid_mapping import GridMapping
from cdds.common.plugins.models import ModelParameters, ModelsStore
from cdds.common.plugins.base.base_grid import BaseGridInfo, AtmosBaseGridInfo, OceanBaseGridInfo
from cdds.common.plugins.base.base_grid_mapping import BaseGridMapping
from cdds.common.plugins.streams import StreamFileInfo, StreamFileFrequency
from cdds.common.plugins.grid import GridType


class ModelId(Enum, metaclass=ABCEnumMeta):
    """
    Represents the ID of a model.
    """

    @abstractmethod
    def get_json_file(self) -> str:
        """
        Returns the json file name for a model containing the model parameters data.

        :return: Json file name for the model with current ID
        :rtype: str
        """
        pass


@dataclass
class SizingInfo(object):
    """
    Represents the sizing information of a model and provides functions
    to extract data and update data.
    """

    DEFAULT_KEY = 'default'

    sizing_data: Dict[str, Dict[str, float]]

    def update(self, new_data: Dict[str, Dict[str, float]]) -> None:
        """
        Update the sizing information

        :param new_data: New data to add or update
        :type new_data: dict
        """
        self.sizing_data.update(new_data)

    def get_all(self) -> Dict[str, Dict[str, float]]:
        """
        Returns the whole sizing information as a dict.

        :return: Sizing information
        :rtype: dict
        """
        return self.sizing_data

    def get_period(self, frequency: str, coordinates: str) -> float:
        """
        Get period for given frequency and the shape with given coordinates.

        :param frequency: Frequency, for example monthly, daily
        :type frequency: str
        :param coordinates: Coordinates of the shape
        :type coordinates: str
        :return: Corresponding period
        :rtype: float
        """
        shape_data = self.sizing_data[frequency]
        shape_key = self._find_shape_key(shape_data, coordinates)

        period = shape_data[shape_key]
        return period

    def _find_shape_key(self, shape_data: Dict[str, float], coordinates: str) -> str:
        shape_key = coordinates
        logger = logging.getLogger(__name__)

        # If the shape actual key doesn't exist look for similar key by removing
        # first element until one can be found, e.g. if shape is `4-192-144`
        # and there is no sizing information try `192-144`.
        # If no sizing information can be found, use `default`.
        while shape_key not in shape_data:
            if '-' not in shape_key:
                shape_key = SizingInfo.DEFAULT_KEY
                break
            tmp = shape_key.split('-')
            shape_key = '-'.join(tmp[1:])

        if coordinates != shape_key:
            msg = 'Could not find sizing entry for this file shape_key used: "{}"\n'.format(shape_key)
            logger.warning(msg)
        return shape_key


class BaseModelParameters(ModelParameters, metaclass=ABCMeta):
    """
    Abstract class to store the parameters for a model.
    The parameters of a model are defined in a json file.
    """

    def __init__(self, model_id: ModelId) -> None:
        self._model_id: ModelId = model_id
        self._cycle_lengths: Dict[str, str] = {}
        self._memory: Dict[str, str] = {}
        self._temp_space: Dict[str, int] = {}
        self._sizing: SizingInfo = SizingInfo({})
        self._grid_info: Dict[GridType, BaseGridInfo] = {}
        self._subdaily_streams: List[str] = []
        self._stream_file_info: StreamFileInfo = None
        self._streams: List[str] = []
        self._grid_mappings: BaseGridMapping = BaseGridMapping()
        self._halo_removal_info: Dict[str, str] = {}

    def temp_space(self, stream_id: str) -> int:
        """
        Returns the temporary space of the given stream.

        :param stream_id: Stream ID
        :type stream_id: str
        :return: Temporary space of the stream
        :rtype: int
        """
        temp_space = self._temp_space[stream_id]
        return temp_space

    def memory(self, stream_id: str) -> str:
        """
        Returns the memory of the given stream.

        :param stream_id: Stream ID
        :type stream_id: str
        :return: Size of memory
        :rtype: str
        """
        return self._memory[stream_id]
    
    def halo_removal_info(self) -> Dict[str, str]:
        """
        Returns the halo removal information for this model.

        :return: Halo removal information
        :rtype: Dict[str, str]
        """
        return self._halo_removal_info

    def cycle_length(self, stream_id: str) -> str:
        """
        Returns the cycle length of the given stream.

        :param stream_id: Stream ID
        :type stream_id: str
        :return: Cycle length
        :rtype: str
        """
        return self._cycle_lengths[stream_id]

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
        return self._sizing.get_period(frequency, shape)

    def full_sizing_info(self) -> Dict[str, Dict[str, float]]:
        """
        Returns all sizing information.

        :return: Sizing information
        :rtype: dict
        """
        return self._sizing.get_all()

    def subdaily_streams(self) -> List[str]:
        """
        Returns a list of subdaily atmospheric streams.

        :return: Subdaily streams
        :rtype: List[str]
        """
        return self._subdaily_streams

    def streams(self) -> List[str]:
        """
        Returns a list of all defined streams.

        :return: Streams
        :rtype: List[str]
        """
        return self._streams

    def stream_file_info(self) -> StreamFileInfo:
        """
        Returns information about the stream files that the model supports.

        :return: Information about the stream files
        :rtype: StreamFileInfo
        """
        return self._stream_file_info

    def grids_mapping(self) -> BaseGridMapping:
        """
        Returns mapping information about the grids for the MIP requested variables.

        :return: Grids mappings for the MIP requested variables
        :rtype: BaseGridMapping
        """
        return self._grid_mappings

    def load_parameters(self, dir_path: str) -> LoadResult:
        """
        Loads parameters from json files contained in the given directory.

        :param dir_path: Path to the directory containing the json files
        :type dir_path: str
        :return: The result that indicate if the parameters could be loaded successful
        :rtype: LoadResult
        """
        loaded = False
        json_file = self._get_json_file(dir_path)
        if os.path.exists(json_file):
            parameters = read_json(json_file)
            new_cylc_lengths = parameters.get('cycle_length', {})
            new_memory = parameters.get('memory', {})
            new_temp_space = parameters.get('temp_space', {})
            new_sizing_info = parameters.get('sizing_info', {})
            new_grid_info = parameters.get('grid_info')
            new_halo_removal = parameters.get('halo_removal', {})
            self._load_stream_file_info(parameters.get('stream_file_frequency', {}))
            self._subdaily_streams = parameters.get('subdaily_streams', [])
            self._cycle_lengths.update(new_cylc_lengths)
            self._memory.update(new_memory)
            self._temp_space.update(new_temp_space)
            self._sizing.update(new_sizing_info)
            self._halo_removal_info.update(new_halo_removal)

            if new_grid_info:
                self._load_grid_info(new_grid_info)
            loaded = True
        return LoadResult(self._model_id.value, json_file, loaded)

    def _load_grid_info(self, new_grid_info: Dict[str, Any]):
        self._grid_info[GridType.ATMOS] = AtmosBaseGridInfo(new_grid_info['atmos'])
        self._grid_info[GridType.OCEAN] = OceanBaseGridInfo(new_grid_info['ocean'])

    def _load_stream_file_info(self, json_parameters: Dict[str, Any]) -> None:
        file_frequencies: Dict[str, StreamFileFrequency] = {}
        for frequency, streams in json_parameters.items():
            file_frequencies.update({
                stream: StreamFileFrequency(frequency, stream) for stream in streams
            })
            self._streams.extend(streams)
        self._stream_file_info = StreamFileInfo(file_frequencies)

    def _get_json_file(self, dir_path: str) -> str:
        file_name = self._model_id.get_json_file()
        return os.path.join(dir_path, file_name)

    def is_model(self, model_id: str) -> bool:
        """
        Returns if the current class represents the given model.

        :param model_id: Model ID to check
        :type model_id: str
        :return: If given model is represent by the class or not
        :rtype: bool
        """
        return model_id.lower() == self._model_id.value.lower()

    def grid_info(self, grid_type: GridType) -> BaseGridInfo:
        """
        Returns the corresponding grid information for the given grid type.

        :param grid_type: Grid type (e.g.: ATMOS, OCEAN)
        :type grid_type: GridType
        :return: Grid information of the given grid type
        :rtype: BaseGridInfo
        """
        return self._grid_info[grid_type]

    def all_ancil_files(self, root_directory: str) -> List[str]:
        """
        Returns the paths to all ancillary files of this model in the
        model directory in given root directory.

        :param root_directory: Path to root directory of the files
        :type root_directory: str
        :return: Paths to the ancillary files
        :rtype: List[str]
        """
        model_directory = os.path.join(root_directory, self._model_id.value)
        file_names = []

        for grid_type in GridType:
            grid_info = self.grid_info(grid_type)
            file_names.extend(grid_info.ancil_filenames())

        return list(map(
            lambda filename: os.path.join(model_directory, filename), file_names
        ))

    def all_ancil_variables(self) -> List[str]:
        """
        Returns all ancillary variables of this model that should
        be removed.

        :return: Ancillary variables
        :rtype: List[str]
        """
        all_ancil_variables = []
        for grid_type in GridType:
            grid_info = self.grid_info(grid_type)
            all_ancil_variables.extend(grid_info.ancil_variables())
        return all_ancil_variables

    def all_hybrid_heights_files(self, root_directory: str) -> List[str]:
        """
        Returns the paths to all hybrid heights files of this model in the
        given root directory.

        :param root_directory: Path to root directory of the files
        :type root_directory: str
        :return: Paths to the hybrid heights files
        :rtype: List[str]
        """
        grids_to_consider = list(filter(lambda x: x != GridType.OCEAN, GridType))
        file_names = []
        for grid_type in grids_to_consider:
            grid_info = self.grid_info(grid_type)
            file_names.extend(grid_info.hybrid_heights_files())
        return list(map(
            lambda file: os.path.join(root_directory, file), file_names
        ))


class BaseModelStore(ModelsStore, metaclass=ABCMeta):
    """
    Singleton class to store for each model the corresponding parameters.
    The parameters are defined in json files.

    The class is a singleton to avoid excessive loading of the parameters from the json files.
    """

    def __init__(self, model_instances: List[BaseModelParameters]) -> None:
        super(BaseModelStore, self).__init__()
        self.model_instances: List[BaseModelParameters] = model_instances
        self._load_default_params()

    @abstractmethod
    def _load_default_params(self) -> None:
        """
        Loads information from a json in a specific location. The json contains
        the default information for each supported resolution.
        """
        pass

    def overload_params(self, dir_path: str) -> LoadResults:
        """
        Overloads model parameters. The new parameters are specified in a json file in the given directory.
        The json file name must match following pattern: <model-name>.json

        :param dir_path: Path to the directory
        :type dir_path: str
        :return: Results containing which model values were overloaded
        :rtype: LoadResults
        """
        self._logger.info('Load model parameters from: {}'.format(dir_path))
        results = LoadResults()
        for model_instance in self.model_instances:
            result = model_instance.load_parameters(dir_path)
            results.add(result)
        return results

    def get(self, model_id: str) -> BaseModelParameters:
        """
        Returns the model parameters data for the given model.

        :param model_id: Model ID
        :type model_id: str
        :return: Class containing the model parameters
        :rtype: BaseModelParameters
        """
        for model_instance in self.model_instances:
            if model_instance.is_model(model_id):
                return model_instance
        raise ValueError('Cannot find any model parameters for model {}.'.format(model_id))

    def get_all(self) -> List[BaseModelParameters]:
        """
        Returns all model parameters data stored in this model store.

        :return:
        :rtype: List[BaseModelParameters]
        """
        return self.model_instances

    def add(self, model_instance: BaseModelParameters) -> None:
        """
        Adds the given CmipModelParameters instance to the cache

        Only used in tests!
        """
        self.model_instances.append(model_instance)
