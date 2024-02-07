# (C) British Crown Copyright 2022-2024, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`gcmodeldev_models` module contains the code required to
handle model parameter information for GCModelDev Modelss.
"""
import logging
import os
from typing import List

from cdds.common.plugins.cmip6.cmip6_models import (
    HadGEM3_GC31_LL_Params, HadGEM3_GC31_MM_Params, UKESM1_0_LL_Params, UKESM1_1_LL_Params)
from cdds.common.plugins.base.base_models import BaseModelParameters, ModelId, BaseModelStore
from cdds.common.plugins.common import LoadResults


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
            HadGEM3_GC3p05_N96ORCA1_Params(),
            HadGEM3_GC3p05_N216ORCA025_Params(),
            HadGEM3_GC5p_N216ORCA025_Params(),
            HadGEM3_GC5c_N96ORCA1_Params(),
            HadGEM3_GC5c_N216ORCA025_Params(),
            HadGEM3_GC50_N96ORCA1_Params(),
            HadGEM3_GC50_N216ORCA025_Params(),
            UKESM1_0_LL_Params(),
            UKESM1_1_LL_Params(),
            eUKESM1_1_ice_N96ORCA1_Params(),
        ]
        self.logger = logging.getLogger(self.__class__.__name__)
        super(GCModelDevStore, self).__init__(model_instances)

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


class GCModelDevModelId(ModelId):
    """
    Represents the ID of a GCModelDev model.
    """

    def get_json_file(self) -> str:
        """
        Returns the json file name for a model containing the model ID as identifier.

        :return: Json file name for the model with current ID
        :rtype: str
        """
        return '{}.json'.format(self.value)

    HadREM3_GA7_05 = 'HadREM3-GA7-05'
    HadGEM3_GC31_LL = 'HadGEM3-GC31-LL'
    HadGEM3_GC31_MM = 'HadGEM3-GC31-MM'
    HadGEM3_GC3p05_N96ORCA1 = 'HadGEM3-GC3p05-N96ORCA1'
    HadGEM3_GC3p05_N216ORCA025 = 'HadGEM3-GC3p05-N216ORCA025'
    HadGEM3_GC5p_N216ORCA025 = 'HadGEM3-GC5p-N216ORCA025'
    HadGEM3_GC5c_N96ORCA1 = 'HadGEM3-GC5c-N96ORCA1'
    HadGEM3_GC5c_N216ORCA025 = 'HadGEM3-GC5c-N216ORCA025'
    HadGEM3_GC50_N96ORCA1 = 'HadGEM3-GC50-N96ORCA1'
    HadGEM3_GC50_N216ORCA025 = 'HadGEM3-GC50-N216ORCA025'
    UKESM1_0_LL = 'UKESM1-0-LL'
    UKESM1_1_LL = 'UKESM1-1-LL'
    EUKESM1_1_ice_N96ORCA1 = 'eUKESM1-1-ice-N96ORCA1'


class HadGEM3_GC5c_N96ORCA1_Params(BaseModelParameters):
    """
    Class to store the parameters for the HadGEM3_GC5c_N96ORCA1 model.
    """

    def __init__(self) -> None:
        super(HadGEM3_GC5c_N96ORCA1_Params, self).__init__(GCModelDevModelId.HadGEM3_GC5c_N96ORCA1)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the HadGEM3_GC5c_N96ORCA1 model.

        :return: Model version of HadGEM3_GC5c_N96ORCA1
        :rtype: str
        """
        return '5.0'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the HadGEM3_GC5c_N96ORCA1 model.

        :return: Data request version of HadGEM3_GC5c_N96ORCA1
        :rtype: str
        """
        return ''

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the HadGEM3_GC5c_N96ORCA1 model.

        :return: UM version of HadGEM3_GC5c_N96ORCA1
        :rtype: str
        """
        return '12.2'


class HadGEM3_GC50_N96ORCA1_Params(BaseModelParameters):
    """
    Class to store the parameters for the HadGEM3_GC50_N96ORCA1 model.
    """

    def __init__(self) -> None:
        super(HadGEM3_GC50_N96ORCA1_Params, self).__init__(GCModelDevModelId.HadGEM3_GC50_N96ORCA1)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the HadGEM3_GC50_N96ORCA1 model.

        :return: Model version of HadGEM3_GC50_N96ORCA1
        :rtype: str
        """
        return '5.0'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the HadGEM3_GC50_N96ORCA1 model.

        :return: Data request version of HadGEM3_GC50_N96ORCA1
        :rtype: str
        """
        return ''

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the HadGEM3_GC50_N96ORCA1 model.

        :return: UM version of HadGEM3_GC50_N96ORCA1
        :rtype: str
        """
        return '12.2'


class HadGEM3_GC50_N216ORCA025_Params(BaseModelParameters):
    """
    Class to store the parameters for the HadGEM3_GC50_N216ORCA025 model.
    """

    def __init__(self) -> None:
        super(HadGEM3_GC50_N216ORCA025_Params, self).__init__(GCModelDevModelId.HadGEM3_GC50_N216ORCA025)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the HadGEM3_GC50_N216ORCA025 model.

        :return: Model version of HadGEM3_GC50_N216ORCA025
        :rtype: str
        """
        return '5.0'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the HadGEM3_GC50_N216ORCA025 model.

        :return: Data request version of HadGEM3_GC50_N216ORCA025
        :rtype: str
        """
        return ''

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the HadGEM3_GC50_N216ORCA025 model.

        :return: UM version of HadGEM3_GC50_N216ORCA025
        :rtype: str
        """
        return '12.2'


