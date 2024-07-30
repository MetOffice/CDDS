# (C) British Crown Copyright 2022-2023, Met Office.
# Please see LICENSE.rst for license details.
import os

OUTPUT_CDDS_DIR = os.environ['SCRATCH']
CDDS_ETC = os.environ['CDDS_ETC']
ROOT_REFERENCE_DATA_DIR = os.path.join(CDDS_ETC 'testdata', 'diagnostics')  # this should be symlinked to /project/cdds_data on-prem
ROOT_REFERENCE_CASES_DIR = os.path.join(CDDS_ETC, 'testdata', 'functional_tests', 'mip_convert')
ROOT_OUTPUT_DATA_DIR = os.path.join(OUTPUT_CDDS_DIR, 'testdata', 'diagnostics')
ROOT_OUTPUT_CASES_DIR = os.path.join(ROOT_OUTPUT_DATA_DIR, 'testdata', 'functional_tests', 'mip_convert')

TEST_DIR_NAME_TEMPLATE = 'test_{project}_{mip_table}_{variable}'

ROOT_ANCIL_DIR = os.path.join(CDDS_ETC, 'ancil')

ROOT_MIP_TABLES_DIR = os.path.join(CDDS_ETC, 'mip_tables')
CORDEX_MIP_TABLE_DIR = '{}/CORDEX/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)
ARISE_MIP_TABLE_DIR = '{}/ARISE/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)
CMIP6_MIP_TABLE_DIR = '{}/CMIP6/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)
SEASONAL_MIP_TABLE_DIR = '{}/SEASONAL/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)
NAHOSMIP_MIP_TABLE_DIR = '{}/GCModelDev/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)

MODEL_OUTPUT_DIR = os.path.join(ROOT_REFERENCE_DATA_DIR, 'input')

REFERENCE_OUTPUT_DIR_NAME = 'reference_output'
DATA_OUTPUT_DIR_NAME = 'data_out_{}'.format(os.environ['USER'])


def get_output_dir(test_location: str):
    return os.path.join(test_location, DATA_OUTPUT_DIR_NAME)


def get_cmor_log(log_dir: str):
    return os.path.join(log_dir, 'cmor.log')
