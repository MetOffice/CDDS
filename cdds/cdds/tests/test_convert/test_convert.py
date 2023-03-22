# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`convert.py`.
"""

import unittest

from cdds.convert.convert import get_rose_args_list


class TestGetRoseArgsList(unittest.TestCase):
    def test_get_rose_args_list_user_name(self):
        rose_args = ['--new', '--name=user_defined_name_{stream}']
        streams = ['stream1', 'stream2']
        request_id = 'model_experiment_variant'
        output_list = get_rose_args_list(rose_args, streams, request_id)

        expected_list = [
            ['--new', '--name=user_defined_name_stream1',
             '--opt-conf-key=stream1'],
            ['--new', '--name=user_defined_name_stream2',
             '--opt-conf-key=stream2']]
        self.assertEqual(output_list, expected_list)

    def test_get_rose_args_list_default_name(self):
        rose_args = ['--new', '--name=cdds_{request_id}_{stream}']
        streams = ['stream1', 'stream2']
        request_id = 'model_experiment_variant'
        output_list = get_rose_args_list(rose_args, streams, request_id)

        expected_list = [
            ['--new', '--name=cdds_model_experiment_variant_stream1',
             '--opt-conf-key=stream1'],
            ['--new', '--name=cdds_model_experiment_variant_stream2',
             '--opt-conf-key=stream2']]
        self.assertEqual(output_list, expected_list)


if __name__ == '__main__':
    unittest.main()
