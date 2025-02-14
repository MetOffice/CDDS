# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name
"""
Tests for the :mod:`cdds.convert.concatenation.concatenation_setup`
module.
"""
import os
from typing import Type, List
import unittest
from unittest import mock

from metomi.isodatetime.data import TimePoint, Duration, Calendar
from metomi.isodatetime.parsers import TimePointParser

from cdds.common import run_command
from cdds.common.plugins.base.base_models import BaseModelParameters, SizingInfo
from cdds.common.plugins.file_info import ModelFileInfo
from cdds.common.plugins.grid import GridLabel, GridType, GridInfo
from cdds.common.plugins.models import ModelParameters
from cdds.common.plugins.plugins import PluginStore, CddsPlugin
from cdds.common.plugins.streams import StreamInfo

import cdds.convert.concatenation.concatenation_setup
from cdds.convert.concatenation.concatenation_setup import (
    get_file_frequency_shape, get_reinitialisation_period,
    organise_concatenations, times_from_filename,
    load_concatenation_setup_config)


MINIMAL_CDL = '''
netcdf filename {
dimensions:
    lat = 1 ;
    lon = 1 ;
    time = UNLIMITED ; // (1 currently)
variables:
    double lat(lat) ;
    double lon(lon) ;
    float rsut(time, lat, lon) ;
    double time(time) ;

// global attributes:
    :Conventions = "CF-1.7 CMIP-6.2" ;
    :frequency = "mon" ;
data:
 lat = -89.375 ;
 lon = 0.9375 ;
 rsut = 213.0 ;
 time = 45 ;
}
'''

DUMMY_SIZING = {
    'arbitrary': {
        'default': 100,
        '30-40-50': 50},
    'mon': {
        'default': 100,
        '1-1': 50}
}


class DummyModel(BaseModelParameters):

    def __init__(self):
        super(DummyModel, self).__init__(None)
        self._sizing = SizingInfo(DUMMY_SIZING)

    @property
    def model_version(self):
        return ''

    @property
    def data_request_version(self):
        return ''

    @property
    def um_version(self) -> str:
        return ''

    def is_model(self, model_id):
        return model_id == 'dummymodel'


class DummyCddsPlugin(CddsPlugin):

    def __init__(self):
        super(DummyCddsPlugin, self).__init__('CMIP6')

    def grid_info(self, grid_type: GridType) -> Type[GridInfo]:
        pass

    def overload_grid_info(self, source_dir: str) -> None:
        pass

    def models_parameters(self, model_id: str) -> ModelParameters:
        return DummyModel()

    def overload_models_parameters(self, model_id: str, source_dir: str) -> None:
        pass

    def grid_labels(self) -> Type[GridLabel]:
        pass

    def stream_info(self) -> StreamInfo:
        pass

    def model_file_info(self) -> ModelFileInfo:
        pass

    def license(self) -> str:
        pass

    def mip_table_dir(self) -> str:
        pass

    def proc_directory(self, request) -> str:
        pass

    def data_directory(self, request) -> str:
        pass

    def requested_variables_list_filename(self, request) -> str:
        pass


