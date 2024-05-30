# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
from cdds.common.plugins.cordex.cordex_attributes import CordexGlobalAttributes

from unittest import TestCase


class TestCordexGlobalAttributes(TestCase):

    def setUp(self):
        self.request = {
            'institution_id': 'MOHC',
            'model_id': 'HadREM3-GA7-05',
            'experiment_id': 'piControl',
            'sub_experiment_id': 'none',
            'variant_label': 'r1i1p1f2'
        }

    def test_further_info_url(self):
        attributes = CordexGlobalAttributes(self.request)
        further_info_url = attributes.further_info_url()
        self.assertEqual(further_info_url, '')
