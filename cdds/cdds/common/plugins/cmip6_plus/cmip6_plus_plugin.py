# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`cmip6_plus_plugin` module contains the code for the CMIP6Plus plugin.
"""
import os

from typing import Type, Dict, Any

from cdds.common.plugins.file_info import ModelFileInfo, GlobalModelFileInfo
from cdds.common.plugins.grid import GridLabel
from cdds.common.plugins.models import ModelParameters
from cdds.common.plugins.streams import StreamInfo
from cdds.common.plugins.base.base_plugin import BasePlugin, MipEra
from cdds.common.plugins.base.base_models import BaseModelParameters
from cdds.common.plugins.cmip6_plus.cmip6_plus_attributes import Cmip6PlusGlobalAttributes
from cdds.common.plugins.cmip6_plus.cmip6_plus_grid import Cmip6PlusGridLabel
from cdds.common.plugins.cmip6_plus.cmip6_plus_models import Cmip6PlusModelsStore
from cdds.common.plugins.cmip6_plus.cmip6_plus_streams import Cmip6PlusStreamStore
from cdds.common.request.request import Request


CMIP6_Plus_LICENSE = ('CMIP6Plus model data produced by .* is licensed under a Creative Commons '
                      'License (https://creativecommons.org/). Consult https://pcmdi.llnl.gov/CMIP6Plus/TermsOfUse '
                      'for terms of use governing CMIP6Plus output, including citation requirements and proper '
                      'acknowledgment. The data producers and data providers make no warranty, either express or '
                      'implied, including, but not limited to, warranties of merchantability and fitness for a '
                      'particular purpose. All liabilities arising from the supply of the information (including '
                      'any liability arising in negligence) are excluded to the fullest extent permitted by law.')


class Cmip6PlusPlugin(BasePlugin):
    """
    Plugin for CMIP6Plus models
    """

    def __init__(self):
        super(Cmip6PlusPlugin, self).__init__(MipEra.CMIP6_Plus.value)

    def models_parameters(self, model_id: str) -> ModelParameters:
        """
        Returns the model parameters of the CMIP6Plus model with given model id.

        :param model_id: Model ID
        :type model_id: str
        :return: Model parameters of model
        :rtype: BaseModelParameters
        """
        models_store = Cmip6PlusModelsStore.instance()
        return models_store.get(model_id)

    def overload_models_parameters(self, source_dir: str) -> None:
        """
        Overloads model parameters of CMIP6Plus models. The new parameters are
        specified in a json file in the given directory. The json file name
        must match following pattern: <model-name>.json

        :param source_dir: Path to the directory containing the files specifies the new values
        :type source_dir: str
        """
        models_store = Cmip6PlusModelsStore.instance()
        models_store.overload_params(source_dir)

    def grid_labels(self) -> Type[GridLabel]:
        """
        Returns the grid labels related to CMIP6Plus models.

        :return: Grid labels
        :rtype: Cmip6PlusGridLabel
        """
        return Cmip6PlusGridLabel

    def stream_info(self) -> StreamInfo:
        """
        Returns the information of streams related to CMIP6Plus.

        :return: Information of streams
        :rtype: StreamInfo
        """
        stream_store = Cmip6PlusStreamStore.instance()
        return stream_store.get()

    def global_attributes(self, request: Request) -> Cmip6PlusGlobalAttributes:
        """
        Returns the global attributes for CMIP6Plus. The given request contains all information
        about the global attributes.

        :param request: Dictionary containing information about the global attributes
        :type request: Dict[str, Any]
        :return: Class to store and manage the global attributes for CMIP6Plus
        :rtype: Cmip6PlusGlobalAttributes
        """
        return Cmip6PlusGlobalAttributes(request)

    def model_file_info(self) -> ModelFileInfo:
        """
        Returns information to the simulation model files related to CMIP6Plus.

        :return: Information to the simulation model files
        :rtype: GlobalModelFileInfo
        """
        return GlobalModelFileInfo()

    def license(self) -> str:
        """
        Returns the license for CMIP6Plus

        :return: License
        :rtype: str
        """
        return CMIP6_Plus_LICENSE

    def mip_table_dir(self) -> str:
        """
        Returns the path to the MIP table directory that should be used for CMIP6Plus

        :return: Path to the MIP table directory
        :rtype: str
        """
        return os.path.join(os.environ['CDDS_ETC'], 'mip_tables', 'CMIP6Plus')
