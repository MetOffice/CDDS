# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`cordex_plugin` module contains the code for the CORDEX plugin.
"""
import os

from typing import Type, Dict, Any

from cdds.common.plugins.base.base_plugin import BasePlugin, MipEra
from cdds.common.plugins.file_info import ModelFileInfo, RegionalModelFileInfo
from cdds.common.plugins.cordex.cordex_attributes import CordexGlobalAttributes
from cdds.common.plugins.cordex.cordex_models import CordexModelStore
from cdds.common.plugins.cordex.cordex_grid import CordexGridLabel
from cdds.common.plugins.cordex.cordex_streams import CordexStreamStore
from cdds.common.plugins.attributes import GlobalAttributes
from cdds.common.plugins.grid import GridLabel
from cdds.common.plugins.models import ModelParameters
from cdds.common.plugins.streams import StreamInfo


CORDEX_LICENSE = ('Creative Commons Attribution 4.0 International License '
                  '(CC BY 4.0; https://creativecommons.org/licenses/by/4.0/).')


class CordexPlugin(BasePlugin):
    """
    Plugin for CORDEX models
    """

    def __init__(self) -> None:
        super(CordexPlugin, self).__init__(MipEra.CORDEX.value)

    def models_parameters(self, model_id: str) -> ModelParameters:
        """
        Returns the model parameters of the CORDEX model with given model id.

        :param model_id: Model ID
        :type model_id: str
        :return: Model parameters of model
        :rtype: BaseModelParameters
        """
        model_store = CordexModelStore.instance()
        return model_store.get(model_id)

    def overload_models_parameters(self, source_dir: str) -> None:
        """
        Overloads model parameters of CORDEX models. The new parameters are
        specified in a json file in the given directory. The json file name
        must match following pattern: <model-name>.json

        :param source_dir: Path to the directory containing the files specifies the new values
        :type source_dir: str
        """
        model_store = CordexModelStore.instance()
        model_store.overload_params(source_dir)

    def grid_labels(self) -> Type[GridLabel]:
        """
        Returns the grid labels related to CORDEX models.

        :return: Grid labels
        :rtype: CordexGridLabel
        """
        return CordexGridLabel

    def stream_info(self) -> StreamInfo:
        """
        Returns the information of streams related to CORDEX.

        :return: Information of streams
        :rtype: StreamInfo
        """
        stream_store = CordexStreamStore.instance()
        return stream_store.get()

    def global_attributes(self, request: Dict[str, Any]) -> GlobalAttributes:
        """
        Returns the global attributes for CORDEX. The given request contains all information
        about the global attributes.

        :param request: Dictionary containing information about the global attributes
        :type request: Dict[str, Any]
        :return: Class to store and manage the global attributes for CORDEX
        :rtype: CordexGlobalAttributes
        """
        return CordexGlobalAttributes(request)

    def model_file_info(self) -> ModelFileInfo:
        """
        Returns information to the simulation model files related to CORDEX.

        :return: Information to the simulation model files
        :rtype: RegionalModelFileInfo
        """
        return RegionalModelFileInfo()

    def license(self) -> str:
        """
        Returns the license for CORDEX

        :return: License
        :rtype: str
        """
        return CORDEX_LICENSE

    def mip_table_dir(self) -> str:
        """
        Returns the path to the MIP table directory that should be used for CORDEX

        :return: Path to the MIP table directory
        :rtype: str
        """
        return '{}/mip_tables/CORDEX/for_functional_tests'.format(os.environ['CDDS_ETC'])
