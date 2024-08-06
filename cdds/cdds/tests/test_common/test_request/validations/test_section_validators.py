# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import tempfile
import unittest

from metomi.isodatetime.data import TimePoint
from unittest import TestCase

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.request.common_section import CommonSection, common_defaults
from cdds.common.request.metadata_section import MetadataSection, metadata_defaults
from cdds.common.request.validations.section_validators import (SectionValidatorFactory,
                                                                CommonSectionValidator,
                                                                MetadataSectionValidator)


class TestCommonSectionValidator(TestCase):

    def setUp(self):
        load_plugin()
        defaults = common_defaults('UKESM1-0-LL', 'piControl', 'r1i1p1f1')
        self.section = CommonSection(**defaults)

    def test_validation_succeed(self):
        validator = CommonSectionValidator(section=self.section)
        valid, messages = validator.validate()
        self.assertTrue(valid)
        self.assertListEqual(messages, [])

    def test_external_plugin_location_failed(self):
        self.section.external_plugin = 'external.plugin'
        validator = CommonSectionValidator(section=self.section)
        valid, messages = validator.validate()
        self.assertFalse(valid)
        self.assertListEqual(messages, [
            'If an external plugin is used the the "external_plugin_location" must be set.'
        ])

    def test_eternal_plugin_failed(self):
        self.section.external_plugin_location = '/path/to/external/plugin'
        validator = CommonSectionValidator(section=self.section)
        valid, messages = validator.validate()
        self.assertFalse(valid)
        self.assertListEqual(messages, ['If an external plugin is used the the "external_plugin" must be set.'])

    def test_directories_failed(self):
        self.section.standard_names_dir = '/not/existing/standard_names_dir'
        self.section.root_replacement_coordinates_dir = '/not/existing/replacement_coordinates_dir'
        self.section.root_hybrid_heights_dir = '/not/existing/hybrid_heights_dir'
        self.section.root_ancil_dir = '/not/existing/ancil_dir'
        self.section.mip_table_dir = '/not/existing/mip_table_dir'

        validator = CommonSectionValidator(section=self.section)
        valid, messages = validator.validate()

        self.assertFalse(valid)
        self.assertListEqual(messages, ['The "standard_names_dir" does not exist.',
                                        'The "root_replacement_coordinates_dir" does not exist.',
                                        'The "root_hybrid_heights_dir" does not exist.',
                                        'The "root_ancil_dir" does not exist.',
                                        'The "mip_table_dir" does not exist.'])

    def test_file_failed(self):
        self.section.sites_file = '/not/existing/sites.file'
        validator = CommonSectionValidator(section=self.section)
        valid, messages = validator.validate()
        self.assertFalse(valid)
        self.assertListEqual(messages, ['The "sites_file" does not exist.'])


class TestMetdataValidator(TestCase):

    def setUp(self):
        load_plugin()
        defaults = metadata_defaults('UKESM1-0-LL')
        values = {
            'branch_method': 'no parent',
            'calendar': '360_day',
            'mip': 'CMIP',
            'experiment_id': 'piControl',
            'mip_era': 'CMIP6',
            'model_id': 'UKESM1-0-LL',
            'variant_label': 'r1i1p1f1'
        }
        values.update(defaults)
        self.section = MetadataSection(**values)

    def test_validation_succeed(self):
        validator = MetadataSectionValidator(section=self.section)
        valid, messages = validator.validate()
        self.assertTrue(valid)
        self.assertListEqual(messages, [])

    def test_allowed_values_failed(self):
        self.section.branch_method = 'unknown'
        self.section.calendar = 'julian'
        validator = MetadataSectionValidator(section=self.section)
        valid, messages = validator.validate()
        self.assertFalse(valid)
        self.assertListEqual(messages, ['The "branch_method" must be set to "no parent, standard".',
                                        'The "calendar" must be set to "360_day, gregorian".'])

    def test_values_not_set(self):
        self.section.mip = ''
        self.section.base_date = None
        self.section.experiment_id = ''
        self.section.mip_era = ''
        self.section.model_id = ''
        self.section.variant_label = ''

        validator = MetadataSectionValidator(section=self.section)
        valid, messages = validator.validate()

        self.assertFalse(valid)
        self.assertListEqual(messages, [
            'Property "mip" must be set.',
            'Property "base_date" must be set.',
            'Property "experiment_id" must be set.',
            'Property "mip_era" must be set.',
            'Property "model_id" must be set.',
            'Property "variant_label" must be set.'
        ])

    def test_parent_values_not_set(self):
        self.section.branch_method = 'standard'

        validator = MetadataSectionValidator(section=self.section)
        valid, messages = validator.validate()

        self.assertFalse(valid)
        self.assertListEqual(messages, ['Property "parent_experiment_id" must be set.',
                                        'Property "parent_mip" must be set.',
                                        'Property "parent_mip_era" must be set.',
                                        'Property "branch_date_in_child" must be set.',
                                        'Property "branch_date_in_parent" must be set.'])


