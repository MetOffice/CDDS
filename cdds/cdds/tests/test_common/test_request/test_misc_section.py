# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from unittest import TestCase

from cdds.common.request.misc_section import misc_defaults
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.plugin_loader import load_plugin


class TestMiscDefaults(TestCase):
    def setUp(self) -> None:
        load_plugin('CMIP6')
        self.model_id = 'UKESM1-0-LL'
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

    def tearDown(self) -> None:
        PluginStore.clean_instance()

    def test_defaults(self):
        expected_defaults = {
            'atmos_timestep': 1200,
            'no_auto_deactivation': False,
            'data_request_version': '01.00.29',
            'data_request_base_dir': '/home/h03/cdds/etc/data_requests/CMIP6',
            'mips_to_contribute_to': self.mips,
            'mapping_status': 'ok',
            'use_proc_dir': False,
            'max_priority': 2,
            'no_overwrite': False
        }

        defaults = misc_defaults(self.model_id)

        self.assertDictEqual(defaults, expected_defaults)
