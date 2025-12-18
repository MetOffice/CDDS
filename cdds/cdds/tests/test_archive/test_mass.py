# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring
"""Tests for :mod:`mass.py`."""

import copy
import os
import unittest
import unittest.mock

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.plugins import PluginStore
from cdds.common.mass_record import MassRecord

from cdds.archive.constants import (
    DATA_PUBLICATION_STATUS_DICT, SUPERSEDED_INFO_FILE_STR)
import cdds.archive.mass
from cdds.tests.factories.request_factory import simple_request
from cdds.tests.test_archive import common


class TestMassPaths(unittest.TestCase):
    def setUp(self):
        load_plugin()
        self.request = simple_request()
        self.request.metadata.mip_era = 'dummyera'
        self.request.metadata.mip = 'dummymip'
        self.request.metadata.experiment_id = 'dummy-exp123'
        self.request.metadata.variant_label = 'dummyvariant'
        self.request.metadata.model_id = 'dummymodel'
        self.request.metadata.institution_id = 'dummyinst'

    def tearDown(self):
        PluginStore.clean_instance()

    @unittest.mock.patch('cdds.archive.mass.retrieve_grid_info')
    def test_get_archive_path(self, mock_grid_info):
        grid = 'dummygrid'
        mock_grid_info.return_value = (None, None, grid, None)
        mass_root = 'moose://root/mass/location/'
        var_dict = {'mip_table_id': 'Amon', 'variable_id': 'tas',
                    'stream_id': 'ap5', 'out_var_name': 'tas', 'frequency': 'mon'}
        output_path = cdds.archive.mass.get_archive_path(mass_root, var_dict, self.request)
        reference_path = os.path.join(mass_root,
                                      self.request.metadata.mip_era,
                                      self.request.metadata.mip,
                                      self.request.metadata.institution_id,
                                      self.request.metadata.model_id,
                                      self.request.metadata.experiment_id,
                                      self.request.metadata.variant_label,
                                      var_dict['mip_table_id'],
                                      var_dict['out_var_name'], grid, )
        self.assertEqual(reference_path, output_path)

    @unittest.mock.patch('cdds.archive.mass.get_archive_path')
    def test_construct_mass_paths(self, mock_mass_path):
        var_list = copy.deepcopy(common.APPROVED_REF_WITH_FILES)
        reference_vars = []
        path_list = []
        mass_root = 'moose://root/mass/location/'
        datestamp_str = 'v20160125'
        new_status = 'dummystat'
        for var_dict in var_list:
            path1 = os.path.join(mass_root, var_dict['variable_id'])
            out_dict = {'mass_path': path1,
                        'new_datestamp': datestamp_str,
                        'mass_status_suffix':
                            os.path.join(
                                new_status,
                                datestamp_str)
                        }
            out_dict.update(var_dict)
            reference_vars += [out_dict]
            path_list += [path1]

        mock_mass_path.side_effect = path_list
        output_vars = cdds.archive.mass.construct_mass_paths(var_list,
                                                             self.request,
                                                             mass_root,
                                                             datestamp_str,
                                                             new_status)
        for ref_var, out_var in zip(reference_vars, output_vars):
            self.assertDictEqual(ref_var, out_var)

    def test_update_memberid_no_subexpt(self):
        # no sub experiment id
        self.assertEqual(self.request.metadata.sub_experiment_id, 'none')
        cdds.archive.mass.update_memberid_if_needed(self.request)
        expected_member_id = 'dummyvariant'
        self.assertEqual(self.request.metadata.variant_label, expected_member_id)

    def test_update_memberid_subexpt(self):
        # first time should add sub experiment id as prefix
        self.request.metadata.sub_experiment_id = 'this'
        cdds.archive.mass.update_memberid_if_needed(self.request)
        expected_member_id = 'this-dummyvariant'
        self.assertEqual(self.request.metadata.variant_label, expected_member_id)
        # second time should do nothing
        cdds.archive.mass.update_memberid_if_needed(self.request)
        expected_member_id = 'this-dummyvariant'
        self.assertEqual(self.request.metadata.variant_label, expected_member_id)

    def test_get_stored_data(self):
        root_mass_path = 'moose://dummy/path/to/archived/file'
        state_id = 'EMBARGOED'
        time_stamp = 'v20191112'
        mass_filename = 'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-210012.nc'
        mass_dir1 = os.path.join(root_mass_path, DATA_PUBLICATION_STATUS_DICT[state_id])
        mass_dir2 = os.path.join(mass_dir1, time_stamp)
        mass_file = os.path.join(mass_dir2, mass_filename)
        mass_records = {
            mass_dir1: MassRecord(mass_dir1, 'D'),
            mass_dir2: MassRecord(mass_dir2, 'D'),
            mass_file: MassRecord(mass_file, 'F')
        }
        var_dict = {'mip_table_id': 'Amon',
                    'variable_id': 'tas',
                    'stream': 'ap5',
                    'mass_path': root_mass_path}

        output_var_dict = cdds.archive.mass.get_stored_data(var_dict, mass_records)

        reference_var_dict = {
            state_id: {
                time_stamp: [mass_file]
            }
        }
        self.assertDictEqual(reference_var_dict, output_var_dict)


