# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.
from datetime import datetime
from unittest import TestCase, mock

from cdds import __version__
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.request.common_section import common_defaults


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
            'external_plugin': '',
            'external_plugin_location': '',
            'log_level': 'INFO',
            'mip_table_dir': '/data/users/cdds/etc/mip_tables/CMIP6/01.00.29',
            'mode': 'strict',
            'root_ancil_dir': '/data/users/cdds/etc/ancil',
            'root_hybrid_heights_dir': '/data/users/cdds/etc/vertical_coordinates',
            'root_replacement_coordinates_dir': '/data/users/cdds/etc/horizontal_coordinates',
            'simulation': False,
            'sites_file': '/data/users/cdds/etc/cfsites/cfmip2-sites-orog.txt',
            'standard_names_dir': '/data/users/cdds/etc/standard_names',
            'standard_names_version': 'latest',
            'workflow_basename': self.workflow_basename
        }

        defaults = common_defaults(self.model_id, self.experiment_id, self.variant_label)

        self.assertDictEqual(defaults, expected_defaults)
