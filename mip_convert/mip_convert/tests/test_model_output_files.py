# (C) British Crown Copyright 2015-2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from unittest import TestCase
from unittest.mock import patch, call
from mip_convert.model_output_files import get_files_to_produce_output_netcdf_files


class TestGetFilesToProduceOutputNetCDFFiles(TestCase):

    @patch('glob.glob')
    def test_get_files_to_produce_output_netcdf_files(self, mock_glob):
        root_load_path = '/dummy/file/location'
        suite_id = 'u-aa000'
        stream_id = 'onm'
        substream = None
        ancil_files = None

        dummy_filenames = ['nemo_aa000_1m_19800101_91800701_grid-T.nc',
                           'nemo_aa000_1m_19800101_91800701_grid-U.nc',
                           'nemo_aa000_1m_19800101_91800701_grid-V.nc',
                           'nemo_aa000_1m_19800101_91800701_grid-W.nc']
        expected_output = [
            os.path.join(root_load_path, suite_id, stream_id, dummy_file) for dummy_file in dummy_filenames
        ]
        mock_glob.side_effect = [None, expected_output]

        test_output = get_files_to_produce_output_netcdf_files(root_load_path=root_load_path,
                                                               suite_id=suite_id,
                                                               stream_id=stream_id,
                                                               substream=substream,
                                                               ancil_files=ancil_files)

        call_list1 = [
            call(os.path.join(root_load_path, suite_id, stream_id, '*{0}').format(extension))
            for extension in ['.pp', '.nc']
        ]
        mock_glob.assert_has_calls(call_list1)
        self.assertEqual(test_output, expected_output)

    @patch('glob.glob')
    def test_get_files_to_produce_output_netcdf_files_substreams(self, mock_glob):
        root_load_path = '/dummy/file/location'
        suite_id = 'u-aa000'
        stream_id = 'onm'
        substream = 'grid-T'
        ancil_files = None

        dummy_filenames = ['nemo_aa000_1m_19800101_91800701_grid-T.nc',
                           'nemo_aa000_1m_19800101_91800701_grid-U.nc',
                           'nemo_aa000_1m_19800101_91800701_grid-V.nc',
                           'nemo_aa000_1m_19800101_91800701_grid-W.nc']

        expected_output = [os.path.join(root_load_path, suite_id, stream_id, dummy_filenames[0])]
        mock_glob.side_effect = [None, expected_output]
        test_output = get_files_to_produce_output_netcdf_files(root_load_path=root_load_path,
                                                               suite_id=suite_id,
                                                               stream_id=stream_id,
                                                               substream=substream,
                                                               ancil_files=ancil_files)

        calls = [call(os.path.join(root_load_path, suite_id, stream_id, '*{0}{1}').format(substream, extension))
                 for extension in ['.pp', '.nc']]
        mock_glob.assert_has_calls(calls)
        self.assertEqual(test_output, expected_output)
