# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import unittest

from cdds import __version__
from cdds.common.request_defaults import (
    metadata_defaults, common_defaults, data_defaults, misc_defaults, inventory_defaults, conversion_defaults
)
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.cmip6.cmip6_plugin import CMIP6_LICENSE
from cdds.common.platforms import Facility

from datetime import datetime
from metomi.isodatetime.data import TimePoint
from unittest import TestCase, mock


class TestMetadataDefaults(TestCase):
    def setUp(self) -> None:
        load_plugin('CMIP6')
        self.model_id = 'UKESM1-0-LL'

    def tearDown(self) -> None:
        PluginStore.clean_instance()

    @mock.patch('cdds.common.request_defaults.whereami')
    def test_defaults_for_jasmin(self, whereami_mock):
        whereami_mock.return_value = Facility.JASMIN
        expected_defaults = {
            'calendar': '360_day',
            'child_base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
            'license': CMIP6_LICENSE,
            'parent_base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
            'parent_model_id': self.model_id,
            'parent_time_units': 'days since 1850-01-01',
            'standard_names_dir': '/gws/smf/j04/cmip6_prep/cdds-env-python3/etc/standard_names/',
            'standard_names_version': 'latest',
        }

        defaults = metadata_defaults(self.model_id)

        self.assertDictEqual(defaults, expected_defaults)

    @mock.patch('cdds.common.request_defaults.whereami')
    def test_defaults_for_metoffice(self, whereami_mock):
        whereami_mock.return_value = Facility.MET_OFFICE
        expected_defaults = {
            'calendar': '360_day',
            'child_base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
            'license': CMIP6_LICENSE,
            'parent_base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
            'parent_model_id': self.model_id,
            'parent_time_units': 'days since 1850-01-01',
            'standard_names_dir': '/home/h03/cdds/etc/standard_names/',
            'standard_names_version': 'latest',
        }

        defaults = metadata_defaults(self.model_id)

        self.assertDictEqual(defaults, expected_defaults)


class TestCommonDefaults(TestCase):
    def setUp(self) -> None:
        load_plugin('CMIP6')
        self.model_id = 'UKESM1-0-LL'
        self.experiment_id = 'piControl'
        self.variant_label = 'r1i1p1f1'
        self.workflow_basename = '{}_{}_{}'.format(self.model_id, self.experiment_id, self.variant_label)

    def tearDown(self) -> None:
        PluginStore.clean_instance()

    @mock.patch('cdds.common.request_defaults.datetime')
    @mock.patch('cdds.common.request_defaults.whereami')
    @mock.patch('cdds.common.plugins.cmip6.cmip6_plugin.whereami')
    def test_defaults_for_jasmin(self, whereami_plugin_mock, whereami_mock, datetime_mock):
        data_version = datetime.utcnow()
        whereami_plugin_mock.return_value = Facility.JASMIN
        whereami_mock.return_value = Facility.JASMIN
        datetime_mock.utcnow.return_value = data_version
        expected_defaults = {
            'cdds_version': __version__,
            'data_version': data_version.strftime('%Y-%m-%dT%H%MZ'),
            'external_plugin': '',
            'external_plugin_location': '',
            'log_level': 'INFO',
            'mip_table_dir': '/gws/smf/j04/cmip6_prep/cdds-env-python3/etc/mip_tables/CMIP6/',
            'mode': 'strict',
            'root_ancil_dir': '/gws/smf/j04/cmip6_prep/cdds-env-python3/etc/ancil/',
            'root_data_dir': '/project/cdds_data',
            'root_proc_dir': '/project/cdds/proc',
            'simulation': False,
            'workflow_basename': self.workflow_basename
        }

        defaults = common_defaults(self.model_id, self.experiment_id, self.variant_label)

        self.assertDictEqual(defaults, expected_defaults)

    @mock.patch('cdds.common.request_defaults.datetime')
    @mock.patch('cdds.common.request_defaults.whereami')
    @mock.patch('cdds.common.plugins.cmip6.cmip6_plugin.whereami')
    def test_defaults_for_metoffice(self, whereami_plugin_mock, whereami_mock, datetime_mock):
        data_version = datetime.utcnow()
        whereami_plugin_mock.return_value = Facility.MET_OFFICE
        whereami_mock.return_value = Facility.MET_OFFICE
        datetime_mock.utcnow.return_value = data_version
        expected_defaults = {
            'cdds_version': __version__,
            'data_version': data_version.strftime('%Y-%m-%dT%H%MZ'),
            'external_plugin': '',
            'external_plugin_location': '',
            'log_level': 'INFO',
            'mip_table_dir': '/home/h03/cdds/etc/mip_tables/CMIP6/',
            'mode': 'strict',
            'root_ancil_dir': '/home/h03/cdds/etc/ancil/',
            'root_data_dir': '/project/cdds_data',
            'root_proc_dir': '/project/cdds/proc',
            'simulation': False,
            'workflow_basename': self.workflow_basename
        }

        defaults = common_defaults(self.model_id, self.experiment_id, self.variant_label)

        self.assertDictEqual(defaults, expected_defaults)


