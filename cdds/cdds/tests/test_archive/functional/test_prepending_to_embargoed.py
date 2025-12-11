# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
from cdds.archive.command_line import main_store
from cdds.tests.test_archive.functional.store_test_tools import (DEFAULT_LOG_DATESTAMP, FileState, ArchiveMode,
                                                                 TestData, LogFile)
from cdds.tests.test_archive.functional.store_test_case import StoreTestCase
from cdds.tests.test_archive.functional.store_test_data import setup_prepending_to_embargoed_test_data
from unittest import mock


class TestStorePrependingToEmbargoed(StoreTestCase):
    """USE CASE 10
        Prepend to embargoed data in MASS or pick up after archiving failure for variable Amon/tas

    INPUT
        1. nc files on disk
            >> /project/cdds/testdata/functional_tests/transfer/use_case10/piControl_10096_data/CMIP6/CMIP/
                UKESM1-0-LL/piControl/r1i1p1f2/cdds_nightly_test_piControl/output/ap5/Amon/tas/
        2. Files in embargoed state already on MASS
            >> moose:moo ls moose:/adhoc/projects/cdds/testdata/transfer_functional/use_case_10/CMIP6/CMIP/MOHC/
                UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/embargoed/v20191120/
        3. Superseded information on MASS
            >> moose:moo ls moose:/adhoc/projects/cdds/testdata/transfer_functional/use_case_10/CMIP6/CMIP/MOHC/
                UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/superseded/v20191120/

    OUTPUT
        Output files on MASS
            >> moose:/adhoc/projects/cdds/testdata/transfer_functional/use_case_10/CMIP6/CMIP/MOHC/
                UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/v20191120/
    """

    @mock.patch('cdds.common.get_log_datestamp', return_value=DEFAULT_LOG_DATESTAMP)
    def test_transfer_functional_usecase10_prepending_to_embargoed(self, mock_log_datestamp):
        self.test_dir, variable_file = setup_prepending_to_embargoed_test_data(
            'piControl_10096_proc', 'piControl_10096_data'
        )
        test_data = TestData(
            number_variables=1,
            data_version='v20191120',
            proc_dir_name='piControl_10096_proc',
            test_dir_root=self.test_dir,
            data_dir_name='piControl_10096_data',
            request_filename='cdds_request_piControl_10096.cfg',
            mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
            mass_suffix='use_case_10',
            log_name='test_transfer_functional_usecase10_prepending',
            variables_file=variable_file
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