class TestConcatenationSetup(unittest.TestCase):

    def setUp(self):
        PluginStore.instance().register_plugin(DummyCddsPlugin())
        self.testncfilename = 'rsut_get_file_frequency_shape_test.nc'
        create_simple_netcdf_file(MINIMAL_CDL, self.testncfilename)
        self.sizing_data = {
            'mon': {'1-1': 1000},
            'arbitrary': {'30-40-50': 2, 'default': 10}
        }

    def tearDown(self):
        PluginStore.clean_instance()
        if os.path.exists(self.testncfilename):
            os.unlink(self.testncfilename)

    def test_reinitialisation_period_identification(self):
        expected_freq = 'mon'
        expected_shape = '1-1'
        freq, shape = get_file_frequency_shape(self.testncfilename)
        self.assertEqual(expected_freq, freq)
        self.assertEqual(expected_shape, shape)

    @mock.patch('os.path.exists')
    def test_get_reinitialisation_period_simple_file(self, mock_exists):
        mock_exists.return_value = True
        cs_mod = cdds.convert.concatenation.concatenation_setup
        cs_mod.SIZING_INFO = DUMMY_SIZING
        result = get_reinitialisation_period(self.testncfilename, 'dummymodel')
        expected = DUMMY_SIZING['mon']['1-1']
        self.assertEqual(result, expected)

    @mock.patch('cdds.convert.concatenation.concatenation_setup'
                '.get_file_frequency_shape')
    @mock.patch('os.path.exists')
    def test_get_reinitialisation_period_2(
            self, mock_exists, mock_get_shape):
        shape = '30-40-50'
        result = self._get_realisation_period_common(
            mock_exists, mock_get_shape, shape)
        expected = DUMMY_SIZING['arbitrary'][shape]
        self.assertEqual(result, expected)

    @mock.patch('cdds.convert.concatenation.concatenation_setup'
                '.get_file_frequency_shape')
    @mock.patch('os.path.exists')
    def test_get_reinitialisation_period_3(
            self, mock_exists, mock_get_shape):
        shape = '30-40'
        result = self._get_realisation_period_common(
            mock_exists, mock_get_shape, shape)
        expected = DUMMY_SIZING['arbitrary']['default']
        self.assertEqual(result, expected)

    @mock.patch('cdds.convert.concatenation.concatenation_setup'
                '.get_file_frequency_shape')
    @mock.patch('os.path.exists')
    def test_get_reinitialisation_period_4(
            self, mock_exists, mock_get_shape):
        shape = '20-30-40-50'
        result = self._get_realisation_period_common(
            mock_exists, mock_get_shape, shape)
        expected = DUMMY_SIZING['arbitrary']['30-40-50']
        self.assertEqual(result, expected)

    def _get_realisation_period_common(self, mock_exists, mock_get_shape,
                                       shape):
        mock_exists.return_value = True
        mock_get_shape.return_value = ('arbitrary', shape)
        cs_mod = cdds.convert.concatenation.concatenation_setup
        cs_mod.SIZING_INFO = DUMMY_SIZING
        result = get_reinitialisation_period(
            'dummy_filename', 'dummymodel')
        mock_get_shape.assert_called_with('dummy_filename')
        return result

    @mock.patch('cdds.convert.concatenation.concatenation_setup.ConfigParser')
    def test_load_concatenation_setup_config(self, mock_cfg_parser):
        config_path = '/dummy/path/to/file.cfg'
        expected_config = {
            'model_id': 'dummymodel',
            'output_location': '/dummy/path/to/output/ap5',
            'start_date': '18500101',
            'output_file': '/dummy/path/to/output/file.db',
            'recursive': True,
            'reference_date': '18500101',
            'end_date': '19490101',
            'calendar': '360day',
            'staging_location': '/dummy/path/to/staging/output/stream/',
            'json': False,
        }
        parser_return_dict = {
            key1: str(val1)
            for key1, val1 in expected_config.items()
        }
        mock_parser_obj = mock.MagicMock()
        mock_parser_obj.__getitem__.return_value = parser_return_dict
        mock_cfg_parser.return_value = mock_parser_obj
        output_config = load_concatenation_setup_config(config_path)
        self.assertEqual(expected_config, output_config)


