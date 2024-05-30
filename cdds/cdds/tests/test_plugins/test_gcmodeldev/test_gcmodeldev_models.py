# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import os
import tempfile

from unittest import TestCase

from cdds.common.io import write_json
from cdds.common.plugins.gcmodeldev.gcmodeldev_models import GCModelDevStore


class TestModelStore(TestCase):

    def setUp(self):
        GCModelDevStore.clean_instance()

    def tearDown(self):
        GCModelDevStore.clean_instance()

    def test_overload_values(self):
        new_values = {'cycle_length': {'ap4': 'P8Y'}}
        temp_dir = tempfile.mkdtemp()
        json_file = os.path.join(temp_dir, 'HadGEM3-GC31-LL.json')
        write_json(json_file, new_values)

        store = GCModelDevStore.instance()
        old_value = store.get('HadGEM3-GC31-LL').cycle_length('ap4')

        result = store.overload_params(temp_dir)
        new_value = store.get('HadGEM3-GC31-LL').cycle_length('ap4')

        self.assertNotEqual(old_value, new_value)
        self.assertEqual(new_value, 'P8Y')

        self.assertTrue(result.loaded['HadGEM3-GC31-LL'].loaded)
        self.assertSize(result.loaded, 1)
        self.assertSize(result.unloaded, (len(store.model_instances) - 1))

    def assertSize(self, actual, expected_size):
        self.assertEqual(len(actual), expected_size)
