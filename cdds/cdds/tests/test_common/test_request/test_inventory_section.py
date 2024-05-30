# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
from unittest import TestCase

from cdds.common.request.inventory_section import inventory_defaults


class TestInventoryDefaults(TestCase):

    def test_defaults(self):
        expected_defaults = {
            'inventory_check': False
        }

        defaults = inventory_defaults()

        self.assertDictEqual(defaults, expected_defaults)
