# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Information required to automatically generate the
|user configuration files| for the functional tests.

The structure of the tests must be as follows:

<root_test_dir>/
    testdata/
        diagnostics/
            input/
                set1/
                set2/
                set3/
            test_cases/
                <test_dir>/
                    data_out/
                    reference_output/

The |MIP tables| must be located in a
``/<root_mip_tables_dir>/etc/mip_tables/<project>/`` directory.
"""
import os

ROOT_TEST_DIR = '/project/cdds'
ROOT_HELIX_MIP_TABLES_DIR = ROOT_TEST_DIR
ROOT_CMIP5_MIP_TABLES_DIR = ROOT_TEST_DIR
ROOT_CMIP6_MIP_TABLES_DIR = '/home/h03/cdds'


def common_info():
    """
    Return the common information required for the functional tests.
    """
    return {
        'COMMON': {
            'root_test_dir': ROOT_TEST_DIR,
            'root_test_location': '${COMMON:root_test_dir}/testdata/diagnostics',
            'root_ancil_dir': '${COMMON:root_test_dir}/etc/um_ancil'
        },
        'cmor_setup': {
            'cmor_log_file': '${COMMON:test_location}/cmor.log',
            'create_subdirectories': '0',
        },
        'cmor_dataset': {
            'calendar': '360_day',
            'grid': 'not checked',
            'grid_label': 'gn',
            'institution_id': 'MOHC',
            'output_dir': '${{COMMON:test_location}}/data_out_{}'.format(os.environ['USER']),
        },
    }


def project_info():
    """
    Return the project-specific information required for the functional
    tests.
    """
    return {
        # 'CMIP5': {
        #     'cmor_setup': {
        #         'mip_table_dir': ('{}/etc/mip_tables/CMIP5/for_functional_tests'.format(ROOT_CMIP5_MIP_TABLES_DIR)),
        #         'netcdf_file_action': 'CMOR_REPLACE_3',
        #     },
        #     'cmor_dataset': {
        #         'branch_date_in_parent': '2006-12-01-00-00-00',
        #         'branch_method': 'standard',
        #         'contact': 'chris.d.jones@metoffice.gov.uk',
        #         'experiment_id': 'rcp45',
        #         'grid_resolution': '5 km',
        #         'license': 'not checked',
        #         'mip': 'CMIP5',
        #         'mip_era': 'CMIP5',
        #         'model_id': 'HadGEM2-ES',
        #         'model_type': 'AOGCM',
        #         'output_file_template': '<variable_id><table><source_id><experiment_id><variant_label>',
        #         'parent_base_date': '2005-12-01-00-00-00',
        #         'parent_experiment_id': 'historical',
        #         'parent_variant_label': 'r1i1p1',
        #         'sub_experiment_id': 'none',
        #         'variant_label': 'r1i1p1f1',
        #     },
        #     'request': {
        #         'child_base_date': '2000-01-01-00-00-00',
        #     },
        # },
        # 'HELIX': {
        #     'cmor_setup': {
        #         'mip_table_dir': ('{}/etc/mip_tables/HELIX/for_functional_tests'.format(ROOT_HELIX_MIP_TABLES_DIR)),
        #         'netcdf_file_action': 'CMOR_REPLACE_3',
        #     },
        #     'cmor_dataset': {
        #         'branch_method': 'no parent',
        #         'contact': 'john.caesar@metoffice.gov.uk',
        #         'experiment_id': 'swl2',
        #         'grid_resolution': '5 km',
        #         'license': 'not checked',
        #         'mip': 'HELIX',
        #         'mip_era': 'HELIX',
        #         'model_id': 'HadGEM3',
        #         'model_type': 'AOGCM',
        #         'output_file_template': '<variable_id><table><source_id><experiment_id><variant_label>',
        #         'sub_experiment_id': 'none',
        #         'variant_label': 'r1i1p1f1',
        #     },
        #     'request': {
        #         'child_base_date': '1978-09-01-00-00-00',
        #     },
        # },
        'ARISE': {
            'cmor_setup': {
                'mip_table_dir': ('{}/etc/mip_tables/ARISE/for_functional_tests'.format(ROOT_CMIP6_MIP_TABLES_DIR)),
                'netcdf_file_action': 'CMOR_REPLACE_4',
            },
            'cmor_dataset': {
                'branch_method': 'standard',
                'branch_date_in_child': '1850-01-01-00-00-00',
                'branch_date_in_parent': '2250-01-01-00-00-00',
                'experiment_id': 'arise-sai-1p5',
                'license': (
                    'ARISE data produced by MOHC is licensed under the Open Government License v3 '
                    '(https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)'
                ),
                'mip': 'ARISE',
                'mip_era': 'ARISE',
                'model_id': 'UKESM1-0-LL',
                'model_type': 'AOGCM',
                'nominal_resolution': '250 km',
                'sub_experiment_id': 'none',
                'variant_label': 'r1i1p1f2',
                'parent_base_date': '1850-01-01-00-00-00',
                'parent_experiment_id': 'ssp245',
                'parent_mip_era': 'CMIP6',
                'parent_model_id': 'UKESM1-0-LL',
                'parent_time_units': 'days since 1850-01-01',
                'parent_variant_label': 'r1i1p1f2',
            },
            'request': {
                'child_base_date': '2000-01-01-00-00-00',
            },
            'global_attributes': {
                'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.UKESM1-0-LL.historical.none.r1i1p1f2'
            },
        },
        'CMIP6': {
            'cmor_setup': {
                'mip_table_dir': ('{}/etc/mip_tables/CMIP6/for_functional_tests'.format(ROOT_CMIP6_MIP_TABLES_DIR)),
                'netcdf_file_action': 'CMOR_REPLACE_4',
            },
            'cmor_dataset': {
                'branch_method': 'no parent',
                'experiment_id': 'amip',
                'license': ('CMIP6 model data produced by MOHC is licensed '
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
                            'the fullest extent permitted by law.'),
                'mip': 'CMIP',
                'mip_era': 'CMIP6',
                'model_id': 'UKESM1-0-LL',
                'model_type': 'AGCM',
                'nominal_resolution': '5 km',
                'sub_experiment_id': 'none',
                'variant_label': 'r1i1p1f1',
            },
            'request': {
                'child_base_date': '2000-01-01-00-00-00',
            },
            'global_attributes': {
                'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.UKESM1-0-LL.amip.none.r1i1p1f1'
            },
        },
        'CORDEX': {
            'cmor_setup': {
                'mip_table_dir': ('{}/etc/mip_tables/CORDEX/for_functional_tests'
                                  ''.format(ROOT_CMIP6_MIP_TABLES_DIR)),
                'netcdf_file_action': 'CMOR_REPLACE_4',
            },
            'cmor_dataset': {
                'branch_method': 'no parent',
                'experiment_id': 'cordex1',
                'grid': 'Model grid',
                'grid_label': 'gn',
                'institution_id': 'MOHC',
                'license': ('CORDEX model data produced by the Met Office Hadley Centre is licensed under a '
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
                'mip_era': 'CORDEX',
                'mip': 'CMIP',
                'model_id': 'HadREM3-GA7-05',
                'model_type': 'ARCM',
                'nominal_resolution': '10 km',
                'output_file_template': ('<variable_id><CORDEX_domain><driving_model_id><experiment_id>'
                                         '<driving_model_ensemble_member><source_id><rcm_version_id><frequency>'),
                'sub_experiment_id': 'none',
                'variant_label': 'r1i1p1f1',
            },
            'request': {
                'child_base_date': '2000-01-01-00-00-00',
            },
            'global_attributes': {
                'driving_experiment': 'historical',
                'driving_model_id': 'MOHC-HadGEM2-ES',
                'driving_model_ensemble_member': 'r1i1p1',
                'driving_experiment_name': 'historical',
                'nesting_levels': 1,
                'rcm_version_id': 'v1',
                'project_id': 'CORDEX-FPSCONV',
                'CORDEX_domain': 'EUR-11',
            }
        },
    }


def specific_info():
    """
    Return the test-specific information required for the functional
    tests.
    """
    return {
        # ('CMIP5', 'Amon', 'sbl'): {  # (lat, lon, time)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_Amon_sbl',
        #     },
        #     'request': {
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_apm': {
        #         'CMIP5_Amon': 'sbl',
        #     },
        #     'other': {
        #         'filenames': ['sbl_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', 'Amon', 'ta'): {  # heaviside (lat, lon, time, plevs)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_Amon_ta',
        #     },
        #     'cmor_dataset': {
        #         'contact': 'chris.d.jones@metoffice.gov.uk, mark.webb@metoffice.gov.uk',
        #         'experiment_id': 'amip',
        #         'references': ('Bellouin N. et al, (2007) Improved '
        #                        'representation of aerosols for HadGEM2. '
        #                        'Meteorological Office Hadley Centre, '
        #                        'Technical Note 73, March 2007; Collins W.J.  '
        #                        'et al, (2008) Evaluation of the HadGEM2 '
        #                        'model. Meteorological Office Hadley Centre, '
        #                        'Technical Note 74,; Johns T.C. et al, (2006) '
        #                        'The new Hadley Centre climate model HadGEM1: '
        #                        'Evaluation of coupled simulations. Journal of '
        #                        'Climate, American Meteorological Society, '
        #                        'Vol. 19, No. 7, pages 1327-1353.; Martin G.M. '
        #                        'et al, (2006) The physical properties of the '
        #                        'atmosphere in the new Hadley Centre Global '
        #                        'Environmental Model, HadGEM1 - Part 1: Model '
        #                        'description and global climatology. Journal '
        #                        'of Climate, American Meteorological Society, '
        #                        'Vol. 19, No.7, pages 1274-1301.; Ringer M.A. '
        #                        'et al, (2006) The physical properties of the '
        #                        'atmosphere in the new Hadley Centre Global '
        #                        'Environmental Model, HadGEM1 - Part 2: '
        #                        'Aspects of variability and regional climate. '
        #                        'Journal of Climate, American Meteorological '
        #                        'Society, Vol. 19, No. 7, pages 1302-1326.'),
        #         'model_id': 'HadGEM2-A',
        #         'parent_experiment_id': 'N/A',
        #     },
        #     'request': {
        #         'child_base_date': '1978-09-01-00-00-00',
        #         'model_output_dir': '${COMMON:root_test_location}/input/set2',
        #         'run_bounds': '2021-09-01-00-00-00 2021-10-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_apm': {
        #         'CMIP5_Amon': 'ta',
        #     },
        #     'other': {
        #         'filenames': ['ta_Amon_HadGEM2-A_amip_r1i1p1f1_202109-202109.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', 'Amon', 'tas_rotated_pole'): {  # (lat, lon, time, height2m)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_Amon_tas_rotated_pole',
        #     },
        #     'cmor_dataset': {
        #         'calendar': 'gregorian',
        #         'experiment_id': 'rcp85',
        #         'parent_experiment_id': 'N/A',
        #     },
        #     'request': {
        #         'child_base_date': '1859-12-01-00-00-00',
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '1989-01-01-00-00-00 1989-02-01-00-00-00',
        #         'suite_id': 'aklfg',
        #     },
        #     'stream_apm': {
        #         'CMIP5_Amon': 'tas',
        #     },
        #     'other': {
        #         'filenames': ['tas_Amon_HadGEM2-ES_rcp85_r1i1p1f1_198901-198901.nc'],
        #         'ignore_history': True,
        #         'tolerance_value': '8e-6',
        #     },
        # },
        # ('CMIP5', 'Amon', 'va'): {  # heaviside (lat, lon, time, plevs)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_Amon_va',
        #     },
        #     'request': {
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_apm': {
        #         'CMIP5_Amon': 'va',
        #     },
        #     'other': {
        #         'filenames': ['va_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', 'Amon', 'multiple_3d'): {  # (lat, lon, time)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_Amon_multiple_3d',
        #     },
        #     'request': {
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_apm': {
        #         'CMIP5_Amon': ('clt evspsbl hfls hfss pr prc prsn prw ps psl '
        #                        'rlds rldscs rlus rlut rlutcs rsds rsdscs rsdt '
        #                        'rsus rsuscs rsut rsutcs sbl sci tauu tauv ts'),
        #     },
        #     'other': {
        #         'filenames': [
        #             'clt_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'evspsbl_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'hfls_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'hfss_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'pr_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'prc_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'prsn_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'prw_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'ps_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'psl_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'rlds_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'rldscs_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'rlus_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'rlut_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'rlutcs_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'rsds_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'rsdscs_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'rsdt_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'rsus_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'rsuscs_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'rsut_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'rsutcs_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'sbl_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'sci_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'tauu_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'tauv_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'ts_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', 'Amon', 'multiple_4d'): {  # (lat, lon, time, height2m/10m)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_Amon_multiple_4d',
        #     },
        #     'request': {
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_apm': {
        #         'CMIP5_Amon': 'hurs huss sfcWind tas uas vas',
        #     },
        #     'other': {
        #         'filenames': [
        #             'hurs_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'huss_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'sfcWind_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'tas_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'uas_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'vas_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', 'Amon', 'multiple_hybrid_height'): {
        #     # (lat, lon, time, hybrid_height)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_Amon_multiple_hybrid_height',
        #     },
        #     'request': {
        #         'ancil_files': '${COMMON:root_ancil_dir}/HadGEM2-ES/hadgem2_es_orog.pp',
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_apm': {
        #         'CMIP5_Amon': 'cl cli clw',
        #     },
        #     'other': {
        #         'filenames': [
        #             'cl_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'cli_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'clw_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', 'Amon', 'multiple_pressure_level'): {
        #     # (lat, lon, time, plevs)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_Amon_multiple_pressure_level',
        #     },
        #     'request': {
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_apm': {
        #         'CMIP5_Amon': 'hur hus ta ua va wap zg',
        #     },
        #     'other': {
        #         'filenames': [
        #             'hur_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'hus_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'ta_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'ua_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'va_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'wap_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc',
        #             'zg_Amon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', 'Lmon', 'baresoilFrac'): {  # (lat, lon, time, pseudo_level)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_Lmon_baresoilFrac',
        #     },
        #     'request': {
        #         'ancil_files': '${COMMON:root_ancil_dir}/HadGEM2-ES/updated_mask_frac.pp',
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_apm': {
        #         'CMIP5_Lmon': 'baresoilFrac',
        #     },
        #     'other': {
        #         'filenames': ['baresoilFrac_Lmon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', 'Lmon', 'mrlsl'): {  # (lat, lon, time, sdepth)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_Lmon_mrlsl',
        #     },
        #     'request': {
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_apm': {
        #         'CMIP5_Lmon': 'mrlsl',
        #     },
        #     'other': {
        #         'filenames': ['mrlsl_Lmon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', 'Lmon', 'mrsos'): {  # (lat, lon, time, sdepth1)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_Lmon_mrsos',
        #     },
        #     'request': {
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_apm': {
        #         'CMIP5_Lmon': 'mrsos',
        #     },
        #     'other': {
        #         'filenames': ['mrsos_Lmon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', 'Lmon', 'tsl'): {  # (lat, lon, time, sdepth)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_Lmon_tsl',
        #     },
        #     'request': {
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_apm': {
        #         'CMIP5_Lmon': 'tsl',
        #     },
        #     'other': {
        #         'filenames': ['tsl_Lmon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', 'day', 'tasmin'): {  # (lat, lon, time, height2m)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_day_tasmin',
        #     },
        #     'request': {
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_apa': {
        #         'CMIP5_day': 'tasmin',
        #     },
        #     'other': {
        #         'filenames': ['tasmin_day_HadGEM2-ES_rcp45_r1i1p1f1_20210101-20210130.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', '6hrLev', 'ua'): {  # (lat, lon, time, hybrid_height)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_6hrLev_ua',
        #     },
        #     'request': {
        #         'ancil_files': '${COMMON:root_ancil_dir}/HadGEM2-ES/hadgem2_es_orog.pp',
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2021-01-01-00-00-00 2021-01-11-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_apg': {
        #         'CMIP5_6hrLev': 'ua',
        #     },
        #     'other': {
        #         'filenames': ['ua_6hrLev_HadGEM2-ES_rcp45_r1i1p1f1_202101010600-202101110000.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', '6hrPlev', 'ua'): {  # (lat, lon, time, plev3)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_6hrPlev_ua',
        #     },
        #     'request': {
        #         'model_output_dir': '${COMMON:root_test_location}/input/set2',
        #         'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_apg': {
        #         'CMIP5_6hrPlev': 'ua',
        #     },
        #     'other': {
        #         'filenames': ['ua_6hrPlev_HadGEM2-ES_rcp45_r1i1p1f1_202101010600-202102010000.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', '3hr', 'clt'): {  # (lat, lon, time)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_3hr_clt',
        #     },
        #     'request': {
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_api': {
        #         'CMIP5_3hr': 'clt',
        #     },
        #     'other': {
        #         'filenames': ['clt_3hr_HadGEM2-ES_rcp45_r1i1p1f1_202101010130-202101302230.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('CMIP5', '3hr', 'tas'): {  # (lat, lon, time, height2m)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_CMIP5_3hr_tas',
        #     },
        #     'request': {
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
        #         'suite_id': 'ajnjg',
        #     },
        #     'stream_api': {
        #         'CMIP5_3hr': 'tas',
        #     },
        #     'other': {
        #         'filenames': ['tas_3hr_HadGEM2-ES_rcp45_r1i1p1f1_202101010300-202102010000.nc'],
        #         'ignore_history': True,
        #     },
        # },
        # ('HELIX', 'day', 'ua850'): {  # (lat, lon, time, p850)
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases/test_HELIX_day_ua850',
        #     },
        #     'request': {
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2010-06-01-00-00-00 2010-07-01-00-00-00',
        #         'suite_id': 'ak991',
        #     },
        #     'stream_apa': {
        #         'HELIX_day': 'ua850',
        #     },
        #     'other': {
        #         'filenames': ['ua850_day_HadGEM3_swl2_r1i1p1f1_20100601-20100630.nc'],
        #         'ignore_history': True,
        #     },
        # },
        ('CMIP6', 'Amon', 'tasmax'): {  # (lat, lon, time, height2m)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Amon_tasmax',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
                'suite_id': 'ajnjg',
            },
            'stream_apa': {
                'CMIP6_Amon': 'tasmax',
            },
            'other': {
                'filenames': [
                    'tasmax_Amon_UKESM1-0-LL_amip_r1i1p1f1_gn_'
                    '202101-202101.nc'],
                'ignore_history': True,
            },
        },
        ('ARISE', 'Emon', 'hussLut'): {  # (lat, lon, time, height2m)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_ARISE_Emon_hussLut',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1850-01-01-00-00-00 1850-03-01-00-00-00',
                'suite_id': 'u-bc179',
            },
            'stream_ap5': {
                'ARISE_Emon': 'hussLut',
            },
            'other': {
                'devel': True,
                'filenames': [
                    'hussLut_Emon_UKESM1-0-LL_arise-sai-1p5_r1i1p1f2_gn_185001-185002.nc'
                ],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'AERmon', 'reffclwtop'): {  # N216 (lat, lon, time)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_AERmon_reffclwtop',
            },
            'cmor_setup': {
                'netcdf_file_action': 'CMOR_REPLACE_3',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1851-05-01-00-00-00 1851-06-01-00-00-00',
                'suite_id': 'u-aq112',
            },
            'stream_ap4': {
                'CMIP6_AERmon': 'reffclwtop',
            },
            'other': {
                'filenames': [
                    'reffclwtop_AERmon_UKESM1-0-LL_amip_r1i1p1f1_gn_'
                    '185105-185105.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'AERmon', 'rlutaf'): {  # (lat, lon, time)
            # Check multiply_cubes with optional orography.
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_AERmon_rlutaf',
            },
            'request': {
                'ancil_files': '${COMMON:root_ancil_dir}/UKESM1-0/UKESM1-0-LL/qrparm.orog.pp',
                'model_output_dir': '${COMMON:root_test_location}/input/set2',
                'run_bounds': '2345-06-01-00-00-00 2345-07-01-00-00-00',
                'suite_id': 'u-aw310',
            },
            'stream_ap4': {
                'CMIP6_AERmon': 'rlutaf',
            },
            'other': {
                'filenames': [
                    'rlutaf_AERmon_UKESM1-0-LL_amip_r1i1p1f1_gn_'
                    '234506-234506.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'AERmon', 'phalf'): {  # (lat, lon, hybrid_height_half, time)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_AERmon_phalf',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '2345-06-01-00-00-00 2345-07-01-00-00-00',
                'suite_id': 'u-aw310',
            },
            'stream_ap4': {
                'CMIP6_AERmon': 'phalf',
            },
            'other': {
                'filenames': ['phalf_AERmon_UKESM1-0-LL_amip_r1i1p1f1_gn_234506-234506.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'CFday', 'ta700'): {  # (lat, lon, time, p700)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_CFday_ta700',
            },
            'cmor_setup': {
                'netcdf_file_action': 'CMOR_REPLACE_3',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1855-05-11-00-00-00 1855-05-21-00-00-00',
                'suite_id': 'u-ar050',
            },
            'stream_ap6': {
                'CMIP6_CFday': 'ta700',
            },
            'other': {
                'filenames': ['ta700_CFday_UKESM1-0-LL_amip_r1i1p1f1_gn_18550511-18550520.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'CFmon', 'clmcalipso'): {  # (lat, lon, time, p560)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_CFmon_clmcalipso',
            },
            'cmor_setup': {
                'netcdf_file_action': 'CMOR_REPLACE_3',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1979-04-01-00-00-00 1979-05-01-00-00-00',
                'suite_id': 'u-an644',
            },
            'stream_ap5': {
                'CMIP6_CFmon': 'clmcalipso',
            },
            'other': {
                'filenames': ['clmcalipso_CFmon_UKESM1-0-LL_amip_r1i1p1f1_gn_197904-197904.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'CFmon', 'cls'): {  # (lat, lon, time, hybrid_height)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_CFmon_cls',
            },
            'cmor_setup': {
                'netcdf_file_action': 'CMOR_REPLACE_3',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1979-04-01-00-00-00 1979-05-01-00-00-00',
                'suite_id': 'u-an644',
            },
            'stream_ap5': {
                'CMIP6_CFmon': 'cls',
            },
            'other': {
                'filenames': ['cls_CFmon_UKESM1-0-LL_amip_r1i1p1f1_gn_197904-197904.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'CFmon', 'clisccp'): {  # (lat, lon, plev7c, tau, time)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_CFmon_clisccp',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1902-04-01-00-00-00 1902-05-01-00-00-00',
                'suite_id': 'u-ar766',
            },
            'stream_ap5': {
                'CMIP6_CFmon': 'clisccp',
            },
            'other': {
                'filenames': ['clisccp_CFmon_UKESM1-0-LL_amip_r1i1p1f1_gn_190204-190204.nc'],
                'ignore_history': True,
            },
        },

        ('CMIP6', 'CFmon', 'tnhus'): {  # (lat, lon, time, hybrid_height)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_CFmon_tnhus',
            },
            'request': {
                'atmos_timestep': '600',
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1902-04-01-00-00-00 1902-05-01-00-00-00',
                'suite_id': 'u-ar050',
            },
            'stream_apu': {
                'CMIP6_CFmon': 'tnhus',
            },
            'other': {
                'filenames': ['tnhus_CFmon_UKESM1-0-LL_amip_r1i1p1f1_gn_190204-190204.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'day', 'zg_deflation'): {  # (pressure, lat)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_day_zg_deflation',
            },
            'cmor_dataset': {
                'branch_date_in_child': 'N/A',
                'branch_date_in_parent': 'N/A',
                'branch_method': 'standard',
                'contact': 'enquiries@metoffice.gov.uk',
                'experiment_id': 'highres-future',
                'grid': 'N96',
                'mip': 'HighResMIP',
                'model_id': 'HadGEM3-GC31-LL',
                'model_type': 'AOGCM',
                'nominal_resolution': '100 km',
                'parent_base_date': '1950-01-01-00-00-00',
                'parent_experiment_id': 'hist-1950',
                'parent_mip_era': 'CMIP6',
                'parent_model_id': 'HadGEM3-GC31-LL',
                'parent_time_units': 'days since 1950-01-01',
                'parent_variant_label': 'r1i1p1f1',
                'references': 'http://dx.doi.org/10.5194%2Fgmd-4-919-2011',
            },
            'request': {
                'child_base_date': '1950-01-01-00-00-00',
                'deflate_level': 3,
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1950-01-01-00-00-00 1950-02-01-00-00-00',
                'shuffle': True,
                'suite_id': 'ai674',
            },
            'global_attributes': {
                'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.HadGEM3-GC31-LL.'
                                    'highres-future.none.r1i1p1f1'
            },
            'stream_ap6': {
                'CMIP6_day': 'zg',
            },
            'other': {
                'filenames': ['zg_day_HadGEM3-GC31-LL_highres-future_r1i1p1f1_gn_19500101-19500130.nc'],
                'ignore_history': True,
                'other_options': '-e',
            },
        },
        ('CMIP6', 'Emon', 'cfadDbze94'): {  # (lat, lon, time, alt40, dbze)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Emon_cfadDbze94',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1983-05-01-00-00-00 1983-06-01-00-00-00',
                'suite_id': 'u-au456',

            },
            'stream_ap5': {
                'CMIP6_Emon': 'cfadDbze94',
            },
            'other': {
                'filenames': ['cfadDbze94_Emon_UKESM1-0-LL_amip_r1i1p1f1_gn_198305-198305.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'Emon', 'sconcdust'): {  # (lat, lon, time)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Emon_sconcdust',
            },
            'cmor_setup': {
                'netcdf_file_action': 'CMOR_REPLACE_3',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1979-04-01-00-00-00 1979-05-01-00-00-00',
                'suite_id': 'u-an644',
            },
            'stream_ap5': {
                'CMIP6_Emon': 'sconcdust',
            },
            'other': {
                'filenames': ['sconcdust_Emon_UKESM1-0-LL_amip_r1i1p1f1_gn_197904-197904.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'Emon', 'hus27'): {  # (lat, lon, plev, time)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Emon_hus27',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1960-03-01-00-00-00 1960-04-01-00-00-00',
                'suite_id': 'u-aw310',
            },
            'stream_ap5': {
                'CMIP6_Emon': 'hus27',
            },
            'other': {
                'filenames': ['hus_Emon_UKESM1-0-LL_amip_r1i1p1f1_gn_196003-196003.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'Emon', 'loaddust'): {  # (lat, lon, time)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Emon_loaddust',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1960-02-01-00-00-00 1960-04-01-00-00-00',
                'suite_id': 'u-aw310',
            },
            'stream_ap5': {
                'CMIP6_Emon': 'loaddust',
            },
            'other': {
                'filenames': ['loaddust_Emon_UKESM1-0-LL_amip_r1i1p1f1_gn_196002-196003.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'Eday', 'parasolRefl'): {  # (lat, lon, time, sza5)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Eday_parasolRefl',
            },
            'cmor_setup': {
                'netcdf_file_action': 'CMOR_REPLACE_3',
            },
            'cmor_dataset': {
                'contact': 'chris.d.jones@metoffice.gov.uk',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1979-01-01-00-00-00 1979-02-01-00-00-00',
                'suite_id': 'u-bh859',
            },
            'stream_ap6': {
                'CMIP6_Eday': 'parasolRefl',
            },
            'other': {
                'filenames': ['parasolRefl_Eday_UKESM1-0-LL_amip_r1i1p1f1_gn_19790101-19790130.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'EdayZ', 'zg'): {  # zonal mean (pressure, lat)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_EdayZ_zg',
            },
            'cmor_dataset': {
                'branch_date_in_child': '1970-01-01-00-00-00',
                'branch_date_in_parent': 'N/A',
                'branch_method': 'standard',
                'contact': 'enquiries@metoffice.gov.uk',
                'experiment_id': 'highres-future',
                'grid': 'N96',
                'grid_resolution': '250 km',
                'mip': 'HighResMIP',
                'model_id': 'HadGEM3-GC31-LL',
                'model_type': 'AOGCM',
                'nominal_resolution': '100 km',
                'parent_base_date': '1950-01-01-00-00-00',
                'parent_experiment_id': 'hist-1950',
                'parent_mip_era': 'CMIP6',
                'parent_model_id': 'HadGEM3-GC31-LL',
                'parent_time_units': 'days since 1950-01-01',
                'parent_variant_label': 'r1i1p1f1',
                'references': 'http://dx.doi.org/10.5194%2Fgmd-4-919-2011',
            },
            'request': {
                'child_base_date': '1950-01-01-00-00-00',
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1950-01-01-00-00-00 1950-02-01-00-00-00',
                'suite_id': 'ai674',
            },
            'global_attributes': {
                'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.HadGEM3-GC31-LL.'
                                    'highres-future.none.r1i1p1f1'
            },
            'stream_ap6': {
                'CMIP6_EdayZ': 'zg',
            },
            'other': {
                'filenames': ['zg_EdayZ_HadGEM3-GC31-LL_highres-future_r1i1p1f1_gn_19500101-19500130.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'EdayZ', 'vtem'): {  # zonal mean, fix lbproc (pressure, lat)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_EdayZ_vtem',
            },
            'cmor_dataset': {
                'branch_date_in_child': 'N/A',
                'branch_date_in_parent': 'N/A',
                'branch_method': 'standard',
                'contact': 'enquiries@metoffice.gov.uk',
                'experiment_id': 'highres-future',
                'grid': 'N96',
                'grid_resolution': '250 km',
                'mip': 'HighResMIP',
                'model_id': 'HadGEM3-GC31-LL',
                'model_type': 'AOGCM',
                'nominal_resolution': '100 km',
                'parent_base_date': '1950-01-01-00-00-00',
                'parent_experiment_id': 'hist-1950',
                'parent_mip_era': 'CMIP6',
                'parent_model_id': 'HadGEM3-GC31-LL',
                'parent_time_units': 'days since 1950-01-01',
                'parent_variant_label': 'r1i1p1f1',
                'references': 'http://dx.doi.org/10.5194%2Fgmd-4-919-2011',
            },
            'request': {
                'child_base_date': '1950-01-01-00-00-00',
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1950-01-01-00-00-00 1950-02-01-00-00-00',
                'suite_id': 'ai674',
            },
            'global_attributes': {
                'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.HadGEM3-GC31-LL.'
                                    'highres-future.none.r1i1p1f1'
            },
            'stream_ap6': {
                'CMIP6_EdayZ': 'vtem',
            },
            'other': {
                'filenames': ['vtem_EdayZ_HadGEM3-GC31-LL_highres-future_r1i1p1f1_gn_19500101-19500130.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'Omon', 'soga'): {  # (time)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Omon_soga',
            },
            'cmor_dataset': {
                'contact': 'chris.d.jones@metoffice.gov.uk',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1851-05-01-00-00-00 1851-06-01-00-00-00',
                'suite_id': 'u-aq112',
            },
            'stream_onm': {
                'CMIP6_Omon': 'soga',
            },
            'other': {
                'filenames': ['soga_Omon_UKESM1-0-LL_amip_r1i1p1f1_gn_185105-185105.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'Omon', 'tos'): {  # (lat, lon, time)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Omon_tos',
            },
            'cmor_dataset': {
                'calendar': 'noleap',
                'contact': 'chris.d.jones@metoffice.gov.uk',
                'output_file_template': '<variable_id><table><source_id><experiment_id><variant_label>',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1976-01-01-00-00-00 1976-01-11-00-00-00',
                'suite_id': 'ai022',
            },
            'stream_onb': {
                'CMIP6_Omon': 'tos',
            },
            'other': {
                'filenames': ['tos_Omon_UKESM1-0-LL_amip_r1i1p1f1_197601-197601.nc'],
            },
        },
        ('CMIP6', 'Omon', 'thetao'): {  # (lat, lon, time, depth)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Omon_thetao',
            },
            'cmor_dataset': {
                'calendar': 'noleap',
                'contact': 'chris.d.jones@metoffice.gov.uk',
                'output_file_template': '<variable_id><table><source_id><experiment_id><variant_label>',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1976-01-01-00-00-00 1976-01-11-00-00-00',
                'suite_id': 'ai022',
            },
            'stream_onb': {
                'CMIP6_Omon': 'thetao',
            },
            'other': {
                'filenames': ['thetao_Omon_UKESM1-0-LL_amip_r1i1p1f1_197601-197601.nc'],
            },
        },
        ('CMIP6', 'Omon', 'thkcello'): {  # (lat, lon, time, verticle T level)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Omon_thkcello',
            },
            'cmor_dataset': {
                'contact': 'chris.d.jones@metoffice.gov.uk',
                'output_file_template': '<variable_id><table><source_id><experiment_id><variant_label>',
                'model_id': 'HadGEM3-GC31-LL',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1980-01-01-00-00-00 1980-02-01-00-00-00',
                'suite_id': 'u-ar766',
            },
            'global_attributes': {
                'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.HadGEM3-GC31-LL.amip.none.r1i1p1f1'
            },
            'stream_onm_grid-T': {
                'CMIP6_Omon': 'thkcello',
            },
            'other': {
                'filenames': ['thkcello_Omon_HadGEM3-GC31-LL_amip_r1i1p1f1_198001-198001.nc'],
            },
        },
        ('CMIP6', 'Omon', 'vmo'): {  # (lat, lon, time, olevel)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Omon_vmo',
            },
            'request': {
                'ancil_files': '${COMMON:root_ancil_dir}/HadGEM3-GC31/HadGEM3-GC31-LL/ocean_byte_masks.nc',
                'model_output_dir': '${COMMON:root_test_location}/input/set2',
                'run_bounds': '1852-03-01-00-00-00 1852-04-01-00-00-00',
                'suite_id': 'u-ar050',
            },
            'stream_onm': {
                'CMIP6_Omon': 'vmo',
            },
            'other': {
                'filenames': ['vmo_Omon_UKESM1-0-LL_amip_r1i1p1f1_gn_185203-185203.nc'],
            },
        },
        ('CMIP6', 'Omon', 'vo'): {  # (lat, lon, time, depth)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Omon_vo',
            },
            'request': {
                'ancil_files': '${COMMON:root_ancil_dir}/UKESM1-0/UKESM1-0-LL/ocean_byte_masks.nc',
                'model_output_dir': '${COMMON:root_test_location}/input/set2',
                'run_bounds': '1960-01-01-00-00-00 1960-04-01-00-00-00',
                'suite_id': 'u-aw310',
            },
            'stream_onm_grid-V': {
                'CMIP6_Omon': 'vo',
            },
            'other': {
                'filenames': ['vo_Omon_UKESM1-0-LL_amip_r1i1p1f1_gn_196001-196003.nc'],
            },
        },
        ('CMIP6', 'Omon', 'multiple_substreams'): {  # (lat, lon, time, depth)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Omon_multiple_substreams',
            },
            'request': {
                'ancil_files': '${COMMON:root_ancil_dir}/UKESM1-0/UKESM1-0-LL/ocean_byte_masks.nc',
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1960-01-01-00-00-00 1960-02-01-00-00-00',
                'suite_id': 'u-aw310',
            },
            'stream_onm_grid-T': {
                'CMIP6_Omon': 'tos',
            },
            'stream_onm_grid-V': {
                'CMIP6_Omon': 'vo',
            },
            'other': {
                'filenames': [
                    'tos_Omon_UKESM1-0-LL_amip_r1i1p1f1_gn_196001-196001.nc',
                    'vo_Omon_UKESM1-0-LL_amip_r1i1p1f1_gn_196001-196001.nc'
                ],
            },
        },
        ('CMIP6', 'SImon', 'sndmassmelt'): {  # (lat, lon, time)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_SImon_sndmassmelt',
            },
            'cmor_setup': {
                'netcdf_file_action': 'CMOR_REPLACE_3',
            },
            'cmor_dataset': {
                'contact': 'chris.d.jones@metoffice.gov.uk',
                'output_file_template': '<variable_id><table><source_id><experiment_id><variant_label>',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set2',
                'run_bounds': '1854-03-01-00-00-00 1854-04-01-00-00-00',
                'suite_id': 'u-ar050',
            },
            'stream_inm': {
                'CMIP6_SImon': 'sndmassmelt',
            },
            'other': {
                'filenames': ['sndmassmelt_SImon_UKESM1-0-LL_amip_r1i1p1f1_185403-185403.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'SImon', 'sicompstren'): {  # (lat, lon, time)
            # Check load ignores 'model output files' not in time constraint.
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_SImon_sicompstren',
            },
            'cmor_setup': {
                'netcdf_file_action': 'CMOR_REPLACE_3',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set2',
                'run_bounds': '1854-03-01-00-00-00 1854-04-01-00-00-00',
                'suite_id': 'u-ar050',
            },
            'stream_inm': {
                'CMIP6_SImon': 'sicompstren',
            },
            'other': {
                'filenames': ['sicompstren_SImon_UKESM1-0-LL_amip_r1i1p1f1_gn_185403-185403.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'SImon', 'siitdsnthick'): {  # (lat, lon, time, iceband)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_SImon_siitdsnthick',
            },
            'cmor_setup': {
                'netcdf_file_action': 'CMOR_REPLACE_3',
            },
            'cmor_dataset': {
                'contact': 'chris.d.jones@metoffice.gov.uk',
                'output_file_template': '<variable_id><table><source_id><experiment_id><variant_label>',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set2',
                'run_bounds': '1854-03-01-00-00-00 1854-04-01-00-00-00',
                'suite_id': 'u-ar050',
            },
            'stream_inm': {
                'CMIP6_SImon': 'siitdsnthick',
            },
            'other': {
                'filenames': ['siitdsnthick_SImon_UKESM1-0-LL_amip_r1i1p1f1_185403-185403.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'SImon', 'sifllwutop'): {  # (lat, lon, time)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_SImon_sifllwutop',
            },
            'cmor_setup': {
                'netcdf_file_action': 'CMOR_REPLACE_3',
            },
            'cmor_dataset': {
                'contact': 'chris.d.jones@metoffice.gov.uk',
                'output_file_template': '<variable_id><table><source_id><experiment_id><variant_label>',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1851-05-01-00-00-00 1851-06-01-00-00-00',
                'suite_id': 'u-ar050',
            },
            'stream_ap5': {
                'CMIP6_SImon': 'sifllwutop',
            },
            'other': {
                'filenames': [
                    'sifllwutop_SImon_UKESM1-0-LL_amip_r1i1p1f1_'
                    '185105-185105.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'SIday', 'multiple_3d'): {  # grids differ (lat, lon, time)
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_SIday_multiple_3d',
            },
            'cmor_setup': {
                'netcdf_file_action': 'CMOR_REPLACE_3',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1978-10-01-00-00-00 1978-12-01-00-00-00',
                'suite_id': 'u-al114',
            },
            'stream_ind': {
                'CMIP6_SIday': 'sisnthick sispeed',
            },
            'other': {
                'filenames': [
                    'sisnthick_SIday_UKESM1-0-LL_amip_r1i1p1f1_gn_19781001-19781130.nc',
                    'sispeed_SIday_UKESM1-0-LL_amip_r1i1p1f1_gn_19781001-19781130.nc'
                ],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'SImon', 'siage'): {
            # Ensure that MIP Convert can cope with inconsistent time units
            # across a data set
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_SImon_siage',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'replacement_coordinates_file': '/project/cdds/etc/horizontal_coordinates/cice_eORCA1_coords.nc',
                'run_bounds': '1854-03-01-00-00-00 1854-05-01-00-00-00',
                'suite_id': 'u-ar050',
            },
            'stream_inm': {
                'CMIP6_SImon': 'siage',
            },
            'other': {
                'filenames': ['siage_SImon_UKESM1-0-LL_amip_r1i1p1f1_gn_185403-185404.nc'],
                'ignore_history': True
            },
        },
        ('CMIP6', 'fx', 'areacella'): {
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_fx_areacella',
            },
            'request': {
                'ancil_files': (
                    '${COMMON:root_ancil_dir}/HadGEM3-GC31/HadGEM3-GC31-LL/qrparm.orog.pp '
                    '${COMMON:root_ancil_dir}/HadGEM3-GC31/HadGEM3-GC31-LL/qrparm.landfrac.pp'
                ),
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1950-01-01-00-00-00 1950-02-01-00-00-00',
                'suite_id': 'ai674',
            },
            'stream_ancil': {
                'CMIP6_fx': 'areacella',
            },
            'other': {
                'filenames': ['areacella_fx_UKESM1-0-LL_amip_r1i1p1f1_gn.nc'],
                'ignore_history': True,
            },
        },
        ('CMIP6', 'Ofx', 'areacello'): {
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Ofx_areacello',
            },
            'request': {
                'ancil_files': (
                    '${COMMON:root_test_dir}/testdata/u-aj460/onf/u-aj460o_1ts_19760101_19760101_constants.nc'
                ),
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1950-01-01-00-00-00 1950-02-01-00-00-00',
                'suite_id': 'aj460',
            },
            'stream_ancil': {
                'CMIP6_Ofx': 'areacello',
            },
            'other': {
                'filenames': ['areacello_Ofx_UKESM1-0-LL_amip_r1i1p1f1_gn.nc'],
            },
        },
        ('CMIP6', '6hrPlevPt', 'vortmean'): {
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_6hrPlevPt_vortmean',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1950-01-01-00-00-00 1950-01-06-00-00-00',
                'suite_id': 'ai674',
            },
            'stream_ap7': {
                'CMIP6_6hrPlevPt': 'vortmean',
            },
            'other': {
                'filenames': ['vortmean_6hrPlevPt_UKESM1-0-LL_amip_r1i1p1f1_gn_195001010600-195001060000.nc'],
                'ignore_history': True
            }
        },
        ('CMIP6', 'Emon', 'thetaot300'): {
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Emon_thetaot300',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1850-01-01-00-00-00 1850-02-01-00-00-00',
                'suite_id': 'u-ar050',
            },
            'stream_onm': {
                'CMIP6_Emon': 'thetaot300',
            },
            'other': {
                'filenames': ['thetaot300_Emon_UKESM1-0-LL_amip_r1i1p1f1_gn_185001-185001.nc'],
                'ignore_history': True
            }
        },
        ('CMIP6', 'Omon', 'fgco2'): {
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Omon_fgco2',
            },
            'request': {
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1850-01-01-00-00-00 1850-03-01-00-00-00',
                'suite_id': 'u-bd288',
            },
            'stream_onm': {
                'CMIP6_Omon': 'fgco2',
            },
            'other': {
                'filenames': ['fgco2_Omon_UKESM1-0-LL_amip_r1i1p1f1_gn_185001-185002.nc'],
                'ignore_history': True,
                'tolerance_value': 1e-14,
            },
        },
        ('CMIP6', 'Omon', 'hfbasin'): {
            'COMMON': {
                'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CMIP6_Omon_hfbasin',
            },
            'request': {
                'ancil_files': '${COMMON:root_ancil_dir}/UKESM1-0/UKESM1-0-LL/diaptr_basin_masks.nc',
                'model_output_dir': '${COMMON:root_test_location}/input/set1',
                'run_bounds': '1960-01-01-00-00-00 1960-03-01-00-00-00',
                'suite_id': 'u-aw310',
            },
            'stream_onm': {
                'CMIP6_Omon': 'hfbasin',
            },
            'other': {
                'filenames': ['hfbasin_Omon_UKESM1-0-LL_amip_r1i1p1f1_gn_196001-196002.nc'],
                'ignore_history': True,
            },
        },
        # ('CORDEX', 'mon', 'uv'): {
        #     'COMMON': {
        #         'test_location': '${COMMON:root_test_location}/test_cases_python3/test_CORDEX_mon_uv',
        #     },
        #     'request': {
        #
        #         'model_output_dir': '${COMMON:root_test_location}/input/set1',
        #         'run_bounds': '2000-01-01-00-00-00 2000-03-01-00-00-00',
        #         'suite_id': 'u-ax977',
        #     },
        #     'stream_apm': {
        #         'CORDEX_mon': 'uas vas',
        #     },
        #     'other': {
        #         'filenames': ['uas_EUR-11_MOHC-HadGEM2-ES_cordex1_r1i1p1_HadREM3-GA7-05_v1_mon_200001-200002.nc',
        #                       'vas_EUR-11_MOHC-HadGEM2-ES_cordex1_r1i1p1_HadREM3-GA7-05_v1_mon_200001-200002.nc'],
        #         'ignore_history': True,
        #         'other_options': '-B',  # Buffer files (they are small so limited impact)
        #     },
        # },
    }
