# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`cmip7_plugin` module contains the code for the CMIP7 plugin.
"""
import os
from typing import Type, Dict, Any, TYPE_CHECKING

from cdds.common.plugins.file_info import ModelFileInfo, GlobalModelFileInfo
from cdds.common.plugins.grid import GridLabel
from cdds.common.plugins.models import ModelParameters
from cdds.common.plugins.streams import StreamInfo
from cdds.common.plugins.base.base_plugin import BasePlugin, MipEra
from cdds.common.plugins.base.base_models import BaseModelParameters
from cdds.common.plugins.cmip7.cmip7_attributes import Cmip7GlobalAttributes
from cdds.common.plugins.cmip7.cmip7_grid import Cmip7GridLabel
from cdds.common.plugins.cmip7.cmip7_models import Cmip7ModelsStore
from cdds.common.plugins.cmip7.cmip7_streams import Cmip7StreamStore
if TYPE_CHECKING:
    from cdds.common.request.request import Request


CMIP7_LICENSE = ('CMIP7 model data produced by MOHC is licensed '
                 'under a Creative Commons Attribution ShareAlike '
                 '4.0 International License '
                 '(https://creativecommons.org/licenses). Consult '
                 'https://pcmdi.llnl.gov/CMIP7/TermsOfUse for '
                 'terms of use governing CMIP7 output, including '
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


class Cmip7Plugin(BasePlugin):
    """
    Plugin for CMIP7 models
    """

    def __init__(self):
        super(Cmip7Plugin, self).__init__(MipEra.CMIP7.value)

    def models_parameters(self, model_id: str) -> ModelParameters:
        """
        Returns the model parameters of the CMIP7 model with given model id.

        :param model_id: Model ID
        :type model_id: str
        :return: Model parameters of model
        :rtype: BaseModelParameters
        """
        models_store = Cmip7ModelsStore.instance()
        return models_store.get(model_id)

    def overload_models_parameters(self, source_dir: str) -> None:
        """
        Overloads model parameters of CMIP7 models. The new parameters are
        specified in a json file in the given directory. The json file name
        must match following pattern: <model-name>.json

        :param source_dir: Path to the directory containing the files specifies the new values
        :type source_dir: str
        """
        models_store = Cmip7ModelsStore.instance()
        models_store.overload_params(source_dir)

    def grid_labels(self) -> Type[GridLabel]:
        """
        Returns the grid labels related to CMIP7 models.

        :return: Grid labels
        :rtype: Cmip7GridLabel
        """
        return Cmip7GridLabel

    def stream_info(self) -> StreamInfo:
        """
        Returns the information of streams related to CMIP7.

        :return: Information of streams
        :rtype: StreamInfo
        """
        stream_store = Cmip7StreamStore.instance()
        return stream_store.get()

    def global_attributes(self, request: "Request") -> Cmip7GlobalAttributes:
        """
        Returns the global attributes for CMIP7. The given request contains all information
        about the global attributes.

        :param request: Dictionary containing information about the global attributes
        :type request: Dict[str, Any]
        :return: Class to store and manage the global attributes for CMIP7
        :rtype: Cmip7GlobalAttributes
        """
        return Cmip7GlobalAttributes(request)

    def model_file_info(self) -> ModelFileInfo:
        """
        Returns information to the simulation model files related to CMIP7.

        :return: Information to the simulation model files
        :rtype: GlobalModelFileInfo
        """
        return GlobalModelFileInfo()

    def license(self) -> str:
        """
        Returns the license for CMIP7

        :return: License
        :rtype: str
        """
        return CMIP7_LICENSE

    def mip_table_dir(self) -> str:
        """
        Returns the path to the MIP table directory that should be used for CMIP7

        :return: Path to the MIP table directory
        :rtype: str
        """
        return os.path.join(os.environ['CDDS_ETC'], 'mip_tables', 'CMIP7', '01.00.29')
