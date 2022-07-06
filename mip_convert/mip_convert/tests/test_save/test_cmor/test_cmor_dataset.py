# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = unused-argument
"""
Tests for cmor_dataset.py.
"""
from io import StringIO
import json
from textwrap import dedent
import unittest

from cdds.common.plugins.plugin_loader import load_plugin
from hadsdk.configuration.cv_config import CVConfig
from hadsdk.configuration.python_config import UserConfig
from unittest.mock import patch

from mip_convert.requirements import software_versions
from mip_convert.save.cmor.cmor_dataset import Dataset


class TestDataset(unittest.TestCase):
    """
    Tests for ``Dataset`` in cmor_dataset.
    """

    def setUp(self):
        load_plugin()
        # Setup 'user_config'.
        self.activity_id_user = 'DCPP'
        self.branch_date_in_parent = '2006-01-01-00-00-00'
        self.branch_method = 'standard'
        self.calendar = '360_day'
        self.experiment_id = 'aqua-control'
        self.parent_experiment_id = 'no parent'
        self.history = software_versions()[21:]  # Ignore timestamp.
        self.institution_id = 'MOHC'
        self.mip_era = 'CMIP6'
        self.parent_base_date = '2001-01-01-00-00-00'
        self.source_id = 'HadGEM3-GC31-LL'
        self.source_type_user = 'AOGCM AER BGC'
        self.sub_experiment_id = 'none'
        self.suite_id = 'ab123'
        self.forcing_index = '8'
        self.initialization_index = '4'
        self.physics_index = '6'
        self.realization_index = '2'
        self.variant_label = 'r{}i{}p{}f{}'.format(self.realization_index,
                                                   self.initialization_index,
                                                   self.physics_index,
                                                   self.forcing_index)
        self._user_config_contents = (
            '[cmor_setup]\n'
            'mip_table_dir:mip_table_dir\n'
            '[cmor_dataset]\n'
            'branch_date_in_parent:{branch_date_in_parent}\n'
            'branch_method:{branch_method}\n'
            'calendar:{calendar}\n'
            'experiment_id:{experiment_id}\n'
            'institution_id:{institution_id}\n'
            'mip_era:{mip_era}\n'
            'output_dir:output_dir\n'
            'parent_base_date:{parent_base_date}:\n'
            'parent_experiment_id:{parent_experiment_id}\n'
            'mip:{activity_id}\n'
            'model_id:{source_id}\n'
            'model_type:{source_type}\n'
            'sub_experiment_id:{sub_experiment_id}\n'
            'variant_label:{variant_label}\n'
            '[request]\n'
            'child_base_date:0000-00-00-00-00-00\n'
            'model_output_dir:model_output_dir\n'
            'run_bounds:0000-00-00-00-00-00 0000-00-00-00-00-00\n'
            'suite_id:{suite_id}\n'
            '[global_attributes]\n'
            'further_info_url:https://furtherinfo.es-doc.org/CMIP6.MOHC.HadGEM3-GC31-LL.aqua-control.none.r2i4p6f8\n'
        )
        self._user_config_values = {
            'activity_id': self.activity_id_user,
            'branch_date_in_parent': self.branch_date_in_parent,
            'branch_method': self.branch_method,
            'calendar': self.calendar,
            'experiment_id': self.experiment_id,
            'institution_id': self.institution_id,
            'mip_era': self.mip_era,
            'parent_base_date': self.parent_base_date,
            'parent_experiment_id': self.parent_experiment_id,
            'source_id': self.source_id,
            'source_type': self.source_type_user,
            'sub_experiment_id': self.sub_experiment_id,
            'suite_id': self.suite_id,
            'variant_label': self.variant_label
        }
        self.user_config_contents = self._user_config_contents.format(**self._user_config_values)
        self.user_config = self._instantiate_user_config(self.user_config_contents)
        # Setup 'cv_config'.
        self.activity_ids = {
            'AerChemMIP': 'Description for AerChemMIP',
            'C4MIP': 'Description for C4MIP',
            'CMIP': 'Description for CMIP',
            'DCPP': 'Description for DCPP',
            'VolMIP': 'Description for VolMIP'}
        self.activity_id = ['DCPP VolMIP']
        self.additional_source_type = ['AER', 'CHEM']
        self.experiment = 'aquaplanet control'
        self.institution = 'Met Office Hadley Centre'
        self.parent_activity_id = 'CMIP'
        self.required_global_attributes = [
            'activity_id', 'experiment', 'experiment_id', 'institution_id', 'source', 'source_type'
        ]
        self.required_source_type = ['AOGCM', 'BGC']
        self.source = 'Long description of model'
        self.source_types = {
            'AER': 'Description of AER',
            'AGCM': 'Description of AGCM',
            'AOGCM': 'Description of AOGCM',
            'BGC': 'Description of BGC',
            'CHEM': 'Description of CHEM',
            'LAND': 'Description of LAND'
        }
        self.sub_experiment = 'none'
        self.tracking_prefix = 'hdl:21.14100'
        self.version = '1.2.3.4'
        self._cv_config_contents = {
            'CV': {
                'version_metadata': {
                    'CV_collection_version': self.version
                },
                'required_global_attributes': self.required_global_attributes,
                'activity_id': self.activity_ids,
                'institution_id': {
                    self.institution_id: self.institution
                },
                'source_id': {
                    self.source_id: {'source': self.source}
                },
                'source_type': self.source_types,
                'sub_experiment_id': {
                    self.sub_experiment_id: self.sub_experiment
                },
                'experiment_id': {
                    self.experiment_id: {
                        'activity_id': self.activity_id,
                        'additional_allowed_model_components': self.additional_source_type,
                        'experiment': self.experiment,
                        'parent_activity_id': [self.parent_activity_id],
                        'parent_experiment_id': [self.parent_experiment_id],
                        'required_model_components': self.required_source_type
                    }
                },
                'tracking_id': ['{}/.*'.format(self.tracking_prefix)]
            }
        }
        self.cv_config_contents = json.dumps(self._cv_config_contents)
        self.cv_config = self._instantiate_cv_config()
        self.obj = Dataset(self.user_config, self.cv_config)

    @patch('os.path.isfile')
    @patch('os.path.isdir')
    @patch('builtins.open')
    def _instantiate_user_config(self, user_config_contents, mock_open, mock_isdir, mock_isfile):
        mock_open.return_value = StringIO(dedent(user_config_contents))
        mock_isdir.return_value = True
        mock_isfile.return_value = True
        return UserConfig('dummy_path', self.history)

    @patch('builtins.open')
    def _instantiate_cv_config(self, mock_open):
        mock_open.return_value = StringIO(dedent(self.cv_config_contents))
        return CVConfig('dummy_path')

    def test_validate_required_global_attributes(self):
        self.assertIsNone(self.obj.validate_required_global_attributes())

    def test_validate_activity_id_values_invalid(self):
        self._user_config_values['activity_id'] = 'FakeMIP DCCP'
        user_config_contents = self._user_config_contents.format(**self._user_config_values)
        user_config = self._instantiate_user_config(user_config_contents)
        dataset = Dataset(user_config, self.cv_config)

        self.assertRaisesRegex(
            RuntimeError, '"FakeMIP" does not exist in "activity_ids"', dataset.validate_activity_id_values
        )

    def test_validate_activity_id_values_multiple_value_exists(self):
        self._user_config_values['activity_id'] = 'DCPP VolMIP'
        user_config_contents = self._user_config_contents.format(**self._user_config_values)
        user_config = self._instantiate_user_config(user_config_contents)
        dataset = Dataset(user_config, self.cv_config)
        self.assertIsNone(dataset.validate_activity_id_values())

    def test_validate_activity_id_values_single_value_inconsistent(self):
        error_message = ('"CMIP" is inconsistent with the values specified for the experiment "{}" '
                         'from the CVs \("{}"\)').format(self.experiment_id, self.activity_id[0])

        self._user_config_values['activity_id'] = 'CMIP'
        user_config_contents = self._user_config_contents.format(**self._user_config_values)
        user_config = self._instantiate_user_config(user_config_contents)
        dataset = Dataset(user_config, self.cv_config)

        self.assertRaisesRegex(RuntimeError, error_message, dataset.validate_activity_id_values)

    def test_validate_source_type_values_invalid(self):
        error_message = '"ABCDE" does not exist in "source_types"'

        self._user_config_values['source_type'] = 'ABCDE LAND'
        user_config_contents = self._user_config_contents.format(**self._user_config_values)
        user_config = self._instantiate_user_config(user_config_contents)
        dataset = Dataset(user_config, self.cv_config)

        self.assertRaisesRegex(RuntimeError, error_message, dataset.validate_source_type_values)

    def test_validate_source_type_values_missing_required(self):
        error_message = 'Required model type "{}" for experiment "{}" not present'.format(
            self.required_source_type[0], self.experiment_id)

        self._user_config_values['source_type'] = 'AER CHEM'
        user_config_contents = self._user_config_contents.format(**self._user_config_values)
        user_config = self._instantiate_user_config(user_config_contents)
        dataset = Dataset(user_config, self.cv_config)

        self.assertRaisesRegex(RuntimeError, error_message, dataset.validate_source_type_values)

    def test_validate_source_types_all_required_no_additional(self):
        self._user_config_values['source_type'] = 'AOGCM BGC'
        user_config_contents = self._user_config_contents.format(**self._user_config_values)
        user_config = self._instantiate_user_config(user_config_contents)
        dataset = Dataset(user_config, self.cv_config)
        self.assertIsNone(dataset.validate_source_type_values())

    def test_validate_source_type_values_inconsistent_additional(self):
        error_message = ('"AGCM LAND" is inconsistent with the additional values specified for the experiment "{}" '
                         'from the CVs \("{}"\)').format(self.experiment_id, ' '.join(self.additional_source_type))

        self._user_config_values['source_type'] = ('AGCM AOGCM AER BGC CHEM LAND')
        user_config_contents = self._user_config_contents.format(**self._user_config_values)
        user_config = self._instantiate_user_config(user_config_contents)
        dataset = Dataset(user_config, self.cv_config)

        self.assertRaisesRegex(RuntimeError, error_message, dataset.validate_source_type_values)

    def test_items(self):
        further_info_url = ('https://furtherinfo.es-doc.org/{}.{}.{}.{}.{}.{}'.format(self.mip_era,
                                                                                      self.institution_id,
                                                                                      self.source_id,
                                                                                      self.experiment_id,
                                                                                      self.sub_experiment_id,
                                                                                      self.variant_label))
        # branch_time_in_parent = days between parent_base_date and
        # branch_date_in_parent
        branch_time_in_parent = 1800.0
        reference = self.user_config.cmor_dataset
        del reference['branch_date_in_parent']
        del reference['parent_base_date']

        values_to_update = {
            '_cmip6_option': 'CMIP6',
            '_controlled_vocabulary_file': 'CMIP6_CV.json',
            '_AXIS_ENTRY_FILE': 'CMIP6_coordinate.json',
            '_FORMULA_VAR_FILE': 'CMIP6_formula_terms.json',
            'branch_time_in_parent': branch_time_in_parent,
            'experiment': self.experiment,
            'forcing_index': self.forcing_index,
            'further_info_url': further_info_url,
            'mo_runid': self.suite_id,
            'history': self.history,
            'initialization_index': self.initialization_index,
            'institution': self.institution,
            'parent_activity_id': self.parent_activity_id,
            'parent_experiment_id': self.parent_experiment_id,
            'physics_index': self.physics_index,
            'realization_index': self.realization_index,
            'source': self.source, 'sub_experiment': self.sub_experiment_id,
            'tracking_prefix': self.tracking_prefix,
            'cv_version': self.version
        }
        reference.update(values_to_update)

        self.assertEqual(self.obj.items, reference)

    def test_global_attributes(self):
        reference = {
            'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.HadGEM3-GC31-LL.aqua-control.none.r2i4p6f8',
            'mo_runid': self.suite_id
        }
        self.assertEqual(self.obj.global_attributes, reference)


if __name__ == '__main__':
    unittest.main()
