# (C) British Crown Copyright 2019-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring
"""
Tests for :mod:`command_line.py`.
"""
import unittest.mock

from nose.plugins.attrib import attr

from cdds_common.cdds_plugins.plugin_loader import load_plugin
from transfer.command_line import main_store
from transfer.tests.data.store_test_data import DEFAULT_LOG_DATESTAMP, TestData
from transfer.tests.data.store_test_utils import LogFile, FileState, ArchiveMode
from hadsdk.mass import mass_info


@attr('slow')
@unittest.mock.patch('hadsdk.common.get_log_datestamp', return_value=DEFAULT_LOG_DATESTAMP)
class TestMainStore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        available, cmds = mass_info(simulation=False)
        if not available:
            raise RuntimeError('MASS not available. Cannot run integration tests.')
        if not cmds['GET'] or not cmds['PUT']:
            raise RuntimeError('Needed MOSSE commands not processable. Cannot run integration tests.')

    def setUp(self):
        load_plugin()
        self.log_datestamp = DEFAULT_LOG_DATESTAMP

    def test_transfer_functional_usecase1_first_archive(self, mock_log_datestamp):
        test_data = TestData(
            number_variables=8,
            proc_dir_name='piControl_10096_proc',
            test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
            data_dir_name='piControl_10096_data',
            request_filename='cdds_request_piControl_10096.json',
            mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
            mass_suffix='use_case_first',
            log_name='test_transfer_functional_usecase1_first_archive'
        )
        test_args = test_data.get_arguments()

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 0)
        log_file = LogFile.load(test_args, test_data.log_name, DEFAULT_LOG_DATESTAMP)
        self.assertSize(log_file.archive_cmds(ArchiveMode.FIRST_PUBLICATION), test_data.number_variables)
        self.assertSize(log_file.moo_test_cmds(), 0)
        self.assertSize(log_file.moo_mkdir_cmds(), test_data.number_variables)
        self.assertSize(log_file.moo_put_cmds(), test_data.number_variables)
        self.assertSize(log_file.critical(), 0)

    def test_transfer_functional_usecase1_first_archive_single_stream(self, mock_log_datestamp):
        test_data = TestData(
            number_variables=4,
            proc_dir_name='piControl_10096_proc',
            test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
            data_dir_name='piControl_10096_data',
            request_filename='cdds_request_piControl_10096.json',
            mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
            mass_suffix='use_case_first',
            log_name='test_transfer_functional_usecase1_first_archive_single_stream',
            stream='ap5'
        )
        test_args = test_data.get_arguments()

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 0)
        log_file = LogFile.load(test_args, test_data.log_name, DEFAULT_LOG_DATESTAMP)
        self.assertSize(log_file.archive_cmds(ArchiveMode.FIRST_PUBLICATION), test_data.number_variables)
        self.assertSize(log_file.moo_test_cmds(), 0)
        self.assertSize(log_file.moo_mkdir_cmds(), test_data.number_variables)
        self.assertSize(log_file.moo_put_cmds(), test_data.number_variables)

    def test_transfer_functional_usecase2_append_or_recover(self, mock_log_datestamp):
        test_data = TestData(
            number_variables=8,
            proc_dir_name='piControl_10096_proc',
            test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
            data_dir_name='piControl_10096_data',
            request_filename='cdds_request_piControl_10096.json',
            mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
            mass_suffix='use_case_continuing',
            log_name='test_transfer_functional_usecase2_append_or_recover'
        )
        test_args = test_data.get_arguments()

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 0)
        log_file = LogFile.load(test_args, test_data.log_name, DEFAULT_LOG_DATESTAMP)
        self.assertSize(log_file.archive_cmds(ArchiveMode.CONTINUE_ABORTED), test_data.number_variables)
        self.assertSize(log_file.moo_test_cmds(), 0)
        self.assertSize(log_file.moo_mkdir_cmds(), test_data.number_variables)
        self.assertSize(log_file.moo_put_cmds(), test_data.number_variables)
        self.assertHasFiles(log_file.moo_put_files(), '205001-214912', '215001-216912')
        self.assertSize(log_file.critical(), 0)

    def test_transfer_functional_usecase3_extend_submitted(self, mock_log_datestamp):
        test_data = TestData(
            number_variables=8,
            proc_dir_name='piControl_10096_proc',
            test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case3_appending',
            data_dir_name='piControl_10096_data',
            request_filename='cdds_request_piControl_10096.json',
            mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
            mass_suffix='use_case_appending',
            log_name='test_transfer_functional_usecase3_extend_submitted'
        )
        test_args = test_data.get_arguments()

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 0)
        log_file = LogFile.load(test_args, test_data.log_name, DEFAULT_LOG_DATESTAMP)
        self.assertSize(log_file.archive_cmds(ArchiveMode.APPEND_IN_TIME), test_data.number_variables)
        self.assertSize(log_file.moo_test_cmds(), 0)
        self.assertSize(log_file.moo_mkdir_cmds(), test_data.number_variables * 3)
        self.assertSize(log_file.moo_put_cmds(), test_data.number_variables * 2)
        self.assertSize(log_file.moo_put_cmds(FileState.SUPERSEDED), test_data.number_variables)
        self.assertSize(log_file.moo_put_cmds(FileState.EMBARGOED), test_data.number_variables)
        self.assertHasFiles(log_file.moo_put_files(FileState.EMBARGOED), '215001-216912')
        self.assertSize(log_file.moo_mv_cmds(), test_data.number_variables)
        self.assertHasFiles(log_file.moo_mv_files(), '196001-204912', '205001-214912')
        self.assertSize(log_file.critical(), 0)

    def test_transfer_functional_usecase4_replace_withdrawn(self, mock_log_datestamp):
        test_data = TestData(
            number_variables=8,
            proc_dir_name='piControl_10096_proc',
            test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
            data_dir_name='piControl_10096_data',
            request_filename='cdds_request_piControl_10096.json',
            mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
            mass_suffix='use_case_previously_withdrawn',
            log_name='test_transfer_functional_usecase4_replace_withdrawn'
        )
        test_args = test_data.get_arguments()

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 0)
        log_file = LogFile.load(test_args, test_data.log_name, DEFAULT_LOG_DATESTAMP)
        self.assertSize(log_file.archive_cmds(ArchiveMode.PREVIOUSLY_WITHDRAWN), test_data.number_variables)
        self.assertSize(log_file.moo_test_cmds(), 0)
        self.assertSize(log_file.moo_mkdir_cmds(), test_data.number_variables)
        self.assertSize(log_file.moo_put_cmds(), test_data.number_variables)
        self.assertSize(log_file.critical(), 0)

    def test_transfer_functional_usecase5_already_submitted(self, mock_log_datestamp):
        test_data = TestData(
            number_variables=8,
            proc_dir_name='piControl_10096_proc',
            test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
            data_dir_name='piControl_10096_data',
            request_filename='cdds_request_piControl_10096.json',
            mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
            mass_suffix='use_case_previously_published',
            log_name='test_transfer_functional_usecase5_already_submitted'
        )
        test_args = test_data.get_arguments()

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 1)
        log_file = LogFile.load(test_args, test_data.log_name, DEFAULT_LOG_DATESTAMP)
        self.assertSize(log_file.critical(), test_data.number_variables)
        # these are critical messages for the day/uas and day/vas variables,
        # which are active in the RV file but have no data, so checking
        # that critical messages were correctly produced.
        self.assertMessagesContain(log_file.critical(), 'already in available state', 'invalid mass state')

    def test_transfer_functional_usecase6_multiple_embargoed(self, mock_log_datestamp):
        test_data = TestData(
            number_variables=8,
            proc_dir_name='piControl_10096_proc',
            test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
            data_dir_name='piControl_10096_data',
            request_filename='cdds_request_piControl_10096.json',
            mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
            mass_suffix='use_case_multiple_embargoed',
            log_name='test_transfer_functional_usecase6_multiple_embargoed'
        )
        test_args = test_data.get_arguments()

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 1)
        log_file = LogFile.load(test_args, test_data.log_name, DEFAULT_LOG_DATESTAMP)
        self.assertSize(log_file.critical(), test_data.number_variables)
        # these are critical messages for the day/uas and day/vas variables,
        # which are active in the RV file but have no data, so checking
        # that critical messages were correctly produced.
        self.assertMessagesContain(
            log_file.critical(), 'embargoed state with a different datestamp', 'invalid mass state'
        )

    def test_transfer_functional_usecase7_altering_published_datestamp(self, mock_log_datestamp):
        test_data = TestData(
            number_variables=8,
            proc_dir_name='piControl_10096_proc',
            test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
            data_dir_name='piControl_10096_data',
            request_filename='cdds_request_piControl_10096.json',
            mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
            mass_suffix='use_case_used_timestamp',
            log_name='test_transfer_functional_usecase7_altering_published_datestamp'
        )
        test_args = test_data.get_arguments()

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 1)
        log_file = LogFile.load(test_args, test_data.log_name, DEFAULT_LOG_DATESTAMP)
        self.assertSize(log_file.critical(), test_data.number_variables)
        # these are critical messages for the day/uas and day/vas variables,
        # which are active in the RV file but have no data, so checking
        # that critical messages were correctly produced.
        self.assertMessagesContain(log_file.critical(), 'used datestamp', 'invalid mass state')

    def test_transfer_functional_usecase8_datestamp_reuse(self, mock_log_datestamp):
        test_data = TestData(
            number_variables=1,
            proc_dir_name='piControl_10096_proc',
            test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case8',
            data_dir_name='piControl_10096_data',
            request_filename='cdds_request_piControl_10096.json',
            mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
            mass_suffix='use_case_8',
            log_name='test_transfer_functional_usecase8_datestamp_reuse'
        )
        test_args = test_data.get_arguments()

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 1)
        log_file = LogFile.load(test_args, test_data.log_name, DEFAULT_LOG_DATESTAMP)
        self.assertSize(log_file.critical(), test_data.number_variables)
        self.assertMessagesContain(
            log_file.critical(), 'publish data with a previously used datestamp', 'invalid mass state'
        )

    def test_transfer_functional_usecase9_prepending(self, mock_log_datestamp):
        test_data = TestData(
            number_variables=1,
            proc_dir_name='piControl_10096_proc',
            test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case9',
            data_dir_name='piControl_10096_data',
            request_filename='cdds_request_piControl_10096.json',
            mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
            mass_suffix='use_case_9',
            log_name='test_transfer_functional_usecase9_prepending'
        )
        test_args = test_data.get_arguments()

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 0)
        log_file = LogFile.load(test_args, test_data.log_name, DEFAULT_LOG_DATESTAMP)
        self.assertSize(log_file.archive_cmds(ArchiveMode.PREPEND_IN_TIME), test_data.number_variables)
        self.assertSize(log_file.moo_test_cmds(), 0)
        self.assertSize(log_file.moo_mkdir_cmds(), test_data.number_variables * 3)
        self.assertSize(log_file.moo_put_cmds(), test_data.number_variables * 2)
        self.assertSize(log_file.moo_put_cmds(FileState.EMBARGOED), test_data.number_variables)
        self.assertHasFiles(log_file.moo_put_files(FileState.EMBARGOED), '190001-195912')
        self.assertSize(log_file.moo_mv_cmds(), test_data.number_variables)
        self.assertSize(log_file.critical(), 0)

    def test_transfer_functional_usecase10_prepending_to_embargoed(self, mock_log_datestamp):
        test_data = TestData(
            number_variables=1,
            data_version='v20191120',
            proc_dir_name='piControl_10096_proc',
            test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case10',
            data_dir_name='piControl_10096_data',
            request_filename='cdds_request_piControl_10096.json',
            mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
            mass_suffix='use_case_10',
            log_name='test_transfer_functional_usecase10_prepending'
        )
        test_args = test_data.get_arguments()

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 0)
        log_file = LogFile.load(test_args, test_data.log_name, DEFAULT_LOG_DATESTAMP)
        self.assertSize(log_file.archive_cmds(ArchiveMode.PREPEND_IN_TIME), test_data.number_variables)
        self.assertSize(log_file.moo_test_cmds(), 0)
        self.assertSize(log_file.moo_mkdir_cmds(), test_data.number_variables)
        self.assertSize(log_file.moo_put_cmds(), test_data.number_variables)
        self.assertSize(log_file.moo_put_cmds(FileState.EMBARGOED), test_data.number_variables)
        self.assertHasFiles(log_file.moo_put_files(FileState.EMBARGOED), '190001-195912')
        self.assertSize(log_file.critical(), 0)

    @unittest.mock.patch('hadsdk.mass.run_mass_command', side_effect=RuntimeError("moo command failed"))
    def test_transfer_functional_failing_moo(self, mock_run_command, mock_log_datestamp):
        test_data = TestData(
            number_variables=1,
            proc_dir_name='piControl_10096_proc',
            test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
            data_dir_name='piControl_10096_data',
            request_filename='cdds_request_piControl_10096.json',
            mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
            mass_suffix='use_case_failing_mass',
            log_name='test_transfer_functional_failing_mass'
        )
        test_args = test_data.get_arguments()

        exit_code = main_store(test_args)

        self.assertEqual(exit_code, 2)
        log_file = LogFile.load(test_args, test_data.log_name, self.log_datestamp)
        self.assertSize(log_file.critical(), 2)
        self.assertMessagesContain(log_file.critical(), 'moo command failed')

    def assertSize(self, actual_list, expected_size):
        self.assertEqual(len(actual_list), expected_size)

    def assertHasFiles(self, filelist_per_cmd, *sub_filenames):
        for filelist in filelist_per_cmd:
            self.assertSize(filelist, len(sub_filenames))
            for index, filename in enumerate(sub_filenames):
                self.assertIn(filename, filelist[index])

    def assertMessagesContain(self, messages, *expected_sub_messages):
        for message in messages:
            for expected_sub_message in expected_sub_messages:
                self.assertIn(expected_sub_message, message)


if __name__ == '__main__':
    unittest.main()
