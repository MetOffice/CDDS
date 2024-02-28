# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.
from datetime import datetime
from unittest import TestCase, mock

from cdds.common.request.data_section import data_defaults, MASS_DATA_ARCHIVE_DATESTAMP


class TestDataDefaults(TestCase):

    @mock.patch('cdds.common.request.data_section.datetime')
    def test_defaults(self, datetime_mock):
        archive_version = datetime.now()
        datetime_mock.now.return_value = archive_version
        expected_defaults = {
            'mass_data_class': 'crum',
            'mass_data_archive_version': archive_version.strftime(MASS_DATA_ARCHIVE_DATESTAMP),
            'streams': 'ap4 ap5 ap6 inm onm',
            'model_workflow_branch': 'cdds',
            'model_workflow_revision': 'HEAD'
        }

        defaults = data_defaults()

        self.assertDictEqual(defaults, expected_defaults)
