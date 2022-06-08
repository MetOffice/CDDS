# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from transfer.command_line import main_store
from transfer.tests.functional.store_test_tools import DEFAULT_LOG_DATESTAMP, TestData, LogFile
from transfer.tests.functional.store_test_case import StoreTestCase
from unittest import mock


class TestStoreAlreadySubmitted(StoreTestCase):
    """
    Some description what to test
    """

    @mock.patch('hadsdk.common.get_log_datestamp', return_value=DEFAULT_LOG_DATESTAMP)
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
