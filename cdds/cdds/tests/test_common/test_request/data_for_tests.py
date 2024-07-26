# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.
from datetime import datetime
from metomi.isodatetime.data import TimePoint
import os


def expected_test_metadata():
    return {
        'branch_date_in_child': TimePoint(year=1960, month_of_year=1, day_of_month=1),
        'branch_date_in_parent': TimePoint(year=1960, month_of_year=1, day_of_month=1),
        'branch_method': 'standard',
        'base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
        'calendar': '360_day',
        'experiment_id': 'piControl',
        'institution_id': 'MOHC',
        'license': ('CMIP6 model data produced by the Met Office Hadley Centre is licensed under a Creative Commons '
                    'Attribution-ShareAlike 4.0 International License (https://creativecommons.org/licenses). Consult '
                    'https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use governing CMIP6 output, including '
                    'citation requirements and proper acknowledgment. Further information about this data, including '
                    'some limitations, can be found via the further_info_url (recorded as a global attribute in this '
                    'file) and at https://ukesm.ac.uk/cmip6. The data producers and data providers make no warranty, '
                    'either express or implied, including, but not limited to, warranties of merchantability and '
                    'fitness for a particular purpose. All liabilities arising from the supply of the information '
                    '(including any liability arising in negligence) are excluded to the fullest extent permitted by '
                    'law.'),
        'mip': 'CMIP',
        'mip_era': 'CMIP6',
        'parent_base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
        'parent_experiment_id': 'piControl-spinup',
        'parent_mip': 'CMIP',
        'parent_mip_era': 'CMIP6',
        'parent_model_id': 'UKESM1-0-LL',
        'parent_time_units': 'days since 1850-01-01',
        'parent_variant_label': 'r1i1p1f2',
        'sub_experiment_id': 'none',
        'variant_label': 'r1i1p1f2',
        'model_id': 'UKESM1-0-LL',
        'model_type': [
            'AOGCM', 'BGC', 'AER', 'CHEM'
        ]
    }


def expected_test_global_attributes():
    return {
        'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.UKESM1-0-LL.piControl.none.r1i1p1f2'
    }


def expected_test_common():
    return {
        'external_plugin': '',
        'external_plugin_location': '',
        'mip_table_dir': os.path.join(os.environ['CDDS_ETC'], 'mip_tables', 'CMIP6', '01.00.29'),
        'mode': 'strict',
        'package': 'round-1',
        'workflow_basename': 'UKESM1-0-LL_piControl_r1i1p1f2',
        'root_proc_dir': '/path/to/proc',
        'root_data_dir': '/path/to/data',
        'root_ancil_dir': os.path.join(os.environ['CDDS_ETC'], 'ancil'),
        'root_hybrid_heights_dir': os.path.join(os.environ['CDDS_ETC'], 'vertical_coordinates'),
        'root_replacement_coordinates_dir': os.path.join(os.environ['CDDS_ETC'], 'horizontal_coordinates'),
        'sites_file': os.path.join(os.environ['CDDS_ETC'], 'cfmip2', 'cfmip2-sites-orog.txt'),
        'standard_names_version': 'latest',
        'standard_names_dir': os.path.join(os.environ['CDDS_ETC'], 'standard_names'),
        'simulation': False,
        'log_level': 'INFO'
    }


def expected_test_data():
    return {
        'data_version': 'v20191128',
        'end_date': TimePoint(year=2170, month_of_year=1, day_of_month=1),
        'mass_data_class': 'crum',
        'mass_ensemble_member': '',
        'start_date': TimePoint(year=1970, month_of_year=1, day_of_month=1),
        'model_workflow_id': 'u-aw310',
        'model_workflow_branch': 'cdds',
        'model_workflow_revision': 115492,
        'streams': ['ap4', 'ap5'],
        'variable_list_file': '/data/cdds/variables.txt',
        'output_mass_root': 'moose:/adhoc/projects/cdds/',
        'output_mass_suffix': 'development'
    }


def expected_test_misc():
    return {
        'atmos_timestep': 1200,
        'use_proc_dir': True,
        'no_overwrite': False,
    }


def expected_test_inventory():
    return {
        'inventory_check': True,
        'inventory_database_location': '/project/cdds/inventory.db'
    }


def expected_text_conversion():
    return {
        'skip_extract': False,
        'skip_extract_validation': False,
        'skip_configure': False,
        'skip_qc': False,
        'skip_archive': False,
        'cdds_workflow_branch': 'trunk',
        'cylc_args': ['--workflow-name=cdds_{request_id}_{stream}'],
        'no_email_notifications': True,
        'scale_memory_limits': 2.0,
        'override_cycling_frequency': ['ap4=P1Y', 'ap5=P2Y'],
        'model_params_dir': '',
        'continue_if_mip_convert_failed': True,
        'delete_preexisting_proc_dir': True,
        'delete_preexisting_data_dir': True
    }


