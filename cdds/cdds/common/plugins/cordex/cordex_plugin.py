# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`cordex_plugin` module contains the code for the CORDEX plugin."""
import os

from typing import Type, Dict, Any, TYPE_CHECKING

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
if TYPE_CHECKING:
    from cdds.common.request.request import Request


CORDEX_LICENSE = 'https://cordex.org/data-access/cordex-cmip6-data/cordex-cmip6-terms-of-use'


class CordexPlugin(BasePlugin):
    """Plugin for CORDEX models"""

    def __init__(self) -> None:
        super(CordexPlugin, self).__init__(MipEra.CORDEX.value)

    def models_parameters(self, model_id: str) -> ModelParameters:
        """Returns the model parameters of the CORDEX model with given model id.

        Parameters
        ----------
        model_id : str
            Model ID

        Returns
        -------
        BaseModelParameters
            Model parameters of model
        """
        model_store = CordexModelStore.instance()
        return model_store.get(model_id)

    def overload_models_parameters(self, source_dir: str) -> None:
        """Overloads model parameters of CORDEX models. The new parameters are
        specified in a json file in the given directory. The json file name
        must match following pattern: <model-name>.json

        Parameters
        ----------
        source_dir : str
            Path to the directory containing the files specifies the new values
        """
        model_store = CordexModelStore.instance()
        model_store.overload_params(source_dir)

    def grid_labels(self) -> Type[GridLabel]:
        """Returns the grid labels related to CORDEX models.

        Returns
        -------
        CordexGridLabel
            Grid labels
        """
        return CordexGridLabel

    def stream_info(self) -> StreamInfo:
        """Returns the information of streams related to CORDEX.

        Returns
        -------
        StreamInfo
            Information of streams
        """
        stream_store = CordexStreamStore.instance()
        return stream_store.get()

    def global_attributes(self, request: "Request") -> GlobalAttributes:
        """Returns the global attributes for CORDEX. The given request contains all information
        about the global attributes.

        Parameters
        ----------
        request : Dict[str, Any]
            Dictionary containing information about the global attributes

        Returns
        -------
        CordexGlobalAttributes
            Class to store and manage the global attributes for CORDEX
        """
        return CordexGlobalAttributes(request)

    def model_file_info(self) -> ModelFileInfo:
        """Returns information to the simulation model files related to CORDEX.

        Returns
        -------
        RegionalModelFileInfo
            Information to the simulation model files
        """
        return RegionalModelFileInfo()

    def license(self) -> str:
        """Returns the license for CORDEX

        Returns
        -------
        str
            License
        """
        return CORDEX_LICENSE

    def mip_table_dir(self) -> str:
        """Returns the path to the MIP table directory that should be used for CORDEX

        Returns
        -------
        str
            Path to the MIP table directory
        """
        return os.path.join(os.environ['CDDS_ETC'], 'mip_tables', 'CORDEX', 'cordex-cmip6-cmor-tables', 'Tables')

    def mip_table_prefix(self):
        return 'CORDEX-'
