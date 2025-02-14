# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
import os
from datetime import datetime
from unittest import TestCase, mock

from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.request.common_section import common_defaults, CommonSection


class TestCommonDefaults(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        load_plugin('CMIP6')
        self.model_id = 'UKESM1-0-LL'
        self.experiment_id = 'piControl'
        self.variant_label = 'r1i1p1f1'
        self.workflow_basename = '{}_{}_{}'.format(self.model_id, self.experiment_id, self.variant_label)

    def tearDown(self) -> None:
        PluginStore.clean_instance()

    def test_defaults(self):
        expected_defaults = {
            'force_plugin': '',
            'external_plugin': '',
            'external_plugin_location': '',
            'log_level': 'INFO',
            'mip_table_dir': os.path.join(os.environ['CDDS_ETC'], 'mip_tables', 'CMIP6', '01.00.29'),
            'mode': 'strict',
            'root_ancil_dir': os.path.join(os.environ['CDDS_ETC'], 'ancil'),
            'root_hybrid_heights_dir': os.path.join(os.environ['CDDS_ETC'], 'vertical_coordinates'),
            'root_replacement_coordinates_dir': os.path.join(os.environ['CDDS_ETC'], 'horizontal_coordinates'),
            'simulation': False,
            'sites_file': os.path.join(os.environ['CDDS_ETC'], 'cfmip2', 'cfmip2-sites-orog.txt'),
            'standard_names_dir': os.path.join(os.environ['CDDS_ETC'], 'standard_names'),
            'standard_names_version': 'latest',
            'workflow_basename': self.workflow_basename
        }

        defaults = common_defaults(self.model_id, self.experiment_id, self.variant_label)
        self.assertDictEqual(defaults, expected_defaults)


class TestPostInitChecks(TestCase):

    def setUp(self):
        load_plugin()

    def test_post_init_check_succeed(self):
        CommonSection(
            external_plugin='',
            external_plugin_location='',
            mip_table_dir='',
            mode='strict',
            package='',
            workflow_basename='',
            root_proc_dir='',
            root_data_dir='',
            root_ancil_dir='',
            root_hybrid_heights_dir='',
            root_replacement_coordinates_dir='',
            sites_file='',
            standard_names_version='latest',
            standard_names_dir='',
            simulation=False,
            log_level='INFO'
        )

    def test_post_init_check_defaults_succeed(self):
        defaults = common_defaults('UKESM1-0-LL', 'piControl', 'r1i1p1f1')
        CommonSection(**defaults)

    def test_post_init_check_failed(self):
        values = {
            'external_plugin': '',
            'external_plugin_location': '',
            'log_level': 'INFO',
            'mip_table_dir': '/not/existing/mip_table_dir',
            'mode': 'strict',
            'root_ancil_dir': '/not/existing/ancil_dir',
            'root_hybrid_heights_dir': '/not/existing/hybrid_heigths/dir',
            'root_replacement_coordinates_dir': '/not/existing/replacement_coordinates_dir',
            'sites_file': '/not/existing/site_file',
            'standard_names_dir': '/not/existing/standard_name_dir',
            'standard_names_version': 'latest',
            'simulation': False,
            'workflow_basename': '{}_{}_{}'.format('UKESM1-0-LL', 'piControl', 'r1i1p1f1')
        }

        self.assertRaises(AttributeError, CommonSection, **values)
