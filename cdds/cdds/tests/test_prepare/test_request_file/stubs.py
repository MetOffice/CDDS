# (C) British Crown Copyright 2020-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
from cdds.prepare.request_file.models import RoseSuiteRequest, RoseSuiteArguments
from cdds.prepare.request_file.request import RoseSuiteRequestManager
from hadsdk.configuration.cv_config import CVConfig


class CVConfigStub(CVConfig):
    def __init__(self, required_source_types, additional_source_type):
        self._required_source_type = required_source_types
        self._additional_source_types = additional_source_type

    def allowed_source_types(self, experiment_id):
        return self._required_source_type + self._additional_source_types

    def required_source_type(self, experiment_id):
        return self._required_source_type

    def additional_source_type(self, experiment_id):
        return self._additional_source_types


class RequestManagerPartialStub(RoseSuiteRequestManager):

    def __init__(self, request=RoseSuiteRequest(), arguments=RoseSuiteArguments()):
        super(RequestManagerPartialStub, self).__init__(request, arguments)
        self._validation_result = True

    def _validate_rose_suite(self, rose_suite):
        return self._validation_result

    def set_validation_result(self, result):
        self._validation_result = result
