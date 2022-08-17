# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

ROOT_TEST_DIR = '/project/cdds'
ROOT_TEST_LOCATION = os.path.join(ROOT_TEST_DIR, 'testdata', 'diagnostics')

ROOT_ANCIL_DIR_NEW = os.path.join(ROOT_TEST_DIR, 'etc', 'ancil')
ROOT_ANCIL_DIR = os.path.join(ROOT_TEST_DIR, 'etc', 'um_ancil')

ROOT_MIP_TABLES_DIR = '/home/h03/cdds/etc/mip_tables'
CORDEX_MIP_TABLES_DIR = '{}/CORDEX/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)
ARISE_MIP_TABLE_DIR = '{}/ARISE/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)
CMIP6_MIP_TABLE_DIR = '{}/CMIP6/for_functional_tests'.format(ROOT_MIP_TABLES_DIR)


ARISE_LICENSE = ('ARISE data produced by MOHC is licensed under the Open Government License v3 '
                 '(https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)')

CMIP6_LICENSE = ('CMIP6 model data produced by MOHC is licensed '
                 'under a Creative Commons Attribution ShareAlike '
                 '4.0 International License '
                 '(https://creativecommons.org/licenses). Consult '
                 'https://pcmdi.llnl.gov/CMIP6/TermsOfUse for '
                 'terms of use governing CMIP6 output, including '
                 'citation requirements and proper acknowledgment. '
                 'Further information about this data, including '
                 'some limitations, can be found via the '
                 'further_info_url (recorded as a global attribute '
                 'in this file) . The data producers and data '
                 'providers make no warranty, either express or '
                 'implied, including, but not limited to, '
                 'warranties of merchantability and fitness for a '
                 'particular purpose. All liabilities arising from '
                 'the supply of the information (including any '
                 'liability arising in negligence) are excluded to '
                 'the fullest extent permitted by law.')

CORDEX_LICENSE = ('CORDEX model data produced by the Met Office Hadley Centre is licensed under a '
                  'Creative Commons Attribution-ShareAlike 4.0 International License '
                  '(https://creativecommons.org/licenses). Consult '
                  'https://pcmdi.llnl.gov/CORDEX/TermsOfUse '
                  'for terms of use governing CORDEX output, including citation requirements and proper '
                  'acknowledgment. Further information about this data, including some limitations, can '
                  'be found via the further_info_url (recorded as a global attribute in this file) and '
                  'at https://ukesm.ac.uk/cmip6. The data producers and data providers make no warranty, '
                  'either express or implied, including, but not limited to, warranties of '
                  'merchantability and fitness for a particular purpose. All liabilities arising from '
                  'the supply of the information (including any liability arising in negligence) are '
                  'excluded to the fullest extent permitted by law.'),

MODEL_OUTPUT_DIR = os.path.join(ROOT_TEST_LOCATION, 'input', 'set1')
MODEL_OUTPUT_DIR_SET1 = os.path.join(ROOT_TEST_LOCATION, 'input', 'set1')
MODEL_OUTPUT_DIR_SET2 = os.path.join(ROOT_TEST_LOCATION, 'input', 'set2')

TEST_CASES_DIR = os.path.join(ROOT_TEST_LOCATION, 'test_cases_python3')

DEBUG = True
NCCMP_TIMINGS = []

COMPARE_NETCDF = (
    'nccmp -dmgfbi {tolerance} {history} {options} --globalex=cmor_version,creation_date,cv_version,'
    'data_specs_version,table_info,tracking_id,_NCProperties {output} {reference}'
)
