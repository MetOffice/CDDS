# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`cmip6_plugin` module contains the code for the CMIP6 plugin."""
import os
from typing import Type, Dict, Any, TYPE_CHECKING

from cdds.common.plugins.file_info import ModelFileInfo, GlobalModelFileInfo
from cdds.common.plugins.grid import GridLabel
from cdds.common.plugins.models import ModelParameters
from cdds.common.plugins.streams import StreamInfo
from cdds.common.plugins.base.base_plugin import BasePlugin, MipEra
from cdds.common.plugins.base.base_models import BaseModelParameters
from cdds.common.plugins.cmip6.cmip6_attributes import Cmip6GlobalAttributes
from cdds.common.plugins.cmip6.cmip6_grid import Cmip6GridLabel
from cdds.common.plugins.cmip6.cmip6_models import Cmip6ModelsStore
from cdds.common.plugins.cmip6.cmip6_streams import Cmip6StreamStore
if TYPE_CHECKING:
    from cdds.common.request.request import Request


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
    """Plugin for CMIP6 models"""

    def __init__(self):
        super(Cmip6Plugin, self).__init__(MipEra.CMIP6.value)

    def models_parameters(self, model_id: str) -> ModelParameters:
        """Returns the model parameters of the CMIP6 model with given model id.

        Parameters
        ----------
        model_id : str
            Model ID

        Returns
        -------
        BaseModelParameters
            Model parameters of model
        """
        models_store = Cmip6ModelsStore.instance()
        return models_store.get(model_id)

    def overload_models_parameters(self, source_dir: str) -> None:
        """Overloads model parameters of CMIP6 models. The new parameters are
        specified in a json file in the given directory. The json file name
        must match following pattern: <model-name>.json

        Parameters
        ----------
        source_dir : str
            Path to the directory containing the files specifies the new values
        """
        models_store = Cmip6ModelsStore.instance()
        models_store.overload_params(source_dir)

    def grid_labels(self) -> Type[GridLabel]:
        """Returns the grid labels related to CMIP6 models.

        Returns
        -------
        Cmip6GridLabel
            Grid labels
        """
        return Cmip6GridLabel

    def stream_info(self) -> StreamInfo:
        """Returns the information of streams related to CMIP6.

        Returns
        -------
        StreamInfo
            Information of streams
        """
        stream_store = Cmip6StreamStore.instance()
        return stream_store.get()

    def global_attributes(self, request: "Request") -> Cmip6GlobalAttributes:
        """Returns the global attributes for CMIP6. The given request contains all information
        about the global attributes.

        Parameters
        ----------
        request : Dict[str, Any]
            Dictionary containing information about the global attributes

        Returns
        -------
        Cmip6GlobalAttributes
            Class to store and manage the global attributes for CMIP6
        """
        return Cmip6GlobalAttributes(request)

    def model_file_info(self) -> ModelFileInfo:
        """Returns information to the simulation model files related to CMIP6.

        Returns
        -------
        GlobalModelFileInfo
            Information to the simulation model files
        """
        return GlobalModelFileInfo()

    def license(self) -> str:
        """Returns the license for CMIP6

        Returns
        -------
        str
            License
        """
        return CMIP6_LICENSE

    def mip_table_dir(self) -> str:
        """Returns the path to the MIP table directory that should be used for CMIP6

        Returns
        -------
        str
            Path to the MIP table directory
        """
        return os.path.join(os.environ['CDDS_ETC'], 'mip_tables', 'CMIP6', '01.00.29')
