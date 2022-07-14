# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
from unittest.mock import patch
import unittest

from cdds_transfer.archive import (allowed_mass_locations,
                                   DEVELOPMENT_MASS_DIR, PRODUCTION_MASS_DIR)


class TestAllowedMassLocations(unittest.TestCase):
    @patch('cdds_transfer.archive._DEV', False)
    def test_production_mode(self):
        expected = ([DEVELOPMENT_MASS_DIR, PRODUCTION_MASS_DIR],
                    DEVELOPMENT_MASS_DIR)
        result = allowed_mass_locations()
        self.assertEqual(expected, result)

    @patch('cdds_transfer.archive._DEV', True)
    def test_development_mode(self):
        expected = ([DEVELOPMENT_MASS_DIR], DEVELOPMENT_MASS_DIR)
        result = allowed_mass_locations()
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
