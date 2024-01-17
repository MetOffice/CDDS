# (C) British Crown Copyright 2021-2024, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`cmip6_plugin` module contains the code for the CMIP6 plugin.
"""
import os
from typing import Type, Dict, Any

from cdds.common.plugins.file_info import ModelFileInfo, GlobalModelFileInfo
from cdds.common.plugins.grid import GridLabel
from cdds.common.plugins.models import ModelParameters
from cdds.common.plugins.streams import StreamInfo
from cdds.common.plugins.base.base_plugin import BasePlugin, MipEra
from cdds.common.plugins.base.base_models import BaseModelParameters
from cdds.common.plugins.cmip6.cmip6_attributes import Cmip6GlobalAttributes
from cdds.common.plugins.cmip6.cmip6_cdds_files import Cmip6CddsPaths
from cdds.common.plugins.cmip6.cmip6_grid import Cmip6GridLabel
from cdds.common.plugins.cmip6.cmip6_models import Cmip6ModelsStore
from cdds.common.plugins.cmip6.cmip6_streams import Cmip6StreamStore


CMIP6_LICENSE = ('CMIP6 model data produced by MOHC is licensed '
                 'under a Creative Commons Attribution ShareAlike '
                 '4.0 International License '
                 '(https://creativecommons.org/licenses). Consult '
                 'https://pcmdi.llnl.gov/CMIP6/TermsOfUse for '
                 'terms of use governing CMIP6 output, including '
                 'citation requirements and proper acknowledgment. '
                 'Further information about this data, including '
                 'some limitations, can be found via the '
                 'further_info_url (recorded as a global attribute '
                 'in this file) . The data producers and data '
                 'providers make no warranty, either express or '
                 'implied, including, but not limited to, '
                 'warranties of merchantability and fitness for a '
                 'particular purpose. All liabilities arising from '
                 'the supply of the information (including any '
                 'liability arising in negligence) are excluded to '
                 'the fullest extent permitted by law.')


class Cmip6Plugin(BasePlugin):
    """
    Plugin for CMIP6 models
    """

    def __init__(self):
        super(Cmip6Plugin, self).__init__(MipEra.CMIP6)

    def models_parameters(self, model_id: str) -> ModelParameters:
        """
        Returns the model parameters of the CMIP6 model with given model id.

        :param model_id: Model ID
        :type model_id: str
        :return: Model parameters of model
        :rtype: BaseModelParameters
        """
        models_store = Cmip6ModelsStore.instance()
        return models_store.get(model_id)

    def overload_models_parameters(self, source_dir: str) -> None:
        """
        Overloads model parameters of CMIP6 models. The new parameters are
        specified in a json file in the given directory. The json file name
        must match following pattern: <model-name>.json

        :param source_dir: Path to the directory containing the files specifies the new values
        :type source_dir: str
        """
        models_store = Cmip6ModelsStore.instance()
        models_store.overload_params(source_dir)

    def grid_labels(self) -> Type[GridLabel]:
        """
        Returns the grid labels related to CMIP6 models.

        :return: Grid labels
        :rtype: Cmip6GridLabel
        """
        return Cmip6GridLabel

    def stream_info(self) -> StreamInfo:
        """
        Returns the information of streams related to CMIP6.

        :return: Information of streams
        :rtype: StreamInfo
        """
        stream_store = Cmip6StreamStore.instance()
        return stream_store.get()

    def global_attributes(self, request: Dict[str, Any]) -> Cmip6GlobalAttributes:
        """
        Returns the global attributes for CMIP6. The given request contains all information
        about the global attributes.

        :param request: Dictionary containing information about the global attributes
        :type request: Dict[str, Any]
        :return: Class to store and manage the global attributes for CMIP6
        :rtype: Cmip6GlobalAttributes
        """
        return Cmip6GlobalAttributes(request)

    def model_file_info(self) -> ModelFileInfo:
        """
        Returns information to the simulation model files related to CMIP6.

        :return: Information to the simulation model files
        :rtype: GlobalModelFileInfo
        """
        return GlobalModelFileInfo()

    def license(self) -> str:
        """
        Returns the license for CMIP6

        :return: License
        :rtype: str
        """
        return CMIP6_LICENSE

    def cdds_paths(self) -> Cmip6CddsPaths:
        """
        Returns the path to the CDDS specific directories and files considering
        the CMIP6 specific files facets.

        :return: Paths to the CDDS specific directories and files
        :rtype: Cmip6CddsPaths
        """
        return Cmip6CddsPaths()
