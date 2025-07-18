# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
import os
import unittest

from unittest import TestCase

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.plugins import PluginStore
from cdds.tests.factories.request_factory import simple_request
from cdds.common.request.validations.exceptions import CVPathError, CVEntryError
from cdds.common.request.validations.cv_validators import CVValidatorFactory
from mip_convert.configuration.cv_config import CVConfig


class TestCVValidatorFactory(TestCase):

    def setUp(self):
        load_plugin(mip_era='CMIP6')
        plugin = PluginStore.instance().get_plugin()
        self.cv_path = os.path.join(plugin.mip_table_dir(), 'CMIP6_CV.json')
        self.cv_config = CVConfig(self.cv_path)
        self.request = simple_request()

    def test_cv_path_succeed(self):
        validate_func = CVValidatorFactory.path_validator()
        validate_func(self.cv_path)

    def test_cv_path_failed(self):
        not_existing_cv_path = '/not/existing/CMIP6_CV.json'
        validate_func = CVValidatorFactory.path_validator()
        self.assertRaises(CVPathError, validate_func, not_existing_cv_path)

    def test_institution_succeed(self):
        self.request.metadata.institution_id = 'MOHC'
        validate_func = CVValidatorFactory.institution_validator()
        validate_func(self.cv_config, self.request)

    def test_institution_failed(self):
        self.request.metadata.institution_id = 'unknown_id'
        validate_func = CVValidatorFactory.institution_validator()
        self.assertRaises(CVEntryError, validate_func, self.cv_config, self.request)

    def test_model_succeed(self):
        self.request.metadata.model_id = 'HadGEM3-GC31-MM'
        validate_func = CVValidatorFactory.model_validator()
        validate_func(self.cv_config, self.request)

    def test_model_failed(self):
        self.request.metadata.model_id = 'UNKNOWN_MODEL_ID'
        validate_func = CVValidatorFactory.model_validator()
        self.assertRaises(CVEntryError, validate_func, self.cv_config, self.request)

    def test_experiment_succeed(self):
        self.request.metadata.sub_experiment_id = 'none'
        self.request.metadata.experiment_id = 'piControl'
        validate_func = CVValidatorFactory.experiment_validator()
        validate_func(self.cv_config, self.request)

    def test_experiment_failed(self):
        self.request.metadata.sub_experiment_id = 'none'
        self.request.metadata.experiment_id = 'unkownExperiment'
        validate_func = CVValidatorFactory.experiment_validator()
        self.assertRaises(CVEntryError, validate_func, self.cv_config, self.request)

    def test_subexperiment_succeed(self):
        self.request.metadata.sub_experiment_id = 's1910'
        self.request.metadata.experiment_id = 'piControl'
        validate_func = CVValidatorFactory.experiment_validator()
        validate_func(self.cv_config, self.request)

    def test_subexperiment_failed(self):
        self.request.metadata.sub_experiment_id = 'unknown_sub_experiment'
        self.request.metadata.experiment_id = 'piControl'
        validate_func = CVValidatorFactory.experiment_validator()
        self.assertRaises(CVEntryError, validate_func, self.cv_config, self.request)

    def test_model_types_validator(self):
        self.request.metadata.model_type = ['AGCM', 'AER', 'CHEM']
        validate_func = CVValidatorFactory.model_types_validator()
        validate_func(self.cv_config, self.request)

    def test_model_types_failed_required_values(self):
        self.request.metadata.model_type = ['AER', 'CHEM']
        validate_func = CVValidatorFactory.model_types_validator()
        self.assertRaises(CVEntryError, validate_func, self.cv_config, self.request)

    def test_model_types_failed_not_allowed_values(self):
        self.request.metadata.model_type = ['AGCM', 'AER', 'CHEM', 'NotAllowed']
        validate_func = CVValidatorFactory.model_types_validator()
        self.assertRaises(CVEntryError, validate_func, self.cv_config, self.request)

    def test_parent_experiment_succeed(self):
        self.request.metadata.experiment_id = 'piControl'
        self.request.metadata.parent_experiment_id = 'piControl-spinup'

        validate_func = CVValidatorFactory.parent_validator()
        validate_func(self.cv_config, self.request)

    def test_parent_experiment_unknown(self):
        self.request.metadata.experiment_id = 'amip'
        self.request.metadata.parent_experiment_id = 'piControl-spinup'

        validate_func = CVValidatorFactory.parent_validator()
        self.assertRaises(CVEntryError, validate_func, self.cv_config, self.request)


if __name__ == '__main__':
    unittest.main()
