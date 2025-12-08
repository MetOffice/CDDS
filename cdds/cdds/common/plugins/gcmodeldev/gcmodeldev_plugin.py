# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`gcmodeldev_plugin` module contains the code for the GCModelDev plugin."""
import os
from typing import Type, Dict, Any, TYPE_CHECKING

from cdds.common.plugins.file_info import ModelFileInfo, GlobalModelFileInfo
from cdds.common.plugins.grid import GridLabel
from cdds.common.plugins.models import ModelParameters
from cdds.common.plugins.streams import StreamInfo
from cdds.common.plugins.base.base_plugin import MipEra, BasePlugin
from cdds.common.plugins.cmip6.cmip6_grid import Cmip6GridLabel
from cdds.common.plugins.attributes import DefaultGlobalAttributes
from cdds.common.plugins.gcmodeldev.gcmodeldev_models import GCModelDevStore
from cdds.common.plugins.gcmodeldev.gcmodeldev_streams import GCModelDevStreamStore
if TYPE_CHECKING:
    from cdds.common.request.request import Request


GCMODEL_DEV_LICENSE = ('GCModelDev model data is licensed under the Open Government License v3 '
                       '(https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/')


class GCModelDevPlugin(BasePlugin):
    """Plugin for GCModelDev models"""

    def __init__(self):
        super(GCModelDevPlugin, self).__init__(MipEra.GC_MODEL_DEV.value)

    def models_parameters(self, model_id: str) -> ModelParameters:
        """Returns the model parameters of the CMIP6 model with given model id.

        Parameters
        ----------
        model_id : str

        Returns
        -------
        CmipModelParameters
            Model parameters of model
        """
        models_store = GCModelDevStore.instance()
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
        models_store = GCModelDevStore.instance()
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
        """Returns the information of streams related to GCModelDev.

        Returns
        -------
        StreamInfo
            Information of streams
        """
        stream_store = GCModelDevStreamStore.instance()
        return stream_store.get()

    def global_attributes(self, request: "Request") -> DefaultGlobalAttributes:
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
        return DefaultGlobalAttributes(request)

    def model_file_info(self) -> ModelFileInfo:
        """Returns the path to the MIP table directory that should be used for the GCModelDev project

        Returns
        -------
        str
            Path to the MIP table directory
        """
        return GlobalModelFileInfo()

    def license(self) -> str:
        """Returns the license GCModelDev

        Returns
        -------
        str
            License
        """
        return GCMODEL_DEV_LICENSE

    def mip_table_dir(self) -> str:
        """Returns the path to the MIP table directory that should be used for GCModelDev

        Returns
        -------
        str
            Path to the MIP table directory
        """
        return os.path.join(os.environ['CDDS_ETC'], 'mip_tables', 'GCModelDev', '0.0.13')
