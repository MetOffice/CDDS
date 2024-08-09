# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import os

from typing import TYPE_CHECKING

from cdds.common.configuration.cv_config import CVConfig
from cdds.common.request.validations.section_validators import SectionValidatorFactory
from cdds.common.request.validations.cv_validators import CVValidatorFactory
from cdds.common.plugins.plugins import PluginStore

if TYPE_CHECKING:
    from cdds.common.request.common_section import CommonSection
    from cdds.common.request.data_section import DataSection
    from cdds.common.request.inventory_section import InventorySection
    from cdds.common.request.metadata_section import MetadataSection
    from cdds.common.request.request import Request


def validate_common_section(section: 'CommonSection'):
    validate_external_plugin = SectionValidatorFactory.external_plugin_validator()
    validate_external_plugin(section.external_plugin, section.external_plugin_location)

    validate_mode = SectionValidatorFactory.allowed_values_validator()
    validate_mode(section.mode, ['relaxed', 'strict'], 'mode')

    directory_dict = {
        'standard_names_dir': section.standard_names_dir,
        'root_replacement_coordinates_dir': section.root_replacement_coordinates_dir,
        'root_hybrid_heights_dir': section.root_hybrid_heights_dir,
        'root_ancil_dir': section.root_ancil_dir,
        'mip_table_dir': section.mip_table_dir
    }

    validate_directory = SectionValidatorFactory.directory_validator()
    for k, v in directory_dict.items():
        validate_directory(v, k)

    file_dict = {
        'sites_file': section.sites_file
    }

    validate_file = SectionValidatorFactory.file_validator()
    for k, v in file_dict.items():
        validate_file(v, k)


def validate_data_section(section: 'DataSection'):
    if section.start_date and section.end_date:
        validate_start_before_end = SectionValidatorFactory.start_before_end_validator()
        validate_start_before_end(section.start_date, section.end_date, 'start_date', 'end_date')


def validate_inventory_section(section: 'InventorySection'):
    if section.inventory_check:
        validate_file = SectionValidatorFactory.file_validator()
        validate_file(section.inventory_database_location, 'inventory_database_location')


def validate_metadata_section(section: 'MetadataSection'):
    values_allowed_dict = {
        'branch_method': (section.branch_method, ['no parent', 'standard']),
        'calendar': (section.calendar, ['360_day', 'gregorian'])
    }

    allowed_values_validate = SectionValidatorFactory.allowed_values_validator()

    for property_name, value_tuple in values_allowed_dict.items():
        allowed_values_validate(value_tuple[0], value_tuple[1], property_name)

    values_most_set_dict = {
        'mip': section.mip,
        'base_date': section.base_date,
        'experiment_id': section.experiment_id,
        'mip_era': section.mip_era,
        'model_id': section.model_id,
        'variant_label': section.variant_label,
    }

    if section.branch_method == 'standard':
        parent_values_set_dict = {
            'parent_experiment_id': section.parent_experiment_id,
            'parent_mip': section.parent_mip,
            'parent_mip_era': section.parent_mip_era,
            'parent_model_id': section.parent_model_id,
            'parent_time_units': section.parent_time_units,
            'branch_date_in_child': section.branch_date_in_child,
            'branch_date_in_parent': section.branch_date_in_parent,
            'parent_base_date': section.parent_base_date
        }
        values_most_set_dict.update(parent_values_set_dict)

    exist_validate = SectionValidatorFactory.exist_validator()
    for property_name, value in values_most_set_dict.items():
        exist_validate(value, property_name)


def validate_request(request: 'Request'):
    mip_era = request.metadata.mip_era

    if request.common.mip_table_dir:
        cv_path = os.path.join(request.common.mip_table_dir, '{}_CV.json'.format(mip_era))
    else:
        plugin = PluginStore.instance().get_plugin()
        cv_path = os.path.join(plugin.mip_table_dir(), '{}_CV.json'.format(mip_era))

    CVValidatorFactory.path_validator()(cv_path)

    cv_config = CVConfig(cv_path)

    validate_funcs = [
        CVValidatorFactory.institution_validator(),
        CVValidatorFactory.model_validator(),
        CVValidatorFactory.experiment_validator(),
        CVValidatorFactory.model_types_validator()
    ]

    if request.metadata.branch_method != 'no parent':
        validate_funcs.append(CVValidatorFactory.parent_validator())

    for validate_func in validate_funcs:
        validate_func(cv_config, request)
