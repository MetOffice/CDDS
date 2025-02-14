# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
from datetime import datetime
from unittest import TestCase, mock

from cdds.common.request.data_section import data_defaults


class TestDataDefaults(TestCase):

    @mock.patch('cdds.common.request.data_section.datetime')
    def test_defaults(self, datetime_mock):
        data_version = datetime.utcnow()
        datetime_mock.utcnow.return_value = data_version
        expected_defaults = {
            'data_version': data_version.strftime('v%Y%m%d'),
            'mass_data_class': 'crum',
            'streams': 'ap4 ap5 ap6 inm onm',
            'model_workflow_branch': 'cdds',
            'model_workflow_revision': 'HEAD',
            'max_file_size': 20e9
        }

        defaults = data_defaults()

        self.assertDictEqual(defaults, expected_defaults)
