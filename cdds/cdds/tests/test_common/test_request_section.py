# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from configparser import ConfigParser
from unittest import TestCase, mock

from cdds.common.platforms import Facility
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.cmip6.cmip6_plugin import CMIP6_LICENSE
from cdds.common.request_section import MetadataSection


class TestMetadataSection(TestCase):

    def setUp(self) -> None:
        load_plugin('CMIP6')

    def tearDown(self) -> None:
        PluginStore.clean_instance()

    def test_items(self):
        metadata = MetadataSection(
            branch_date_in_child='1999-01-01',
            branch_date_in_parent='1992-01-01',
            branch_method='standard',
            child_base_date='2002-01-01',
            calendar='360_day',
            experiment_id='piControl',
            institution_id='MOHC',
            license='CMIP6 model data produced by MOHC',
            mip='CMIP',
            mip_era='CMIP6',
            parent_base_date='1850-01-01',
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
            model_type='AOGCM'
        )

        expected_items = {
            'branch_date_in_child': '1999-01-01',
            'branch_date_in_parent': '1992-01-01',
            'branch_method': 'standard',
            'calendar': '360_day',
            'child_base_date': '2002-01-01',
            'experiment_id': 'piControl',
            'institution_id': 'MOHC',
            'license': 'CMIP6 model data produced by MOHC',
            'mip': 'CMIP',
            'mip_era': 'CMIP6',
            'model_id': 'HadGEM3-GC31-LL',
            'model_type': 'AOGCM',
            'parent_base_date': '1850-01-01',
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

    @mock.patch('cdds.common.request_defaults.whereami')
    def test_from_config_only_defaults(self, whereami_mock):
        whereami_mock.return_value = Facility.MET_OFFICE
        config = ConfigParser()
        config.add_section('metadata')
        config.set('metadata', 'model_id', 'HadGEM3-GC31-LL')

        metadata = MetadataSection.from_config(config)

        self.assertEqual(metadata.calendar, '360_day')
        self.assertEqual(metadata.child_base_date, '1850-01-01')
        self.assertEqual(metadata.license, CMIP6_LICENSE)
        self.assertEqual(metadata.parent_base_date, '1850-01-01')
        self.assertEqual(metadata.parent_experiment_id, '')
        self.assertEqual(metadata.parent_model_id, 'HadGEM3-GC31-LL')
        self.assertEqual(metadata.parent_time_units, 'days since 1850-01-01')
        self.assertEqual(metadata.standard_names_dir, '/home/h03/cdds/etc/standard_names/')
        self.assertEqual(metadata.standard_names_version, 'latest')
        self.assertEqual(metadata.branch_date_in_child, '')
        self.assertEqual(metadata.branch_date_in_parent, '')
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
        self.assertEqual(metadata.model_type, '')

    @mock.patch('cdds.common.request_defaults.whereami')
    def test_from_config(self, whereami_mock):
        whereami_mock.return_value = Facility.MET_OFFICE
        config = ConfigParser()
        config.add_section('metadata')
        config.set('metadata', 'branch_date_in_child', '1999-01-01')
        config.set('metadata', 'branch_date_in_parent', '1992-01-01')
        config.set('metadata', 'branch_method', 'standard')
        config.set('metadata', 'child_base_date', '2002-01-01')
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
        config.set('metadata', 'standard_names_version', '62')
        config.set('metadata', 'standard_names_dir', '/home/h04/cdds/standard_names')
        config.set('metadata', 'model_id', 'HadGEM3-GC31-LL')
        config.set('metadata', 'model_type', 'AOGCM')

        metadata = MetadataSection.from_config(config)

        self.assertEqual(metadata.branch_date_in_child, '1999-01-01')
        self.assertEqual(metadata.branch_date_in_parent, '1992-01-01')
        self.assertEqual(metadata.branch_method, 'standard')
        self.assertEqual(metadata.child_base_date, '2002-01-01')
        self.assertEqual(metadata.calendar, '360_day')
        self.assertEqual(metadata.experiment_id, 'piControl')
        self.assertEqual(metadata.institution_id, 'MOHC')
        self.assertEqual(metadata.license, 'CMIP6 model data produced by MOHC')
        self.assertEqual(metadata.mip, 'CMIP')
        self.assertEqual(metadata.mip_era, 'CMIP6')
        self.assertEqual(metadata.parent_base_date, '1850-01-01')
        self.assertEqual(metadata.parent_experiment_id, 'amip')
        self.assertEqual(metadata.parent_mip, 'CMIP')
        self.assertEqual(metadata.parent_mip_era, 'CMIP6')
        self.assertEqual(metadata.parent_model_id, 'UKESM1-0-LL')
        self.assertEqual(metadata.parent_time_units, 'days since 1850-01-01')
        self.assertEqual(metadata.parent_variant_label, 'r1i1p1f2')
        self.assertEqual(metadata.sub_experiment_id, 'none')
        self.assertEqual(metadata.variant_label, 'r1i2p3f4')
        self.assertEqual(metadata.standard_names_version, '62')
        self.assertEqual(metadata.standard_names_dir, '/home/h04/cdds/standard_names')
        self.assertEqual(metadata.model_id, 'HadGEM3-GC31-LL')
        self.assertEqual(metadata.model_type, 'AOGCM')
