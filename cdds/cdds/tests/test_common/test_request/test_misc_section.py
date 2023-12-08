# (C) British Crown Copyright 2023-2023, Met Office.
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
            'mips_to_contribute_to': self.mips,
            'use_proc_dir': False,
            'max_priority': 2,
            'no_overwrite': False
        }

        defaults = misc_defaults(self.model_id)

        self.assertDictEqual(defaults, expected_defaults)
