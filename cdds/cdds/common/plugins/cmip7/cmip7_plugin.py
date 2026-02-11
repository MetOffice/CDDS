# (C) British Crown Copyright 2021-2026, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`cmip7_plugin` module contains the code for the CMIP7 plugin."""
import os
from typing import Type, Dict, Any, TYPE_CHECKING

from cdds.common.plugins.file_info import ModelFileInfo, CMIP7GlobalModelFileInfo
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


CMIP7_LICENSE = "CC-BY-4-0"


class Cmip7Plugin(BasePlugin):
    """Plugin for CMIP7 models"""

    def __init__(self):
        super(Cmip7Plugin, self).__init__(MipEra.CMIP7.value)

    def models_parameters(self, model_id: str) -> ModelParameters:
        """Returns the model parameters of the CMIP7 model with given model id.

        Parameters
        ----------
        model_id : str
            Model ID

        Returns
        -------
        BaseModelParameters
            Model parameters of model
        """
        models_store = Cmip7ModelsStore.instance()
        return models_store.get(model_id)

    def overload_models_parameters(self, source_dir: str) -> None:
        """Overloads model parameters of CMIP7 models. The new parameters are
        specified in a json file in the given directory. The json file name
        must match following pattern: <model-name>.json

        Parameters
        ----------
        source_dir : str
            Path to the directory containing the files specifies the new values
        """
        models_store = Cmip7ModelsStore.instance()
        models_store.overload_params(source_dir)

    def grid_labels(self) -> Type[GridLabel]:
        """Returns the grid labels related to CMIP7 models.

        Returns
        -------
        Cmip7GridLabel
            Grid labels
        """
        return Cmip7GridLabel

    def stream_info(self) -> StreamInfo:
        """Returns the information of streams related to CMIP7.

        Returns
        -------
        StreamInfo
            Information of streams
        """
        stream_store = Cmip7StreamStore.instance()
        return stream_store.get()

    def global_attributes(self, request: "Request") -> Cmip7GlobalAttributes:
        """Returns the global attributes for CMIP7. The given request contains all information
        about the global attributes.

        Parameters
        ----------
        request : Dict[str, Any]
            Dictionary containing information about the global attributes

        Returns
        -------
        Cmip7GlobalAttributes
            Class to store and manage the global attributes for CMIP7
        """
        return Cmip7GlobalAttributes(request)

    def model_file_info(self) -> ModelFileInfo:
        """Returns information to the simulation model files related to CMIP7.

        Returns
        -------
        GlobalModelFileInfo
            Information to the simulation model files
        """
        return CMIP7GlobalModelFileInfo()

    def license(self) -> str:
        """Returns the license for CMIP7

        Returns
        -------
        str
            License
        """
        return CMIP7_LICENSE

    def mip_table_dir(self) -> str:
        """Returns the path to the MIP table directory that should be used for CMIP7

        Returns
        -------
        str
            Path to the MIP table directory
        """
        return os.path.join(os.environ['CDDS_ETC'], 'mip_tables', 'CMIP7', 'DR-1.2.2.3-v1.0.2')