class TestDataDefaults(TestCase):
    def test_defaults(self):
        expected_defaults = {
            "mass_data_class": 'crum',
            "output_mass_root": "moose:/adhoc/projects/cdds/",
            "output_mass_suffix": "development",
            "streams": "ap4 ap5 ap6 inm onm",
            "workflow_branch": 'cdds',
            "worklow_revision": 'HEAD'
        }

        defaults = data_defaults()

        self.assertDictEqual(defaults, expected_defaults)


class TestMiscDefaults(TestCase):
    def setUp(self) -> None:
        load_plugin('CMIP6')
        self.model_id = 'UKESM1-0-LL'

    def tearDown(self) -> None:
        PluginStore.clean_instance()

    def test_defaults(self):
        expected_defaults = {
            "atmos_timestep": 1200
        }

        defaults = misc_defaults(self.model_id)

        self.assertDictEqual(defaults, expected_defaults)


class TestInventoryDefaults(TestCase):
    def setUp(self) -> None:
        self.mips = [
            'AerChemMIP',
            'C4MIP',
            'CDRMIP',
            'CFMIP',
            'CMIP',
            'CORDEX',
            'DAMIP',
            'DCPP',
            'DynVar',
            'FAFMIP',
            'GeoMIP',
            'GMMIP',
            'HighResMIP',
            'ISMIP6',
            'LS3MIP',
            'LUMIP',
            'OMIP',
            'PAMIP',
            'PMIP',
            'RFMIP',
            'ScenarioMIP',
            'SIMIP',
            'VIACSAB',
            'VolMIP'
        ]

    @mock.patch('cdds.common.request_defaults.whereami')
    def test_defaults_for_jasmin(self, whereami_mock):
        whereami_mock.return_value = Facility.JASMIN
        expected_defaults = {
            "inventory_check": True,
            "inventory_database_location": '/gws/smf/j04/cmip6_prep/cdds-env-python3/etc/inventory/inventory.db',
            "no_auto_deactivation": False,
            'data_request_version': '01.00.29',
            'data_request_base_dir': '/gws/smf/j04/cmip6_prep/cdds-env-python3/etc/data_requests/CMIP6/',
            'mips_to_contribute_to': self.mips,
            'mapping_status': 'ok',
            'use_proc_dir': False,
            'max_priority': 2,
            'no_overwrite': False
        }

        defaults = inventory_defaults()

        self.assertDictEqual(defaults, expected_defaults)

    @mock.patch('cdds.common.request_defaults.whereami')
    def test_defaults_for_metoffice(self, whereami_mock):
        whereami_mock.return_value = Facility.MET_OFFICE
        expected_defaults = {
            "inventory_check": True,
            "inventory_database_location": '/project/cdds/inventory/inventory.db',
            "no_auto_deactivation": False,
            'data_request_version': '01.00.29',
            'data_request_base_dir': '/home/h03/cdds/etc/data_requests/CMIP6',
            'mips_to_contribute_to': self.mips,
            'mapping_status': 'ok',
            'use_proc_dir': False,
            'max_priority': 2,
            'no_overwrite': False
        }

        defaults = inventory_defaults()

        self.assertDictEqual(defaults, expected_defaults)


class TestConversionDefaults(TestCase):

    @mock.patch('cdds.common.request_defaults.whereami')
    def test_defaults_for_jasmin(self, whereami_mock):
        whereami_mock.return_value = Facility.JASMIN
        expected_defaults = {
            "cdds_workflow_branch": "cdds_jasmin_2.3",
            "no_email_notifications": False,
            "skip_extract": True,
            "skip_extract_validation": False,
            "skip_configure": False,
            "skip_qc": False,
            "skip_archive": True
        }

        defaults = conversion_defaults()

        self.assertDictEqual(defaults, expected_defaults)

    @mock.patch('cdds.common.request_defaults.whereami')
    def test_defaults_for_metoffice(self, whereami_mock):
        whereami_mock.return_value = Facility.MET_OFFICE
        expected_defaults = {
            "cdds_workflow_branch": "trunk",
            "no_email_notifications": False,
            "skip_extract": False,
            "skip_extract_validation": False,
            "skip_configure": False,
            "skip_qc": False,
            "skip_archive": False
        }

        defaults = conversion_defaults()

        self.assertDictEqual(defaults, expected_defaults)


if __name__ == "__main__":
    unittest.main()
