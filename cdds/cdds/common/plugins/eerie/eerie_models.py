# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`EERIE_models` module contains the code required to
handle model parameter information for EERIE Models.
"""
import logging
import os
from typing import List

# from cdds.common.plugins.cmip6.cmip6_models import (
#     HadGEM3_GC31_LL_Params, HadGEM3_GC31_MM_Params, UKESM1_0_LL_Params, UKESM1_1_LL_Params)
from cdds.common.plugins.base.base_models import BaseModelParameters, ModelId, BaseModelStore
from cdds.common.plugins.common import LoadResults


class EERIEStore(BaseModelStore):
    """
    Singleton class to store for each model the corresponding parameters.
    The parameters are defined in json files. The default parameters are
    stored in the data/model directory.

    The class is a singleton to avoid excessive loading of the parameters from the json files.
    """

    def __init__(self) -> None:
        model_instances: List[BaseModelParameters] = [
            HadGEM3_GC5_COMA9P9_N96_ORCA1_Params(),
            HadGEM3_GC5_COMA9P9_N216_ORCA025_Params(),
            HadGEM3_GC5_COMA9P9_N640_ORCA12_Params(),
        ]
        self.logger = logging.getLogger(self.__class__.__name__)
        super(EERIEStore, self).__init__(model_instances)

    @classmethod
    def create_instance(cls) -> 'EERIEStore':
        """
        Creates a new class instance.

        :return: New class instance
        :rtype: EERIEStore
        """
        return EERIEStore()

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


class EERIEModelId(ModelId):
    """
    Represents the ID of a EERIE model.
    """

    def get_json_file(self) -> str:
        """
        Returns the json file name for a model containing the model ID as identifier.

        :return: Json file name for the model with current ID
        :rtype: str
        """
        return '{}.json'.format(self.value)

    HadGEM3_GC5_COMA9P9_N96_ORCA1 = 'HadGEM3-GC5-CoMA9p9-N96-ORCA1'
    HadGEM3_GC5_COMA9P9_N216_ORCA025 = 'HadGEM3-GC5-CoMA9p9-N216-ORCA025'
    HadGEM3_GC5_COMA9P9_N640_ORCA12 = 'HadGEM3-GC5-CoMA9p9-N640-ORCA12'


class HadGEM3_GC5_COMA9P9_N96_ORCA1_Params(BaseModelParameters):
    """
    Class to store the parameters for the HadGEM3_GC5_COMA9P9_N96_ORCA1 model.
    """

    def __init__(self) -> None:
        super(HadGEM3_GC5_COMA9P9_N96_ORCA1_Params, self).__init__(EERIEModelId.HadGEM3_GC5_COMA9P9_N96_ORCA1)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the HadGEM3_GC5_COMA9P9_N96_ORCA1 model.

        :return: Model version of HadGEM3_GC5_COMA9P9_N96_ORCA1
        :rtype: str
        """
        return '5.0'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the HadGEM3_GC5_COMA9P9_N96_ORCA1 model.

        :return: Data request version of HadGEM3_GC5_COMA9P9_N96_ORCA1
        :rtype: str
        """
        return ''

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the HadGEM3-GC5-CoMA9p9-N96-ORCA1 model.

        :return: UM version of HadGEM3_GC5_COMA9P9_N96_ORCA1
        :rtype: str
        """
        return '13.1'


class HadGEM3_GC5_COMA9P9_N216_ORCA025_Params(BaseModelParameters):
    """
    Class to store the parameters for the HadGEM3_GC5_COMA9P9_N216_ORCA025 model.
    """

    def __init__(self) -> None:
        super(HadGEM3_GC5_COMA9P9_N216_ORCA025_Params, self).__init__(EERIEModelId.HadGEM3_GC5_COMA9P9_N216_ORCA025)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the HadGEM3_GC5_COMA9P9_N216_ORCA025 model.

        :return: Model version of HadGEM3_GC5_COMA9P9_N216_ORCA025
        :rtype: str
        """
        return '5.0'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the HadGEM3_GC5_COMA9P9_N216_ORCA025 model.

        :return: Data request version of HadGEM3_GC5_COMA9P9_N216_ORCA025
        :rtype: str
        """
        return ''

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the HadGEM3-GC5-CoMA9p9-N216_ORCA025 model.

        :return: UM version of HadGEM3_GC5_COMA9P9_N216_ORCA025
        :rtype: str
        """
        return '13.1'


class HadGEM3_GC5_COMA9P9_N640_ORCA12_Params(BaseModelParameters):
    """
    Class to store the parameters for the HadGEM3_GC5_COMA9P9_N640_ORCA12 model.
    """

    def __init__(self) -> None:
        super(HadGEM3_GC5_COMA9P9_N640_ORCA12_Params, self).__init__(EERIEModelId.HadGEM3_GC5_COMA9P9_N640_ORCA12)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the HadGEM3_GC5_COMA9P9_N640_ORCA12 model.

        :return: Model version of HadGEM3_GC5_COMA9P9_N640_ORCA12
        :rtype: str
        """
        return '5.0'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the HadGEM3_GC5_COMA9P9_N640_ORCA12 model.

        :return: Data request version of HadGEM3_GC5_COMA9P9_N640_ORCA12
        :rtype: str
        """
        return ''

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the HadGEM3-GC5-CoMA9p9-N640-ORCA12 model.

        :return: UM version of HadGEM3_GC5_COMA9P9_N640_ORCA12
        :rtype: str
        """
        return '13.1'
