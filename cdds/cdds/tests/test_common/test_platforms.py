# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
from unittest import TestCase, mock

from cdds.common.platforms import whereami, Facility


class TestWhereami(TestCase):

    @mock.patch('socket.getfqdn')
    def test_whereami_jasmin(self, getfqdn_mock):
        getfqdn_mock.return_value = 'www.jasmin.ac.uk'
        facility = whereami()
        self.assertEqual(facility, Facility.JASMIN)

    @mock.patch('socket.getfqdn')
    def test_whereami_metoffice(self, getfqdn_mock):
        getfqdn_mock.return_value = 'www.metoffice.gov.uk'
        facility = whereami()
        self.assertEqual(facility, Facility.MET_OFFICE)
