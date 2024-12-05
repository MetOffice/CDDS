# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
"""
Module to transform a request JSON object into a request configuration object
"""
import logging
import os

from metomi.isodatetime.parsers import TimePointParser

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.io import read_json
from cdds.common.request.request import Request
from cdds.common.request.metadata_section import MetadataSection
from cdds.common.request.common_section import CommonSection
from cdds.common.request.conversion_section import ConversionSection
from cdds.common.request.data_section import DataSection
from cdds.common.request.inventory_section import InventorySection
from cdds.common.request.misc_section import MiscSection
from cdds.common.request.attributes_section import GlobalAttributesSection


def transform_request(input_json: str, output_cfg: str) -> None:
    """
    Transforms the request JSON from the input file into a request configuration
    with corresponding information and writes it into to given output file.

    :param input_json: Input file containing the request JSON information
    :type input_json: str
    :param output_cfg: Output file where the request cfg will be written to
    :type output_cfg: str
    """
    logger = logging.getLogger(__name__)

    logger.info('Read request json from {}'.format(input_json))
    json_request = read_json(input_json)

    external_plugin = json_request.get('external_plugin', '')
    external_plugin_location = json_request.get('external_plugin_location', '')
    load_plugin(json_request['mip_era'], external_plugin, external_plugin_location)

    branch_method = json_request['branch_method']

    start_date, end_date = json_request['run_bounds'].split()

    streams = [key.split('run_bounds_for_stream_')[1] for key in json_request.keys()
               if key.startswith('run_bounds_for_stream_')]

    root_ancil_dir = os.path.join(os.environ['CDDS_ETC'], 'ancil')
    root_hybrid_heights_dir = os.path.join(os.environ['CDDS_ETC'], 'vertical_coordinates')
    root_replacement_coordinates_dir = os.path.join(os.environ['CDDS_ETC'], 'horizontal_coordinates')
    sites_file = os.path.join(os.environ['CDDS_ETC'], 'cfmip2', 'cfmip2-sites-orog.txt')
    standard_names_dir = os.path.join(os.environ['CDDS_ETC'], 'standard_names')

    if branch_method != 'no parent':
        metadata = MetadataSection(
            branch_date_in_child=TimePointParser().parse(json_request['branch_date_in_child']),
            branch_date_in_parent=TimePointParser().parse(json_request['branch_date_in_parent']),
            branch_method=branch_method,
            base_date=TimePointParser().parse(json_request['child_base_date']),
            calendar=json_request['calendar'],
            experiment_id=json_request['experiment_id'],
            institution_id=json_request['institution_id'],
            license=json_request['license'],
            mip=json_request['mip'],
            mip_era=json_request['mip_era'],
            parent_base_date=TimePointParser().parse(json_request['parent_base_date']),
            parent_experiment_id=json_request['parent_experiment_id'],
            parent_mip=json_request['parent_mip'],
            parent_mip_era=json_request['parent_mip_era'],
            parent_model_id=json_request['parent_model_id'],
            parent_time_units=json_request['parent_time_units'],
            parent_variant_label=json_request['parent_variant_label'],
            sub_experiment_id=json_request['sub_experiment_id'],
            variant_label=json_request['variant_label'],
            model_id=json_request['model_id'],
            model_type=json_request['model_type']
        )
    else:
        metadata = MetadataSection(
            branch_method=branch_method,
            base_date=TimePointParser().parse(json_request['child_base_date']),
            calendar=json_request['calendar'],
            experiment_id=json_request['experiment_id'],
            institution_id=json_request['institution_id'],
            license=json_request['license'],
            mip=json_request['mip'],
            mip_era=json_request['mip_era'],
            sub_experiment_id=json_request['sub_experiment_id'],
            variant_label=json_request['variant_label'],
            model_id=json_request['model_id'],
            model_type=json_request['model_type']
        )

    common = CommonSection(
        force_plugin='',
        external_plugin=json_request.get('external_plugin', ''),
        external_plugin_location=json_request.get('external_plugin_location', ''),
        mip_table_dir=json_request['mip_table_dir'],
        mode='strict',
        package=json_request['package'],
        workflow_basename=json_request['request_id'],
        root_proc_dir='',
        root_data_dir='',
        root_ancil_dir=root_ancil_dir,
        root_hybrid_heights_dir=root_hybrid_heights_dir,
        root_replacement_coordinates_dir=root_replacement_coordinates_dir,
        sites_file=sites_file,
        standard_names_version='latest',
        standard_names_dir=standard_names_dir,
        simulation=False,
        log_level='INFO'
    )

    logger.info('The path to the root proc directory ("{root_proc_dir}") and the path to the data directory '
                '("root_data_dir") must be set in the common section manually.')

    conversion = ConversionSection(
        skip_extract=False,
        skip_extract_validation=False,
        skip_configure=False,
        skip_qc=False,
        skip_archive=False,
        cylc_args=[],
        no_email_notifications=True,
        scale_memory_limits=None,
        override_cycling_frequency=[],
        model_params_dir='',
        continue_if_mip_convert_failed=False,
        delete_preexisting_proc_dir=False,
        delete_preexisting_data_dir=False
    )

    # Set data version to empty white space to make sure that it won't be set to the default
    data = DataSection(
        data_version=' ',
        end_date=TimePointParser().parse(end_date),
        mass_data_class=json_request.get('mass_data_class', 'crum'),
        mass_ensemble_member=json_request.get('mass_ensemble_member', ''),
        start_date=TimePointParser().parse(start_date),
        model_workflow_id=json_request['suite_id'],
        model_workflow_branch=json_request.get('suite_branch', 'cdds'),
        model_workflow_revision=json_request.get('suite_revision', 'HEAD'),
        streams=streams,
        variable_list_file='',
        output_mass_root='',
        output_mass_suffix=''
    )

    logger.info('The path to the variable list file ("variable_list_file") must be set in the data section manually.')
    logger.info('Following MASS related values must be set manually in the data section: {}'
                ''.format(', '.join(['output_mass_root', 'output_mass_suffix', 'data_version'])))

    inventory = InventorySection(
        inventory_check=False,
        inventory_database_location=''
    )

    misc = MiscSection(
        atmos_timestep=int(json_request['atmos_timestep']),
        use_proc_dir=True,
        no_overwrite=False
    )

    global_attributes = GlobalAttributesSection(
        attributes=json_request.get('global_attributes', {})
    )

    logger.info('Write request configuration into {}'.format(output_cfg))
    logger.info('Please, check all configuration settings before running CDDS.')

    cfg_request = Request(
        metadata=metadata,
        common=common,
        data=data,
        inventory=inventory,
        conversion=conversion,
        misc=misc,
        netcdf_global_attributes=global_attributes
    )
    cfg_request.write(output_cfg)