class TestArchiveFiles(unittest.TestCase):
    """Tests for :func:`archive_files` in :mod:`mass.py`."""

    def setUp(self):
        self.simulation = True

    @unittest.mock.patch('cdds.archive.mass.mass_mkdir')
    @unittest.mock.patch('cdds.archive.mass.mass_put')
    @unittest.mock.patch('cdds.archive.mass.mass_move')
    def test_archive_files_first_pub(self, mock_mass_mv, mock_mass_put, mock_mass_mkdir):
        var_list = common.APPROVED_REF_WITH_MASS
        cdds.archive.mass.archive_files(var_list, simulation=False)
        mkdir_calls = []
        put_calls = []

        for var1 in var_list:
            mass_dest = os.path.join(var1['mass_path'], 'embargoed', common.APPROVED_NEW_DATESTAMP)
            mkdir_calls += [unittest.mock.call(mass_dest, simulation=False, create_parents=True, exist_ok=True)]
            put_calls += [unittest.mock.call(
                var1['mip_output_files'], mass_dest, simulation=False, check_mass_location=False
            )]

        mock_mass_mkdir.assert_has_calls(mkdir_calls, any_order=True)
        mock_mass_put.assert_has_calls(put_calls, any_order=True)

    @unittest.mock.patch('cdds.archive.mass.mass_mkdir')
    @unittest.mock.patch('cdds.archive.mass.mass_put')
    def test_archive_files_continuing(self, mock_mass_put, mock_mass_mkdir):
        var_list = common.APPROVED_REF_WITH_MASS
        mkdir_calls = []
        put_calls = []
        input_vars = []

        cont_ix = 2

        for var1 in var_list:
            mass_dest = os.path.join(var1['mass_path'], 'embargoed', common.APPROVED_NEW_DATESTAMP)
            stored_files = [os.path.join(mass_dest, os.path.split(path1)[-1]) for path1 in var1['mip_output_files']]
            stored_state = {'EMBARGOED': {common.APPROVED_NEW_DATESTAMP: stored_files[:cont_ix]}}
            prefilter_var = {'stored_data': stored_state}
            prefilter_var.update(var1)
            prefilter_var['mass_status'] = 'PROCESSING_CONTINUATION'
            input_vars += [prefilter_var]
            mkdir_calls += [unittest.mock.call(mass_dest, simulation=False, create_parents=True, exist_ok=True)]
            put_calls += [unittest.mock.call(
                var1['mip_output_files'][cont_ix:], mass_dest, simulation=False, check_mass_location=False
            )]

        cdds.archive.mass.archive_files(input_vars, simulation=False)
        mock_mass_mkdir.assert_has_calls(mkdir_calls, any_order=True)
        mock_mass_put.assert_has_calls(put_calls, any_order=True)

    @unittest.mock.patch('cdds.archive.mass.mass_mkdir')
    @unittest.mock.patch('cdds.archive.mass.mass_put')
    def test_archive_files_continuing_var_complete(self, mock_mass_put, mock_mass_mkdir):
        var_list = common.APPROVED_REF_WITH_MASS
        mkdir_calls = []
        put_calls = []
        input_vars = []

        for var1 in var_list:
            mass_dest = os.path.join(var1['mass_path'], 'embargoed', common.APPROVED_NEW_DATESTAMP)
            stored_files = var1['mip_output_files']
            stored_state = {'EMBARGOED': {common.APPROVED_NEW_DATESTAMP: stored_files}}
            prefilter_var = {'stored_data': stored_state}
            prefilter_var.update(var1)
            prefilter_var['mass_status'] = 'PROCESSING_CONTINUATION'
            input_vars += [prefilter_var]

        cdds.archive.mass.archive_files(input_vars, simulation=False)
        mock_mass_mkdir.assert_has_calls(mkdir_calls, any_order=True)
        mock_mass_put.assert_has_calls(put_calls, any_order=True)
        self.assertEqual(mock_mass_put.call_count, 0)

    @unittest.mock.patch('cdds.archive.mass._write_superseded_info_file')
    @unittest.mock.patch('shutil.rmtree')
    @unittest.mock.patch('tempfile.mkdtemp')
    @unittest.mock.patch('cdds.archive.mass.mass_mkdir')
    @unittest.mock.patch('cdds.archive.mass.mass_put')
    @unittest.mock.patch('cdds.archive.mass.mass_move')
    @unittest.mock.patch('cdds.archive.mass.mass_rmdir')
    def test_archive_files_appending(self, mock_mass_rmdir, mock_mass_mv, mock_mass_put, mock_mass_mkdir, mock_mkdtemp,
                                     mock_rmtree, mock_write_info_file):
        var_list = common.APPROVED_REF_WITH_MASS
        mkdir_calls = []
        put_calls = []
        input_var_list = []
        move_calls = []
        rmdir_calls = []
        cont_ix = {'tas': 1, 'ua': 2, 'tos': 1}
        tmp_dir_path = '/path/to/temp'

        for var1 in var_list:
            vid = var1['variable_id']
            mass_src = os.path.join(var1['mass_path'], 'available', common.OLD_DATESTAMP)
            mass_dest = os.path.join(var1['mass_path'], 'embargoed', common.APPROVED_NEW_DATESTAMP)
            stored_paths = [os.path.join(mass_src, os.path.split(p1)[-1]) for p1 in var1['mip_output_files']]
            files_to_move = stored_paths[:cont_ix[vid]]
            stored_state = {'AVAILABLE': {common.OLD_DATESTAMP: files_to_move}}
            input_var1 = {'stored_data': stored_state}
            input_var1.update(var1)
            input_var1['mass_status'] = 'APPENDING'
            input_var1['mip_output_files'] = (var1['mip_output_files'][cont_ix[vid]:])
            input_var_list += [input_var1]
            move_calls += [unittest.mock.call(files_to_move, mass_dest, simulation=False, check_mass_location=True)]
            mkdir_calls += [unittest.mock.call(mass_dest, simulation=False, create_parents=True, exist_ok=True)]
            log_fname = SUPERSEDED_INFO_FILE_STR.format(**input_var1)
            log_path = os.path.join(tmp_dir_path, log_fname)
            mass_dir_superseded = os.path.join(var1['mass_path'], 'superseded', common.OLD_DATESTAMP)
            put_calls += [
                unittest.mock.call([log_path], mass_dir_superseded, simulation=False, check_mass_location=True)
            ]
            put_calls += [
                unittest.mock.call(
                    var1['mip_output_files'][cont_ix[vid]:], mass_dest, simulation=False, check_mass_location=False
                )]
            rmdir_calls += [unittest.mock.call(mass_src, simulation=False)]

        mock_rmtree.return_value = None
        mock_mkdtemp.return_value = tmp_dir_path
        cdds.archive.mass.archive_files(input_var_list, simulation=False)
        self.assertEqual(mock_write_info_file.call_count, len(var_list))
        mock_mass_mv.assert_has_calls(move_calls, any_order=True)
        mock_mass_mkdir.assert_has_calls(mkdir_calls, any_order=True)
        mock_mass_put.assert_has_calls(put_calls, any_order=True)
        mock_mass_rmdir.assert_has_calls(rmdir_calls, any_order=True)

    @unittest.mock.patch('cdds.archive.mass.mass_mkdir')
    @unittest.mock.patch('cdds.archive.mass.mass_put')
    def test_archive_files_withdrawn(self, mock_mass_put, mock_mass_mkdir):
        var_list = common.APPROVED_REF_WITH_MASS
        input_var_list = []
        mkdir_calls = []
        put_calls = []

        for var1 in var_list:
            files_to_move = var1['mip_output_files']
            mass_old = os.path.join(var1['mass_path'], 'withdrawn', common.OLD_DATESTAMP)
            mass_dest = os.path.join(var1['mass_path'], 'embargoed', common.APPROVED_NEW_DATESTAMP)
            stored_files = [os.path.join(mass_old, os.path.split(path1)[-1]) for path1 in files_to_move]
            stored_state = {'WITHDRAWN': {common.OLD_DATESTAMP: stored_files}}
            input_var1 = {'stored_data': stored_state}
            input_var1.update(var1)
            input_var_list += [input_var1]
            mkdir_calls += [unittest.mock.call(mass_dest, simulation=False, create_parents=True, exist_ok=True)]
            put_calls += [unittest.mock.call(
                var1['mip_output_files'], mass_dest, simulation=False, check_mass_location=False
            )]

        cdds.archive.mass.archive_files(input_var_list, simulation=False)
        mock_mass_mkdir.assert_has_calls(mkdir_calls, any_order=True)
        mock_mass_put.assert_has_calls(put_calls, any_order=True)


if __name__ == '__main__':
    unittest.main()
