# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from unittest import TestCase

from cdds.common.request.data_section import data_defaults


class TestDataDefaults(TestCase):
    def test_defaults(self):
        expected_defaults = {
            'mass_data_class': 'crum',
            'streams': 'ap4 ap5 ap6 inm onm',
            'model_workflow_branch': 'cdds',
            'model_workflow_revision': 'HEAD'
        }

        defaults = data_defaults()

        self.assertDictEqual(defaults, expected_defaults)
