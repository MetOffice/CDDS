# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module to provide validations for each request section
"""
import os


from typing import TYPE_CHECKING, Tuple, List

from cdds.common.configuration.cv_config import CVConfig
from cdds.common.request.validations.section_validators import (SectionValidatorFactory,
                                                                CommonSectionValidator,
                                                                MetadataSectionValidator,
                                                                MiscSectionValidator)
from cdds.common.request.validations.cv_validators import CVValidatorFactory
from cdds.common.plugins.plugins import PluginStore

if TYPE_CHECKING:
    from cdds.common.request.common_section import CommonSection
    from cdds.common.request.data_section import DataSection
    from cdds.common.request.inventory_section import InventorySection
    from cdds.common.request.metadata_section import MetadataSection
    from cdds.common.request.misc_section import MiscSection
    from cdds.common.request.request import Request


def validate_common_section(section: 'CommonSection') -> None:
    """
    Validates given common section and raises an error if validation failed.

    :param section: common section to validate
    :type section: 'CommonSection'
    """
    validator = CommonSectionValidator(section=section)
    valid, messages = validator.validate()

    if not valid:
        raise AttributeError('\n'.join(messages))


def validate_data_section(section: 'DataSection') -> None:
    """
    Validates given data sections and raises an error if validation failed.

    :param section: data section to validate
    :type section: 'DataSection'
    """
    messages = []
    validate_file = SectionValidatorFactory.file_validator()
    valid, message = validate_file(section.variable_list_file, 'variable_list_file')
    if not valid:
        messages.append(message)

    if section.start_date and section.end_date:
        validate_start_before_end = SectionValidatorFactory.start_before_end_validator()
        valid, message = validate_start_before_end(section.start_date, section.end_date, 'start_date', 'end_date')
        if not valid:
            messages.append(message)

    validate_workflow_id = SectionValidatorFactory.workflow_id_validator()
    workflow_id_valid, workflow_invalid_message = validate_workflow_id(section.model_workflow_id, 'model_workflow_id')
    if not workflow_id_valid:
        messages.append(workflow_invalid_message)

    if messages:
        raise AttributeError('\n'.join(messages))


def validate_inventory_section(section: 'InventorySection') -> None:
    """
    Validates given inventory section and raises an error if validation failed.

    :param section: inventory section to validate
    :type section: 'InventorySection'
    """
    if section.inventory_check:
        validate_file = SectionValidatorFactory.file_validator()
        valid, message = validate_file(section.inventory_database_location, 'inventory_database_location')
        if not valid:
            raise AttributeError(message)


def validate_metadata_section(section: 'MetadataSection') -> None:
    """
    Validates given metadata section and raises an error if validation failed.

    :param section: metadata section to validate
    :type section: 'MetadataSection'
    """
    validator = MetadataSectionValidator(section=section)
    valid, messages = validator.validate()

    if not valid:
        raise AttributeError('\n'.join(messages))


def validate_misc_section(section: 'MiscSection') -> None:
    """
    Validates given metadata section and raises an error if validation failed.

    :param section: misc section to validate
    :type section: 'MiscSection'
    """
    validator = MiscSectionValidator(section=section)
    valid, messages = validator.validate()

    if not valid:
        raise AttributeError('\n'.join(messages))


def validate_request(request: 'Request') -> None:
    """
    Validates given request against the controlled vocabulary

    :param request: request to validate
    :type request: 'Request'
    """
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
