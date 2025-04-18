# (C) British Crown Copyright 2020-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
from cdds.tests.factories.request_factory import simple_request
from cdds.common.request.request import Request
from cdds.prepare.parameters import VariableParameters


class VariableParametersStub(VariableParameters):

    def __init__(self, request=simple_request(), data_request_variables={}, experiment_metadata={},
                 model_data_request_variables={}, model_to_mip_mappings={}, model_suite_variables={}):
        self._request = request
        self._data_request_variables = data_request_variables
        self._experiment_metadata = experiment_metadata
        self._model_data_request_variables = model_data_request_variables
        self._model_to_mip_mappings = model_to_mip_mappings
        self._model_suite_variables = model_suite_variables
