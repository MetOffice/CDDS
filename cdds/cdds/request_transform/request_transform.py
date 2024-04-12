# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
"""
Module to transform a request JSON object into a request configuration object
"""
import logging

from metomi.isodatetime.parsers import TimePointParser

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.io import read_json
from cdds.common.request.request import Request


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

    cfg_request = Request()
    cfg_request.metadata.branch_method = branch_method

    if branch_method != 'no parent':
        cfg_request.metadata.branch_date_in_child = TimePointParser().parse(json_request['branch_date_in_child'])
        cfg_request.metadata.branch_date_in_parent = TimePointParser().parse(json_request['branch_date_in_parent'])
        cfg_request.metadata.parent_base_date = TimePointParser().parse(json_request['parent_base_date'])
        cfg_request.metadata.parent_experiment_id = json_request['parent_experiment_id']
        cfg_request.metadata.parent_mip = json_request['parent_mip']
        cfg_request.metadata.parent_mip_era = json_request['parent_mip_era']
        cfg_request.metadata.parent_model_id = json_request['parent_model_id']
        cfg_request.metadata.parent_time_units = json_request['parent_time_units']
        cfg_request.metadata.parent_variant_label = json_request['parent_variant_label']

    cfg_request.metadata.child_base_date = TimePointParser().parse(json_request['child_base_date'])
    cfg_request.metadata.calendar = json_request['calendar']
    cfg_request.metadata.experiment_id = json_request['experiment_id']
    cfg_request.metadata.institution_id = json_request['institution_id']
    cfg_request.metadata.license = json_request['license']
    cfg_request.metadata.mip = json_request['mip']
    cfg_request.metadata.mip_era = json_request['mip_era']
    cfg_request.metadata.sub_experiment_id = json_request['sub_experiment_id']
    cfg_request.metadata.variant_label = json_request['variant_label']
    cfg_request.metadata.model_id = json_request['model_id']
    cfg_request.metadata.model_type = json_request['model_type']

    cfg_request.common.cdds_version = json_request['config_version']
    cfg_request.common.external_plugin = json_request.get('external_plugin', '')
    cfg_request.common.external_plugin_location = json_request.get('external_plugin_location', '')
    cfg_request.common.mip_table_dir = json_request['mip_table_dir']
    cfg_request.common.package = json_request['package']
    cfg_request.common.workflow_basename = json_request['request_id']

    cfg_request.conversion.skip_extract = False
    cfg_request.conversion.skip_extract_validation = False
    cfg_request.conversion.skip_configure = False
    cfg_request.conversion.skip_qc = False
    cfg_request.conversion.skip_archive = False
    cfg_request.conversion.cdds_workflow_branch = 'trunk'
    cfg_request.conversion.no_email_notifications = True
    cfg_request.conversion.scale_memory_limits = None
    cfg_request.conversion.override_cycling_frequency = []

    cfg_request.data.end_date = TimePointParser().parse(end_date)
    cfg_request.data.mass_data_class = json_request.get('mass_data_class', 'crum')
    cfg_request.data.mass_ensemble_member = json_request.get('mass_ensemble_member', '')
    cfg_request.data.start_date = TimePointParser().parse(start_date)
    cfg_request.data.model_workflow_id = json_request['suite_id']
    cfg_request.data.model_workflow_branch = json_request.get('suite_branch', 'cdds')
    cfg_request.data.model_workflow_revision = json_request.get('suite_revision', 'HEAD')
    cfg_request.data.streams = streams

    cfg_request.inventory.inventory_check = False
    cfg_request.inventory.inventory_database_location = ''

    cfg_request.misc.atmos_timestep = int(json_request['atmos_timestep'])
    cfg_request.misc.use_proc_dir = False
    cfg_request.misc.no_overwrite = False

    cfg_request.netcdf_global_attributes.attributes = json_request.get('global_attributes', {})

    logger.info('Write request configuration into {}'.format(output_cfg))
    cfg_request.write(output_cfg)
