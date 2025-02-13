# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
import json
import unittest

from mip_convert.configuration.cv_config import CVConfig
from io import StringIO
from unittest.mock import patch
from textwrap import dedent


class TestCVConfig(unittest.TestCase):
    """
    Tests for ``CVConfig`` in configuration.py.
    """

    def setUp(self):
        self.read_path = 'cv_config'
        self.required_global_attributes = [  # Taken from 01.00.27.
            'Conventions', 'activity_id', 'creation_date',
            'data_specs_version', 'experiment', 'experiment_id',
            'forcing_index', 'frequency', 'further_info_url', 'grid',
            'grid_label', 'initialization_index', 'institution',
            'institution_id', 'license', 'mip_era', 'nominal_resolution',
            'parent_experiment_id',
            'physics_index', 'product', 'realization_index', 'realm', 'source',
            'source_id', 'source_type', 'sub_experiment', 'sub_experiment_id',
            'table_id', 'tracking_id', 'variable_id', 'variant_label']
        self.mip_era = 'CMIP6'
        self.activity_id1 = 'CMIP'
        self.activity_id2 = 'OMIP'
        self.activity_id3 = 'PMIP'
        self.activity_id4 = 'SIMIP'
        self.activity_ids = {
            self.activity_id1: 'Description1',
            self.activity_id2: 'Description2',
            self.activity_id3: 'Description3',
            self.activity_id4: 'Description4'
        }
        self.institution_id = 'MOHC'
        self.institution = 'Long description of institution'
        self.source_id = 'UKESM1-0-MMh'
        self.source = 'Long description of source'
        self.source_type1 = 'AOGCM'
        self.source_type2 = 'AER'
        self.source_type3 = 'BGC'
        self.source_type4 = 'CHEM'
        self.source_types = {
            self.source_type1: 'Description1',
            self.source_type2: 'Description2',
            self.source_type3: 'Description3',
            self.source_type4: 'Description4'
        }
        self.sub_experiment_id = 'none'
        self.sub_experiment = 'Long description of sub-experiment'
        self.experiment_id = '1pctCO2'
        self.experiment = '1 percent per year increase in CO2'
        self.parent_activity_id = 'CMIP'
        self.parent_experiment_id = 'piControl'
        self.tracking_prefix = 'hdl:21.14100'
        self.cv_config_dict = {
            'CV': {
                'required_global_attributes': self.required_global_attributes,
                'activity_id': self.activity_ids,
                'institution_id': {
                    self.institution_id: self.institution
                },
                'source_id': {
                    self.source_id: {
                        'source': self.source
                    }
                },
                'source_type': self.source_types,
                'sub_experiment_id': {
                    self.sub_experiment_id: self.sub_experiment
                },
                'experiment_id': {
                    self.experiment_id: {
                        'activity_id': [self.activity_id3],
                        'additional_allowed_model_components': [self.source_type2, self.source_type3],
                        'experiment': self.experiment,
                        'parent_activity_id': [self.parent_activity_id],
                        'parent_experiment_id': [self.parent_experiment_id],
                        'required_model_components': [self.source_type1]
                    }
                },
                'tracking_id': ['{}/.*'.format(self.tracking_prefix)]
            }
        }
        self.cv_config = json.dumps(self.cv_config_dict)
        self.obj = None
        self.test_cv_config_instantiation()

    @patch('builtins.open')
    def test_cv_config_instantiation(self, mopen):
        mopen.return_value = StringIO(dedent(self.cv_config))
        self.obj = CVConfig(self.read_path)
        mopen.assert_called_once_with(self.read_path)

    def test_activity_ids(self):
        output = self.obj.activity_ids
        reference = self.activity_ids
        self.assertEqual(output, reference)

    def test_activity_id(self):
        output = self.obj.activity_id(self.experiment_id)
        reference = [self.activity_id3]
        self.assertEqual(output, reference)

    def test_experiment(self):
        output = self.obj.experiment(self.experiment_id)
        reference = self.experiment
        self.assertEqual(output, reference)

    def test_experiment_id_not_in_CV(self):
        output = self.obj.experiment('random_experiment_id')
        reference = 'unknown'
        self.assertEqual(output, reference)

    def test_experiment_not_in_CV(self):
        del self.cv_config_dict['CV']['experiment_id'][self.experiment_id]['experiment']
        self.cv_config = json.dumps(self.cv_config_dict)
        self.test_cv_config_instantiation()
        output = self.obj.experiment(self.experiment_id)
        reference = 'unknown'
        self.assertEqual(output, reference)

    def test_institution(self):
        output = self.obj.institution(self.institution_id)
        reference = self.institution
        self.assertEqual(output, reference)

    def test_institution_not_in_CV(self):
        output = self.obj.institution('random_institution_id')
        reference = 'unknown'
        self.assertEqual(output, reference)

    def test_parent_activity_id(self):
        output = self.obj.parent_activity_id(self.experiment_id, self.parent_experiment_id, self.mip_era)
        reference = self.parent_activity_id
        self.assertEqual(output, reference)

    def test_parent_activity_id_not_in_CV(self):
        output = self.obj.parent_activity_id('random_activity_id', 'random_experiment_id', self.mip_era)
        reference = 'unknown'
        self.assertEqual(output, reference)

    def test_parent_activity_id_correct_choice(self):
        new_parent_mip = 'NewMIP'
        new_parent_expt = 'new-expt'
        self.cv_config_dict['CV']['experiment_id'][self.experiment_id]['parent_activity_id'].append(new_parent_mip)
        self.cv_config_dict['CV']['experiment_id'][self.experiment_id]['parent_experiment_id'].append(new_parent_expt)

        self.cv_config = json.dumps(self.cv_config_dict)
        self.test_cv_config_instantiation()
        reference = new_parent_mip
        output = self.obj.parent_activity_id(self.experiment_id, new_parent_expt, self.mip_era)
        self.assertEqual(output, reference)

    def test_source(self):
        output = self.obj.source(self.source_id)
        reference = self.source
        self.assertEqual(output, reference)

    def test_source_types(self):
        output = self.obj.source_types
        reference = self.source_types
        self.assertEqual(output, reference)

    def test_required_source_type(self):
        output = self.obj.required_source_type(self.experiment_id)
        reference = [self.source_type1]
        self.assertEqual(output, reference)

    def test_additional_source_type(self):
        output = self.obj.additional_source_type(self.experiment_id)
        reference = [self.source_type2, self.source_type3]
        self.assertEqual(output, reference)

    def test_sub_experiment(self):
        output = self.obj.sub_experiment(self.sub_experiment_id)
        reference = self.sub_experiment
        self.assertEqual(output, reference)

    def test_tracking_prefix(self):
        output = self.obj.tracking_prefix
        reference = self.tracking_prefix
        self.assertEqual(output, reference)

    def test_required_global_attributes(self):
        reference = [
            'activity_id', 'experiment', 'experiment_id', 'forcing_index',
            'further_info_url', 'grid', 'grid_label', 'initialization_index',
            'institution', 'institution_id', 'license', 'nominal_resolution',
            'parent_experiment_id',
            'physics_index', 'realization_index', 'source', 'source_id',
            'source_type', 'sub_experiment', 'sub_experiment_id',
            'variant_label']
        self.assertEqual(self.obj.required_global_attributes, reference)

    def test_validate_method_exists_value_exists(self):
        self.assertIsNone(self.obj.validate_with_error(self.activity_id1, 'activity_ids'))

    def test_validate_method_exists_value_missing(self):
        self.assertRaises(RuntimeError, self.obj.validate_with_error, 'MadeUpMIP', 'activity_ids')

    def test_validate_method_missing(self):
        self.assertRaises(AttributeError, self.obj.validate_with_error, self.activity_id2, 'made_up_method')


if __name__ == '__main__':
    unittest.main()
