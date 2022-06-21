# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`cmip6_plugin` module contains the code for the CMIP6 plugin.
"""
from typing import Type, Dict, Any

from cdds_common.cdds_plugins.grid import GridLabel
from cdds_common.cdds_plugins.models import ModelParameters
from cdds_common.cdds_plugins.streams import StreamInfo
from cdds_common.cdds_plugins.base.base_plugin import BasePlugin, MipEra
from cdds_common.cdds_plugins.base.base_models import BaseModelParameters
from cdds_common.cdds_plugins.cmip6.cmip6_attributes import Cmip6GlobalAttributes
from cdds_common.cdds_plugins.cmip6.cmip6_grid import Cmip6GridLabel
from cdds_common.cdds_plugins.cmip6.cmip6_models import Cmip6ModelsStore
from cdds_common.cdds_plugins.cmip6.cmip6_streams import Cmip6StreamStore


class Cmip6Plugin(BasePlugin):
    """
    Plugin for CMIP6 models
    """

    def __init__(self):
        super(Cmip6Plugin, self).__init__(MipEra.CMIP6)

    def models_parameters(self, model_id: str) -> ModelParameters:
        """
        Returns the model parameters of the CMIP6 model with given model id.

        :param model_id:
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
