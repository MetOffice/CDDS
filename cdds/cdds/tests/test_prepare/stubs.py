# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = no-member
from cdds.common.request.request import Request
from cdds.prepare.parameters import VariableParameters


class VariableParametersStub(VariableParameters):

    def __init__(self, request=Request(), data_request_variables={}, experiment_metadata={},
                 model_data_request_variables={}, model_to_mip_mappings={}, model_suite_variables={}):
        self._request = request
        self._data_request_variables = data_request_variables
        self._experiment_metadata = experiment_metadata
        self._model_data_request_variables = model_data_request_variables
        self._model_to_mip_mappings = model_to_mip_mappings
        self._model_suite_variables = model_suite_variables
