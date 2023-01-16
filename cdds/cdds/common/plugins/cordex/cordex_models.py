# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import logging
import os

from cdds.common.plugins.common import LoadResults
from cdds.common.plugins.base.base_models import BaseModelParameters, ModelId, BaseModelStore


class CordexModelId(ModelId):

    def get_json_file(self) -> str:
        return '{}.json'.format(self.value)

    HadGEM3_GC31_LL = 'HadGEM3-GC31-LL'


class HadGEM3_GC31_LL_Params(BaseModelParameters):

    def __init__(self) -> None:
        super(HadGEM3_GC31_LL_Params, self).__init__(CordexModelId.HadGEM3_GC31_LL)

    @property
    def model_version(self) -> str:
        return '3.1'

    @property
    def data_request_version(self) -> str:
        return '01.00.10'

    @property
    def um_version(self) -> str:
        return '10.7'


class CordexModelStore(BaseModelStore):

    def __init__(self) -> None:
        model_instances = [HadGEM3_GC31_LL_Params()]
        super(CordexModelStore, self).__init__(model_instances)
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def create_instance(cls) -> 'CordexModelStore':
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
