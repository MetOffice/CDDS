# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module providing functionality to validate model parameters configurations
"""
import logging
import os

from typing import List, Dict, Any, Set

from cdds.common.io import read_json
from cdds.common.plugins.plugins import PluginStore
from cdds.common.request.request import read_request


FREQUENCIES = ['monthly', '10 day', 'quarterly', 'daily', 'hourly']


def do_model_params_validations(request_path: str) -> bool:
    """
    Validate all model parameters configurations in the given request configuration.

    :param request_path: Path to the request configuration containg the directory containing all
                         model parameters configurations
    :type request_path: str
    :return: If the model parameters files in the directory are valid or not
    :rtype: bool
    """
    logger = logging.getLogger(__name__)
    request = read_request(request_path)
    valid = False

    model_params_dir = request.conversion.model_params_dir
    model_id = request.metadata.model_id
    existingDir = True
    if not model_params_dir:
        logger.error('Please provide a "model_params_dir" in "conversion" section for validation.')
        existingDir = False
    elif not os.path.exists(model_params_dir):
        logger.error('Given model params dir "{}" does not exist.')
        existingDir = False
    elif not os.path.isdir(model_params_dir):
        logger.error('Given model params dir "{}" is not a directory.'.format(model_params_dir))
        existingDir = False

    if existingDir:
        valid = _validate_model_params(model_params_dir, model_id)
    return valid


def _validate_model_params(model_params_dir: str, model_id: str) -> bool:
    logger = logging.getLogger(__name__)
    valid = True

    model_params_files = [
        os.path.join(model_params_dir, f) for f in os.listdir(model_params_dir)
        if os.path.isfile(os.path.join(model_params_dir, f))
    ]

    model_param_files_for_model_id = [
        os.path.basename(f) for f in model_params_files if os.path.basename(f) == '{}.json'.format(model_id)
    ]

    logger.info('Check if model parameters are found for model id: "{}"'.format(model_id))
    logger.info('------------------------------------------------------')
    if len(model_param_files_for_model_id) < 1:
        logger.warn('No model parameters file in "{}" found for model id "{}"'.format(model_params_dir, model_id))
    else:
        logger.info('Find model parameters file "{}" for model id "{}"'.format(
            model_param_files_for_model_id[0], model_id)
        )
    logger.info('------------------------------------------------------')

    for model_param_file in model_params_files:
        validator = ModelParamsFileValidator()
        validator.validate(model_param_file)

        logger.info('Validation of model parameters file: "{}"'.format(model_param_file))
        logger.info('-----------------------------------------')
        if validator.valid and not validator.warning:
            logger.info('Model parameters file is valid.')
        if not validator.valid:
            logger.info('Model parameters file is invalid.')
            logger.error('\n'.join(validator.error_messages))
            valid = False
        if validator.warning:
            logger.info('Model parameters file validation has some warnings.')
            logger.warn('\n'.join(validator.warning_messages()))
        logger.info('-----------------------------------------')
    return valid


class ModelParamsFileValidator:
    """
    Provides functionality to validate model parameters file
    """

    def __init__(self):
        self._warning = False
        self._valid = True
        self._error_messages = []
        self._warning_messages = []

    @property
    def error_messages(self) -> List[str]:
        """
        Returns error messages of the validation of the model parameter file.

        :return: Error messages
        :rtype: List[str]
        """
        return self._error_messages

    @property
    def valid(self) -> bool:
        """
        Returns if model parameter file is valid.

        :return: Is model parameter file valid
        :rtype: bool
        """
        return self._valid

    @property
    def warning(self) -> bool:
        """
        Returns if there are any warnings after validation the model parameters file.

        :return: Are there any warnings
        :rtype: bool
        """
        return self._warning

    def warning_messages(self) -> List[str]:
        """
        Returns warning messages of the validation of the model parameter file.

        :return: Warning messages
        :rtype: List[str]
        """
        return self._warning_messages

    def validate(self, model_params_file: str) -> None:
        """
        Validates the sections of the given model parameter configuration file.

        :param model_params_file: Path to the model parameter configuration file
        :type model_params_file: str
        """
        logger = logging.getLogger(__name__)

        model_params_json = read_json(model_params_file)

        frequencies = model_params_json['stream_file_frequency']

        streams = {
            stream
            for stream_list in frequencies.values()
            for stream in stream_list
        }

        self._validate_cylc_length(streams, model_params_json['cycle_length'])
        self._validate_memory(streams, model_params_json['memory'])
        self._validate_temp_space(streams, model_params_json['temp_space'])
        self._validate_sub_dailys_streams(streams, model_params_json['subdaily_streams'])

        grid_info = model_params_json['grid_info']
        self._validate_atmos_grid_info(grid_info['atmos'])
        self._validate_ocean_grid_info(grid_info['ocean'])

    def _validate_atmos_grid_info(self, atmos_grid_info: Dict[str, Any]) -> None:
        if not atmos_grid_info['atmos_timestep']:
            message = 'There is no atmos timestep value defined in the atmos grid info'
            self._warning = True
            self._warning_messages.append(message)

        if not atmos_grid_info['model_info']:
            message = 'There is no model info value defined in the atmos grid info'
            self._warning = True
            self._warning_messages.append(message)

        if not atmos_grid_info['nominal_resolution']:
            message = 'There is no nominal resolution defined in the atmos grid info'
            self._warning = True
            self._warning_messages.append(message)

        if not atmos_grid_info['longitude']:
            message = 'The is no longitude defined in the atmos grid info'
            self._warning = True
            self._warning_messages.append(message)

        if not atmos_grid_info['latitude']:
            message = 'There is no latitude defined in the atmos grid info'
            self._warning = True
            self._warning_messages.append(message)

        if not atmos_grid_info['v_latitude']:
            message = 'There is no v_latitude defined in the atmos grid info'
            self._valid = True
            self._warning_messages.append(message)

    def _validate_ocean_grid_info(self, ocean_grid_info: Dict[str, Any]) -> None:
        if not ocean_grid_info['model_info']:
            message = 'There is no model info value defined in the ocean grid info'
            self._warning = True
            self._warning_messages.append(message)

        if not ocean_grid_info['nominal_resolution']:
            message = 'There is no nominal resolution defined in the ocean grid info'
            self._warning = True
            self._warning_messages.append(message)

        if not ocean_grid_info['longitude']:
            message = 'The is no longitude defined in the ocean grid info'
            self._warning = True
            self._warning_messages.append(message)

        if not ocean_grid_info['latitude']:
            message = 'There is no latitude defined in the ocean grid info'
            self._warning = True
            self._warning_messages.append(message)

        if not ocean_grid_info['replacement_coordinates_file']:
            message = 'There is no replacement coordinates file defined in the ocean grid info'
            self._warning = True
            self._warning_messages.append(message)

    def _validate_cylc_length(self, expected_streams: Set[str], cylc_lengths: Dict[str, Any]) -> None:
        cylc_lengths_streams = set(cylc_lengths.keys())
        if not expected_streams.issubset(cylc_lengths_streams):
            missing_streams = self._get_subset(set(expected_streams), cylc_lengths_streams)
            message = 'Following streams have no cylc length defined: {}'.format(', '.join(missing_streams))
            self._valid = False
            self._error_messages.append(message)

    def _validate_memory(self, expected_streams: Set[str], memories: Dict[str, Any]) -> None:
        memories_streams = set(memories.keys())
        if not expected_streams.issubset(memories_streams):
            missing_streams = self._get_subset(set(expected_streams), memories_streams)
            message = 'Following streams have no memory defined: {}'.format(', '.join(missing_streams))
            self._valid = False
            self._error_messages.append(message)

    def _validate_temp_space(self, expected_streams: Set[str], temp_spaces: Dict[str, Any]) -> None:
        temp_space_streams = set(temp_spaces.keys())
        if not expected_streams.issubset(temp_space_streams):
            missing_streams = self._get_subset(set(expected_streams), temp_space_streams)
            message = 'Following streams have no temp space defined: {}'.format(', '.join(missing_streams))
            self._valid = False
            self._error_messages.append(message)

    def _validate_sub_dailys_streams(self, expected_streams: Set[str], subdaily_streams: List[str]) -> None:
        if not set(subdaily_streams).issubset(expected_streams):
            missing_streams = self._get_subset(set(subdaily_streams), expected_streams)
            message = ('Following sub daily streams are defined but are not present in the streams section: '
                       '{}').format(', '.join(missing_streams))
            self._valid = False
            self._error_messages.append(message)

    def _get_subset(self, expected_items: Set[str], actual_items: Set[str]) -> List[str]:
        return sorted([
            item for item in expected_items if item not in actual_items
        ])
