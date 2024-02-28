# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import unittest

from cdds.common.plugins.cmip6_plus.cmip6_plus_attributes import Cmip6PlusGlobalAttributes, AttributesValidator
from cdds.common.request.request import Request

from unittest import TestCase


class TestCmip6PlusGlobalAttributes(TestCase):

    def setUp(self):
        self.mip_era = 'CMIP6Plus'
        self.institution_id = 'MOHC'
        self.model_id = 'HadGEM3-GC31-LL'
        self.experiment_id = 'piControl'
        self.sub_experiment_id = 'none'
        self.variant_label = 'r1i1p1f2'
        self.request = Request()
        self.request.metadata.institution_id = self.institution_id
        self.request.metadata.model_id = self.model_id
        self.request.metadata.experiment_id = self.experiment_id
        self.request.metadata.variant_label = self.variant_label

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

    def test_request_valid(self):
        request = Request()
        request.metadata.institution_id = 'MOHC'
        request.metadata.model_id = 'HadGEM3-GC31-LL'
        request.metadata.experiment_id = 'piControl'
        request.metadata.sub_experiment_id = 'none'
        request.metadata.variant_label = 'r1i1p1f2'
        AttributesValidator.validate_request(request)

    def test_request_no_institution_id(self):
        request = Request()
        request.metadata.institution_id = ''
        request.metadata.model_id = 'HadGEM3-GC31-LL'
        request.metadata.experiment_id = 'piControl'
        request.metadata.sub_experiment_id = 'none'
        request.metadata.variant_label = 'r1i1p1f2'

        self.assertRaises(ValueError, AttributesValidator.validate_request, request)

    def test_request_no_model_id(self):
        request = Request()
        request.metadata.institution_id = 'MOHC'
        request.metadata.model_id = ''
        request.metadata.experiment_id = 'piControl'
        request.metadata.sub_experiment_id = 'none'
        request.metadata.variant_label = 'r1i1p1f2'

        self.assertRaises(ValueError, AttributesValidator.validate_request, request)

    def test_request_no_experiment_id(self):
        request = Request()
        request.metadata.institution_id = 'MOHC'
        request.metadata.model_id = 'HadGEM3-GC31-LL'
        request.metadata.experiment_id = ''
        request.metadata.sub_experiment_id = 'none'
        request.metadata.variant_label = 'r1i1p1f2'

        self.assertRaises(ValueError, AttributesValidator.validate_request, request)

    def test_request_no_sub_experiment_id(self):
        request = Request()
        request.metadata.institution_id = 'MOHC'
        request.metadata.model_id = 'HadGEM3-GC31-LL'
        request.metadata.experiment_id = 'piControl'
        request.metadata.sub_experiment_id = ''
        request.metadata.variant_label = 'r1i1p1f2'

        self.assertRaises(ValueError, AttributesValidator.validate_request, request)

    def test_request_no_variant_label(self):
        request = Request()
        request.metadata.institution_id = 'MOHC'
        request.metadata.model_id = 'HadGEM3-GC31-LL'
        request.metadata.experiment_id = 'piControl'
        request.metadata.sub_experiment_id = 'none'
        request.metadata.variant_label = ''

        self.assertRaises(ValueError, AttributesValidator.validate_request, request)


if __name__ == '__main__':
    unittest.main()
