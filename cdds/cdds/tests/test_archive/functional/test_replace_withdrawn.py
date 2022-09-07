# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from cdds.archive.command_line import main_store
from cdds.tests.test_archive.functional.store_test_tools import DEFAULT_LOG_DATESTAMP, TestData, LogFile, ArchiveMode
from cdds.tests.test_archive.functional.store_test_case import StoreTestCase
from unittest import mock


class TestStoreReplaceWithdrawn(StoreTestCase):
    """
    USE CASE 4
        Replace previously withdrawn dataset

    INPUT
        1. nc files on disk
            >> /project/cdds/testdata/functional_tests/transfer/use_case_various/piControl_10096_data/CMIP6/CMIP/
                UKESM1-0-LL/piControl/r1i1p1f2/cdds_nightly_test_piControl/output/ap5/Amon/tas/
        2. Files in withdrawn state already on MASS
            >> moose:/adhoc/projects/cdds/testdata/transfer_functional/use_case_previously_withdrawn/development/
                CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/withdrawn/v20190722/

    OUTPUT
        1. Output files in withdrawn state on MASS
            >> moose:/adhoc/projects/cdds/testdata/transfer_functional/use_case_previously_withdrawn/development/
                CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/withdrawn/v20190722/
        2. Output files in embargoed state on MASS
            >> moose:/adhoc/projects/cdds/testdata/transfer_functional/use_case_previously_withdrawn/development/
                CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/embargoed/v20190726/
    """

    @mock.patch('cdds.common.get_log_datestamp', return_value=DEFAULT_LOG_DATESTAMP)
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
