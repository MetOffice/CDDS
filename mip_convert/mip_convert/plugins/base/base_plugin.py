# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
import logging
import os
import glob

from typing import Dict, Any

from mip_convert.configuration.python_config import ModelToMIPMappingConfig
from mip_convert.plugins.constants import all_constants
from mip_convert.plugins.quality_control import MaskedArrayBoundsChecker, UM_MDI, RAISE_EXCEPTION
from mip_convert.plugins.plugins import MappingPlugin


class BaseMappingPlugin(MappingPlugin):

    def __init__(self, plugin_id: str, mapping_data_dir: str):
        super(BaseMappingPlugin, self).__init__(plugin_id)
        self.mapping_data_dir = mapping_data_dir
        self.model_to_mip_mapping_config = ModelToMIPMappingConfig

    def load(self) -> None:
        logger = logging.getLogger(__name__)
        dirname = self.mapping_data_dir
        suffix = 'mappings.cfg'

        filename = '{model_configuration}_{suffix}'.format(model_configuration=self._plugin_id, suffix=suffix)
        pathname = os.path.join(self.mapping_data_dir, filename)

        if os.path.isfile(pathname):
            model_to_mip_mappings = ModelToMIPMappingConfig(pathname, self._plugin_id)
            logger.debug('Reading "{filename}"'.format(filename=filename))

        fileregex = '{model_configuration}_*_{suffix}'.format(model_configuration=self._plugin_id, suffix=suffix)
        pathregex = os.path.join(self.mapping_data_dir, fileregex)
        files = glob.glob(pathregex)

        for file in files:
            if os.path.isfile(file):
                model_to_mip_mappings.read(file)
                logger.debug('Reading "{filename}"'.format(filename=filename))

        self.model_to_mip_mapping_config = model_to_mip_mappings

    def model_to_mip_mapping(self) -> ModelToMIPMappingConfig:
        return self.model_to_mip_mapping_config

    def constants(self) -> Dict[str, str]:
        """
        Returns the names and values of the constants available for use in the |model to MIP mapping| expressions.

        :return: The names and values of the constants available for use in the |model to MIP mapping| expressions.
        :rtype: Dict[str, str]
        """
        return all_constants()

    def bounds_checker(
            self, fill_value: float = UM_MDI, valid_min: float = None, valid_max: float = None, tol_min: float = None,
            tol_max: float = None, tol_min_action: int = RAISE_EXCEPTION, tol_max_action: int = RAISE_EXCEPTION,
            oob_action: int = RAISE_EXCEPTION) -> MaskedArrayBoundsChecker:
        """
        Returns the checker for checking and, if required, adjusting numpy MaskedArrays

        :param fill_value: Filling value
        :type fill_value: float
        :param valid_min: Valid minimum
        :type valid_min: float
        :param valid_max: Valid maximum
        :type valid_max: float
        :param tol_min: Minimal tolerance
        :type tol_min: float
        :param tol_max: Maximal tolerance
        :type tol_max: float
        :param tol_min_action: Action for minimal tolerance
        :type tol_min_action: int
        :param tol_max_action: Action for maximal tolerance
        :type tol_max_action: int
        :param oob_action: Action of out-of-bounds values
        :type oob_action: int
        :return: Checker to masked the array
        :rtype: MaskedArrayBoundsChecker
        """
        return MaskedArrayBoundsChecker(fill_value, valid_min, valid_max, tol_min, tol_max, tol_min_action, oob_action)
