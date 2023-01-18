# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`cordex_models` module contains the code required to
handle model parameters information for CORDEX models.
"""
import logging
import os

from cdds.common.plugins.common import LoadResults
from cdds.common.plugins.base.base_models import BaseModelParameters, ModelId, BaseModelStore


class CordexModelId(ModelId):
    """
    Represents the ID of a CORDEX model.
    """

    def get_json_file(self) -> str:
        """
        Returns the json file name for a model containing the model ID as identifier.

        :return: Json file name for the model with current ID
        :rtype: str
        """
        return '{}.json'.format(self.value)

    HadGEM3_GC31_MM = 'HadGEM3_GC31_MM'


class HadGEM3_GC31_MM_Params(BaseModelParameters):
    """
    Class to store the parameters for the HadGEM3_GC31_MM model.
    """

    def __init__(self) -> None:
        super(HadGEM3_GC31_MM_Params, self).__init__(CordexModelId.HadGEM3_GC31_MM)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the HadGEM3_GC31_MM model.

        :return: Model version of HadGEM3_GC31_MM
        :rtype: str
        """
        return '3.1'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the HadGEM3_GC31_MM model.

        :return: Data request version of HadGEM3_GC31_MM
        :rtype: str
        """
        return '01.00.10'

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the HadGEM3_GC31_MM model.

        :return: UM version of HadGEM3_GC31_MM
        :rtype: str
        """
        return '10.7'


class CordexModelStore(BaseModelStore):
    """
    Singleton class to store for each model the corresponding parameters.
    The parameters are defined in json files. The default parameters are
    stored in the data/model directory.

    The class is a singleton to avoid excessive loading of the parameters from the json files.
    """

    def __init__(self) -> None:
        model_instances = [HadGEM3_GC31_MM_Params()]
        super(CordexModelStore, self).__init__(model_instances)
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def create_instance(cls) -> 'CordexModelStore':
        """
        Creates a new class instance.

        :return: New class instance
        :rtype: CordexModelStore
        """
        return CordexModelStore()

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
