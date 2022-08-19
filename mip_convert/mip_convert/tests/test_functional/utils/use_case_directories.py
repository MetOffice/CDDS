# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

PROJECT_CDDS_DIR = '/project/cdds'
ROOT_TEST_DATA_DIR = os.path.join(PROJECT_CDDS_DIR, 'testdata', 'diagnostics')
ROOT_TEST_CASES_DIR = os.path.join(ROOT_TEST_DATA_DIR, 'test_cases_python3')

TEST_DIR_NAME_TEMPLATE = 'test_{project}_{mip_table}_{variable}'

ROOT_ANCIL_DIR = os.path.join(PROJECT_CDDS_DIR, 'etc', 'ancil')

ROOT_MIP_TABLES_DIR = '/home/h03/cdds/etc/mip_tables'
CORDEX_MIP_TABLES_DIR = '{}/CORDEX/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)
ARISE_MIP_TABLE_DIR = '{}/ARISE/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)
CMIP6_MIP_TABLE_DIR = '{}/CMIP6/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)

MODEL_OUTPUT_DIR_SET1 = os.path.join(ROOT_TEST_DATA_DIR, 'input', 'set1')
MODEL_OUTPUT_DIR_SET2 = os.path.join(ROOT_TEST_DATA_DIR, 'input', 'set2')


def get_output_dir(test_location: str):
    return os.path.join(test_location, 'data_out_{}'.format(os.environ['USER']))


def cmor_log(log_dir: str):
    return os.path.join(log_dir, 'cmor.log')
