# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from cdds.common.plugins.cordex.cordex_attributes import CordexGlobalAttributes

from unittest import TestCase


class TestCordexGlobalAttributes(TestCase):

    def setUp(self):
        self.request = {
            'institution_id': 'MOHC',
            'model_id': 'HadGEM3-GC31-MM',
            'experiment_id': 'piControl',
            'sub_experiment_id': 'none',
            'variant_label': 'r1i1p1f2'
        }

    def test_further_info_url(self):
        attributes = CordexGlobalAttributes(self.request)
        further_info_url = attributes.further_info_url()
        self.assertEqual(further_info_url, '')
