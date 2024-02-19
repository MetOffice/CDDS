# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.
from unittest import TestCase, mock

from cdds.common.platforms import Facility
from cdds.common.request.conversion_section import conversion_defaults


class TestConversionDefaults(TestCase):

    @mock.patch('cdds.common.request.conversion_section.whereami')
    def test_defaults_for_jasmin(self, whereami_mock):
        whereami_mock.return_value = Facility.JASMIN
        expected_defaults = {
            'cdds_workflow_branch': 'cdds_jasmin_2.3',
            'cylc_args': '-v',
            'no_email_notifications': False,
            'skip_extract': True,
            'skip_extract_validation': False,
            'skip_configure': False,
            'skip_qc': False,
            'skip_archive': True
        }

        defaults = conversion_defaults()

        self.assertDictEqual(defaults, expected_defaults)

    @mock.patch('cdds.common.request.conversion_section.whereami')
    def test_defaults_for_metoffice(self, whereami_mock):
        whereami_mock.return_value = Facility.MET_OFFICE
        expected_defaults = {
            'cdds_workflow_branch': 'trunk',
            'cylc_args': '-v',
            'no_email_notifications': False,
            'skip_extract': False,
            'skip_extract_validation': False,
            'skip_configure': False,
            'skip_qc': False,
            'skip_archive': False
        }

        defaults = conversion_defaults()

        self.assertDictEqual(defaults, expected_defaults)