class TestOrganiseConcatenations(unittest.TestCase):

    def setUp(self):
        Calendar.default().set_mode('360_day')

    def _generate_test_data(self, ref, start, end, chunk_start, chunk_end,
                            concat_cycle, concat_window, mc_cycle):
        reference_date = TimePoint(year=ref, month_of_year=1, day_of_month=1)
        start_date = TimePoint(year=start, month_of_year=1, day_of_month=1)
        end_date = TimePoint(year=end, month_of_year=1, day_of_month=1)
        chunk_start = TimePoint(year=chunk_start, month_of_year=1, day_of_month=1)
        chunk_end = TimePoint(year=chunk_end, month_of_year=1, day_of_month=1)

        mip_convert_cycle_length = mc_cycle
        expected_time_chunks = {}
        filenames = []
        output_dir = '/path/to/dummy/dir/dummystream'
        base_dir_staging = '/path/to/dummy/dir/dummystream_staging'
        template_filename = ('var_mip_experiment_activity_variant_grid_'
                             '{start_year}01-{end_year}12.nc')
        template_path = os.path.join(
            base_dir_staging, 'mip', 'var', template_filename)
        template_path_output = os.path.join(
            output_dir, 'mip', 'var', template_filename)
        for window_start in range(chunk_start.year, chunk_end.year,
                                  concat_window):
            window_end = min(window_start + concat_window, chunk_end.year)
            files_window = [template_path.format(
                start_year=year,
                end_year=year + mip_convert_cycle_length - 1)
                for year in range(window_start,
                                  window_end,
                                  mip_convert_cycle_length)]
            # calculate the end year of the last
            data_end = max(window_end - 1,
                           [year + mip_convert_cycle_length - 1
                            for year in range(window_start,
                                              window_end,
                                              mip_convert_cycle_length)][-1])
            tc_key = template_path_output.format(start_year=window_start,
                                                 end_year=data_end)
            expected_time_chunks[tc_key] = files_window
            filenames += files_window

        return (reference_date, start_date, end_date, filenames,
                expected_time_chunks, output_dir)

    def test_times_from_filename_360day_calendar(self):
        test_filename = 'ta_Amon_UKESM1-0-LL_amip_r1i1p1f2_gn_197901-201412.nc'
        expected_start = TimePoint(year=1979, month_of_year=1, day_of_month=1)
        expected_end = TimePoint(year=2014, month_of_year=12, day_of_month=1)
        output_start, output_end = times_from_filename(test_filename)
        self.assertTrue(expected_start, output_start)
        self.assertTrue(expected_end, output_end)

    def test_organise_concatenations_aligned_50yr(self):
        concat_cycle = 50
        concat_window = 50
        mip_convert_cycle_length = 5
        (reference_date, start_date, end_date, filenames,
         expected_time_chunks, output_dir) = self._generate_test_data(
            1850, 1950, 2150, 2000, 2050, concat_cycle, concat_window,
            mip_convert_cycle_length)

        output_time_chunks = organise_concatenations(reference_date,
                                                     start_date,
                                                     end_date,
                                                     concat_window,
                                                     filenames,
                                                     output_dir)
        self.assertEqual(expected_time_chunks, output_time_chunks)

    def test_organise_concatenations_aligned_less_than_1yr_gregorian_calendar(self):
        Calendar.default().set_mode('gregorian')
        concat_cycle = 50
        concat_window = 0.25
        mip_convert_cycle_length = 5
        (reference_date, start_date, end_date, filenames,
         expected_time_chunks, output_dir) = self._generate_test_data(
            1850, 1950, 2150, 2000, 2050, concat_cycle, 1,
            mip_convert_cycle_length)

        output_time_chunks = organise_concatenations(reference_date,
                                                     start_date,
                                                     end_date,
                                                     concat_window,
                                                     filenames,
                                                     output_dir)
        self.assertEqual(expected_time_chunks, output_time_chunks)

    def test_organise_concatenations_aligned_35yr(self):
        concat_cycle = 35
        concat_window = 35
        mip_convert_cycle_length = 5
        (reference_date, start_date, end_date, filenames,
         expected_time_chunks, output_dir) = self._generate_test_data(
            1850, 1920, 2200, 1990, 2025, concat_cycle, concat_window,
            mip_convert_cycle_length)
        output_time_chunks = organise_concatenations(reference_date,
                                                     start_date,
                                                     end_date,
                                                     concat_window,
                                                     filenames,
                                                     output_dir)
        self.assertEqual(expected_time_chunks, output_time_chunks)

    def test_organise_concatenations_aligned_50yr_cycle_25yr_window(self):
        concat_cycle = 50
        concat_window = 25
        mip_convert_cycle_length = 5
        (reference_date, start_date, end_date, filenames,
         expected_time_chunks, output_dir) = self._generate_test_data(
            1850, 1950, 2150, 2000, 2050, concat_cycle, concat_window,
            mip_convert_cycle_length)

        output_time_chunks = organise_concatenations(reference_date,
                                                     start_date,
                                                     end_date,
                                                     concat_window,
                                                     filenames,
                                                     output_dir)
        self.assertEqual(expected_time_chunks, output_time_chunks)

    def test_organise_concatenations_concat_misaligned(self):
        concat_cycle = 50
        concat_window = 50
        mip_convert_cycle_length = 5
        (reference_date, start_date, end_date, filenames,
         expected_time_chunks, output_dir) = self._generate_test_data(
            1850, 1979, 2015, 1979, 2000, concat_cycle, concat_window,
            mip_convert_cycle_length)
        output_time_chunks = organise_concatenations(reference_date,
                                                     start_date,
                                                     end_date,
                                                     concat_window,
                                                     filenames,
                                                     output_dir)
        self.assertEqual(expected_time_chunks, output_time_chunks)

    def test_organise_concatenations_first_cycle_aligned(self):
        concat_cycle = 50
        concat_window = 50
        mip_convert_cycle_length = 5
        (reference_date, start_date, end_date, filenames,
         expected_time_chunks, output_dir) = self._generate_test_data(
            1850, 1950, 2300, 1950, 2000, concat_cycle, concat_window,
            mip_convert_cycle_length)
        output_time_chunks = organise_concatenations(reference_date,
                                                     start_date,
                                                     end_date,
                                                     concat_window,
                                                     filenames,
                                                     output_dir)
        self.assertEqual(expected_time_chunks, output_time_chunks)

    def test_organise_concatenations_first_cycle_misaligned(self):
        concat_cycle = 50
        concat_window = 50
        mip_convert_cycle_length = 5
        (reference_date, start_date, end_date, filenames,
         expected_time_chunks, output_dir) = self._generate_test_data(
            1850, 1965, 2300, 1965, 2000, concat_cycle, concat_window,
            mip_convert_cycle_length)
        output_time_chunks = organise_concatenations(reference_date,
                                                     start_date,
                                                     end_date,
                                                     concat_window,
                                                     filenames,
                                                     output_dir)
        self.assertEqual(expected_time_chunks, output_time_chunks)

    def test_organise_concatenations_last_cycle_aligned(self):
        concat_cycle = 50
        concat_window = 50
        mip_convert_cycle_length = 5
        (reference_date, start_date, end_date, filenames,
         expected_time_chunks, output_dir) = self._generate_test_data(
            1850, 1950, 2300, 2250, 2300, concat_cycle, concat_window,
            mip_convert_cycle_length)
        output_time_chunks = organise_concatenations(reference_date,
                                                     start_date,
                                                     end_date,
                                                     concat_window,
                                                     filenames,
                                                     output_dir)
        self.assertEqual(expected_time_chunks, output_time_chunks)

    def test_organise_concatenations_last_cycle_misaligned(self):
        concat_cycle = 50
        concat_window = 25
        mip_convert_cycle_length = 5
        (reference_date, start_date, end_date, filenames,
         expected_time_chunks, output_dir) = self._generate_test_data(
            1850, 1960, 2270, 2250, 2270, concat_cycle, concat_window,
            mip_convert_cycle_length)
        output_time_chunks = organise_concatenations(reference_date,
                                                     start_date,
                                                     end_date,
                                                     concat_window,
                                                     filenames,
                                                     output_dir)
        self.assertEqual(expected_time_chunks, output_time_chunks)


def create_simple_netcdf_file(source_cdl, output_filepath):
    """
    Write a small netCDF4 file to the specified output file path based
    on the supplied CDL description.

    Parameters
    ----------
    source_cdl : str
        CDL template
    output_filepath : str
        Path to the output file
    """

    temp_file_name = 'simple.cdl'
    with open(temp_file_name, 'w') as cdl_file_handle:
        cdl_file_handle.write(source_cdl)
    command = ['ncgen', '-k' '4', '-o', output_filepath, temp_file_name]
    try:
        run_command(command)
    except RuntimeError:
        raise
    finally:
        os.unlink(temp_file_name)


if __name__ == '__main__':
    unittest.main()
