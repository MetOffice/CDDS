# (C) British Crown Copyright 2022-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`gcmodeldev_plugin` module contains the code for the GCModelDev plugin.
"""
from typing import Type, Dict, Any

from cdds_common.cdds_plugins.grid import GridLabel
from cdds_common.cdds_plugins.models import ModelParameters
from cdds_common.cdds_plugins.plugins import CddsPlugin
from cdds_common.cdds_plugins.cmip6.cmip6_grid import Cmip6GridLabel
from cdds_common.cdds_plugins.attributes import DefaultGlobalAttributes
from cdds_common.cdds_plugins.gcmodeldev.gcmodeldev_models import GCModelDevStore


class GCModelDevPlugin(CddsPlugin):
    """
    Plugin for GCModelDev models
    """

    def __init__(self):
        super(GCModelDevPlugin, self).__init__('gcmodeldev')

    def models_parameters(self, model_id: str) -> ModelParameters:
        """
        Returns the model parameters of the CMIP6 model with given model id.

        :param model_id:
        :type model_id: str
        :return: Model parameters of model
        :rtype: CmipModelParameters
        """
        models_store = GCModelDevStore.instance()
        return models_store.get(model_id)

    def overload_models_parameters(self, source_dir: str) -> None:
        """
        Overloads model parameters of CMIP6 models. The new parameters are
        specified in a json file in the given directory. The json file name
        must match following pattern: <model-name>.json

        :param source_dir: Path to the directory containing the files specifies the new values
        :type source_dir: str
        """
        pass

    def grid_labels(self) -> Type[GridLabel]:
        """
        Returns the grid labels related to CMIP6 models.

        :return: Grid labels
        :rtype: Cmip6GridLabel
        """
        return Cmip6GridLabel

    def global_attributes(self, request: Dict[str, Any]) -> DefaultGlobalAttributes:
        """
        Returns the global attributes for CMIP6. The given request contains all information
        about the global attributes.

        :param request: Dictionary containing information about the global attributes
        :type request: Dict[str, Any]
        :return: Class to store and manage the global attributes for CMIP6
        :rtype: Cmip6GlobalAttributes
        """
        return DefaultGlobalAttributes(request)
