# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import logging
import os

from datetime import datetime

from cdds import __version__
from cdds.common.plugins.grid import GridType
from cdds.common.plugins.plugins import PluginStore
from cdds.common.platforms import whereami, Facility


def metadata_defaults(model_id):
    license = PluginStore.get_plugin().license()
    facility = whereami()
    if facility == Facility.JASMIN:
        standard_names_dir = '/gws/smf/j04/cmip6_prep/cdds-env-python3/etc/standard_names/'
    else:
        standard_names_dir = '{}/standard_names/'.format(os.environ['CDDS_ETC'])

    return {
        'calendar': '360_day',
        'child_base_date': '1850-01-01-00-00-00',
        'license': license,
        'parent_base_date': '1850-01-01-00-00-00',
        'parent_model_id': model_id,
        'parent_time_units': 'days since 1850-01-01',
        'standard_names_dir': standard_names_dir,
        'standard_names_version': 'latest',
    }


def common_defaults(model_id, experiment_id, variant_label):
    mip_table_dir = PluginStore.get_plugin().mip_table_dir()

    facility = whereami()
    if facility == Facility.JASMIN:
        root_ancil_dir = '/gws/smf/j04/cmip6_prep/cdds-env-python3/etc/ancil/'
    else:
        root_ancil_dir = '{}/ancil/'.format(os.environ['CDDS_ETC'])
    return {
        'cdds_version': __version__,
        'data_version': datetime.now(),
        'external_plugin': '',
        'external_plugin_location': '',
        'log_level': logging.INFO,
        'mip_table_dir': mip_table_dir,
        'root_ancil_dir': root_ancil_dir,
        'root_data_dir': '/project/cdds_data',
        'root_proc_dir': '/project/cdds/proc',
        'simulation': False,
        'workflow_basename': '{}_{}_{}'.format(model_id, experiment_id, variant_label)
    }


def data_defaults():
    return {
        "mass_data_class": 'crum',
        "output_mass_root": "moose:/adhoc/projects/cdds/",
        "output_mass_suffix": "development",
        "streams": "ap4 ap5 ap6 inm onm",
        "workflow_branch": 'cdds',
        "worklow_revision": 'HEAD',
    }


def misc_defaults(model_id):
    grid_info = PluginStore.get_plugin().grid_info(model_id, GridType.ATMOS)
    atmos_timestep = grid_info.atmos_timestep

    return {
        "atmos_timestep": atmos_timestep
    }


def inventory_defaults():
    facility = whereami()
    if facility == Facility.JASMIN:
        inventory_database_location = '/gws/smf/j04/cmip6_prep/cdds-env-python3/etc/inventory/inventory.db'
        data_request_base_dir = '/gws/smf/j04/cmip6_prep/cdds-env-python3/etc/data_requests/CMIP6/'
    else:
        inventory_database_location = '/project/cdds/inventory/inventory.db'
        data_request_base_dir = '{}/data_requests/CMIP6'.format(os.environ['CDDS_ETC'])

    return {
        "inventory_check": True,
        "inventory_database_location": inventory_database_location,
        "no_auto_deactivation": False,
        # 'auto_deactivation_rules': 'https://code.metoffice.gov.uk/svn/cdds/variable_issues/trunk/',
        # Todo: needs considerations:
        'data_request_version': '01.00.29',
        'data_request_base_dir': data_request_base_dir,
        'mips_to_contribute_to': [
            'AerChemMIP',
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
            'VolMIP'
        ],
        'mapping_status': 'ok',
        'use_proc_dir': False,
        'max_priority': 2,
        'no_overwrite': False
    }


def conversion_defaults():
    facility = whereami()
    if facility == Facility.JASMIN:
        skip_extract = True
        skip_extract_validation = False
        skip_configure = False
        skip_qc = False
        skip_archive = True
        cdds_workflow_branch = "cdds_jasmin_2.3"
    else:
        skip_extract = False
        skip_extract_validation = False
        skip_configure = False
        skip_qc = False
        skip_archive = False
        cdds_workflow_branch = "trunk"

    return {
        "cdds_workflow_branch": cdds_workflow_branch,
        "no_email_notifications": False,
        "skip_extract": skip_extract,
        "skip_extract_validation": skip_extract_validation,
        "skip_configure": skip_configure,
        "skip_qc": skip_qc,
        "skip_archive": skip_archive,
    }
