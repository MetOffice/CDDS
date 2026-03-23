# (C) British Crown Copyright 2021-2026, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`cmip7_models` module contains the code required to
handle model parameters information for CMIP7 models.
"""
import logging
import os

from typing import List

from cdds.common.plugins.common import LoadResults
from cdds.common.plugins.base.base_models import BaseModelParameters, ModelId, BaseModelStore
from cdds.common.plugins.cmip7.cmip7_grid_mapping import CMIP7GridMapping


class Cmip7ModelId(ModelId):
    """Represents the ID of a CMIP7 model."""

    def get_json_file(self) -> str:
        """Returns the json file name for a model containing the model ID as identifier.

        Returns
        -------
        str
            Json file name for the model with current ID
        """
        return '{}.json'.format(self.value)

    UKESM1_3_LL = 'UKESM1-3-LL'
    UKCM2_0_LL = 'UKCM2-0-LL'
    UKCM2A_0_HH = 'UKCM2a-0-HH'


class UKESM1_3_LL_Params(BaseModelParameters):
    """Class to store the parameters for the UKESM1_3_LL model."""

    def __init__(self) -> None:
        super(UKESM1_3_LL_Params, self).__init__(Cmip7ModelId.UKESM1_3_LL)
        self._grid_mappings: CMIP7GridMapping = CMIP7GridMapping()

    @property
    def model_version(self) -> str:
        """Returns the model version of the UKESM1_3_LL model.

        Returns
        -------
        str
            Model version of UKESM1_3_LL
        """
        return '1.0'

    @property
    def data_request_version(self) -> str:
        """Returns the data request version of the UKESM1_3_LL model.

        Returns
        -------
        str
            Data request version of UKESM1_3_LL
        """
        return '01.00.17'

    @property
    def um_version(self) -> str:
        """Returns the UM version of the UKESM1_3_LL model.

        Returns
        -------
        str
            UM version of UKESM1_3_LL
        """
        return '10.8'


class UKCM2_0_LL_Params(BaseModelParameters):
    """Class to store the parameters for the UKCM2.0 model."""

    def __init__(self) -> None:
        super(UKCM2_0_LL_Params, self).__init__(Cmip7ModelId.UKCM2_0_LL)
        self._grid_mappings: CMIP7GridMapping = CMIP7GridMapping()

    @property
    def model_version(self) -> str:
        """Returns the model version of the UKCM2.0 model.

        Returns
        -------
        str
            Model version of UKCM2.0
        """
        return '1.0'

    @property
    def data_request_version(self) -> str:
        """Returns the data request version of the UKCM2.0 model.

        Returns
        -------
        str
            Data request version of UKCM2.0
        """
        return '01.00.17'

    @property
    def um_version(self) -> str:
        """Returns the UM version of the UKCM2.0 model.

        Returns
        -------
        str
            UM version of UKCM2.0
        """
        return '10.8'


class UKCM2a_0_HH_Params(BaseModelParameters):
    """Class to store the parameters for the UKCM2a high res model."""

    def __init__(self) -> None:
        super(UKCM2a_0_HH_Params, self).__init__(Cmip7ModelId.UKCM2A_0_HH)
        self._grid_mappings: CMIP7GridMapping = CMIP7GridMapping()

    @property
    def model_version(self) -> str:
        """Returns the model version of the UKCM2a model.

        Returns
        -------
        str
            Model version of UKCM2a
        """
        return '1.0'

    @property
    def data_request_version(self) -> str:
        """Returns the data request version of the UKCM2a model.

        Returns
        -------
        str
            Data request version of UKCM2a
        """
        return '01.00.17'

    @property
    def um_version(self) -> str:
        """Returns the UM version of the UKCM2a model.

        Returns
        -------
        str
            UM version of UKCM2a
        """
        return '10.8'


class Cmip7ModelsStore(BaseModelStore):
    """Singleton class to store for each model the corresponding parameters.
    The parameters are defined in json files. The default parameters are
    stored in the data/model directory.

    The class is a singleton to avoid excessive loading of the parameters from the json files.
    """

    def __init__(self) -> None:
        model_instances: List[BaseModelParameters] = [
            UKESM1_3_LL_Params(),
            UKCM2_0_LL_Params(),
            UKCM2a_0_HH_Params(),
        ]
        super(Cmip7ModelsStore, self).__init__(model_instances)
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def create_instance(cls) -> 'Cmip7ModelsStore':
        """Creates a new class instance.

        Returns
        -------
        Cmip7ModelsStore
            New class instance
        """
        return Cmip7ModelsStore()

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
