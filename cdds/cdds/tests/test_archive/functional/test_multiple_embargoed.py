# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
from cdds.archive.command_line import main_store
from cdds.tests.test_archive.functional.store_test_tools import DEFAULT_LOG_DATESTAMP, TestData, LogFile
from cdds.tests.test_archive.functional.store_test_case import StoreTestCase
from cdds.tests.test_archive.functional.store_test_data import setup_basic_test_data
from unittest import mock


class TestStoreMultipleEmbargoed(StoreTestCase):
    """
    USE CASE 6
        Archive data when there is already data with a different datestamp in the embargoed state

    INPUT
        1. nc files on disk
            >> /project/cdds/testdata/functional_tests/transfer/use_case_various/piControl_10096_data/CMIP6/CMIP/
                UKESM1-0-LL/piControl/r1i1p1f2/cdds_nightly_test_piControl/output/ap5/Amon/tas/
        2. Available files already on MASS
            >> moose:/adhoc/projects/cdds/testdata/transfer_functional/use_case_multiple_embargoed/development/
                CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Amon/tas/gn/available/v20190615/

    OUTPUT
        Critical errors for this variable in log file
    """

    @mock.patch('cdds.common.get_log_datestamp', return_value=DEFAULT_LOG_DATESTAMP)
    def test_transfer_functional_usecase6_multiple_embargoed(self, mock_log_datestamp):
        self.test_dir, variable_file = setup_basic_test_data('piControl_10096_proc', 'piControl_10096_data')
        test_data = TestData(
            number_variables=1,
            proc_dir_name='piControl_10096_proc',
            test_dir_root=self.test_dir,
            data_dir_name='piControl_10096_data',
            request_filename='cdds_request_piControl_10096.cfg',
            mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
            mass_suffix='use_case_multiple_embargoed',
            log_name='test_transfer_functional_usecase6_multiple_embargoed',
            variables_file=variable_file
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
