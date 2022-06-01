# (C) British Crown Copyright 2019-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring
"""
Tests for :mod:`command_line.py`.
"""
import os
import shutil
import tempfile
import unittest.mock

from nose.plugins.attrib import attr

from cdds_common.cdds_plugins.plugin_loader import load_plugin
from transfer.command_line import main_store, parse_args_store
from transfer.tests.data.store_test_data import TestData, UseCase
from transfer.tests.data.store_test_log import LogFile, LogKey
from hadsdk.mass import mass_info
from hadsdk.config import FullPaths
from hadsdk.request import read_request


@attr('slow')
@unittest.mock.patch('hadsdk.common.get_log_datestamp', return_value='2019-11-23T1432Z')
class TestMainStore(unittest.TestCase):
    """
    Tests for :func:`main` in :mod:`command_line.py`.
    These are functional integration that run through the cdds_store script
    for the various use cases described in the CDDS wiki here:
    https://code.metoffice.gov.uk/trac/cdds/wiki/ticket/641/...
    ...TransferArchivingUseCases
    """

    @classmethod
    def setUpClass(cls):
        available, cmds = mass_info(simulation=False)
        if not available:
            raise RuntimeError('MASS not available. Cannot run integration tests.')
        if not cmds['GET'] or not cmds['PUT']:
            raise RuntimeError('Needed MOSSE commands not processable. Cannot run integration tests.')

    def setUp(self):
        load_plugin()
        self.files_to_delete = []
        self.directories_to_delete = []
        self.temp_test_dir = tempfile.mkdtemp()
        self.directories_to_delete += [self.temp_test_dir]

        self.test_dir_root = ('/project/cdds/testdata/functional_tests/'
                              'transfer/use_case_various')
        self.proc_dir_name = 'piControl_10096_proc'
        self.data_dir_name = 'piControl_10096_data'
        self.log_datestamp = '2019-11-23T1432Z'
        shutil.copytree(os.path.join(self.test_dir_root, self.proc_dir_name),
                        os.path.join(self.temp_test_dir, self.proc_dir_name))
        self.request_filename = 'cdds_request_piControl_10096.json'
        self.log_name = 'transfer_functional_test'
        self.mass_test_base = ('moose:/adhoc/projects/cdds/testdata/'
                               'transfer_functional')

    def tearDown(self):
        for fname1 in self.files_to_delete:
            if os.path.isfile(fname1):
                os.remove(fname1)
        for dir1 in self.directories_to_delete:
            if os.path.isdir(dir1):
                shutil.rmtree(dir1)

    def construct_args(self, test_data: TestData):
        base_args = [
            test_data.request_json_path,
            '--use_proc_dir',
            '--data_version', test_data.data_version,
            '--root_proc_dir', test_data.root_proc_dir,
            '--root_data_dir', test_data.root_data_dir,
            '--output_mass_root', test_data.mass_root,
            '--output_mass_suffix', test_data.mass_suffix,
            '--log_name', test_data.log_name,
            '--simulate',
        ]
        if test_data.stream:
            base_args += ['--stream', test_data.stream]
        return base_args

    def _construct_base_args(self, test_temp_dir, data_version='v20191128'):
        self.root_proc_dir = os.path.join(test_temp_dir,
                                          self.proc_dir_name)
        self.root_data_dir = os.path.join(self.test_dir_root,
                                          self.data_dir_name)
        self.request_json_path = os.path.join(self.test_dir_root,
                                              self.request_filename)
        base_args = [
            self.request_json_path,
            '--use_proc_dir',
            '--data_version', data_version,
            '--root_proc_dir', self.root_proc_dir,
            '--root_data_dir', self.root_data_dir,
            '--output_mass_root', self.mass_root,
            '--output_mass_suffix', self.mass_suffix,
            '--log_name', self.log_name,
            '--simulate',
        ]
        return base_args

    def _get_log_file_contents(self, test_args, stream=None):
        args = parse_args_store(test_args, 'cdds_store')
        request = read_request(args.request)
        fp = FullPaths(args, request)
        log_dir = fp.log_directory('archive')
        if stream:
            log_fname = '{0}_{1}_{2}.log'.format(self.log_name, stream, self.log_datestamp)
        else:
            log_fname = '{0}_{1}.log'.format(self.log_name, self.log_datestamp)
        log_path = os.path.join(log_dir, log_fname)
        with open(log_path) as log_file:
            log_txt = log_file.readlines()
        return log_txt

    def test_transfer_functional_usecase1_first_archive(self, mock_log_datestamp):
        test_data = UseCase.FIRST_ARCHIVE.data
        test_args = self.construct_args(test_data)

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 0)
        log_file = LogFile.load(test_args, test_data.log_name, self.log_datestamp)
        self.assertSize(log_file.archive_cmds(LogKey.FIRST_PUBLICATION), test_data.number_variables)
        self.assertSize(log_file.simulation_cmds(LogKey.MOO_TEST), 0)
        self.assertSize(log_file.simulation_cmds(LogKey.MOO_MKDIR), test_data.number_variables)
        self.assertSize(log_file.simulation_cmds(LogKey.MOO_PUT), test_data.number_variables)
        self.assertSize(log_file.critical(), 0)

    def assertSize(self, actual_list, expected_size):
        self.assertEqual(len(actual_list), expected_size)

    def test_transfer_functional_usecase1_first_archive_single_stream(self, mock_log_datestamp):
        test_data = UseCase.FIRST_ARCHIVE_SINGLE_STREAM.data
        test_args = self.construct_args(test_data)

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 0)
        log_file = LogFile.load(test_args, test_data.log_name, self.log_datestamp)
        self.assertSize(log_file.archive_cmds(LogKey.FIRST_PUBLICATION), test_data.number_variables)
        self.assertSize(log_file.simulation_cmds(LogKey.MOO_TEST), 0)
        self.assertSize(log_file.simulation_cmds(LogKey.MOO_MKDIR), test_data.number_variables)
        self.assertSize(log_file.simulation_cmds(LogKey.MOO_PUT), test_data.number_variables)

    def test_transfer_functional_usecase2_append_or_recover(self, mock_log_datestamp):
        test_data = UseCase.APPEND_OR_RECOVER.data
        test_args = self.construct_args(test_data)

        exit_code = main_store(test_args)
        self.assertEqual(exit_code, 0)
        log_file = LogFile.load(test_args, test_data.log_name, self.log_datestamp)
        self.assertSize(log_file.archive_cmds(LogKey.CONTINUE_ABORTED), test_data.number_variables)
        self.assertSize(log_file.simulation_cmds(LogKey.MOO_TEST), 0)
        self.assertSize(log_file.simulation_cmds(LogKey.MOO_MKDIR), test_data.number_variables)
        self.assertSize(log_file.simulation_cmds(LogKey.MOO_PUT), test_data.number_variables)
        filelist = log_file.moo_put_files()
        self.assertEqual(len(filelist), 2)
        self.assertIn('205001-214912', filelist[0])
        self.assertIn('215001-216912', filelist[1])
        self.assertSize(log_file.critical(), 0)

    def test_transfer_functional_usecase3_extend_submitted(self, mock_log_datestamp):
        test_data = UseCase.EXTEND_SUBMITTED.data
        test_args = self.construct_args(test_data)

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 0)
        log_file = LogFile.load(test_args, test_data.log_name, self.log_datestamp)
        self.assertSize(log_file.archive_cmds(LogKey.APPEND_IN_TIME), test_data.number_variables)
        self.assertSize(log_file.simulation_cmds(LogKey.MOO_TEST), 0)
        self.assertSize(log_file.simulation_cmds(LogKey.MOO_MKDIR), test_data.number_variables * 3)
        self.assertSize(log_file.simulation_cmds(LogKey.MOO_PUT), test_data.number_variables * 2)
        self.assertSize(log_file.moo_put_cmds(LogKey.SUPERSEDED), test_data.number_variables)
        self.assertSize(log_file.moo_put_cmds(LogKey.EMBARGOED), test_data.number_variables)
        for cmd1 in log_file.moo_put_cmds(LogKey.EMBARGOED):
            filelist = sorted(cmd1.split()[9:-1])
            self.assertEqual(len(filelist), 1)
            self.assertIn('215001-216912', filelist[0])
        self.assertSize(log_file.simulation_cmds(LogKey.MOO_MV), test_data.number_variables)
        for cmd1 in log_file.simulation_cmds(LogKey.MOO_MV):
            filelist = sorted(cmd1.split()[9:-1])
            self.assertEqual(len(filelist), 2)
            self.assertIn('196001-204912', filelist[0])
            self.assertIn('205001-214912', filelist[1])
        self.assertSize(log_file.critical(), 0)

    @unittest.mock.patch('hadsdk.common.get_log_datestamp')
    def test_transfer_functional_usecase4_replace_withdrawn(
            self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        self.log_name = ('test_transfer_functional_'
                         'usecase4_replace_withdrawn')
        self.mass_root = self.mass_test_base
        self.mass_suffix = 'use_case_previously_withdrawn'
        self.mass_root = os.path.join(self.mass_test_base,
                                      '')
        test_args = self._construct_base_args(self.temp_test_dir)
        exit_code = main_store(test_args)
        self.assertEqual(exit_code, 0)
        log_txt = self._get_log_file_contents(test_args)
        num_vars = 8
        mode_msgs = [l1 for l1 in log_txt if 'archiving mode' in l1.lower()]
        wd_mode_msgs = [l1 for l1 in mode_msgs if
                        'previously withdrawn' in l1.lower()]
        self.assertEqual(num_vars, len(wd_mode_msgs))
        mass_log_cmds = [l1 for l1 in log_txt if
                         'simulating mass command' in l1]
        mass_is_dir_cmds = [mc1 for mc1 in mass_log_cmds if 'moo test' in mc1]
        self.assertEqual(len(mass_is_dir_cmds), 0)
        mass_mkdir_cmds = [mc1 for mc1 in mass_log_cmds if 'moo mkdir' in mc1]
        self.assertEqual(len(mass_mkdir_cmds), num_vars)
        mass_put_cmds = [mc1 for mc1 in mass_log_cmds if 'moo put' in mc1]
        self.assertEqual(len(mass_put_cmds), num_vars)
        critical_msgs = [l1 for l1 in log_txt if 'CRITICAL' in l1]
        # these are critical messages for the day/uas and day/vas
        # variables, which are active in the RV file but have no
        # data, so checking that critical messages were
        # correctly produced.
        self.assertEqual(0, len(critical_msgs))

    @unittest.mock.patch('hadsdk.common.get_log_datestamp')
    def test_transfer_functional_usecase5_already_submitted(
            self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        self.log_name = ('test_transfer_functional_'
                         'usecase5_already_submitted')
        self.mass_root = self.mass_test_base
        self.mass_suffix = 'use_case_previously_published'
        test_args = self._construct_base_args(self.temp_test_dir)
        exit_code = main_store(test_args)
        self.assertEqual(exit_code, 1)
        log_txt = self._get_log_file_contents(test_args)
        num_vars = 8
        critical_msgs = [l1 for l1 in log_txt if 'CRITICAL' in l1]
        self.assertEqual(num_vars, len(critical_msgs))
        # these are critical messages for the day/uas and day/vas
        # variables, which are active in the RV file but have no
        # data, so checking that critical messages were
        # correctly produced.
        crit_msgs_invalid_state = sorted(critical_msgs)
        for msg1 in crit_msgs_invalid_state:
            self.assertIn('already in available state', msg1)
            self.assertIn('invalid mass state', msg1)

    @unittest.mock.patch('hadsdk.common.get_log_datestamp')
    def test_transfer_functional_usecase6_multiple_embargoed(
            self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        self.log_name = ('test_transfer_functional_'
                         'usecase6_multiple_embargoed')
        self.mass_root = self.mass_test_base
        self.mass_suffix = 'use_case_multiple_embargoed'
        test_args = self._construct_base_args(self.temp_test_dir)
        exit_code = main_store(test_args)
        self.assertEqual(exit_code, 1)
        log_txt = self._get_log_file_contents(test_args)
        num_vars = 8
        critical_msgs = [l1 for l1 in log_txt if 'CRITICAL' in l1]
        self.assertEqual(num_vars, len(critical_msgs))
        # these are critical messages for the day/uas and day/vas
        # variables, which are active in the RV file but have no
        # data, so checking that critical messages were
        # correctly produced.
        crit_msgs_invalid_state = sorted(critical_msgs)
        for msg1 in crit_msgs_invalid_state:
            self.assertIn('embargoed state with a different datestamp', msg1)
            self.assertIn('invalid mass state', msg1)

    @unittest.mock.patch('hadsdk.common.get_log_datestamp')
    def test_transfer_functional_usecase7_altering_published_datestamp(
            self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        self.log_name = ('test_transfer_functional_'
                         'usecase7_altering_published_datestamp')
        self.mass_root = self.mass_test_base
        self.mass_suffix = 'use_case_used_timestamp'
        test_args = self._construct_base_args(self.temp_test_dir)
        exit_code = main_store(test_args)
        self.assertEqual(exit_code, 1)
        log_txt = self._get_log_file_contents(test_args)
        num_vars = 8
        critical_msgs = [l1 for l1 in log_txt if 'CRITICAL' in l1]
        self.assertEqual(num_vars, len(critical_msgs))
        # these are critical messages for the day/uas and day/vas
        # variables, which are active in the RV file but have no
        # data, so checking that critical messages were
        # correctly produced.
        crit_msgs_invalid_state = sorted(critical_msgs)
        for msg1 in crit_msgs_invalid_state:
            self.assertIn('used datestamp', msg1)
            self.assertIn('invalid mass state', msg1)

    @unittest.mock.patch('hadsdk.common.get_log_datestamp')
    def test_transfer_functional_usecase8_datestamp_reuse(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        self.log_name = 'test_transfer_functional_usecase8_datestamp_reuse'
        self.test_dir_root = '/project/cdds/testdata/functional_tests/transfer/use_case8'
        temp_test_dir = tempfile.mkdtemp()
        self.directories_to_delete += [temp_test_dir]
        shutil.copytree(os.path.join(self.test_dir_root, self.proc_dir_name),
                        os.path.join(temp_test_dir, self.proc_dir_name))
        self.mass_root = self.mass_test_base
        self.mass_suffix = 'use_case_8'
        test_args = self._construct_base_args(temp_test_dir)

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 1)
        log_txt = self._get_log_file_contents(test_args)
        num_vars = 1
        critical_msgs = [l1 for l1 in log_txt if 'CRITICAL' in l1]
        self.assertEqual(num_vars, len(critical_msgs))
        crit_msgs_invalid_state = sorted(critical_msgs)
        for msg1 in crit_msgs_invalid_state:
            self.assertIn('publish data with a previously used datestamp', msg1)
            self.assertIn('invalid mass state', msg1)

    @unittest.mock.patch('hadsdk.common.get_log_datestamp')
    def test_transfer_functional_usecase9_prepending(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        self.log_name = 'test_transfer_functional_usecase9_prepending'
        self.test_dir_root = '/project/cdds/testdata/functional_tests/transfer/use_case9'
        temp_test_dir = tempfile.mkdtemp()
        self.directories_to_delete += [temp_test_dir]
        shutil.copytree(os.path.join(self.test_dir_root, self.proc_dir_name),
                        os.path.join(temp_test_dir, self.proc_dir_name))
        self.mass_root = self.mass_test_base
        self.mass_suffix = 'use_case_9'
        test_args = self._construct_base_args(temp_test_dir)

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 0)
        log_txt = self._get_log_file_contents(test_args)
        mass_log_cmds = [l1 for l1 in log_txt if 'simulating mass command' in l1]
        num_vars = 1
        mode_msgs = [l1 for l1 in log_txt if 'archiving mode' in l1.lower()]
        mode_msgs = [l1 for l1 in mode_msgs if 'prepend (in time)' in l1.lower()]
        self.assertEqual(num_vars, len(mode_msgs))
        mass_is_dir_cmds = [mc1 for mc1 in mass_log_cmds if 'moo test' in mc1]
        self.assertEqual(len(mass_is_dir_cmds), 0)
        mass_mkdir_cmds = [mc1 for mc1 in mass_log_cmds if 'moo mkdir' in mc1]
        self.assertEqual(len(mass_mkdir_cmds), num_vars * 3)
        mass_put_cmds = [mc1 for mc1 in mass_log_cmds if 'moo put' in mc1]
        self.assertEqual(len(mass_put_cmds), num_vars * 2)
        mass_put_emb_cmds = [mc1 for mc1 in mass_put_cmds if 'embargoed' in mc1]
        self.assertEqual(len(mass_put_emb_cmds), num_vars)
        for cmd1 in mass_put_emb_cmds:
            filelist = sorted(cmd1.split()[9:-1])
            self.assertEqual(len(filelist), 1)
            self.assertIn('190001-195912', filelist[0])
        mass_mv_cmds = [mc1 for mc1 in mass_log_cmds if 'moo mv' in mc1]
        self.assertEqual(len(mass_mv_cmds), 1)
        critical_msgs = [l1 for l1 in log_txt if 'CRITICAL' in l1]
        self.assertEqual(0, len(critical_msgs))

    @unittest.mock.patch('hadsdk.common.get_log_datestamp')
    def test_transfer_functional_usecase10_prepending_to_embargoed(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        self.log_name = 'test_transfer_functional_usecase10_prepending'
        self.test_dir_root = '/project/cdds/testdata/functional_tests/transfer/use_case10'
        temp_test_dir = tempfile.mkdtemp()
        self.directories_to_delete += [temp_test_dir]
        shutil.copytree(os.path.join(self.test_dir_root, self.proc_dir_name),
                        os.path.join(temp_test_dir, self.proc_dir_name))
        self.mass_root = self.mass_test_base
        self.mass_suffix = 'use_case_10'
        test_args = self._construct_base_args(temp_test_dir, 'v20191120')

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 0)
        log_txt = self._get_log_file_contents(test_args)
        mass_log_cmds = [l1 for l1 in log_txt if 'simulating mass command' in l1]
        num_vars = 1
        mode_msgs = [l1 for l1 in log_txt if 'archiving mode' in l1.lower()]
        mode_msgs = [l1 for l1 in mode_msgs if 'prepend (in time)' in l1.lower()]
        self.assertEqual(num_vars, len(mode_msgs))
        mass_is_dir_cmds = [mc1 for mc1 in mass_log_cmds if 'moo test' in mc1]
        self.assertEqual(len(mass_is_dir_cmds), 0)
        mass_mkdir_cmds = [mc1 for mc1 in mass_log_cmds if 'moo mkdir' in mc1]
        self.assertEqual(len(mass_mkdir_cmds), num_vars)
        mass_put_cmds = [mc1 for mc1 in mass_log_cmds if 'moo put' in mc1]
        self.assertEqual(len(mass_put_cmds), num_vars)
        mass_put_emb_cmds = [mc1 for mc1 in mass_put_cmds if 'embargoed' in mc1]
        self.assertEqual(len(mass_put_emb_cmds), num_vars)
        for cmd1 in mass_put_emb_cmds:
            filelist = sorted(cmd1.split()[9:-1])
            self.assertEqual(len(filelist), 1)
            self.assertIn('190001-195912', filelist[0])
        critical_msgs = [l1 for l1 in log_txt if 'CRITICAL' in l1]
        self.assertEqual(0, len(critical_msgs))

    @unittest.mock.patch('hadsdk.common.get_log_datestamp')
    @unittest.mock.patch('hadsdk.mass.run_mass_command', side_effect=RuntimeError(
        "moo command failed"))
    def test_transfer_functional_failing_moo(
            self, mock_run_command, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp

        self.log_name = ('test_transfer_functional_'
                         'failing_mass')
        self.mass_root = self.mass_test_base
        self.mass_suffix = 'use_case_failing_mass'
        test_args = self._construct_base_args(self.temp_test_dir)
        exit_code = main_store(test_args)
        self.assertEqual(exit_code, 2)
        log_txt = self._get_log_file_contents(test_args)
        critical_msgs = [l1 for l1 in log_txt if 'CRITICAL' in l1]
        self.assertEqual(2, len(critical_msgs))
        for msg1 in critical_msgs:
            self.assertIn('moo command failed', msg1)


if __name__ == '__main__':
    unittest.main()
