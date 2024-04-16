# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.
import unittest

from configparser import ConfigParser
from metomi.isodatetime.data import TimePoint
from unittest import TestCase

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.cmip6.cmip6_plugin import CMIP6_LICENSE
from cdds.common.request.metadata_section import MetadataSection, metadata_defaults


class TestMetadataDefaults(TestCase):
    def setUp(self) -> None:
        load_plugin('CMIP6')
        self.model_id = 'UKESM1-0-LL'

    def tearDown(self) -> None:
        PluginStore.clean_instance()

    def test_defaults(self):
        expected_defaults = {
            'base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
            'license': CMIP6_LICENSE,
            'parent_base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
            'parent_model_id': self.model_id,
            'parent_time_units': 'days since 1850-01-01',
            'standard_names_dir': '/home/h03/cdds/etc/standard_names/',
            'standard_names_version': 'latest',
        }

        defaults = metadata_defaults(self.model_id)

        self.assertDictEqual(defaults, expected_defaults)


class TestMetadataSection(TestCase):

    def setUp(self) -> None:
        load_plugin('CMIP6')

    def tearDown(self) -> None:
        PluginStore.clean_instance()

    def test_items(self):
        metadata = MetadataSection(
            branch_date_in_child=TimePoint(year=1999, month_of_year=1, day_of_month=1),
            branch_date_in_parent=TimePoint(year=1992, month_of_year=1, day_of_month=1),
            branch_method='standard',
            base_date=TimePoint(year=2002, month_of_year=1, day_of_month=1),
            calendar='360_day',
            experiment_id='piControl',
            institution_id='MOHC',
            license='CMIP6 model data produced by MOHC',
            mip='CMIP',
            mip_era='CMIP6',
            parent_base_date=TimePoint(year=1850, month_of_year=1, day_of_month=1),
            parent_experiment_id='amip',
            parent_mip='CMIP',
            parent_mip_era='CMIP6',
            parent_model_id='UKESM1-0-LL',
            parent_time_units='days since 1850-01-01',
            parent_variant_label='r1i1p1f2',
            sub_experiment_id='none',
            variant_label='r1i2p3f4',
            standard_names_version='62',
            standard_names_dir='/home/h04/cdds/standard_names',
            model_id='HadGEM3-GC31-LL',
            model_type=['AOGCM']
        )

        expected_items = {
            'branch_date_in_child': TimePoint(year=1999, month_of_year=1, day_of_month=1),
            'branch_date_in_parent': TimePoint(year=1992, month_of_year=1, day_of_month=1),
            'branch_method': 'standard',
            'calendar': '360_day',
            'base_date': TimePoint(year=2002, month_of_year=1, day_of_month=1),
            'experiment_id': 'piControl',
            'institution_id': 'MOHC',
            'license': 'CMIP6 model data produced by MOHC',
            'mip': 'CMIP',
            'mip_era': 'CMIP6',
            'model_id': 'HadGEM3-GC31-LL',
            'model_type': ['AOGCM'],
            'parent_base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
            'parent_experiment_id': 'amip',
            'parent_mip': 'CMIP',
            'parent_mip_era': 'CMIP6',
            'parent_model_id': 'UKESM1-0-LL',
            'parent_time_units': 'days since 1850-01-01',
            'parent_variant_label': 'r1i1p1f2',
            'standard_names_dir': '/home/h04/cdds/standard_names',
            'standard_names_version': '62',
            'sub_experiment_id': 'none',
            'variant_label': 'r1i2p3f4'
        }

        self.assertDictEqual(metadata.items, expected_items)

    def test_from_config_only_defaults(self):
        config = ConfigParser()
        config.add_section('metadata')
        config.set('metadata', 'model_id', 'HadGEM3-GC31-LL')

        metadata = MetadataSection.from_config(config)

        self.assertEqual(metadata.calendar, '')
        self.assertEqual(metadata.base_date, TimePoint(year=1850, month_of_year=1, day_of_month=1))
        self.assertEqual(metadata.license, CMIP6_LICENSE)
        self.assertEqual(metadata.parent_base_date, TimePoint(year=1850, month_of_year=1, day_of_month=1))
        self.assertEqual(metadata.parent_experiment_id, '')
        self.assertEqual(metadata.parent_model_id, 'HadGEM3-GC31-LL')
        self.assertEqual(metadata.parent_time_units, 'days since 1850-01-01')
        self.assertEqual(metadata.standard_names_dir, '/home/h03/cdds/etc/standard_names/')
        self.assertEqual(metadata.standard_names_version, 'latest')
        self.assertEqual(metadata.branch_date_in_child, None)
        self.assertEqual(metadata.branch_date_in_parent, None)
        self.assertEqual(metadata.branch_method, '')
        self.assertEqual(metadata.experiment_id, '')
        self.assertEqual(metadata.institution_id, '')
        self.assertEqual(metadata.mip, '')
        self.assertEqual(metadata.mip_era, '')
        self.assertEqual(metadata.parent_mip, '')
        self.assertEqual(metadata.parent_mip_era, '')
        self.assertEqual(metadata.parent_variant_label, '')
        self.assertEqual(metadata.sub_experiment_id, 'none')
        self.assertEqual(metadata.variant_label, '')
        self.assertEqual(metadata.model_id, 'HadGEM3-GC31-LL')
        self.assertEqual(metadata.model_type, [])

    def test_from_config(self):
        config = ConfigParser()
        config.add_section('metadata')
        config.set('metadata', 'branch_date_in_child', '1999-01-01')
        config.set('metadata', 'branch_date_in_parent', '1992-01-01')
        config.set('metadata', 'branch_method', 'standard')
        config.set('metadata', 'base_date', '2002-01-01')
        config.set('metadata', 'calendar', '360_day')
        config.set('metadata', 'experiment_id', 'piControl')
        config.set('metadata', 'institution_id', 'MOHC')
        config.set('metadata', 'license', 'CMIP6 model data produced by MOHC')
        config.set('metadata', 'mip', 'CMIP')
        config.set('metadata', 'mip_era', 'CMIP6')
        config.set('metadata', 'parent_experiment_id', 'amip')
        config.set('metadata', 'parent_mip', 'CMIP')
        config.set('metadata', 'parent_mip_era', 'CMIP6')
        config.set('metadata', 'parent_model_id', 'UKESM1-0-LL')
        config.set('metadata', 'parent_time_units', 'days since 1850-01-01')
        config.set('metadata', 'parent_variant_label', 'r1i1p1f2')
        config.set('metadata', 'sub_experiment_id', 'none')
        config.set('metadata', 'variant_label', 'r1i2p3f4')
        config.set('metadata', 'standard_names_version', '6.2.0')
        config.set('metadata', 'standard_names_dir', '/home/h04/cdds/standard_names')
        config.set('metadata', 'model_id', 'HadGEM3-GC31-LL')
        config.set('metadata', 'model_type', 'AOGCM BGC AER CHEM')

        metadata = MetadataSection.from_config(config)

        self.assertEqual(metadata.branch_date_in_child, TimePoint(year=1999, month_of_year=1, day_of_month=1))
        self.assertEqual(metadata.branch_date_in_parent, TimePoint(year=1992, month_of_year=1, day_of_month=1))
        self.assertEqual(metadata.branch_method, 'standard')
        self.assertEqual(metadata.base_date, TimePoint(year=2002, month_of_year=1, day_of_month=1))
        self.assertEqual(metadata.calendar, '360_day')
        self.assertEqual(metadata.experiment_id, 'piControl')
        self.assertEqual(metadata.institution_id, 'MOHC')
        self.assertEqual(metadata.license, 'CMIP6 model data produced by MOHC')
        self.assertEqual(metadata.mip, 'CMIP')
        self.assertEqual(metadata.mip_era, 'CMIP6')
        self.assertEqual(metadata.parent_base_date, TimePoint(year=1850, month_of_year=1, day_of_month=1))
        self.assertEqual(metadata.parent_experiment_id, 'amip')
        self.assertEqual(metadata.parent_mip, 'CMIP')
        self.assertEqual(metadata.parent_mip_era, 'CMIP6')
        self.assertEqual(metadata.parent_model_id, 'UKESM1-0-LL')
        self.assertEqual(metadata.parent_time_units, 'days since 1850-01-01')
        self.assertEqual(metadata.parent_variant_label, 'r1i1p1f2')
        self.assertEqual(metadata.sub_experiment_id, 'none')
        self.assertEqual(metadata.variant_label, 'r1i2p3f4')
        self.assertEqual(metadata.standard_names_version, '6.2.0')
        self.assertEqual(metadata.standard_names_dir, '/home/h04/cdds/standard_names')
        self.assertEqual(metadata.model_id, 'HadGEM3-GC31-LL')
        self.assertListEqual(metadata.model_type, ['AOGCM', 'BGC', 'AER', 'CHEM'])


if __name__ == '__main__':
    unittest.main()
