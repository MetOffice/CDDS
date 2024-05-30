# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
from cdds.common.plugins.attributes import DefaultGlobalAttributes

from unittest import TestCase


class TestDefaultGlobalAttributes(TestCase):

    def test_further_info_url(self):
        attributes = DefaultGlobalAttributes()
        url = attributes.further_info_url()
        self.assertEqual(url, 'none')