def expected_test_minimal_metadata():
    return {
        'branch_date_in_child': TimePoint(year=1960, month_of_year=1, day_of_month=1),
        'branch_date_in_parent': TimePoint(year=1960, month_of_year=1, day_of_month=1),
        'branch_method': 'standard',
        'calendar': '360_day',
        'base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
        'experiment_id': 'piControl',
        'institution_id': 'MOHC',
        'license': 'CMIP6 model data produced by MOHC is licensed under a Creative '
                   'Commons Attribution ShareAlike 4.0 International License '
                   '(https://creativecommons.org/licenses). Consult '
                   'https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use '
                   'governing CMIP6 output, including citation requirements and '
                   'proper acknowledgment. Further information about this data, '
                   'including some limitations, can be found via the further_info_url '
                   '(recorded as a global attribute in this file) . The data '
                   'producers and data providers make no warranty, either express or '
                   'implied, including, but not limited to, warranties of '
                   'merchantability and fitness for a particular purpose. All '
                   'liabilities arising from the supply of the information (including '
                   'any liability arising in negligence) are excluded to the fullest '
                   'extent permitted by law.',
        'mip': 'CMIP',
        'mip_era': 'CMIP6',
        'model_id': 'UKESM1-0-LL',
        'model_type': ['AOGCM', 'BGC', 'AER', 'CHEM'],
        'parent_base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
        'parent_experiment_id': 'piControl-spinup',
        'parent_mip': 'CMIP',
        'parent_mip_era': 'CMIP6',
        'parent_model_id': 'UKESM1-0-LL',
        'parent_time_units': 'days since 1850-01-01',
        'parent_variant_label': 'r1i1p1f2',
        'sub_experiment_id': 'none',
        'variant_label': 'r1i1p1f2'
    }


def expected_test_minimal_common():
    return {
        'external_plugin': '',
        'external_plugin_location': '',
        'log_level': 'INFO',
        'mip_table_dir': os.path.join(os.environ['CDDS_ETC'], 'mip_tables', 'CMIP6', '01.00.29'),
        'mode': 'strict',
        'package': 'round-1',
        'root_ancil_dir': os.path.join(os.environ['CDDS_ETC'], 'ancil'),
        'root_data_dir': '/path/to/data',
        'root_proc_dir': '/path/to/proc',
        'root_hybrid_heights_dir': os.path.join(os.environ['CDDS_ETC'], 'vertical_coordinates'),
        'root_replacement_coordinates_dir': os.path.join(os.environ['CDDS_ETC'], 'horizontal_coordinates'),
        'sites_file': os.path.join(os.environ['CDDS_ETC'], 'cfmip2', 'cfmip2-sites-orog.txt'),
        'standard_names_dir': os.path.join(os.environ['CDDS_ETC'], 'standard_names'),
        'standard_names_version': 'latest',
        'simulation': False,
        'workflow_basename': 'UKESM1-0-LL_piControl_r1i1p1f2'
    }


def expected_test_minimal_data(data_version: datetime):
    return {
        'data_version': data_version.strftime('v%Y%m%d'),
        'end_date': TimePoint(year=2170, month_of_year=1, day_of_month=1),
        'mass_data_class': 'crum',
        'mass_ensemble_member': '',
        'output_mass_root': '',
        'output_mass_suffix': '',
        'start_date': TimePoint(year=1970, month_of_year=1, day_of_month=1),
        'streams': ['ap4', 'ap5', 'ap6', 'inm', 'onm'],
        'variable_list_file': '/data/cdds/variables.txt',
        'model_workflow_branch': 'cdds',
        'model_workflow_id': 'u-aw310',
        'model_workflow_revision': 'HEAD'
    }


def expected_test_minimal_misc():
    return {
        'atmos_timestep': 1200,
        'no_overwrite': False,
        'use_proc_dir': True
    }


def expected_test_minimal_inventory():
    return {
        'inventory_check': False,
        'inventory_database_location': ''
    }


def expected_test_minimal_conversion():
    return {
        'cdds_workflow_branch': 'trunk',
        'cylc_args': [],
        'model_params_dir': '',
        'no_email_notifications': True,
        'override_cycling_frequency': [],
        'continue_if_mip_convert_failed': False,
        'scale_memory_limits': None,
        'skip_archive': False,
        'skip_configure': False,
        'skip_extract': False,
        'skip_extract_validation': False,
        'skip_qc': False,
        'delete_preexisting_proc_dir': False,
        'delete_preexisting_data_dir': False
    }
