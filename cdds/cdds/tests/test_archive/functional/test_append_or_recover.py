# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from cdds.archive.command_line import main_store
from cdds.tests.test_archive.functional.store_test_tools import DEFAULT_LOG_DATESTAMP, TestData, LogFile, ArchiveMode
from cdds.tests.test_archive.functional.store_test_case import StoreTestCase
from cdds.tests.test_archive.functional.test_data_creator import create_use_case_various_data
from unittest import mock


class TestStoreAppendOrRecover(StoreTestCase):
    """
    USE CASE 2
        Append to embargoed data in MASS or pick up after archiving failure for variable Amon/tas

    INPUT
        1. nc files on disk
            >> /project/cdds/testdata/functional_tests/transfer/use_case_various/piControl_10096_data/CMIP6/CMIP/
                UKESM1-0-LL/piControl/r1i1p1f2/cdds_nightly_test_piControl/output/ap5/Amon/tas/
        2. Files in embargoed state already on MASS
            >> moose:/adhoc/projects/cdds/testdata/transfer_functional/use_case_continuing/development/
                CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/embargoed/v20190722/
        3. Already archived file on MASS in embargoed state:
            a. tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_187001-187912.nc
            b. tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_188001-188912.nc
            c. tas_Amon_UKESM1-0-LL_piControl_r1i1p1f2_gn_189001-189912.nc

    OUTPUT
        Output files on MASS
            >> moose:/adhoc/projects/cdds/testdata/transfer_functional/use_case_continuing/development/
                CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/embargoed/v20190722/
    """

    @mock.patch('cdds.common.get_log_datestamp', return_value=DEFAULT_LOG_DATESTAMP)
    def test_transfer_functional_usecase2_append_or_recover(self, mock_log_datestamp):
        test_dir = create_use_case_various_data('piControl_10096_proc', 'piControl_10096_data')
        test_data = TestData(
            number_variables=1,
            proc_dir_name='piControl_10096_proc',
            test_dir_root=test_dir,
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
