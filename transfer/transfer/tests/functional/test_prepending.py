# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from transfer.command_line import main_store
from transfer.tests.functional.store_test_tools import DEFAULT_LOG_DATESTAMP, FileState, ArchiveMode, TestData, LogFile
from transfer.tests.functional.store_test_case import StoreTestCase
from unittest import mock


class TestStorePrepending(StoreTestCase):
    """
    Some description what to test
    """

    @mock.patch('hadsdk.common.get_log_datestamp', return_value=DEFAULT_LOG_DATESTAMP)
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
