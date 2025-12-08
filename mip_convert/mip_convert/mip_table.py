# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
import logging
import os

from mip_convert.configuration.json_config import MIPConfig
from mip_convert.configuration.python_config import ModelToMIPMappingConfig
from mip_convert.new_variable import VariableModelToMIPMapping, VariableMIPMetadata
from mip_convert.plugins.plugins import MappingPluginStore


def get_variable_model_to_mip_mapping(model_to_mip_mappings: ModelToMIPMappingConfig,
                                      variable_name: str, mip_table_id: str) -> VariableModelToMIPMapping:
    """Return an object that enables access to the
    |model to MIP mappings| for a specific |MIP requested variable|.

    Parameters
    ----------
    model_to_mip_mappings : :class:`configuration.ModelToMIPMappingConfig` object
        the |model to MIP mappings|
    variable_name : string
        the |MIP requested variable name|
    mip_table_id : string
        the |MIP table identifier|

    Returns
    -------
    :class:`new_variable.VariableModelToMIPMapping` object
        access to the |model to MIP mappings| for a specific |MIP requested variable|

    Raises
    ------
    RuntimeError
        if any of the required options (``expression``, ``mip_table_id``, ``positive``, ``units``) are not available for
        the |MIP requested variable|
    """
    model_to_mip_mapping = model_to_mip_mappings.select_mapping(variable_name, mip_table_id)

    mapping_plugin = MappingPluginStore.instance().get_plugin()
    for option in mapping_plugin.required_options():
        if option not in model_to_mip_mapping:
            message = 'No "{}" available for "{}" for "{}"'
            raise RuntimeError(message.format(option, variable_name, mip_table_id))

    # Create the object that enables access to the 'model to MIP mappings' for a specific 'MIP requested variable'.
    variable_model_to_mip_mapping = VariableModelToMIPMapping(variable_name,
                                                              model_to_mip_mapping,
                                                              model_to_mip_mappings.model_id)
    return variable_model_to_mip_mapping


def get_variable_mip_metadata(variable_name: str, mip_table: str) -> VariableMIPMetadata:
    """Return an object that enables access to the |MIP table| for a
    specific |MIP requested variable|.

    Parameters
    ----------
    variable_name : string
        the |MIP requested variable name|
    mip_table : :class:`configuration.MIPConfig` object
        the |MIP table|

    Returns
    -------
    :class:`new_variable.VariableMIPMetadata` object
        access to the |MIP table| for a specific |MIP requested variable| and additional constraint information

    Raises
    ------
    KeyError
        if |MIP requested variable name| does not exist in the MIP table
    """
    try:
        variable_info = mip_table.variables[variable_name]
    except KeyError:
        message = 'Variable "{variable_name}" does not exist in MIP table "{mip_table_name}"'
        raise KeyError(message.format(variable_name=variable_name, mip_table_name=mip_table.name))

    variable_mip_metadata = VariableMIPMetadata(variable_info, mip_table.axes)
    return variable_mip_metadata


def get_mip_table(mip_table_dir: str, mip_table_name: str) -> MIPConfig:
    """Return an object that enables access to the |MIP table|.

    Parameters
    ----------
    mip_table_dir : string
        the name of the validated |MIP table| directory
    mip_table_name : string
        the name of the |MIP table|

    Returns
    -------
    :class:`configuration.MIPConfig` object
        access to the |MIP table|
    """
    # Read and validate the 'MIP table'.
    logger = logging.getLogger(__name__)
    mip_table_path = os.path.join(mip_table_dir, mip_table_name)
    mip_table = MIPConfig(mip_table_path)
    logger.debug('MIP table "{}" exists'.format(mip_table_path))
    return mip_table