class HadGEM3_GC5c_N216ORCA025_Params(BaseModelParameters):
    """
    Class to store the parameters for the HadGEM3_GC5c_N216ORCA025 model.
    """

    def __init__(self) -> None:
        super(HadGEM3_GC5c_N216ORCA025_Params, self).__init__(GCModelDevModelId.HadGEM3_GC5c_N216ORCA025)

    @property
    def model_version(self) -> str:
        """
         Returns the model version of the HadGEM3_GC5c_N216ORCA025 model.

        :return: Model version of HadGEM3_GC5c_N216ORCA025
        :rtype: str
        """
        return '5.0'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the HadGEM3_GC5c_N216ORCA025 model.

        :return: Data request version of HadGEM3_GC5c_N216ORCA025
        :rtype: str
        """
        return ''

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the HadGEM3_GC5c_N216ORCA025 model.

        :return: UM version of HadGEM3_GC5c_N216ORCA025
        :rtype: str
        """
        return '12.2'


class HadGEM3_GC3p05_N96ORCA1_Params(BaseModelParameters):
    """
    Class to store the parameters for the HadGEM3_GC3p05_N96ORCA1 model.
    """

    def __init__(self) -> None:
        super(HadGEM3_GC3p05_N96ORCA1_Params, self).__init__(GCModelDevModelId.HadGEM3_GC3p05_N96ORCA1)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the HadGEM3_GC3p05_N96ORCA1 model.

        :return: Model version of HadGEM3_GC3p05_N96ORCA1
        :rtype: str
        """
        return '3.05'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the HadGEM3_GC3p05_N96ORCA1 model.

        :return: Data request version of HadGEM3_GC3p05_N96ORCA1
        :rtype: str
        """
        return ''

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the HadGEM3_GC3p05_N96ORCA1 model.

        :return: UM version of HadGEM3_GC3p05_N96ORCA1
        :rtype: str
        """
        return '10.7'


class HadGEM3_GC3p05_N216ORCA025_Params(BaseModelParameters):
    """
    Class to store the parameters for the HadGEM3_GC3p05_N216ORCA025 model.
    """

    def __init__(self) -> None:
        super(HadGEM3_GC3p05_N216ORCA025_Params, self).__init__(GCModelDevModelId.HadGEM3_GC3p05_N216ORCA025)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the HadGEM3_GC3p05_N216ORCA025 model.

        :return: Model version of HadGEM3_GC3p05_N216ORCA025
        :rtype: str
        """
        return '3.05'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the HadGEM3_GC3p05_N216ORCA025 model.

        :return: Data request version of HadGEM3_GC3p05_N216ORCA025
        :rtype: str
        """
        return ''

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the HadGEM3_GC3p05_N216ORCA025 model.

        :return: UM version of HadGEM3_GC3p05_N216ORCA025
        :rtype: str
        """
        return '10.7'


class HadGEM3_GC5p_N216ORCA025_Params(BaseModelParameters):
    """
    Class to store the parameters for the HadGEM3_GC5p_N216ORCA025 model.
    """

    def __init__(self) -> None:
        super(HadGEM3_GC5p_N216ORCA025_Params, self).__init__(GCModelDevModelId.HadGEM3_GC5p_N216ORCA025)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the HadGEM3_GC5p_N216ORCA025 model.

        :return: Model version of HadGEM3_GC5p_N216ORCA025
        :rtype: str
        """
        return '5.0'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the HadGEM3_GC5p_N216ORCA025 model.

        :return: Data request version of HadGEM3_GC5p_N216ORCA025
        :rtype: str
        """
        return ''

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the HadGEM3_GC5p_N216ORCA025 model.

        :return: UM version of HadGEM3_GC5p_N216ORCA025
        :rtype: str
        """
        return '12.2'


class eUKESM1_1_ice_N96ORCA1_Params(BaseModelParameters):
    """
    Class to store the parameters for the eUKESM1_1_ice_N96ORCA1 model.
    """

    def __init__(self) -> None:
        super(eUKESM1_1_ice_N96ORCA1_Params, self).__init__(GCModelDevModelId.EUKESM1_1_ice_N96ORCA1)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the eUKESM1_1_ice_N96ORCA1 model.

        :return: Model version of eUKESM1_1_ice_N96ORCA1
        :rtype: str
        """
        return '1.0'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the eUKESM1_1_ice_N96ORCA1 model.

        :return: Data request version of eUKESM1_1_ice_N96ORCA1
        :rtype: str
        """
        return '01.00.17'

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the eUKESM1_1_ice_N96ORCA1 model.

        :return: UM version of eUKESM1_1_ice_N96ORCA1
        :rtype: str
        """
        return '10.8'
