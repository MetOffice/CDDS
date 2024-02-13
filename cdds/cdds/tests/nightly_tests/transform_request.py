#!/usr/bin/env python
# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
from metomi.isodatetime.parsers import TimePointParser

from cdds.common.io import read_json
# from cdds.common.request.request import Request


def main(input_json, output_cfg):

    json_request = read_json(input_json)

    branch_method = json_request['branch_method']

    # cfg_request = Request()
    # cfg_request.metadata.branch_date_in_child = TimePointParser().parse(json_request['branch_date_in_child'])
    # cfg_request.metadata.branch_method = branch_method
    #
    # if branch_method is not 'no parent':
    #     cfg_request.metadata.branch_date_in_parent = ''
    #     cfg_request.metadata.parent_base_date = ''
    #     cfg_request.metadata.parent_experiment_id = ''
    #     cfg_request.metadata.parent_mip = ''
    #     cfg_request.metadata.parent_mip_era = ''
    #     cfg_request.metadata.parent_model_id = ''
    #     cfg_request.metadata.parent_time_units = ''
    #     cfg_request.metadata.parent_variant_label = ''
    #
    # cfg_request.metadata.child_base_date = ''
    # cfg_request.metadata.calendar = ''
    # cfg_request.metadata.experiment_id = ''
    # cfg_request.metadata.institution_id = ''
    # cfg_request.metadata.license = ''
    # cfg_request.metadata.mip = ''
    # cfg_request.metadata.mip_era = ''
    # cfg_request.metadata.sub_experiment_id = ''
    # cfg_request.metadata.variant_label = ''
    # cfg_request.metadata.standard_names_dir = ''
    # cfg_request.metadata.standard_names_version = ''
    # cfg_request.metadata.model_id = ''
    # cfg_request.metadata.model_type = ''
    #
    # cfg_request.common.cdds_version = ''
    # cfg_request.common.external_plugin = ''
    # cfg_request.common.external_plugin_location = ''
    # cfg_request.common.mip_table_dir = ''
    # cfg_request.common.mode = ''
    # cfg_request.common.package = ''
    # cfg_request.common.workflow_basename = ''
    # cfg_request.common.root_proc_dir = ''
    # cfg_request.common.root_data_dir = ''
    # cfg_request.common.root_ancil_dir = ''
    # cfg_request.common.root_hybrid_heights_dir = ''
    # cfg_request.common.root_replacement_coordinates_dir = ''
    # cfg_request.common.sites_file = ''
    # cfg_request.common.simulation = ''
    # cfg_request.common.log_level = ''
    # cfg_request.common.data_version = ''
    #
    # cfg_request.conversion.skip_extract = False
    # cfg_request.conversion.skip_extract_validation = False
    # cfg_request.conversion.skip_configure = False
    # cfg_request.conversion.skip_qc = False
    # cfg_request.conversion.skip_archive = False
    # cfg_request.conversion.cdds_workflow_branch = ''
    # cfg_request.conversion.cylc_args = ''
    # cfg_request.conversion.no_email_notifications = False
    # cfg_request.conversion.scale_memory_limits = None
    # cfg_request.conversion.override_cycling_frequency = []
    # cfg_request.conversion.model_params_dir = ''
    #
    # cfg_request.data.end_date = ''
    # cfg_request.data.mass_data_class = ''
    # cfg_request.data.mass_ensemble_member = ''
    # cfg_request.data.start_date = ''
    # cfg_request.data.model_workflow_id = ''
    # cfg_request.data.model_workflow_branch = ''
    # cfg_request.data.model_workflow_revision = ''
    # cfg_request.data.streams = []
    # cfg_request.data.variable_list_file = ''
    # cfg_request.data.output_mass_root = ''
    # cfg_request.data.output_mass_suffix = ''
    #
    # cfg_request.inventory.inventory_check = False
    # cfg_request.inventory.inventory_database_location = ''
    #
    # cfg_request.misc.atmos_timestep = json_request['atmos_timestep']
    # cfg_request.misc.use_proc_dir = False
    # cfg_request.misc.no_overwrite = False
    #
    # cfg_request.netcdf_global_attributes.attributes = {}
    #
    # cfg_request.write(output_cfg)


if __name__ == '__main__':
    input_json = ''
    output_cfg = ''
    main(input_json, output_cfg)
