# (C) British Crown Copyright 2019-2023, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`constants` module contains constants (values that should never
be changes by a user and exist for readability and maintainability
purposes) for all CDDS components.
"""
import numpy as np

import cf_units


# Note that orography (m01s00i033) must not go in this list
ANCIL_VARIABLES = [
    # land frac
    'm01s00i505',  # Land fraction in grid box
    # soil
    'm01s00i008',  # SOIL BULK DENSITY   KG/M3 (retd)
    'm01s00i040',  # VOL SMC AT WILTING AFTER TIMESTEP
    'm01s00i041',  # VOL SMC AT CRIT PT AFTER TIMESTEP
    'm01s00i043',  # VOL SMC AT SATURATION AFTER TIMESTEP
    'm01s00i044',  # SAT SOIL CONDUCTIVITY AFTER TIMESTEP
    'm01s00i046',  # THERMAL CAPACITY AFTER TIMESTEP
    'm01s00i047',  # THERMAL CONDUCTIVITY AFTER TIMESTEP
    'm01s00i048',  # SATURATED SOIL WATER SUCTION
    'm01s00i207',  # CLAPP-HORNBERGER "B" COEFFICIENT
    'm01s00i220',  # SNOW-FREE ALBEDO OF SOIL
    'm01s00i223',  # SOIL CARBON CONTENT       KG C / M2
    # ocean_constants.nc
    'areacello',  # cell_area
    'deptho',  # sea_floor_depth_below_geoid
    'deptht',  # depth
    'difmxlo2d',  # ocean_momentum_xy_laplacian_diffusivity
    'diftrelo2d',  # ocean_tracer_epineutral_laplacian_diffusivity
    'difvmbo',  # ocean_vertical_momentum_diffusivity_due_to_background
    'difvtrbo',  # ocean_vertical_tracer_diffusivity_due_to_background
    'hfgeou',  # upward_geothermal_heat_flux_at_sea_floor
    'sftof',  # sea_area_fraction
    # ocean_byte_masks.nc
    'mask_2D_T',  # 2D_mask_grid_T
    'mask_2D_U',  # 2D_mask_grid_U
    'mask_2D_V',  # 2D_mask_grid_V
    'mask_3D_T',  # 3D_mask_grid_T
    'mask_3D_U',  # 3D_mask_grid_U
    'mask_3D_V',  # 3D_mask_grid_V
    'atlantic_arctic_ocean_2D_T',  # 2D_mask_grid_T
    'global_ocean_2D_T',  # 2D_mask_grid_T
    'indian_pacific_ocean_2D_T',  # 2D_mask_grid_T
    'atlantic_arctic_ocean_1D_T',  # 1D_mask_grid_T
    'global_ocean_1D_T',  # 1D_mask_grid_T
    'indian_pacific_ocean_1D_T',  # 1D_mask_grid_T
    'atlantic_arctic_ocean_2D_V',  # 2D_mask_grid_V
    'global_ocean_2D_V',  # 2D_mask_grid_V
    'indian_pacific_ocean_2D_V',  # 2D_mask_grid_V
    'atlantic_arctic_ocean_1D_V',  # 1D_mask_grid_V
    'global_ocean_1D_V',  # 1D_mask_grid_V
    'indian_pacific_ocean_1D_V',  # 1D_mask_grid_V
    'zfullo_0',  # ocean_zostoga
    'so_0',  # ocean_zostoga
    'rho_0_mean',  # ocean_zostoga
    'deptho_0_mean',  # ocean_zostoga
]
APPROVED_VARS_PREFIX = 'approved_variables'
APPROVED_VARS_FILENAME_TEMPLATE = APPROVED_VARS_PREFIX + '_{dt}.txt'
APPROVED_VARS_FILENAME_STREAM_TEMPLATE = (
    APPROVED_VARS_PREFIX + '_{stream_id}_{dt}.txt')

# regex to find the datetime in the approved variables files present in the
# proc directory, so they can be sorted
APPROVED_VARS_DATETIME_REGEX = (
    r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
    r'T(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})')
APPROVED_VARS_DATETIME_STREAM_REGEX = '?(?P<stream>[a-z0-9]{3})?_' + APPROVED_VARS_DATETIME_REGEX
APPROVED_VARS_FILENAME_REGEX = APPROVED_VARS_PREFIX + '_' + APPROVED_VARS_DATETIME_REGEX + '.txt'
APPROVED_VARS_FILENAME_STREAM_REGEX = APPROVED_VARS_PREFIX + '_' + APPROVED_VARS_DATETIME_STREAM_REGEX + '.txt'

# regex to process the contents of each line of the approved variables file
APPROVED_VARS_VARIABLE_REGEX = ('(?P<mip_table_id>[a-zA-Z0-9]+)/'
                                '(?P<variable_id>[a-zA-Z0-9]+);'
                                '(?P<outdir>[a-zA-Z0-9-/_.]+)')

ARGUMENTS_FILENAME = 'arguments.json'
BYTES_32BIT_DATA = 4
CDDS_DEFAULT_DIRECTORY_PERMISSIONS = 0o775
COMMENT_FORMAT = '# {}\n\n'
COMPONENT_LIST = ['prepare', 'extract', 'configure', 'convert',
                  'qualitycheck', 'archive']
CYLC_DATE_FORMAT = '%Y%m%dT%H%M%SZ'
DATA_DIR_FACET_STRING = (
    'programme|project|model|experiment|realisation|package')
# used for Dataset version
DATESTAMP_TEMPLATE = 'v{dt.year:04d}{dt.month:02d}{dt.day:02d}'
DATESTAMP_PARSER_STR = 'v%Y%m%d'

DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
DATE_TIME_REGEX = (
    r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})T(?P<hour>\d{2}):'
    r'(?P<minute>\d{2}):(?P<second>\d{2})')
DAYS_IN_MONTH = 30
DAYS_IN_YEAR = 360
GLOBAL_ARGUMENTS_FILENAME = 'global_arguments.json'
GLOBAL_ARGUMENTS_FILENAME_JASMIN = 'global_arguments_jasmin.json'
JASMIN_URL_IDS = {'.ac.uk'}

INPUT_DATA_DIRECTORY = 'input'
INVENTORY_DB_FILENAME = 'inventory'
INVENTORY_FACET_LIST = ["mip_era", "mip", "institution", "model", "experiment", "variant", "mip_table", "variable",
                        "grid", "status", "timestamp"]
INVENTORY_HEADINGS = ['Mip Era', 'Mip', 'Institute', 'Model', 'Experiment', 'Variant', 'Mip Table', 'Variable Name',
                      'Grid', 'Status', 'Version', 'Facet String']
INVENTORY_HEADINGS_FORMAT = '{:7} {:6} {:10} {:18} {:15} {:10} {:10} {:20} {:4} {:10} {:10} {:10}'
LOG_DIRECTORY = 'log'
LOG_TIMESTAMP_FORMAT = '%Y-%m-%dT%H%MZ'
MIP_CONVERT_DATETIME_FORMAT = ('{0.year:04d}-{0.month_of_year:02d}-{0.day_of_month:02d}T'
                               '{0.hour_of_day:02d}:{0.minute_of_hour:02d}:{0.second_of_minute:02d}')

NC_CONSTRAINT_NOT_FOR_MOOSE = ["depth"]
NO_PARENT = 'no parent'
STANDARD = 'standard'
OUTPUT_DATA_DIRECTORY = 'output'
PACKAGE_KEY_FOR_ARGUMENTS = 'package'
PARENT_ATTRIBUTES = [
    'branch_date_in_child', 'branch_date_in_parent', 'parent_base_date',
    'parent_mip', 'parent_mip_era', 'parent_model_id', 'parent_time_units',
    'parent_variant_label', 'parent_experiment_id'
]
# The use of "days since ..." as the time units is hard coded into
# the CMIP6 CVs. This could be otherwise for other projects.
PARENT_TIME_UNITS_FORMAT = 'days since {}'
PARENT_TIME_UNITS_DATETIME_FORMAT = '%Y-%m-%d'
PP_CODE_HYBRID_HEIGHT = 65
PP_CODE_HYBRID_PRESSURE = 9
PP_CODE_SOIL = 6
PP_HEADER_CORRECTIONS = {
    # {(STASH codes to be corrected): (
    #     (um_version_with_expression),
    #     (({pp_field_header_element_name:
    #        pp_field_header_element_value_to_match},
    #       {pp_field_header_element_name:
    #        correct_pp_field_header_element_value}),),)}
    (2261,): (
        # Old versions of the UM set 'lbvc' incorrectly in fields with
        # this STASH code, suggesting they were hybrid sigma pressure,
        # when in fact they were hybrid height. This has since been
        # fixed; this correction provides compatatibility with old UM
        # versions.
        ('<8.6'),
        (({'lbvc': PP_CODE_HYBRID_PRESSURE},
          {'lbvc': PP_CODE_HYBRID_HEIGHT}),),),
    (2321, 2344): (
        ('>1.0'),
        (({'blev': -1.0},
          {'blev': 840.0}),),),
    (2322, 2345): (
        ('>1.0'),
        (({'blev': -1.0},
          {'blev': 560.0}),),),
    (2323, 2346): (
        ('>1.0'),
        (({'blev': -1.0},
          {'blev': 220.0}),),),
    (2337, 2450): (
        ('>1.0'),
        (({'blev': 115.0},
          {'blev': 90.0}),),),
    (8223, 8225): (
        ('<9.3'),
        (({'lbvc': PP_CODE_SOIL, 'blev': 1.0},
          {'blev': 0.05, 'brsvd1': 0.0, 'brlev': 0.1}),
         ({'lbvc': PP_CODE_SOIL, 'blev': 2.},
          {'blev': 0.225, 'brsvd1': 0.1, 'brlev': 0.35}),
         ({'lbvc': PP_CODE_SOIL, 'blev': 3.},
          {'blev': 0.675, 'brsvd1': 0.35, 'brlev': 1.0}),
         ({'lbvc': PP_CODE_SOIL, 'blev': 4.},
          {'blev': 2.0, 'brsvd1': 1.0, 'brlev': 3.0}),),),
    (30310, 30311, 30312, 30313, 30314, 30315, 30316): (
        # These STASH codes are only output as zonal means but LBPROC is not
        # set to indicate a zonal mean by the UM
        ('>1.0'),  # all versions
        (({'lbproc': 128},
          {'lbproc': 192}),),),
    (30455,): (
        ('>1.0'),
        (({'blev': -1.0},
          {'blev': 850.0}),),),
}
PROC_DIRECTORY_FACET_STRING = 'programme|project|request|package'
PROCESSING_WORKFLOW = 'u-cy526'
REQUESTED_VARIABLES_LIST_FACET_STRING = 'programme|project|experiment|model'
REQUIRED_KEYS_FOR_GENERAL_CONFIG_ACCESS = ['config_version', 'mip_era']
REQUIRED_KEYS_FOR_PROC_DIRECTORY = [
    'experiment_id', 'mip', 'mip_era', 'model_id', 'package', 'variant_label']
REQUIRED_KEYS_FOR_REQUESTED_VARIABLES_LIST = [
    'experiment_id', 'mip', 'mip_era', 'model_id', 'model_type',
    'suite_branch', 'suite_id', 'suite_revision']
ROSE_URLS = {
    'u': {'external': 'https://code.metoffice.gov.uk/svn/roses-u',
          # Access to the mirror does not require authentication.
          'internal': 'svn://fcm1/roses-u.xm_svn'},
    'mi': {'internal': 'svn://fcm1/roses_mi_svn'}
}
SCRIPT_TEMPLATE = """#!/bin/bash -l
#SBATCH --output={log_directory}/{component}_%J.out
#SBATCH --error={log_directory}/{component}_%J.err
#SBATCH --mail-type=END
#SBATCH --mail-user={email}
#SBATCH --wckey=cdds
#SBATCH --time={wall_time}
#SBATCH --ntasks=1
#SBATCH --mem={memory}
#SBATCH --qos={queue}

