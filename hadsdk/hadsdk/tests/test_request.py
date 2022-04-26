# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`request.py`.
"""
import unittest

from hadsdk.request import Request


class TestRequest(unittest.TestCase):
    """
    Tests for :class:`Request` in :mod:`request.py`.
    """
    def setUp(self):
        self.mip_era_attribute = 'mip_era'
        self.mip_era_value = 'CMIP6'
        self.experiment_id_attribute = 'experiment_id'
        self.experiment_id_value = 'historical'
        self.stream_attribute_apa = 'run_bounds_for_stream_apa'
        self.stream_bounds_apa = '1851-01-01-00-00-00 1857-01-01-00-00-00'
        self.stream_type_apa = 'pp'
        self.stream_attribute_onm = 'run_bounds_for_stream_onm'
        self.stream_bounds_onm = '1852-01-01-00-00-00 1858-01-01-00-00-00'
        self.stream_type_onm = 'nc'
        self.items = {
            self.mip_era_attribute: self.mip_era_value,
            self.experiment_id_attribute: self.experiment_id_value,
            self.stream_attribute_apa: self.stream_bounds_apa,
            self.stream_attribute_onm: self.stream_bounds_onm,
        }

    def test_attributes(self):
        request = Request(self.items)
        self.assertEqual(getattr(request, self.mip_era_attribute),
                         self.mip_era_value)
        self.assertEqual(getattr(request, self.experiment_id_attribute),
                         self.experiment_id_value)
        self.assertEqual(getattr(request, self.stream_attribute_apa),
                         self.stream_bounds_apa)
        self.assertEqual(getattr(request, self.stream_attribute_onm),
                         self.stream_bounds_onm)

    def test_validate_attributes_all_exist(self):
        required_keys = [self.mip_era_attribute, self.experiment_id_attribute]
        request = Request(self.items, required_keys)
        self.assertEqual(getattr(request, self.mip_era_attribute),
                         self.mip_era_value)
        self.assertEqual(getattr(request, self.experiment_id_attribute),
                         self.experiment_id_value)

    def test_validate_attributes_one_missing(self):
        required_keys = ['model_id']
        self.assertRaises(AttributeError, Request, self.items, required_keys)

    def test_streaminfo(self):
        request = Request(self.items)
        self.assertEqual(request.streaminfo, {
            'apa': {
                'var': self.stream_attribute_apa,
                'start_date': '1851-01-01-00-00-00',
                'end_date': '1857-01-01-00-00-00',
                'type': 'pp'
            },
            'onm': {
                'var': self.stream_attribute_onm,
                'start_date': '1852-01-01-00-00-00',
                'end_date': '1858-01-01-00-00-00',
                'type': 'nc'
            },
        })

    def test_global_attributes(self):
        metadata = {
            'driving_model_id': 'ERAINT',
            'driving_model_ensemble_member': 'r0i0p0',
            'driving_experiment': 'thingy',
            'arbitrary_attribute': 'stuff'
        }
        self.items['global_attributes'] = metadata
        request = Request(self.items)
        self.assertDictEqual(request.items_global_attributes, metadata)

    def test_no_global_attributes(self):
        request = Request(self.items)
        self.assertDictEqual(request.items_global_attributes, {})


if __name__ == '__main__':
    unittest.main()
