# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from common.plugins.attributes import DefaultGlobalAttributes

from unittest import TestCase


class TestDefaultGlobalAttributes(TestCase):

    def test_further_info_url(self):
        attributes = DefaultGlobalAttributes()
        url = attributes.further_info_url()
        self.assertEqual(url, 'none')