{env_setup};{command}
"""
SUPPORTED_CALENDARS = ["gregorian", "360_day", "360day"]
TIME_UNIT_DESCRIPTION = 'days since 1850-01-01'
TIME_UNIT = cf_units.Unit(TIME_UNIT_DESCRIPTION, calendar='360_day')
USER_CONFIG_OPTIONS = {
    # section: {option_type: [options]}
    'cmor_setup': {
        'required': ['mip_table_dir'],
        'optional': [
            'cmor_log_file', 'create_subdirectories', 'exit_control',
            'netcdf_file_action', 'set_verbosity'],
    },
    'cmor_dataset': {
        'required': [
            'branch_method', 'calendar', 'experiment_id', 'institution_id',
            'license', 'mip', 'mip_era', 'model_id', 'model_type',
            'output_dir', 'sub_experiment_id', 'variant_label'],
        'required_for_grid': ['grid', 'grid_label', 'nominal_resolution'],
        'optional': [
            'comment', 'contact',
            'grid_resolution',  # required for CMIP5 functional tests
            'output_file_template', 'output_path_template', 'references',
            'variant_info'],
        'branch': [
            'branch_date_in_child', 'branch_date_in_parent',
            'parent_base_date', 'parent_experiment_id', 'parent_mip_era',
            'parent_model_id', 'parent_time_units', 'parent_variant_label'],
    },
    'request': {
        'required': [
            'child_base_date', 'model_output_dir', 'run_bounds', 'suite_id'],
        'optional': [
            'ancil_files', 'atmos_timestep', 'deflate_level',
            'hybrid_heights_files', 'replacement_coordinates_file', 'shuffle',
            'sites_file'],
    },
}
VARIANT_LABEL_FORMAT = r'^r(\d+)i(\d+)p(\d+)f(\d+)$'
PRINT_STACK_TRACE = 1

CYLC_PATHS = [r'\/net\/home\/h03\/fcm\/rose\-.+\/lib\/python', r'\/net\/home\/h03\/fcm\/cylc\-.+\/lib',
              r'\/apps\/contrib\/metomi\/rose\-.+\/lib\/python', r'\/apps\/contrib\/metomi\/cylc\-.+\/lib',
              r'\/apps\/jasmin\/metomi\/rose\-.+\/lib\/python', r'\/apps\/jasmin/metomi\/cylc\-.+\/lib', ]
