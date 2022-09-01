# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from unittest import TestCase, mock

from cdds.common.platforms import whereami, Facility, System


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


class TestSystem(TestCase):

    def test_jasmin_package_args_file(self):
        system = System(Facility.JASMIN)
        package_args_file = system.default_package_args_file('cdds')
        self.assertEndsWith(package_args_file, 'cdds/arguments.json')

    def test_jasmin_global_args_file(self):
        system = System(Facility.JASMIN)
        package_args_file = system.default_global_args_file()
        self.assertEndsWith(package_args_file, 'cdds/global_arguments_jasmin.json')

    def test_metoffice_package_args_file(self):
        system = System(Facility.MET_OFFICE)
        package_args_file = system.default_package_args_file('cdds')
        self.assertEndsWith(package_args_file, 'cdds/arguments.json')

    def test_metoffice_global_args_file(self):
        system = System(Facility.MET_OFFICE)
        package_args_file = system.default_global_args_file()
        self.assertEndsWith(package_args_file, 'cdds/global_arguments.json')

    def assertEndsWith(self, actual, expected_end):
        self.assertTrue(actual.endswith(expected_end))
