# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

PROJECT_CDDS_DIR = '/project/cdds'
ROOT_TEST_DATA_DIR = os.path.join(PROJECT_CDDS_DIR, 'testdata', 'diagnostics')
ROOT_TEST_CASES_DIR = os.path.join(ROOT_TEST_DATA_DIR, 'test_cases_python3')

TEST_DIR_NAME_TEMPLATE = 'test_{project}_{mip_table}_{variable}'

ROOT_ANCIL_DIR = os.path.join(PROJECT_CDDS_DIR, 'etc', 'ancil')

ROOT_MIP_TABLES_DIR = os.path.join(os.environ['CDDS_ETC'], 'mip_tables')
CORDEX_MIP_TABLE_DIR = '{}/CORDEX/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)
ARISE_MIP_TABLE_DIR = '{}/ARISE/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)
CMIP6_MIP_TABLE_DIR = '{}/CMIP6/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)
SEASONAL_MIP_TABLE_DIR = '{}/SEASONAL/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)

MODEL_OUTPUT_DIR_SET1 = os.path.join(ROOT_TEST_DATA_DIR, 'input', 'set1')
MODEL_OUTPUT_DIR_SET2 = os.path.join(ROOT_TEST_DATA_DIR, 'input', 'set2')
MODEL_OUTPUT_DIR_SET3 = os.path.join(ROOT_TEST_DATA_DIR, 'input', 'set3')

REFERENCE_OUTPUT_DIR_NAME = 'reference_output'
DATA_OUTPUT_DIR_NAME = 'data_out_{}'.format(os.environ['USER'])


def get_output_dir(test_location: str):
    return os.path.join(test_location, DATA_OUTPUT_DIR_NAME)


def get_cmor_log(log_dir: str):
    return os.path.join(log_dir, 'cmor.log')
