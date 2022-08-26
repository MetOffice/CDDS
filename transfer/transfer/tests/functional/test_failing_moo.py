# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from transfer.command_line import main_store
from transfer.tests.functional.store_test_tools import DEFAULT_LOG_DATESTAMP, TestData, LogFile
from transfer.tests.functional.store_test_case import StoreTestCase
from unittest import mock


class TestStoreFailingMoo(StoreTestCase):
    """
    USE CASE 11
        Test MASS command failures

    INPUT
        nc files on disk
            >> /project/cdds/testdata/functional_tests/transfer/use_case_various/piControl_10096_data/CMIP6/CMIP/
                UKESM1-0-LL/piControl/r1i1p1f2/cdds_nightly_test_piControl/output/ap5/Amon/tas/

    OUTPUT
        Critical errors in log because of MASS failure
    """

    @mock.patch('hadsdk.common.get_log_datestamp', return_value=DEFAULT_LOG_DATESTAMP)
    @mock.patch('hadsdk.mass.run_mass_command', side_effect=RuntimeError("moo command failed"))
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
        log_file = LogFile.load(test_args, test_data.log_name, DEFAULT_LOG_DATESTAMP)
        self.assertSize(log_file.critical(), 2)
        self.assertMessagesContain(log_file.critical(), 'moo command failed')
