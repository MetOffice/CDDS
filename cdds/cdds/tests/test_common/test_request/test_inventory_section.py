# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.
import tempfile
from unittest import TestCase

from cdds.common.request.inventory_section import inventory_defaults, InventorySection


class TestInventoryDefaults(TestCase):

    def test_defaults(self):
        expected_defaults = {
            'inventory_check': False
        }

        defaults = inventory_defaults()

        self.assertDictEqual(defaults, expected_defaults)


class TestInventoryPostInitChecks(TestCase):

    def test_no_inventory_used_and_db_not_set(self):
        InventorySection(
            inventory_check=False,
            inventory_database_location=''
        )

    def test_no_inventory_non_existing_db(self):
        InventorySection(
            inventory_check=False,
            inventory_database_location='/no/existing/inventory.db'
        )

    def test_inventory_checks_and_existing_db(self):
        with tempfile.NamedTemporaryFile() as inventory_db:
            inventory_db.write(b'')

            InventorySection(
                inventory_check=True,
                inventory_database_location=inventory_db.name
            )
            inventory_db.close()

    def test_inventory_checks_and_non_existing_db(self):
        inventory_db = '/not/existing/inventory.db'
        self.assertRaises(AttributeError, InventorySection, True, inventory_db)
