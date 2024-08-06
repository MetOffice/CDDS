# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import tempfile
import unittest

from metomi.isodatetime.data import TimePoint
from unittest import TestCase

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.request.metadata_section import MetadataSection, metadata_defaults
from cdds.common.request.common_section import CommonSection, common_defaults
from cdds.common.request.data_section import DataSection, data_defaults
from cdds.common.request.inventory_section import InventorySection, inventory_defaults
from cdds.common.request.request_validations import (validate_common_section, validate_metadata_section,
                                                     validate_data_section, validate_inventory_section,
                                                     validate_request)


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
        self.section = DataSection(**defaults)

    def test_start_date_before_end_date_succeed(self):
        self.section.start_date = TimePoint(year=1990, month_of_year=1, day_of_month=1)
        self.section.end_date = TimePoint(year=2010, month_of_year=1, day_of_month=1)
        validate_data_section(self.section)

    def test_start_date_after_end_date_failed(self):
        self.section.start_date = TimePoint(year=2010, month_of_year=1, day_of_month=1)
        self.section.end_date = TimePoint(year=1990, month_of_year=1, day_of_month=1)
        self.assertRaises(AttributeError, validate_data_section, self.section)


class TestValidateMetadataSection(TestCase):

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

    def test_metadata_values_succeed(self):
        validate_metadata_section(self.section)

    def test_metadata_values_failed(self):
        self.section.calendar = 'julian'
        self.assertRaises(AttributeError, validate_metadata_section, self.section)


if __name__ == '__main__':
    unittest.main()
