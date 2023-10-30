# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import unittest

from cdds.common.plugins.cmip6_plus.cimp6_plus_attributes import Cmip6PlusGlobalAttributes, AttributeValidator

from unittest import TestCase


class TestCmip6PlusGlobalAttributes(TestCase):

    def setUp(self):
        self.mip_era = 'CMIP6Plus'
        self.institution_id = 'MOHC'
        self.model_id = 'HadGEM3-GC31-LL'
        self.experiment_id = 'piControl'
        self.sub_experiment_id = 'none'
        self.variant_label = 'r1i1p1f2'
        self.request = {
            'institution_id': self.institution_id,
            'model_id': self.model_id,
            'experiment_id': self.experiment_id,
            'sub_experiment_id': self.sub_experiment_id,
            'variant_label': self.variant_label
        }

    def test_further_info_url(self):
        expected_url = 'https://furtherinfo.es-doc.org/{}.{}.{}.{}.{}.{}'.format(
            self.mip_era,
            self.institution_id,
            self.model_id,
            self.experiment_id,
            self.sub_experiment_id,
            self.variant_label
        )

        attributes = Cmip6PlusGlobalAttributes(self.request)
        actual_url = attributes.further_info_url()
        self.assertEqual(actual_url, expected_url)


class TestAttributeValidator(TestCase):

    def test_request_equals_expected(self):
        request = {
            'institution_id': 'MOHC',
            'model_id': 'HadGEM3-GC31-LL',
            'experiment_id': 'piControl',
            'sub_experiment_id': 'none',
            'variant_label': 'r1i1p1f2'
        }
        AttributeValidator.validate_request_keys(request)

    def test_request_contains_more_than_expected(self):
        request = {
            'institution_id': 'MOHC',
            'model_id': 'HadGEM3-GC31-LL',
            'experiment_id': 'piControl',
            'sub_experiment_id': 'none',
            'variant_label': 'r1i1p1f2',
            'calendar': '360_day',
            'suite_id': 'u-bx562'
        }
        AttributeValidator.validate_request_keys(request)

    def test_request_contains_less_than_expected(self):
        request = {
            'model_id': 'HadGEM3-GC31-LL',
            'experiment_id': 'piControl',
            'sub_experiment_id': 'none',
            'variant_label': 'r1i1p1f2'
        }
        self.assertRaises(ValueError, AttributeValidator.validate_request_keys, request)


if __name__ == '__main__':
    unittest.main()
