# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`cmip6_models` module contains the code required to
handle model parameters information for CMIP6 models.
"""
import logging
import os

from typing import List

from cdds_common.cdds_plugins.common import LoadResults
from cdds_common.cdds_plugins.base.base_models import BaseModelParameters, ModelId, BaseModelStore


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

    HadREM3_GA7_05 = 'HadREM3-GA7-05'
    HadGEM3_GC31_LL = 'HadGEM3-GC31-LL'
    HadGEM3_GC31_MM = 'HadGEM3-GC31-MM'
    UKESM1_0_LL = 'UKESM1-0-LL'
    UKESM1_1_LL = 'UKESM1-1-LL'
    UKESM1_ICE_LL = 'UKESM1-ice-LL'


class HadREM3_GA7_05_Params(BaseModelParameters):
    """
    Class to store the parameters for the HadREM3_GA7_05 model.
    Note: At the moment, there are no sizing info, memory parameters,
          cycle length parameters, temp space parameters or data request
          version for this type of model.
    """

    def __init__(self) -> None:
        super(HadREM3_GA7_05_Params, self).__init__(Cmip6ModelId.HadREM3_GA7_05)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the HadREM3_GA7_05 model.

        :return: Model version of HadREM3_GA7_05
        :rtype: str
        """
        return '4.0'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the HadREM3_GA7_05 model.

        :return: Data request version of HadREM3_GA7_05
        :rtype: str
        """
        return ''

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the HadREM3_GA7_05 model.

        :return: UM version of HadREM3_GA7_05
        :rtype: str
        """
        return '10.9'


class HadGEM3_GC31_LL_Params(BaseModelParameters):
    """
    Class to store the parameters for the HadGEM3_GC31_LL model.
    """

    def __init__(self) -> None:
        super(HadGEM3_GC31_LL_Params, self).__init__(Cmip6ModelId.HadGEM3_GC31_LL)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the HadGEM3_GC31_LL model.

        :return: Model version of HadGEM3_GC31_LL
        :rtype: str
        """
        return '3.1'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the HadGEM3_GC31_LL model.

        :return: Data request version of HadGEM3_GC31_LL
        :rtype: str
        """
        return '01.00.10'

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the HadGEM3_GC31_LL model.

        :return: UM version of HadGEM3_GC31_LL
        :rtype: str
        """
        return '10.7'


class HadGEM3_GC31_MM_Params(BaseModelParameters):
    """
    Class to store the parameters for the HadGEM3_GC31_MM model.
    """

    def __init__(self) -> None:
        super(HadGEM3_GC31_MM_Params, self).__init__(Cmip6ModelId.HadGEM3_GC31_MM)

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


class UKESM1_0_LL_Params(BaseModelParameters):
    """
    Class to store the parameters for the UKESM1_0_LL model.
    """

    def __init__(self) -> None:
        super(UKESM1_0_LL_Params, self).__init__(Cmip6ModelId.UKESM1_0_LL)

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


class UKESM1_ice_LL_Params(BaseModelParameters):
    """
    Class to store the parameters for the UKESM1_ice_LL model.
    """

    def __init__(self) -> None:
        super(UKESM1_ice_LL_Params, self).__init__(Cmip6ModelId.UKESM1_ICE_LL)

    @property
    def model_version(self) -> str:
        """
        Returns the model version of the UKESM1_ice_LL model.

        :return: Model version of UKESM1_ice_LL
        :rtype: str
        """
        return '1.0'

    @property
    def data_request_version(self) -> str:
        """
        Returns the data request version of the UKESM1_ice_LL model.

        :return: Data request version of UKESM1_ice_LL
        :rtype: str
        """
        return '01.00.17'

    @property
    def um_version(self) -> str:
        """
        Returns the UM version of the UKESM1_ice_LL model.

        :return: UM version of UKESM1_ice_LL
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
            HadREM3_GA7_05_Params(),
            HadGEM3_GC31_LL_Params(),
            HadGEM3_GC31_MM_Params(),
            UKESM1_0_LL_Params(),
            UKESM1_1_LL_Params(),
            UKESM1_ice_LL_Params()
        ]
        super(Cmip6ModelsStore, self).__init__(model_instances)
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def create_instance(cls) -> 'Cmip6ModelsStore':
        """
        Creates a new class instance.

        :return: New class instance
        :rtype: Cmip6GridInfoStore
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
