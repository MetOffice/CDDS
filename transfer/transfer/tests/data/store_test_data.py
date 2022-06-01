# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os
import tempfile
import shutil

from enum import Enum
from dataclasses import dataclass


@dataclass
class TestData:
    number_variables: int = 0
    data_version: str = 'v20191128'
    test_temp_dir: str = ''
    test_dir_root: str = ''
    proc_dir_name: str = ''
    data_dir_name: str = ''
    request_filename: str = ''
    mass_root: str = ''
    mass_suffix: str = ''
    log_name: str = ''
    stream: str = ''

    @property
    def root_proc_dir(self):
        if not self.test_temp_dir:
            self.test_temp_dir = tempfile.mkdtemp()
            shutil.copytree(os.path.join(self.test_dir_root, self.proc_dir_name),
                            os.path.join(self.test_temp_dir, self.proc_dir_name))
        return os.path.join(self.test_temp_dir, self.proc_dir_name)

    @property
    def root_data_dir(self):
        return os.path.join(self.test_dir_root, self.data_dir_name)

    @property
    def request_json_path(self):
        return os.path.join(self.test_dir_root, self.request_filename)


class UseCase(Enum):

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, data):
        self.data = data

    FIRST_ARCHIVE = TestData(
        number_variables=8,
        proc_dir_name='piControl_10096_proc',
        test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
        data_dir_name='piControl_10096_data',
        request_filename='cdds_request_piControl_10096.json',
        mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
        mass_suffix='use_case_first',
        log_name='test_transfer_functional_usecase1_first_archive'
    ),
    FIRST_ARCHIVE_SINGLE_STREAM = TestData(
        number_variables=4,
        proc_dir_name='piControl_10096_proc',
        test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
        data_dir_name='piControl_10096_data',
        request_filename='cdds_request_piControl_10096.json',
        mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
        mass_suffix='use_case_first',
        log_name='test_transfer_functional_usecase1_first_archive_single_stream',
        stream='ap5'
    ),
    APPEND_OR_RECOVER = TestData(
        number_variables=8,
        proc_dir_name='piControl_10096_proc',
        test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
        data_dir_name='piControl_10096_data',
        request_filename='cdds_request_piControl_10096.json',
        mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
        mass_suffix='use_case_continuing',
        log_name='test_transfer_functional_usecase2_append_or_recover'
    ),
    EXTEND_SUBMITTED = TestData(
        number_variables=8,
        proc_dir_name='piControl_10096_proc',
        test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case3_appending',
        data_dir_name='piControl_10096_data',
        request_filename='cdds_request_piControl_10096.json',
        mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
        mass_suffix='use_case_appending',
        log_name='test_transfer_functional_usecase3_extend_submitted'
    ),
    REPLACE_WITHDRAWN = TestData(
        proc_dir_name='piControl_10096_proc',
        test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
        data_dir_name='piControl_10096_data',
        request_filename='cdds_request_piControl_10096.json',
        mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
        mass_suffix='use_case_previously_withdrawn',
        log_name='test_transfer_functional_usecase4_replace_withdrawn'
    ),
    ALREADY_SUBMITTED = TestData(
        proc_dir_name='piControl_10096_proc',
        test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
        data_dir_name='piControl_10096_data',
        request_filename='cdds_request_piControl_10096.json',
        mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
        mass_suffix='use_case_previously_published',
        log_name='test_transfer_functional_usecase5_already_submitted'
    ),
    MULTIPLE_EMBARGOED = TestData(
        proc_dir_name='piControl_10096_proc',
        test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
        data_dir_name='piControl_10096_data',
        request_filename='cdds_request_piControl_10096.json',
        mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
        mass_suffix='use_case_multiple_embargoed',
        log_name='test_transfer_functional_usecase6_multiple_embargoed'
    ),
    ALTERING_PUBLISHED_DATESTAMP = TestData(
        proc_dir_name='piControl_10096_proc',
        test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case_various',
        data_dir_name='piControl_10096_data',
        request_filename='cdds_request_piControl_10096.json',
        mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
        mass_suffix='use_case_used_timestamp',
        log_name='test_transfer_functional_usecase7_altering_published_datestamp'
    ),
    DATESTAMP_REUSE = TestData(
        proc_dir_name='piControl_10096_proc',
        test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case8',
        data_dir_name='piControl_10096_data',
        request_filename='cdds_request_piControl_10096.json',
        mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
        mass_suffix='use_case_8',
        log_name='test_transfer_functional_usecase8_datestamp_reuse'
    ),
    PREPENDING = TestData(
        proc_dir_name='piControl_10096_proc',
        test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case9',
        data_dir_name='piControl_10096_data',
        request_filename='cdds_request_piControl_10096.json',
        mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
        mass_suffix='use_case_9',
        log_name='test_transfer_functional_usecase9_prepending'
    ),
    PREPENDING_TO_EMBARGOED = TestData(
        data_version='v20191120',
        proc_dir_name='piControl_10096_proc',
        test_dir_root='/project/cdds/testdata/functional_tests/transfer/use_case10',
        data_dir_name='piControl_10096_data',
        request_filename='cdds_request_piControl_10096.json',
        mass_root='moose:/adhoc/projects/cdds/testdata/transfer_functional',
        mass_suffix='use_case_10',
        log_name='test_transfer_functional_usecase10_prepending'
    )
