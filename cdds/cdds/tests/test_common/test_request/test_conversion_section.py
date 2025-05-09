# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
import os
from unittest import TestCase, mock

from cdds.common.platforms import Facility
from cdds.common.request.conversion_section import conversion_defaults


class TestConversionDefaults(TestCase):

    @mock.patch('cdds.common.request.conversion_section.whereami')
    def test_defaults_for_jasmin(self, whereami_mock):
        whereami_mock.return_value = Facility.JASMIN
        expected_defaults = {
            'delete_preexisting_proc_dir': False,
            'delete_preexisting_data_dir': False,
            'no_email_notifications': True,
            'skip_extract': True,
            'skip_extract_validation': False,
            'skip_configure': False,
            'skip_qc': False,
            'skip_archive': True,
            'continue_if_mip_convert_failed': False
        }

        defaults = conversion_defaults()

        self.assertDictEqual(defaults, expected_defaults)

    @mock.patch('cdds.common.request.conversion_section.whereami')
    def test_defaults_for_metoffice(self, whereami_mock):
        whereami_mock.return_value = Facility.MET_OFFICE
        expected_defaults = {
            'delete_preexisting_proc_dir': False,
            'delete_preexisting_data_dir': False,
            'no_email_notifications': True,
            'skip_extract': False,
            'skip_extract_validation': False,
            'skip_configure': False,
            'skip_qc': False,
            'skip_archive': False,
            'continue_if_mip_convert_failed': False
        }

        defaults = conversion_defaults()

        self.assertDictEqual(defaults, expected_defaults)
