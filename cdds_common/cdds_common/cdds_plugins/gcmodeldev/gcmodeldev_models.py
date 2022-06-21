# (C) British Crown Copyright 2022-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`gcmodeldev_models` module contains the code required to
handle model parameter information for GCModelDev Modelss.
"""
import logging
import os
from typing import List

from cdds_common.cdds_plugins.cmip6.cmip6_models import (
    HadGEM3_GC31_LL_Params, HadGEM3_GC31_MM_Params, UKESM1_0_LL_Params, UKESM1_1_LL_Params)
from cdds_common.cdds_plugins.base.base_models import (BaseModelParameters,
                                                       BaseModelStore)
from cdds_common.cdds_plugins.common import LoadResults


class GCModelDevStore(BaseModelStore):
    """
    Singleton class to store for each model the corresponding parameters.
    The parameters are defined in json files. The default parameters are
    stored in the data/model directory.

    The class is a singleton to avoid excessive loading of the parameters from the json files.
    """

    def __init__(self) -> None:
        model_instances: List[BaseModelParameters] = [
            HadGEM3_GC31_LL_Params(),
            HadGEM3_GC31_MM_Params(),
            UKESM1_0_LL_Params(),
            UKESM1_1_LL_Params()
        ]
        super(GCModelDevStore, self).__init__(model_instances)
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def create_instance(cls) -> 'GCModelDevStore':
        """
        Creates a new class instance.

        :return: New class instance
        :rtype: GCModelDevStore
        """
        return GCModelDevStore()

    def _load_default_params(self) -> None:
        local_dir = os.path.dirname(os.path.abspath(__file__))
        default_dir = os.path.join(local_dir, 'data/model')
        results = self.overload_params(default_dir)
        self._process_load_results(results)

    def _process_load_results(self, results: LoadResults) -> None:
        if results.unloaded:
            template = 'Failed to load model parameters for model "{}" from file: "{}"'
            error_messages = [
                template.format(model_id, path) for model_id, path in results.unloaded.items()
            ]
            self.logger.critical('\n'.join(error_messages))
            raise RuntimeError('\n'.join(error_messages))
