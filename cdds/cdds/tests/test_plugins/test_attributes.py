# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
from cdds.common.plugins.attributes import DefaultGlobalAttributes

from unittest import TestCase


class TestDefaultGlobalAttributes(TestCase):

    def test_further_info_url(self):
        attributes = DefaultGlobalAttributes()
        url = attributes.further_info_url()
        self.assertEqual(url, 'none')
