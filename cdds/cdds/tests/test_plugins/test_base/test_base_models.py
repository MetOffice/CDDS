# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.md for license details.
import unittest

from cdds.common.plugins.base.base_models import SizingInfo
from unittest import TestCase


class TestSizingInfo(TestCase):

    def setUp(self):
        self.data = {
            'mon': {
                'default': 100,
                '85-144-192': 50,
                '85-145-192': 50,
                '86-144-192': 50,
                '75-330-360': 50
            },
            'monPt': {
                'default': 100,
                '85-144-192': 50,
                '85-145-192': 50,
                '86-144-192': 50,
                '75-330-360': 50
            },
            'yr': {
                'default': 100
            }
        }

    def test_get_all(self):
        sizing_info = SizingInfo(self.data)
        result = sizing_info.get_all()
        self.assertDictEqual(result, self.data)

    def test_get_period(self):
        sizing_info = SizingInfo(self.data)
        period = sizing_info.get_period('mon', '85-144-192')
        self.assertEqual(period, 50)

    def test_get_period_if_coordinates_are_longer(self):
        sizing_info = SizingInfo(self.data)
        period = sizing_info.get_period('mon', '22-85-144-192')
        self.assertEqual(period, 50)

    def test_get_period_if_coordinates_not_in_data(self):
        sizing_info = SizingInfo(self.data)
        period = sizing_info.get_period('mon', '12-100-100')
        self.assertEqual(period, 100)


if __name__ == '__main__':
    unittest.main()
