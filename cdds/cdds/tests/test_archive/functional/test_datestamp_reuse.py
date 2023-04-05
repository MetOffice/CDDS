# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from cdds.archive.command_line import main_store
from cdds.tests.test_archive.functional.store_test_tools import DEFAULT_LOG_DATESTAMP, TestData, LogFile
from cdds.tests.test_archive.functional.store_test_case import StoreTestCase
from cdds.tests.test_archive.functional.test_data_creator import create_use_case_various_data
from unittest import mock


class TestStoreDatestampReuse(StoreTestCase):
    """
    USE CASE 8
        Archive data when there is already data with a same datestamp in the embargoed state

    INPUT
        1. nc files on disk
            >> /project/cdds/testdata/functional_tests/transfer/use_case8/piControl_10096_data/CMIP6/CMIP/
                UKESM1-0-LL/piControl/r1i1p1f2/cdds_nightly_test_piControl/output/ap5/Amon/tas/
        2. Available files already on MASS
            >> moose:/adhoc/projects/cdds/testdata/transfer_functional/use_case_8/CMIP6/CMIP/MOHC/
                UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/available/v20191128/
        3. Superseded information on MASS
            >> moose:/adhoc/projects/cdds/testdata/transfer_functional/use_case_8/CMIP6/CMIP/MOHC/
                UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/superseded/v20190810

    OUTPUT
        Critical errors for this variable in log file
    """

    @mock.patch('cdds.common.get_log_datestamp', return_value=DEFAULT_LOG_DATESTAMP)
    def test_transfer_functional_usecase8_datestamp_reuse(self, mock_log_datestamp):
        test_dir = create_use_case_various_data('piControl_10096_proc', 'piControl_10096_data')
        test_data = TestData(
            number_variables=1,
            proc_dir_name='piControl_10096_proc',
            test_dir_root=test_dir,
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
