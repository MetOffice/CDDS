# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`convert.py`.
"""

import unittest

from cdds.convert.convert import get_cylc_args_list


class TestGetCylcArgsList(unittest.TestCase):
    def test_get_cylc_args_list_user_name(self):
        cylc_args = ['--new', '--name=user_defined_name_{stream}']
        streams = ['stream1', 'stream2']
        request_id = 'model_experiment_variant'
        output_list = get_cylc_args_list(cylc_args, streams, request_id)

        expected_list = [
            ['--new', '--name=user_defined_name_stream1',
             '--opt-conf-key=stream1'],
            ['--new', '--name=user_defined_name_stream2',
             '--opt-conf-key=stream2']]
        self.assertEqual(output_list, expected_list)

    def test_get_cylc_args_list_default_name(self):
        cylc_args = ['--new', '--name=cdds_{request_id}_{stream}']
        streams = ['stream1', 'stream2']
        request_id = 'model_experiment_variant'
        output_list = get_cylc_args_list(cylc_args, streams, request_id)

        expected_list = [
            ['--new', '--name=cdds_model_experiment_variant_stream1',
             '--opt-conf-key=stream1'],
            ['--new', '--name=cdds_model_experiment_variant_stream2',
             '--opt-conf-key=stream2']]
        self.assertEqual(output_list, expected_list)


if __name__ == '__main__':
    unittest.main()
