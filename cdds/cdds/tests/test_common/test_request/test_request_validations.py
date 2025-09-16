# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
import tempfile
import unittest

from metomi.isodatetime.data import TimePoint
from unittest import TestCase

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.request.metadata_section import MetadataSection, metadata_defaults
from cdds.common.request.misc_section import MiscSection, misc_defaults
from cdds.common.request.common_section import CommonSection, common_defaults
from cdds.common.request.data_section import DataSection, data_defaults
from cdds.common.request.inventory_section import InventorySection, inventory_defaults
from cdds.common.request.request_validations import (validate_common_section, validate_metadata_section,
                                                     validate_data_section, validate_inventory_section,
                                                     validate_request, validate_misc_section)


class TestValidateCommonSection(TestCase):

    def setUp(self):
        load_plugin()
        defaults = common_defaults('UKESM1-0-LL', 'piControl', 'r1i1p1f1')
        self.section = CommonSection(**defaults)

    def test_validate_succeed(self):
        validate_common_section(self.section)

    def test_validate_failed(self):
        self.section.mip_table_dir = '/not/existing/mip_table_dir'
        self.assertRaises(AttributeError, validate_common_section, self.section)


class TestValidateInventorySection(TestCase):

    def setUp(self):
        defaults = inventory_defaults()
        self.section = InventorySection(**defaults)

    def test_no_inventory_check_succeed(self):
        validate_inventory_section(self.section)

    def test_inventory_db_set_succeed(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write('something'.encode())
            self.section.inventory_check = True
            self.section.inventory_database_location = temp_file.name
            validate_inventory_section(self.section)
            temp_file.close()

    def test_inventory_db_failed(self):
        self.section.inventory_check = True
        self.section.inventory_database_location = '/not/existing/inventory.db'
        self.assertRaises(AttributeError, validate_inventory_section, self.section)


class TestValidateDataSection(TestCase):

    def setUp(self):
        defaults = data_defaults()
        defaults['model_workflow_id'] = 'u-gs135'
        self.section = DataSection(**defaults)

    def test_start_date_before_end_date_succeed(self):
        self.section.start_date = TimePoint(year=1990, month_of_year=1, day_of_month=1)
        self.section.end_date = TimePoint(year=2010, month_of_year=1, day_of_month=1)
        validate_data_section(self.section)

    def test_start_date_after_end_date_failed(self):
        self.section.start_date = TimePoint(year=2010, month_of_year=1, day_of_month=1)
        self.section.end_date = TimePoint(year=1990, month_of_year=1, day_of_month=1)
        self.assertRaises(AttributeError, validate_data_section, self.section)

    def test_correct_workflow_id_format_succeed(self):
        validate_data_section(self.section)

    def test_incorrect_workflow_id_format_failed(self):
        for invalid_id in ['5-125', 'adf-fa223', 'ad-gwsgs', '3-', True, None, '']:
            with self.subTest(model_workflow_id=invalid_id):
                self.section.model_workflow_id = invalid_id
                self.assertRaises(AttributeError, validate_data_section, self.section)


class TestValidateMetadataSection(TestCase):

    def setUp(self):
        load_plugin()
        defaults = metadata_defaults('UKESM1-0-LL', 'no parent')
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

    def test_metadata_values_succeed(self):
        validate_metadata_section(self.section)

    def test_metadata_values_failed(self):
        self.section.calendar = 'julian'
        self.assertRaises(AttributeError, validate_metadata_section, self.section)


class TestMiscSection(TestCase):

    def setUp(self):
        load_plugin()
        defaults = misc_defaults('UKESM1-0-LL')
        self.section = MiscSection(**defaults)

    def test_misc_values_succed_if_halo_options_not_set(self):
        validate_misc_section(self.section)

    def test_misc_values_succeed_if_halo_options_are_set(self):
        self.section.halo_removal_latitude = '5:-5'
        self.section.halo_removal_longitude = '-1:-12'
        validate_misc_section(self.section)

    def test_misc_values_only_halo_removal_latitude_is_set(self):
        self.section.halo_removal_latitude = '5:-5'
        self.assertRaises(AttributeError, validate_misc_section, self.section)

    def test_misc_values_only_halo_removal_longitude_is_set(self):
        self.section.halo_removal_longitude = '5:-5'
        self.assertRaises(AttributeError, validate_misc_section, self.section)

    def test_misc_values_failed_because_halo_removal_latitude_not_matches_pattern(self):
        self.section.halo_removal_latitude = '5,-5'
        self.section.halo_removal_longitude = '-1:-12'
        self.assertRaises(AttributeError, validate_misc_section, self.section)

    def test_misc_values_failed_because_halo_removal_longitude_not_matches_pattern(self):
        self.section.halo_removal_latitude = '5:-5'
        self.section.halo_removal_longitude = 'h:-9'
        self.assertRaises(AttributeError, validate_misc_section, self.section)


if __name__ == '__main__':
    unittest.main()
