# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring
"""
Tests for :mod:`command_line.py`.
"""
import logging
import os
import unittest
import unittest.mock

from nose.plugins.attrib import attr

from cdds_template.command_line import main


@attr('slow')
class TestMain(unittest.TestCase):
    """
    Tests for :func:`main` in :mod:`command_line.py`.
    """
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.log_name = 'template_test'
        self.log_datestamp = '2019-11-23T1432Z'
        self.log_path = '{0}_{1}.log'.format(self.log_name,
                                             self.log_datestamp)
        self.args = ['--log_name', self.log_name]
        self.files_to_delete = [self.log_path]

    @unittest.mock.patch('cdds.common.get_log_datestamp')
    def test_x(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        args = self.args + ['-x', 'xylophone']  # ThisReasonError
        exit_code = main(args)
        self.assertEqual(exit_code, 2)

    @unittest.mock.patch('cdds.common.get_log_datestamp')
    def test_y(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        args = self.args + ['-y', 'yacht']  # ThatReasonError
        exit_code = main(args)
        self.assertEqual(exit_code, 3)

    @unittest.mock.patch('cdds.common.get_log_datestamp')
    def test_z(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        args = self.args + ['-z', 'zoo']  # AnotherReasonError
        exit_code = main(args)
        self.assertEqual(exit_code, 4)

    def tearDown(self):
        for fname1 in self.files_to_delete:
            if os.path.isfile(fname1):
                os.remove(fname1)
