# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`cmip6_models` module contains the code required to
handle model parameters information for CMIP6 models.
"""
import logging
import os

from typing import List

from cdds.common.plugins.common import LoadResults
from cdds.common.plugins.base.base_models import BaseModelParameters, ModelId, BaseModelStore


class Cmip6ModelId(ModelId):
    """
    Represents the ID of a CMIP6 model.
    """

    def get_json_file(self) -> str:
        """
        Returns the json file name for a model containing the model ID as identifier.

        :return: Json file name for the model with current ID
        :rtype: str
        """
        return '{}.json'.format(self.value)

    UKESM1_1_LL = 'UKESM1-1-LL'


class UKESM1_1_LL_Params(BaseModelParameters):
    """
    Class to store the parameters for the UKESM1_0_LL model.
    """

    def __init__(self) -> None:
        super(UKESM1_1_LL_Params, self).__init__(Cmip6ModelId.UKESM1_1_LL)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the UKESM1_0_LL model.

        :return: Model version of UKESM1_0_LL
        :rtype: str
        """
        return '1.0'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the UKESM1_0_LL model.

        :return: Data request version of UKESM1_0_LL
        :rtype: str
        """
        return '01.00.17'

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the UKESM1_0_LL model.

        :return: UM version of UKESM1_0_LL
        :rtype: str
        """
        return '10.8'


class Cmip6ModelsStore(BaseModelStore):
    """
    Singleton class to store for each model the corresponding parameters.
    The parameters are defined in json files. The default parameters are
    stored in the data/model directory.

    The class is a singleton to avoid excessive loading of the parameters from the json files.
    """

    def __init__(self) -> None:
        model_instances: List[BaseModelParameters] = [
            UKESM1_1_LL_Params(),
        ]
        super(Cmip6ModelsStore, self).__init__(model_instances)
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def create_instance(cls) -> 'Cmip6ModelsStore':
        """
        Creates a new class instance.

        :return: New class instance
        :rtype: Cmip6ModelsStore
        """
        return Cmip6ModelsStore()

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
            self.logger.warning('\n'.join(error_messages))
            raise RuntimeError('\n'.join(error_messages))
