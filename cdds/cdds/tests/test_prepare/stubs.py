# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
from cdds.prepare.parameters import VariableParameters
from hadsdk.arguments import Arguments
from hadsdk.request import Request


class VariableParametersStub(VariableParameters):

    def __init__(self, arguments=Arguments, request=Request({}), data_request_variables={}, experiment_metadata={},
                 model_data_request_variables={}, model_to_mip_mappings={}, model_suite_variables={}):
        self._arguments = arguments
        self._request = request
        self._data_request_variables = data_request_variables
        self._experiment_metadata = experiment_metadata
        self._model_data_request_variables = model_data_request_variables
        self._model_to_mip_mappings = model_to_mip_mappings
        self._model_suite_variables = model_suite_variables
