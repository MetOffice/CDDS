# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
import os
import tempfile
import unittest

from cdds.common.io import write_json
from cdds.common.plugins.models import ModelsStore
from cdds.common.plugins.grid import GridType
from cdds.common.plugins.base.base_grid import AtmosBaseGridInfo, OceanBaseGridInfo
from cdds.common.plugins.streams import StreamFileInfo
from cdds.common.plugins.cmip6.cmip6_models import Cmip6ModelsStore, HadGEM3_GC31_LL_Params, Cmip6ModelId

from pathlib import Path
from unittest import TestCase


class TestModelsStore(TestCase):

    def setUp(self):
        Cmip6ModelsStore.clean_instance()

    def tearDown(self):
        Cmip6ModelsStore.clean_instance()

    def test_get_model_params_for_hadgem3_gc31_ll(self):
        store = Cmip6ModelsStore.instance()
        model_params = store.get(Cmip6ModelId.HadGEM3_GC31_LL.value)
        self.assertIsInstance(model_params, HadGEM3_GC31_LL_Params)

    def test_overload_values(self):
        new_values = {'cycle_length': {'ap4': 'P8Y'}}
        temp_dir = tempfile.mkdtemp()
        json_file = os.path.join(temp_dir, 'HadGEM3-GC31-LL.json')
        write_json(json_file, new_values)

        store = Cmip6ModelsStore.instance()
        old_value = store.get('HadGEM3-GC31-LL').cycle_length('ap4')

        result = store.overload_params(temp_dir)
        new_value = store.get('HadGEM3-GC31-LL').cycle_length('ap4')

        self.assertNotEqual(old_value, new_value)
        self.assertEqual(new_value, 'P8Y')

        self.assertTrue(result.loaded['HadGEM3-GC31-LL'].loaded)
        self.assertSize(result.loaded, 1)
        self.assertSize(result.unloaded, 5)

    def test_models_store_is_singleton(self):
        Cmip6ModelsStore.instance()
        self.assertRaises(Exception, ModelsStore)

    def assertSize(self, actual, expected_size):
        self.assertEqual(len(actual), expected_size)


class TestModelParameters(TestCase):

    def setUp(self):
        self.model_params_dir = tempfile.mkdtemp()

        local_dir = os.path.dirname(os.path.abspath(__file__))
        default_dir = os.path.join(local_dir, 'data/model')

        self.model_params = HadGEM3_GC31_LL_Params()
        self.model_params.load_parameters(default_dir)

    def test_no_data_loaded(self):
        self.model_params = HadGEM3_GC31_LL_Params()
        self.assertRaises(KeyError, self.model_params.cycle_length, 'ap4')

    def test_only_default_data_loaded(self):
        self.model_params.cycle_length('ap4')

    def test_load_no_new_data(self):
        data = {}
        self.write_params_file(data)
        old_value = self.model_params.cycle_length('ap4')

        self.model_params.load_parameters(self.model_params_dir)
        new_value = self.model_params.cycle_length('ap4')

        self.assertEqual(new_value, old_value)

    def test_load_new_data(self):
        data = {
            'cycle_length': {
                'ap4': 'P10Y'
            }
        }
        self.write_params_file(data)
        old_value = self.model_params.cycle_length('ap4')

        self.model_params.load_parameters(self.model_params_dir)
        new_value = self.model_params.cycle_length('ap4')

        self.assertNotEqual(new_value, old_value)
        self.assertEqual(new_value, 'P10Y')

    def test_get_atmos_grid_info(self):
        grid_info = self.model_params.grid_info(GridType.ATMOS)
        self.assertIsInstance(grid_info, AtmosBaseGridInfo)

    def test_get_ocean_grid_info(self):
        grid_info = self.model_params.grid_info(GridType.OCEAN)
        self.assertIsInstance(grid_info, OceanBaseGridInfo)

    def test_stream_file_info(self):
        stream_file_info = self.model_params.stream_file_info()

        ap4_file_info = stream_file_info.file_frequencies["ap4"]
        self.assertEqual(ap4_file_info.frequency, "monthly")
        self.assertEqual(ap4_file_info.stream, "ap4")
        self.assertEqual(ap4_file_info.file_per_year, 12)

    def write_params_file(self, data):
        json_file = os.path.join(self.model_params_dir, 'HadGEM3-GC31-LL.json')
        write_json(json_file, data)


class TestModelId(TestCase):

    def test_enum_definition(self):
        # test if enum is correctly defined and is valid
        value = Cmip6ModelId.HadGEM3_GC31_LL.value
        self.assertEqual(value, 'HadGEM3-GC31-LL')

    def test_get_json_file_name(self):
        json_file = Cmip6ModelId.HadGEM3_GC31_LL.get_json_file()
        self.assertEqual(json_file, 'HadGEM3-GC31-LL.json')


class TestDefaultModelJsonFiles(TestCase):

    def setUp(self) -> None:
        model_dir_relative_path = 'common/plugins/cmip6/data/model'

        cdds_dir = Path(__file__).parent.parent.parent.parent
        model_dir = cdds_dir.joinpath(cdds_dir, model_dir_relative_path).absolute()
        self.model_files = [
            file.name for file in model_dir.iterdir()
        ]

    def test_default_json_files_for_HadGEM3_GC31_LL(self):
        json_file_name = Cmip6ModelId.HadGEM3_GC31_LL.get_json_file()
        self.assertIn(json_file_name, self.model_files)

    def test_default_json_files_for_HadGEM3_GC31_MM(self):
        json_file_name = Cmip6ModelId.HadGEM3_GC31_MM.get_json_file()
        self.assertIn(json_file_name, self.model_files)

    def test_default_json_files_for_HadREM3_GA7_05(self):
        json_file_name = Cmip6ModelId.HadREM3_GA7_05.get_json_file()
        self.assertIn(json_file_name, self.model_files)

    def test_default_json_files_for_UKESM1_0_LL(self):
        json_file_name = Cmip6ModelId.UKESM1_0_LL.get_json_file()
        self.assertIn(json_file_name, self.model_files)

    def test_default_json_files_for_UKESM1_ICE_LL(self):
        json_file_name = Cmip6ModelId.UKESM1_ICE_LL.get_json_file()
        self.assertIn(json_file_name, self.model_files)


if __name__ == '__main__':
    unittest.main()
