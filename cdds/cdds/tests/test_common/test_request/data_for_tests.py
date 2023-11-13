# (C) British Crown Copyright 2023-2023, Met Office.
# Please see LICENSE.rst for license details.
import datetime

from metomi.isodatetime.data import TimePoint


def expected_test_metadata():
    return {
        'branch_date_in_child': TimePoint(year=1960, month_of_year=1, day_of_month=1),
        'branch_date_in_parent': TimePoint(year=1960, month_of_year=1, day_of_month=1),
        'branch_method': 'standard',
        'child_base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
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
        'standard_names_version': 'latest',
        'standard_names_dir': '/etc/standard_names',
        'model_id': 'UKESM1-0-LL',
        'model_type': [
            'AOGCM', 'BGC', 'AER', 'CHEM'
        ]
    }


def expected_test_global_attributes():
    return {
        'further_info_url': 'https://furtherinfo.es-doc.org/'
    }


def expected_test_common():
    return {
        'cdds_version': '',
        'external_plugin': '',
        'external_plugin_location': '',
        'mip_table_dir': '/home/h03/cdds/etc/mip_tables/CMIP6/01.00.29',
        'mode': 'strict',
        'package': 'round-1',
        'workflow_basename': 'UKESM1-0-LL_piControl_r1i1p1f2',
        'root_proc_dir': '/project/cdds/proc',
        'root_data_dir': '/project/cdds/data',
        'root_ancil_dir': '/project/cdds/ancil',
        'simulation': False,
        'log_level': 'INFO',
        'data_version': 'v20191128'
    }


def expected_test_data():
    return {
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
        'data_request_version': '01.00.29',
        'data_request_base_dir': '/data_requests/CMIP6',
        'mips_to_contribute_to': ['AerChemMIP', 'C4MIP'],
        'mapping_status': 'ok',
        'alternate_data_request_experiment': '',
        'use_proc_dir': True,
        'max_priority': 2,
        'mip_era_defaults': '',
        'no_overwrite': False,
        'no_auto_deactivation': False,
        'auto_deactivation_rules': ''
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
        'cylc_args': '',
        'no_email_notifications': False,
        'scale_memory_limits': 2.0,
        'override_cycling_frequency': ['ap4=P1Y', 'ap5=P2Y'],
        'model_params_dir': ''
    }


def expected_test_minimal_metadata():
    return {
        'branch_date_in_child': TimePoint(year=1960, month_of_year=1, day_of_month=1),
        'branch_date_in_parent': TimePoint(year=1960, month_of_year=1, day_of_month=1),
        'branch_method': 'standard',
        'calendar': '360_day',
        'child_base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
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
        'standard_names_dir': '/home/h03/cdds/etc/standard_names/',
        'standard_names_version': 'latest',
        'sub_experiment_id': 'none',
        'variant_label': 'r1i1p1f2'
    }


def expected_test_minimal_common(data_version):
    return {
        'cdds_version': '2.6.0.dev0',
        'data_version': data_version.strftime('%Y-%m-%dT%H%MZ'),
        'external_plugin': '',
        'external_plugin_location': '',
        'log_level': 'INFO',
        'mip_table_dir': '/home/h03/cdds/etc/mip_tables/CMIP6/01.00.29/',
        'mode': 'strict',
        'package': 'round-1',
        'root_ancil_dir': '/home/h03/cdds/etc/ancil/',
        'root_data_dir': '/project/cdds_data',
        'root_proc_dir': '/project/cdds/proc',
        'simulation': False,
        'workflow_basename': 'UKESM1-0-LL_piControl_r1i1p1f2'
    }


def expected_test_minimal_data():
    return {
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
        'alternate_data_request_experiment': '',
        'auto_deactivation_rules': '',
        'data_request_base_dir': '/home/h03/cdds/etc/data_requests/CMIP6',
        'data_request_version': '01.00.29',
        'mapping_status': 'ok',
        'max_priority': 2,
        'mip_era_defaults': '',
        'mips_to_contribute_to': ['AerChemMIP',
                                  'C4MIP',
                                  'CDRMIP',
                                  'CFMIP',
                                  'CMIP',
                                  'CORDEX',
                                  'DAMIP',
                                  'DCPP',
                                  'DynVar',
                                  'FAFMIP',
                                  'GeoMIP',
                                  'GMMIP',
                                  'HighResMIP',
                                  'ISMIP6',
                                  'LS3MIP',
                                  'LUMIP',
                                  'OMIP',
                                  'PAMIP',
                                  'PMIP',
                                  'RFMIP',
                                  'ScenarioMIP',
                                  'SIMIP',
                                  'VIACSAB',
                                  'VolMIP'],
        'no_auto_deactivation': False,
        'no_overwrite': False,
        'use_proc_dir': False
    }


def expected_test_minimal_inventory():
    return {
        'inventory_check': False,
        'inventory_database_location': ''
    }


def expected_test_minimal_conversion():
    return {
        'cdds_workflow_branch': 'trunk',
        'cylc_args': '',
        'model_params_dir': '',
        'no_email_notifications': False,
        'override_cycling_frequency': [],
        'scale_memory_limits': None,
        'skip_archive': False,
        'skip_configure': False,
        'skip_extract': False,
        'skip_extract_validation': False,
        'skip_qc': False
    }
