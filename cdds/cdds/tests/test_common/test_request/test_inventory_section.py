# (C) British Crown Copyright 2023-2023, Met Office.
# Please see LICENSE.rst for license details.
from unittest import TestCase

from cdds.common.request.inventory_section import inventory_defaults


class TestInventoryDefaults(TestCase):

    def test_defaults(self):
        expected_defaults = {
            'inventory_check': False
        }

        defaults = inventory_defaults()

        self.assertDictEqual(defaults, expected_defaults)