class TestSectionValidatorFactory(TestCase):

    def test_allowed_values_succeed(self):
        allowed_values = ['no parent', 'standard']
        validate_func = SectionValidatorFactory.allowed_values_validator()
        valid, message = validate_func('standard', allowed_values, 'branch_method')
        self.assertTrue(valid)
        self.assertEqual(message, '')

    def test_allowed_values_failed(self):
        allowed_values = ['no parent', 'standard']
        validate_func = SectionValidatorFactory.allowed_values_validator()
        valid, message = validate_func('not allowed', allowed_values, 'branch_method')
        self.assertFalse(valid)
        self.assertEqual(message, 'The "branch_method" must be set to "no parent, standard".')

    def test_directory_succeed(self):
        temp_dir = tempfile.mkdtemp()
        validate_func = SectionValidatorFactory.directory_validator()
        valid, message = validate_func(temp_dir, 'mip_table_dir')
        self.assertTrue(valid)
        self.assertEqual(message, '')

    def test_directory_failed(self):
        not_existing_dir = '/not/existing/dir'
        validate_func = SectionValidatorFactory.directory_validator()
        valid, message = validate_func(not_existing_dir, 'mip_table_dir')
        self.assertFalse(valid)
        self.assertEqual(message, 'The "mip_table_dir" does not exist.')

    def test_file_succeed(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write('something'.encode())

            validate_func = SectionValidatorFactory.file_validator()
            valid, message = validate_func(temp_file.name, 'sites_file')
            self.assertTrue(valid)
            self.assertEqual(message, '')
            temp_file.close()

    def test_file_failed(self):
        not_exising_file = '/not/existing/file.txt'
        validate_func = SectionValidatorFactory.file_validator()
        valid, message = validate_func(not_exising_file, 'sites_file')
        self.assertFalse(valid)
        self.assertEqual(message, 'The "sites_file" does not exist.')

    def test_external_plugin_succeed(self):
        validate_func = SectionValidatorFactory.external_plugin_validator()
        valid, message = validate_func('arise.plugin', '/path/to/plugin/location')
        self.assertTrue(valid)
        self.assertEqual(message, '')

    def test_no_external_plugin_failed(self):
        validate_func = SectionValidatorFactory.external_plugin_validator()
        valid, message = validate_func('arise.plugin', '')
        self.assertFalse(valid)
        self.assertEqual(message, 'If an external plugin is used the the "external_plugin_location" must be set.')

    def test_no_external_plugin_location_failed(self):
        validate_func = SectionValidatorFactory.external_plugin_validator()
        valid, message = validate_func('', '/path/to/external/plugin')
        self.assertFalse(valid)
        self.assertEqual(message, 'If an external plugin is used the the "external_plugin" must be set.')

    def test_no_external_plugin_configured(self):
        validate_func = SectionValidatorFactory.external_plugin_validator()
        valid, message = validate_func('', '')
        self.assertTrue(valid)
        self.assertEqual(message, '')

    def test_start_before_end_succeed(self):
        start = TimePoint(year=1990, month_of_year=1, day_of_month=1)
        end = TimePoint(year=1990, month_of_year=1, day_of_month=2)

        validate_func = SectionValidatorFactory.start_before_end_validator()
        valid, message = validate_func(start, end, 'start_date', 'end_date')

        self.assertTrue(valid)
        self.assertEqual(message, '')

    def test_start_equals_end_failed(self):
        start = TimePoint(year=1990, month_of_year=1, day_of_month=1)
        end = TimePoint(year=1990, month_of_year=1, day_of_month=1)

        validate_func = SectionValidatorFactory.start_before_end_validator()
        valid, message = validate_func(start, end, 'start_date', 'end_date')
        self.assertFalse(valid)
        self.assertEqual(message, '"start_date" must be before "end_date"')

    def test_start_after_end_failed(self):
        start = TimePoint(year=1990, month_of_year=1, day_of_month=2)
        end = TimePoint(year=1990, month_of_year=1, day_of_month=1)

        validate_func = SectionValidatorFactory.start_before_end_validator()
        valid, message = validate_func(start, end, 'start_date', 'end_date')
        self.assertFalse(valid)
        self.assertEqual(message, '"start_date" must be before "end_date"')

    def test_value_exist_succeed(self):
        validate_func = SectionValidatorFactory.exist_validator()
        valid, message = validate_func('CMIP6', 'mip_era')
        self.assertTrue(valid)
        self.assertEqual(message, '')

    def test_value_none_failed(self):
        validate_func = SectionValidatorFactory.exist_validator()
        valid, message = validate_func(None, 'mip_era')
        self.assertFalse(valid)
        self.assertEqual(message, 'Property "mip_era" must be set.')

    def test_value_empty_failed(self):
        validate_func = SectionValidatorFactory.exist_validator()
        valid, message = validate_func('', 'mip_era')
        self.assertFalse(valid)
        self.assertEqual(message, 'Property "mip_era" must be set.')

    def test_value_blank_failed(self):
        validate_func = SectionValidatorFactory.exist_validator()
        valid, message = validate_func('    ', 'mip_era')
        self.assertFalse(valid)
        self.assertEqual(message, 'Property "mip_era" must be set.')


if __name__ == '__main__':
    unittest.main()
